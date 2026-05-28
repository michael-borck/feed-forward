"""Tests for the student-view assignment filter."""

from app.utils.assignment_filter import filter_assignments_by_status


class _A:
    """Minimal stand-in for an ``Assignment`` row — only ``.status`` matters here."""

    def __init__(self, status: str):
        self.status = status


def test_filter_all_returns_a_copy_unchanged():
    items = [_A("active"), _A("closed"), _A("draft")]
    out = filter_assignments_by_status(items, "all")
    assert [a.status for a in out] == ["active", "closed", "draft"]
    # Caller can mutate without affecting the input list.
    assert out is not items


def test_filter_active_keeps_only_active():
    items = [_A("active"), _A("closed"), _A("active"), _A("draft")]
    out = filter_assignments_by_status(items, "active")
    assert [a.status for a in out] == ["active", "active"]


def test_filter_completed_keeps_only_closed():
    items = [_A("active"), _A("closed"), _A("closed"), _A("archived")]
    out = filter_assignments_by_status(items, "completed")
    assert [a.status for a in out] == ["closed", "closed"]


def test_filter_unknown_value_falls_through_to_all():
    items = [_A("active"), _A("closed")]
    out = filter_assignments_by_status(items, "garbage")
    assert [a.status for a in out] == ["active", "closed"]


def test_filter_empty_input_returns_empty():
    assert filter_assignments_by_status([], "active") == []
    assert filter_assignments_by_status([], "all") == []
