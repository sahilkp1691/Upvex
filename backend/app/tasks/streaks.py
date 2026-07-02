"""Daily Celery beat job: evaluate streak continuation/breakage for all users.

Streaks are extended in real time when users complete lessons (services.xp.touch_streak);
this job handles the breakage side — resetting current_streak for users who missed a day.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from ..config import settings
from ..models import Streak
from .celery_app import celery_app

logger = logging.getLogger("upvex.streaks")


async def _run() -> int:
    connect_args = {}
    if settings.database_url.startswith("postgresql+asyncpg"):
        connect_args = {"statement_cache_size": 0}
    engine = create_async_engine(settings.database_url, connect_args=connect_args)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    broken = 0
    try:
        async with session_factory() as db:
            yesterday = datetime.now(timezone.utc).date() - timedelta(days=1)
            streaks = (
                await db.execute(select(Streak).where(Streak.current_streak > 0))
            ).scalars().all()
            for s in streaks:
                if s.last_active_date is None or s.last_active_date < yesterday:
                    s.current_streak = 0
                    broken += 1
            await db.commit()
    finally:
        await engine.dispose()
    return broken


@celery_app.task(name="app.tasks.streaks.evaluate_streaks")
def evaluate_streaks() -> int:
    broken = asyncio.run(_run())
    logger.info("Streak evaluation complete: %s streaks broken", broken)
    return broken
