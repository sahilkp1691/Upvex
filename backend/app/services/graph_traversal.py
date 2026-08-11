"""Knowledge-graph traversal over ConceptEdge.

Uses the free in-process KnowledgeGraph runtime (knowledge_graph.py) so multi-hop
queries and root-gap ranking stay fast without a separate graph database.
Recursive SQL CTEs are retained below for reference / AGE-less SQL debugging.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from .knowledge_graph import WEAK_THRESHOLD, load_topic_graph

UNTESTED_SCORE = None  # concepts absent from the gap map are untested

# Kept for SQL-level debugging / optional AGE hybrid paths.
_ANCESTORS_SQL = text("""
WITH RECURSIVE ancestors(concept_id, depth) AS (
    SELECT ce.from_concept_id, 1
    FROM concept_edges ce
    WHERE ce.to_concept_id = :concept_id AND ce.topic_id = :topic_id
    UNION
    SELECT ce.from_concept_id, a.depth + 1
    FROM concept_edges ce
    JOIN ancestors a ON ce.to_concept_id = a.concept_id
    WHERE ce.topic_id = :topic_id AND a.depth < 20
)
SELECT DISTINCT concept_id FROM ancestors
""")

_DESCENDANTS_SQL = text("""
WITH RECURSIVE descendants(concept_id, depth) AS (
    SELECT ce.to_concept_id, 1
    FROM concept_edges ce
    WHERE ce.from_concept_id = :concept_id AND ce.topic_id = :topic_id
    UNION
    SELECT ce.to_concept_id, d.depth + 1
    FROM concept_edges ce
    JOIN descendants d ON ce.from_concept_id = d.concept_id
    WHERE ce.topic_id = :topic_id AND d.depth < 20
)
SELECT DISTINCT concept_id FROM descendants
""")


async def get_ancestors(db: AsyncSession, topic_id: str, concept_id: str) -> set[str]:
    """All prerequisite concepts (direct and transitive) of a concept."""
    kg = await load_topic_graph(db, topic_id)
    return kg.ancestors(concept_id)


async def get_descendants(db: AsyncSession, topic_id: str, concept_id: str) -> set[str]:
    """All concepts that (directly or transitively) depend on a concept."""
    kg = await load_topic_graph(db, topic_id)
    return kg.descendants(concept_id)


def _is_weak_or_untested(concept_id: str, gap_map: dict[str, float]) -> bool:
    score = gap_map.get(concept_id)
    return score is None or score < WEAK_THRESHOLD


async def find_root_gaps(
    db: AsyncSession,
    topic_id: str,
    concept_gap_map: dict[str, float],
    completed_concepts: set[str] | None = None,
) -> list[str]:
    """Identify root gap concepts via the in-process knowledge graph."""
    kg = await load_topic_graph(db, topic_id)
    return kg.find_root_gaps(concept_gap_map, completed_concepts)
