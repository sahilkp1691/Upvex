"""ProfileSignature: the cache key for generated content.

Grounded at concept-node level. Components chosen so meaningfully different learners
get different content while similar learners share cache entries:
topic + concept node + difficulty band (from the user's current concept score) +
primary root gap + learning style + tone preference.
"""

import hashlib


def difficulty_band(concept_score: float | None) -> str:
    """Bucket the user's current score on this concept into a coarse band."""
    if concept_score is None:
        return "untested"
    if concept_score < 40:
        return "novice"
    if concept_score < 70:
        return "developing"
    return "proficient"


def compute_signature(
    topic_id: str,
    concept_node_id: str,
    concept_score: float | None,
    root_gap_concepts: list[str],
    learning_style: str,
    tone_preference: str,
) -> tuple[str, dict]:
    """Returns (signature_hash, human_readable_inputs)."""
    # only the primary root gap influences content, and only if it's not the node itself
    primary_root_gap = next((c for c in root_gap_concepts if c != concept_node_id), "")
    inputs = {
        "topic_id": topic_id,
        "concept_node_id": concept_node_id,
        "difficulty_band": difficulty_band(concept_score),
        "primary_root_gap": primary_root_gap,
        "learning_style": learning_style,
        "tone_preference": tone_preference,
    }
    raw = "|".join(inputs[k] for k in sorted(inputs))
    return hashlib.sha256(raw.encode()).hexdigest()[:40], inputs
