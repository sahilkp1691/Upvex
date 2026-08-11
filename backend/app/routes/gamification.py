from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Badge, User, UserBadge, XPLedger
from ..services import xp as xp_service

router = APIRouter()


@router.get("/gamification/summary")
async def summary(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    total = await xp_service.total_xp(db, user.id)
    progress = xp_service.level_from_xp(total)
    streak, broken_from = await xp_service.sync_streak(db, user.id)
    if broken_from:
        await db.commit()
    else:
        await db.flush()
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
    streak_info = xp_service.streak_payload(streak)
    if broken_from:
        streak_info["just_broken"] = True
        streak_info["broken_from"] = broken_from
        streak_info["warning"] = (
            f"Your {broken_from}-day streak ended — practice today to start a new one."
        )
    else:
        streak_info["just_broken"] = False
        streak_info["broken_from"] = None
    return {
        "total_xp": total,
        "level": progress["level"],
        "xp_into_level": progress["xp_into_level"],
        "xp_to_next_level": progress["xp_to_next_level"],
        "next_level_at": progress["next_level_at"],
        "streak": streak_info,
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
    me_rank, my_xp = await xp_service.user_weekly_rank(db, user.id, days=7)
    me = None
    if me_rank is not None:
        me = {
            "rank": me_rank,
            "user_id": user.id,
            "display_name": user.display_name or "Learner",
            "xp": my_xp,
        }
    return {
        "window_days": 7,
        "entries": rows,
        "my_rank": me_rank,
        "my_xp": my_xp,
        "me": me,
    }


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
