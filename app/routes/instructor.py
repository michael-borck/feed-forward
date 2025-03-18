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
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Welcome, " + user.name, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P("Instructor Account", cls="text-gray-600 mb-4"),
            Div(
                Div(
                    "3", 
                    cls="text-indigo-700 font-bold"
                ),
                P("Active Courses", cls="text-gray-600"),
                cls="flex items-center space-x-2 mb-2"
            ),
            Div(
                Div(
                    "12", 
                    cls="text-indigo-700 font-bold"
                ),
                P("Pending Reviews", cls="text-gray-600"),
                cls="flex items-center space-x-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Quick Actions
        Div(
            H3("Quick Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Create New Course", color="indigo", href="/instructor/courses/new", icon="+"),
                action_button("Import Students", color="teal", href="/instructor/students/import", icon="↑"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content
    main_content = Div(
        # Analytics summary
        Div(
            Div(
                # Course card
                card(
                    Div(
                        H3("3", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Active Courses", cls="text-gray-600"),
                        P("Last updated today", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Students card
                card(
                    Div(
                        H3("48", cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Total Students", cls="text-gray-600"),
                        P("Across all courses", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Feedback card
                card(
                    Div(
                        H3("87%", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Feedback Engagement", cls="text-gray-600"),
                        P("↑ 12% from last month", cls="text-xs text-green-600 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            ),
            
            # Course list
            Div(
                Div(
                    H2("Your Courses", cls="text-2xl font-bold text-indigo-900"),
                    action_button("Create New Course", color="indigo", href="/instructor/courses/new", icon="+", size="small"),
                    cls="flex justify-between items-center mb-6"
                ),
                
                P("You haven't created any courses yet.", cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
                
                cls="mb-8"
            ),
            
            # Recent submissions
            Div(
                H2("Recent Submissions", cls="text-2xl font-bold text-indigo-900 mb-6"),
                
                P("No recent submissions to review.", cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
                
                cls="mb-8"
            ),
        )
    )
    
    # Use the dashboard layout with our components
    from app.utils.ui import dashboard_layout
    return Titled(
        "Instructor Dashboard | FeedForward",
        dashboard_layout(
            "Instructor Dashboard", 
            sidebar_content, 
            main_content, 
            user_role=Role.INSTRUCTOR
        )
    )