"""
Characterization tests for the feedback aggregation that the signal refactor
(task 11) must preserve. These pin current behaviour BEFORE the refactor:

- per-category scores are averaged into one AggregatedFeedback row, and
- only scores whose model_run is in ``successful_runs`` contribute — the exact
  hook the synthetic "Signal Engine" ModelRun will use to join aggregation.

(Async tests run automatically: pyproject sets asyncio_mode = auto.)
"""

from types import SimpleNamespace

from app.services.feedback_generator import FeedbackGenerationResult, FeedbackGenerator


def _id(res):
    return res.id if hasattr(res, "id") else res


async def test_aggregate_feedback_averages_category_scores():
    from app.models.assignment import (
        Rubric,
        RubricCategory,
        rubric_categories,
        rubrics,
    )
    from app.models.feedback import (
        CategoryScore,
        aggregated_feedback,
        category_scores,
    )

    rid = _id(rubrics.insert(
        Rubric(assignment_id=1, assessment_type_id=1, type_specific_criteria="")))
    cid = _id(rubric_categories.insert(
        RubricCategory(rubric_id=rid, name="Clarity", description="", weight=1.0)))
    category_scores.insert(CategoryScore(model_run_id=101, category_id=cid, score=60.0, confidence=0.8))
    category_scores.insert(CategoryScore(model_run_id=102, category_id=cid, score=80.0, confidence=0.8))

    gen = FeedbackGenerator()
    await gen._aggregate_feedback(
        SimpleNamespace(id=5),
        SimpleNamespace(id=1),
        SimpleNamespace(aggregation_method_id=999),  # unknown -> falls back to Average
        [
            FeedbackGenerationResult(model_run_id=101, success=True),
            FeedbackGenerationResult(model_run_id=102, success=True),
        ],
    )

    agg = [a for a in aggregated_feedback() if a.draft_id == 5]
    assert len(agg) == 1
    assert agg[0].category_id == cid
    assert agg[0].aggregated_score == 70.0  # mean(60, 80)
    # Current behaviour. The refactor will flip this to "pending_review".
    assert agg[0].status == "approved"


async def test_aggregate_only_counts_successful_runs():
    from app.models.assignment import (
        Rubric,
        RubricCategory,
        rubric_categories,
        rubrics,
    )
    from app.models.feedback import (
        CategoryScore,
        aggregated_feedback,
        category_scores,
    )

    rid = _id(rubrics.insert(
        Rubric(assignment_id=2, assessment_type_id=1, type_specific_criteria="")))
    cid = _id(rubric_categories.insert(
        RubricCategory(rubric_id=rid, name="Clarity", description="", weight=1.0)))
    category_scores.insert(CategoryScore(model_run_id=201, category_id=cid, score=50.0, confidence=0.8))
    category_scores.insert(CategoryScore(model_run_id=202, category_id=cid, score=90.0, confidence=0.8))

    gen = FeedbackGenerator()
    await gen._aggregate_feedback(
        SimpleNamespace(id=6),
        SimpleNamespace(id=2),
        SimpleNamespace(aggregation_method_id=999),
        [FeedbackGenerationResult(model_run_id=201, success=True)],  # 202 excluded
    )

    agg = [a for a in aggregated_feedback() if a.draft_id == 6]
    assert len(agg) == 1
    assert agg[0].aggregated_score == 50.0  # 202 not in successful_runs -> excluded
