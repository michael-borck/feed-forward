"""
Admin routes - user management, system configuration, etc.
"""

import json
from datetime import datetime

from fasthtml.common import *
from starlette.responses import RedirectResponse

from app import admin_required, rt
from app.models.config import (
    AIModel,
    DomainWhitelist,
    ai_models,
    domain_whitelist,
    model_capabilities,
)
from app.models.course import courses, enrollments
from app.models.user import Role, users


# --- Admin Dashboard ---
@rt("/admin/dashboard")
@admin_required
def get(session):
    # Get current user
    user = users[session["auth"]]

    # Import UI components
    from app.utils.ui import action_button, card, dashboard_layout

    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3(
                "Welcome, " + user.name,
                cls="text-xl font-semibold text-indigo-900 mb-2",
            ),
            P("Admin Account", cls="text-gray-600 mb-4"),
            Div(
                # System stats summary
                Div(
                    Div("3", cls="text-indigo-700 font-bold"),
                    P("Total Users", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2",
                ),
                # Pending approvals summary
                Div(
                    Div("0", cls="text-indigo-700 font-bold"),
                    P("Pending Approvals", cls="text-gray-600"),
                    cls="flex items-center space-x-2",
                ),
                cls="space-y-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Quick actions section
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Approve Instructors",
                    color="indigo",
                    href="/admin/instructors/approve",
                    icon="✓",
                ),
                action_button(
                    "Manage Instructors",
                    color="teal",
                    href="/admin/instructors",
                    icon="👨‍🏫",
                ),
                action_button(
                    "Manage Users", color="teal", href="/admin/users", icon="👥"
                ),
                action_button(
                    "Domain Whitelist", color="amber", href="/admin/domains", icon="🔑"
                ),
                action_button(
                    "System Settings", color="indigo", href="/admin/settings", icon="⚙️"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = Div(
        # System stats
        Div(
            Div(
                # Users card
                card(
                    Div(
                        H3("3", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Total Users", cls="text-gray-600"),
                        P("Last updated today", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Courses card
                card(
                    Div(
                        H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Active Courses", cls="text-gray-600"),
                        P("Across all instructors", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # System health card
                card(
                    Div(
                        H3("100%", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("System Health", cls="text-gray-600"),
                        P(
                            "All services operational",
                            cls="text-xs text-green-600 mt-2",
                        ),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
            )
        ),
        # User Management
        Div(
            H2("User Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3(
                        "Instructor Approval",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    P("No pending instructor approvals.", cls="text-gray-500 italic"),
                    Div(
                        action_button(
                            "View All",
                            color="indigo",
                            href="/admin/instructors/approve",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                ),
                Div(
                    H3(
                        "Recent Users", cls="text-lg font-semibold text-indigo-800 mb-4"
                    ),
                    P("3 users registered in the system.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button(
                            "Manage Users",
                            color="teal",
                            href="/admin/users",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                cls="mb-8",
            ),
        ),
        # System Configuration
        Div(
            H2("System Configuration", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3("AI Models", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P(
                        "Configure the AI models used for feedback generation.",
                        cls="text-gray-600 mb-2",
                    ),
                    Div(
                        action_button(
                            "Configure Models",
                            color="indigo",
                            href="/admin/ai-models",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                ),
                Div(
                    H3(
                        "Feedback Settings",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    P(
                        "Adjust global feedback settings and templates.",
                        cls="text-gray-600 mb-2",
                    ),
                    Div(
                        action_button(
                            "Adjust Settings",
                            color="teal",
                            href="/admin/feedback-settings",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                cls="mb-8",
            ),
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Admin Dashboard | FeedForward",
        dashboard_layout(
            "Admin Dashboard", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


# --- Approve Instructors Route ---
@rt("/admin/instructors/approve")
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session["auth"]]
    from app.utils.ui import action_button, dashboard_layout

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


# --- Approve Instructor API ---
@rt("/admin/instructors/approve/{email}")
@admin_required
def post(session, email: str):
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


# --- Reject Instructor API ---
@rt("/admin/instructors/reject/{email}")
@admin_required
def post(session, email: str):
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


# --- Instructor Management ---
@rt("/admin/instructors")
@admin_required
def get(session):
    # Get current user
    user = users[session["auth"]]

    # Import UI components
    from app.utils.ui import action_button, dashboard_layout

    # Get all instructors who aren't deleted
    instructor_list = []
    for u in users():
        if u.role == Role.INSTRUCTOR and (
            not hasattr(u, "status") or u.status != "deleted"
        ):
            instructor_list.append(u)

    # Create instructor management content
    management_content = Div(
        Div(
            H2("Manage Instructors", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                H3(
                    f"{len(instructor_list)} Instructors",
                    cls="text-xl font-bold text-indigo-800 mb-4",
                ),
                Div(
                    P("• Manage instructor accounts", cls="text-gray-600 mb-1"),
                    P(
                        "• Approve new instructor registrations",
                        cls="text-gray-600 mb-1",
                    ),
                    P("• Remove instructors from the system", cls="text-gray-600"),
                    cls="text-sm mb-4",
                ),
                cls="bg-indigo-50 p-4 rounded-lg mb-6",
            ),
            # Instructor table
            Div(
                Table(
                    Thead(
                        Tr(
                            Th(
                                "Name",
                                cls="px-4 py-3 text-left text-sm font-semibold text-gray-700",
                            ),
                            Th(
                                "Email",
                                cls="px-4 py-3 text-left text-sm font-semibold text-gray-700",
                            ),
                            Th(
                                "Status",
                                cls="px-4 py-3 text-left text-sm font-semibold text-gray-700",
                            ),
                            Th(
                                "Department",
                                cls="px-4 py-3 text-left text-sm font-semibold text-gray-700",
                            ),
                            Th(
                                "Actions",
                                cls="px-4 py-3 text-left text-sm font-semibold text-gray-700",
                            ),
                            cls="bg-gray-100",
                        )
                    ),
                    Tbody(
                        *(
                            Tr(
                                Td(
                                    instructor.name,
                                    cls="px-4 py-3 text-sm text-gray-800",
                                ),
                                Td(
                                    instructor.email,
                                    cls="px-4 py-3 text-sm text-gray-800",
                                ),
                                Td(
                                    (
                                        Span(
                                            "✅ Approved",
                                            cls="px-3 py-1 rounded-full text-xs bg-green-100 text-green-800",
                                        )
                                        if instructor.approved
                                        else Span(
                                            "⏳ Pending Approval",
                                            cls="px-3 py-1 rounded-full text-xs bg-amber-100 text-amber-800",
                                        )
                                    ),
                                    cls="px-4 py-3",
                                ),
                                Td(
                                    instructor.department or "Not specified",
                                    cls="px-4 py-3 text-sm text-gray-800",
                                ),
                                Td(
                                    Div(
                                        (
                                            Button(
                                                "Approve",
                                                cls="text-xs px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 mr-2",
                                                hx_post=f"/admin/instructors/approve/{instructor.email}",
                                                hx_target="#message",
                                            )
                                            if not instructor.approved
                                            else Span("", cls="")
                                        ),
                                        Button(
                                            "Remove",
                                            cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                                            hx_post=f"/admin/instructors/remove/{instructor.email}",
                                            hx_confirm=f"Are you sure you want to remove {instructor.email}? This will delete their account and cannot be undone.",
                                            hx_target="#message",
                                        ),
                                    ),
                                    cls="px-4 py-3",
                                ),
                                cls="border-b border-gray-200 hover:bg-gray-50",
                            )
                            for instructor in instructor_list
                        )
                    ),
                    cls="min-w-full",
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow border border-gray-200",
            ),
            # Message area for feedback
            Div(id="message", cls="mt-6"),
            cls="",
        ),
        cls="p-6",
    )

    # Create sidebar content
    sidebar_content = Div(
        Div(
            H3("Admin Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
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
                action_button(
                    "Domain Whitelist", color="amber", href="/admin/domains", icon="🔑"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Instructor Stats", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total: {len(instructor_list)}", cls="text-gray-600 mb-2"),
            P(
                f"Approved: {sum(1 for i in instructor_list if i.approved)}",
                cls="text-green-600 mb-2",
            ),
            P(
                f"Pending: {sum(1 for i in instructor_list if not i.approved)}",
                cls="text-amber-600 mb-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return Titled(
        "Manage Instructors | FeedForward",
        dashboard_layout(
            "Manage Instructors",
            sidebar_content,
            management_content,
            user_role=Role.ADMIN,
        ),
    )


# --- Remove Instructor ---
@rt("/admin/instructors/remove/{email}")
@admin_required
def post(session, email: str):
    # Get current user
    admin_user = users[session["auth"]]

    # Don't allow removing self
    if email == admin_user.email:
        return Div(
            P("You cannot remove your own account.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )

    try:
        # Get the instructor
        instructor = users[email]

        # Check if this is actually an instructor
        if instructor.role != Role.INSTRUCTOR:
            return Div(
                P("This user is not an instructor.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg",
            )

        # Import datetime for timestamp updates
        from datetime import datetime

        # Remove all enrollments for courses taught by this instructor
        for c in courses():
            if c.instructor_email == email:
                # Soft delete all enrollments for this course
                for e in enrollments():
                    if e.course_id == c.id:
                        try:
                            # No status field in enrollments yet, so we'll still need to hard delete
                            enrollments.delete(e.id)
                        except:
                            pass

                # Soft delete the course
                try:
                    c.status = "deleted"
                    c.updated_at = datetime.now().isoformat()
                    courses.update(c)
                except:
                    pass

        # Soft delete the instructor account
        instructor.status = "deleted"
        instructor.last_active = datetime.now().isoformat()
        users.update(instructor)

        return Div(
            P(
                f"Instructor {email} has been removed from the system.",
                cls="text-green-600",
            ),
            Script("setTimeout(function() { window.location.reload(); }, 1500);"),
            cls="bg-green-50 p-4 rounded-lg",
        )
    except Exception as e:
        return Div(
            P(f"Error removing instructor: {e!s}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- Domain Whitelist Management ---
@rt("/admin/domains")
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session["auth"]]
    from app.utils.ui import action_button, dashboard_layout

    # Get all domains from the whitelist
    all_domains = list(domain_whitelist())

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
                    "Approve Instructors",
                    color="indigo",
                    href="/admin/instructors/approve",
                    icon="✓",
                ),
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

    # Main content - Domain whitelist management
    main_content = Div(
        H1(
            "Domain Whitelist Management", cls="text-3xl font-bold text-indigo-900 mb-6"
        ),
        P(
            "Configure which domains are allowed for instructor registration and whether they're auto-approved.",
            cls="text-gray-600 mb-8",
        ),
        # Add new domain form
        Div(
            H2("Add New Domain", cls="text-2xl font-bold text-indigo-900 mb-4"),
            Form(
                Div(
                    Div(
                        Label(
                            "Domain",
                            for_="domain",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "e.g. 'curtin.edu.au' (without 'http://' or '@')",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            id="domain",
                            type="text",
                            placeholder="Domain name",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-4 w-full",
                    ),
                    Div(
                        Div(
                            Input(
                                type="checkbox",
                                id="auto_approve",
                                cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Auto-approve instructors from this domain",
                                for_="auto_approve",
                                cls="ml-2 block text-indigo-900 font-medium",
                            ),
                            cls="flex items-center",
                        ),
                        cls="mb-6",
                    ),
                    Div(
                        Button(
                            "Add Domain",
                            type="submit",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="mb-4",
                    ),
                    Span(id="domain_result", cls="block text-center"),
                    cls="flex flex-wrap",
                ),
                hx_post="/admin/domains/add",
                hx_target="#domain_result",
                hx_swap="innerHTML",
                cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-8",
            ),
        ),
        # Domain list
        Div(
            H2("Current Domains", cls="text-2xl font-bold text-indigo-900 mb-4"),
            # Check if there are domains
            (
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th(
                                    "Domain",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Auto-approve",
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
                                    Td(domain["domain"], cls="py-4 px-6"),
                                    Td(
                                        Span(
                                            "✅ Yes"
                                            if domain["auto_approve_instructor"]
                                            else "❌ No",
                                            cls="px-3 py-1 rounded-full text-sm "
                                            + (
                                                "bg-green-100 text-green-800"
                                                if domain["auto_approve_instructor"]
                                                else "bg-red-100 text-red-800"
                                            ),
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    Td(
                                        Div(
                                            Button(
                                                "Toggle Auto-approve",
                                                cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                                                hx_post=f"/admin/domains/toggle/{domain['id']}",
                                                hx_target="closest tr",
                                                hx_swap="outerHTML",
                                            ),
                                            Button(
                                                "Delete",
                                                cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                hx_post=f"/admin/domains/delete/{domain['id']}",
                                                hx_target="closest tr",
                                                hx_swap="outerHTML",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for domain in all_domains
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                )
            )
            if all_domains
            else Div(
                P(
                    "No domains in the whitelist. Add some domains to allow instructor registration.",
                    cls="text-gray-500 italic text-center py-8",
                ),
                cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
            ),
            cls="mb-8",
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
        "Domain Whitelist | FeedForward",
        dashboard_layout(
            "Domain Whitelist", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


# --- Add Domain to Whitelist ---
@rt("/admin/domains/add")
@admin_required
def post(session, domain: str, auto_approve: bool = False):
    # Basic validation
    if not domain:
        return Div(P("Domain name is required", cls="text-red-500"))

    # Clean up domain
    domain = domain.strip().lower()

    # Remove any protocol or @ symbol
    domain = domain.replace("http://", "").replace("https://", "").replace("@", "")

    # Check if domain already exists
    for existing in domain_whitelist.select():
        if existing["domain"] == domain:
            return Div(
                P(
                    f"Domain '{domain}' already exists in the whitelist",
                    cls="text-amber-500",
                )
            )

    try:
        # Get next available ID
        next_id = 1
        existing_ids = [d["id"] for d in domain_whitelist.select()]
        if existing_ids:
            next_id = max(existing_ids) + 1

        # Create timestamp
        from datetime import datetime

        now = datetime.now().isoformat()

        # Create new domain entry
        new_domain = DomainWhitelist(
            id=next_id,
            domain=domain,
            auto_approve_instructor=auto_approve,
            created_at=now,
            updated_at=now,
        )

        # Add to database
        domain_whitelist.insert(new_domain)

        # Return success message with page reload
        return Div(
            P(f"Added domain '{domain}' to the whitelist", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        )
    except Exception as e:
        # Return error message
        return Div(P(f"Error adding domain: {e!s}", cls="text-red-500"))


# --- Toggle Auto-approve for Domain ---
@rt("/admin/domains/toggle/{id}")
@admin_required
def post(session, id: int):
    try:
        # Find the domain
        domain_record = None
        for d in domain_whitelist.select():
            if d["id"] == id:
                domain_record = d
                break

        if not domain_record:
            return "Domain not found"

        # Toggle auto-approve
        domain_record["auto_approve_instructor"] = not domain_record[
            "auto_approve_instructor"
        ]

        # Update timestamp
        from datetime import datetime

        domain_record["updated_at"] = datetime.now().isoformat()

        # Save changes
        domain_whitelist.update(domain_record)

        # Return updated row
        return Tr(
            Td(domain_record["domain"], cls="py-4 px-6"),
            Td(
                Span(
                    "✅ Yes" if domain_record["auto_approve_instructor"] else "❌ No",
                    cls="px-3 py-1 rounded-full text-sm "
                    + (
                        "bg-green-100 text-green-800"
                        if domain_record["auto_approve_instructor"]
                        else "bg-red-100 text-red-800"
                    ),
                ),
                cls="py-4 px-6",
            ),
            Td(
                Div(
                    Button(
                        "Toggle Auto-approve",
                        cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                        hx_post=f"/admin/domains/toggle/{id}",
                        hx_target="closest tr",
                        hx_swap="outerHTML",
                    ),
                    Button(
                        "Delete",
                        cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                        hx_post=f"/admin/domains/delete/{id}",
                        hx_target="closest tr",
                        hx_swap="outerHTML",
                    ),
                    cls="flex",
                ),
                cls="py-4 px-6",
            ),
        )
    except Exception as e:
        return f"Error updating domain: {e!s}"


# --- Delete Domain from Whitelist ---
@rt("/admin/domains/delete/{id}")
@admin_required
def post(session, id: int):
    try:
        # Find the domain
        domain_found = False
        for d in domain_whitelist.select():
            if d["id"] == id:
                domain_found = True
                break

        if not domain_found:
            return "Domain not found"

        # Delete the domain
        domain_whitelist.delete(id)

        # Return deleted confirmation
        return Div(
            P("Domain deleted", cls="text-green-500 p-4"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        )
    except Exception as e:
        return f"Error deleting domain: {e!s}"


# --- AI Model Management ---
@rt("/admin/ai-models")
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session["auth"]]
    from app.utils.ui import action_button, dashboard_layout

    # Get all AI models
    model_list = list(ai_models())

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
                    "Add New Model",
                    color="indigo",
                    href="/admin/ai-models/new",
                    icon="➕",
                ),
                action_button(
                    "System Settings", color="teal", href="/admin/settings", icon="⚙️"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Model stats section
        Div(
            H3("AI Model Stats", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                Div(
                    P(f"Total Models: {len(model_list)}", cls="text-gray-700 mb-1"),
                    P(
                        f"Active Models: {sum(1 for m in model_list if m.active)}",
                        cls="text-green-700 mb-1",
                    ),
                    P(
                        f"System Models: {sum(1 for m in model_list if m.owner_type == 'system')}",
                        cls="text-indigo-700 mb-1",
                    ),
                    P(
                        f"Instructor Models: {sum(1 for m in model_list if m.owner_type == 'instructor')}",
                        cls="text-teal-700",
                    ),
                ),
                cls="space-y-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - AI Model management
    main_content = Div(
        H1("AI Model Management", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P(
            "Configure AI models available for feedback generation.",
            cls="text-gray-600 mb-8",
        ),
        # AI Model list
        Div(
            H2("Available Models", cls="text-2xl font-bold text-indigo-900 mb-4"),
            Div(
                # Explanatory info
                Div(
                    H3(
                        "Model Configuration",
                        cls="text-lg font-semibold text-indigo-800 mb-2",
                    ),
                    P(
                        "Models can be provided by the system or configured by individual instructors.",
                        cls="text-gray-600 mb-1",
                    ),
                    P(
                        "System models are available to all instructors, while instructor models are private.",
                        cls="text-gray-600 mb-1",
                    ),
                    cls="bg-indigo-50 p-4 rounded-lg mb-6",
                ),
                # Add New Model button
                Div(
                    action_button(
                        "Add New Model",
                        color="indigo",
                        href="/admin/ai-models/new",
                        icon="➕",
                        size="regular",
                    ),
                    cls="mb-6",
                ),
                # Model table
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
                                        "Provider",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Model ID",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Owner",
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
                                        Td(model.name, cls="py-4 px-6"),
                                        Td(model.provider, cls="py-4 px-6"),
                                        Td(model.model_id, cls="py-4 px-6"),
                                        Td(
                                            Span(
                                                "System"
                                                if model.owner_type == "system"
                                                else "Instructor",
                                                cls="px-3 py-1 rounded-full text-xs "
                                                + (
                                                    "bg-indigo-100 text-indigo-800"
                                                    if model.owner_type == "system"
                                                    else "bg-teal-100 text-teal-800"
                                                ),
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Span(
                                                "Active"
                                                if model.active
                                                else "Inactive",
                                                cls="px-3 py-1 rounded-full text-xs "
                                                + (
                                                    "bg-green-100 text-green-800"
                                                    if model.active
                                                    else "bg-gray-100 text-gray-800"
                                                ),
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Div(
                                                A(
                                                    "Edit",
                                                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                                    href=f"/admin/ai-models/edit/{model.id}",
                                                ),
                                                Button(
                                                    "Delete",
                                                    cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                    hx_delete=f"/admin/ai-models/{model.id}",
                                                    hx_confirm=f"Are you sure you want to delete the model '{model.name}'?",
                                                    hx_target="closest tr",
                                                    hx_swap="outerHTML",
                                                ),
                                                cls="flex",
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                    )
                                    for model in model_list
                                )
                            ),
                            cls="w-full",
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                    )
                )
                if model_list
                else Div(
                    P(
                        "No AI models configured yet. Add a model to get started.",
                        cls="text-gray-500 italic text-center py-8",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
                ),
                cls="mb-8",
            ),
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
        "AI Model Management | FeedForward",
        dashboard_layout(
            "AI Model Management", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


# --- New AI Model Form ---
@rt("/admin/ai-models/new")
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session["auth"]]
    from app.utils.ui import action_button, dashboard_layout

    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Models", color="gray", href="/admin/ai-models", icon="←"
                ),
                action_button(
                    "Dashboard", color="gray", href="/admin/dashboard", icon="🏠"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Help section
        Div(
            H3("Provider Help", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                # Provider cards
                Div(
                    H4("OpenAI", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: gpt-4, gpt-3.5-turbo", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Anthropic", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P(
                        "Models: claude-3-opus, claude-3-sonnet",
                        cls="text-gray-600 text-sm",
                    ),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Google", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P(
                        "Models: gemini-pro, gemini-1.5-pro",
                        cls="text-gray-600 text-sm",
                    ),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Ollama", cls="font-semibold text-indigo-800 mb-1"),
                    P("Server URL required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: llama3, mistral", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("HuggingFace", cls="font-semibold text-indigo-800 mb-1"),
                    P(
                        "API Key optional, URL for custom endpoints",
                        cls="text-gray-600 mb-1 text-sm",
                    ),
                    P("Models: microsoft/DialoGPT-large", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Other/Custom", cls="font-semibold text-indigo-800 mb-1"),
                    P("Custom endpoint URL required", cls="text-gray-600 mb-1 text-sm"),
                    P("Compatible with OpenAI-style APIs", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                cls="space-y-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Add new AI Model form
    main_content = Div(
        H1("Add New AI Model", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P(
            "Configure a new AI model for feedback generation.",
            cls="text-gray-600 mb-8",
        ),
        # Model configuration form
        Form(
            # Basic model information
            Div(
                H2("Model Information", cls="text-2xl font-bold text-indigo-900 mb-6"),
                Div(
                    Div(
                        Label(
                            "Model Name",
                            for_="name",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Display name for this model",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="name",
                            name="name",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Provider",
                            for_="provider",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("AI model provider", cls="text-sm text-gray-500 mb-1"),
                        Select(
                            Option(
                                "Select a provider",
                                value="",
                                disabled=True,
                                selected=True,
                            ),
                            Option("OpenAI", value="OpenAI"),
                            Option("Anthropic", value="Anthropic"),
                            Option("Google", value="Google"),
                            Option("Ollama", value="Ollama"),
                            Option("HuggingFace", value="HuggingFace"),
                            Option("Other", value="Other"),
                            id="provider",
                            name="provider",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Model ID",
                            for_="model_id",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Specific model identifier (e.g., gpt-4, claude-3-opus)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="model_id",
                            name="model_id",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Version",
                            for_="version",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Version information (optional)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="version",
                            name="version",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Description",
                            for_="description",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Brief description of this model's capabilities",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Textarea(
                            id="description",
                            name="description",
                            rows=3,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    Div(
                        Label(
                            "Maximum Context Length",
                            for_="max_context",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Maximum token length this model can process",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="number",
                            id="max_context",
                            name="max_context",
                            value="8192",
                            min="1024",
                            step="1024",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Owner Type",
                            for_="owner_type",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Who owns/manages this model",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Select(
                            Option("System", value="system", selected=True),
                            Option("Instructor", value="instructor"),
                            id="owner_type",
                            name="owner_type",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Status",
                            for_="active",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Select(
                            Option("Active", value="true", selected=True),
                            Option("Inactive", value="false"),
                            id="active",
                            name="active",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # Model capabilities section
                H2(
                    "Model Capabilities",
                    cls="text-2xl font-bold text-indigo-900 mb-6 mt-8",
                ),
                Div(
                    P(
                        "Select which capabilities this model supports:",
                        cls="text-gray-600 mb-4",
                    ),
                    Div(
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_text",
                                name="capabilities",
                                value="text",
                                checked=True,
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Text",
                                for_="capability_text",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_code",
                                name="capabilities",
                                value="code",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Code",
                                for_="capability_code",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_vision",
                                name="capabilities",
                                value="vision",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Vision",
                                for_="capability_vision",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_audio",
                                name="capabilities",
                                value="audio",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Audio",
                                for_="capability_audio",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        cls="mb-6",
                    ),
                    H3(
                        "Primary Capability",
                        cls="text-xl font-bold text-indigo-900 mb-2",
                    ),
                    P(
                        "Select the primary capability this model is optimized for:",
                        cls="text-gray-600 mb-4",
                    ),
                    Div(
                        Select(
                            Option("Text", value="text", selected=True),
                            Option("Code", value="code"),
                            Option("Vision", value="vision"),
                            Option("Audio", value="audio"),
                            id="primary_capability",
                            name="primary_capability",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # API Configuration section
                H2(
                    "API Configuration",
                    cls="text-2xl font-bold text-indigo-900 mb-6 mt-8",
                ),
                Div(
                    # OpenAI Config
                    Div(
                        Label(
                            "API Key",
                            for_="openai_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("OpenAI API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="openai_api_key",
                            name="openai_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="openai-config",
                        cls="w-full",
                    ),
                    # Anthropic Config
                    Div(
                        Label(
                            "API Key",
                            for_="anthropic_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("Anthropic API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="anthropic_api_key",
                            name="anthropic_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="anthropic-config",
                        cls="w-full hidden",
                    ),
                    # Google Config
                    Div(
                        Label(
                            "API Key",
                            for_="google_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("Google AI API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="google_api_key",
                            name="google_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="google_base_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Google AI endpoint URL (optional, leave empty for default)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="google_base_url",
                            name="google_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="google-config",
                        cls="w-full hidden",
                    ),
                    # Ollama Config
                    Div(
                        Label(
                            "Server URL",
                            for_="ollama_base_url",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Ollama server URL (e.g., http://localhost:11434)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="ollama_base_url",
                            name="ollama_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: No API key required for local Ollama",
                            cls="text-xs text-green-600 mt-1",
                        ),
                        id="ollama-config",
                        cls="w-full hidden",
                    ),
                    # HuggingFace Config
                    Div(
                        Label(
                            "API Key",
                            for_="huggingface_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Hugging Face API key (optional for public models)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="password",
                            id="huggingface_api_key",
                            name="huggingface_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="huggingface_api_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Custom endpoint URL (optional, leave empty for default)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="huggingface_api_url",
                            name="huggingface_api_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="huggingface-config",
                        cls="w-full hidden",
                    ),
                    # Other Provider Config
                    Div(
                        Label(
                            "API Key",
                            for_="other_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "API key for custom provider (if required)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="password",
                            id="other_api_key",
                            name="other_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="other_api_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Custom endpoint URL (required for custom providers)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="other_api_url",
                            name="other_api_url",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="other-config",
                        cls="w-full hidden",
                    ),
                    # Common settings
                    Div(
                        Label(
                            "Temperature",
                            for_="temperature",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Controls randomness (0.0-1.0)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="number",
                            id="temperature",
                            name="temperature",
                            value="0.2",
                            min="0",
                            max="1",
                            step="0.1",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "System Prompt",
                            for_="system_prompt",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Default system prompt for educational assessment",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Textarea(
                            id="system_prompt",
                            name="system_prompt",
                            rows=3,
                            value="You are an expert educational assessor providing detailed, constructive feedback on student work.",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    # Provider selection script
                    Script("""
                    document.getElementById('provider').addEventListener('change', function() {
                        // Hide all config sections
                        document.getElementById('openai-config').classList.add('hidden');
                        document.getElementById('anthropic-config').classList.add('hidden');
                        document.getElementById('google-config').classList.add('hidden');
                        document.getElementById('ollama-config').classList.add('hidden');
                        document.getElementById('huggingface-config').classList.add('hidden');
                        document.getElementById('other-config').classList.add('hidden');
                        
                        // Show selected provider config
                        if (this.value === 'OpenAI') {
                            document.getElementById('openai-config').classList.remove('hidden');
                        } else if (this.value === 'Anthropic') {
                            document.getElementById('anthropic-config').classList.remove('hidden');
                        } else if (this.value === 'Google') {
                            document.getElementById('google-config').classList.remove('hidden');
                        } else if (this.value === 'Ollama') {
                            document.getElementById('ollama-config').classList.remove('hidden');
                        } else if (this.value === 'HuggingFace') {
                            document.getElementById('huggingface-config').classList.remove('hidden');
                        } else if (this.value === 'Other') {
                            document.getElementById('other-config').classList.remove('hidden');
                        }
                    });
                    """),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # Test Connection Button and Form submission
                Div(
                    Div(id="test-result", cls="mb-4"),
                    Div(id="form-message", cls="mb-4"),
                    Div(
                        Button(
                            "Test Connection",
                            type="button",
                            id="test-connection-btn",
                            cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm mr-4",
                            onclick="testConnection()",
                        ),
                        Button(
                            "Cancel",
                            type="button",
                            onClick="window.location='/admin/ai-models'",
                            cls="bg-gray-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm mr-4",
                        ),
                        Button(
                            "Save Model",
                            type="submit",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="flex",
                    ),
                    cls="mt-6",
                ),
                # Test Connection Script
                Script("""
                function testConnection() {
                    const provider = document.getElementById('provider').value;
                    if (!provider) {
                        document.getElementById('test-result').innerHTML = '<div class="bg-red-50 p-4 rounded-lg"><p class="text-red-500">Please select a provider first</p></div>';
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('provider', provider);
                    
                    // Get API key based on provider
                    if (provider === 'OpenAI') {
                        formData.append('api_key', document.getElementById('openai_api_key').value);
                    } else if (provider === 'Anthropic') {
                        formData.append('api_key', document.getElementById('anthropic_api_key').value);
                    } else if (provider === 'Google') {
                        formData.append('api_key', document.getElementById('google_api_key').value);
                        formData.append('base_url', document.getElementById('google_base_url').value);
                    } else if (provider === 'Ollama') {
                        formData.append('base_url', document.getElementById('ollama_base_url').value);
                    } else if (provider === 'HuggingFace') {
                        formData.append('api_key', document.getElementById('huggingface_api_key').value);
                        formData.append('base_url', document.getElementById('huggingface_api_url').value);
                    } else if (provider === 'Other') {
                        formData.append('api_key', document.getElementById('other_api_key').value);
                        formData.append('base_url', document.getElementById('other_api_url').value);
                    }
                    
                    // Show loading state
                    document.getElementById('test-result').innerHTML = '<div class="bg-blue-50 p-4 rounded-lg"><p class="text-blue-600">Testing connection...</p></div>';
                    
                    // Make the request
                    fetch('/admin/ai-models/test', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('test-result').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('test-result').innerHTML = '<div class="bg-red-50 p-4 rounded-lg"><p class="text-red-500">Error: ' + error + '</p></div>';
                    });
                }
                """),
                cls="mb-8",
            ),
            hx_post="/admin/ai-models/create",
            hx_target="#form-message",
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Add New AI Model | FeedForward",
        dashboard_layout(
            "Add New AI Model", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


# --- Create New AI Model ---
@rt("/admin/ai-models/create")
@admin_required
def post(
    session,
    name: str,
    provider: str,
    model_id: str,
    version: str = "",
    description: str = "",
    max_context: int = 8192,
    owner_type: str = "system",
    owner_id: int = 0,
    active: str = "true",
    capabilities: list = None,
    primary_capability: str = "text",
    temperature: float = 0.2,
    system_prompt: str = "You are an expert educational assessor providing detailed, constructive feedback on student work.",
    openai_api_key: str = None,
    anthropic_api_key: str = None,
    google_api_key: str = None,
    google_base_url: str = None,
    ollama_base_url: str = None,
    huggingface_api_key: str = None,
    huggingface_api_url: str = None,
    other_api_key: str = None,
    other_api_url: str = None,
):
    try:
        # Convert capabilities to list if it's a single value
        if capabilities and not isinstance(capabilities, list):
            capabilities = [capabilities]

        # Default to text if no capabilities selected
        if not capabilities:
            capabilities = ["text"]

        # Create API config based on provider
        api_config = {}
        if provider == "OpenAI":
            api_config = {
                "api_key": openai_api_key,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Anthropic":
            api_config = {
                "api_key": anthropic_api_key,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Google":
            api_config = {
                "api_key": google_api_key,
                "base_url": google_base_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Ollama":
            if not ollama_base_url:
                return Div(
                    P("Ollama requires a server URL", cls="text-red-500"),
                    cls="bg-red-50 p-4 rounded-lg",
                )
            api_config = {
                "base_url": ollama_base_url,
                "temperature": float(temperature),
            }
        elif provider == "HuggingFace":
            api_config = {
                "api_key": huggingface_api_key,
                "base_url": huggingface_api_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        else:
            # Generic config for "Other" providers
            api_config = {
                "api_key": other_api_key,
                "base_url": other_api_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }

        # For security, encrypt API keys if present
        from app.utils.crypto import encrypt_sensitive_data

        for key in api_config:
            if key.endswith("api_key") and api_config[key]:
                api_config[key] = encrypt_sensitive_data(api_config[key])

        # Convert api_config to JSON string
        api_config_str = json.dumps(api_config)

        # Get next available ID
        next_id = 1
        existing_ids = [m.id for m in ai_models()]
        if existing_ids:
            next_id = max(existing_ids) + 1

        # Create timestamp
        now = datetime.now().isoformat()

        # Create new AI model
        new_model = AIModel(
            id=next_id,
            name=name,
            provider=provider,
            model_id=model_id,
            model_version=version,
            description=description,
            api_config=api_config_str,
            owner_type=owner_type,
            owner_id=int(owner_id) if owner_id else 0,
            capabilities=json.dumps(capabilities),
            max_context=int(max_context),
            active=active.lower() == "true",
            created_at=now,
            updated_at=now,
        )

        # Add to database
        ai_models.insert(new_model)

        # Skip capability entries for now to get demo working
        # TODO: Re-enable capability insertion after demo

        # Return success message with redirect
        return Div(
            P(f"AI Model '{name}' created successfully!", cls="text-green-500 mb-2"),
            Script(
                "setTimeout(function() { window.location = '/admin/ai-models'; }, 1500);"
            ),
            cls="bg-green-50 p-4 rounded-lg",
        )
    except Exception as e:
        # Return detailed error message for debugging
        import traceback

        error_details = traceback.format_exc()
        return Div(
            P(f"Error creating AI model: {e!s}", cls="text-red-500 mb-2"),
            P("Debug details:", cls="text-red-600 text-sm font-semibold"),
            Pre(
                error_details,
                cls="text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-40",
            ),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- Edit AI Model (Admin) ---
@rt("/admin/ai-models/edit/{id}")
@admin_required
def get(session, id: int):
    try:
        # Get the specific model
        model = None
        for m in ai_models():
            if m.id == id:
                model = m
                break

        if not model:
            return RedirectResponse("/error/404")

        # Parse model configuration
        import json

        try:
            config = json.loads(model.api_config) if model.api_config else {}
        except:
            config = {}

        try:
            capabilities = json.loads(model.capabilities) if model.capabilities else []
        except:
            capabilities = []

        from app.utils.ui import card, dashboard_layout

        # Sidebar content
        sidebar_content = Div(
            card(
                Div(
                    H3("AI Models", cls="font-semibold text-indigo-900 mb-4"),
                    A(
                        "← Back to Models",
                        href="/admin/ai-models",
                        cls="text-indigo-600 hover:text-indigo-800 text-sm",
                    ),
                    A(
                        "Create New Model",
                        href="/admin/ai-models/new",
                        cls="block mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg text-center hover:bg-indigo-700 transition-colors",
                    ),
                )
            )
        )

        # Main content - Edit AI Model form
        main_content = Div(
            H1(
                f"Edit AI Model: {model.name}",
                cls="text-3xl font-bold text-indigo-900 mb-6",
            ),
            P("Update AI model configuration.", cls="text-gray-600 mb-8"),
            # Model configuration form
            Form(
                # Basic model information
                Div(
                    H2(
                        "Model Information",
                        cls="text-2xl font-bold text-indigo-900 mb-6",
                    ),
                    Div(
                        Div(
                            Label(
                                "Model Name",
                                for_="name",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            P(
                                "Display name for this model",
                                cls="text-sm text-gray-500 mb-1",
                            ),
                            Input(
                                type="text",
                                id="name",
                                name="name",
                                value=model.name,
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-6 w-full md:w-1/2",
                        ),
                        Div(
                            Label(
                                "Provider",
                                for_="provider",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            P("AI model provider", cls="text-sm text-gray-500 mb-1"),
                            Select(
                                Option(
                                    "OpenAI",
                                    value="OpenAI",
                                    selected=(model.provider == "OpenAI"),
                                ),
                                Option(
                                    "Anthropic",
                                    value="Anthropic",
                                    selected=(model.provider == "Anthropic"),
                                ),
                                Option(
                                    "Google",
                                    value="Google",
                                    selected=(model.provider == "Google"),
                                ),
                                Option(
                                    "Ollama",
                                    value="Ollama",
                                    selected=(model.provider == "Ollama"),
                                ),
                                Option(
                                    "HuggingFace",
                                    value="HuggingFace",
                                    selected=(model.provider == "HuggingFace"),
                                ),
                                Option(
                                    "Other",
                                    value="Other",
                                    selected=(model.provider == "Other"),
                                ),
                                id="provider",
                                name="provider",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-6 w-full md:w-1/2",
                        ),
                        Div(
                            Label(
                                "Model ID",
                                for_="model_id",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            P(
                                "Specific model identifier",
                                cls="text-sm text-gray-500 mb-1",
                            ),
                            Input(
                                type="text",
                                id="model_id",
                                name="model_id",
                                value=model.model_id,
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-6 w-full md:w-1/2",
                        ),
                        Div(
                            Label(
                                "Status",
                                for_="active",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            Select(
                                Option("Active", value="true", selected=model.active),
                                Option(
                                    "Inactive", value="false", selected=not model.active
                                ),
                                id="active",
                                name="active",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-6 w-full md:w-1/2",
                        ),
                        cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                    ),
                ),
                # API Configuration section
                H2(
                    "API Configuration",
                    cls="text-2xl font-bold text-indigo-900 mb-6 mt-8",
                ),
                Div(
                    # API Key field
                    Div(
                        Label(
                            "API Key",
                            for_="api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "API key for this provider (leave empty to keep current)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="password",
                            id="api_key",
                            name="api_key",
                            placeholder="Enter new API key or leave empty to keep current",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        cls="mb-6 w-full",
                    ),
                    # Base URL field
                    Div(
                        Label(
                            "Base URL",
                            for_="base_url",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Custom endpoint URL (for Ollama, custom providers, etc.)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="base_url",
                            name="base_url",
                            value=config.get("base_url", ""),
                            placeholder="e.g., http://localhost:11434 for Ollama",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    # Temperature
                    Div(
                        Label(
                            "Temperature",
                            for_="temperature",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Controls randomness (0.0-1.0)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="number",
                            id="temperature",
                            name="temperature",
                            value=str(config.get("temperature", 0.2)),
                            min="0",
                            max="1",
                            step="0.1",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    # System Prompt
                    Div(
                        Label(
                            "System Prompt",
                            for_="system_prompt",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Default system prompt for educational assessment",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Textarea(
                            id="system_prompt",
                            name="system_prompt",
                            rows=3,
                            value=config.get(
                                "system_prompt",
                                "You are an expert educational assessor providing detailed, constructive feedback on student work.",
                            ),
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # Test Connection and Form submission
                Div(
                    Div(id="test-result", cls="mb-4"),
                    Div(id="form-message", cls="mb-4"),
                    Div(
                        Button(
                            "Test Connection",
                            type="button",
                            id="test-connection-btn",
                            cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm mr-4",
                            onclick=f"testConnectionEdit('{model.provider}')",
                        ),
                        Button(
                            "Cancel",
                            type="button",
                            onClick="window.location='/admin/ai-models'",
                            cls="bg-gray-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm mr-4",
                        ),
                        Button(
                            "Save Changes",
                            type="submit",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="flex",
                    ),
                    cls="mt-6",
                ),
                # Test Connection Script for Edit Form
                Script("""
                function testConnectionEdit(provider) {
                    const formData = new FormData();
                    formData.append('provider', provider);
                    
                    // Get current values
                    const apiKey = document.getElementById('api_key').value;
                    const baseUrl = document.getElementById('base_url').value;
                    
                    if (apiKey) {
                        formData.append('api_key', apiKey);
                    }
                    if (baseUrl) {
                        formData.append('base_url', baseUrl);
                    }
                    
                    // Show loading state
                    document.getElementById('test-result').innerHTML = '<div class="bg-blue-50 p-4 rounded-lg"><p class="text-blue-600">Testing connection...</p></div>';
                    
                    // Make the request
                    fetch('/admin/ai-models/test', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('test-result').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('test-result').innerHTML = '<div class="bg-red-50 p-4 rounded-lg"><p class="text-red-500">Error: ' + error + '</p></div>';
                    });
                }
                """),
                cls="mb-8",
                hx_post=f"/admin/ai-models/edit/{id}",
                hx_target="#form-message",
            ),
        )

        return dashboard_layout(
            title=f"Edit AI Model: {model.name}",
            sidebar=sidebar_content,
            main_content=main_content,
            user_role=users[session["auth"]].role,
            user=users[session["auth"]],
            current_path=f"/admin/ai-models/edit/{id}",
        )

    except Exception:
        return RedirectResponse("/error/500")


# --- Update AI Model (Admin) ---
@rt("/admin/ai-models/edit/{id}")
@admin_required
def post(
    session,
    id: int,
    name: str,
    provider: str,
    model_id: str,
    active: str,
    api_key: str = None,
    base_url: str = None,
    temperature: float = 0.2,
    system_prompt: str = "You are an expert educational assessor providing detailed, constructive feedback on student work.",
):
    try:
        # Get the specific model
        model = None
        for m in ai_models():
            if m.id == id:
                model = m
                break

        if not model:
            return Div(
                P("Model not found", cls="text-red-500"), cls="bg-red-50 p-4 rounded-lg"
            )

        # Parse existing config
        import json

        try:
            config = json.loads(model.api_config) if model.api_config else {}
        except:
            config = {}

        # Update configuration
        config["temperature"] = float(temperature)
        config["system_prompt"] = system_prompt

        # Update API key only if provided
        if api_key and api_key.strip():
            from app.utils.crypto import encrypt_sensitive_data

            config["api_key"] = encrypt_sensitive_data(api_key)

        # Update base URL
        if base_url is not None:
            config["base_url"] = base_url

        # Update model properties
        model.name = name
        model.provider = provider
        model.model_id = model_id
        model.active = active.lower() == "true"
        model.api_config = json.dumps(config)
        model.updated_at = datetime.now().isoformat()

        # Save to database
        ai_models.update(model)

        # Return success message with redirect
        return Div(
            P(f"AI Model '{name}' updated successfully!", cls="text-green-500 mb-2"),
            Script(
                "setTimeout(function() { window.location = '/admin/ai-models'; }, 1500);"
            ),
            cls="bg-green-50 p-4 rounded-lg",
        )

    except Exception as e:
        return Div(
            P(f"Error updating AI model: {e!s}", cls="text-red-500"),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- Test AI Model Connection ---
@rt("/admin/ai-models/test")
@admin_required
def post(session, provider: str, api_key: str = None, base_url: str = None):
    """Test AI model connection"""
    try:

        # Create temporary config
        config = {"temperature": 0.2, "system_prompt": "You are a test assistant."}

        # Add provider-specific configuration
        if provider in ["OpenAI", "Anthropic", "Google"]:
            if not api_key:
                return Div(
                    P(f"{provider} requires an API key", cls="text-red-500"),
                    cls="bg-red-50 p-4 rounded-lg",
                )
            config["api_key"] = api_key

        if provider in ["Google", "HuggingFace", "Other"] and base_url:
            config["base_url"] = base_url
        elif provider == "Ollama":
            if not base_url:
                return Div(
                    P("Ollama requires a server URL", cls="text-red-500"),
                    cls="bg-red-50 p-4 rounded-lg",
                )
            config["base_url"] = base_url

        # Test model ID based on provider
        test_models = {
            "OpenAI": "gpt-3.5-turbo",
            "Anthropic": "claude-3-haiku-20240307",
            "Google": "gemini-1.5-flash",
            "Ollama": "llama3",
            "HuggingFace": "microsoft/DialoGPT-small",
            "Other": "gpt-3.5-turbo",  # Assume OpenAI-compatible
        }

        model_id = test_models.get(provider, "gpt-3.5-turbo")

        # Try to test connection using litellm directly
        import litellm

        # Build the model string for litellm
        if provider == "OpenAI":
            model_string = model_id  # e.g., "gpt-3.5-turbo"
        elif provider == "Anthropic":
            model_string = model_id  # e.g., "claude-3-haiku-20240307"
        elif provider == "Google":
            model_string = (
                f"gemini/{model_id.replace('gemini-', '')}"  # e.g., "gemini/1.5-flash"
            )
        elif provider == "Ollama":
            # For Ollama, LiteLLM requires the provider prefix
            model_string = f"ollama/{model_id}"  # e.g., "ollama/llama3"
        elif provider == "HuggingFace":
            model_string = f"huggingface/{model_id}"  # e.g., "huggingface/microsoft/DialoGPT-small"
        else:
            model_string = model_id  # Assume OpenAI-compatible

        # Set up litellm parameters
        kwargs = {
            "model": model_string,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Connection successful' in exactly 3 words.",
                }
            ],
            "max_tokens": 10,
            "temperature": config.get("temperature", 0.2),
        }

        # Add API key if present
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]

        # Add base URL if present
        if config.get("base_url"):
            if provider == "Ollama":
                kwargs["api_base"] = config["base_url"]
            elif provider in ["Google", "HuggingFace", "Other"]:
                kwargs["base_url"] = config["base_url"]

        # Enable debugging for detailed error messages
        litellm.set_verbose = True

        # Test with a simple prompt
        try:
            response = litellm.completion(**kwargs)

            if response and response.choices:
                content = response.choices[0].message.content
                return Div(
                    P(
                        f"✅ {provider} connection successful!",
                        cls="text-green-600 font-medium",
                    ),
                    P(f"Response: {content}", cls="text-gray-600 text-sm mt-2"),
                    cls="bg-green-50 p-4 rounded-lg",
                )
            else:
                return Div(
                    P(
                        f"❌ {provider} connection failed - no response",
                        cls="text-red-500",
                    ),
                    cls="bg-red-50 p-4 rounded-lg",
                )

        except Exception as e:
            # Show full error details for debugging
            import traceback

            error_details = traceback.format_exc()

            return Div(
                P(f"❌ {provider} connection failed", cls="text-red-500 font-medium"),
                P(f"Error: {e!s}", cls="text-gray-600 text-sm mt-2"),
                P("Debug details:", cls="text-red-600 text-sm font-semibold mt-2"),
                Pre(
                    error_details,
                    cls="text-xs text-red-600 bg-red-100 p-2 rounded overflow-auto max-h-40 mt-1",
                ),
                cls="bg-red-50 p-4 rounded-lg",
            )

    except Exception as e:
        return Div(
            P(f"Error testing connection: {e!s}", cls="text-red-500"),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- Delete AI Model ---
@rt("/admin/ai-models/{id}")
@admin_required
def delete(session, id: int):
    try:
        # Find the model
        model_found = False
        model_name = None
        for m in ai_models():
            if m.id == id:
                model_found = True
                model_name = m.name
                break

        if not model_found:
            return "Model not found"

        # Delete the model
        ai_models.delete(id)

        # Delete related capabilities
        for cap in model_capabilities():
            if cap.model_id == id:
                model_capabilities.delete(cap.id)

        # Return deleted confirmation
        return Div(
            P(f"Model '{model_name}' deleted", cls="text-green-500 p-4"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        )
    except Exception as e:
        return f"Error deleting model: {e!s}"
