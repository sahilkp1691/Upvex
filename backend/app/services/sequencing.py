"""Deterministic sequencing: annotate every concept node in a topic's graph with a
roadmap state for a specific user goal.

States:
- tested_out:       diagnostic score high enough to skip
- completed:        user finished the lesson + quiz for this concept
- recommended_next: what to do now — root gaps first, then unlocked weak concepts
- available:        unlocked (all required prerequisites met) but not the top pick
- locked:           at least one required prerequisite not yet met
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ConceptEdge, ConceptNode, UserGoal

TESTED_OUT_THRESHOLD = 80
MAX_RECOMMENDED = 3


def _prereq_met(cid: str, gap_map: dict, completed: set[str]) -> bool:
    if cid in completed:
        return True
    score = gap_map.get(cid)
    return score is not None and score >= TESTED_OUT_THRESHOLD


async def build_roadmap(db: AsyncSession, goal: UserGoal) -> dict:
    nodes = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == goal.topic_id))
    ).scalars().all()
    edges = (
        await db.execute(select(ConceptEdge).where(ConceptEdge.topic_id == goal.topic_id))
    ).scalars().all()

    gap_map: dict[str, float] = goal.concept_gap_map or {}
    completed: set[str] = set(goal.completed_concepts or [])
    root_gaps: list[str] = [c for c in (goal.root_gap_concepts or []) if c not in completed]

    required_prereqs: dict[str, list[str]] = {}
    recommended_prereqs: dict[str, list[str]] = {}
    for e in edges:
        target = required_prereqs if e.edge_type == "required" else recommended_prereqs
        target.setdefault(e.to_concept_id, []).append(e.from_concept_id)

    states: dict[str, dict] = {}
    unlocked_candidates: list[str] = []

    for n in nodes:
        blocked_by = [
            p for p in required_prereqs.get(n.id, [])
            if not _prereq_met(p, gap_map, completed)
        ]
        if n.id in completed:
            state = "completed"
        elif gap_map.get(n.id) is not None and gap_map[n.id] >= TESTED_OUT_THRESHOLD:
            state = "tested_out"
        elif blocked_by:
            state = "locked"
        else:
            state = "available"
            unlocked_candidates.append(n.id)
        states[n.id] = {"state": state, "blocked_by": blocked_by}

    # Recommendations: root gaps first (they unlock the most), then weakest unlocked
    recommended: list[str] = [c for c in root_gaps if states.get(c, {}).get("state") == "available"]
    if len(recommended) < MAX_RECOMMENDED:
        remaining = [
            c for c in unlocked_candidates
            if c not in recommended
        ]
        remaining.sort(key=lambda c: (gap_map.get(c) if gap_map.get(c) is not None else -1))
        # untested (-1) sorts first, then weakest scores
        recommended.extend(remaining[: MAX_RECOMMENDED - len(recommended)])
    for c in recommended:
        states[c]["state"] = "recommended_next"

    node_payload = [
        {
            "id": n.id,
            "title": n.title,
            "learning_objective": n.learning_objective,
            "difficulty_tag": n.difficulty_tag,
            "bloom_level": n.bloom_level,
            "estimated_duration_mins": n.estimated_duration_mins,
            "is_root": n.is_root,
            "state": states[n.id]["state"],
            "blocked_by": states[n.id]["blocked_by"],
            "score": gap_map.get(n.id),
            "is_root_gap": n.id in root_gaps,
        }
        for n in nodes
    ]
    edge_payload = [
        {"from": e.from_concept_id, "to": e.to_concept_id, "type": e.edge_type}
        for e in edges
    ]
    return {"nodes": node_payload, "edges": edge_payload}
