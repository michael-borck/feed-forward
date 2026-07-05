"""Tests for the lens analyser HTTP client (graceful degradation)."""

import requests

from app.utils import analyser_client


def test_analyse_text_empty_returns_none():
    assert analyser_client.analyse_text("") is None
    assert analyser_client.analyse_text("   ") is None


def test_analyse_text_service_down_returns_none(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "post", boom)
    assert analyser_client.analyse_text("a real essay body") is None


def test_analyse_text_invalid_json_returns_none(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            raise ValueError("not json")

    monkeypatch.setattr(analyser_client.requests, "post", lambda *a, **k: FakeResp())
    assert analyser_client.analyse_text("text") is None


def test_analyse_text_success_returns_payload(monkeypatch):
    payload = {"analysis": {"readability": {"flesch_score": 50.0}}}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    monkeypatch.setattr(analyser_client.requests, "post", lambda *a, **k: FakeResp())
    assert analyser_client.analyse_text("text") == payload


def test_health_down_returns_false(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "get", boom)
    assert analyser_client.health() is False


def test_analyse_sentiment_empty_returns_none():
    assert analyser_client.analyse_sentiment("") is None


def test_analyse_sentiment_down_returns_none(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "post", boom)
    assert analyser_client.analyse_sentiment("a real essay body") is None


def test_analyse_sentiment_success_returns_payload(monkeypatch):
    payload = {
        "document_sentiment": {
            "positive": 0.9,
            "negative": 0.0,
            "neutral": 0.1,
            "compound": 0.9,
        }
    }

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    monkeypatch.setattr(analyser_client.requests, "post", lambda *a, **k: FakeResp())
    assert analyser_client.analyse_sentiment("text") == payload


# ---- service_health (admin signal-services card) ----


def test_service_health_reports_all_three_services(monkeypatch):
    class FakeResp:
        status_code = 200

        def json(self):
            return {"status": "ok", "version": "1.2.3"}

    monkeypatch.setattr(analyser_client.requests, "get", lambda *a, **k: FakeResp())
    results = analyser_client.service_health()
    names = {r["name"] for r in results}
    assert names == {"document-analyser", "code-analyser", "cite-sight"}
    assert all(r["ok"] for r in results)
    assert all(r["version"] == "1.2.3" for r in results)
    assert all(r["url"].startswith("http") for r in results)


def test_service_health_marks_unreachable(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "get", boom)
    results = analyser_client.service_health()
    assert all(not r["ok"] for r in results)
    assert all(r["error"] for r in results)


def test_service_health_handles_non_200(monkeypatch):
    class FakeResp:
        status_code = 503

        def json(self):
            return {}

    monkeypatch.setattr(analyser_client.requests, "get", lambda *a, **k: FakeResp())
    results = analyser_client.service_health()
    assert all(not r["ok"] for r in results)
    assert all(r["error"] == "HTTP 503" for r in results)
