"""
Admin dashboard routes
"""

from fasthtml import common as fh

from app import admin_required, rt
from app.models.user import Role, users
from app.utils.ui import action_button, card, dashboard_layout


@rt("/admin/dashboard")
@admin_required
def admin_dashboard(session):
    """Admin dashboard view"""
    # Get current user
    user = users[session["auth"]]

    # Sidebar content
    sidebar_content = fh.Div(
        # User welcome card
        fh.Div(
            fh.H3(
                "Welcome, " + user.name,
                cls="text-xl font-semibold text-indigo-900 mb-2",
            ),
            fh.P("Admin Account", cls="text-gray-600 mb-4"),
            fh.Div(
                # System stats summary
                fh.Div(
                    fh.Div("3", cls="text-indigo-700 font-bold"),
                    fh.P("Total Users", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2",
                ),
                # Pending approvals summary
                fh.Div(
                    fh.Div("0", cls="text-indigo-700 font-bold"),
                    fh.P("Pending Approvals", cls="text-gray-600"),
                    cls="flex items-center space-x-2",
                ),
                cls="space-y-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Quick actions section
        fh.Div(
            fh.H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
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
    main_content = fh.Div(
        # System stats
        fh.Div(
            fh.Div(
                # Users card
                card(
                    fh.Div(
                        fh.H3("3", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        fh.P("Total Users", cls="text-gray-600"),
                        fh.P("Last updated today", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Courses card
                card(
                    fh.Div(
                        fh.H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        fh.P("Active Courses", cls="text-gray-600"),
                        fh.P("Across all instructors", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # System health card
                card(
                    fh.Div(
                        fh.H3("100%", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        fh.P("System Health", cls="text-gray-600"),
                        fh.P(
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
        fh.Div(
            fh.H2("User Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
            fh.Div(
                fh.Div(
                    fh.H3(
                        "Instructor Approval",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    fh.P("No pending instructor approvals.", cls="text-gray-500 italic"),
                    fh.Div(
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
                fh.Div(
                    fh.H3(
                        "Recent Users", cls="text-lg font-semibold text-indigo-800 mb-4"
                    ),
                    fh.P("3 users registered in the system.", cls="text-gray-600 mb-2"),
                    fh.Div(
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
        fh.Div(
            fh.H2("System Configuration", cls="text-2xl font-bold text-indigo-900 mb-6"),
            fh.Div(
                fh.Div(
                    fh.H3("AI Models", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    fh.P(
                        "Configure the AI models used for feedback generation.",
                        cls="text-gray-600 mb-2",
                    ),
                    fh.Div(
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
                fh.Div(
                    fh.H3(
                        "Feedback Settings",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    fh.P(
                        "Adjust global feedback settings and templates.",
                        cls="text-gray-600 mb-2",
                    ),
                    fh.Div(
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
    return fh.Titled(
        "Admin Dashboard | FeedForward",
        dashboard_layout(
            "Admin Dashboard", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )
