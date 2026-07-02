from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Category, ConceptNode, Topic, User

router = APIRouter()


@router.get("/catalog")
async def get_catalog(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
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
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "topics": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "concept_count": counts.get(t.id, 0),
                }
                for t in topics if t.category_id == c.id
            ],
        }
        for c in categories
    ]
