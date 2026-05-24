"""
Pytest configuration for FeedForward.

Forces a throwaway SQLite DB before any ``app.models`` import — the FastHTML
``db`` is built at import time from ``DATABASE_PATH`` (see app/models/user.py),
so this MUST run before the app package is imported. Keeps tests off any real
database.
"""

import os
import tempfile

_TEST_DB = os.path.join(tempfile.gettempdir(), "ff-pytest.db")
os.environ["DATABASE_PATH"] = _TEST_DB  # force, even if the shell set one
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)

import pytest


@pytest.fixture(autouse=True)
def _clean_tables():
    """Wipe signal/draft rows between tests so state doesn't leak."""
    from app.models.feedback import drafts
    from app.models.signal_rules import signal_rules
    from app.models.signals import signals

    for table in (signals, signal_rules, drafts):
        for row in list(table()):
            table.delete(row.id)
    yield
