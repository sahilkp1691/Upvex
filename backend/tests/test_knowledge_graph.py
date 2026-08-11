"""Unit tests for the free in-process knowledge graph runtime."""

from app.services.knowledge_graph import KnowledgeGraph, WEAK_THRESHOLD


def _sample_graph() -> KnowledgeGraph:
    # arch -> storage -> partitioning -> shuffles -> optimization
    kg = KnowledgeGraph(topic_id="t1")
    for nid, title, is_root in [
        ("arch", "Architecture", True),
        ("storage", "Storage", False),
        ("partitioning", "Partitioning", False),
        ("shuffles", "Shuffles", False),
        ("optimization", "Optimization", False),
        ("orphan", "Orphan", False),
    ]:
        kg.add_node(nid, title=title, is_root=is_root)
    kg.add_edge("arch", "storage")
    kg.add_edge("storage", "partitioning")
    kg.add_edge("partitioning", "shuffles")
    kg.add_edge("shuffles", "optimization")
    return kg


def test_ancestors_and_descendants():
    kg = _sample_graph()
    assert kg.ancestors("optimization") == {"shuffles", "partitioning", "storage", "arch"}
    assert kg.ancestors("partitioning") == {"storage", "arch"}
    assert kg.ancestors("storage") == {"arch"}
    assert kg.descendants("storage") == {"partitioning", "shuffles", "optimization"}


def test_shortest_path():
    kg = _sample_graph()
    assert kg.shortest_path("arch", "shuffles") == ["arch", "storage", "partitioning", "shuffles"]
    assert kg.shortest_path("shuffles", "arch") is None


def test_would_create_cycle():
    kg = _sample_graph()
    assert kg.would_create_cycle("optimization", "arch") is True
    assert kg.would_create_cycle("arch", "optimization") is False  # already exists path; adding parallel ok
    assert kg.would_create_cycle("storage", "arch") is True


def test_root_gaps_trace_to_common_ancestor():
    kg = _sample_graph()
    gap_map = {"partitioning": 35.0, "shuffles": 40.0, "arch": 90.0}
    roots = kg.find_root_gaps(gap_map)
    assert roots[0] == "storage"


def test_validate_reports_orphan():
    kg = _sample_graph()
    report = kg.validate()
    assert report["ok"] is False
    codes = {i["code"] for i in report["issues"]}
    assert "orphan" in codes


def test_validate_clean_dag():
    kg = KnowledgeGraph(topic_id="t2")
    kg.add_node("a", title="A", is_root=True)
    kg.add_node("b", title="B", is_root=False)
    kg.add_edge("a", "b")
    report = kg.validate()
    assert report["ok"] is True
    assert report["engine"] == "memory"
    assert WEAK_THRESHOLD == 60
