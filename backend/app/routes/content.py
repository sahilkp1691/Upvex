"""Lesson delivery: cache-or-generate by ProfileSignature, then quiz submission
with Evaluator re-scoring, XP, streaks, and badges."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..agents import evaluator
from ..auth import get_current_user
from ..database import get_db
from ..models import (
    ConceptNode,
    ConceptVisit,
    GeneratedContent,
    GenerationContract,
    LessonCompletion,
    User,
    UserGoal,
    UserProfile,
    utcnow,
)
from ..config import settings
from ..services import xp as xp_service
from ..services.scoring import keyword_overlap_score
from ..services.signature import compute_signature
from ..services.sql_sandbox import dataset_for_client, verify_sandbox_answer
from ..tasks.generate import _run_generation, generate_content

router = APIRouter()

_DIFFICULTY_TO_QUIZ = {"beginner": "easy", "intermediate": "medium", "advanced": "hard"}


class QuizAnswer(BaseModel):
    question_index: int
    selected_option: int | None = None
    answer_text: str | None = None
    user_sql: str | None = None
    hints_used: int = 0
    check_attempts: int = 0


class SandboxVerifyRequest(BaseModel):
    generated_content_id: str | None = None
    question_index: int | None = None
    dataset: str | None = None
    user_sql: str
    solution_sql: str | None = None
    order_sensitive: bool = False


class QuizSubmission(BaseModel):
    generated_content_id: str
    answers: list[QuizAnswer]


async def _load_context(db: AsyncSession, goal_id: str, concept_id: str, user: User):
    goal = await db.get(UserGoal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    node = await db.get(ConceptNode, concept_id)
    if node is None or node.topic_id != goal.topic_id:
        raise HTTPException(404, "Concept not found in this topic")
    profile = (
        await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    ).scalar_one_or_none()
    if profile is None:
        raise HTTPException(409, "Complete onboarding first")
    return goal, node, profile


def _quiz_for_client(quiz_body: dict) -> dict:
    """Strip answers before sending the quiz to the client."""
    questions = []
    datasets_used: set[str] = set()
    for q in quiz_body.get("questions", []):
        qtype = q.get("type")
        if qtype == "sandbox_sql":
            datasets_used.add(q.get("dataset", ""))
            questions.append({
                "type": "sandbox_sql",
                "question_text": q.get("question_text"),
                "dataset": q.get("dataset"),
                "starter_sql": q.get("starter_sql"),
                "hints": q.get("hints") or [],
                "order_sensitive": q.get("order_sensitive", False),
                "difficulty": q.get("difficulty", 4),
            })
        else:
            questions.append({
                "type": qtype,
                "question_text": q.get("question_text"),
                "options": q.get("options"),
            })
    datasets = {}
    for name in datasets_used:
        if name:
            ds = dataset_for_client(name)
            if ds:
                datasets[name] = ds
    return {
        "mode": quiz_body.get("mode", "classic"),
        "questions": questions,
        "datasets": datasets,
    }


def _content_payload(content: GeneratedContent, *, visit_count: int = 0, completion_count: int = 0, last_visited_at=None) -> dict:
    return {
        "status": content.status,
        "content_id": content.id,
        "lesson": content.lesson_body if content.status == "ready" else None,
        "quiz": _quiz_for_client(content.quiz_body) if content.status == "ready" and content.quiz_body else None,
        "error": content.error if content.status == "failed" else None,
        "visit_count": visit_count,
        "completion_count": completion_count,
        "last_visited_at": last_visited_at.isoformat() if last_visited_at else None,
    }


async def _record_visit_and_counts(
    db: AsyncSession, user: User, goal: UserGoal, concept_id: str
) -> tuple[int, int, object]:
    """Increment visit counter on lesson open; return visit_count, completion_count, last_visited_at."""
    visit = (
        await db.execute(
            select(ConceptVisit).where(
                ConceptVisit.user_id == user.id,
                ConceptVisit.user_goal_id == goal.id,
                ConceptVisit.concept_node_id == concept_id,
            )
        )
    ).scalar_one_or_none()
    if visit is None:
        visit = ConceptVisit(
            user_id=user.id,
            user_goal_id=goal.id,
            concept_node_id=concept_id,
            visit_count=1,
            last_visited_at=utcnow(),
        )
        db.add(visit)
    else:
        visit.visit_count = (visit.visit_count or 0) + 1
        visit.last_visited_at = utcnow()

    completion_count = (
        await db.execute(
            select(func.count()).select_from(LessonCompletion).where(
                LessonCompletion.user_id == user.id,
                LessonCompletion.user_goal_id == goal.id,
                LessonCompletion.concept_node_id == concept_id,
            )
        )
    ).scalar_one()

    await db.flush()
    return visit.visit_count, int(completion_count or 0), visit.last_visited_at


@router.get("/content/{goal_id}/{concept_id}")
async def get_content(
    goal_id: str,
    concept_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal, node, profile = await _load_context(db, goal_id, concept_id, user)

    visit_count, completion_count, last_visited_at = await _record_visit_and_counts(
        db, user, goal, concept_id
    )

    contract = (
        await db.execute(select(GenerationContract).where(GenerationContract.is_active.is_(True)))
    ).scalar_one_or_none()
    if contract is None:
        raise HTTPException(500, "No active GenerationContract")

    gap_map = goal.concept_gap_map or {}
    sig, sig_inputs = compute_signature(
        goal.topic_id,
        concept_id,
        gap_map.get(concept_id),
        goal.root_gap_concepts or [],
        profile.learning_style,
        profile.tone_preference,
    )

    content = (
        await db.execute(
            select(GeneratedContent).where(
                GeneratedContent.signature == sig,
                GeneratedContent.generation_contract_version == contract.version,
            ).order_by(GeneratedContent.created_at.desc())
        )
    ).scalars().first()

    if content is not None and content.status != "failed":
        await db.commit()
        return _content_payload(
            content,
            visit_count=visit_count,
            completion_count=completion_count,
            last_visited_at=last_visited_at,
        )

    # MISS (or previous failure): create a pending row and enqueue generation
    content = GeneratedContent(
        signature=sig,
        signature_inputs=sig_inputs,
        topic_id=goal.topic_id,
        concept_node_id=concept_id,
        generation_contract_version=contract.version,
        status="pending",
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)
    if settings.celery_task_always_eager:
        # dev mode without a worker: run the pipeline inline on this event loop
        await _run_generation(content.id)
        await db.refresh(content)
    else:
        generate_content.delay(content.id)
    return _content_payload(
        content,
        visit_count=visit_count,
        completion_count=completion_count,
        last_visited_at=last_visited_at,
    )


@router.get("/content/status/{content_id}")
async def poll_content(content_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    content = await db.get(GeneratedContent, content_id)
    if content is None:
        raise HTTPException(404, "Content not found")
    return _content_payload(content)


@router.post("/content/verify-sandbox")
async def verify_sandbox(
    payload: SandboxVerifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Live Check for sandbox SQL — re-verifies on the server."""
    _ = user
    solution_sql = payload.solution_sql
    dataset = payload.dataset
    order_sensitive = payload.order_sensitive

    if payload.generated_content_id is not None and payload.question_index is not None:
        content = await db.get(GeneratedContent, payload.generated_content_id)
        if content is None or not content.quiz_body:
            raise HTTPException(404, "Content not found")
        questions = content.quiz_body.get("questions", [])
        if not (0 <= payload.question_index < len(questions)):
            raise HTTPException(422, "Invalid question index")
        q = questions[payload.question_index]
        if q.get("type") != "sandbox_sql":
            raise HTTPException(422, "Not a sandbox question")
        solution_sql = q.get("solution_sql")
        dataset = q.get("dataset")
        order_sensitive = q.get("order_sensitive", False)

    if not solution_sql or not dataset:
        raise HTTPException(422, "Missing dataset or solution")

    result = verify_sandbox_answer(
        dataset,
        payload.user_sql,
        solution_sql,
        order_sensitive=order_sensitive,
    )
    return {
        "passed": result.get("passed", False),
        "column_match": result.get("column_match", False),
        "row_count_match": result.get("row_count_match", False),
        "expected_row_count": result.get("expected_row_count"),
        "actual_row_count": result.get("actual_row_count"),
        "expected_columns": result.get("expected_columns"),
        "actual_columns": result.get("actual_columns"),
        "issues": result.get("issues", []),
        "error": result.get("error"),
        "expected": result.get("expected"),
        "actual": result.get("actual"),
    }


@router.post("/content/{goal_id}/{concept_id}/submit-quiz")
async def submit_quiz(
    goal_id: str,
    concept_id: str,
    payload: QuizSubmission,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal, node, _profile = await _load_context(db, goal_id, concept_id, user)
    content = await db.get(GeneratedContent, payload.generated_content_id)
    if content is None or content.status != "ready" or not content.quiz_body:
        raise HTTPException(409, "Content not ready")

    questions = content.quiz_body.get("questions", [])
    difficulty = _DIFFICULTY_TO_QUIZ.get(node.difficulty_tag, "medium")
    quiz_mode = content.quiz_body.get("mode", "classic")

    responses: list[dict] = []
    review: list[dict] = []
    sandbox_scores: list[float] = []
    mcq_scores: list[float] = []

    for ans in payload.answers:
        if not (0 <= ans.question_index < len(questions)):
            continue
        q = questions[ans.question_index]
        qtype = q.get("type")
        record: dict = {
            "question_id": f"{content.id}:{ans.question_index}",
            "concept_node_id": concept_id,
            "difficulty": difficulty,
            "type": qtype,
            "question_text": q.get("question_text"),
        }
        if qtype == "sandbox_sql":
            user_sql = (ans.user_sql or "").strip()
            verification = verify_sandbox_answer(
                q.get("dataset", ""),
                user_sql,
                q.get("solution_sql", ""),
                order_sensitive=q.get("order_sensitive", False),
            )
            passed = verification.get("passed", False)
            col_match = verification.get("column_match", False)
            if passed:
                score = 1.0
            elif col_match:
                score = 0.5
            else:
                score = 0.0
            sandbox_scores.append(score)
            record["user_sql"] = user_sql
            record["correct"] = passed
            record["score"] = score
            review.append({
                "question_index": ans.question_index,
                "correct": passed,
                "score": score,
                "explanation": q.get("explanation"),
                "issues": verification.get("issues", []),
                "user_sql": user_sql,
            })
        elif qtype == "multiple_choice":
            correct = ans.selected_option == q.get("correct_option")
            mcq_scores.append(1.0 if correct else 0.0)
            record["selected_option"] = ans.selected_option
            record["correct"] = correct
            review.append({
                "question_index": ans.question_index,
                "correct": correct,
                "correct_option": q.get("correct_option"),
                "explanation": q.get("explanation"),
            })
        else:
            record["answer_text"] = ans.answer_text or ""
            record["expected_concepts"] = q.get("expected_concepts") or []
            correct = keyword_overlap_score(record["answer_text"], record["expected_concepts"]) >= 0.5
            mcq_scores.append(1.0 if correct else 0.0)
            review.append({
                "question_index": ans.question_index,
                "correct": correct,
                "explanation": q.get("explanation"),
            })
        responses.append(record)

    if not responses:
        raise HTTPException(422, "No valid answers submitted")

    # Weighted quiz score: sandbox 50%, MCQ split remaining in mixed mode
    if quiz_mode in ("sandbox", "mixed") and sandbox_scores:
        sandbox_avg = sum(sandbox_scores) / len(sandbox_scores)
        if mcq_scores:
            mcq_avg = sum(mcq_scores) / len(mcq_scores)
            raw_quiz_score = sandbox_avg * 50 + mcq_avg * 50
        else:
            raw_quiz_score = sandbox_avg * 100
    else:
        all_scores = sandbox_scores + mcq_scores
        raw_quiz_score = (sum(all_scores) / len(all_scores) * 100) if all_scores else 0.0

    # Evaluator light re-scoring pass: blends new evidence into the gap map and
    # re-runs graph traversal to check whether root gaps are resolved.
    prior_root_gaps = set(goal.root_gap_concepts or [])
    prior_score = (goal.concept_gap_map or {}).get(concept_id)
    completed = set(goal.completed_concepts or [])

    output = await evaluator.evaluate(
        db,
        goal.topic_id,
        responses,
        completed_concepts=completed | {concept_id},
        prior_gap_map=dict(goal.concept_gap_map or {}),
    )

    raw_quiz_score = round(raw_quiz_score, 1)
    quiz_score = raw_quiz_score
    new_score = output["concept_scores"].get(concept_id)
    delta = (new_score - prior_score) if (prior_score is not None and new_score is not None) else (new_score or 0.0)

    goal.concept_gap_map = output["concept_scores"]
    goal.root_gap_concepts = output["root_gap_concepts"]
    if concept_id not in completed:
        goal.completed_concepts = sorted(completed | {concept_id})

    completion = LessonCompletion(
        user_id=user.id,
        user_goal_id=goal.id,
        concept_node_id=concept_id,
        generated_content_id=content.id,
        quiz_score=quiz_score,
        concept_score_delta=round(delta, 1),
    )
    db.add(completion)
    await db.flush()

    # Gamification: XP, streak, badges
    earned_xp = xp_service.lesson_xp(node.difficulty_tag, quiz_score)
    await xp_service.award_xp(db, user.id, earned_xp, "lesson_complete", completion.id)
    streak, extended, broken, previous_streak = await xp_service.touch_streak(db, user.id)
    if extended and streak.current_streak > 1 and not broken:
        await xp_service.award_xp(db, user.id, xp_service.XP_STREAK_BONUS, "streak_bonus")
        earned_xp += xp_service.XP_STREAK_BONUS

    root_gap_resolved = concept_id in prior_root_gaps and concept_id not in set(output["root_gap_concepts"])
    lessons_total = len(goal.completed_concepts or [])
    badges = await xp_service.check_and_award_badges(
        db, user.id, goal=goal,
        root_gap_resolved=root_gap_resolved,
        lessons_completed_total=lessons_total,
        quiz_score=quiz_score,
    )

    # Include milestone XP in the reported earn total
    earned_xp += xp_service.XP_MILESTONE * len(badges)

    await db.flush()
    total = await xp_service.total_xp(db, user.id)
    progress = xp_service.level_from_xp(total)

    await db.commit()

    streak_info = xp_service.streak_payload(streak)
    streak_info["extended"] = extended
    streak_info["broken"] = broken
    streak_info["previous"] = previous_streak if broken else None
    if broken and previous_streak > 0:
        streak_info["message"] = (
            f"Your {previous_streak}-day streak was lost. Starting a new one today."
        )
    elif extended and streak.current_streak > 1:
        streak_info["message"] = f"Streak extended to {streak.current_streak} days!"
    else:
        streak_info["message"] = None

    return {
        "quiz_score": quiz_score,
        "raw_quiz_score": round(raw_quiz_score, 1),
        "quiz_mode": quiz_mode,
        "concept_score_delta": round(delta, 1),
        "review": review,
        "xp_earned": earned_xp,
        "streak": streak_info,
        "badges_earned": [{"id": b.id, "name": b.name, "description": b.description} for b in badges],
        "level": progress["level"],
        "xp_into_level": progress["xp_into_level"],
        "xp_to_next_level": progress["xp_to_next_level"],
        "next_level_at": progress["next_level_at"],
        "total_xp": total,
        "root_gap_resolved": root_gap_resolved,
        "root_gap_concepts": output["root_gap_concepts"],
        "gap_reasoning": output["gap_reasoning"],
    }
