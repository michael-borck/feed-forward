"""
LLM usage / cost reporting (Phase 3).

Rolls up the per-run token counts and cost captured on ``model_runs`` (see
``feedback_generator._extract_usage``) into per-assignment and per-course
totals — answering "what does this cost per cohort". Pure read-side; no network.

Only real LLM runs are counted (``model_id > 0``): the signal-engine sentinel
(``-1``) and mock runs (``0``) carry no token cost.
"""

from typing import Any

from app.models.assignment import assignments
from app.models.course import courses
from app.models.feedback import drafts, model_runs
from app.utils.db_query import where


def _is_llm_run(run: Any) -> bool:
    return (getattr(run, "model_id", 0) or 0) > 0


def _blank() -> dict[str, Any]:
    return {"llm_runs": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}


def _accumulate(acc: dict[str, Any], run: Any) -> None:
    acc["llm_runs"] += 1
    acc["input_tokens"] += int(getattr(run, "input_tokens", 0) or 0)
    acc["output_tokens"] += int(getattr(run, "output_tokens", 0) or 0)
    acc["cost_usd"] += float(getattr(run, "cost_usd", 0.0) or 0.0)


def usage_for_draft_ids(draft_ids: set[int]) -> dict[str, Any]:
    """Aggregate LLM usage across a set of draft ids."""
    totals = _blank()
    if not draft_ids:
        return totals
    for run in model_runs():
        if _is_llm_run(run) and run.draft_id in draft_ids:
            _accumulate(totals, run)
    totals["cost_usd"] = round(totals["cost_usd"], 4)
    return totals


def usage_for_assignment(assignment_id: int) -> dict[str, Any]:
    """Total LLM usage for one assignment (across all its drafts)."""
    draft_ids = {d.id for d in where(drafts, assignment_id=assignment_id)}
    return usage_for_draft_ids(draft_ids)


def usage_for_course(course_id: int) -> dict[str, Any]:
    """Total LLM usage for one course (across all its assignments' drafts)."""
    assignment_ids = {a.id for a in where(assignments, course_id=course_id)}
    draft_ids = {d.id for d in drafts() if d.assignment_id in assignment_ids}
    return usage_for_draft_ids(draft_ids)


def usage_by_course(instructor_email: str | None = None) -> list[dict[str, Any]]:
    """Per-course usage rows, optionally scoped to one instructor's courses.

    Single pass over model_runs (drafts → assignments → course) so the report
    stays one scan regardless of cohort size. Returns rows sorted by cost
    descending: ``{course_id, course_code, course_title, ...usage}``.
    """
    course_list = [
        c
        for c in courses()
        if instructor_email is None or c.instructor_email == instructor_email
    ]
    course_by_id = {c.id: c for c in course_list}
    if not course_by_id:
        return []

    # draft_id -> course_id (only for drafts in the in-scope courses)
    assignment_course = {
        a.id: a.course_id for a in assignments() if a.course_id in course_by_id
    }
    draft_course = {
        d.id: assignment_course[d.assignment_id]
        for d in drafts()
        if d.assignment_id in assignment_course
    }

    totals: dict[int, dict[str, Any]] = {cid: _blank() for cid in course_by_id}
    for run in model_runs():
        if not _is_llm_run(run):
            continue
        course_id = draft_course.get(run.draft_id)
        if course_id is not None:
            _accumulate(totals[course_id], run)

    rows = []
    for course_id, acc in totals.items():
        c = course_by_id[course_id]
        rows.append(
            {
                "course_id": course_id,
                "course_code": getattr(c, "code", ""),
                "course_title": getattr(c, "title", ""),
                **acc,
                "cost_usd": round(acc["cost_usd"], 4),
            }
        )
    rows.sort(key=lambda r: r["cost_usd"], reverse=True)
    return rows
