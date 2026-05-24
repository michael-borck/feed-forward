"""Tests for signal extraction (flatten logic + persistence/idempotency)."""

from datetime import datetime

from app.services import signal_service

# A representative document-analyser /text response.
SAMPLE = {
    "service": "DocumentAnalyser",
    "analysis": {
        "text_metrics": {
            "word_count": 237, "sentence_count": 16,
            "paragraph_count": 6, "avg_words_per_sentence": 14.8,
        },
        "readability": {
            "flesch_score": 15.2, "flesch_kincaid_grade": 14.8,
            "interpretation": "Very Difficult",  # string -> must be ignored
        },
        "writing_quality": {
            "passive_voice_percentage": 18.8, "sentence_variety": 73.3,
            "academic_tone": 30.0, "transition_words": 42.0, "hedging_language": 5.3,
        },
        "word_analysis": {
            "unique_words": 166, "total_words": 237, "vocabulary_richness": 70.0,
            "top_words": [{"word": "x", "count": 1}],  # list -> must be ignored
        },
        "ner": {"entities": []},
    },
}


# ---- _flatten_text_response (pure) ----

def test_flatten_extracts_expected_numeric_signals():
    flat = signal_service._flatten_text_response(SAMPLE)
    assert flat["flesch_score"] == 15.2
    assert flat["passive_voice_percentage"] == 18.8
    assert flat["word_count"] == 237.0
    assert flat["vocabulary_richness"] == 70.0
    assert "interpretation" not in flat  # string excluded
    assert "top_words" not in flat  # list excluded
    assert len(flat) == 14
    assert all(isinstance(v, float) for v in flat.values())


def test_flatten_empty_and_missing_sections():
    assert signal_service._flatten_text_response({}) == {}
    assert signal_service._flatten_text_response({"analysis": {}}) == {}


def test_flatten_ignores_bools():
    resp = {"analysis": {"text_metrics": {"word_count": 10, "flag": True}}}
    assert signal_service._flatten_text_response(resp) == {"word_count": 10.0}


# ---- extract_signals_for_draft (temp DB + mocked client) ----

def _make_draft(content="An essay with several words and a few ideas worth marking."):
    from app.models.feedback import Draft, drafts

    res = drafts.insert(Draft(
        assignment_id=1, student_email="s@example.com", version=1, content=content,
        submission_date=datetime.now().isoformat(), status="submitted",
        word_count=len(content.split()),
    ))
    return res.id if hasattr(res, "id") else res


def test_extract_persists_signals(monkeypatch):
    monkeypatch.setattr(signal_service.analyser_client, "analyse_text", lambda text: SAMPLE)
    did = _make_draft()
    assert signal_service.extract_signals_for_draft(did) is True
    sigs = signal_service.get_signals_for_draft(did)
    names = {s.name for s in sigs}
    assert {"flesch_score", "vocabulary_richness"} <= names
    assert all(s.source == "document-analyser" for s in sigs)
    assert len(sigs) == 14


def test_extract_is_idempotent(monkeypatch):
    monkeypatch.setattr(signal_service.analyser_client, "analyse_text", lambda text: SAMPLE)
    did = _make_draft()
    signal_service.extract_signals_for_draft(did)
    n1 = len(signal_service.get_signals_for_draft(did))
    signal_service.extract_signals_for_draft(did)  # second run must skip
    n2 = len(signal_service.get_signals_for_draft(did))
    assert n1 == n2 == 14


def test_extract_no_content_skips_analyser(monkeypatch):
    calls = {"n": 0}

    def spy(text):
        calls["n"] += 1
        return SAMPLE

    monkeypatch.setattr(signal_service.analyser_client, "analyse_text", spy)
    did = _make_draft(content="   ")
    assert signal_service.extract_signals_for_draft(did) is False
    assert calls["n"] == 0  # analyser never called when there's no content


def test_extract_analyser_down_returns_false(monkeypatch):
    monkeypatch.setattr(signal_service.analyser_client, "analyse_text", lambda text: None)
    did = _make_draft()
    assert signal_service.extract_signals_for_draft(did) is False
    assert signal_service.get_signals_for_draft(did) == []
