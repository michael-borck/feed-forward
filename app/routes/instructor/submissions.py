"""
Instructor submission review and feedback management routes
"""

import builtins
import contextlib
from datetime import datetime

from fasthtml import common as fh
from fastlite import NotFoundError

from app import instructor_required, rt
from app.models.assignment import assignments
from app.models.course import courses
from app.models.feedback import (
    aggregated_feedback,
    drafts,
    model_runs,
)
from app.models.user import Role, users
from app.utils.ui import card, dashboard_layout


@rt("/instructor/assignments/{assignment_id}/submissions")
@instructor_required
def instructor_submissions_list(session, assignment_id: int):
    """List all submissions for an assignment with feedback status"""
    # Get current user
    user = users[session["auth"]]

    # Get assignment and verify ownership
    try:
        assignment = assignments[assignment_id]
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    # Get course and verify instructor owns it
    try:
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return fh.RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all drafts for this assignment
    all_drafts = drafts()
    assignment_drafts = [d for d in all_drafts if d.assignment_id == assignment_id]

    # Get aggregated feedback for status
    all_agg_feedback = aggregated_feedback()
    agg_feedback_map = {}
    for af in all_agg_feedback:
        if af.draft_id not in agg_feedback_map:
            agg_feedback_map[af.draft_id] = []
        agg_feedback_map[af.draft_id].append(af)

    # Get model runs for additional stats
    all_runs = model_runs()
    runs_map = {}
    for run in all_runs:
        if run.draft_id not in runs_map:
            runs_map[run.draft_id] = []
        runs_map[run.draft_id].append(run)

    # Build submissions data
    submissions_data = []
    for draft in assignment_drafts:
        # Get feedback status
        feedback_list = agg_feedback_map.get(draft.id, [])
        runs_list = runs_map.get(draft.id, [])

        # Calculate status
        if draft.status == "submitted":
            status = "pending"
            status_color = "yellow"
        elif draft.status == "processing":
            status = "processing"
            status_color = "blue"
        elif draft.status == "feedback_ready":
            if feedback_list and any(
                af.status == "pending_review" for af in feedback_list
            ):
                status = "needs_review"
                status_color = "orange"
            elif feedback_list and any(af.status == "approved" for af in feedback_list):
                status = "approved"
                status_color = "green"
            else:
                status = "ready"
                status_color = "green"
        elif draft.status == "error":
            status = "error"
            status_color = "red"
        else:
            status = draft.status
            status_color = "gray"

        # Calculate AI model stats
        total_runs = len(runs_list)
        successful_runs = len([r for r in runs_list if r.status == "complete"])
        failed_runs = len([r for r in runs_list if r.status == "error"])

        submissions_data.append(
            {
                "draft": draft,
                "status": status,
                "status_color": status_color,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "has_feedback": len(feedback_list) > 0,
                "feedback_status": feedback_list[0].status if feedback_list else "none",
            }
        )

    # Sort by submission date (newest first)
    submissions_data.sort(key=lambda x: x["draft"].submission_date, reverse=True)

    # Build submissions table
    if submissions_data:
        table_rows = []
        for sub in submissions_data:
            draft = sub["draft"]

            # Status badge
            status_badge_elem = fh.Span(
                sub["status"].replace("_", " ").title(),
                cls=f"px-2 py-1 text-xs font-medium rounded-full bg-{sub['status_color']}-100 text-{sub['status_color']}-800",
            )

            # AI Models info
            if sub["total_runs"] > 0:
                models_info = f"{sub['successful_runs']}/{sub['total_runs']} models"
                if sub["failed_runs"] > 0:
                    models_info += f" ({sub['failed_runs']} failed)"
            else:
                models_info = "No runs"

            # Action buttons
            actions = fh.Div(
                fh.A(
                    "View Details",
                    href=f"/instructor/submissions/{draft.id}",
                    cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium mr-3",
                ),
                fh.A(
                    "Signals",
                    href=f"/instructor/submissions/{draft.id}/signals",
                    cls="text-emerald-600 hover:text-emerald-800 text-sm font-medium mr-3",
                ),
                cls="flex items-center",
            )

            # Add review/approve actions if needed
            if sub["status"] == "needs_review":
                actions.children.insert(
                    0,
                    fh.A(
                        "Review Feedback",
                        href=f"/instructor/submissions/{draft.id}/review",
                        cls="text-orange-600 hover:text-orange-800 text-sm font-medium mr-3",
                    ),
                )

            table_rows.append(
                fh.Tr(
                    fh.Td(draft.student_email, cls="px-4 py-3 text-sm"),
                    fh.Td(f"Version {draft.version}", cls="px-4 py-3 text-sm"),
                    fh.Td(f"{draft.word_count} words", cls="px-4 py-3 text-sm"),
                    fh.Td(
                        datetime.fromisoformat(draft.submission_date).strftime(
                            "%b %d, %Y %I:%M %p"
                        ),
                        cls="px-4 py-3 text-sm",
                    ),
                    fh.Td(status_badge_elem, cls="px-4 py-3"),
                    fh.Td(models_info, cls="px-4 py-3 text-sm text-gray-600"),
                    fh.Td(actions, cls="px-4 py-3"),
                )
            )

        submissions_table = fh.Div(
            fh.Table(
                fh.Thead(
                    fh.Tr(
                        fh.Th(
                            "Student",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "Version",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "Length",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "Submitted",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "Status",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "AI Models",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        fh.Th(
                            "Actions",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                    )
                ),
                fh.Tbody(*table_rows, cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg",
        )
    else:
        submissions_table = fh.Div(
            fh.P("No submissions yet.", cls="text-gray-500 text-center py-8"),
            cls="bg-white rounded-lg shadow",
        )

    # Stats summary
    total_submissions = len(submissions_data)
    pending_review = len([s for s in submissions_data if s["status"] == "needs_review"])
    completed = len(
        [s for s in submissions_data if s["status"] in ["approved", "ready"]]
    )

    stats_cards = fh.Div(
        fh.Div(
            fh.Div(
                fh.P("Total Submissions", cls="text-sm font-medium text-gray-500"),
                fh.P(str(total_submissions), cls="text-2xl font-bold text-gray-900"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        fh.Div(
            fh.Div(
                fh.P("Pending Review", cls="text-sm font-medium text-gray-500"),
                fh.P(str(pending_review), cls="text-2xl font-bold text-orange-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        fh.Div(
            fh.Div(
                fh.P("Completed", cls="text-sm font-medium text-gray-500"),
                fh.P(str(completed), cls="text-2xl font-bold text-green-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
    )

    # Build page content
    main_content = fh.Div(
        # Header
        fh.Div(
            fh.Div(
                fh.H1(
                    f"Submissions: {assignment.title}",
                    cls="text-2xl font-bold text-gray-900",
                ),
                fh.P(f"Course: {course.name}", cls="text-gray-600"),
                cls="flex-1",
            ),
            fh.Div(
                fh.A(
                    "← Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                fh.A(
                    "Analytics",
                    href=f"/instructor/assignments/{assignment_id}/analytics",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
                ),
                fh.A(
                    "Signal Rules",
                    href=f"/instructor/assignments/{assignment_id}/signal-rules",
                    cls="bg-emerald-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-emerald-700 transition-colors ml-3",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Stats
        stats_cards,
        # Submissions table
        submissions_table,
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.H3("Quick Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        fh.Div(
            fh.A(
                "Export Data",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            fh.A(
                "Bulk Review",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            fh.A(
                "Assignment Settings",
                href=f"/instructor/assignments/{assignment_id}/edit",
                cls="block text-indigo-600 hover:text-indigo-800",
            ),
        ),
    )

    return dashboard_layout(
        f"Submissions: {assignment.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/submissions",
    )


@rt("/instructor/submissions/{draft_id}")
@instructor_required
def instructor_submission_detail(session, draft_id: int):
    """View detailed submission information with AI feedback breakdown"""
    import json

    # Get current user
    user = users[session["auth"]]

    # Get draft
    try:
        draft = drafts[draft_id]
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    # Get assignment and verify ownership
    try:
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return fh.RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all model runs for this draft
    all_runs = model_runs()
    draft_runs = [r for r in all_runs if r.draft_id == draft_id]

    # Get aggregated feedback
    all_agg_feedback = aggregated_feedback()
    agg_feedback = [af for af in all_agg_feedback if af.draft_id == draft_id]

    # Build model results
    model_results = []
    for run in draft_runs:
        result = {
            "model_name": run.model_name,
            "status": run.status,
            "execution_time": run.execution_time,
            "rubric_scores": {},
            "overall_score": None,
            "general_feedback": None,
            "error": run.error_message,
        }

        if run.response:
            try:
                response_data = json.loads(run.response)
                result["overall_score"] = response_data.get("overall_score")
                result["general_feedback"] = response_data.get("general_feedback")
                result["rubric_scores"] = response_data.get("rubric_scores", {})
            except Exception:
                pass

        model_results.append(result)

    # Get aggregated scores
    agg_scores = {}
    agg_feedback_text = None
    if agg_feedback:
        af = agg_feedback[0]  # Should only be one per draft
        agg_feedback_text = af.aggregated_feedback
        if af.aggregated_scores:
            with contextlib.suppress(builtins.BaseException):
                agg_scores = json.loads(af.aggregated_scores)

    # Build model results table
    model_cards = []
    for result in model_results:
        status_color = "green" if result["status"] == "complete" else "red"
        status_text = "Success" if result["status"] == "complete" else "Failed"

        # Score display
        score_display = "-"
        if result["overall_score"] is not None:
            score_display = f"{result['overall_score']:.1f}%"

        card_content = fh.Div(
            fh.Div(
                fh.H4(result["model_name"], cls="font-semibold text-gray-900"),
                fh.Span(
                    status_text,
                    cls=f"text-xs px-2 py-1 rounded-full bg-{status_color}-100 text-{status_color}-800",
                ),
                cls="flex items-center justify-between mb-2",
            ),
            fh.Div(
                fh.P(f"Score: {score_display}", cls="text-sm text-gray-600"),
                fh.P(
                    f"Time: {result['execution_time']:.1f}s"
                    if result["execution_time"]
                    else "Time: -",
                    cls="text-sm text-gray-600",
                ),
                cls="space-y-1",
            ),
        )

        if result["error"]:
            card_content.children.append(
                fh.P(f"Error: {result['error']}", cls="text-xs text-red-600 mt-2")
            )

        model_cards.append(card(card_content))

    # Build main content
    main_content = fh.Div(
        # Header
        fh.Div(
            fh.Div(
                fh.H1("Submission Details", cls="text-2xl font-bold text-gray-900"),
                fh.P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                cls="flex-1",
            ),
            fh.Div(
                fh.A(
                    "← Back to Submissions",
                    href=f"/instructor/assignments/{assignment.assignment_id}/submissions",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Student info
        fh.Div(
            fh.H3("Student Information", cls="text-lg font-semibold text-gray-900 mb-3"),
            fh.Div(
                fh.P(f"Email: {draft.student_email}", cls="text-gray-700"),
                fh.P(f"Version: {draft.version}", cls="text-gray-700"),
                fh.P(f"Word Count: {draft.word_count}", cls="text-gray-700"),
                fh.P(
                    f"Submitted: {datetime.fromisoformat(draft.submission_date).strftime('%B %d, %Y at %I:%M %p')}",
                    cls="text-gray-700",
                ),
                cls="space-y-1",
            ),
            cls="bg-white p-6 rounded-lg shadow mb-6",
        ),
        # AI Model Results
        fh.Div(
            fh.H3("AI Model Evaluations", cls="text-lg font-semibold text-gray-900 mb-3"),
            fh.Div(*model_cards, cls="grid grid-cols-1 md:grid-cols-3 gap-4")
            if model_cards
            else fh.P("No AI evaluations available.", cls="text-gray-500"),
            cls="mb-6",
        ),
        # Aggregated Feedback
        fh.Div(
            fh.H3("Aggregated Feedback", cls="text-lg font-semibold text-gray-900 mb-3"),
            (
                fh.Div(
                    fh.Div(
                        fh.P("Overall Score", cls="text-sm text-gray-600"),
                        fh.P(
                            f"{agg_scores.get('overall_score', 0):.1f}%",
                            cls="text-2xl font-bold text-indigo-600",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.H4("Feedback", cls="font-medium text-gray-800 mb-2"),
                        fh.P(
                            agg_feedback_text or "No feedback available.",
                            cls="text-gray-700",
                        ),
                        cls="",
                    ),
                    cls="",
                )
                if agg_feedback
                else fh.P("No aggregated feedback available.", cls="text-gray-500")
            ),
            cls="bg-white p-6 rounded-lg shadow mb-6",
        ),
        # Actions
        fh.Div(
            fh.A(
                "Review & Edit Feedback",
                href=f"/instructor/submissions/{draft_id}/review",
                cls="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors",
            ),
            cls="flex justify-end",
        ),
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.H3("Submission Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        fh.Div(
            fh.A(
                "View Student Work",
                href=f"/instructor/submissions/{draft_id}/edit",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            fh.A(
                "Export Feedback",
                href=f"/instructor/submissions/{draft_id}/export",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            fh.A(
                "Email Student",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800",
            ),
        ),
    )

    return dashboard_layout(
        "Submission Details | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}",
    )


# ----------------------------------------------------------------------
# Signal analysis (ADR 012 / SIGNAL_INTEGRATION_PLAN.md, phase S1)
# Read-only view of deterministic lens signals for a draft. Lives on its own
# route rather than the detail view (which references stale ModelRun fields).
# ----------------------------------------------------------------------

_SIGNAL_LABELS = {
    "word_count": "Word count",
    "sentence_count": "Sentence count",
    "paragraph_count": "Paragraph count",
    "avg_words_per_sentence": "Avg words / sentence",
    "flesch_score": "Flesch reading ease",
    "flesch_kincaid_grade": "Flesch-Kincaid grade",
    "passive_voice_percentage": "Passive voice %",
    "sentence_variety": "Sentence variety",
    "academic_tone": "Academic tone",
    "transition_words": "Transition words",
    "hedging_language": "Hedging language",
    "unique_words": "Unique words",
    "total_words": "Total words",
    "vocabulary_richness": "Vocabulary richness",
}


def _signal_row(label: str, value: float):
    return fh.Div(
        fh.Span(label, cls="text-sm text-gray-600"),
        fh.Span(f"{value:.1f}", cls="text-sm font-semibold text-gray-900"),
        cls="flex items-center justify-between py-2 border-b border-gray-100 last:border-0",
    )


def _verify_draft_ownership(session, draft_id: int):
    """Return (draft, assignment) if the current instructor owns it, else None."""
    user = users[session["auth"]]
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
    except NotFoundError:
        return None
    if course.instructor_email != user.email:
        return None
    return draft, assignment


@rt("/instructor/submissions/{draft_id}/signals")
@instructor_required
def instructor_submission_signals(session, draft_id: int):
    """Read-only view of lens signals extracted for a draft (ADR 012, S1)."""
    from app.services.signal_service import get_signals_for_draft

    owned = _verify_draft_ownership(session, draft_id)
    if owned is None:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)
    draft, assignment = owned

    draft_signals = get_signals_for_draft(draft_id)

    # Estimated rubric scores from signals (auto-matched; instructor reviews/adjusts).
    from app.models.assignment import rubric_categories, rubrics
    from app.services import signal_scorer

    rubric = next((r for r in rubrics() if r.assignment_id == draft.assignment_id), None)
    categories = (
        [c for c in rubric_categories() if c.rubric_id == rubric.id] if rubric else []
    )
    estimates = signal_scorer.category_estimates(draft_id, categories) if categories else {}

    if categories and estimates:
        est_rows = []
        for cat in categories:
            e = estimates.get(cat.id)
            if e:
                badge = "auto-suggested" if e["suggested"] else "instructor-set"
                value = fh.Span(
                    f"{e['score']:.0f} ",
                    fh.Span(
                        f"· {badge} · conf {e['confidence']:.2f}",
                        cls="text-xs text-gray-400",
                    ),
                    cls="text-sm font-semibold text-gray-900",
                )
            else:
                value = fh.Span(
                    "— LLM only (no signal maps here)", cls="text-sm text-gray-400"
                )
            est_rows.append(
                fh.Div(
                    fh.Span(cat.name, cls="text-sm text-gray-600"),
                    value,
                    cls="flex items-center justify-between py-2 border-b border-gray-100 last:border-0",
                )
            )
        estimates_section = fh.Div(
            fh.H4("Estimated rubric scores", cls="font-semibold text-gray-900 mb-1"),
            fh.P(
                "Auto-matched from signals — review and adjust; not a mark.",
                cls="text-xs text-gray-400 mb-2",
            ),
            fh.Div(*est_rows),
            cls="bg-white p-6 rounded-lg shadow mb-6 border-l-4 border-emerald-400",
        )
    else:
        estimates_section = fh.Div()

    by_source: dict[str, list] = {}
    for s in draft_signals:
        by_source.setdefault(s.source, []).append(s)

    if draft_signals:
        panels = []
        for source, items in by_source.items():
            rows = [
                _signal_row(_SIGNAL_LABELS.get(s.name, s.name), s.value)
                for s in sorted(items, key=lambda x: x.name)
            ]
            panels.append(
                fh.Div(
                    fh.H4(source, cls="font-semibold text-gray-900 mb-2"),
                    fh.Div(*rows),
                    cls="bg-white p-6 rounded-lg shadow mb-6",
                )
            )
        body = fh.Div(*panels)
    else:
        body = fh.Div(
            fh.P(
                "No signals extracted yet. Signals are computed from the submission "
                "via the document-analyser service while the draft content is still "
                "available. If the service was offline at submission time, use the "
                "button below to retry (only works while the draft content remains).",
                cls="text-gray-600",
            ),
            cls="bg-white p-6 rounded-lg shadow mb-6",
        )

    main_content = fh.Div(
        fh.Div(
            fh.Div(
                fh.H1("Signal Analysis", cls="text-2xl font-bold text-gray-900"),
                fh.P(
                    f"{draft.student_email} · Version {draft.version} · {assignment.title}",
                    cls="text-gray-600",
                ),
                cls="flex-1",
            ),
            fh.A(
                "← Back to Submissions",
                href=f"/instructor/assignments/{draft.assignment_id}/submissions",
                cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        fh.P(
            "Deterministic metrics from the lens analyser family — read-only evidence "
            "for review, not a score (ADR 012).",
            cls="text-sm text-gray-500 mb-4",
        ),
        estimates_section,
        body,
        fh.A(
            "Run extraction now",
            href=f"/instructor/submissions/{draft_id}/signals/extract",
            cls="inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors",
        ),
        cls="max-w-4xl mx-auto px-4 py-6",
    )

    return dashboard_layout(
        "Signal Analysis | FeedForward",
        fh.Div(),
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}/signals",
    )


@rt("/instructor/submissions/{draft_id}/signals/extract")
@instructor_required
def instructor_submission_signals_extract(session, draft_id: int):
    """Manually (re)run signal extraction for a draft, then show the signals."""
    from app.services.signal_service import extract_signals_for_draft

    owned = _verify_draft_ownership(session, draft_id)
    if owned is None:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    extract_signals_for_draft(draft_id)
    return fh.RedirectResponse(
        f"/instructor/submissions/{draft_id}/signals", status_code=303
    )


@rt("/instructor/submissions/{draft_id}/review")
@instructor_required
def instructor_feedback_review(session, draft_id: int):
    """Review and edit AI-generated feedback before approval"""

    # Get current user
    user = users[session["auth"]]

    # Get draft and verify permissions
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return fh.RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    # Re-review is allowed; approval state lives on each AggregatedFeedback row.

    # Get aggregated feedback
    all_agg_feedback = aggregated_feedback()
    agg_feedback = [af for af in all_agg_feedback if af.draft_id == draft_id]

    if not agg_feedback:
        return fh.Div(
            fh.H2("No Feedback Available", cls="text-xl font-bold text-gray-900 mb-4"),
            fh.P("This submission hasn't been processed yet.", cls="text-gray-600"),
            fh.A(
                "← Back to Submission",
                href=f"/instructor/submissions/{draft_id}",
                cls="text-indigo-600 hover:text-indigo-800",
            ),
            cls="max-w-2xl mx-auto p-6",
        )

    # Per-category review cards: editable score + feedback, with signal estimate context.
    from app.models.assignment import rubric_categories as _rcats
    from app.services import signal_scorer

    cat_names = {c.id: c.name for c in _rcats()}
    cats_for_draft = [c for c in _rcats() if any(a.category_id == c.id for a in agg_feedback)]
    estimates = signal_scorer.category_estimates(draft_id, cats_for_draft)

    category_cards = []
    for af in agg_feedback:
        est = estimates.get(af.category_id)
        est_note = (
            f"signal estimate {est['score']:.0f} (conf {est['confidence']:.2f})"
            if est
            else "no signal estimate"
        )
        status_note = "released" if af.status == "approved" else "pending review"
        category_cards.append(
            fh.Div(
                fh.Div(
                    fh.H4(
                        cat_names.get(af.category_id, f"Category {af.category_id}"),
                        cls="font-semibold text-gray-900",
                    ),
                    fh.Span(
                        f"{status_note} · {est_note}", cls="text-xs text-gray-400"
                    ),
                    cls="flex items-center justify-between mb-2",
                ),
                fh.Div(
                    fh.Label(
                        "Score (0-100)",
                        for_=f"score_{af.id}",
                        cls="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    fh.Input(
                        type="number",
                        id=f"score_{af.id}",
                        name=f"score_{af.id}",
                        value=str(round(af.aggregated_score or 0)),
                        min="0",
                        max="100",
                        cls="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    ),
                    cls="mb-3",
                ),
                fh.Div(
                    fh.Label(
                        "Feedback",
                        for_=f"feedback_{af.id}",
                        cls="block text-sm font-medium text-gray-700 mb-1",
                    ),
                    fh.Textarea(
                        af.feedback_text or "",
                        id=f"feedback_{af.id}",
                        name=f"feedback_{af.id}",
                        rows=5,
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    ),
                    cls="mb-1",
                ),
                cls="bg-white p-5 rounded-lg shadow mb-4",
            )
        )

    feedback_form = fh.Form(
        *category_cards,
        fh.Div(
            fh.Button(
                "Approve & release to student",
                type="submit",
                name="action",
                value="approve",
                cls="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors",
            ),
            fh.Button(
                "Save draft (keep hidden)",
                type="submit",
                name="action",
                value="save",
                cls="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors ml-3",
            ),
            fh.A(
                "Cancel",
                href=f"/instructor/submissions/{draft_id}/signals",
                cls="ml-3 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
            ),
            cls="flex items-center",
        ),
        action=f"/instructor/submissions/{draft_id}/review/save",
        method="post",
    )

    # Build main content
    main_content = fh.Div(
        # Header
        fh.Div(
            fh.H1("Review Feedback", cls="text-2xl font-bold text-gray-900 mb-2"),
            fh.P(f"Student: {draft.student_email}", cls="text-gray-600"),
            fh.P(f"Assignment: {assignment.title}", cls="text-gray-600"),
            cls="mb-6",
        ),
        # Form
        feedback_form,
        cls="max-w-4xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.H3("Review Guidelines", cls="text-lg font-semibold text-gray-900 mb-4"),
        fh.Div(
            fh.P("• Check for accuracy", cls="text-sm text-gray-600 mb-1"),
            fh.P("• Ensure constructive tone", cls="text-sm text-gray-600 mb-1"),
            fh.P("• Add specific examples", cls="text-sm text-gray-600 mb-1"),
            fh.P("• Personalize feedback", cls="text-sm text-gray-600 mb-1"),
            fh.P("• Verify score fairness", cls="text-sm text-gray-600"),
            cls="bg-gray-50 p-4 rounded-lg",
        ),
    )

    return dashboard_layout(
        "Review Feedback | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}/review",
    )


@rt("/instructor/submissions/{draft_id}/review/save")
@instructor_required
async def instructor_feedback_save(session, request, draft_id: int, action: str = "save"):
    """Save per-category reviewed feedback; 'approve' releases it to the student."""
    user = users[session["auth"]]

    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return fh.RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    form = await request.form()
    approving = action == "approve"

    from app.services import feedback_review

    feedback_review.apply_review(draft_id, dict(form), user.email, approving)

    if approving:
        return fh.RedirectResponse(
            f"/instructor/assignments/{draft.assignment_id}/submissions",
            status_code=303,
        )
    return fh.RedirectResponse(
        f"/instructor/submissions/{draft_id}/review", status_code=303
    )


# ----------------------------------------------------------------------
# Signal rules editor (ADR 012, S2) — confirm/override the signal -> rubric mapping.
# ----------------------------------------------------------------------

def _verify_assignment_ownership(session, assignment_id: int):
    """Return the assignment if the current instructor owns its course, else None."""
    user = users[session["auth"]]
    try:
        assignment = assignments[assignment_id]
        course = courses[assignment.course_id]
    except NotFoundError:
        return None
    if course.instructor_email != user.email:
        return None
    return assignment


def _transform_summary(transform_json) -> str:
    import json as _json

    try:
        t = _json.loads(transform_json) if isinstance(transform_json, str) else (transform_json or {})
    except (ValueError, TypeError):
        return ""
    if t.get("type") == "band":
        return "banded thresholds"
    if t.get("type") == "linear":
        out = t.get("out", [0, 100])
        direction = "higher is better" if out and out[0] <= out[-1] else "lower is better"
        return f"linear ({direction})"
    return ""


@rt("/instructor/assignments/{assignment_id}/signal-rules")
@instructor_required
def instructor_signal_rules(session, assignment_id: int):
    """Editor for an assignment's signal -> rubric rules (confirm/override)."""
    from app.services import signal_rules_service

    assignment = _verify_assignment_ownership(session, assignment_id)
    if assignment is None:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    cards = []
    for entry in signal_rules_service.rules_view_for_assignment(assignment_id):
        cat = entry["category"]
        rules = entry["rules"]
        if not rules:
            rows = [
                fh.P(
                    "No signals map to this category — graded by the LLM only.",
                    cls="text-sm text-gray-400",
                )
            ]
        else:
            rows = []
            for r in rules:
                sig = r["signal_name"]
                rows.append(
                    fh.Div(
                        fh.Div(
                            fh.Label(
                                fh.Input(
                                    type="checkbox",
                                    name=f"en_{cat.id}_{sig}",
                                    checked=r["enabled"],
                                    cls="mr-2",
                                ),
                                _SIGNAL_LABELS.get(sig, sig),
                                cls="text-sm text-gray-700 flex items-center",
                            ),
                            fh.Span(
                                _transform_summary(r["transform"]),
                                cls="text-xs text-gray-400 ml-3",
                            ),
                            cls="flex items-center",
                        ),
                        fh.Div(
                            fh.Label("weight", cls="text-xs text-gray-500 mr-2"),
                            fh.Input(
                                type="number",
                                step="0.1",
                                min="0",
                                name=f"w_{cat.id}_{sig}",
                                value=str(r["weight"]),
                                cls="w-20 px-2 py-1 border border-gray-300 rounded-md text-sm",
                            ),
                            cls="flex items-center",
                        ),
                        cls="flex items-center justify-between py-2 border-b border-gray-100 last:border-0",
                    )
                )
        saved = any(r.get("persisted") for r in rules)
        cards.append(
            fh.Div(
                fh.Div(
                    fh.H4(cat.name, cls="font-semibold text-gray-900"),
                    fh.Span(
                        "saved" if saved else "auto-suggested (not yet saved)",
                        cls="text-xs text-gray-400",
                    ),
                    cls="flex items-center justify-between mb-2",
                ),
                *rows,
                cls="bg-white p-5 rounded-lg shadow mb-4",
            )
        )

    form = fh.Form(
        *cards,
        fh.Button(
            "Save rules",
            type="submit",
            cls="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors",
        ),
        action=f"/instructor/assignments/{assignment_id}/signal-rules/save",
        method="post",
    )

    main_content = fh.Div(
        fh.Div(
            fh.Div(
                fh.H1("Signal Rules", cls="text-2xl font-bold text-gray-900"),
                fh.P(assignment.title, cls="text-gray-600"),
                cls="flex-1",
            ),
            fh.A(
                "← Back to Submissions",
                href=f"/instructor/assignments/{assignment_id}/submissions",
                cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        fh.P(
            "Map document signals to rubric categories. Auto-matched defaults are shown — "
            "adjust the weight, enable/disable, and save. Saved rules drive the estimated "
            "scores instructors review (ADR 012).",
            cls="text-sm text-gray-500 mb-4",
        ),
        form,
        cls="max-w-3xl mx-auto px-4 py-6",
    )
    return dashboard_layout(
        "Signal Rules | FeedForward",
        fh.Div(),
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/signal-rules",
    )


@rt("/instructor/assignments/{assignment_id}/signal-rules/save")
@instructor_required
async def instructor_signal_rules_save(session, request, assignment_id: int):
    """Persist the signal -> rubric rules (confirm/override)."""
    from app.services import signal_rules_service

    if _verify_assignment_ownership(session, assignment_id) is None:
        return fh.RedirectResponse("/instructor/dashboard", status_code=303)

    form = await request.form()
    signal_rules_service.save_rules_for_assignment(assignment_id, dict(form))
    return fh.RedirectResponse(
        f"/instructor/assignments/{assignment_id}/signal-rules", status_code=303
    )
