"""Knowledge-graph traversal over ConceptEdge using recursive CTEs.

These are the deterministic queries behind root-gap detection (walk upstream from
weak concepts) and roadmap sequencing (prerequisite checks). Pure SQL, no LLM.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

WEAK_THRESHOLD = 60  # concept score below this counts as weak
UNTESTED_SCORE = None  # concepts absent from the gap map are untested

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
    rows = await db.execute(_ANCESTORS_SQL, {"concept_id": concept_id, "topic_id": topic_id})
    return {r[0] for r in rows}


async def get_descendants(db: AsyncSession, topic_id: str, concept_id: str) -> set[str]:
    """All concepts that (directly or transitively) depend on a concept."""
    rows = await db.execute(_DESCENDANTS_SQL, {"concept_id": concept_id, "topic_id": topic_id})
    return {r[0] for r in rows}


def _is_weak_or_untested(concept_id: str, gap_map: dict[str, float]) -> bool:
    score = gap_map.get(concept_id)
    return score is None or score < WEAK_THRESHOLD


async def find_root_gaps(
    db: AsyncSession,
    topic_id: str,
    concept_gap_map: dict[str, float],
    completed_concepts: set[str] | None = None,
) -> list[str]:
    """Identify root gap concepts: foundational weaknesses driving surface-level ones.

    For each weak concept, walk upstream through prerequisites. A weak/untested concept
    is a ROOT gap if none of its own ancestors are also weak/untested (i.e. the weakness
    chain bottoms out there). Weak concepts whose ancestors are all strong are their own
    root gaps. Results are ranked by how many weak concepts each root gap sits beneath.
    """
    completed = completed_concepts or set()
    weak = [
        cid for cid, score in concept_gap_map.items()
        if score is not None and score < WEAK_THRESHOLD and cid not in completed
    ]
    if not weak:
        return []

    impact: dict[str, int] = {}
    for weak_cid in weak:
        ancestors = await get_ancestors(db, topic_id, weak_cid)
        weak_ancestors = {
            a for a in ancestors
            if _is_weak_or_untested(a, concept_gap_map) and a not in completed
        }
        if not weak_ancestors:
            # weakness bottoms out at this concept itself
            impact[weak_cid] = impact.get(weak_cid, 0) + 1
            continue
        # roots among weak ancestors: those with no weak/untested ancestor of their own
        for cand in weak_ancestors:
            cand_ancestors = await get_ancestors(db, topic_id, cand)
            if not any(
                _is_weak_or_untested(a, concept_gap_map) and a not in completed
                for a in cand_ancestors
            ):
                impact[cand] = impact.get(cand, 0) + 1

    return [cid for cid, _ in sorted(impact.items(), key=lambda kv: (-kv[1], kv[0]))]
