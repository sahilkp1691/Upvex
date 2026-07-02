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


def _validate_lesson(lesson: dict) -> None:
    for key in ("title", "intro", "sections", "key_takeaways", "check_understanding"):
        if key not in lesson:
            raise ValueError(f"Lesson missing required key: {key}")
    if not isinstance(lesson["sections"], list) or not lesson["sections"]:
        raise ValueError("Lesson sections must be a non-empty list")


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
            },
            {
                "heading": "About this placeholder",
                "body": (
                    "Upvex generates lessons live via OpenRouter using the active GenerationContract "
                    "and your learner profile. Since no API key is configured, this stub is served so "
                    "the full product flow can be exercised in development."
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
