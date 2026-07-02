from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Badge, Streak, User, UserBadge, XPLedger
from ..services import xp as xp_service

router = APIRouter()


@router.get("/gamification/summary")
async def summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total = await xp_service.total_xp(db, user.id)
    streak = await db.get(Streak, user.id)
    badge_rows = (
        await db.execute(
            select(Badge, UserBadge.earned_at)
            .join(UserBadge, UserBadge.badge_id == Badge.id)
            .where(UserBadge.user_id == user.id)
            .order_by(UserBadge.earned_at.desc())
        )
    ).all()
    recent_xp = (
        await db.execute(
            select(XPLedger).where(XPLedger.user_id == user.id)
            .order_by(XPLedger.created_at.desc()).limit(10)
        )
    ).scalars().all()
    return {
        "total_xp": total,
        "streak": {
            "current": streak.current_streak if streak else 0,
            "longest": streak.longest_streak if streak else 0,
            "last_active_date": streak.last_active_date.isoformat() if streak and streak.last_active_date else None,
        },
        "badges": [
            {"id": b.id, "name": b.name, "description": b.description, "earned_at": earned.isoformat()}
            for b, earned in badge_rows
        ],
        "recent_xp": [
            {"amount": e.amount, "reason": e.reason, "created_at": e.created_at.isoformat()}
            for e in recent_xp
        ],
    }


@router.get("/gamification/leaderboard")
async def get_leaderboard(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = await xp_service.leaderboard(db, days=7, limit=20)
    me_rank = next((r["rank"] for r in rows if r["user_id"] == user.id), None)
    return {"window_days": 7, "entries": rows, "my_rank": me_rank}


@router.get("/gamification/badges")
async def all_badges(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    badges = (await db.execute(select(Badge))).scalars().all()
    earned_ids = {
        ub.badge_id for ub in (
            await db.execute(select(UserBadge).where(UserBadge.user_id == user.id))
        ).scalars().all()
    }
    return [
        {"id": b.id, "name": b.name, "description": b.description, "earned": b.id in earned_ids}
        for b in badges
    ]
