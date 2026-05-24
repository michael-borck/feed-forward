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
