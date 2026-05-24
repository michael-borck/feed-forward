"""Tests for the synthetic Signal Engine run (signals -> ModelRun + CategoryScores)."""

from app.services import signal_evidence


def _id(res):
    return res.id if hasattr(res, "id") else res


def _seed_draft(draft_id, assignment_id):
    from app.models.feedback import Draft, drafts

    drafts.insert(Draft(
        id=draft_id, assignment_id=assignment_id, student_email="s@example.com",
        version=1, content="x", submission_date="t", status="feedback_ready",
        word_count=1,
    ))


def _seed_rubric(assignment_id, category_name="Clarity"):
    from app.models.assignment import Rubric, RubricCategory, rubric_categories, rubrics

    rid = _id(rubrics.insert(
        Rubric(assignment_id=assignment_id, assessment_type_id=1, type_specific_criteria="")))
    cid = _id(rubric_categories.insert(
        RubricCategory(rubric_id=rid, name=category_name, description="", weight=1.0)))
    return cid


def test_produce_signal_run_writes_category_scores():
    from app.models.feedback import category_scores, model_runs
    from app.models.signals import Signal, signals

    _seed_draft(10, assignment_id=1)
    cid = _seed_rubric(assignment_id=1)
    signals.insert(Signal(draft_id=10, source="document-analyser",
                          name="flesch_score", value=45.0, raw="", created_at="t"))

    run_id = signal_evidence.produce_signal_run(10)
    assert run_id is not None

    run = [r for r in model_runs() if r.id == run_id][0]
    assert run.model_id == signal_evidence.SIGNAL_MODEL_ID
    assert run.status == "complete"

    scores = [s for s in category_scores() if s.model_run_id == run_id]
    assert len(scores) == 1
    assert scores[0].category_id == cid
    assert scores[0].score == 72.0  # flesch 45 -> band [30,50) -> 72


def test_produce_signal_run_no_rubric_returns_none():
    _seed_draft(11, assignment_id=99)  # no rubric for assignment 99
    assert signal_evidence.produce_signal_run(11) is None


def test_produce_signal_run_no_signals_returns_none():
    _seed_draft(12, assignment_id=2)
    _seed_rubric(assignment_id=2)  # category exists, but no signals were extracted
    assert signal_evidence.produce_signal_run(12) is None
