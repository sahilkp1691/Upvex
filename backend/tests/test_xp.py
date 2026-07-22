"""Unit tests for XP level curve and lesson XP."""

from app.services.xp import level_from_xp, lesson_xp, xp_for_level


def test_xp_for_level_floor():
    assert xp_for_level(1) == 0
    assert xp_for_level(2) == 100
    assert xp_for_level(3) == 400
    assert xp_for_level(4) == 900


def test_level_from_xp_boundaries():
    assert level_from_xp(0)["level"] == 1
    assert level_from_xp(99)["level"] == 1
    assert level_from_xp(100)["level"] == 2
    assert level_from_xp(399)["level"] == 2
    assert level_from_xp(400)["level"] == 3

    p = level_from_xp(150)
    assert p["level"] == 2
    assert p["xp_into_level"] == 50
    assert p["xp_to_next_level"] == 250
    assert p["next_level_at"] == 400


def test_lesson_xp_scales():
    assert lesson_xp("beginner", 0) == 50
    assert lesson_xp("beginner", 100) == 100
    assert lesson_xp("advanced", 100) == 150
