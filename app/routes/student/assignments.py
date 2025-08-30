"""
Student assignment routes
"""

from fasthtml import common as fh
from starlette.responses import FileResponse

from app import rt, student_required
from app.models.assignment import assignments, rubric_categories, rubrics
from app.models.course import courses, enrollments
from app.models.feedback import aggregated_feedback, drafts
from app.models.user import Role, users
from app.utils.ui import (
    action_button,
    card,
    dashboard_layout,
    feedback_card,
    status_badge,
    tabs,
)


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


@rt("/student/assignments/{assignment_id}")
@student_required
def student_assignment_view(session, request, assignment_id: int):
    """Student assignment detail view"""
    # Get current user
    user = users[session["auth"]]

    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return fh.Div(
            fh.P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            fh.A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Get rubric information
    assignment_rubric = None
    rubric_cats = []

    # Find the rubric for this assignment
    for rubric in rubrics():
        if rubric.assignment_id == assignment_id:
            assignment_rubric = rubric
            break

    # Get the rubric categories if the rubric exists
    if assignment_rubric:
        for category in rubric_categories():
            if category.rubric_id == assignment_rubric.id:
                rubric_cats.append(category)

    # Get drafts for this assignment
    assignment_drafts = []

    for draft in drafts():
        if draft.assignment_id == assignment_id and draft.student_email == user.email:
            assignment_drafts.append(draft)

    # Determine if student can submit a new draft
    can_submit = len(assignment_drafts) < assignment.max_drafts

    # Get feedback for drafts
    draft_feedback = {}

    for draft in assignment_drafts:
        draft_feedback[draft.id] = []
        for feedback in aggregated_feedback():
            if feedback.draft_id == draft.id:
                draft_feedback[draft.id].append(feedback)

    # Sort drafts by version
    assignment_drafts.sort(key=lambda d: d.version)

    # Sidebar content
    sidebar_content = fh.Div(
        # Assignment info card
        fh.Div(
            fh.H3("Assignment Details", cls="text-xl font-semibold text-indigo-900 mb-2"),
            fh.P(f"Course: {course.title} ({course.code})", cls="text-gray-600 mb-2"),
            fh.P(f"Due Date: {assignment.due_date}", cls="text-gray-600 mb-2"),
            fh.P(f"Maximum Drafts: {assignment.max_drafts}", cls="text-gray-600 mb-2"),
            fh.P(f"Your Drafts: {len(assignment_drafts)}", cls="text-gray-600 mb-2"),
            fh.P(f"Status: {assignment.status.capitalize()}", cls="text-gray-600 mb-4"),
            fh.Div(
                action_button(
                    "Back to Course",
                    color="gray",
                    href=f"/student/courses/{course.id}",
                    icon="←",
                ),
                action_button(
                    "Submit Draft",
                    color="teal",
                    href=f"/student/assignments/{assignment_id}/submit",
                    disabled=not can_submit,
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Rubric info if available
        (
            fh.Div(
                fh.H3(
                    "Rubric Categories",
                    cls="text-xl font-semibold text-indigo-900 mb-3",
                ),
                fh.Div(
                    *(
                        fh.Div(
                            fh.P(
                                f"{category.name} ({int(category.weight)}%)",
                                cls="font-medium text-indigo-700 mb-1",
                            ),
                            fh.P(category.description, cls="text-sm text-gray-600"),
                            cls="mb-3",
                        )
                        for category in sorted(
                            rubric_cats, key=lambda c: c.weight, reverse=True
                        )
                    )
                ),
                cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
            )
            if rubric_cats
            else ""
        ),
    )

    # Main content
    main_content = fh.Div(
        # Header
        fh.H2(assignment.title, cls="text-2xl font-bold text-indigo-900 mb-2"),
        # Assignment description and specification
        card(
            fh.Div(
                fh.H3(
                    "Assignment Instructions",
                    cls="text-xl font-semibold text-indigo-900 mb-4",
                ),
                fh.P(
                    getattr(assignment, 'instructions', assignment.description), 
                    cls="text-gray-700 whitespace-pre-line mb-4"
                ),
                # Display specification link if available
                (
                    fh.Div(
                        fh.H4(
                            "Assignment Specification",
                            cls="text-lg font-semibold text-indigo-800 mb-2 mt-6",
                        ),
                        fh.Div(
                            fh.A(
                                fh.Span("📄 ", cls="mr-2"),
                                getattr(assignment, 'spec_file_name', 'View Specification'),
                                href=f"/student/assignments/{assignment_id}/spec",
                                target="_blank",
                                cls="inline-flex items-center text-indigo-600 hover:text-indigo-800 font-medium",
                            ),
                            fh.P(
                                "View the detailed assignment specification document",
                                cls="text-sm text-gray-600 mt-1",
                            ),
                            cls="p-3 bg-indigo-50 rounded-lg border border-indigo-200",
                        ),
                    )
                    if hasattr(assignment, 'spec_file_path') and assignment.spec_file_path
                    else ""
                ),
                cls="prose max-w-none",
            )
        ),
        # Draft history and selection
        fh.Div(
            fh.H3("Your Drafts", cls="text-xl font-semibold text-indigo-900 mt-8 mb-4"),
            (
                fh.Div(
                    tabs(
                        [
                            (f"Draft {draft.version}", f"#draft-{draft.id}")
                            for draft in assignment_drafts
                        ],
                        active_index=len(assignment_drafts) - 1,
                    ),
                    # Draft content and feedback
                    *(
                        fh.Div(
                            fh.Div(
                                # Draft info
                                fh.Div(
                                    fh.Div(
                                        fh.H4(
                                            f"Draft {draft.version}",
                                            cls="text-lg font-bold text-indigo-900 mb-2",
                                        ),
                                        fh.P(
                                            f"Submitted: {draft.submission_date}",
                                            cls="text-sm text-gray-500 mb-2",
                                        ),
                                        fh.Div(
                                            status_badge(
                                                draft.status.replace(
                                                    "_", " "
                                                ).capitalize(),
                                                "green"
                                                if draft.status == "feedback_ready"
                                                else "yellow"
                                                if draft.status == "processing"
                                                else "blue",
                                            ),
                                            cls="mb-4",
                                        ),
                                        cls="border-b border-gray-200 pb-4 mb-4",
                                    ),
                                    # Draft content
                                    fh.Div(
                                        fh.H5(
                                            "Your Submission",
                                            cls="text-md font-semibold text-gray-700 mb-2",
                                        ),
                                        (
                                            fh.P(
                                                "For your privacy, the content of this submission has been removed after feedback was generated.",
                                                cls="text-amber-600 italic mb-2 text-sm",
                                            )
                                            if draft.content
                                            == "[Content removed for privacy]"
                                            else ""
                                        ),
                                        (
                                            fh.P(
                                                f"Word count: {getattr(draft, 'word_count', 'N/A')}",
                                                cls="text-gray-500 text-sm mb-2",
                                            )
                                            if hasattr(draft, "word_count")
                                            and draft.word_count
                                            else ""
                                        ),
                                        fh.Pre(
                                            draft.content,
                                            cls="bg-gray-50 p-4 rounded-md text-gray-700 text-sm mb-6 whitespace-pre-wrap border border-gray-200 overflow-auto max-h-60",
                                        ),
                                        cls="mb-6",
                                    ),
                                    # Feedback if available
                                    fh.Div(
                                        fh.H5(
                                            "Feedback",
                                            cls="text-md font-semibold text-gray-700 mb-3",
                                        ),
                                        (
                                            fh.Div(
                                                *(
                                                    fh.Div(
                                                        feedback_card(
                                                            next(
                                                                (
                                                                    c.name
                                                                    for c in rubric_cats
                                                                    if c.id
                                                                    == fb.category_id
                                                                ),
                                                                "General Feedback",
                                                            ),
                                                            fh.Div(
                                                                fh.P(
                                                                    fb.feedback_text,
                                                                    cls="text-gray-700",
                                                                ),
                                                                fh.P(
                                                                    f"Score: {fb.aggregated_score}/100",
                                                                    cls="text-sm text-gray-500 mt-2 font-medium",
                                                                ),
                                                                cls="py-1",
                                                            ),
                                                            color="green"
                                                            if fb.aggregated_score >= 80
                                                            else "yellow"
                                                            if fb.aggregated_score >= 60
                                                            else "red",
                                                        ),
                                                        cls="mb-4",
                                                    )
                                                    for fb in draft_feedback.get(
                                                        draft.id, []
                                                    )
                                                )
                                            )
                                        )
                                        if draft_feedback.get(draft.id)
                                        and draft.status == "feedback_ready"
                                        else fh.Div(
                                            fh.P(
                                                "Feedback is not available yet.",
                                                cls="text-gray-500 italic text-center p-4 bg-gray-50 rounded-md",
                                            )
                                        ),
                                        cls="",
                                    ),
                                ),
                                id=f"draft-{draft.id}",
                                cls="bg-white p-6 rounded-xl shadow-md",
                            )
                        )
                        for draft in assignment_drafts
                    ),
                )
            )
            if assignment_drafts
            else fh.Div(
                fh.P(
                    "You haven't submitted any drafts for this assignment yet.",
                    cls="text-gray-500 italic",
                ),
                fh.Div(
                    fh.A(
                        "Submit Your First Draft",
                        href=f"/student/assignments/{assignment_id}/submit",
                        cls="inline-block bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm mt-4",
                    ),
                    cls="text-center",
                ),
                cls="text-center bg-white p-8 rounded-xl shadow-md mt-4",
            ),
            cls="mb-8",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
            f"Assignment: {assignment.title}",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",  # Keep dashboard highlighted in nav,
    )


@rt("/student/assignments")
@student_required
def student_assignments_list(session, request):
    """Student assignments list view"""
    # Get current user
    user = users[session["auth"]]

    # Get student's enrollments and courses
    student_enrollments = []
    enrolled_courses = {}

    for enrollment in enrollments():
        if enrollment.student_email == user.email:
            student_enrollments.append(enrollment)

    # Get course details for each enrollment
    for enrollment in student_enrollments:
        for course in courses():
            if course.id == enrollment.course_id:
                enrolled_courses[course.id] = course
                break

    # Get all assignments for the enrolled courses
    student_assignments = []

    for assignment in assignments():
        if assignment.course_id in enrolled_courses:
            # Add course info to assignment
            student_assignments.append(
                {
                    "assignment": assignment,
                    "course": enrolled_courses[assignment.course_id],
                }
            )

    # Get student drafts
    student_drafts = {}

    for draft in drafts():
        if draft.student_email == user.email:
            if draft.assignment_id not in student_drafts:
                student_drafts[draft.assignment_id] = []
            student_drafts[draft.assignment_id].append(draft)

    # Sidebar content
    sidebar_content = fh.Div(
        # User welcome card
        fh.Div(
            fh.H3("Assignment Options", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Dashboard", color="gray", href="/student/dashboard", icon="←"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Courses filter
        fh.Div(
            fh.H3("Filter by Course", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                *(
                    fh.Div(
                        fh.A(
                            f"{course.code}: {course.title}",
                            href=f"/student/courses/{course.id}/assignments",
                            cls="text-indigo-700 hover:underline",
                        ),
                        cls="mb-2",
                    )
                    for course in enrolled_courses.values()
                )
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - assignment table
    main_content = fh.Div(
        fh.H2("All Assignments", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Assignments table
        fh.Div(
            fh.Div(
                fh.Table(
                    fh.Thead(
                        fh.Tr(
                            fh.Th(
                                "Assignment",
                                cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            fh.Th(
                                "Course",
                                cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            fh.Th(
                                "Due Date",
                                cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            fh.Th(
                                "Status",
                                cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            fh.Th(
                                "Progress",
                                cls="text-center py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            fh.Th(
                                "Actions",
                                cls="text-center py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                            ),
                            cls="",
                        )
                    ),
                    fh.Tbody(
                        *(
                            fh.Tr(
                                fh.Td(
                                    fh.Div(
                                        fh.H4(
                                            assignment_data["assignment"].title,
                                            cls="font-medium text-indigo-800",
                                        ),
                                        fh.P(
                                            assignment_data["assignment"].description[
                                                :100
                                            ]
                                            + "..."
                                            if len(
                                                assignment_data[
                                                    "assignment"
                                                ].description
                                            )
                                            > 100
                                            else assignment_data[
                                                "assignment"
                                            ].description,
                                            cls="text-sm text-gray-600 mt-1",
                                        ),
                                        cls="",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                fh.Td(
                                    fh.Div(
                                        fh.P(
                                            assignment_data["course"].title,
                                            cls="font-medium text-gray-800",
                                        ),
                                        fh.P(
                                            assignment_data["course"].code,
                                            cls="text-sm text-gray-600",
                                        ),
                                        cls="",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                fh.Td(
                                    fh.P(
                                        assignment_data["assignment"].due_date,
                                        cls="text-gray-700",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                fh.Td(
                                    status_badge(
                                        assignment_data[
                                            "assignment"
                                        ].status.capitalize(),
                                        "green"
                                        if assignment_data["assignment"].status
                                        == "active"
                                        else "yellow"
                                        if assignment_data["assignment"].status
                                        == "closed"
                                        else "gray",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                fh.Td(
                                    fh.Div(
                                        fh.P(
                                            f"{len(student_drafts.get(assignment_data['assignment'].id, []))}/{assignment_data['assignment'].max_drafts}",
                                            cls="font-medium text-indigo-700",
                                        ),
                                        fh.P("Drafts", cls="text-xs text-gray-500"),
                                        cls="text-center",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                fh.Td(
                                    fh.Div(
                                        action_button(
                                            "View",
                                            color="indigo",
                                            href=f"/student/assignments/{assignment_data['assignment'].id}",
                                            size="small",
                                        ),
                                        action_button(
                                            "Submit",
                                            color="teal",
                                            href=f"/student/assignments/{assignment_data['assignment'].id}/submit",
                                            size="small",
                                            disabled=len(
                                                student_drafts.get(
                                                    assignment_data["assignment"].id, []
                                                )
                                            )
                                            >= assignment_data["assignment"].max_drafts
                                            or assignment_data["assignment"].status
                                            != "active",
                                        ),
                                        cls="flex gap-2 justify-center",
                                    ),
                                    cls="py-4 px-6 border-b border-gray-100",
                                ),
                                cls="hover:bg-gray-50",
                            )
                            for assignment_data in sorted(
                                student_assignments,
                                key=lambda a: (
                                    a["assignment"].status != "active",
                                    a["assignment"].due_date,
                                ),
                                reverse=False,
                            )
                        )
                        if student_assignments
                        else [
                            fh.Tr(
                                fh.Td(
                                    fh.P(
                                        "No assignments found.",
                                        cls="text-gray-500 italic text-center",
                                    ),
                                    colspan="6",
                                    cls="py-8 px-6 text-center",
                                )
                            )
                        ]
                    ),
                    cls="min-w-full divide-y divide-gray-200",
                ),
                cls="overflow-x-auto bg-white rounded-xl shadow-md border border-gray-100",
            ),
            cls="",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
            "All Assignments",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard"
    )


@rt("/student/assignments/{assignment_id}/spec")
@student_required
def student_assignment_spec_view(session, assignment_id: int):
    """Serve assignment specification file to students"""
    # Get current user
    user = users[session["auth"]]
    
    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return fh.Div(
            fh.P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            fh.A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )
    
    # Check if specification exists
    if not hasattr(assignment, 'spec_file_path') or not assignment.spec_file_path:
        return fh.Div(
            fh.P("No specification file available for this assignment.", 
                 cls="text-amber-600 bg-amber-50 p-4 rounded-lg"),
            fh.A(
                "Back to Assignment",
                href=f"/student/assignments/{assignment_id}",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )
    
    # Serve the file
    from pathlib import Path
    file_path = Path("data/assignment_specs") / assignment.spec_file_path
    
    if not file_path.exists():
        return fh.Div(
            fh.P("Specification file not found.", 
                 cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            fh.A(
                "Back to Assignment",
                href=f"/student/assignments/{assignment_id}",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )
    
    # Return file response
    return FileResponse(
        path=str(file_path),
        filename=getattr(assignment, 'spec_file_name', 'assignment_specification.pdf'),
        media_type='application/octet-stream'
    )
