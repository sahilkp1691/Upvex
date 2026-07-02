"""Deterministic scoring unit tests + evaluator eval fixtures (known response
patterns with expected score ranges, per the PRD evals section)."""

from app.services.scoring import blend_concept_score, keyword_overlap_score, score_responses


def mcq(cid, difficulty, correct):
    return {"concept_node_id": cid, "difficulty": difficulty, "type": "multiple_choice", "correct": correct}


def short(cid, difficulty, credit):
    return {"concept_node_id": cid, "difficulty": difficulty, "type": "short_answer", "credit": credit}


def test_all_correct_scores_100():
    result = score_responses([mcq("a", "easy", True), mcq("a", "hard", True)])
    assert result["concept_scores"]["a"] == 100.0
    assert result["level_score"] == 100.0


def test_all_wrong_scores_0():
    result = score_responses([mcq("a", "medium", False), mcq("b", "hard", False)])
    assert result["level_score"] == 0.0


def test_difficulty_weighting_hard_counts_more():
    # correct hard + wrong easy should beat correct easy + wrong hard
    high = score_responses([mcq("a", "hard", True), mcq("a", "easy", False)])
    low = score_responses([mcq("a", "easy", True), mcq("a", "hard", False)])
    assert high["concept_scores"]["a"] > low["concept_scores"]["a"]


def test_bloom_weighting_applies():
    plain = score_responses([mcq("a", "medium", True), mcq("a", "medium", False)])
    weighted = score_responses(
        [mcq("a", "medium", True), mcq("b", "medium", False)],
        bloom_by_concept={"a": "analyse", "b": "remember"},
    )
    # analyse-correct outweighs remember-wrong -> above 50
    assert weighted["level_score"] > plain["level_score"]


def test_partial_credit_short_answer():
    result = score_responses([short("a", "medium", 0.5)])
    assert result["concept_scores"]["a"] == 50.0


def test_confidence_grows_with_evidence():
    few = score_responses([mcq("a", "medium", True)] * 3)
    many = score_responses([mcq(f"c{i}", "medium", True) for i in range(12)])
    assert many["confidence"] > few["confidence"]


def test_keyword_overlap():
    assert keyword_overlap_score("the shuffle and partition pruning help", ["shuffle", "partition_pruning"]) > 0
    assert keyword_overlap_score("", ["shuffle"]) == 0.0
    assert keyword_overlap_score("totally unrelated", ["shuffle"]) == 0.0


def test_blend_concept_score_recency_weighted():
    assert blend_concept_score(None, 80.0) == 80.0
    blended = blend_concept_score(40.0, 80.0)
    assert 40.0 < blended < 80.0
    assert blended == 64.0  # 0.6*80 + 0.4*40


# ---- Evaluator eval fixtures: known patterns -> expected score bounds ----

def test_eval_fixture_mostly_strong_user():
    responses = (
        [mcq("dataframes", "medium", True)] * 3
        + [mcq("partitioning", "hard", True)] * 2
        + [mcq("shuffles", "medium", False)]
    )
    result = score_responses(responses)
    assert 70 <= result["level_score"] <= 95
    assert result["concept_scores"]["dataframes"] == 100.0
    assert result["concept_scores"]["shuffles"] == 0.0


def test_eval_fixture_struggling_user():
    responses = (
        [mcq("dataframes", "easy", True)]
        + [mcq("partitioning", "medium", False)] * 2
        + [mcq("shuffles", "medium", False)]
        + [short("optimization", "hard", 0.25)]
    )
    result = score_responses(responses)
    assert 10 <= result["level_score"] <= 40
