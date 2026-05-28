"""Tests for ``build_submissions_csv`` (per-assignment CSV export)."""

import csv
from io import StringIO

from app.utils.csv_export import SUBMISSION_FIELDS, build_submissions_csv


class _Draft:
    """Minimal stand-in for a Draft row — only the exported fields matter here."""

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


def _csv_rows(out: str) -> list[list[str]]:
    return list(csv.reader(StringIO(out)))


def test_csv_starts_with_header_row():
    rows = _csv_rows(build_submissions_csv([]))
    assert rows == [SUBMISSION_FIELDS]


def test_csv_writes_one_row_per_draft():
    drafts = [
        (_Draft(
            student_email="a@x.com", version=1, status="feedback_ready",
            submission_date="2026-05-01"), 87.5),
        (_Draft(
            student_email="b@y.com", version=2, status="processing",
            submission_date="2026-05-02"), None),
    ]
    rows = _csv_rows(build_submissions_csv(drafts))
    assert rows[1] == ["a@x.com", "1", "feedback_ready", "2026-05-01", "87.5"]
    assert rows[2] == ["b@y.com", "2", "processing", "2026-05-02", ""]


def test_csv_score_formatted_to_one_decimal():
    drafts = [(_Draft(
        student_email="s@x.com", version=1, status="feedback_ready",
        submission_date="2026-05-01"), 72.333)]
    rows = _csv_rows(build_submissions_csv(drafts))
    assert rows[1][4] == "72.3"


def test_csv_none_score_renders_empty_cell():
    """Empty cell, not "None" or "0" — so spreadsheets can distinguish "no feedback yet"."""
    drafts = [(_Draft(
        student_email="s@x.com", version=1, status="submitted",
        submission_date="2026-05-01"), None)]
    rows = _csv_rows(build_submissions_csv(drafts))
    assert rows[1][4] == ""


def test_csv_escapes_commas_via_quoting():
    """csv module must quote any field containing a delimiter — verify round-trip."""
    drafts = [(_Draft(
        student_email="a,b@x.com", version=1, status="ok",
        submission_date="2026-05-01"), 50.0)]
    rows = _csv_rows(build_submissions_csv(drafts))
    # Round-trip parsing returns the original value, not a split one.
    assert rows[1][0] == "a,b@x.com"


def test_csv_missing_attrs_render_empty():
    """A degenerate row missing attrs shouldn't raise — empty cells instead."""
    drafts = [(_Draft(), None)]
    rows = _csv_rows(build_submissions_csv(drafts))
    assert rows[1] == ["", "", "", "", ""]
