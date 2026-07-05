"""Tests for db_query — the thin lookup helper over fastlite Tables."""

from app.models.signals import Signal, signals
from app.utils.db_query import by_id, count, first, where


def _insert(draft_id=1, name="x", value=0.0, source="document-analyser"):
    row = signals.insert(
        Signal(
            draft_id=draft_id,
            source=source,
            name=name,
            value=value,
            raw="",
            created_at="t",
        )
    )
    return row.id if hasattr(row, "id") else row


# ---- by_id ----


def test_by_id_returns_row():
    rid = _insert(draft_id=1, name="flesch_score", value=50.0)
    row = by_id(signals, rid)
    assert row is not None
    assert row.draft_id == 1 and row.name == "flesch_score" and row.value == 50.0


def test_by_id_missing_returns_none():
    assert by_id(signals, 999999) is None


# ---- where ----


def test_where_filters_by_equality():
    _insert(draft_id=1, name="flesch_score")
    _insert(draft_id=1, name="vocabulary_richness")
    _insert(draft_id=2, name="flesch_score")
    rows = where(signals, draft_id=1)
    assert {r.name for r in rows} == {"flesch_score", "vocabulary_richness"}


def test_where_multiple_filters_combined_with_and():
    _insert(draft_id=1, name="flesch_score", value=50.0)
    _insert(draft_id=1, name="vocabulary_richness", value=80.0)
    rows = where(signals, draft_id=1, name="flesch_score")
    assert len(rows) == 1 and rows[0].value == 50.0


def test_where_no_match_returns_empty():
    _insert(draft_id=1)
    assert where(signals, draft_id=999) == []


# ---- first ----


def test_first_returns_first_match():
    rid1 = _insert(draft_id=1, name="a")
    _insert(draft_id=1, name="b")
    row = first(signals, draft_id=1)
    assert row is not None and row.id == rid1


def test_first_no_match_returns_none():
    _insert(draft_id=1)
    assert first(signals, draft_id=999) is None


# ---- count ----


def test_count_matches():
    _insert(draft_id=1, name="a")
    _insert(draft_id=1, name="b")
    _insert(draft_id=2, name="a")
    assert count(signals, draft_id=1) == 2
    assert count(signals, name="a") == 2
    assert count(signals, draft_id=999) == 0
