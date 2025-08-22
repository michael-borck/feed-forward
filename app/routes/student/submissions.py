"""
Student submission routes
"""

from datetime import datetime

from fasthtml.common import *
from starlette.responses import RedirectResponse

from app import rt, student_required
from app.models.assignment import assignments
from app.models.course import courses
from app.models.feedback import Draft, drafts
from app.models.user import Role, users
from app.utils.privacy import calculate_word_count
from app.utils.ui import action_button, dashboard_layout, status_badge


def get_student_course(course_id, student_email):
    """
    Verify that the student is enrolled in the course and return the course.
    Returns (course, error_message) tuple.
    """
    # Find the course
    target_course = None
    try:
        # Get all courses to find the one with matching ID
        for course in courses():
            if course.id == course_id:
                target_course = course
                break

        if not target_course:
            return None, "Course not found"

        # Check if student is enrolled
        is_enrolled = False
        from app.models.course import enrollments

        for enrollment in enrollments():
            if (
                enrollment.course_id == course_id
                and enrollment.student_email == student_email
            ):
                is_enrolled = True
                break

        if not is_enrolled:
            return None, "You are not enrolled in this course"

        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {e!s}"


def get_student_assignment(assignment_id, student_email):
    """
    Verify that the student is enrolled in the course containing the assignment.
    Returns (assignment, course, error_message) tuple.
    """
    # Find the assignment
    target_assignment = None
    for assignment in assignments():
        if assignment.id == assignment_id:
            target_assignment = assignment
            break

    if not target_assignment:
        return None, None, "Assignment not found"

    # Check if student is enrolled in the course
    course_id = target_assignment.course_id

    # Use the course helper to verify enrollment
    course, error = get_student_course(course_id, student_email)
    if error:
        return None, None, error

    return target_assignment, course, None


@rt("/student/assignments/{assignment_id}/submit")
@student_required
def student_assignment_submit_form(session, request, assignment_id: int):
    """Student assignment submission form view"""
    # Get current user
    user = users[session["auth"]]

    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Get existing drafts for this assignment
    assignment_drafts = []

    for draft in drafts():
        if draft.assignment_id == assignment_id and draft.student_email == user.email:
            assignment_drafts.append(draft)

    # Determine if student can submit a new draft
    if len(assignment_drafts) >= assignment.max_drafts:
        return Div(
            P(
                f"You have reached the maximum number of drafts ({assignment.max_drafts}) for this assignment.",
                cls="text-red-600 bg-red-50 p-4 rounded-lg",
            ),
            A(
                "View Assignment",
                href=f"/student/assignments/{assignment_id}",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Calculate next draft version
    next_version = len(assignment_drafts) + 1

    # Get content from previous draft if available
    previous_content = ""
    if assignment_drafts:
        latest_draft = max(assignment_drafts, key=lambda d: d.version)
        previous_content = latest_draft.content

    # Sidebar content
    sidebar_content = Div(
        # Assignment info card
        Div(
            H3("Assignment Details", cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course: {course.title} ({course.code})", cls="text-gray-600 mb-2"),
            P(f"Due Date: {assignment.due_date}", cls="text-gray-600 mb-2"),
            P(f"Maximum Drafts: {assignment.max_drafts}", cls="text-gray-600 mb-2"),
            P(
                f"Current Draft: {next_version} of {assignment.max_drafts}",
                cls="text-indigo-700 font-medium mb-4",
            ),
            Div(
                action_button(
                    "Cancel",
                    color="gray",
                    href=f"/student/assignments/{assignment_id}",
                    icon="×",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Submission tips
        Div(
            H3("Submission Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Each submission counts as one draft",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P("• You cannot edit after submitting", cls="text-gray-600 mb-2 text-sm"),
            P(
                f"• You have {assignment.max_drafts - next_version + 1} remaining drafts",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Feedback will be provided after submission",
                cls="text-gray-600 text-sm",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Submission form
    main_content = Div(
        H2(
            f"Submit Draft {next_version} for {assignment.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        # Submission form
        Form(
            # Hidden fields for POST
            Input(type="hidden", name="assignment_id", value=str(assignment_id)),
            Input(type="hidden", name="version", value=str(next_version)),
            # Draft content textarea
            Div(
                Label(
                    "Your Draft",
                    for_="content",
                    cls="block text-lg font-semibold text-indigo-900 mb-2",
                ),
                P("Enter or paste your draft text below.", cls="text-gray-600 mb-1"),
                P(
                    "Note: For privacy reasons, your submission content will be automatically removed from our system after feedback is generated. Please keep your own copy.",
                    cls="text-amber-600 text-sm mb-4 font-medium",
                ),
                Textarea(
                    id="content",
                    name="content",
                    value=previous_content,
                    placeholder="Enter your draft here...",
                    rows="20",
                    cls="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono",
                ),
                cls="mb-6",
            ),
            # Submit button
            Div(
                Button(
                    "Submit Draft",
                    type="submit",
                    cls="bg-green-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors shadow-md",
                ),
                cls="text-center",
            ),
            # Form settings
            method="post",
            action=f"/student/assignments/{assignment_id}/submit",
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        f"Submit Draft - {assignment.title} | FeedForward",
        dashboard_layout(
            f"Submit Draft - {assignment.title}",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",  # Keep dashboard active in nav
        ),
    )


@rt("/student/assignments/{assignment_id}/submit")
@student_required
def student_assignment_submit_process(
    session, assignment_id: int, content: str, version: int
):
    """Student assignment submission POST handler"""
    # Get current user
    user = users[session["auth"]]

    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Validate content
    if not content or content.strip() == "":
        return Div(
            P(
                "Draft content cannot be empty.",
                cls="text-red-600 bg-red-50 p-4 rounded-lg",
            ),
            A(
                "Try Again",
                href=f"/student/assignments/{assignment_id}/submit",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Calculate word count for statistics
    word_count = calculate_word_count(content)

    # Create a new draft
    new_draft = Draft(
        assignment_id=assignment_id,
        student_email=user.email,
        version=version,
        content=content,
        submission_date=datetime.now().isoformat(),
        status="submitted",
        word_count=word_count,
    )

    # Insert the draft
    try:
        drafts.insert(new_draft)

        # Redirect to the assignment view to see the submitted draft
        return RedirectResponse(
            f"/student/assignments/{assignment_id}",
            status_code=303,
        )

    except Exception as e:
        return Div(
            P(
                f"Error submitting draft: {e!s}",
                cls="text-red-600 bg-red-50 p-4 rounded-lg",
            ),
            A(
                "Try Again",
                href=f"/student/assignments/{assignment_id}/submit",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )


@rt("/student/submissions")
@student_required
def student_submissions_list(session, request):
    """Student submissions history view"""
    # Get current user
    user = users[session["auth"]]

    # Get all student drafts
    student_drafts = []

    for draft in drafts():
        if draft.student_email == user.email:
            # Skip drafts that are marked as hidden by student if the flag exists and is True
            if hasattr(draft, "hidden_by_student") and draft.hidden_by_student:
                continue
            student_drafts.append(draft)

    # Sort drafts by submission date (newest first)
    student_drafts.sort(key=lambda d: d.submission_date, reverse=True)

    # Group drafts by assignment
    draft_groups = {}
    assignment_info = {}
    course_info = {}

    # Get assignment and course information
    for draft in student_drafts:
        if draft.assignment_id not in assignment_info:
            # Find assignment
            for a in assignments():
                if a.id == draft.assignment_id:
                    assignment_info[a.id] = a

                    # Find course for this assignment
                    for c in courses():
                        if c.id == a.course_id:
                            course_info[c.id] = c
                            break
                    break

        # Group drafts by assignment
        if draft.assignment_id not in draft_groups:
            draft_groups[draft.assignment_id] = []
        draft_groups[draft.assignment_id].append(draft)

    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3(
                "Submission Management",
                cls="text-xl font-semibold text-indigo-900 mb-2",
            ),
            P(
                "This page allows you to view and manage all your submissions across courses.",
                cls="text-gray-600 mb-4",
            ),
            P(
                "• Your submission content is removed after feedback is generated",
                cls="text-gray-600 text-sm mb-1",
            ),
            P(
                "• You can hide submissions you no longer need to see",
                cls="text-gray-600 text-sm mb-1",
            ),
            P(
                "• Hidden submissions still count toward your draft limits",
                cls="text-gray-600 text-sm mb-1",
            ),
            P(
                "• Draft statistics are preserved for analytics",
                cls="text-gray-600 text-sm mb-1",
            ),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/student/dashboard", icon="←"
                ),
                cls="mt-4",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Submission stats
        Div(
            H3(
                "Submission Statistics",
                cls="text-xl font-semibold text-indigo-900 mb-4",
            ),
            P(f"Total Submissions: {len(student_drafts)}", cls="text-gray-600 mb-2"),
            P(f"Active Assignments: {len(draft_groups)}", cls="text-gray-600 mb-2"),
            # Count drafts by status
            P(
                f"Feedback Available: {sum(1 for d in student_drafts if d.status == 'feedback_ready')}",
                cls="text-gray-600 mb-2",
            ),
            P(
                f"Processing: {sum(1 for d in student_drafts if d.status == 'processing')}",
                cls="text-gray-600 mb-2",
            ),
            A(
                "View Hidden Submissions",
                hx_get="/student/submissions/hidden",
                hx_target="#main-content",
                cls="text-sm text-indigo-600 hover:underline block mt-4",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - grouped submissions with management options
    main_content = Div(
        H2(
            "Your Submission History",
            cls="text-2xl font-bold text-indigo-900 mb-6",
            id="main-content",
        ),
        # If no submissions yet
        (
            P(
                "You haven't submitted any drafts yet.",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center mb-8",
            )
            if not student_drafts
            else ""
        ),
        # Submissions by assignment
        *(
            Div(
                H3(
                    Div(
                        Span(
                            assignment_info[assignment_id].title,
                            cls="text-xl font-bold text-indigo-800",
                        ),
                        Span(
                            f" ({course_info[assignment_info[assignment_id].course_id].code})",
                            cls="text-gray-600 font-normal text-base",
                        ),
                    ),
                    cls="mb-4",
                ),
                # Table of drafts for this assignment
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th(
                                    "Draft",
                                    cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                                ),
                                Th(
                                    "Date",
                                    cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                                ),
                                Th(
                                    "Status",
                                    cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                                ),
                                Th(
                                    "Words",
                                    cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                                ),
                                Th(
                                    "Actions",
                                    cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                                ),
                            )
                        ),
                        Tbody(
                            *(
                                Tr(
                                    # Draft number
                                    Td(str(draft.version), cls="py-3 px-4 font-medium"),
                                    # Submission date
                                    Td(
                                        draft.submission_date.split("T")[0]
                                        if "T" in draft.submission_date
                                        else draft.submission_date,
                                        cls="py-3 px-4 text-gray-600",
                                    ),
                                    # Status with badge
                                    Td(
                                        status_badge(
                                            draft.status.replace("_", " ").capitalize(),
                                            "green"
                                            if draft.status == "feedback_ready"
                                            else "yellow"
                                            if draft.status == "processing"
                                            else "blue",
                                        ),
                                        cls="py-3 px-4",
                                    ),
                                    # Word count
                                    Td(
                                        str(getattr(draft, "word_count", "N/A")),
                                        cls="py-3 px-4 text-gray-600",
                                    ),
                                    # Action buttons
                                    Td(
                                        Div(
                                            A(
                                                "View",
                                                href=f"/student/assignments/{assignment_id}#draft-{draft.id}",
                                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                                            ),
                                            Button(
                                                "Hide",
                                                hx_post=f"/student/submissions/hide/{draft.id}",
                                                hx_confirm="This will hide the draft from your history. It will still count toward your draft limit. Continue?",
                                                hx_target=f"#draft-row-{draft.id}",
                                                cls="text-xs px-3 py-1 bg-gray-600 text-white rounded-md hover:bg-gray-700",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-3 px-4",
                                    ),
                                    id=f"draft-row-{draft.id}",
                                    cls="border-b border-gray-100 hover:bg-gray-50",
                                )
                                for draft in sorted(
                                    draft_groups[assignment_id],
                                    key=lambda d: d.version,
                                    reverse=True,
                                )
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 overflow-x-auto mb-8",
                ),
            )
            for assignment_id in draft_groups
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Submission History | FeedForward",
        dashboard_layout(
            "Submission History",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",  # Keep dashboard active in nav
        ),
    )


@rt("/student/submissions/hide/{draft_id}")
@student_required
def student_submission_hide(session, draft_id: int):
    """Hide a draft from the student's view (soft delete)"""
    # Get current user
    user = users[session["auth"]]

    # Get the draft
    target_draft = None

    for draft in drafts():
        if draft.id == draft_id and draft.student_email == user.email:
            target_draft = draft
            break

    if not target_draft:
        return Div(
            P(
                "Draft not found or you don't have permission to hide it.",
                cls="text-red-600 p-3 bg-red-50 rounded",
            )
        )

    # Update the draft to mark it as hidden by student
    if not hasattr(target_draft, "hidden_by_student"):
        # Add the attribute if it doesn't exist
        target_draft.hidden_by_student = True
    else:
        target_draft.hidden_by_student = True
    drafts.update(target_draft)

    # Return a confirmation message that will replace the table row
    return Div(
        Td(
            "Draft hidden",
            colspan="5",
            cls="py-3 px-4 text-gray-500 italic text-center",
        ),
        cls="border-b border-gray-100 bg-gray-50",
    )


@rt("/student/submissions/hidden")
@student_required
def student_submissions_hidden(session, request):
    """Show the student's hidden submissions"""
    # Get current user
    user = users[session["auth"]]

    # Get all student hidden drafts
    hidden_drafts = []
    assignment_info = {}
    course_info = {}

    for draft in drafts():
        if (
            draft.student_email == user.email
            and hasattr(draft, "hidden_by_student")
            and draft.hidden_by_student
        ):
            hidden_drafts.append(draft)

            # Get assignment and course info
            if draft.assignment_id not in assignment_info:
                for a in assignments():
                    if a.id == draft.assignment_id:
                        assignment_info[a.id] = a

                        # Find course for this assignment
                        for c in courses():
                            if c.id == a.course_id:
                                course_info[c.id] = c
                                break
                        break

    # Sort drafts by submission date (newest first)
    hidden_drafts.sort(key=lambda d: d.submission_date, reverse=True)

    # Return the hidden submissions view
    return Div(
        H2("Hidden Submissions", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Show button to go back
        Div(
            Button(
                "← Back to Visible Submissions",
                hx_get="/student/submissions",
                hx_target="#main-content",
                cls="mb-6 bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md",
            ),
            cls="mb-6",
        ),
        # If no hidden submissions
        (
            P(
                "You don't have any hidden submissions.",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center mb-8",
            )
            if not hidden_drafts
            else ""
        ),
        # Hidden submissions table
        (
            Div(
                Table(
                    Thead(
                        Tr(
                            Th(
                                "Assignment",
                                cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                            ),
                            Th(
                                "Draft",
                                cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                            ),
                            Th(
                                "Date",
                                cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                            ),
                            Th(
                                "Status",
                                cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                            ),
                            Th(
                                "Actions",
                                cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100",
                            ),
                        )
                    ),
                    Tbody(
                        *(
                            Tr(
                                # Assignment name
                                Td(
                                    Div(
                                        P(
                                            assignment_info[draft.assignment_id].title,
                                            cls="font-medium text-indigo-700",
                                        ),
                                        P(
                                            f"{course_info[assignment_info[draft.assignment_id].course_id].code}",
                                            cls="text-xs text-gray-500",
                                        ),
                                        cls="",
                                    ),
                                    cls="py-3 px-4",
                                ),
                                # Draft number
                                Td(str(draft.version), cls="py-3 px-4 font-medium"),
                                # Submission date
                                Td(
                                    draft.submission_date.split("T")[0]
                                    if "T" in draft.submission_date
                                    else draft.submission_date,
                                    cls="py-3 px-4 text-gray-600",
                                ),
                                # Status with badge
                                Td(
                                    status_badge(
                                        draft.status.replace("_", " ").capitalize(),
                                        "green"
                                        if draft.status == "feedback_ready"
                                        else "yellow"
                                        if draft.status == "processing"
                                        else "blue",
                                    ),
                                    cls="py-3 px-4",
                                ),
                                # Action buttons
                                Td(
                                    Div(
                                        A(
                                            "View",
                                            href=f"/student/assignments/{draft.assignment_id}#draft-{draft.id}",
                                            cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                                        ),
                                        Button(
                                            "Unhide",
                                            hx_post=f"/student/submissions/unhide/{draft.id}",
                                            hx_target="#main-content",
                                            cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700",
                                        ),
                                        cls="flex",
                                    ),
                                    cls="py-3 px-4",
                                ),
                                cls="border-b border-gray-100 hover:bg-gray-50",
                            )
                            for draft in hidden_drafts
                        )
                    ),
                    cls="w-full",
                ),
                cls="bg-white rounded-lg shadow-md border border-gray-100 overflow-x-auto mb-8",
            )
            if hidden_drafts
            else ""
        ),
    )


@rt("/student/submissions/unhide/{draft_id}")
@student_required
def student_submission_unhide(session, draft_id: int):
    """Unhide a draft previously hidden by the student"""
    # Get current user
    user = users[session["auth"]]

    # Get the draft
    target_draft = None

    for draft in drafts():
        if draft.id == draft_id and draft.student_email == user.email:
            target_draft = draft
            break

    if not target_draft:
        return Div(
            P(
                "Draft not found or you don't have permission to unhide it.",
                cls="text-red-600 p-3 bg-red-50 rounded",
            )
        )

    # Update the draft to mark it as not hidden
    target_draft.hidden_by_student = False
    drafts.update(target_draft)

    # Redirect back to hidden submissions view (which will now show one less item)
    from starlette.responses import RedirectResponse

    return RedirectResponse("/student/submissions/hidden", status_code=303)
