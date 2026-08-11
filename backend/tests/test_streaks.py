"""Streak sync, breakage, and at-risk warning tests."""

from datetime import date, timedelta

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database import Base
from app.models import Streak
from app.services import xp as xp_service

pytestmark = pytest.mark.anyio


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite://")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


async def test_sync_resets_missed_streak(db):
    today = date(2026, 8, 11)
    db.add(
        Streak(
            user_id="u1",
            current_streak=5,
            longest_streak=9,
            last_active_date=today - timedelta(days=2),
        )
    )
    await db.commit()

    streak, broken_from = await xp_service.sync_streak(db, "u1", today=today)
    assert broken_from == 5
    assert streak.current_streak == 0
    assert streak.longest_streak == 9


async def test_sync_keeps_at_risk_streak(db):
    today = date(2026, 8, 11)
    db.add(
        Streak(
            user_id="u1",
            current_streak=3,
            longest_streak=3,
            last_active_date=today - timedelta(days=1),
        )
    )
    await db.commit()

    streak, broken_from = await xp_service.sync_streak(db, "u1", today=today)
    assert broken_from == 0
    assert streak.current_streak == 3
    payload = xp_service.streak_payload(streak, today=today)
    assert payload["status"] == "at_risk"
    assert "lose your 3-day streak" in payload["warning"]


async def test_touch_extends_yesterday(db):
    today = date(2026, 8, 11)
    db.add(
        Streak(
            user_id="u1",
            current_streak=2,
            longest_streak=2,
            last_active_date=today - timedelta(days=1),
        )
    )
    await db.commit()

    streak, extended, broken, previous = await xp_service.touch_streak(db, "u1", today=today)
    assert extended is True
    assert broken is False
    assert previous == 0
    assert streak.current_streak == 3
    assert streak.last_active_date == today


async def test_touch_reports_break_and_restarts(db):
    today = date(2026, 8, 11)
    db.add(
        Streak(
            user_id="u1",
            current_streak=7,
            longest_streak=10,
            last_active_date=today - timedelta(days=3),
        )
    )
    await db.commit()

    streak, extended, broken, previous = await xp_service.touch_streak(db, "u1", today=today)
    assert extended is True
    assert broken is True
    assert previous == 7
    assert streak.current_streak == 1
    assert streak.longest_streak == 10


async def test_streak_payload_active_today(db):
    today = date(2026, 8, 11)
    streak = Streak(user_id="u1", current_streak=4, longest_streak=4, last_active_date=today)
    payload = xp_service.streak_payload(streak, today=today)
    assert payload["status"] == "active_today"
    assert payload["warning"] is None
