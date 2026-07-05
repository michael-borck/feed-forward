"""Tests for LLM usage/cost rollups (Phase 3)."""

from datetime import datetime
from types import SimpleNamespace

from app.services import usage_report
from app.services.feedback_generator import _extract_usage

# ---- _extract_usage (per-run capture) ----


def test_extract_usage_reads_litellm_token_counts():
    resp = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=1200, completion_tokens=340), model="x"
    )
    u = _extract_usage(resp)
    assert u["input_tokens"] == 1200
    assert u["output_tokens"] == 340
    assert isinstance(u["cost_usd"], float)


def test_extract_usage_missing_usage_is_zeros():
    assert _extract_usage(SimpleNamespace(model="x")) == {
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
    }


def _course(code="C1", title="Course", instructor="i@example.com"):
    from app.models.course import Course, courses

    now = datetime.now().isoformat()
    return courses.insert(
        Course(
            code=code,
            title=title,
            term="S1",
            department="CS",
            description="",
            instructor_email=instructor,
            status="active",
            created_at=now,
            updated_at=now,
        )
    )


def _assignment(course_id):
    from app.models.assignment import Assignment, assignments

    now = datetime.now().isoformat()
    return assignments.insert(
        Assignment(
            course_id=course_id,
            title="A",
            created_by="i@example.com",
            status="active",
            created_at=now,
        )
    )


def _draft(assignment_id):
    from app.models.feedback import Draft, drafts

    return drafts.insert(
        Draft(
            assignment_id=assignment_id,
            student_email="s@example.com",
            version=1,
            content="x",
            submission_date=datetime.now().isoformat(),
            status="feedback_ready",
            word_count=1,
        )
    )


def _run(draft_id, model_id, inp=0, out=0, cost=0.0, status="complete"):
    from app.models.feedback import ModelRun, model_runs

    return model_runs.insert(
        ModelRun(
            draft_id=draft_id,
            model_id=model_id,
            run_number=1,
            timestamp=datetime.now().isoformat(),
            prompt="",
            raw_response="",
            status=status,
            input_tokens=inp,
            output_tokens=out,
            cost_usd=cost,
        )
    )


def test_usage_for_assignment_sums_llm_runs():
    c = _course()
    a = _assignment(c.id)
    d = _draft(a.id)
    _run(d.id, model_id=5, inp=1000, out=200, cost=0.012)
    _run(d.id, model_id=7, inp=500, out=100, cost=0.006)

    u = usage_report.usage_for_assignment(a.id)
    assert u["llm_runs"] == 2
    assert u["input_tokens"] == 1500
    assert u["output_tokens"] == 300
    assert u["cost_usd"] == 0.018


def test_excludes_signal_and_mock_runs():
    c = _course()
    a = _assignment(c.id)
    d = _draft(a.id)
    _run(d.id, model_id=5, inp=1000, out=200, cost=0.01)
    _run(d.id, model_id=-1, inp=0, out=0, cost=0.0)  # signal engine
    _run(d.id, model_id=0, inp=0, out=0, cost=0.0)  # mock

    u = usage_report.usage_for_assignment(a.id)
    assert u["llm_runs"] == 1  # only the real LLM run
    assert u["input_tokens"] == 1000


def test_usage_for_course_spans_assignments():
    c = _course()
    a1, a2 = _assignment(c.id), _assignment(c.id)
    d1, d2 = _draft(a1.id), _draft(a2.id)
    _run(d1.id, model_id=5, inp=100, out=10, cost=0.001)
    _run(d2.id, model_id=5, inp=300, out=30, cost=0.003)

    u = usage_report.usage_for_course(c.id)
    assert u["llm_runs"] == 2
    assert u["input_tokens"] == 400
    assert u["cost_usd"] == 0.004


def test_usage_by_course_sorted_by_cost():
    cheap = _course(code="CHEAP")
    pricey = _course(code="PRICEY")
    dc = _draft(_assignment(cheap.id).id)
    dp = _draft(_assignment(pricey.id).id)
    _run(dc.id, model_id=5, inp=10, out=1, cost=0.001)
    _run(dp.id, model_id=5, inp=9999, out=999, cost=0.5)

    rows = usage_report.usage_by_course()
    codes = [r["course_code"] for r in rows]
    assert codes.index("PRICEY") < codes.index("CHEAP")  # pricier first
    assert rows[0]["cost_usd"] == 0.5


def test_usage_by_course_scoped_to_instructor():
    mine = _course(code="MINE", instructor="me@example.com")
    other = _course(code="OTHER", instructor="other@example.com")
    _run(_draft(_assignment(mine.id).id).id, model_id=5, inp=10, out=1, cost=0.001)
    _run(_draft(_assignment(other.id).id).id, model_id=5, inp=10, out=1, cost=0.001)

    rows = usage_report.usage_by_course(instructor_email="me@example.com")
    assert {r["course_code"] for r in rows} == {"MINE"}


def test_empty_when_no_runs():
    a = _assignment(_course().id)
    assert usage_report.usage_for_assignment(a.id) == {
        "llm_runs": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cost_usd": 0.0,
    }
