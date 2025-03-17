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
    
    return Container(
        # Header with navigation bar
        Header(
            Div(
                # Left side - Logo and name
                Div(
                    H1("FeedForward", cls="text-2xl font-bold"),
                    cls="flex items-center"
                ),
                # Right side - User info and logout
                Nav(
                    Span(user.email, cls="mr-4"),
                    Button("Logout", hx_post="/logout", cls="bg-red-500 text-white px-4 py-2 rounded-full hover:bg-red-600"),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-800 text-white p-4"
        ),
        
        # Dashboard content
        Div(
            H1("Admin Dashboard", cls="text-3xl font-bold mb-8"),
            P("Welcome, " + user.name, cls="text-lg mb-6"),
            
            # Admin actions
            Div(
                Div(
                    H2("User Management", cls="text-2xl font-bold"),
                    cls="mb-2"
                ),
                Div(
                    A("Approve Instructors", href="/admin/instructors/approve", 
                      cls="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 mr-3"),
                    A("Manage Users", href="/admin/users",
                      cls="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"),
                    cls="mb-8"
                ),
                
                # System configuration
                Div(
                    H2("System Configuration", cls="text-2xl font-bold"),
                    cls="mb-2"
                ),
                Div(
                    A("AI Models", href="/admin/ai-models",
                      cls="bg-purple-500 text-white px-4 py-2 rounded-md hover:bg-purple-600 mr-3"),
                    A("Feedback Settings", href="/admin/feedback-settings",
                      cls="bg-purple-500 text-white px-4 py-2 rounded-md hover:bg-purple-600"),
                    cls="mb-8"
                ),
                
                # Pending approvals
                Div(
                    H2("Pending Approvals", cls="text-2xl font-bold mb-4"),
                    P("No pending instructor approvals.", cls="text-gray-500 italic"),
                    cls="mb-8"
                ),
                
                cls="container mx-auto px-4 py-8"
            ),
            
            cls="container mx-auto px-4 py-8"
        ),
        
        # Footer
        Footer(
            Div(
                P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
                cls="container mx-auto text-center"
            ),
            cls="bg-gray-100 border-t border-gray-200 py-6"
        )
    )

# --- Approve Instructors Route ---
@rt('/admin/instructors/approve')
@admin_required
def get(session):
    # Get all instructors that need approval
    pending_instructors = []
    for user in users():
        if user.role == Role.INSTRUCTOR and not user.approved:
            pending_instructors.append(user)
    
    # Render the page
    return Container(
        # Header with navigation bar
        Header(
            Div(
                # Left side - Logo and name
                Div(
                    H1("FeedForward", cls="text-2xl font-bold"),
                    cls="flex items-center"
                ),
                # Right side - User info and logout
                Nav(
                    A("Dashboard", href="/admin/dashboard", cls="mr-4 text-blue-300 hover:text-white"),
                    Span(users[session['auth']].email, cls="mr-4"),
                    Button("Logout", hx_post="/logout", cls="bg-red-500 text-white px-4 py-2 rounded-full hover:bg-red-600"),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-800 text-white p-4"
        ),
        
        # Page content
        Div(
            H1("Approve Instructors", cls="text-3xl font-bold mb-8"),
            
            # Pending instructors table
            Div(
                H2("Pending Approval", cls="text-2xl font-bold mb-4"),
                
                # Table of pending instructors
                Table(
                    Thead(
                        Tr(
                            Th("Name", cls="py-2 px-4 text-left"),
                            Th("Email", cls="py-2 px-4 text-left"),
                            Th("Department", cls="py-2 px-4 text-left"),
                            Th("Actions", cls="py-2 px-4 text-left")
                        ),
                        cls="bg-gray-100"
                    ),
                    Tbody(
                        *(Tr(
                            Td(instructor.name, cls="py-2 px-4"),
                            Td(instructor.email, cls="py-2 px-4"),
                            Td(instructor.department or "Not specified", cls="py-2 px-4"),
                            Td(
                                Button("Approve", 
                                       cls="bg-green-500 text-white px-3 py-1 rounded mr-2 hover:bg-green-600",
                                       hx_post=f"/admin/instructors/approve/{instructor.email}",
                                       hx_swap="outerHTML"),
                                Button("Reject", 
                                       cls="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600",
                                       hx_post=f"/admin/instructors/reject/{instructor.email}",
                                       hx_swap="outerHTML"),
                                cls="py-2 px-4"
                            )
                        ) for instructor in pending_instructors) if pending_instructors else 
                        Tr(
                            Td("No pending approvals", colspan="4", cls="py-4 px-4 text-center text-gray-500 italic")
                        )
                    ),
                    cls="w-full border-collapse"
                ),
                
                cls="mb-8"
            ),
            
            # Back button
            A("Back to Dashboard", href="/admin/dashboard", 
              cls="inline-block mt-4 text-blue-500 hover:underline"),
            
            cls="container mx-auto px-4 py-8"
        ),
        
        # Footer
        Footer(
            Div(
                P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
                cls="container mx-auto text-center"
            ),
            cls="bg-gray-100 border-t border-gray-200 py-6"
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