"""Celery task: generate lesson + quiz for a pending GeneratedContent row.

Runs the async pipeline via asyncio.run with a task-local engine (Celery workers
can't share the API process's event loop). Two OpenRouter calls — lesson and quiz —
with independently configurable models. When OpenRouter isn't configured, a
deterministic stub lesson is produced so local development works end to end.
"""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..config import settings
from ..generation import openrouter, prompts
from ..models import ConceptNode, GeneratedContent, GenerationContract
from .celery_app import celery_app

logger = logging.getLogger("upvex.generate")


_VISUAL_TYPES = frozenset({"bar", "line", "flow", "compare", "stack"})


def _sanitize_visual(visual: object) -> dict | None:
    """Keep only renderable visuals; drop malformed ones so generation still succeeds."""
    if not isinstance(visual, dict):
        return None
    vtype = visual.get("type")
    if vtype not in _VISUAL_TYPES:
        return None
    out: dict = {"type": vtype}
    if isinstance(visual.get("title"), str) and visual["title"].strip():
        out["title"] = visual["title"].strip()
    if isinstance(visual.get("caption"), str) and visual["caption"].strip():
        out["caption"] = visual["caption"].strip()

    if vtype == "bar":
        bars = visual.get("bars")
        if not isinstance(bars, list) or len(bars) < 2:
            return None
        cleaned = []
        for b in bars[:8]:
            if not isinstance(b, dict):
                continue
            label, value = b.get("label"), b.get("value")
            if isinstance(label, str) and isinstance(value, (int, float)):
                cleaned.append({"label": label.strip()[:60], "value": float(value)})
        if len(cleaned) < 2:
            return None
        out["bars"] = cleaned
        if isinstance(visual.get("y_label"), str):
            out["y_label"] = visual["y_label"].strip()[:40]
        return out

    if vtype == "line":
        points = visual.get("points")
        if not isinstance(points, list) or len(points) < 2:
            return None
        cleaned = []
        for p in points[:12]:
            if not isinstance(p, dict):
                continue
            label, value = p.get("label"), p.get("value")
            if isinstance(label, str) and isinstance(value, (int, float)):
                cleaned.append({"label": label.strip()[:40], "value": float(value)})
        if len(cleaned) < 2:
            return None
        out["points"] = cleaned
        if isinstance(visual.get("y_label"), str):
            out["y_label"] = visual["y_label"].strip()[:40]
        return out

    if vtype == "flow":
        steps = visual.get("steps")
        if not isinstance(steps, list) or len(steps) < 2:
            return None
        cleaned = []
        for s in steps[:6]:
            if not isinstance(s, dict) or not isinstance(s.get("label"), str):
                continue
            step = {"label": s["label"].strip()[:48]}
            if isinstance(s.get("detail"), str) and s["detail"].strip():
                step["detail"] = s["detail"].strip()[:80]
            cleaned.append(step)
        if len(cleaned) < 2:
            return None
        out["steps"] = cleaned
        return out

    if vtype == "compare":
        columns = visual.get("columns")
        if not isinstance(columns, list) or not (2 <= len(columns) <= 3):
            return None
        cleaned = []
        for c in columns:
            if not isinstance(c, dict) or not isinstance(c.get("title"), str):
                continue
            items = c.get("items")
            if not isinstance(items, list):
                continue
            item_strs = [str(i).strip()[:80] for i in items[:6] if str(i).strip()]
            if not item_strs:
                continue
            cleaned.append({"title": c["title"].strip()[:48], "items": item_strs})
        if len(cleaned) < 2:
            return None
        out["columns"] = cleaned
        return out

    if vtype == "stack":
        segments = visual.get("segments")
        if not isinstance(segments, list) or len(segments) < 2:
            return None
        cleaned = []
        for s in segments[:6]:
            if not isinstance(s, dict):
                continue
            label, value = s.get("label"), s.get("value")
            if isinstance(label, str) and isinstance(value, (int, float)) and value > 0:
                cleaned.append({"label": label.strip()[:40], "value": float(value)})
        if len(cleaned) < 2:
            return None
        out["segments"] = cleaned
        if isinstance(visual.get("total_label"), str):
            out["total_label"] = visual["total_label"].strip()[:48]
        return out

    return None


def _validate_lesson(lesson: dict) -> None:
    for key in ("title", "intro", "sections", "key_takeaways", "check_understanding"):
        if key not in lesson:
            raise ValueError(f"Lesson missing required key: {key}")
    if not isinstance(lesson["sections"], list) or not lesson["sections"]:
        raise ValueError("Lesson sections must be a non-empty list")
    for section in lesson["sections"]:
        if not isinstance(section, dict):
            continue
        if "visual" in section:
            cleaned = _sanitize_visual(section.get("visual"))
            if cleaned:
                section["visual"] = cleaned
            else:
                section.pop("visual", None)


def _stub_visual_for(node: ConceptNode) -> dict:
    """Concept-flavored placeholder visuals so local/dev lessons show the UI."""
    cid = node.id
    if "join" in cid:
        return {
            "type": "compare",
            "title": "Join strategies at a glance",
            "caption": "Broadcast wins when one side is small; sort-merge is the default for large×large.",
            "columns": [
                {
                    "title": "Broadcast",
                    "items": ["Small table fits in memory", "No shuffle of the large side", "Fast when applicable"],
                },
                {
                    "title": "Sort-merge",
                    "items": ["Both sides shuffled/sorted", "Handles large×large", "Sensitive to skew"],
                },
            ],
        }
    if "partition" in cid or "skew" in cid or "shuffle" in cid:
        return {
            "type": "bar",
            "title": "Work per partition (illustrative)",
            "caption": "One hot partition dominates runtime even if average load looks fine.",
            "y_label": "Relative work",
            "bars": [
                {"label": "P0", "value": 12},
                {"label": "P1", "value": 14},
                {"label": "P2", "value": 11},
                {"label": "P3 (skew)", "value": 68},
            ],
        }
    if "memory" in cid or "cach" in cid:
        return {
            "type": "stack",
            "title": "Unified memory (illustrative split)",
            "caption": "Execution and storage compete for the same pool — pressure on one squeezes the other.",
            "total_label": "Executor memory",
            "segments": [
                {"label": "Execution", "value": 40},
                {"label": "Storage", "value": 35},
                {"label": "User / reserved", "value": 25},
            ],
        }
    if "architecture" in cid or "deploy" in cid:
        return {
            "type": "flow",
            "title": "How a Spark app runs",
            "caption": "The driver plans; the cluster manager allocates; executors do the work.",
            "steps": [
                {"label": "Driver", "detail": "Builds the plan"},
                {"label": "Cluster manager", "detail": "Allocates executors"},
                {"label": "Executors", "detail": "Run tasks + cache data"},
            ],
        }
    if "window" in cid or "aggregat" in cid:
        return {
            "type": "compare",
            "title": "GROUP BY vs window",
            "caption": "Aggregations collapse rows; windows keep every row and add a computed column.",
            "columns": [
                {"title": "GROUP BY", "items": ["One row per group", "Drops detail rows", "Great for summaries"]},
                {"title": "Window (OVER)", "items": ["Keeps all rows", "Adds rank / running total", "PARTITION BY defines peers"]},
            ],
        }
    if "index" in cid or "optim" in cid or "big_data" in cid:
        return {
            "type": "line",
            "title": "Illustrative time vs data size",
            "caption": "Single-machine cost grows steeply; distributed work stays flatter when parallelism holds.",
            "y_label": "Relative time",
            "points": [
                {"label": "1 GB", "value": 1},
                {"label": "10 GB", "value": 4},
                {"label": "100 GB", "value": 22},
                {"label": "1 TB", "value": 180},
            ],
        }
    if "transaction" in cid or "stream" in cid:
        return {
            "type": "flow",
            "title": "Lifecycle at a glance",
            "caption": "Follow the sequence — each stage depends on the previous one's guarantees.",
            "steps": [
                {"label": "Begin", "detail": "Start unit of work"},
                {"label": "Read / write", "detail": "Apply changes"},
                {"label": "Commit or abort", "detail": "Make durable or roll back"},
            ],
        }
    return {
        "type": "flow",
        "title": f"Mental model: {node.title}",
        "caption": "A simple sequence to keep the idea oriented while you read.",
        "steps": [
            {"label": "Idea", "detail": "What problem it solves"},
            {"label": "Mechanism", "detail": "How it works"},
            {"label": "Apply", "detail": "When you'd use it"},
        ],
    }


def _stub_lesson(node: ConceptNode) -> dict:
    return {
        "title": node.title,
        "intro": (
            f"This is a locally generated placeholder lesson for '{node.title}'. "
            "Connect an OpenRouter API key to generate real, personalized content."
        ),
        "sections": [
            {
                "heading": "Learning objective",
                "body": node.learning_objective,
                "visual": _stub_visual_for(node),
            },
            {
                "heading": "About this placeholder",
                "body": (
                    "Upvex generates lessons live via OpenRouter using the active GenerationContract "
                    "and your learner profile. Since no API key is configured, this stub is served so "
                    "the full product flow can be exercised in development — including lesson visuals."
                ),
            },
        ],
        "key_takeaways": [
            f"Objective: {node.learning_objective}",
            f"Difficulty: {node.difficulty_tag}, Bloom level: {node.bloom_level}",
            "Set OPENROUTER_API_KEY to enable real generation.",
        ],
        "check_understanding": f"In your own words, what would mastering '{node.title}' let you do?",
    }


def _validate_quiz(quiz: dict) -> None:
    questions = quiz.get("questions")
    if not isinstance(questions, list) or len(questions) < 3:
        raise ValueError("Quiz must contain at least 3 questions")
    for q in questions:
        if q.get("type") == "multiple_choice":
            if not isinstance(q.get("options"), list) or q.get("correct_option") is None:
                raise ValueError("Multiple choice question missing options/correct_option")
        elif q.get("type") == "short_answer":
            if not q.get("expected_concepts"):
                raise ValueError("Short answer question missing expected_concepts")


def _stub_quiz(node: ConceptNode) -> dict:
    return {
        "questions": [
            {
                "type": "multiple_choice",
                "question_text": f"(Placeholder) Which statement best matches the objective of '{node.title}'?",
                "options": [
                    node.learning_objective,
                    "An unrelated statement about frontend styling",
                    "An unrelated statement about project management",
                    "An unrelated statement about hardware",
                ],
                "correct_option": 0,
                "explanation": "The learning objective defines what this concept teaches.",
            },
            {
                "type": "multiple_choice",
                "question_text": f"(Placeholder) What difficulty is '{node.title}' tagged as?",
                "options": ["beginner", "intermediate", "advanced", "expert"],
                "correct_option": ["beginner", "intermediate", "advanced"].index(node.difficulty_tag),
                "explanation": "Matches the concept's difficulty tag.",
            },
            {
                "type": "multiple_choice",
                "question_text": "(Placeholder) What generates real Upvex lessons in production?",
                "options": [
                    "A static content library",
                    "The GenerationContract + learner profile via OpenRouter",
                    "Manually written admin content",
                    "Wikipedia scraping",
                ],
                "correct_option": 1,
                "explanation": "Content is generated live per profile-signature and cached.",
            },
            {
                "type": "short_answer",
                "question_text": f"(Placeholder) Briefly describe what '{node.title}' covers.",
                "expected_concepts": [w.lower() for w in node.title.split()[:3]],
                "explanation": "Any answer touching the concept's core ideas counts.",
            },
        ]
    }


async def _run_generation(content_id: str) -> None:
    connect_args = {}
    if settings.database_url.startswith("postgresql+asyncpg"):
        connect_args = {"statement_cache_size": 0}
    engine = create_async_engine(settings.database_url, connect_args=connect_args)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as db:
            content = await db.get(GeneratedContent, content_id)
            if content is None or content.status == "ready":
                return
            node = await db.get(ConceptNode, content.concept_node_id)
            contract = (
                await db.execute(
                    select(GenerationContract).where(
                        GenerationContract.version == content.generation_contract_version
                    )
                )
            ).scalar_one()

            user_vars = dict(content.signature_inputs or {})
            root_gap_title = None
            primary_root_gap = user_vars.get("primary_root_gap")
            if primary_root_gap:
                gap_node = await db.get(ConceptNode, primary_root_gap)
                root_gap_title = gap_node.title if gap_node else None
            user_vars["root_gap_context"] = prompts.build_root_gap_context(root_gap_title)

            try:
                if openrouter.is_configured():
                    sys_p, usr_p = prompts.build_lesson_prompt(contract, node, user_vars)
                    lesson = await openrouter.chat_json(
                        settings.model_lesson_generation, sys_p, usr_p, temperature=0.7
                    )
                    _validate_lesson(lesson)

                    sys_q, usr_q = prompts.build_quiz_prompt(contract, node, user_vars, lesson)
                    quiz = await openrouter.chat_json(
                        settings.model_quiz_generation, sys_q, usr_q, temperature=0.4
                    )
                    _validate_quiz(quiz)
                    model_used = f"{settings.model_lesson_generation} + {settings.model_quiz_generation}"
                else:
                    lesson, quiz = _stub_lesson(node), _stub_quiz(node)
                    model_used = "stub (no OpenRouter key)"

                content.lesson_body = lesson
                content.quiz_body = quiz
                content.model_used = model_used
                content.status = "ready"
                content.error = None
            except Exception as exc:  # noqa: BLE001 — record failure for polling clients
                logger.exception("Generation failed for content %s", content_id)
                content.status = "failed"
                content.error = str(exc)[:2000]
            await db.commit()
    finally:
        await engine.dispose()


@celery_app.task(name="app.tasks.generate.generate_content", bind=True, max_retries=2)
def generate_content(self, content_id: str) -> str:
    asyncio.run(_run_generation(content_id))
    return content_id
