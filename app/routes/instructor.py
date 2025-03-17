"""
Instructor routes - dashboard, course management, assignment creation, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment
from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.feedback import AIModel, Draft, ModelRun, CategoryScore, FeedbackItem, AggregatedFeedback
from app.models.config import SystemConfig, AggregationMethod, FeedbackStyle, MarkDisplayOption, AssignmentSettings

from app import app, rt, instructor_required

# --- Instructor Dashboard ---
@rt('/instructor/dashboard')
@instructor_required
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
            H1("Instructor Dashboard", cls="text-3xl font-bold mb-8"),
            P("Welcome, " + user.name, cls="text-lg mb-6"),
            
            # Action buttons
            Div(
                A("Create New Course", href="/instructor/courses/new", 
                  cls="bg-blue-500 text-white px-6 py-3 rounded-md hover:bg-blue-600 mr-4"),
                A("Add Students", href="/instructor/students/import",
                  cls="bg-green-500 text-white px-6 py-3 rounded-md hover:bg-green-600"),
                cls="mb-8"
            ),
            
            # Placeholder for course list
            Div(
                Div(
                    H2("Your Courses", cls="text-2xl font-bold"),
                    A("Create New Course", href="/instructor/courses/new", 
                      cls="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 text-sm"),
                    cls="flex justify-between items-center mb-4"
                ),
                P("You haven't created any courses yet.", cls="text-gray-500 italic"),
                cls="mb-8"
            ),
            
            # Placeholder for recent submissions
            Div(
                H2("Recent Submissions", cls="text-2xl font-bold mb-4"),
                P("No recent submissions to review.", cls="text-gray-500 italic"),
                cls="mb-8"
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