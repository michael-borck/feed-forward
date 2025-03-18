"""
Student routes - dashboard, assignment submission, feedback viewing, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment
from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.feedback import AIModel, Draft, ModelRun, CategoryScore, FeedbackItem, AggregatedFeedback

from app import app, rt, student_required

# --- Student Dashboard ---
@rt('/student/dashboard')
@student_required
def get(session):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, feedback_card
    
    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3("Welcome, " + user.name, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P("Student Account", cls="text-gray-600 mb-4"),
            Div(
                # Active assignments summary
                Div(
                    Div(
                        "0", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Active Assignments", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                # Recent feedback summary
                Div(
                    Div(
                        "0", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Recent Feedback", cls="text-gray-600"),
                    cls="flex items-center space-x-2"
                ),
                cls="space-y-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Active assignments section
        Div(
            H3("Active Assignments", cls="font-semibold text-indigo-900 mb-4"),
            P("You have no active assignments.", cls="text-gray-500 italic text-sm"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content
    main_content = Div(
        # Progress summary
        Div(
            Div(
                # Courses card
                card(
                    Div(
                        H3("0", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Enrolled Courses", cls="text-gray-600"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Completed assignments card
                card(
                    Div(
                        H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Completed Assignments", cls="text-gray-600"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Overall progress card
                card(
                    Div(
                        H3("N/A", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Overall Progress", cls="text-gray-600"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            )
        ),
        
        # Courses section
        Div(
            H2("Your Courses", cls="text-2xl font-bold text-indigo-900 mb-6"),
            P("You are not enrolled in any courses yet.", 
              cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
            cls="mb-8"
        ),
        
        # Upcoming assignments section
        Div(
            H2("Upcoming Assignments", cls="text-2xl font-bold text-indigo-900 mb-6"),
            P("No upcoming assignments.", 
              cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
            cls="mb-8"
        ),
        
        # Recent feedback section
        Div(
            H2("Recent Feedback", cls="text-2xl font-bold text-indigo-900 mb-6"),
            P("No recent feedback.", 
              cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
            cls="mb-8"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Student Dashboard | FeedForward",
        dashboard_layout(
            "Student Dashboard", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT
        )
    )