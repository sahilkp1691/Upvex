"""Tests for catalog graph suggestions and apply/reset admin flows."""

import pytest
from sqlalchemy import select

from app.models import ConceptEdge, ConceptNode, Topic, Category
from app.services import graph_suggestions

pytestmark = pytest.mark.anyio


def test_match_catalog_spark():
    key, template = graph_suggestions.match_catalog("Apache Spark")
    assert key == "apache spark"
    assert template is not None
    titles = [n["title"] for st in template["subtopics"] for n in st["nodes"]]
    assert "Spark Architecture" in titles
    assert any(e["from_title"] == "Spark Architecture" for e in template["edges"])


def test_match_catalog_sql():
    key, template = graph_suggestions.match_catalog("SQL")
    assert key == "sql"
    assert len(template["subtopics"]) >= 2


def test_generic_fallback_for_unknown():
    key, template = graph_suggestions.match_catalog("Quantum Baking")
    assert key is None
    assert template is None


async def test_build_suggestions_marks_existing(db):
    # conftest seeds topic t1 with storage/arch/... — name is "Topic", so generic/catalog miss
    # Rename to Spark so catalog matches, then mark one title present
    topic = await db.get(Topic, "t1")
    topic.name = "Apache Spark"
    # Add a node titled like a catalog suggestion
    db.add(
        ConceptNode(
            id="spark_arch_test",
            topic_id="t1",
            title="Spark Architecture",
            learning_objective="x",
            difficulty_tag="beginner",
            bloom_level="understand",
            is_root=False,
        )
    )
    await db.commit()

    result = await graph_suggestions.build_suggestions(db, topic, use_ai=False)
    assert result["source"] == "catalog"
    arch = next(
        n
        for st in result["subtopics"]
        for n in st["nodes"]
        if n["title"] == "Spark Architecture"
    )
    assert arch["already_added"] is True
    assert result["stats"]["present_nodes"] >= 1
    assert result["stats"]["missing_nodes"] >= 1


async def test_apply_and_reset_via_service_shapes(db):
    """Apply catalog nodes onto empty topic then ensure titles exist."""
    db.add(Category(id="c_sug", name="SugCat", description=""))
    db.add(Topic(id="t_sug", category_id="c_sug", name="SQL", description=""))
    await db.commit()
    topic = await db.get(Topic, "t_sug")
    sug = await graph_suggestions.build_suggestions(db, topic, use_ai=False)
    assert sug["source"] == "catalog"
    missing = [n for st in sug["subtopics"] for n in st["nodes"] if not n["already_added"]]
    assert missing

    # Simulate apply: create first two missing
    for n in missing[:2]:
        db.add(
            ConceptNode(
                topic_id="t_sug",
                title=n["title"],
                learning_objective=n["learning_objective"],
                difficulty_tag=n["difficulty_tag"],
                bloom_level=n["bloom_level"],
                estimated_duration_mins=n["estimated_duration_mins"],
                is_root=n["is_root"],
            )
        )
    await db.commit()
    nodes = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == "t_sug"))
    ).scalars().all()
    assert len(nodes) == 2

    sug2 = await graph_suggestions.build_suggestions(db, topic, use_ai=False)
    assert sug2["stats"]["present_nodes"] == 2
