"""Diagnostic question bank helpers: readiness checks and AI drafts."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..generation import openrouter
from ..models import ConceptNode, DiagnosticQuestion, Topic

logger = logging.getLogger("upvex.diagnostic_bank")

# Adaptive quiz aims for 8–12 questions; require a usable bank before learners start.
MIN_BANK_SIZE = 8
MIN_CONCEPTS_COVERED = 3


def _question_dict(q: DiagnosticQuestion) -> dict:
    return {
        "id": q.id,
        "topic_id": q.topic_id,
        "concept_node_id": q.concept_node_id,
        "difficulty": q.difficulty,
        "type": q.type,
        "question_text": q.question_text,
        "options": q.options,
        "correct_option": q.correct_option,
        "expected_concepts": q.expected_concepts,
    }


async def readiness(db: AsyncSession, topic_id: str) -> dict[str, Any]:
    """Return whether a topic has enough diagnostics to run the adaptive quiz."""
    concept_count = int(
        (
            await db.execute(
                select(func.count()).select_from(ConceptNode).where(ConceptNode.topic_id == topic_id)
            )
        ).scalar_one()
    )
    questions = (
        await db.execute(select(DiagnosticQuestion).where(DiagnosticQuestion.topic_id == topic_id))
    ).scalars().all()
    question_count = len(questions)
    covered = {q.concept_node_id for q in questions}
    difficulties = sorted({q.difficulty for q in questions})
    by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
    for q in questions:
        if q.difficulty in by_difficulty:
            by_difficulty[q.difficulty] += 1

    needed_concepts = min(MIN_CONCEPTS_COVERED, concept_count) if concept_count else MIN_CONCEPTS_COVERED
    issues: list[str] = []
    if concept_count == 0:
        issues.append("Add concept nodes to the knowledge graph first.")
    if question_count < MIN_BANK_SIZE:
        issues.append(f"Need at least {MIN_BANK_SIZE} diagnostic questions (have {question_count}).")
    if concept_count > 0 and len(covered) < needed_concepts:
        issues.append(
            f"Cover at least {needed_concepts} concepts with questions (have {len(covered)})."
        )
    if question_count > 0 and len(difficulties) < 2:
        issues.append("Include more than one difficulty (easy / medium / hard).")

    ready = (
        concept_count > 0
        and question_count >= MIN_BANK_SIZE
        and len(covered) >= needed_concepts
    )
    return {
        "ready": ready,
        "min_bank_size": MIN_BANK_SIZE,
        "min_concepts_covered": needed_concepts,
        "concept_count": concept_count,
        "question_count": question_count,
        "concepts_covered": len(covered),
        "covered_concept_ids": sorted(covered),
        "difficulties": difficulties,
        "by_difficulty": by_difficulty,
        "issues": issues,
        "message": None if ready else (issues[0] if issues else "Diagnostic bank not ready"),
    }


async def list_questions(db: AsyncSession, topic_id: str) -> list[dict]:
    rows = (
        await db.execute(
            select(DiagnosticQuestion)
            .where(DiagnosticQuestion.topic_id == topic_id)
            .order_by(DiagnosticQuestion.concept_node_id, DiagnosticQuestion.difficulty)
        )
    ).scalars().all()
    return [_question_dict(q) for q in rows]


def validate_question_payload(payload: dict) -> str | None:
    """Return an error message or None if valid."""
    qtype = payload.get("type")
    if qtype not in ("multiple_choice", "short_answer"):
        return "type must be multiple_choice or short_answer"
    if payload.get("difficulty") not in ("easy", "medium", "hard"):
        return "difficulty must be easy, medium, or hard"
    text = (payload.get("question_text") or "").strip()
    if len(text) < 8:
        return "question_text is too short"
    if qtype == "multiple_choice":
        options = payload.get("options") or []
        if not isinstance(options, list) or len(options) < 2:
            return "multiple_choice needs at least 2 options"
        correct = payload.get("correct_option")
        if correct is None or not isinstance(correct, int) or correct < 0 or correct >= len(options):
            return "correct_option must be a valid options index"
    else:
        concepts = payload.get("expected_concepts") or []
        if not isinstance(concepts, list) or len(concepts) < 1:
            return "short_answer needs expected_concepts keywords"
    return None


async def draft_questions(
    db: AsyncSession,
    topic: Topic,
    *,
    concept_ids: list[str] | None = None,
    count_per_concept: int = 2,
) -> list[dict]:
    """Draft diagnostic questions via OpenRouter (or deterministic stubs without a key)."""
    nodes_q = select(ConceptNode).where(ConceptNode.topic_id == topic.id)
    if concept_ids:
        nodes_q = nodes_q.where(ConceptNode.id.in_(concept_ids))
    nodes = (await db.execute(nodes_q)).scalars().all()
    if not nodes:
        return []

    if not openrouter.is_configured():
        return _stub_drafts(topic, nodes, count_per_concept)

    system = (
        "You write diagnostic quiz questions for an adaptive tech-skills assessment. "
        "Return JSON: {\"questions\": [ ... ]}. Each question has: "
        "concept_title (exact match to a provided concept), difficulty (easy|medium|hard), "
        "type (multiple_choice|short_answer), question_text, "
        "options (array of 4 strings for multiple_choice, else null), "
        "correct_option (0-based index for multiple_choice, else null), "
        "expected_concepts (keyword array for short_answer, else null). "
        "Prefer mostly multiple_choice. Keep questions unambiguous and concept-specific."
    )
    concept_lines = "\n".join(
        f"- {n.title}: {n.learning_objective} (difficulty_tag={n.difficulty_tag})" for n in nodes
    )
    user = (
        f"Topic: {topic.name}\nDescription: {topic.description or ''}\n\n"
        f"Concepts:\n{concept_lines}\n\n"
        f"Write about {count_per_concept} questions per concept "
        f"(mix easy/medium/hard). Total roughly {len(nodes) * count_per_concept} questions."
    )
    try:
        from ..config import settings

        data = await openrouter.chat_json(
            settings.model_diagnostic_evaluator,
            system,
            user,
            temperature=0.45,
            max_tokens=6000,
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("AI diagnostic draft failed: %s", exc)
        return _stub_drafts(topic, nodes, count_per_concept)

    by_title = {n.title.strip().lower(): n for n in nodes}
    drafts: list[dict] = []
    for raw in data.get("questions") or []:
        title = (raw.get("concept_title") or "").strip().lower()
        node = by_title.get(title)
        if node is None:
            # fuzzy: contain match
            node = next((n for t, n in by_title.items() if t in title or title in t), None)
        if node is None:
            continue
        item = {
            "concept_node_id": node.id,
            "concept_title": node.title,
            "difficulty": raw.get("difficulty") if raw.get("difficulty") in ("easy", "medium", "hard") else "medium",
            "type": raw.get("type") if raw.get("type") in ("multiple_choice", "short_answer") else "multiple_choice",
            "question_text": (raw.get("question_text") or "").strip(),
            "options": raw.get("options"),
            "correct_option": raw.get("correct_option"),
            "expected_concepts": raw.get("expected_concepts"),
        }
        if item["type"] == "multiple_choice":
            opts = item["options"] if isinstance(item["options"], list) else []
            item["options"] = [str(o) for o in opts][:6] or [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ]
            co = item["correct_option"]
            if not isinstance(co, int) or co < 0 or co >= len(item["options"]):
                item["correct_option"] = 0
            item["expected_concepts"] = None
        else:
            item["options"] = None
            item["correct_option"] = None
            kws = item["expected_concepts"] if isinstance(item["expected_concepts"], list) else []
            item["expected_concepts"] = [str(k) for k in kws][:12] or [node.title.split()[0].lower()]
        err = validate_question_payload(item)
        if err:
            continue
        drafts.append(item)
    return drafts or _stub_drafts(topic, nodes, count_per_concept)


def _stub_drafts(topic: Topic, nodes: list[ConceptNode], count_per_concept: int) -> list[dict]:
    """Deterministic offline drafts when OpenRouter is unavailable."""
    difficulties = ["easy", "medium", "hard"]
    drafts: list[dict] = []
    for node in nodes:
        for i in range(max(1, count_per_concept)):
            diff = difficulties[i % 3]
            drafts.append(
                {
                    "concept_node_id": node.id,
                    "concept_title": node.title,
                    "difficulty": diff,
                    "type": "multiple_choice",
                    "question_text": (
                        f"[{topic.name}] Which statement best reflects {node.title} "
                        f"({diff})?"
                    ),
                    "options": [
                        f"A core idea of {node.title}",
                        f"An unrelated claim about {topic.name}",
                        "A syntax-only trivia fact with no concept link",
                        "A contradiction of the learning objective",
                    ],
                    "correct_option": 0,
                    "expected_concepts": None,
                }
            )
    return drafts
