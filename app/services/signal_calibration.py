"""
Signal calibration (ADR 012 follow-on): how well do the signal rules predict
what instructors actually release?

For every draft of an assignment with released feedback, compare the signal
estimate per rubric category against the released (instructor-approved,
possibly adjusted) score. Systematic bias means the category's transforms
need retuning — this closes the loop that makes signal_rules self-correcting
instead of folklore.

Pure read-side computation: no network, no LLM, nothing written.
"""

from typing import Any

from app.models.assignment import rubric_categories, rubrics
from app.models.feedback import drafts
from app.services import feedback_review, signal_scorer
from app.utils.db_query import first, where

# |bias| below this is noise, not a calibration problem.
WELL_CALIBRATED_BAND = 5.0


def _verdict(bias: float) -> str:
    if abs(bias) < WELL_CALIBRATED_BAND:
        return "well calibrated"
    direction = "overestimates" if bias > 0 else "underestimates"
    return f"{direction} by ~{abs(bias):.0f} points"


def calibration_for_assignment(assignment_id: int) -> list[dict[str, Any]]:
    """
    Per-category calibration stats for an assignment.

    Returns one entry per rubric category that has at least one
    (signal estimate, released score) pair:
    ``{category_id, category_name, n, mean_estimate, mean_released,
    bias, mean_abs_error, verdict}`` where ``bias`` is mean(estimate -
    released): positive means the signals flatter the work.
    """
    rubric = first(rubrics, assignment_id=assignment_id)
    if rubric is None:
        return []
    categories = where(rubric_categories, rubric_id=rubric.id)
    if not categories:
        return []

    # (category_id) -> list of (estimate, released) score pairs
    pairs: dict[int, list[tuple[float, float]]] = {}

    for draft in where(drafts, assignment_id=assignment_id):
        released = {
            af.category_id: af.aggregated_score
            for af in feedback_review.released_feedback_for_draft(draft.id)
            if af.aggregated_score is not None
        }
        if not released:
            continue
        estimates = signal_scorer.category_estimates(draft.id, categories)
        for category_id, estimate in estimates.items():
            if category_id in released:
                pairs.setdefault(category_id, []).append(
                    (float(estimate["score"]), float(released[category_id]))
                )

    report = []
    for cat in categories:
        cat_pairs = pairs.get(cat.id)
        if not cat_pairs:
            continue
        n = len(cat_pairs)
        mean_estimate = sum(e for e, _ in cat_pairs) / n
        mean_released = sum(r for _, r in cat_pairs) / n
        bias = mean_estimate - mean_released
        mean_abs_error = sum(abs(e - r) for e, r in cat_pairs) / n
        report.append(
            {
                "category_id": cat.id,
                "category_name": cat.name,
                "n": n,
                "mean_estimate": round(mean_estimate, 1),
                "mean_released": round(mean_released, 1),
                "bias": round(bias, 1),
                "mean_abs_error": round(mean_abs_error, 1),
                "verdict": _verdict(bias),
            }
        )
    return report
