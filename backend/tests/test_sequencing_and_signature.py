"""Sequencing state labels and ProfileSignature computation."""

import pytest

from app.models import UserGoal
from app.services.sequencing import build_roadmap
from app.services.signature import compute_signature, difficulty_band

pytestmark = pytest.mark.anyio


def make_goal(**kwargs):
    defaults = dict(
        id="g1", user_id="u1", topic_id="t1", status="active",
        concept_gap_map={}, root_gap_concepts=[], completed_concepts=[],
    )
    defaults.update(kwargs)
    return UserGoal(**defaults)


async def test_untested_graph_unlocks_only_roots(db):
    goal = make_goal()
    roadmap = await build_roadmap(db, goal)
    states = {n["id"]: n["state"] for n in roadmap["nodes"]}
    # roots have no required prereqs -> unlocked; downstream locked
    assert states["storage"] in ("available", "recommended_next")
    assert states["arch"] in ("available", "recommended_next")
    assert states["partitioning"] == "locked"
    assert states["shuffles"] == "locked"


async def test_root_gap_recommended_first(db):
    goal = make_goal(
        concept_gap_map={"storage": 30.0, "arch": 90.0, "partitioning": 40.0},
        root_gap_concepts=["storage"],
    )
    roadmap = await build_roadmap(db, goal)
    states = {n["id"]: n["state"] for n in roadmap["nodes"]}
    assert states["storage"] == "recommended_next"
    assert states["arch"] == "tested_out"


async def test_high_score_tests_out_and_unlocks_downstream(db):
    goal = make_goal(concept_gap_map={"storage": 85.0, "arch": 85.0})
    roadmap = await build_roadmap(db, goal)
    states = {n["id"]: n["state"] for n in roadmap["nodes"]}
    assert states["storage"] == "tested_out"
    # both prereqs met -> partitioning unlocked
    assert states["partitioning"] in ("available", "recommended_next")


async def test_completion_unlocks_downstream(db):
    goal = make_goal(
        completed_concepts=["storage", "arch", "partitioning"],
        concept_gap_map={"storage": 75.0, "arch": 75.0, "partitioning": 70.0},
    )
    roadmap = await build_roadmap(db, goal)
    states = {n["id"]: n["state"] for n in roadmap["nodes"]}
    assert states["partitioning"] == "completed"
    assert states["shuffles"] in ("available", "recommended_next")
    assert states["optimization"] == "locked"


async def test_locked_nodes_list_blockers(db):
    goal = make_goal()
    roadmap = await build_roadmap(db, goal)
    shuffles = next(n for n in roadmap["nodes"] if n["id"] == "shuffles")
    assert "partitioning" in shuffles["blocked_by"]


# ---- ProfileSignature ----

def test_difficulty_bands():
    assert difficulty_band(None) == "untested"
    assert difficulty_band(20) == "novice"
    assert difficulty_band(55) == "developing"
    assert difficulty_band(85) == "proficient"


def test_signature_stable_and_sensitive():
    sig1, inputs1 = compute_signature("t1", "c1", 50.0, ["gap1"], "visual", "playful")
    sig2, _ = compute_signature("t1", "c1", 55.0, ["gap1"], "visual", "playful")  # same band
    sig3, _ = compute_signature("t1", "c1", 50.0, ["gap1"], "reading", "playful")
    sig4, _ = compute_signature("t1", "c1", 90.0, ["gap1"], "visual", "playful")  # different band
    assert sig1 == sig2, "same band + style -> cache hit"
    assert sig1 != sig3, "learning style changes signature"
    assert sig1 != sig4, "difficulty band changes signature"
    assert inputs1["primary_root_gap"] == "gap1"


def test_signature_ignores_self_root_gap():
    # if the concept IS the root gap, it shouldn't fragment its own cache key
    sig_a, inputs = compute_signature("t1", "c1", None, ["c1"], "visual", "neutral")
    sig_b, _ = compute_signature("t1", "c1", None, [], "visual", "neutral")
    assert sig_a == sig_b
    assert inputs["primary_root_gap"] == ""
