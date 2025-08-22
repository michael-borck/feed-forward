"""
Instructor dashboard routes
"""

from fasthtml.common import *

from app import instructor_required, rt
from app.models.assignment import assignments
from app.models.course import courses, enrollments
from app.models.feedback import drafts
from app.models.user import users
from app.utils.ui import action_button, card, dashboard_layout, status_badge


@rt("/instructor/dashboard")
@instructor_required
def instructor_dashboard(session, request):
    """Main instructor dashboard view"""
    # Get current instructor
    instructor = users[session["auth"]]

    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == instructor.email:
            instructor_courses.append(course)

    # Get enrollment counts
    course_enrollments = {}
    for course in instructor_courses:
        enrollment_count = sum(1 for e in enrollments() if e.course_id == course.id)
        course_enrollments[course.id] = enrollment_count

    # Get assignment counts
    course_assignments = {}
    for course in instructor_courses:
        assignment_count = sum(1 for a in assignments() if a.course_id == course.id)
        course_assignments[course.id] = assignment_count

    # Get recent submissions
    recent_submissions = []
    for draft in sorted(drafts(), key=lambda d: d.submission_date, reverse=True)[:10]:
        # Check if this draft is for one of instructor's assignments
        for assignment in assignments():
            if draft.assignment_id == assignment.id:
                for course in instructor_courses:
                    if assignment.course_id == course.id:
                        recent_submissions.append(
                            {"draft": draft, "assignment": assignment, "course": course}
                        )
                        break
                break

    # Sidebar content
    sidebar_content = Div(
        # Welcome card
        Div(
            H3(
                f"Welcome, {instructor.name or instructor.email}",
                cls="text-xl font-semibold text-indigo-900 mb-2",
            ),
            P("Instructor Dashboard", cls="text-gray-600 mb-4"),
            Div(
                action_button(
                    "Manage Courses", color="indigo", href="/instructor/courses"
                ),
                action_button("AI Models", color="teal", href="/instructor/models"),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Quick stats
        Div(
            H3("Quick Stats", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Active Courses: {len(instructor_courses)}", cls="text-gray-600 mb-2"),
            P(
                f"Total Students: {sum(course_enrollments.values())}",
                cls="text-gray-600 mb-2",
            ),
            P(
                f"Total Assignments: {sum(course_assignments.values())}",
                cls="text-gray-600",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = Div(
        # Stats overview
        Div(
            card(
                Div(
                    H3(
                        str(len(instructor_courses)),
                        cls="text-4xl font-bold text-indigo-700 mb-2",
                    ),
                    P("Active Courses", cls="text-gray-600"),
                    cls="text-center p-4",
                ),
                padding=0,
            ),
            card(
                Div(
                    H3(
                        str(sum(course_enrollments.values())),
                        cls="text-4xl font-bold text-teal-700 mb-2",
                    ),
                    P("Total Students", cls="text-gray-600"),
                    cls="text-center p-4",
                ),
                padding=0,
            ),
            card(
                Div(
                    H3(
                        str(sum(course_assignments.values())),
                        cls="text-4xl font-bold text-indigo-700 mb-2",
                    ),
                    P("Total Assignments", cls="text-gray-600"),
                    cls="text-center p-4",
                ),
                padding=0,
            ),
            cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
        ),
        # Courses section
        Div(
            Div(
                H2("Your Courses", cls="text-2xl font-bold text-indigo-900"),
                A(
                    "Manage Courses",
                    href="/instructor/courses",
                    cls="text-indigo-600 hover:underline text-sm",
                ),
                cls="flex justify-between items-center mb-6",
            ),
            Div(
                *(
                    Div(
                        H3(course.title, cls="text-xl font-bold text-indigo-800 mb-1"),
                        P(f"Code: {course.code}", cls="text-gray-600 mb-1"),
                        Div(
                            Span(
                                f"{course_enrollments.get(course.id, 0)} students",
                                cls="text-sm text-gray-500 mr-4",
                            ),
                            Span(
                                f"{course_assignments.get(course.id, 0)} assignments",
                                cls="text-sm text-gray-500",
                            ),
                            cls="mb-3",
                        ),
                        Div(
                            action_button(
                                "View Details",
                                color="indigo",
                                href=f"/instructor/courses/{course.id}",
                                size="small",
                            ),
                            action_button(
                                "Assignments",
                                color="teal",
                                href=f"/instructor/courses/{course.id}/assignments",
                                size="small",
                            ),
                            cls="flex gap-3",
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                    )
                    for course in instructor_courses[:3]  # Show first 3 courses
                )
            )
            if instructor_courses
            else P(
                "No courses yet. Create your first course!",
                cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center",
            ),
            cls="mb-8",
        ),
        # Recent submissions section
        Div(
            H2("Recent Submissions", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                *(
                    Div(
                        Div(
                            P(
                                f"Student submitted draft for {sub['assignment'].title}",
                                cls="text-indigo-800 font-medium",
                            ),
                            P(
                                f"Course: {sub['course'].title}",
                                cls="text-sm text-gray-500",
                            ),
                            P(
                                f"Status: {sub['draft'].status.replace('_', ' ').capitalize()}",
                                cls="text-sm text-gray-600 mt-1",
                            ),
                            cls="flex-1",
                        ),
                        status_badge(
                            sub["draft"].status.replace("_", " ").capitalize(),
                            "green"
                            if sub["draft"].status == "feedback_ready"
                            else "yellow"
                            if sub["draft"].status == "processing"
                            else "blue",
                        ),
                        cls="flex justify-between items-start p-4 border-l-4 border-indigo-500 bg-white rounded-r-lg shadow-sm mb-3",
                    )
                    for sub in recent_submissions[:5]
                )
            )
            if recent_submissions
            else P(
                "No recent submissions",
                cls="text-gray-500 italic p-4 bg-white rounded-xl border border-gray-200",
            ),
        ),
    )

    return Titled(
        "Instructor Dashboard | FeedForward",
        dashboard_layout(
            "Instructor Dashboard",
            sidebar_content,
            main_content,
            user_role="instructor",
            current_path="/instructor/dashboard",
        ),
    )
