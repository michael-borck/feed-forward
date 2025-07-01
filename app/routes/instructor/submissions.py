"""
Instructor submission review and feedback management routes
"""

from datetime import datetime

from fasthtml.common import *
from fastlite import NotFoundError
from starlette.responses import RedirectResponse

from app import instructor_required, rt
from app.models.assignment import assignments
from app.models.course import courses
from app.models.feedback import (aggregated_feedback, drafts, feedback,
                                model_runs, Draft, Feedback)
from app.models.user import Role, users
from app.utils.ui import action_button, card, dashboard_layout, status_badge


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
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get course and verify instructor owns it
    try:
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

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
            status_badge_elem = Span(
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
            actions = Div(
                A(
                    "View Details",
                    href=f"/instructor/submissions/{draft.id}",
                    cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium mr-3",
                ),
                cls="flex items-center",
            )

            # Add review/approve actions if needed
            if sub["status"] == "needs_review":
                actions.children.insert(
                    0,
                    A(
                        "Review Feedback",
                        href=f"/instructor/submissions/{draft.id}/review",
                        cls="text-orange-600 hover:text-orange-800 text-sm font-medium mr-3",
                    ),
                )

            table_rows.append(
                Tr(
                    Td(draft.student_email, cls="px-4 py-3 text-sm"),
                    Td(f"Version {draft.version}", cls="px-4 py-3 text-sm"),
                    Td(f"{draft.word_count} words", cls="px-4 py-3 text-sm"),
                    Td(
                        datetime.fromisoformat(draft.submission_date).strftime(
                            "%b %d, %Y %I:%M %p"
                        ),
                        cls="px-4 py-3 text-sm",
                    ),
                    Td(status_badge_elem, cls="px-4 py-3"),
                    Td(models_info, cls="px-4 py-3 text-sm text-gray-600"),
                    Td(actions, cls="px-4 py-3"),
                )
            )

        submissions_table = Div(
            Table(
                Thead(
                    Tr(
                        Th(
                            "Student",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Version",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Length",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Submitted",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Status",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "AI Models",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Actions",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                    )
                ),
                Tbody(*table_rows, cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg",
        )
    else:
        submissions_table = Div(
            P("No submissions yet.", cls="text-gray-500 text-center py-8"),
            cls="bg-white rounded-lg shadow",
        )

    # Stats summary
    total_submissions = len(submissions_data)
    pending_review = len([s for s in submissions_data if s["status"] == "needs_review"])
    completed = len(
        [s for s in submissions_data if s["status"] in ["approved", "ready"]]
    )

    stats_cards = Div(
        Div(
            Div(
                P("Total Submissions", cls="text-sm font-medium text-gray-500"),
                P(str(total_submissions), cls="text-2xl font-bold text-gray-900"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Pending Review", cls="text-sm font-medium text-gray-500"),
                P(str(pending_review), cls="text-2xl font-bold text-orange-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Completed", cls="text-sm font-medium text-gray-500"),
                P(str(completed), cls="text-2xl font-bold text-green-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
    )

    # Build page content
    main_content = Div(
        # Header
        Div(
            Div(
                H1(
                    f"Submissions: {assignment.title}",
                    cls="text-2xl font-bold text-gray-900",
                ),
                P(f"Course: {course.name}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                A(
                    "Analytics",
                    href=f"/instructor/assignments/{assignment_id}/analytics",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
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
    sidebar_content = Div(
        H3("Quick Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            A(
                "Export Data",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Bulk Review",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
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
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get assignment and verify ownership
    try:
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

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
            except:
                pass

        model_results.append(result)

    # Get aggregated scores
    agg_scores = {}
    agg_feedback_text = None
    if agg_feedback:
        af = agg_feedback[0]  # Should only be one per draft
        agg_feedback_text = af.aggregated_feedback
        if af.aggregated_scores:
            try:
                agg_scores = json.loads(af.aggregated_scores)
            except:
                pass

    # Build model results table
    model_cards = []
    for result in model_results:
        status_color = "green" if result["status"] == "complete" else "red"
        status_text = "Success" if result["status"] == "complete" else "Failed"

        # Score display
        score_display = "-"
        if result["overall_score"] is not None:
            score_display = f"{result['overall_score']:.1f}%"

        card_content = Div(
            Div(
                H4(result["model_name"], cls="font-semibold text-gray-900"),
                Span(
                    status_text,
                    cls=f"text-xs px-2 py-1 rounded-full bg-{status_color}-100 text-{status_color}-800",
                ),
                cls="flex items-center justify-between mb-2",
            ),
            Div(
                P(f"Score: {score_display}", cls="text-sm text-gray-600"),
                P(
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
                P(f"Error: {result['error']}", cls="text-xs text-red-600 mt-2")
            )

        model_cards.append(card(card_content))

    # Build main content
    main_content = Div(
        # Header
        Div(
            Div(
                H1("Submission Details", cls="text-2xl font-bold text-gray-900"),
                P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Submissions",
                    href=f"/instructor/assignments/{assignment.assignment_id}/submissions",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Student info
        Div(
            H3("Student Information", cls="text-lg font-semibold text-gray-900 mb-3"),
            Div(
                P(f"Email: {draft.student_email}", cls="text-gray-700"),
                P(f"Version: {draft.version}", cls="text-gray-700"),
                P(f"Word Count: {draft.word_count}", cls="text-gray-700"),
                P(
                    f"Submitted: {datetime.fromisoformat(draft.submission_date).strftime('%B %d, %Y at %I:%M %p')}",
                    cls="text-gray-700",
                ),
                cls="space-y-1",
            ),
            cls="bg-white p-6 rounded-lg shadow mb-6",
        ),
        # AI Model Results
        Div(
            H3("AI Model Evaluations", cls="text-lg font-semibold text-gray-900 mb-3"),
            Div(*model_cards, cls="grid grid-cols-1 md:grid-cols-3 gap-4")
            if model_cards
            else P("No AI evaluations available.", cls="text-gray-500"),
            cls="mb-6",
        ),
        # Aggregated Feedback
        Div(
            H3("Aggregated Feedback", cls="text-lg font-semibold text-gray-900 mb-3"),
            (
                Div(
                    Div(
                        P("Overall Score", cls="text-sm text-gray-600"),
                        P(
                            f"{agg_scores.get('overall_score', 0):.1f}%",
                            cls="text-2xl font-bold text-indigo-600",
                        ),
                        cls="mb-4",
                    ),
                    Div(
                        H4("Feedback", cls="font-medium text-gray-800 mb-2"),
                        P(agg_feedback_text or "No feedback available.", cls="text-gray-700"),
                        cls="",
                    ),
                    cls="",
                )
                if agg_feedback
                else P("No aggregated feedback available.", cls="text-gray-500")
            ),
            cls="bg-white p-6 rounded-lg shadow mb-6",
        ),
        # Actions
        Div(
            A(
                "Review & Edit Feedback",
                href=f"/instructor/submissions/{draft_id}/review",
                cls="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors",
            ),
            cls="flex justify-end",
        ),
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Submission Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            A(
                "View Student Work",
                href=f"/instructor/submissions/{draft_id}/edit",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Export Feedback",
                href=f"/instructor/submissions/{draft_id}/export",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Email Student",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800",
            ),
        ),
    )

    return dashboard_layout(
        f"Submission Details | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}",
    )


@rt("/instructor/submissions/{draft_id}/review")
@instructor_required
def instructor_feedback_review(session, draft_id: int):
    """Review and edit AI-generated feedback before approval"""
    import json
    
    # Get current user
    user = users[session["auth"]]

    # Get draft and verify permissions
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Check if feedback is already approved
    all_feedback = feedback()
    existing_feedback = [f for f in all_feedback if f.draft_id == draft_id]
    if existing_feedback and existing_feedback[0].instructor_approved:
        return RedirectResponse(f"/instructor/submissions/{draft_id}", status_code=303)

    # Get aggregated feedback
    all_agg_feedback = aggregated_feedback()
    agg_feedback = [af for af in all_agg_feedback if af.draft_id == draft_id]

    if not agg_feedback:
        return Div(
            H2("No Feedback Available", cls="text-xl font-bold text-gray-900 mb-4"),
            P("This submission hasn't been processed yet.", cls="text-gray-600"),
            A(
                "← Back to Submission",
                href=f"/instructor/submissions/{draft_id}",
                cls="text-indigo-600 hover:text-indigo-800",
            ),
            cls="max-w-2xl mx-auto p-6",
        )

    af = agg_feedback[0]
    agg_scores = {}
    if af.aggregated_scores:
        try:
            agg_scores = json.loads(af.aggregated_scores)
        except:
            pass

    # Build feedback form
    feedback_form = Form(
        # Overall Score
        Div(
            Label("Overall Score (%)", for_="overall_score",
                  cls="block text-sm font-medium text-gray-700 mb-2"),
            Input(
                type="number",
                id="overall_score",
                name="overall_score",
                value=str(int(agg_scores.get("overall_score", 0))),
                min="0",
                max="100",
                required=True,
                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            cls="mb-4",
        ),
        # Feedback Text
        Div(
            Label("Feedback", for_="feedback_text",
                  cls="block text-sm font-medium text-gray-700 mb-2"),
            Textarea(
                af.aggregated_feedback or "",
                id="feedback_text",
                name="feedback_text",
                rows=10,
                required=True,
                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
            ),
            P(
                "Edit the AI-generated feedback to personalize it for the student.",
                cls="text-sm text-gray-500 mt-1",
            ),
            cls="mb-6",
        ),
        # Approval Checkbox
        Div(
            Label(
                cls="flex items-center",
                children=[
                    Input(
                        type="checkbox",
                        name="approve",
                        value="true",
                        cls="mr-2",
                    ),
                    Span("Approve this feedback for student viewing",
                         cls="text-sm text-gray-700"),
                ],
            ),
            cls="mb-6",
        ),
        # Submit buttons
        Div(
            Button(
                "Save & Send to Student",
                type="submit",
                name="action",
                value="approve",
                cls="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors",
            ),
            Button(
                "Save Draft",
                type="submit",
                name="action",
                value="save",
                cls="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors ml-3",
            ),
            A(
                "Cancel",
                href=f"/instructor/submissions/{draft_id}",
                cls="ml-3 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
            ),
            cls="flex items-center",
        ),
        action=f"/instructor/submissions/{draft_id}/review",
        method="post",
        cls="bg-white p-6 rounded-lg shadow",
    )

    # Build main content
    main_content = Div(
        # Header
        Div(
            H1("Review Feedback", cls="text-2xl font-bold text-gray-900 mb-2"),
            P(f"Student: {draft.student_email}", cls="text-gray-600"),
            P(f"Assignment: {assignment.title}", cls="text-gray-600"),
            cls="mb-6",
        ),
        # Form
        feedback_form,
        cls="max-w-4xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Review Guidelines", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            P("• Check for accuracy", cls="text-sm text-gray-600 mb-1"),
            P("• Ensure constructive tone", cls="text-sm text-gray-600 mb-1"),
            P("• Add specific examples", cls="text-sm text-gray-600 mb-1"),
            P("• Personalize feedback", cls="text-sm text-gray-600 mb-1"),
            P("• Verify score fairness", cls="text-sm text-gray-600"),
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


@rt("/instructor/submissions/{draft_id}/review")
@instructor_required
def instructor_feedback_save(session, draft_id: int, overall_score: int,
                           feedback_text: str, action: str = "save", approve: str = None):
    """Save reviewed feedback"""
    # Get current user
    user = users[session["auth"]]

    # Verify permissions
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Check if feedback already exists
    all_feedback = feedback()
    existing_feedback = [f for f in all_feedback if f.draft_id == draft_id]

    if existing_feedback:
        # Update existing feedback
        fb = existing_feedback[0]
        fb.overall_score = overall_score
        fb.general_feedback = feedback_text.strip()
        fb.instructor_approved = (action == "approve" or approve == "true")
        fb.approved_at = datetime.now() if fb.instructor_approved else None
        fb.approved_by = user.email if fb.instructor_approved else None
        feedback.update(fb)
    else:
        # Create new feedback record
        new_feedback = Feedback(
            id=None,
            draft_id=draft_id,
            overall_score=overall_score,
            general_feedback=feedback_text.strip(),
            rubric_scores="{}",  # Empty for now
            instructor_approved=(action == "approve" or approve == "true"),
            approved_at=datetime.now() if (action == "approve" or approve == "true") else None,
            approved_by=user.email if (action == "approve" or approve == "true") else None,
            created_at=datetime.now()
        )
        feedback.insert(new_feedback)

    # Update aggregated feedback status
    all_agg_feedback = aggregated_feedback()
    for af in all_agg_feedback:
        if af.draft_id == draft_id:
            af.status = "approved" if (action == "approve" or approve == "true") else "pending_review"
            aggregated_feedback.update(af)
            break

    # Redirect based on action
    if action == "approve" or approve == "true":
        return RedirectResponse(
            f"/instructor/assignments/{assignment.assignment_id}/submissions", status_code=303
        )
    else:
        return RedirectResponse(
            f"/instructor/submissions/{draft_id}/review", status_code=303
        )