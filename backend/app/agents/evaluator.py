"""Diagnostic Evaluator agent — hybrid, not pure LLM.

Given quiz/diagnostic response data, outputs a structured assessment:
level score, per-concept scores, root gap concepts, confidence, gap reasoning.
Nothing else — no content generation, no recommendations, no personality.

Three layers:
1. Deterministic scoring in code (services.scoring) — objective items weighted by
   difficulty and bloom level.
2. Graph traversal in Postgres (services.graph_traversal) — root-cause gaps via
   recursive CTE. Pure SQL.
3. LLM assist (low temperature, structured output) ONLY for grading free-text
   answers and writing the human-readable gap_reasoning. Falls back to keyword
   heuristics + template text when OpenRouter isn't configured, with reduced
   confidence.
"""

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..generation import openrouter
from ..models import ConceptNode
from ..services import graph_traversal, scoring

logger = logging.getLogger("upvex.evaluator")

_GRADER_SYSTEM_PROMPT = (
    "You are a strict, consistent grader for short-answer technical quiz responses. "
    "For each response you receive, judge how well the answer demonstrates the expected concepts. "
    "Assign credit as a float from 0.0 to 1.0 (partial credit allowed; 1.0 = clearly demonstrates "
    "understanding, 0.5 = partially correct or incomplete, 0.0 = wrong or empty). "
    "Judge substance, not phrasing — synonyms and paraphrases of expected concepts count. "
    'Respond with JSON only: {"grades": [{"index": <int>, "credit": <float>, "rationale": "<one sentence>"}]}'
)

_REASONING_SYSTEM_PROMPT = (
    "You write one short paragraph (2-3 sentences) explaining a learner's diagnostic result in plain, "
    "encouraging language. You are given per-concept scores and the root gap concepts identified by "
    "prerequisite-graph analysis. Explain which foundational concept(s) are holding back the surface-level "
    "weak areas and why addressing them first unlocks progress. Address the learner as 'you'. No emojis. "
    'Respond with JSON only: {"gap_reasoning": "<paragraph>"}'
)


async def _grade_short_answers_llm(short_answers: list[dict]) -> list[float] | None:
    """Returns credits (0-1) per item, or None if LLM unavailable/failed."""
    if not openrouter.is_configured() or not short_answers:
        return None
    items = [
        {
            "index": i,
            "question": sa.get("question_text", ""),
            "expected_concepts": sa.get("expected_concepts", []),
            "answer": sa.get("answer_text", ""),
        }
        for i, sa in enumerate(short_answers)
    ]
    try:
        result = await openrouter.chat_json(
            settings.model_diagnostic_evaluator,
            _GRADER_SYSTEM_PROMPT,
            json.dumps({"responses": items}),
            temperature=0.1,
            max_tokens=2000,
        )
        grades = {g["index"]: float(g["credit"]) for g in result.get("grades", [])}
        return [max(0.0, min(1.0, grades.get(i, 0.0))) for i in range(len(short_answers))]
    except Exception as exc:  # noqa: BLE001 — degrade gracefully to heuristic grading
        logger.warning("LLM short-answer grading failed, falling back to heuristic: %s", exc)
        return None


async def _gap_reasoning_llm(
    concept_titles: dict[str, str],
    concept_scores: dict[str, float],
    root_gaps: list[str],
) -> str | None:
    if not openrouter.is_configured():
        return None
    payload = {
        "concept_scores": {concept_titles.get(cid, cid): s for cid, s in concept_scores.items()},
        "root_gap_concepts": [concept_titles.get(cid, cid) for cid in root_gaps],
    }
    try:
        result = await openrouter.chat_json(
            settings.model_diagnostic_evaluator,
            _REASONING_SYSTEM_PROMPT,
            json.dumps(payload),
            temperature=0.3,
            max_tokens=800,
        )
        text = result.get("gap_reasoning")
        return text if isinstance(text, str) and text.strip() else None
    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM gap reasoning failed, using template: %s", exc)
        return None


def _template_gap_reasoning(
    concept_titles: dict[str, str],
    concept_scores: dict[str, float],
    root_gaps: list[str],
) -> str:
    strong = [concept_titles.get(c, c) for c, s in sorted(concept_scores.items(), key=lambda kv: -kv[1]) if s >= 70][:2]
    weak = [concept_titles.get(c, c) for c, s in sorted(concept_scores.items(), key=lambda kv: kv[1]) if s < graph_traversal.WEAK_THRESHOLD][:2]
    parts = []
    if strong:
        parts.append(f"You're strongest on {' and '.join(strong)}.")
    if weak:
        parts.append(f"The biggest opportunities are {' and '.join(weak)}.")
    if root_gaps:
        roots = [concept_titles.get(c, c) for c in root_gaps[:2]]
        parts.append(
            f"Our prerequisite analysis traces these back to {' and '.join(roots)} — "
            "strengthening that foundation first should unlock progress on the concepts that build on it."
        )
    return " ".join(parts) or "Complete a few lessons and we'll refine your assessment as we learn more about you."


async def evaluate(
    db: AsyncSession,
    topic_id: str,
    responses: list[dict],
    *,
    completed_concepts: set[str] | None = None,
    prior_gap_map: dict[str, float] | None = None,
) -> dict:
    """Run the full evaluation pipeline. Returns the evaluator output dict.

    Response items: question_id, concept_node_id, difficulty, type,
    correct (mcq) / answer_text + expected_concepts + question_text (short answer).
    """
    # 1. LLM (or heuristic) credit for short answers
    short_idx = [i for i, r in enumerate(responses) if r.get("type") == "short_answer"]
    short_items = [responses[i] for i in short_idx]
    llm_credits = await _grade_short_answers_llm(short_items)
    llm_used = llm_credits is not None
    for j, i in enumerate(short_idx):
        if llm_used:
            responses[i]["credit"] = llm_credits[j]
        else:
            responses[i]["credit"] = scoring.keyword_overlap_score(
                responses[i].get("answer_text", ""),
                responses[i].get("expected_concepts") or [],
            )

    # 2. Deterministic scoring, weighted by difficulty + bloom level
    nodes = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == topic_id))
    ).scalars().all()
    bloom_by_concept = {n.id: n.bloom_level for n in nodes}
    concept_titles = {n.id: n.title for n in nodes}
    result = scoring.score_responses(responses, bloom_by_concept)

    # Blend with prior scores when re-scoring after a lesson quiz
    concept_scores = dict(prior_gap_map or {})
    for cid, new_score in result["concept_scores"].items():
        concept_scores[cid] = scoring.blend_concept_score(concept_scores.get(cid), new_score)

    # 3. Root gaps via prerequisite graph traversal (pure SQL, deterministic)
    root_gaps = await graph_traversal.find_root_gaps(
        db, topic_id, concept_scores, completed_concepts
    )

    # 4. Human-readable reasoning (LLM assist, template fallback)
    reasoning = await _gap_reasoning_llm(concept_titles, concept_scores, root_gaps)
    if reasoning is None:
        reasoning = _template_gap_reasoning(concept_titles, concept_scores, root_gaps)

    confidence = result["confidence"]
    if short_items and not llm_used:
        confidence = round(max(0.1, confidence - 0.15), 2)  # heuristic grading is less trustworthy

    return {
        "level_score": result["level_score"],
        "confidence": confidence,
        "concept_scores": concept_scores,
        "root_gap_concepts": root_gaps,
        "gap_reasoning": reasoning,
        "llm_grading_used": llm_used,
    }
