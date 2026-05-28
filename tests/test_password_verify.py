"""Tests for ``verify_password`` — bcrypt-based credential check (no bypasses)."""

from app.utils.auth import get_password_hash, verify_password


def test_correct_password_round_trips():
    h = get_password_hash("CorrectHorseBatteryStaple")
    assert verify_password("CorrectHorseBatteryStaple", h) is True


def test_wrong_password_returns_false():
    h = get_password_hash("right_one")
    assert verify_password("wrong_one", h) is False


def test_empty_password_returns_false():
    """An empty password must never authenticate, regardless of the stored hash."""
    h = get_password_hash("anything")
    assert verify_password("", h) is False


def test_malformed_hash_returns_false_not_raises():
    """A non-bcrypt-shaped string from the DB must not crash the login handler."""
    assert verify_password("any", "not-a-bcrypt-hash") is False
    assert verify_password("any", "") is False


def test_unicode_password_round_trips():
    pw = "pässwörd_with_émojis_🔐"
    h = get_password_hash(pw)
    assert verify_password(pw, h) is True
    assert verify_password("pässwörd_with_émojis", h) is False  # close but no cigar


def test_hash_is_not_plaintext():
    """Sanity check: stored hash should never be the plain password (bcrypt is invasive)."""
    pw = "Plaintext123!"
    h = get_password_hash(pw)
    assert h != pw
    assert h.startswith("$2")  # bcrypt prefix
