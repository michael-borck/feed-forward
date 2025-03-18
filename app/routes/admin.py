"""
Admin routes - user management, system configuration, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment
from app.models.feedback import AIModel
from app.models.config import SystemConfig, AggregationMethod, FeedbackStyle, MarkDisplayOption

from app import app, rt, admin_required

# --- Admin Dashboard ---
@rt('/admin/dashboard')
@admin_required
def get(session):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button
    
    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3("Welcome, " + user.name, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P("Admin Account", cls="text-gray-600 mb-4"),
            Div(
                # System stats summary
                Div(
                    Div(
                        "3", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Total Users", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                # Pending approvals summary
                Div(
                    Div(
                        "0", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Pending Approvals", cls="text-gray-600"),
                    cls="flex items-center space-x-2"
                ),
                cls="space-y-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Quick actions section
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Approve Instructors", color="indigo", href="/admin/instructors/approve", icon="✓"),
                action_button("Manage Users", color="teal", href="/admin/users", icon="👥"),
                action_button("System Settings", color="indigo", href="/admin/settings", icon="⚙️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
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
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Courses card
                card(
                    Div(
                        H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Active Courses", cls="text-gray-600"),
                        P("Across all instructors", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # System health card
                card(
                    Div(
                        H3("100%", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("System Health", cls="text-gray-600"),
                        P("All services operational", cls="text-xs text-green-600 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            )
        ),
        
        # User Management
        Div(
            H2("User Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3("Instructor Approval", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("No pending instructor approvals.", cls="text-gray-500 italic"),
                    Div(
                        action_button("View All", color="indigo", href="/admin/instructors/approve", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ),
                Div(
                    H3("Recent Users", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("3 users registered in the system.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Manage Users", color="teal", href="/admin/users", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                cls="mb-8"
            )
        ),
        
        # System Configuration
        Div(
            H2("System Configuration", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3("AI Models", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("Configure the AI models used for feedback generation.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Configure Models", color="indigo", href="/admin/ai-models", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ),
                Div(
                    H3("Feedback Settings", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("Adjust global feedback settings and templates.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Adjust Settings", color="teal", href="/admin/feedback-settings", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                cls="mb-8"
            )
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Admin Dashboard | FeedForward",
        dashboard_layout(
            "Admin Dashboard", 
            sidebar_content, 
            main_content, 
            user_role=Role.ADMIN
        )
    )

# --- Approve Instructors Route ---
@rt('/admin/instructors/approve')
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session['auth']]
    from app.utils.ui import dashboard_layout, card, action_button, data_table
    
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
                A("← Dashboard", href="/admin/dashboard", 
                  cls="text-indigo-600 font-medium hover:text-indigo-800 transition-colors"),
                cls="mb-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Admin actions
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Manage Users", color="teal", href="/admin/users", icon="👥"),
                action_button("System Settings", color="indigo", href="/admin/settings", icon="⚙️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
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
                (Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Name", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Email", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Department", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                            ),
                            cls="bg-indigo-50"
                        ),
                        Tbody(
                            *(Tr(
                                Td(instructor.name, cls="py-4 px-6"),
                                Td(instructor.email, cls="py-4 px-6"),
                                Td(instructor.department or "Not specified", cls="py-4 px-6"),
                                Td(
                                    Div(
                                        Button("Approve", 
                                               cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                               hx_post=f"/admin/instructors/approve/{instructor.email}",
                                               hx_swap="outerHTML"),
                                        Button("Reject", 
                                               cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                               hx_post=f"/admin/instructors/reject/{instructor.email}",
                                               hx_swap="outerHTML"),
                                        cls="flex"
                                    ),
                                    cls="py-4 px-6"
                                )
                            ) for instructor in pending_instructors)
                        ),
                        cls="w-full"
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
                )) if pending_instructors else 
                Div(
                    P("No pending instructor approvals at this time.", 
                      cls="text-gray-500 italic text-center py-8"),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full"
                ),
                Div(cls="mb-8")
            )
        ),
        
        # Back button
        Div(
            A("← Back to Dashboard", href="/admin/dashboard", 
              cls="text-indigo-600 font-medium hover:text-indigo-800 transition-colors"),
            cls="mt-4"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Approve Instructors | FeedForward",
        dashboard_layout(
            "Approve Instructors", 
            sidebar_content, 
            main_content, 
            user_role=Role.ADMIN
        )
    )

# --- Approve Instructor API ---
@rt('/admin/instructors/approve/{email}')
@admin_required
def post(session, email: str):
    try:
        # Get the instructor
        instructor = users[email]
        
        # Update approval status
        instructor.approved = True
        users.update(instructor)
        
        # Return success message
        return Div(
            P("Approved successfully", cls="text-green-500"),
            cls="py-2 px-4"
        )
    except:
        # Return error message
        return Div(
            P("Error approving instructor", cls="text-red-500"),
            cls="py-2 px-4"
        )

# --- Reject Instructor API ---
@rt('/admin/instructors/reject/{email}')
@admin_required
def post(session, email: str):
    try:
        # Get the instructor and delete
        users.delete(email)
        
        # Return success message
        return Div(
            P("Rejected and removed", cls="text-green-500"),
            cls="py-2 px-4"
        )
    except:
        # Return error message
        return Div(
            P("Error rejecting instructor", cls="text-red-500"),
            cls="py-2 px-4"
        )