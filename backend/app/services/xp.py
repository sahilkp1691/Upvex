"""XP, streaks, and badge awarding — the gamification engine."""

from datetime import datetime, timedelta, timezone
from math import floor, sqrt

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Badge, Streak, User, UserBadge, UserGoal, XPLedger

XP_LESSON_BASE = 50
XP_QUIZ_MAX_BONUS = 50  # scaled by quiz score
XP_DIFFICULTY_MULT = {"beginner": 1.0, "intermediate": 1.25, "advanced": 1.5}
XP_STREAK_BONUS = 20
XP_MILESTONE = 100

# Quadratic XP curve: cumulative XP to reach level L is ~100 * (L-1)^2.
# Level 1 @ 0, Level 2 @ 100, Level 3 @ 400, Level 4 @ 900, …
_LEVEL_XP_BASE = 100


def xp_for_level(level: int) -> int:
    """Cumulative XP required to *reach* this level (level 1 = 0)."""
    if level <= 1:
        return 0
    return _LEVEL_XP_BASE * (level - 1) ** 2


def level_from_xp(total: int) -> dict:
    """Derive level progress from total lifetime XP."""
    total = max(0, int(total))
    # Invert: level = floor(sqrt(total / base)) + 1
    level = floor(sqrt(total / _LEVEL_XP_BASE)) + 1
    floor_xp = xp_for_level(level)
    next_at = xp_for_level(level + 1)
    into = total - floor_xp
    to_next = next_at - total
    return {
        "level": level,
        "xp_into_level": into,
        "xp_to_next_level": to_next,
        "next_level_at": next_at,
        "level_floor_xp": floor_xp,
    }


async def award_xp(db: AsyncSession, user_id: str, amount: int, reason: str, related_id: str | None = None) -> XPLedger:
    entry = XPLedger(user_id=user_id, amount=amount, reason=reason, related_id=related_id)
    db.add(entry)
    return entry


def lesson_xp(difficulty_tag: str, quiz_score: float) -> int:
    mult = XP_DIFFICULTY_MULT.get(difficulty_tag, 1.0)
    return int((XP_LESSON_BASE + XP_QUIZ_MAX_BONUS * (quiz_score / 100)) * mult)


async def touch_streak(db: AsyncSession, user_id: str) -> tuple[Streak, bool]:
    """Record activity today. Returns (streak, extended) — extended True when the
    streak counter grew (used to trigger streak bonus XP)."""
    today = datetime.now(timezone.utc).date()
    streak = await db.get(Streak, user_id)
    if streak is None:
        streak = Streak(user_id=user_id, current_streak=1, longest_streak=1, last_active_date=today)
        db.add(streak)
        return streak, True

    if streak.last_active_date == today:
        return streak, False
    if streak.last_active_date == today - timedelta(days=1):
        streak.current_streak += 1
    else:
        streak.current_streak = 1
    streak.last_active_date = today
    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    return streak, True


async def total_xp(db: AsyncSession, user_id: str) -> int:
    result = await db.execute(
        select(func.coalesce(func.sum(XPLedger.amount), 0)).where(XPLedger.user_id == user_id)
    )
    return int(result.scalar_one())


async def weekly_xp(db: AsyncSession, user_id: str, *, days: int = 7) -> int:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(func.coalesce(func.sum(XPLedger.amount), 0)).where(
            XPLedger.user_id == user_id,
            XPLedger.created_at >= since,
        )
    )
    return int(result.scalar_one())


async def leaderboard(db: AsyncSession, *, days: int = 7, limit: int = 20) -> list[dict]:
    """Weekly XP ranking (cohort = all users in v1)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = await db.execute(
        select(
            User.id,
            User.display_name,
            func.coalesce(func.sum(XPLedger.amount), 0).label("xp"),
        )
        .join(XPLedger, XPLedger.user_id == User.id)
        .where(XPLedger.created_at >= since)
        .group_by(User.id, User.display_name)
        .order_by(func.sum(XPLedger.amount).desc())
        .limit(limit)
    )
    return [
        {"rank": i + 1, "user_id": uid, "display_name": name or "Learner", "xp": int(xp)}
        for i, (uid, name, xp) in enumerate(rows.all())
    ]


async def user_weekly_rank(db: AsyncSession, user_id: str, *, days: int = 7) -> tuple[int | None, int]:
    """Return (rank, weekly_xp). Rank is None only if the user has 0 weekly XP."""
    my_xp = await weekly_xp(db, user_id, days=days)
    if my_xp <= 0:
        return None, 0
    since = datetime.now(timezone.utc) - timedelta(days=days)
    # Count distinct users with strictly more weekly XP
    subq = (
        select(XPLedger.user_id, func.sum(XPLedger.amount).label("xp"))
        .where(XPLedger.created_at >= since)
        .group_by(XPLedger.user_id)
        .having(func.sum(XPLedger.amount) > my_xp)
        .subquery()
    )
    result = await db.execute(select(func.count()).select_from(subq))
    higher = int(result.scalar_one())
    return higher + 1, my_xp


async def _has_badge(db: AsyncSession, user_id: str, badge_id: str) -> bool:
    row = await db.execute(
        select(UserBadge.id).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)
    )
    return row.scalar_one_or_none() is not None


async def check_and_award_badges(
    db: AsyncSession,
    user_id: str,
    *,
    goal: UserGoal | None = None,
    root_gap_resolved: bool = False,
    lessons_completed_total: int | None = None,
    quiz_score: float | None = None,
) -> list[Badge]:
    """Evaluate badge criteria against the current event context. Awards + XP."""
    badges = (await db.execute(select(Badge))).scalars().all()
    streak = await db.get(Streak, user_id)
    awarded: list[Badge] = []

    for badge in badges:
        criteria = badge.criteria or {}
        ctype = criteria.get("type")
        earned = False
        if ctype == "first_lesson":
            earned = (lessons_completed_total or 0) >= 1
        elif ctype == "root_gap_resolved":
            earned = root_gap_resolved
        elif ctype == "concepts_completed" and goal is not None:
            earned = len(goal.completed_concepts or []) >= int(criteria.get("count", 0))
        elif ctype == "streak_days" and streak is not None:
            earned = streak.current_streak >= int(criteria.get("days", 0))
        elif ctype == "perfect_quiz":
            earned = quiz_score is not None and quiz_score >= 100

        if earned and not await _has_badge(db, user_id, badge.id):
            db.add(UserBadge(user_id=user_id, badge_id=badge.id))
            await award_xp(db, user_id, XP_MILESTONE, "milestone", badge.id)
            awarded.append(badge)

    return awarded
