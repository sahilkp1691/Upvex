from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import ConceptVisit, LessonCompletion, Topic, User, UserGoal
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

    visit_rows = (
        await db.execute(
            select(ConceptVisit.concept_node_id, ConceptVisit.visit_count).where(
                ConceptVisit.user_id == user.id,
                ConceptVisit.user_goal_id == goal.id,
            )
        )
    ).all()
    visit_map = {cid: count for cid, count in visit_rows}

    completion_rows = (
        await db.execute(
            select(LessonCompletion.concept_node_id, func.count())
            .where(
                LessonCompletion.user_id == user.id,
                LessonCompletion.user_goal_id == goal.id,
            )
            .group_by(LessonCompletion.concept_node_id)
        )
    ).all()
    completion_map = {cid: int(count) for cid, count in completion_rows}

    for node in roadmap["nodes"]:
        node["visit_count"] = visit_map.get(node["id"], 0)
        node["completion_count"] = completion_map.get(node["id"], 0)

    return {
        "goal_id": goal.id,
        "topic_id": goal.topic_id,
        "topic_name": topic.name if topic else None,
        "level_score": goal.level_score,
        "pacing_choice": goal.pacing_choice,
        "target_deadline": goal.target_deadline.isoformat() if goal.target_deadline else None,
        **roadmap,
    }
