"""Tests for the instructor submissions route helpers."""

from urllib.parse import unquote

from app.utils.mailto import student_mailto


def test_student_mailto_basic_shape():
    href = student_mailto("student@example.com", "Essay 1")
    assert href.startswith("mailto:student@example.com?subject=")


def test_student_mailto_subject_includes_assignment_title():
    href = student_mailto("s@ex.com", "Reflection Essay")
    subject = unquote(href.split("subject=", 1)[1])
    assert subject == "Feedback on your submission for Reflection Essay"


def test_student_mailto_url_encodes_spaces():
    href = student_mailto("a@b.c", "An Essay With Spaces")
    assert "An%20Essay%20With%20Spaces" in href


def test_student_mailto_url_encodes_reserved_chars():
    href = student_mailto("a@b.c", "Final & Critical Essay")
    # ``&`` must be percent-encoded or it would terminate the subject query.
    assert "%26" in href
    assert "&" not in href.split("?", 1)[1]


def test_student_mailto_preserves_email_as_is():
    """Email itself sits in the URI path before ``?`` — must not be re-encoded."""
    href = student_mailto("first.last+tag@example.co.uk", "Title")
    assert href.startswith("mailto:first.last+tag@example.co.uk?")
