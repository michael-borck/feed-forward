"""Tests for signal calibration (estimates vs instructor-released scores)."""

from datetime import datetime

from app.services import feedback_review, signal_calibration


def _seed_assignment_with_category():
    from app.models.assignment import (
        Assignment,
        Rubric,
        RubricCategory,
        assignments,
        rubric_categories,
        rubrics,
    )

    now = datetime.now().isoformat()
    a = assignments.insert(
        Assignment(
            course_id=1,
            title="Essay",
            created_by="i@example.com",
            status="active",
            created_at=now,
        )
    )
    r = rubrics.insert(Rubric(assignment_id=a.id, assessment_type_id=0))
    cat = rubric_categories.insert(
        RubricCategory(
            rubric_id=r.id,
            name="Clarity",
            description="",
            weight=1.0,
        )
    )
    return a, cat


def _seed_draft(assignment_id, flesch, released_score, cat, status=None):
    """A draft with one signal (flesch_score) and one released score."""
    from app.models.feedback import (
        AggregatedFeedback,
        Draft,
        aggregated_feedback,
        drafts,
    )
    from app.models.signals import Signal, signals

    now = datetime.now().isoformat()
    d = drafts.insert(
        Draft(
            assignment_id=assignment_id,
            student_email="s@example.com",
            version=1,
            content="",
            submission_date=now,
            status="feedback_ready",
            word_count=0,
        )
    )
    signals.insert(
        Signal(
            draft_id=d.id,
            source="document-analyser",
            name="flesch_score",
            value=flesch,
            raw="",
            created_at=now,
        )
    )
    aggregated_feedback.insert(
        AggregatedFeedback(
            draft_id=d.id,
            category_id=cat.id,
            aggregated_score=released_score,
            feedback_text="",
            edited_by_instructor=True,
            instructor_email="i@example.com",
            status=status or feedback_review.RELEASED,
            release_date=now,
        )
    )
    return d


def test_calibration_reports_bias():
    a, cat = _seed_assignment_with_category()
    # flesch 55 -> "Clarity" auto-match band gives estimate 85
    _seed_draft(a.id, flesch=55.0, released_score=70.0, cat=cat)
    _seed_draft(a.id, flesch=55.0, released_score=80.0, cat=cat)

    report = signal_calibration.calibration_for_assignment(a.id)
    assert len(report) == 1
    row = report[0]
    assert row["category_name"] == "Clarity"
    assert row["n"] == 2
    assert row["mean_estimate"] == 85.0
    assert row["mean_released"] == 75.0
    assert row["bias"] == 10.0
    assert row["mean_abs_error"] == 10.0
    assert "overestimates" in row["verdict"]


def test_calibration_well_calibrated_band():
    a, cat = _seed_assignment_with_category()
    _seed_draft(a.id, flesch=55.0, released_score=83.0, cat=cat)  # estimate 85

    report = signal_calibration.calibration_for_assignment(a.id)
    assert report[0]["verdict"] == "well calibrated"


def test_calibration_ignores_unreleased_feedback():
    a, cat = _seed_assignment_with_category()
    _seed_draft(
        a.id, flesch=55.0, released_score=60.0, cat=cat, status="pending_review"
    )

    assert signal_calibration.calibration_for_assignment(a.id) == []


def test_calibration_empty_without_rubric():
    assert signal_calibration.calibration_for_assignment(999999) == []
