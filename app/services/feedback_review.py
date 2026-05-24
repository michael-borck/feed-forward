"""
Instructor review/approval of aggregated feedback (the approval gate).

Feedback is generated as ``pending_review`` and is invisible to students until an
instructor approves it (→ ``approved``, with a ``release_date``). This module holds
the gate's logic so it's testable without standing up the web layer.
"""

import contextlib
from datetime import datetime
from typing import Any

from app.models.feedback import aggregated_feedback

RELEASED = "approved"  # AggregatedFeedback.status value that students may see


def released_feedback_for_draft(draft_id: int) -> list[Any]:
    """Aggregated-feedback rows a student may see (instructor-approved/released)."""
    return [
        af
        for af in aggregated_feedback()
        if af.draft_id == draft_id and af.status == RELEASED
    ]


def has_pending_feedback(draft_id: int) -> bool:
    """True if feedback exists for the draft but isn't released yet."""
    return any(
        af.draft_id == draft_id and af.status != RELEASED
        for af in aggregated_feedback()
    )


def apply_review(
    draft_id: int, fields: dict[str, Any], instructor_email: str, approve: bool
) -> int:
    """
    Apply an instructor's edits to a draft's aggregated feedback.

    ``fields`` maps form names to values (``score_<id>`` / ``feedback_<id>``).
    ``approve=True`` releases the feedback (status → approved, stamps release_date).
    Returns the number of category rows updated.
    """
    now = datetime.now().isoformat()
    updated = 0
    for af in aggregated_feedback():
        if af.draft_id != draft_id:
            continue
        score_raw = fields.get(f"score_{af.id}")
        if score_raw not in (None, ""):
            with contextlib.suppress(TypeError, ValueError):
                af.aggregated_score = float(score_raw)
        fb_text = fields.get(f"feedback_{af.id}")
        if fb_text is not None:
            af.feedback_text = str(fb_text).strip()
        af.edited_by_instructor = True
        af.instructor_email = instructor_email
        if approve:
            af.status = RELEASED
            af.release_date = now
        aggregated_feedback.update(af)
        updated += 1
    return updated
