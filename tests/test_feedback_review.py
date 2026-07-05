"""Tests for the approval gate logic (release filtering + instructor edits)."""

from app.services import feedback_review


def _id(res):
    return res.id if hasattr(res, "id") else res


def _seed_agg(draft_id, category_id=10, score=50.0, status="pending_review"):
    from app.models.feedback import AggregatedFeedback, aggregated_feedback

    return _id(
        aggregated_feedback.insert(
            AggregatedFeedback(
                draft_id=draft_id,
                category_id=category_id,
                aggregated_score=score,
                feedback_text="orig",
                edited_by_instructor=False,
                instructor_email="",
                release_date="",
                status=status,
            )
        )
    )


def test_pending_feedback_is_hidden():
    _seed_agg(1, status="pending_review")
    assert feedback_review.released_feedback_for_draft(1) == []
    assert feedback_review.has_pending_feedback(1) is True


def test_approved_feedback_is_released():
    aid = _seed_agg(2, status="approved")
    released = feedback_review.released_feedback_for_draft(2)
    assert len(released) == 1 and released[0].id == aid
    assert feedback_review.has_pending_feedback(2) is False


def test_apply_review_approve_releases_and_edits():
    from app.models.feedback import aggregated_feedback

    aid = _seed_agg(3, score=50.0, status="pending_review")
    n = feedback_review.apply_review(
        3,
        {f"score_{aid}": "82", f"feedback_{aid}": "  great work  "},
        "instructor@example.com",
        approve=True,
    )
    assert n == 1
    af = next(a for a in aggregated_feedback() if a.id == aid)
    assert af.aggregated_score == 82.0
    assert af.feedback_text == "great work"  # trimmed
    assert af.status == "approved"
    assert af.release_date != ""
    assert af.edited_by_instructor  # stored as 1 by SQLite
    assert af.instructor_email == "instructor@example.com"
    # Now visible to the student:
    assert len(feedback_review.released_feedback_for_draft(3)) == 1


def test_apply_review_save_keeps_pending():
    from app.models.feedback import aggregated_feedback

    aid = _seed_agg(4, score=50.0, status="pending_review")
    feedback_review.apply_review(4, {f"score_{aid}": "60"}, "i@e.com", approve=False)
    af = next(a for a in aggregated_feedback() if a.id == aid)
    assert af.aggregated_score == 60.0  # edit saved
    assert af.status == "pending_review"  # but not released
    assert af.release_date == ""
    assert feedback_review.released_feedback_for_draft(4) == []


def test_apply_review_ignores_bad_score():
    from app.models.feedback import aggregated_feedback

    aid = _seed_agg(5, score=50.0)
    feedback_review.apply_review(
        5, {f"score_{aid}": "notanumber"}, "i@e.com", approve=False
    )
    af = next(a for a in aggregated_feedback() if a.id == aid)
    assert af.aggregated_score == 50.0  # unchanged on bad input


# ---- bulk_approve ----


def test_bulk_approve_empty_ids_is_a_noop():
    _seed_agg(10, status="pending_review")
    res = feedback_review.bulk_approve([], "i@e.com")
    assert res == {"drafts_approved": 0, "rows_released": 0}
    # Nothing was released:
    assert feedback_review.has_pending_feedback(10) is True


def test_bulk_approve_releases_all_pending_for_listed_drafts():
    from app.models.feedback import aggregated_feedback

    # Three drafts, each with one pending row.
    aids = [
        _seed_agg(d, category_id=10 + d, status="pending_review") for d in (11, 12, 13)
    ]
    res = feedback_review.bulk_approve([11, 12, 13], "i@e.com")
    assert res == {"drafts_approved": 3, "rows_released": 3}
    for did, aid in zip([11, 12, 13], aids, strict=True):
        af = next(a for a in aggregated_feedback() if a.id == aid)
        assert af.status == "approved"
        assert af.release_date != ""
        assert af.instructor_email == "i@e.com"
        # Bulk-approve does NOT claim edits:
        assert not af.edited_by_instructor
        # Visible to the student now:
        assert len(feedback_review.released_feedback_for_draft(did)) == 1


def test_bulk_approve_skips_already_released_rows():
    from app.models.feedback import aggregated_feedback

    already = _seed_agg(14, status="approved")
    pending = _seed_agg(14, category_id=99, status="pending_review")

    res = feedback_review.bulk_approve([14], "i@e.com")
    assert res == {"drafts_approved": 1, "rows_released": 1}  # only the pending one

    af_already = next(a for a in aggregated_feedback() if a.id == already)
    assert af_already.release_date == ""  # not re-stamped
    af_pending = next(a for a in aggregated_feedback() if a.id == pending)
    assert af_pending.status == "approved"


def test_bulk_approve_leaves_unrelated_drafts_alone():
    from app.models.feedback import aggregated_feedback

    other_aid = _seed_agg(15, status="pending_review")
    listed_aid = _seed_agg(16, status="pending_review")

    feedback_review.bulk_approve([16], "i@e.com")

    other = next(a for a in aggregated_feedback() if a.id == other_aid)
    listed = next(a for a in aggregated_feedback() if a.id == listed_aid)
    assert other.status == "pending_review"  # not in the set, untouched
    assert listed.status == "approved"


def test_bulk_approve_drafts_touched_counts_unique_drafts_not_rows():
    """One draft with two pending rows still counts as ONE draft approved."""
    _seed_agg(17, category_id=20, status="pending_review")
    _seed_agg(17, category_id=21, status="pending_review")

    res = feedback_review.bulk_approve([17], "i@e.com")
    assert res == {"drafts_approved": 1, "rows_released": 2}
