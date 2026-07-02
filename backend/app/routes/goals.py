from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import ConceptNode, Topic, User, UserGoal

router = APIRouter()

PACING_DAYS_PER_CONCEPT = {"casual": 5, "regular": 3, "intense": 1}


class CreateGoalPayload(BaseModel):
    topic_id: str


class PacingPayload(BaseModel):
    pacing_choice: str = Field(pattern="^(casual|regular|intense)$")


def _goal_dict(goal: UserGoal, topic_name: str | None = None) -> dict:
    return {
        "id": goal.id,
        "topic_id": goal.topic_id,
        "topic_name": topic_name,
        "status": goal.status,
        "level_score": goal.level_score,
        "concept_gap_map": goal.concept_gap_map or {},
        "root_gap_concepts": goal.root_gap_concepts or [],
        "completed_concepts": goal.completed_concepts or [],
        "pacing_choice": goal.pacing_choice,
        "target_deadline": goal.target_deadline.isoformat() if goal.target_deadline else None,
        "created_at": goal.created_at.isoformat(),
    }


@router.get("/goals")
async def list_goals(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (
        await db.execute(
            select(UserGoal, Topic.name)
            .join(Topic, Topic.id == UserGoal.topic_id)
            .where(UserGoal.user_id == user.id)
            .order_by(UserGoal.created_at.desc())
        )
    ).all()
    return [_goal_dict(g, name) for g, name in rows]


@router.post("/goals")
async def create_goal(
    payload: CreateGoalPayload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    topic = await db.get(Topic, payload.topic_id)
    if topic is None or not topic.is_active:
        raise HTTPException(404, "Topic not found")
    existing = (
        await db.execute(
            select(UserGoal).where(UserGoal.user_id == user.id, UserGoal.topic_id == payload.topic_id)
        )
    ).scalar_one_or_none()
    if existing:
        return _goal_dict(existing, topic.name)
    goal = UserGoal(user_id=user.id, topic_id=payload.topic_id, status="diagnostic_pending")
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return _goal_dict(goal, topic.name)


@router.get("/goals/{goal_id}")
async def get_goal(goal_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    goal = await db.get(UserGoal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    topic = await db.get(Topic, goal.topic_id)
    return _goal_dict(goal, topic.name if topic else None)


@router.patch("/goals/{goal_id}/pacing")
async def set_pacing(
    goal_id: str,
    payload: PacingPayload,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    goal = await db.get(UserGoal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    goal.pacing_choice = payload.pacing_choice

    # Overall target deadline: remaining concepts x days-per-concept for the pacing
    node_count = len(
        (await db.execute(select(ConceptNode.id).where(ConceptNode.topic_id == goal.topic_id))).all()
    )
    gap_map = goal.concept_gap_map or {}
    done_or_tested = set(goal.completed_concepts or []) | {
        cid for cid, s in gap_map.items() if s is not None and s >= 80
    }
    remaining = max(1, node_count - len(done_or_tested))
    days = remaining * PACING_DAYS_PER_CONCEPT[payload.pacing_choice]
    goal.target_deadline = date.today() + timedelta(days=days)

    await db.commit()
    topic = await db.get(Topic, goal.topic_id)
    return _goal_dict(goal, topic.name if topic else None)
