"""Deterministic graph traversal tests — root-gap detection over a known DAG."""

import pytest

from app.services import graph_traversal

pytestmark = pytest.mark.anyio


async def test_ancestors(db):
    ancestors = await graph_traversal.get_ancestors(db, "t1", "optimization")
    assert ancestors == {"shuffles", "partitioning", "storage", "arch"}

    ancestors = await graph_traversal.get_ancestors(db, "t1", "partitioning")
    assert ancestors == {"storage", "arch"}

    assert await graph_traversal.get_ancestors(db, "t1", "storage") == set()


async def test_descendants(db):
    descendants = await graph_traversal.get_descendants(db, "t1", "storage")
    assert descendants == {"partitioning", "shuffles", "optimization"}


async def test_root_gap_traces_to_common_ancestor(db):
    # weak on two downstream concepts, untested foundational ancestor -> root gap is the ancestor
    gap_map = {"partitioning": 35.0, "shuffles": 40.0, "arch": 90.0}
    roots = await graph_traversal.find_root_gaps(db, "t1", gap_map)
    # storage is untested (absent) and is an ancestor of both weak nodes; arch is strong
    assert roots[0] == "storage"


async def test_weak_node_with_strong_ancestors_is_its_own_root(db):
    gap_map = {"partitioning": 30.0, "storage": 85.0, "arch": 90.0}
    roots = await graph_traversal.find_root_gaps(db, "t1", gap_map)
    assert roots == ["partitioning"]


async def test_no_weak_concepts_no_root_gaps(db):
    gap_map = {"partitioning": 80.0, "shuffles": 75.0, "storage": 90.0}
    assert await graph_traversal.find_root_gaps(db, "t1", gap_map) == []


async def test_completed_concepts_excluded(db):
    gap_map = {"partitioning": 35.0, "storage": 30.0, "arch": 85.0}
    roots = await graph_traversal.find_root_gaps(db, "t1", gap_map, completed_concepts={"storage"})
    # storage is completed and arch is strong, so the weakness bottoms out at partitioning itself
    assert "storage" not in roots
    assert "partitioning" in roots
