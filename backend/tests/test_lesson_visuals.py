"""Unit tests for lesson visual sanitization."""

from app.tasks.generate import _sanitize_visual, _validate_lesson


def test_sanitize_bar_ok():
    v = _sanitize_visual({
        "type": "bar",
        "title": "Skew",
        "caption": "Hot partition",
        "y_label": "Work",
        "bars": [{"label": "P0", "value": 10}, {"label": "P1", "value": 90}],
    })
    assert v["type"] == "bar"
    assert len(v["bars"]) == 2
    assert v["title"] == "Skew"


def test_sanitize_bar_rejects_short():
    assert _sanitize_visual({"type": "bar", "bars": [{"label": "only", "value": 1}]}) is None


def test_sanitize_flow_and_compare():
    flow = _sanitize_visual({
        "type": "flow",
        "steps": [{"label": "A", "detail": "one"}, {"label": "B"}],
    })
    assert flow["steps"][0]["detail"] == "one"

    compare = _sanitize_visual({
        "type": "compare",
        "columns": [
            {"title": "Left", "items": ["x"]},
            {"title": "Right", "items": ["y", "z"]},
        ],
    })
    assert len(compare["columns"]) == 2


def test_validate_lesson_strips_bad_visual():
    lesson = {
        "title": "T",
        "intro": "I",
        "sections": [
            {"heading": "H", "body": "B", "visual": {"type": "bar", "bars": []}},
            {
                "heading": "H2",
                "body": "B2",
                "visual": {
                    "type": "stack",
                    "segments": [{"label": "a", "value": 1}, {"label": "b", "value": 2}],
                },
            },
        ],
        "key_takeaways": ["k"],
        "check_understanding": "?",
    }
    _validate_lesson(lesson)
    assert "visual" not in lesson["sections"][0]
    assert lesson["sections"][1]["visual"]["type"] == "stack"
