"""Deterministic scoring for diagnostic/quiz responses.

Objective items (multiple choice) are scored in code, weighted by difficulty and
bloom level. Short answers get a keyword-overlap heuristic score here; the LLM
assist in the evaluator can override it with a judged score when available.
"""

DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.5, "hard": 2.0}
BLOOM_WEIGHT = {"remember": 1.0, "understand": 1.1, "apply": 1.25, "analyse": 1.4}


def keyword_overlap_score(answer_text: str, expected_concepts: list[str]) -> float:
    """Fraction (0-1) of expected concept keywords present in a free-text answer.

    Fallback grader when no LLM is available; intentionally lenient on phrasing
    (substring match on normalized text).
    """
    if not expected_concepts:
        return 0.0
    normalized = " ".join((answer_text or "").lower().split())
    hits = sum(1 for kw in expected_concepts if kw.lower() in normalized)
    # full credit at >= half the expected concepts mentioned
    return min(1.0, hits / max(1, len(expected_concepts) / 2))


def score_responses(
    responses: list[dict],
    bloom_by_concept: dict[str, str] | None = None,
) -> dict:
    """Compute per-concept scores (0-100) and an overall level score.

    Each response dict needs: concept_node_id, difficulty, type, and either
    `correct` (bool, multiple_choice) or `credit` (0-1 float, short_answer —
    set by LLM judge or keyword heuristic).

    Per-concept score = weighted credit / weighted max. Overall level score is
    the weighted mean across all responses (not the mean of concept means, so
    concepts probed with more/harder questions count proportionally).
    """
    bloom_by_concept = bloom_by_concept or {}
    per_concept: dict[str, dict[str, float]] = {}
    total_earned = 0.0
    total_possible = 0.0

    for r in responses:
        cid = r["concept_node_id"]
        weight = DIFFICULTY_WEIGHT.get(r.get("difficulty", "medium"), 1.5)
        weight *= BLOOM_WEIGHT.get(bloom_by_concept.get(cid, "understand"), 1.1)

        if r.get("type") == "short_answer":
            credit = float(r.get("credit", 0.0))
        else:
            credit = 1.0 if r.get("correct") else 0.0

        bucket = per_concept.setdefault(cid, {"earned": 0.0, "possible": 0.0})
        bucket["earned"] += credit * weight
        bucket["possible"] += weight
        total_earned += credit * weight
        total_possible += weight

    concept_scores = {
        cid: round(100 * b["earned"] / b["possible"], 1)
        for cid, b in per_concept.items()
        if b["possible"] > 0
    }
    level_score = round(100 * total_earned / total_possible, 1) if total_possible else 0.0

    # confidence grows with evidence: number of questions and concept coverage
    n = len(responses)
    confidence = round(min(0.95, 0.35 + 0.04 * n + 0.02 * len(concept_scores)), 2)

    return {
        "level_score": level_score,
        "concept_scores": concept_scores,
        "confidence": confidence,
    }


def blend_concept_score(old_score: float | None, new_score: float, weight_new: float = 0.6) -> float:
    """Blend a fresh quiz score into an existing concept score (recency-weighted)."""
    if old_score is None:
        return round(new_score, 1)
    return round(weight_new * new_score + (1 - weight_new) * old_score, 1)
