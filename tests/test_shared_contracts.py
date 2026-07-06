"""Contract tests for shared/ — the server↔desktop agreement surface.

If these fail, the server has drifted from the contracts that FeedForward
Desktop (desktop/) also consumes. Fix shared/ and both apps together.
"""

import json
import pathlib

import jsonschema
import pytest

SHARED = pathlib.Path(__file__).parent.parent / "shared"


@pytest.fixture(scope="module")
def rubric_schema():
    with open(SHARED / "ffrubric.schema.json") as f:
        return json.load(f)


def test_levels_json_drives_formatter():
    """get_level_text/get_score_color must come from shared/levels.json."""
    from app.utils import feedback_formatter as ff

    with open(SHARED / "levels.json") as f:
        spec = json.load(f)

    for level in spec["levels"]:
        assert ff.get_level_text(level["min"]) == level["label"]
        assert ff.get_level_text(level["min"] + 0.5) == level["label"]
    for band in spec["colorBands"]:
        assert ff.get_score_color(band["min"]) == band["color"]


def test_levels_json_covers_full_range():
    with open(SHARED / "levels.json") as f:
        spec = json.load(f)
    assert spec["levels"][-1]["min"] == 0, "bands must cover score 0"
    mins = [level["min"] for level in spec["levels"]]
    assert mins == sorted(mins, reverse=True), "bands must be ordered high→low"


def test_rubric_export_payload_matches_schema(rubric_schema):
    """Build an export payload the way the route does and validate it."""
    payload = {
        "formatVersion": "1.0",
        "kind": "ffrubric",
        "exportedAt": "2026-07-06T00:00:00",
        "source": {"app": "FeedForward", "courseCode": "COMS1000", "courseTitle": "X"},
        "assignment": {
            "title": "Essay 1",
            "description": "Critical analysis",
            "dueDate": "",
            "maxDrafts": 3,
        },
        "rubric": {
            "categories": [
                {"name": "Argument", "description": "", "weight": 40.0},
                {"name": "Evidence", "description": "", "weight": 60.0},
            ]
        },
    }
    jsonschema.validate(payload, rubric_schema)


def test_schema_rejects_missing_categories(rubric_schema):
    bad = {
        "formatVersion": "1.0",
        "kind": "ffrubric",
        "assignment": {"title": "Essay"},
        "rubric": {"categories": []},
    }
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, rubric_schema)


def test_prompt_contract_json_keys_match_shared():
    """The JSON response contract in shared/feedback-prompt.md names the keys
    both parsers rely on — make sure the canonical file still contains them."""
    text = (SHARED / "feedback-prompt.md").read_text()
    for key in (
        '"overall_feedback"',
        '"categories"',
        '"name"',
        '"score"',
        '"feedback"',
        '"strengths"',
        '"improvements"',
    ):
        assert key in text, f"prompt contract lost {key}"
