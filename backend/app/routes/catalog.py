from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Category, ConceptNode, Topic, User

router = APIRouter()


@router.get("/catalog")
async def get_catalog(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from ..services import diagnostic_bank as bank

    categories = (
        await db.execute(select(Category).where(Category.is_active.is_(True)))
    ).scalars().all()
    topics = (
        await db.execute(select(Topic).where(Topic.is_active.is_(True)))
    ).scalars().all()
    counts = dict(
        (await db.execute(
            select(ConceptNode.topic_id, func.count()).group_by(ConceptNode.topic_id)
        )).all()
    )
    topic_payloads = []
    for t in topics:
        ready = await bank.readiness(db, t.id)
        topic_payloads.append(
            {
                "id": t.id,
                "category_id": t.category_id,
                "name": t.name,
                "description": t.description,
                "concept_count": counts.get(t.id, 0),
                "diagnostic_ready": ready["ready"],
                "diagnostic_question_count": ready["question_count"],
                "diagnostic_message": ready["message"],
            }
        )
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "topics": [tp for tp in topic_payloads if tp["category_id"] == c.id],
        }
        for c in categories
    ]
