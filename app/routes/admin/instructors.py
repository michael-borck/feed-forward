"""
Admin instructor management routes
"""

from fasthtml.common import *
from starlette.responses import RedirectResponse

from app import admin_required, rt
from app.models.course import courses, enrollments
from app.models.user import Role, users
from app.utils.ui import action_button, dashboard_layout


@rt("/admin/instructors/approve")
@admin_required
def admin_instructors_approve_list(session):
    """Admin instructor approval list view"""
    # Get current user and UI components
    user = users[session["auth"]]

    # Get all instructors that need approval
    pending_instructors = []
    for instructor in users():
        if instructor.role == Role.INSTRUCTOR and not instructor.approved:
            pending_instructors.append(instructor)

    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/admin/dashboard", icon="←"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Admin actions
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Manage Users", color="teal", href="/admin/users", icon="👥"
                ),
                action_button(
                    "System Settings", color="indigo", href="/admin/settings", icon="⚙️"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Instructor approval list
    main_content = Div(
        H1("Approve Instructors", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P("Review and approve instructor account requests.", cls="text-gray-600 mb-8"),
        # Instructor approval table
        Div(
            Div(
                H2("Pending Approval", cls="text-2xl font-bold text-indigo-900 mb-4"),
                # Check if there are pending instructors
                (
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    Th(
                                        "Name",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Email",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Department",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Actions",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                ),
                                cls="bg-indigo-50",
                            ),
                            Tbody(
                                *(
                                    Tr(
                                        Td(instructor.name, cls="py-4 px-6"),
                                        Td(instructor.email, cls="py-4 px-6"),
                                        Td(
                                            instructor.department or "Not specified",
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Div(
                                                Button(
                                                    "Approve",
                                                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                                    hx_post=f"/admin/instructors/approve/{instructor.email}",
                                                    hx_swap="outerHTML",
                                                ),
                                                Button(
                                                    "Reject",
                                                    cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                    hx_post=f"/admin/instructors/reject/{instructor.email}",
                                                    hx_swap="outerHTML",
                                                ),
                                                cls="flex",
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                    )
                                    for instructor in pending_instructors
                                )
                            ),
                            cls="w-full",
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                    )
                )
                if pending_instructors
                else Div(
                    P(
                        "No pending instructor approvals at this time.",
                        cls="text-gray-500 italic text-center py-8",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
                ),
                Div(cls="mb-8"),
            )
        ),
        # Back button
        Div(
            action_button(
                "Back to Dashboard", color="gray", href="/admin/dashboard", icon="←"
            ),
            cls="mt-4",
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Approve Instructors | FeedForward",
        dashboard_layout(
            "Approve Instructors", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


@rt("/admin/instructors/approve/{email}")
@admin_required
def admin_instructor_approve(session, email: str):
    """Approve instructor POST handler"""
    try:
        # Get the instructor
        instructor = users[email]

        # Update approval status
        instructor.approved = True
        users.update(instructor)

        # Return success message with auto-refresh
        return Div(
            P("Approved successfully", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
            cls="py-2 px-4",
        )
    except:
        # Return error message
        return Div(P("Error approving instructor", cls="text-red-500"), cls="py-2 px-4")


@rt("/admin/instructors/reject/{email}")
@admin_required
def admin_instructor_reject(session, email: str):
    """Reject instructor POST handler"""
    try:
        # Get the instructor and delete
        users.delete(email)

        # Return success message with auto-refresh
        return Div(
            P("Rejected and removed", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
            cls="py-2 px-4",
        )
    except:
        # Return error message
        return Div(P("Error rejecting instructor", cls="text-red-500"), cls="py-2 px-4")


@rt("/admin/instructors")
@admin_required
def admin_instructors_list(session):
    """Admin instructors management list view"""
    # Get current user
    user = users[session["auth"]]

    # Get all instructors who aren't deleted
    instructor_list = []
    for u in users():
        if u.role == Role.INSTRUCTOR and (
            not hasattr(u, "status") or u.status != "deleted"
        ):
            instructor_list.append(u)

    # Count courses per instructor
    instructor_courses = {}
    instructor_enrollments = {}

    for course in courses():
        if course.instructor_email not in instructor_courses:
            instructor_courses[course.instructor_email] = 0
        instructor_courses[course.instructor_email] += 1

    for enrollment in enrollments():
        # Get course instructor
        for course in courses():
            if course.id == enrollment.course_id:
                if course.instructor_email not in instructor_enrollments:
                    instructor_enrollments[course.instructor_email] = 0
                instructor_enrollments[course.instructor_email] += 1
                break

    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/admin/dashboard", icon="←"
                ),
                action_button(
                    "Approve Instructors",
                    color="indigo",
                    href="/admin/instructors/approve",
                    icon="✓",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Filter options
        Div(
            H3("Filter Options", cls="font-semibold text-indigo-900 mb-4"),
            P("All active instructors", cls="text-gray-600 text-sm"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Instructor management
    main_content = Div(
        H1("Manage Instructors", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P(
            "View and manage instructor accounts in the system.",
            cls="text-gray-600 mb-8",
        ),
        # Instructors table
        Div(
            Div(
                H2("Active Instructors", cls="text-2xl font-bold text-indigo-900 mb-4"),
                # Instructors table
                (
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    Th(
                                        "Name",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Email",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Department",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Courses",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Students",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Status",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Actions",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                ),
                                cls="bg-indigo-50",
                            ),
                            Tbody(
                                *(
                                    Tr(
                                        Td(instructor.name, cls="py-4 px-6"),
                                        Td(instructor.email, cls="py-4 px-6"),
                                        Td(
                                            instructor.department or "Not specified",
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            str(
                                                instructor_courses.get(
                                                    instructor.email, 0
                                                )
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            str(
                                                instructor_enrollments.get(
                                                    instructor.email, 0
                                                )
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Span(
                                                "Approved" if instructor.approved else "Pending",
                                                cls="px-3 py-1 rounded-full text-sm "
                                                + (
                                                    "bg-green-100 text-green-800"
                                                    if instructor.approved
                                                    else "bg-yellow-100 text-yellow-800"
                                                ),
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Div(
                                                Button(
                                                    "Remove",
                                                    cls="bg-red-600 text-white px-3 py-1 text-sm rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                    hx_post=f"/admin/instructors/remove/{instructor.email}",
                                                    hx_confirm="Are you sure you want to remove this instructor? This will also delete all their courses and assignments.",
                                                    hx_swap="outerHTML",
                                                ),
                                                cls="flex",
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                    )
                                    for instructor in instructor_list
                                )
                            ),
                            cls="w-full",
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                    )
                )
                if instructor_list
                else Div(
                    P(
                        "No instructors found in the system.",
                        cls="text-gray-500 italic text-center py-8",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
                ),
                Div(cls="mb-8"),
            )
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Manage Instructors | FeedForward",
        dashboard_layout(
            "Manage Instructors", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


@rt("/admin/instructors/remove/{email}")
@admin_required
def admin_instructor_remove(session, email: str):
    """Remove instructor POST handler"""
    try:
        # Find and remove the instructor
        instructor = users[email]

        # Delete user (soft delete by setting status)
        if hasattr(instructor, "status"):
            instructor.status = "deleted"
            users.update(instructor)
        else:
            # Hard delete if no status field
            users.delete(email)

        # Return success message with auto-refresh
        return Div(
            P("Instructor removed successfully", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
            cls="py-2 px-4",
        )
    except Exception as e:
        # Return error message
        return Div(
            P(f"Error removing instructor: {e!s}", cls="text-red-500"), cls="py-2 px-4"
        )