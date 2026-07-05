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

    rid = _id(
        rubrics.insert(
            Rubric(assignment_id=1, assessment_type_id=1, type_specific_criteria="")
        )
    )
    cid = _id(
        rubric_categories.insert(
            RubricCategory(rubric_id=rid, name="Clarity", description="", weight=1.0)
        )
    )
    category_scores.insert(
        CategoryScore(model_run_id=101, category_id=cid, score=60.0, confidence=0.8)
    )
    category_scores.insert(
        CategoryScore(model_run_id=102, category_id=cid, score=80.0, confidence=0.8)
    )

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
    # Feedback is gated for instructor review before students see it (approval gate).
    assert agg[0].status == "pending_review"
    assert agg[0].release_date == ""


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

    rid = _id(
        rubrics.insert(
            Rubric(assignment_id=2, assessment_type_id=1, type_specific_criteria="")
        )
    )
    cid = _id(
        rubric_categories.insert(
            RubricCategory(rubric_id=rid, name="Clarity", description="", weight=1.0)
        )
    )
    category_scores.insert(
        CategoryScore(model_run_id=201, category_id=cid, score=50.0, confidence=0.8)
    )
    category_scores.insert(
        CategoryScore(model_run_id=202, category_id=cid, score=90.0, confidence=0.8)
    )

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


async def test_signal_scores_blend_with_llm_scores():
    """End-to-end S2: a signal run's CategoryScores aggregate alongside an LLM run."""
    from app.models.assignment import (
        Rubric,
        RubricCategory,
        rubric_categories,
        rubrics,
    )
    from app.models.feedback import (
        CategoryScore,
        Draft,
        aggregated_feedback,
        category_scores,
        drafts,
    )
    from app.models.signals import Signal, signals
    from app.services import signal_evidence

    drafts.insert(
        Draft(
            id=20,
            assignment_id=3,
            student_email="s@example.com",
            version=1,
            content="x",
            submission_date="t",
            status="feedback_ready",
            word_count=1,
        )
    )
    rid = _id(
        rubrics.insert(
            Rubric(assignment_id=3, assessment_type_id=1, type_specific_criteria="")
        )
    )
    cid = _id(
        rubric_categories.insert(
            RubricCategory(rubric_id=rid, name="Clarity", description="", weight=1.0)
        )
    )
    # An LLM run scored this category 60.
    category_scores.insert(
        CategoryScore(model_run_id=301, category_id=cid, score=60.0, confidence=0.8)
    )
    # A signal that auto-matches "Clarity" -> 72 (flesch 45).
    signals.insert(
        Signal(
            draft_id=20,
            source="document-analyser",
            name="flesch_score",
            value=45.0,
            raw="",
            created_at="t",
        )
    )

    signal_run = signal_evidence.produce_signal_run(20)
    assert signal_run is not None

    gen = FeedbackGenerator()
    await gen._aggregate_feedback(
        SimpleNamespace(id=20),
        SimpleNamespace(id=3),
        SimpleNamespace(aggregation_method_id=999),
        [
            FeedbackGenerationResult(model_run_id=301, success=True),
            FeedbackGenerationResult(model_run_id=signal_run, success=True),
        ],
    )

    agg = [a for a in aggregated_feedback() if a.draft_id == 20]
    assert len(agg) == 1
    assert agg[0].aggregated_score == 66.0  # mean(LLM 60, signal 72)
