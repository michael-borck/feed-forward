"""Tests for the in-process auth rate limiter."""

from app.utils import rate_limit


def _fresh_key(name):
    rate_limit._BUCKETS.pop(name, None)
    return name


def test_allows_up_to_limit():
    key = _fresh_key("t:allow")
    assert all(not rate_limit.rate_limited(key, 3, 60) for _ in range(3))


def test_rejects_over_limit():
    key = _fresh_key("t:reject")
    for _ in range(3):
        rate_limit.rate_limited(key, 3, 60)
    assert rate_limit.rate_limited(key, 3, 60) is True


def test_window_expiry_resets(monkeypatch):
    key = _fresh_key("t:expire")
    t = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: t[0])
    for _ in range(3):
        rate_limit.rate_limited(key, 3, 60)
    assert rate_limit.rate_limited(key, 3, 60) is True
    t[0] += 61
    assert rate_limit.rate_limited(key, 3, 60) is False


def test_rejected_attempts_keep_counting(monkeypatch):
    """A hammering client stays limited until it actually backs off."""
    key = _fresh_key("t:hammer")
    t = [1000.0]
    monkeypatch.setattr(rate_limit.time, "monotonic", lambda: t[0])
    for _ in range(10):
        rate_limit.rate_limited(key, 3, 60)
        t[0] += 10  # keeps hitting well above the allowed rate
    assert rate_limit.rate_limited(key, 3, 60) is True


def test_keys_are_independent():
    a, b = _fresh_key("t:a"), _fresh_key("t:b")
    for _ in range(5):
        rate_limit.rate_limited(a, 3, 60)
    assert rate_limit.rate_limited(b, 3, 60) is False
