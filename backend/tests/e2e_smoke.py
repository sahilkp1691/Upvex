"""End-to-end smoke test against a running dev server (DEV_AUTH_BYPASS + eager Celery).

Run:  .venv/bin/python tests/e2e_smoke.py
"""

import sys
import time

import httpx

BASE = "http://localhost:8000/api"
client = httpx.Client(timeout=180)  # real LLM generation can take a while


def step(name, fn):
    result = fn()
    print(f"OK   {name}")
    return result


def main():
    # onboarding
    step("onboarding", lambda: client.post(f"{BASE}/onboarding", json={
        "learning_style": "hands_on",
        "time_availability": "30_to_60",
        "motivation": "upskilling",
        "tech_background": "some_scripting",
        "tone_preference": "neutral",
        "display_name": "Smoke Tester",
        "raw_answers": {"src": "e2e"},
    }).raise_for_status())

    me = client.get(f"{BASE}/me").json()
    assert me["onboarded"], "should be onboarded"

    # goal (re-runnable: reuses an existing goal if present)
    goal = step("create goal", lambda: client.post(
        f"{BASE}/goals", json={"topic_id": "topic_apache_spark"}
    ).raise_for_status().json())
    goal_id = goal["id"]

    if goal["status"] == "diagnostic_pending":
        # adaptive diagnostic
        res = client.post(f"{BASE}/diagnostic/{goal_id}/start").raise_for_status().json()
        n = 0
        while not res.get("done"):
            q = res["question"]
            payload = {"question_id": q["question_id"]}
            if q["type"] == "multiple_choice":
                payload["selected_option"] = 1  # frequently correct in the seed bank
            else:
                payload["answer_text"] = "data locality means moving compute to data; shuffle and partition pruning matter"
            res = client.post(f"{BASE}/diagnostic/{goal_id}/answer", json=payload).raise_for_status().json()
            n += 1
            assert n < 20, "diagnostic should terminate"
        print(f"OK   adaptive diagnostic ({n} questions)")

        results = step("evaluator complete", lambda: client.post(
            f"{BASE}/diagnostic/{goal_id}/complete"
        ).raise_for_status().json())
        assert 0 <= results["level_score"] <= 100
        assert results["concept_scores"], "concept scores present"
        assert results["gap_reasoning"], "gap reasoning present"
        print(f"     level={results['level_score']} conf={results['confidence']} root_gaps={results['root_gap_concepts']}")
    else:
        print("SKIP diagnostic (goal already active from a previous run)")

    # roadmap
    roadmap = step("roadmap", lambda: client.get(f"{BASE}/roadmap/{goal_id}").raise_for_status().json())
    states = {n_["state"] for n_ in roadmap["nodes"]}
    assert "recommended_next" in states, f"expected a recommendation, got {states}"
    target = next(n_ for n_ in roadmap["nodes"] if n_["state"] == "recommended_next")
    locked = [n_ for n_ in roadmap["nodes"] if n_["state"] == "locked"]
    print(f"     states={ {s: sum(1 for x in roadmap['nodes'] if x['state']==s) for s in states} } target={target['id']}")
    if locked:
        assert locked[0]["blocked_by"], "locked nodes must list blockers"

    # pacing
    paced = step("pacing", lambda: client.patch(
        f"{BASE}/goals/{goal_id}/pacing", json={"pacing_choice": "regular"}
    ).raise_for_status().json())
    assert paced["target_deadline"]

    # content generation (eager celery -> stub lesson)
    content = client.get(f"{BASE}/content/{goal_id}/{target['id']}").raise_for_status().json()
    for _ in range(15):
        if content["status"] in ("ready", "failed"):
            break
        time.sleep(1)
        content = client.get(f"{BASE}/content/status/{content['content_id']}").raise_for_status().json()
    assert content["status"] == "ready", f"content status: {content['status']} err={content.get('error')}"
    assert content["lesson"]["sections"], "lesson has sections"
    assert content["quiz"]["questions"], "quiz has questions"
    assert "correct_option" not in content["quiz"]["questions"][0], "answers must not leak to client"
    print("OK   content generation (cache miss -> generate -> ready)")

    # cache hit
    content2 = client.get(f"{BASE}/content/{goal_id}/{target['id']}").raise_for_status().json()
    assert content2["status"] == "ready" and content2["content_id"] == content["content_id"]
    print("OK   cache hit on same signature")

    # quiz submit
    answers = []
    for i, q in enumerate(content["quiz"]["questions"]):
        if q["type"] == "multiple_choice":
            answers.append({"question_index": i, "selected_option": 0})
        else:
            answers.append({"question_index": i, "answer_text": "it covers the concept objective"})
    result = step("quiz submit + rescoring", lambda: client.post(
        f"{BASE}/content/{goal_id}/{target['id']}/submit-quiz",
        json={"generated_content_id": content["content_id"], "answers": answers},
    ).raise_for_status().json())
    assert result["xp_earned"] > 0
    assert result["streak"]["current"] >= 1
    print(f"     score={result['quiz_score']} xp={result['xp_earned']} badges={[b['id'] for b in result['badges_earned']]}")

    # roadmap updated
    roadmap2 = client.get(f"{BASE}/roadmap/{goal_id}").raise_for_status().json()
    completed = [n_ for n_ in roadmap2["nodes"] if n_["state"] == "completed"]
    assert any(n_["id"] == target["id"] for n_ in completed), "completed concept should be marked"
    print("OK   roadmap reflects completion")

    # gamification
    summary = step("gamification summary", lambda: client.get(
        f"{BASE}/gamification/summary"
    ).raise_for_status().json())
    assert summary["total_xp"] > 0
    assert summary.get("level", 0) >= 1
    board = client.get(f"{BASE}/gamification/leaderboard").raise_for_status().json()
    assert board["entries"], "leaderboard has entries"
    assert "my_rank" in board and "my_xp" in board
    print(f"     xp={summary['total_xp']} level={summary['level']} streak={summary['streak']['current']} badges={len(summary['badges'])}")

    # admin surface
    analytics = step("admin analytics", lambda: client.get(f"{BASE}/admin/analytics").raise_for_status().json())
    assert analytics["total_users"] >= 1
    contracts = client.get(f"{BASE}/admin/contracts").raise_for_status().json()
    assert contracts and contracts[0]["version"] >= 1
    review = client.get(f"{BASE}/admin/content").raise_for_status().json()
    assert review, "content review queue has entries"
    graph = client.get(f"{BASE}/admin/topics/topic_apache_spark/graph").raise_for_status().json()
    assert graph["nodes"] and graph["edges"]
    assert graph.get("topic_name"), "graph should include topic_name"

    # cycle rejection
    r = client.post(f"{BASE}/admin/topics/topic_apache_spark/edges", json={
        "from_concept_id": "spark_optimization", "to_concept_id": "spark_big_data_fundamentals",
    })
    assert r.status_code == 422, f"cycle should be rejected, got {r.status_code}"
    print("OK   admin graph cycle rejection")

    print("\nALL E2E CHECKS PASSED")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:
        print(f"FAIL {exc}")
        sys.exit(1)
