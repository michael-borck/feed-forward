"""Orchestration tests with a stubbed provider."""

import json

import pytest

from feedforward_practice import run as run_mod
from feedforward_practice.providers import ProviderConfig, ProviderError
from tests.test_engine import RUBRIC, model_json


def test_practice_feedback_happy_path(monkeypatch):
    monkeypatch.setattr(run_mod, "chat", lambda cfg, s, u: model_json())
    result = run_mod.practice_feedback(RUBRIC, "A draft.", ProviderConfig(model="m"))
    assert result["overall"]["score"] > 0
    assert result["failed_runs"] == 0
    assert result["word_count"] == 2


def test_partial_run_failures_tolerated(monkeypatch):
    calls = iter([ProviderError("boom"), model_json()])

    def flaky(cfg, s, u):
        item = next(calls)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(run_mod, "chat", flaky)
    result = run_mod.practice_feedback(
        RUBRIC, "A draft.", ProviderConfig(model="m"), num_runs=2
    )
    assert result["failed_runs"] == 1
    assert result["runs"] == 1


def test_all_failures_raise(monkeypatch):
    def broken(cfg, s, u):
        raise ProviderError("endpoint down")

    monkeypatch.setattr(run_mod, "chat", broken)
    with pytest.raises(ProviderError, match="endpoint down"):
        run_mod.practice_feedback(RUBRIC, "A draft.", ProviderConfig(model="m"))


def test_empty_draft_rejected():
    with pytest.raises(ValueError, match="empty"):
        run_mod.practice_feedback(RUBRIC, "  ", ProviderConfig(model="m"))


def test_unparseable_model_output(monkeypatch):
    monkeypatch.setattr(run_mod, "chat", lambda c, s, u: "I cannot help with that.")
    with pytest.raises(ProviderError, match="No JSON object"):
        run_mod.practice_feedback(RUBRIC, "A draft.", ProviderConfig(model="m"))


def test_num_runs_clamped(monkeypatch):
    counter = {"n": 0}

    def counting(cfg, s, u):
        counter["n"] += 1
        return model_json()

    monkeypatch.setattr(run_mod, "chat", counting)
    run_mod.practice_feedback(RUBRIC, "d", ProviderConfig(model="m"), num_runs=99)
    assert counter["n"] == 5


def test_rubric_json_roundtrip_from_export_shape():
    """A payload shaped like the server's export route works end to end."""
    exported = json.loads(json.dumps(RUBRIC))  # simulate file round-trip
    from feedforward_practice.engine import build_prompt, validate_rubric

    prompt = build_prompt(validate_rubric(exported), "text")
    assert "Argument" in prompt["user"]
