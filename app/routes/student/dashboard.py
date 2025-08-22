"""
Student dashboard routes
"""

from fasthtml import common as fh

from app import rt, student_required
from app.models.assignment import assignments
from app.models.course import courses, enrollments
from app.models.feedback import drafts
from app.models.user import Role, users
from app.utils.ui import (
    action_button,
    card,
    dashboard_layout,
    feedback_card,
    status_badge,
)


def generate_recent_feedback(student_drafts):
    """Generate the recent feedback section for student dashboard"""
    # Filter out hidden drafts
    visible_drafts = [
        draft
        for draft in student_drafts
        if not (hasattr(draft, "hidden_by_student") and draft.hidden_by_student)
    ]

    # Main content
    if not visible_drafts:
        return fh.Div(
            fh.H2("Recent Feedback", cls="text-2xl font-bold text-indigo-900 mb-6"),
            fh.P(
                "No recent feedback.",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center",
            ),
            cls="mb-8",
        )

    # Sort drafts by submission date, get 2 most recent
    recent_drafts = sorted(
        visible_drafts, key=lambda d: d.submission_date, reverse=True
    )[:2]

    # Create feedback cards
    feedback_items = []
    for draft in recent_drafts:
        feedback_items.append(
            fh.Div(
                feedback_card(
                    f"Feedback on Assignment {draft.assignment_id} - Draft {draft.version}",
                    fh.Div(
                        fh.P(
                            "No feedback available yet. Your submission is being processed.",
                            cls="text-gray-600 italic",
                        ),
                        cls="py-2",
                    ),
                    color="teal",
                )
            )
        )

    return fh.Div(
        fh.H2("Recent Feedback", cls="text-2xl font-bold text-indigo-900 mb-6"),
        fh.Div(*feedback_items),
        cls="mb-8",
    )


def generate_assignments_sidebar(student_assignments, student_drafts):
    """Generate the assignments sidebar component for student dashboard"""
    if not student_assignments:
        return fh.Div(
            fh.H3("Active Assignments", cls="font-semibold text-indigo-900 mb-4"),
            fh.P("No active assignments.", cls="text-gray-500 italic text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )

    # Filter out hidden drafts when counting
    [
        d
        for d in student_drafts
        if not (hasattr(d, "hidden_by_student") and d.hidden_by_student)
    ]

    # Create assignment items
    assignment_items = []
    for assignment_data in student_assignments[:3]:  # Show only 3 most recent
        assignment_items.append(
            fh.Div(
                fh.Div(
                    fh.Div(
                        fh.Div(
                            fh.H4(
                                assignment_data["assignment"].title,
                                cls="font-medium text-indigo-700",
                            ),
                            fh.P(
                                f"{assignment_data['course'].code}: {assignment_data['course'].title}",
                                cls="text-xs text-gray-500",
                            ),
                            cls="flex-1",
                        ),
                        fh.Div(
                            # Calculate draft count for this assignment (both visible and hidden)
                            status_badge(
                                f"Draft {sum(1 for d in student_drafts if d.assignment_id == assignment_data['assignment'].id)}/{assignment_data['assignment'].max_drafts}",
                                "blue",
                            ),
                            cls="",
                        ),
                        cls="flex justify-between items-start",
                    ),
                    fh.P(
                        f"Due: {assignment_data['assignment'].due_date}",
                        cls="text-xs text-gray-500 mt-1",
                    ),
                    cls="p-3",
                ),
                cls="bg-white border border-gray-200 rounded-md mb-2 hover:border-indigo-300 transition-colors",
            )
        )

    # Create the full sidebar component
    return fh.Div(
        fh.H3("Active Assignments", cls="font-semibold text-indigo-900 mb-4"),
        fh.Div(*assignment_items),
        fh.A(
            "View All Assignments",
            href="/student/assignments",
            cls="text-sm text-indigo-600 hover:underline block mt-2",
        ),
        cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
    )


@rt("/student/dashboard")
@student_required
def student_dashboard(session, request):
    """Student dashboard view"""
    # Get current user
    user = users[session["auth"]]

    # Get student's enrollments and courses
    student_enrollments = []
    for enrollment in enrollments():
        if enrollment.student_email == user.email:
            student_enrollments.append(enrollment)

    # Get course details for each enrollment
    enrolled_courses = []
    for enrollment in student_enrollments:
        for course in courses():
            if course.id == enrollment.course_id:
                enrolled_courses.append(course)
                break

    # Get all assignments for the enrolled courses
    student_assignments = []

    for course in enrolled_courses:
        for assignment in assignments():
            if assignment.course_id == course.id and assignment.status == "active":
                # Add course info to assignment
                assignment_with_course = {"assignment": assignment, "course": course}
                student_assignments.append(assignment_with_course)

    # Get student drafts
    student_drafts = []

    for draft in drafts():
        if draft.student_email == user.email:
            student_drafts.append(draft)

    # Count pending assignments (active assignments where max drafts > current draft count)
    pending_assignments = 0
    for assignment_data in student_assignments:
        assignment = assignment_data["assignment"]
        draft_count = sum(1 for d in student_drafts if d.assignment_id == assignment.id)
        if draft_count < assignment.max_drafts:
            pending_assignments += 1

    # Create each part of the sidebar separately
    welcome_card = fh.Div(
        fh.H3("Welcome, " + user.name, cls="text-xl font-semibold text-indigo-900 mb-2"),
        fh.P("Student Account", cls="text-gray-600 mb-4"),
        fh.Div(
            # Active assignments summary
            fh.Div(
                fh.Div(str(len(enrolled_courses)), cls="text-indigo-700 font-bold"),
                fh.P("Enrolled Courses", cls="text-gray-600"),
                cls="flex items-center space-x-2 mb-2",
            ),
            # Pending assignments summary
            fh.Div(
                fh.Div(str(pending_assignments), cls="text-indigo-700 font-bold"),
                fh.P("Pending Assignments", cls="text-gray-600"),
                cls="flex items-center space-x-2",
            ),
            cls="space-y-2",
        ),
        cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
    )

    # Active courses section
    courses_card = fh.Div(
        fh.H3("Your Courses", cls="font-semibold text-indigo-900 mb-4"),
        fh.Div(
            *(
                fh.Div(
                    fh.A(
                        course.title,
                        href=f"/student/courses/{course.id}",
                        cls="font-medium text-indigo-700 hover:underline",
                    ),
                    cls="mb-2",
                )
                for course in enrolled_courses
            )
        )
        if enrolled_courses
        else fh.P(
            "You are not enrolled in any courses yet.",
            cls="text-gray-500 italic text-sm",
        ),
        cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
    )

    # Assignments section from helper function
    assignments_card = generate_assignments_sidebar(student_assignments, student_drafts)

    # Combine all sidebar components
    sidebar_content = fh.Div(welcome_card, courses_card, assignments_card)

    # Main content
    main_content = fh.Div(
        # Progress summary
        fh.Div(
            fh.Div(
                # Courses card
                card(
                    fh.Div(
                        fh.H3(
                            str(len(enrolled_courses)),
                            cls="text-4xl font-bold text-indigo-700 mb-2",
                        ),
                        fh.P("Enrolled Courses", cls="text-gray-600"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Active assignments card
                card(
                    fh.Div(
                        fh.H3(
                            str(len(student_assignments)),
                            cls="text-4xl font-bold text-teal-700 mb-2",
                        ),
                        fh.P("Active Assignments", cls="text-gray-600"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Completed drafts card
                card(
                    fh.Div(
                        fh.H3(
                            str(len(student_drafts)),
                            cls="text-4xl font-bold text-indigo-700 mb-2",
                        ),
                        fh.P("Submitted Drafts", cls="text-gray-600"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
            )
        ),
        # Courses section
        fh.Div(
            fh.H2("Your Courses", cls="text-2xl font-bold text-indigo-900 mb-6"),
            (
                fh.Div(
                    *(
                        fh.Div(
                            fh.Div(
                                fh.H3(
                                    course.title,
                                    cls="text-xl font-bold text-indigo-800 mb-1",
                                ),
                                fh.P(f"Code: {course.code}", cls="text-gray-600 mb-1"),
                                fh.P(
                                    f"Term: {getattr(course, 'term', 'Current')}",
                                    cls="text-gray-600 mb-1",
                                ),
                                fh.Div(
                                    fh.Span(
                                        getattr(
                                            course, "status", "active"
                                        ).capitalize(),
                                        cls="px-3 py-1 rounded-full text-sm "
                                        + (
                                            "bg-green-100 text-green-800"
                                            if getattr(course, "status", "active")
                                            == "active"
                                            else "bg-gray-100 text-gray-800"
                                        ),
                                    ),
                                    cls="mt-2",
                                ),
                                cls="flex-1",
                            ),
                            fh.Div(
                                fh.Div(
                                    action_button(
                                        "View Course",
                                        color="indigo",
                                        href=f"/student/courses/{course.id}",
                                        size="small",
                                    ),
                                    action_button(
                                        "Assignments",
                                        color="teal",
                                        href=f"/student/courses/{course.id}/assignments",
                                        size="small",
                                    ),
                                    cls="space-y-2",
                                ),
                                cls="ml-auto",
                            ),
                            cls="flex justify-between items-start bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                        )
                        for course in enrolled_courses
                    )
                )
            )
            if enrolled_courses
            else fh.P(
                "You are not enrolled in any courses yet.",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center",
            ),
            cls="mb-8",
        ),
        # Upcoming assignments section
        fh.Div(
            fh.H2("Upcoming Assignments", cls="text-2xl font-bold text-indigo-900 mb-6"),
            fh.Div(
                *(
                    fh.Div(
                        fh.Div(
                            fh.Div(
                                fh.H3(
                                    assignment_data["assignment"].title,
                                    cls="text-xl font-bold text-indigo-800 mb-1",
                                ),
                                fh.P(
                                    f"Course: {assignment_data['course'].title} ({assignment_data['course'].code})",
                                    cls="text-gray-600 mb-1",
                                ),
                                fh.P(
                                    f"Due: {assignment_data['assignment'].due_date}",
                                    cls="text-gray-600 mb-2",
                                ),
                                # Calculate current drafts
                                fh.Div(
                                    fh.P(
                                        f"Drafts: {sum(1 for d in student_drafts if d.assignment_id == assignment_data['assignment'].id)}/{assignment_data['assignment'].max_drafts}",
                                        cls="text-sm text-gray-600",
                                    ),
                                    cls="mb-3",
                                ),
                                cls="flex-1",
                            ),
                            fh.Div(
                                action_button(
                                    "View Assignment",
                                    color="indigo",
                                    href=f"/student/assignments/{assignment_data['assignment'].id}",
                                    size="small",
                                ),
                                action_button(
                                    "Submit Draft",
                                    color="teal",
                                    href=f"/student/assignments/{assignment_data['assignment'].id}/submit",
                                    size="small",
                                ),
                                cls="space-y-2",
                            ),
                            cls="flex flex-col md:flex-row md:justify-between items-start md:items-center gap-4",
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                    )
                    for assignment_data in student_assignments
                )
            )
            if student_assignments
            else fh.P(
                "No upcoming assignments.",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center",
            ),
            cls="mb-8",
        ),
        # Recent feedback section using helper function
        generate_recent_feedback(student_drafts),
    )

    # Use the dashboard layout with our components
    return fh.Titled(
        "Student Dashboard | FeedForward",
        dashboard_layout(
            "Student Dashboard",
            sidebar_content,
            main_content,
            user_role=Role.STUDENT,
            current_path="/student/dashboard",
        ),
    )
