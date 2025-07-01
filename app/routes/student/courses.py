"""
Student course routes
"""

from fasthtml.common import *

from app import rt, student_required
from app.models.assignment import assignments
from app.models.course import courses, enrollments
from app.models.feedback import drafts
from app.models.user import Role, users
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


@rt("/student/courses/{course_id}")
@student_required
def student_course_view(session, request, course_id: int):
    """Student course detail view"""
    # Get current user
    user = users[session["auth"]]

    # Verify course and enrollment
    course, error = get_student_course(course_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Get assignments for this course
    course_assignments = []

    for assignment in assignments():
        if assignment.course_id == course_id and assignment.status == "active":
            course_assignments.append(assignment)

    # Get student drafts for these assignments
    student_drafts = []

    for draft in drafts():
        if draft.student_email == user.email:
            for assignment in course_assignments:
                if draft.assignment_id == assignment.id:
                    student_drafts.append(draft)

    # Sidebar content
    sidebar_content = Div(
        # Course info card
        Div(
            H3(course.title, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course Code: {course.code}", cls="text-gray-600 mb-1"),
            P(f"Term: {getattr(course, 'term', 'Current')}", cls="text-gray-600 mb-1"),
            P(
                f"Status: {getattr(course, 'status', 'active').capitalize()}",
                cls="text-gray-600 mb-4",
            ),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/student/dashboard",
                    icon="←",
                ),
                action_button(
                    "View Assignments",
                    color="indigo",
                    href=f"/student/courses/{course_id}/assignments",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Course stats
        Div(
            H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Assignments: {len(course_assignments)}", cls="text-gray-600 mb-2"),
            P(f"Submitted Drafts: {len(student_drafts)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = Div(
        H2(f"Course: {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Assignments section
        Div(
            H3("Active Assignments", cls="text-xl font-bold text-indigo-900 mb-4"),
            (
                Div(
                    *(
                        Div(
                            Div(
                                Div(
                                    H4(
                                        assignment.title,
                                        cls="text-lg font-semibold text-indigo-800 mb-1",
                                    ),
                                    P(
                                        f"Due: {assignment.due_date}",
                                        cls="text-gray-600 mb-2",
                                    ),
                                    Div(
                                        P(
                                            f"Drafts: {sum(1 for d in student_drafts if d.assignment_id == assignment.id)}/{assignment.max_drafts}",
                                            cls="text-sm text-gray-600 mb-1",
                                        ),
                                        # Get the last draft status if exists
                                        Div(
                                            status_badge(
                                                next(
                                                    (
                                                        d.status.capitalize()
                                                        for d in sorted(
                                                            [
                                                                d
                                                                for d in student_drafts
                                                                if d.assignment_id
                                                                == assignment.id
                                                            ],
                                                            key=lambda x: x.version,
                                                            reverse=True,
                                                        )
                                                    ),
                                                    "Not Started",
                                                ),
                                                "green"
                                                if any(
                                                    d.status == "feedback_ready"
                                                    for d in student_drafts
                                                    if d.assignment_id == assignment.id
                                                )
                                                else "yellow"
                                                if any(
                                                    d.status == "processing"
                                                    for d in student_drafts
                                                    if d.assignment_id == assignment.id
                                                )
                                                else "blue"
                                                if any(
                                                    d.status == "submitted"
                                                    for d in student_drafts
                                                    if d.assignment_id == assignment.id
                                                )
                                                else "gray",
                                            ),
                                            cls="mt-1",
                                        ),
                                        cls="",
                                    ),
                                    cls="flex-1",
                                ),
                                Div(
                                    action_button(
                                        "View Assignment",
                                        color="indigo",
                                        href=f"/student/assignments/{assignment.id}",
                                        size="small",
                                    ),
                                    action_button(
                                        "Submit Draft",
                                        color="teal",
                                        href=f"/student/assignments/{assignment.id}/submit",
                                        size="small",
                                    ),
                                    cls="flex flex-col gap-3",
                                ),
                                cls="flex flex-col md:flex-row justify-between",
                            ),
                            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4 hover:shadow-lg transition-shadow",
                        )
                        for assignment in course_assignments
                    )
                )
            )
            if course_assignments
            else P(
                "No active assignments in this course.",
                cls="text-gray-500 italic p-4 bg-white rounded-xl border border-gray-200",
            ),
            cls="mb-8",
        ),
        # Recent activity for this course
        Div(
            H3("Recent Activity", cls="text-xl font-bold text-indigo-900 mb-4"),
            (
                Div(
                    *(
                        Div(
                            Div(
                                P(
                                    f"Draft {draft.version} submitted for "
                                    + next(
                                        (
                                            a.title
                                            for a in course_assignments
                                            if a.id == draft.assignment_id
                                        ),
                                        "Assignment",
                                    ),
                                    cls="text-indigo-800 font-medium",
                                ),
                                P(
                                    f"Submission Date: {draft.submission_date}",
                                    cls="text-sm text-gray-500",
                                ),
                                P(
                                    f"Status: {draft.status.replace('_', ' ').capitalize()}",
                                    cls="text-sm text-gray-600 mt-1",
                                ),
                                cls="p-4 border-l-4 border-indigo-500 bg-white rounded-r-lg shadow-sm mb-3",
                            )
                        )
                        for draft in sorted(
                            student_drafts,
                            key=lambda d: d.submission_date,
                            reverse=True,
                        )[:5]
                    )
                )
            )
            if student_drafts
            else P(
                "No activity recorded for this course yet.",
                cls="text-gray-500 italic p-4 bg-white rounded-xl border border-gray-200",
            ),
            cls="mb-6",
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        f"{course.title} | FeedForward",
        dashboard_layout(
            f"Course: {course.title}",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",  # Keep dashboard highlighted in nav
        ),
    )


@rt("/student/courses/{course_id}/assignments")
@student_required
def student_course_assignments(session, request, course_id: int):
    """Student course assignments list view"""
    # Get current user
    user = users[session["auth"]]

    # Verify course and enrollment
    course, error = get_student_course(course_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A(
                "Return to Dashboard",
                href="/student/dashboard",
                cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg",
            ),
        )

    # Get assignments for this course
    course_assignments = []

    for assignment in assignments():
        if assignment.course_id == course_id:
            # Include all assignments, not just active ones
            course_assignments.append(assignment)

    # Get student drafts for these assignments
    student_drafts = {}

    for draft in drafts():
        if draft.student_email == user.email:
            for assignment in course_assignments:
                if draft.assignment_id == assignment.id:
                    if assignment.id not in student_drafts:
                        student_drafts[assignment.id] = []
                    student_drafts[assignment.id].append(draft)

    # Sidebar content
    sidebar_content = Div(
        # Course info card
        Div(
            H3(course.title, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course Code: {course.code}", cls="text-gray-600 mb-1"),
            P(f"Term: {getattr(course, 'term', 'Current')}", cls="text-gray-600 mb-1"),
            P(
                f"Status: {getattr(course, 'status', 'active').capitalize()}",
                cls="text-gray-600 mb-4",
            ),
            Div(
                action_button(
                    "Back to Course",
                    color="gray",
                    href=f"/student/courses/{course_id}",
                    icon="←",
                ),
                action_button("Dashboard", color="indigo", href="/student/dashboard"),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Assignment status summary
        Div(
            H3("Assignment Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                Div(
                    Div(
                        str(sum(1 for a in course_assignments if a.status == "active")),
                        cls="text-indigo-700 font-bold",
                    ),
                    P("Active", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2",
                ),
                Div(
                    Div(
                        str(sum(1 for a in course_assignments if a.status == "closed")),
                        cls="text-yellow-700 font-bold",
                    ),
                    P("Closed", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2",
                ),
                Div(
                    Div(
                        str(
                            sum(
                                1
                                for a in course_assignments
                                if a.status in ["archived", "deleted"]
                            )
                        ),
                        cls="text-gray-700 font-bold",
                    ),
                    P("Archived", cls="text-gray-600"),
                    cls="flex items-center space-x-2",
                ),
                cls="space-y-2",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = Div(
        H2(
            f"Assignments for {course.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        # Filter controls (to be implemented later)
        Div(
            Div(
                # Status filter
                Div(
                    A(
                        "All",
                        href="#",
                        cls="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md",
                    ),
                    A(
                        "Active",
                        href="#",
                        cls="inline-block px-4 py-2 bg-gray-200 rounded-md ml-2",
                    ),
                    A(
                        "Completed",
                        href="#",
                        cls="inline-block px-4 py-2 bg-gray-200 rounded-md ml-2",
                    ),
                    cls="mb-4 md:mb-0",
                ),
                # Sort options (to be implemented later)
                Div(
                    Select(
                        Option(
                            "Sort by Due Date (newest)",
                            value="due_date_desc",
                            selected=True,
                        ),
                        Option("Sort by Due Date (oldest)", value="due_date_asc"),
                        Option("Sort by Title (A-Z)", value="title_asc"),
                        cls="border border-gray-300 rounded-md px-3 py-2",
                    ),
                    cls="",
                ),
                cls="flex flex-col md:flex-row md:justify-between mb-6",
            ),
            cls="bg-gray-50 p-4 rounded-lg mb-6",
        ),
        # Assignments list
        Div(
            *(
                Div(
                    Div(
                        # Assignment title and status
                        Div(
                            Div(
                                H3(
                                    assignment.title,
                                    cls="text-xl font-bold text-indigo-800 mb-1",
                                ),
                                P(
                                    f"Due: {assignment.due_date}",
                                    cls="text-gray-600 mb-2",
                                ),
                                status_badge(
                                    assignment.status.capitalize(),
                                    "green"
                                    if assignment.status == "active"
                                    else "yellow"
                                    if assignment.status == "closed"
                                    else "gray",
                                ),
                                cls="flex-1",
                            ),
                            # Draft status
                            Div(
                                P(
                                    f"Drafts: {len(student_drafts.get(assignment.id, []))}/{assignment.max_drafts}",
                                    cls="text-sm text-gray-600 mb-2",
                                ),
                                # Display the latest draft status if exists
                                Div(
                                    status_badge(
                                        "Feedback Ready"
                                        if any(
                                            d.status == "feedback_ready"
                                            for d in student_drafts.get(
                                                assignment.id, []
                                            )
                                        )
                                        else "Processing"
                                        if any(
                                            d.status == "processing"
                                            for d in student_drafts.get(
                                                assignment.id, []
                                            )
                                        )
                                        else "Submitted"
                                        if student_drafts.get(assignment.id, [])
                                        else "Not Started",
                                        "green"
                                        if any(
                                            d.status == "feedback_ready"
                                            for d in student_drafts.get(
                                                assignment.id, []
                                            )
                                        )
                                        else "yellow"
                                        if any(
                                            d.status == "processing"
                                            for d in student_drafts.get(
                                                assignment.id, []
                                            )
                                        )
                                        else "blue"
                                        if student_drafts.get(assignment.id, [])
                                        else "gray",
                                    ),
                                    cls="",
                                ),
                                cls="md:text-right",
                            ),
                            cls="flex flex-col md:flex-row justify-between mb-4",
                        ),
                        # Description and actions
                        Div(
                            Div(
                                P(
                                    assignment.description[:150] + "..."
                                    if len(assignment.description) > 150
                                    else assignment.description,
                                    cls="text-gray-600 mb-4",
                                ),
                                cls="flex-1",
                            ),
                            Div(
                                Div(
                                    action_button(
                                        "View Assignment",
                                        color="indigo",
                                        href=f"/student/assignments/{assignment.id}",
                                        size="small",
                                    ),
                                    action_button(
                                        "Submit Draft",
                                        color="teal",
                                        href=f"/student/assignments/{assignment.id}/submit",
                                        size="small",
                                        # Only show submit button if max drafts not reached and assignment active
                                        disabled=len(
                                            student_drafts.get(assignment.id, [])
                                        )
                                        >= assignment.max_drafts
                                        or assignment.status != "active",
                                    ),
                                    cls="flex flex-col gap-2",
                                ),
                                cls="",
                            ),
                            cls="flex flex-col md:flex-row justify-between",
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6 hover:shadow-lg transition-shadow",
                    )
                )
                for assignment in sorted(
                    course_assignments,
                    key=lambda a: (a.status != "active", a.due_date),
                    reverse=False,
                )
            )
            if course_assignments
            else P(
                "No assignments found for this course.",
                cls="text-gray-500 italic p-6 bg-white rounded-xl border border-gray-200 text-center",
            )
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        f"Assignments - {course.title} | FeedForward",
        dashboard_layout(
            f"Assignments - {course.title}",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",  # Keep dashboard active in nav
        ),
    )
