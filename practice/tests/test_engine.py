"""Engine tests: prompt rendering, response parsing, aggregation."""

import json

import pytest

from feedforward_practice import engine
from feedforward_practice.contracts import level_for

RUBRIC = {
    "formatVersion": "1.0",
    "kind": "ffrubric",
    "assignment": {"title": "Essay 1", "description": "Critical analysis"},
    "rubric": {
        "categories": [
            {"name": "Argument", "description": "Thesis quality", "weight": 40},
            {"name": "Evidence", "description": "Use of sources", "weight": 60},
        ]
    },
}


def model_json(arg_score=80, ev_score=70):
    return json.dumps(
        {
            "overall_feedback": "Solid draft overall.",
            "categories": [
                {
                    "name": "Argument",
                    "score": arg_score,
                    "feedback": "Clear thesis.",
                    "strengths": ["Specific claim"],
                    "improvements": ["Sharpen scope"],
                },
                {
                    "name": "evidence",  # case-insensitive match
                    "score": ev_score,
                    "feedback": "Sources thin in para 3.",
                    "strengths": [],
                    "improvements": ["Cite the second source"],
                },
            ],
        }
    )


def test_validate_rejects_non_rubric():
    with pytest.raises(engine.RubricError):
        engine.validate_rubric({"kind": "something"})
    with pytest.raises(engine.RubricError):
        engine.validate_rubric({"kind": "ffrubric", "rubric": {"categories": []}})


def test_build_prompt_renders_all_placeholders():
    prompt = engine.build_prompt(RUBRIC, "My draft text.")
    assert "Essay 1" in prompt["user"]
    assert "Argument (40%)" in prompt["user"]
    assert "My draft text." in prompt["user"]
    assert "{{" not in prompt["user"], "unrendered placeholder left in prompt"
    assert "formative feedback" in prompt["system"]


def test_parse_plain_json():
    parsed = engine.parse_response(model_json(), RUBRIC)
    assert [c["name"] for c in parsed["categories"]] == ["Argument", "Evidence"]
    assert parsed["missing_categories"] == []


def test_parse_fenced_json_with_prose():
    raw = "Here is my assessment:\n```json\n" + model_json() + "\n```\nHope it helps!"
    parsed = engine.parse_response(raw, RUBRIC)
    assert len(parsed["categories"]) == 2


def test_parse_drops_invented_categories_and_reports_missing():
    data = json.loads(model_json())
    data["categories"][1]["name"] = "Grammar"  # not in rubric
    parsed = engine.parse_response(json.dumps(data), RUBRIC)
    assert [c["name"] for c in parsed["categories"]] == ["Argument"]
    assert parsed["missing_categories"] == ["Evidence"]


def test_parse_clamps_scores():
    data = json.loads(model_json(arg_score=140, ev_score=-5))
    parsed = engine.parse_response(json.dumps(data), RUBRIC)
    scores = {c["name"]: c["score"] for c in parsed["categories"]}
    assert scores == {"Argument": 100.0, "Evidence": 0.0}


def test_aggregate_weighted_mean_and_levels():
    runs = [
        engine.parse_response(model_json(80, 70), RUBRIC),
        engine.parse_response(model_json(90, 60), RUBRIC),
    ]
    result = engine.aggregate_runs(runs, RUBRIC)
    scores = {c["name"]: c["score"] for c in result["categories"]}
    assert scores == {"Argument": 85.0, "Evidence": 65.0}
    # weighted overall: 85*40 + 65*60 / 100 = 73
    assert result["overall"]["score"] == 73.0
    assert result["overall"]["level"] == level_for(73.0)
    assert result["runs"] == 2


def test_levels_match_shared_contract():
    assert level_for(95)["label"] == "On the bullseye"
    assert level_for(50)["color"] == "red"
