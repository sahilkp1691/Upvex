from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Topic, User, UserGoal
from ..services import sequencing

router = APIRouter()


@router.get("/roadmap/{goal_id}")
async def get_roadmap(goal_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    goal = await db.get(UserGoal, goal_id)
    if goal is None or goal.user_id != user.id:
        raise HTTPException(404, "Goal not found")
    if goal.status == "diagnostic_pending":
        raise HTTPException(409, "Diagnostic not completed yet")
    topic = await db.get(Topic, goal.topic_id)
    roadmap = await sequencing.build_roadmap(db, goal)
    titles = {n["id"]: n["title"] for n in roadmap["nodes"]}
    for node in roadmap["nodes"]:
        node["blocked_by_titles"] = [titles.get(b, b) for b in node["blocked_by"]]
    return {
        "goal_id": goal.id,
        "topic_id": goal.topic_id,
        "topic_name": topic.name if topic else None,
        "level_score": goal.level_score,
        "pacing_choice": goal.pacing_choice,
        "target_deadline": goal.target_deadline.isoformat() if goal.target_deadline else None,
        **roadmap,
    }
