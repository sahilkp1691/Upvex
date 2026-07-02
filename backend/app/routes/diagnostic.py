"""Adaptive diagnostic quiz: starts at medium difficulty, branches up/down on
correctness, spreads questions across concept nodes for coverage. Question
selection is deterministic and synchronous (latency matters mid-quiz);
final scoring runs the Diagnostic Evaluator."""

import random

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents import evaluator
from ..auth import get_current_user
from ..database import get_db
from ..models import DiagnosticAttempt, DiagnosticQuestion, User, UserGoal
from ..services.scoring import keyword_overlap_score

router = APIRouter()

MAX_QUESTIONS = 12
MIN_QUESTIONS = 8
_HARDER = {"easy": "medium", "medium": "hard", "hard": "hard"}
_EASIER = {"easy": "easy", "medium": "easy", "hard": "medium"}


class AnswerPayload(BaseModel):
    question_id: str
    selected_option: int | None = None
    answer_text: str | None = None


def _question_payload(q: DiagnosticQuestion, index: int) -> dict:
    return {
        "question_id": q.id,
        "index": index,
        "total_estimate": MAX_QUESTIONS,
        "concept_node_id": q.concept_node_id,
        "difficulty": q.difficulty,
        "type": q.type,
        "question_text": q.question_text,
        "options": q.options,  # correct_option is never sent to the client
    }


async def _get_goal(db: AsyncSession, goal_id: str, user: User) -> UserGoal:
    goal = await db.get(UserGoal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    return goal


async def _get_open_attempt(db: AsyncSession, goal_id: str) -> DiagnosticAttempt | None:
    return (
        await db.execute(
            select(DiagnosticAttempt)
            .where(DiagnosticAttempt.user_goal_id == goal_id, DiagnosticAttempt.status == "in_progress")
            .order_by(DiagnosticAttempt.created_at.desc())
        )
    ).scalars().first()


def _next_difficulty(responses: list[dict]) -> str:
    if not responses:
        return "medium"
    last = responses[-1]
    return _HARDER[last["difficulty"]] if last.get("correct") else _EASIER[last["difficulty"]]


def _pick_question(
    pool: list[DiagnosticQuestion], responses: list[dict], target_difficulty: str
) -> DiagnosticQuestion | None:
    asked_ids = {r["question_id"] for r in responses}
    ask_count_by_concept: dict[str, int] = {}
    for r in responses:
        ask_count_by_concept[r["concept_node_id"]] = ask_count_by_concept.get(r["concept_node_id"], 0) + 1

    candidates = [q for q in pool if q.id not in asked_ids]
    if not candidates:
        return None
    at_difficulty = [q for q in candidates if q.difficulty == target_difficulty]
    working = at_difficulty or candidates
    # coverage first: fewest prior questions on that concept wins; shuffle ties
    rng = random.Random(len(responses))
    rng.shuffle(working)
    working.sort(key=lambda q: ask_count_by_concept.get(q.concept_node_id, 0))
    return working[0]


@router.post("/diagnostic/{goal_id}/start")
async def start_diagnostic(
    goal_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    goal = await _get_goal(db, goal_id, user)
    attempt = await _get_open_attempt(db, goal_id)
    if attempt is None:
        attempt = DiagnosticAttempt(user_goal_id=goal_id, responses=[])
        db.add(attempt)
        await db.commit()
        await db.refresh(attempt)

    pool = (
        await db.execute(select(DiagnosticQuestion).where(DiagnosticQuestion.topic_id == goal.topic_id))
    ).scalars().all()
    if not pool:
        raise HTTPException(500, "No diagnostic questions seeded for this topic")

    question = _pick_question(pool, attempt.responses, _next_difficulty(attempt.responses))
    if question is None:
        return {"attempt_id": attempt.id, "done": True, "answered": len(attempt.responses)}
    return {
        "attempt_id": attempt.id,
        "done": False,
        "question": _question_payload(question, len(attempt.responses) + 1),
    }


@router.post("/diagnostic/{goal_id}/answer")
async def answer_question(
    goal_id: str,
    payload: AnswerPayload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await _get_goal(db, goal_id, user)
    attempt = await _get_open_attempt(db, goal_id)
    if attempt is None:
        raise HTTPException(409, "No diagnostic in progress — call start first")

    question = await db.get(DiagnosticQuestion, payload.question_id)
    if question is None or question.topic_id != goal.topic_id:
        raise HTTPException(404, "Question not found")
    if any(r["question_id"] == question.id for r in attempt.responses):
        raise HTTPException(409, "Question already answered")

    record: dict = {
        "question_id": question.id,
        "concept_node_id": question.concept_node_id,
        "difficulty": question.difficulty,
        "type": question.type,
        "question_text": question.question_text,
    }
    if question.type == "multiple_choice":
        record["selected_option"] = payload.selected_option
        record["correct"] = payload.selected_option == question.correct_option
    else:
        record["answer_text"] = payload.answer_text or ""
        record["expected_concepts"] = question.expected_concepts or []
        # heuristic correctness for adaptive branching only; evaluator re-grades properly
        record["correct"] = keyword_overlap_score(record["answer_text"], record["expected_concepts"]) >= 0.5

    attempt.responses = attempt.responses + [record]
    await db.commit()

    if len(attempt.responses) >= MAX_QUESTIONS:
        return {"done": True, "answered": len(attempt.responses)}

    pool = (
        await db.execute(select(DiagnosticQuestion).where(DiagnosticQuestion.topic_id == goal.topic_id))
    ).scalars().all()
    question_next = _pick_question(pool, attempt.responses, _next_difficulty(attempt.responses))
    if question_next is None or (
        len(attempt.responses) >= MIN_QUESTIONS
        and len({r["concept_node_id"] for r in attempt.responses}) >= len({q.concept_node_id for q in pool})
    ):
        return {"done": True, "answered": len(attempt.responses)}
    return {
        "done": False,
        "answered": len(attempt.responses),
        "question": _question_payload(question_next, len(attempt.responses) + 1),
    }


@router.post("/diagnostic/{goal_id}/complete")
async def complete_diagnostic(
    goal_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    goal = await _get_goal(db, goal_id, user)
    attempt = await _get_open_attempt(db, goal_id)
    if attempt is None:
        raise HTTPException(409, "No diagnostic in progress")
    if not attempt.responses:
        raise HTTPException(409, "No responses recorded")

    output = await evaluator.evaluate(db, goal.topic_id, list(attempt.responses))

    attempt.evaluator_output = output
    attempt.status = "completed"
    goal.level_score = output["level_score"]
    goal.concept_gap_map = output["concept_scores"]
    goal.root_gap_concepts = output["root_gap_concepts"]
    goal.status = "active"
    await db.commit()

    return {
        "goal_id": goal.id,
        "level_score": output["level_score"],
        "confidence": output["confidence"],
        "concept_scores": output["concept_scores"],
        "root_gap_concepts": output["root_gap_concepts"],
        "gap_reasoning": output["gap_reasoning"],
    }
