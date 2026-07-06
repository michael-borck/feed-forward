"""API tests (require the [serve] extra: fastapi + lens-contract)."""

import time

import pytest

fastapi = pytest.importorskip("fastapi")
pytest.importorskip("lens_contract")

from fastapi.testclient import TestClient  # noqa: E402

from feedforward_practice import api as api_mod  # noqa: E402
from tests.test_engine import RUBRIC, model_json  # noqa: E402

client = TestClient(api_mod.app)


def test_health_and_manifest():
    assert client.get("/health").json()["status"] == "ok"
    manifest = client.get("/manifest").json()
    assert manifest["name"] == "feedforward-practice"
    assert manifest["role"] == "lens"


def test_feedback_job_lifecycle(monkeypatch):
    monkeypatch.setattr(
        api_mod,
        "practice_feedback",
        lambda rubric, draft, provider, runs: {"overall": {"score": 75.0}},
    )
    resp = client.post(
        "/practice/feedback",
        json={"rubric": RUBRIC, "draft_text": "My draft", "num_runs": 1},
    )
    assert resp.status_code == 202
    job_id = resp.json()["id"]

    for _ in range(50):
        job = client.get(f"/practice/feedback/{job_id}").json()
        if job["status"] != "running":
            break
        time.sleep(0.05)
    assert job["status"] == "done"
    assert job["result"]["overall"]["score"] == 75.0


def test_feedback_job_error_surfaces(monkeypatch):
    def boom(rubric, draft, provider, runs):
        raise ValueError("Draft is empty")

    monkeypatch.setattr(api_mod, "practice_feedback", boom)
    job_id = client.post(
        "/practice/feedback",
        json={"rubric": RUBRIC, "draft_text": " ", "num_runs": 1},
    ).json()["id"]
    for _ in range(50):
        job = client.get(f"/practice/feedback/{job_id}").json()
        if job["status"] != "running":
            break
        time.sleep(0.05)
    assert job["status"] == "error"
    assert "empty" in job["error"]


def test_unknown_job_404():
    assert client.get("/practice/feedback/nope").status_code == 404


def test_auth_gate(monkeypatch):
    """With the token env set, routes 401 without the bearer header."""
    monkeypatch.setenv("FEEDFORWARD_PRACTICE_AUTH_TOKEN", "sekrit")
    # auth middleware reads env at app build time -> build a fresh app
    import importlib

    import feedforward_practice.api as fresh_api

    fresh_api = importlib.reload(fresh_api)
    c = TestClient(fresh_api.app)
    assert c.get("/health").status_code == 200  # open path
    assert c.get("/practice/feedback/x").status_code == 401
    assert (
        c.get(
            "/practice/feedback/x", headers={"Authorization": "Bearer sekrit"}
        ).status_code
        == 404
    )
    monkeypatch.delenv("FEEDFORWARD_PRACTICE_AUTH_TOKEN")
    importlib.reload(fresh_api)
