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
    from app.models.assessment import assessment_types, submission_files
    from app.models.assignment import assignments, rubric_categories, rubrics
    from app.models.course import courses, enrollments
    from app.models.feedback import (
        aggregated_feedback,
        category_scores,
        drafts,
        feedback_items,
        model_runs,
    )
    from app.models.signal_rules import signal_rules
    from app.models.signals import signals

    tables = (
        signals,
        signal_rules,
        category_scores,
        feedback_items,
        aggregated_feedback,
        model_runs,
        rubric_categories,
        rubrics,
        drafts,
        submission_files,
        assignments,
        assessment_types,
        courses,
        enrollments,
    )
    for table in tables:
        for row in list(table()):
            table.delete(row.id)
    yield


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Auth rate limiting is per-IP; the test client shares one IP, so
    clear the in-memory buckets between tests."""
    from app.utils import rate_limit

    rate_limit._BUCKETS.clear()
    yield
    rate_limit._BUCKETS.clear()
