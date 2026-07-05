"""Tests for the cite-sight signal slice (S4 second half).

Covers: citation-response flattening (including the verification-disabled
guard), essay extraction now running two independent sources, the
referencing-category auto-match, and the analyse_citations client.
"""

from datetime import datetime

import requests

from app.services import signal_scorer, signal_service
from app.utils import analyser_client

# A representative cite-sight /analyse response (verification enabled).
CITE_SAMPLE = {
    "fileName": "submission.txt",
    "references": {
        "totalReferences": 4,
        "verifiedCount": 3,
        "suspiciousCount": 1,
        "notFoundCount": 0,
        "brokenUrlCount": 1,
        "detectedStyle": "apa",
        "crossReference": {
            "unmatchedBibliography": [{"raw": "Orphan, A. (2020)."}],
            "unmatchedInText": [],
        },
        "verifications": [
            {"status": "verified", "formatIssues": []},
            {"status": "verified", "formatIssues": [{"rule": "x"}]},
            {"status": "likely_valid", "formatIssues": []},
            {"status": "suspicious", "formatIssues": [{"rule": "y"}, {"rule": "z"}]},
        ],
    },
}

# Same document analysed with verification disabled: every status format_only.
CITE_SAMPLE_UNVERIFIED = {
    "fileName": "submission.txt",
    "references": {
        "totalReferences": 4,
        "verifiedCount": 0,
        "suspiciousCount": 0,
        "notFoundCount": 0,
        "brokenUrlCount": 0,
        "detectedStyle": "apa",
        "crossReference": {"unmatchedBibliography": [], "unmatchedInText": []},
        "verifications": [{"status": "format_only", "formatIssues": []}] * 4,
    },
}

TEXT_SAMPLE = {"analysis": {"text_metrics": {"word_count": 10}}}


def _make_draft(content="An essay citing Smith (2020) and Jones (2021)."):
    from app.models.feedback import Draft, drafts

    res = drafts.insert(
        Draft(
            assignment_id=1,
            student_email="s@example.com",
            version=1,
            content=content,
            submission_date=datetime.now().isoformat(),
            status="submitted",
            word_count=len(content.split()),
        )
    )
    return res.id if hasattr(res, "id") else res


# ---- _flatten_citation_response (pure) ----


def test_flatten_citations_with_verification():
    flat = signal_service._flatten_citation_response(CITE_SAMPLE)
    assert flat["total_references"] == 4.0
    assert flat["verified_reference_count"] == 3.0
    assert flat["suspicious_reference_count"] == 1.0
    assert flat["broken_url_count"] == 1.0
    assert flat["orphaned_reference_count"] == 1.0
    assert flat["uncited_reference_count"] == 0.0
    assert flat["citation_format_issue_count"] == 3.0
    assert flat["citation_integrity_pct"] == 75.0


def test_flatten_citations_unverified_omits_verification_signals():
    """format_only runs must not emit verified counts (0 verified would read
    as 'all citations bogus')."""
    flat = signal_service._flatten_citation_response(CITE_SAMPLE_UNVERIFIED)
    assert flat["total_references"] == 4.0
    assert "citation_integrity_pct" not in flat
    assert "verified_reference_count" not in flat
    assert "broken_url_count" not in flat
    assert flat["citation_format_issue_count"] == 0.0


def test_flatten_citations_empty():
    assert signal_service._flatten_citation_response({}) == {}
    assert signal_service._flatten_citation_response({"references": {}}) == {}


# ---- essay extraction now has two independent sources ----


def test_essay_extraction_stores_both_sources(monkeypatch):
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_text", lambda t: TEXT_SAMPLE
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_sentiment", lambda t: None
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_citations", lambda t, **kw: CITE_SAMPLE
    )

    did = _make_draft()
    assert signal_service.extract_signals_for_draft(did) is True
    sigs = signal_service.get_signals_for_draft(did)
    sources = {s.source for s in sigs}
    assert sources == {"document-analyser", "cite-sight"}


def test_cite_sight_down_does_not_block_document_signals(monkeypatch):
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_text", lambda t: TEXT_SAMPLE
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_sentiment", lambda t: None
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_citations", lambda t, **kw: None
    )

    did = _make_draft()
    assert signal_service.extract_signals_for_draft(did) is True
    sources = {s.source for s in signal_service.get_signals_for_draft(did)}
    assert sources == {"document-analyser"}


def test_per_source_idempotency_backfills_missing_source(monkeypatch):
    """If cite-sight was down on the first pass, a re-run adds its signals
    without duplicating document-analyser's."""
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_text", lambda t: TEXT_SAMPLE
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_sentiment", lambda t: None
    )
    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_citations", lambda t, **kw: None
    )

    did = _make_draft()
    signal_service.extract_signals_for_draft(did)
    n_first = len(signal_service.get_signals_for_draft(did))

    monkeypatch.setattr(
        signal_service.analyser_client, "analyse_citations", lambda t, **kw: CITE_SAMPLE
    )
    signal_service.extract_signals_for_draft(did)
    sigs = signal_service.get_signals_for_draft(did)

    doc_count = sum(1 for s in sigs if s.source == "document-analyser")
    assert doc_count == n_first  # not duplicated
    assert any(s.source == "cite-sight" for s in sigs)  # backfilled


# ---- referencing-category auto-match ----


def test_referencing_category_maps_to_cite_sight_signals():
    rules = signal_scorer.suggest_rules_for_category("Referencing", type_code="essay")
    names = {r.signal_name for r in rules}
    assert "citation_integrity_pct" in names
    assert "orphaned_reference_count" in names
    assert all(r.signal_source == "cite-sight" for r in rules)


def test_referencing_estimate_from_signals():
    rules = signal_scorer.suggest_rules_for_category("Citations", type_code="essay")
    signals_by_name = {
        "citation_integrity_pct": 75.0,
        "orphaned_reference_count": 1.0,
        "citation_format_issue_count": 3.0,
    }
    score, confidence = signal_scorer.score_category(rules, signals_by_name)
    assert score == (75.0 + 70.0 + 70.0) / 3
    assert confidence == 1.0


# ---- analyse_citations client ----


def test_analyse_citations_empty_returns_none():
    assert analyser_client.analyse_citations("") is None


def test_analyse_citations_service_down_returns_none(monkeypatch):
    def boom(*args, **kwargs):
        raise requests.ConnectionError("connection refused")

    monkeypatch.setattr(analyser_client.requests, "post", boom)
    assert analyser_client.analyse_citations("text with refs") is None


def test_analyse_citations_sends_verification_flags(monkeypatch):
    seen = {}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return CITE_SAMPLE

    def fake_post(url, files=None, data=None, timeout=None):
        seen["url"] = url
        seen["data"] = data
        return FakeResp()

    monkeypatch.setattr(analyser_client.requests, "post", fake_post)
    assert analyser_client.analyse_citations("text", verify=False) == CITE_SAMPLE
    assert seen["url"].endswith("/analyse")
    assert seen["data"]["checkUrls"] == "false"
    assert seen["data"]["checkDoi"] == "false"
    assert seen["data"]["checkInText"] == "true"  # local cross-ref always on
