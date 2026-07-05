"""
Simple in-process rate limiter for auth endpoints.

Sliding-window counter keyed by an arbitrary string (typically
``"<route>:<client-ip>"``). State is in-memory, which matches the
single-process deployment; if the app ever runs multiple workers, move
this to a shared store.
"""

import time
from collections import defaultdict, deque

_BUCKETS: dict[str, deque] = defaultdict(deque)

RATE_LIMIT_MESSAGE = "Too many attempts. Please wait a few minutes and try again."


def rate_limited(key: str, max_requests: int, window_seconds: float) -> bool:
    """Record an attempt for ``key`` and report whether it exceeds the limit.

    Returns True when the caller should be rejected. Attempts that are
    rejected still count toward the window (a hammering client stays
    limited until they back off).
    """
    now = time.monotonic()
    bucket = _BUCKETS[key]
    while bucket and now - bucket[0] > window_seconds:
        bucket.popleft()
    bucket.append(now)
    return len(bucket) > max_requests


def client_ip(request) -> str:
    """Best-effort client IP: first X-Forwarded-For hop (Caddy terminates
    TLS in front of the app), falling back to the socket peer."""
    try:
        forwarded = request.headers.get("x-forwarded-for", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host or "unknown"
    except Exception:
        return "unknown"
