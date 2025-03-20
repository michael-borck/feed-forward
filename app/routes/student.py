"""
Student routes - dashboard, assignment submission, feedback viewing, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse
from datetime import datetime

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.feedback import AIModel, Draft, ModelRun, CategoryScore, FeedbackItem, AggregatedFeedback
from app.utils.auth import get_password_hash, verify_password, is_strong_password
from app.utils.email import APP_DOMAIN

from app import app, rt, student_required

# --- Student Join Route (from invitation) ---
@rt('/student/join')
def get(token: str):
    # Import UI components
    from app.utils.ui import page_container
    
    # Check if token is valid
    found_user = None
    for user in users():
        if user.verification_token == token and user.role == Role.STUDENT:
            found_user = user
            break
    
    if not found_user:
        # Invalid token
        error_content = Div(
            Div(
                Div(
                    # Error icon
                    Div(
                        Span("❌", cls="text-5xl block mb-4"),
                        cls="text-center"
                    ),
                    # Brand logo
                    Div(
                        Span("Feed", cls="text-indigo-600 font-bold"),
                        Span("Forward", cls="text-teal-500 font-bold"),
                        cls="text-3xl mb-4 text-center"
                    ),
                    H1("Invalid Invitation Link", cls="text-2xl font-bold text-indigo-900 mb-4 text-center"),
                    P("The invitation link is invalid or has expired.", cls="text-gray-600 mb-6 text-center"),
                    Div(
                        A("Return to Home", href="/", 
                          cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="text-center"
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 max-w-md w-full"
            ),
            cls="flex justify-center items-center py-16 px-4"
        )
        
        return page_container("Invalid Invitation - FeedForward", error_content)
    
    # Valid token, show registration form
    registration_content = Div(
        Div(
            # Brand logo on registration form
            Div(
                Span("Feed", cls="text-indigo-600 font-bold"),
                Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center"
            ),
            H1("Complete Your Registration", cls="text-2xl font-bold text-indigo-900 mb-6 text-center"),
            Div(
                Form(
                    Input(type="hidden", id="token", value=token),
                    Input(type="hidden", id="email", value=found_user.email),
                    
                    Div(
                        Label("Email", for_="display_email", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="display_email", type="email", value=found_user.email, disabled=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg bg-gray-100"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Name", for_="name", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="name", type="text", placeholder="Your full name", required=True, 
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Password", for_="password", cls="block text-indigo-900 font-medium mb-1"),
                        P("At least 8 characters with uppercase, lowercase, number, and special character", 
                          cls="text-sm text-gray-500 mb-1"),
                        Input(id="password", type="password", placeholder="Create a password", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Confirm Password", for_="confirm_password", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="confirm_password", type="password", placeholder="Confirm your password", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6"
                    ),
                    Div(
                        Button("Complete Registration", type="submit", cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/student/join",
                    hx_target="#error",
                    cls="w-full"
                ),
                cls="w-full max-w-md"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
    )
    
    return page_container("Complete Registration - FeedForward", registration_content)

@rt('/student/join')
def post(session, token: str, email: str, name: str, password: str, confirm_password: str):
    # Validate inputs
    if not name or not password or not confirm_password:
        return "All fields are required"
    
    if password != confirm_password:
        return "Passwords do not match"
    
    if not is_strong_password(password):
        return "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
    
    # Find user with matching token
    try:
        user = users[email]
        if user.verification_token != token or user.role != Role.STUDENT:
            return "Invalid registration token"
            
        # Update user information
        user.name = name
        user.password = get_password_hash(password)
        user.verified = True
        user.verification_token = ""  # Clear the token
        users.update(user)
        
        # Update enrollment status if there's a status field
        # Note: The current schema doesn't have these fields, but this
        # is a placeholder for when they are added
        try:
            now = datetime.now().isoformat()
            for enrollment in enrollments():
                if enrollment.student_email == email:
                    if hasattr(enrollment, 'status') and enrollment.status == "pending":
                        enrollment.status = "active"
                    if hasattr(enrollment, 'date_enrolled') and not enrollment.date_enrolled:
                        enrollment.date_enrolled = now
                    if hasattr(enrollment, 'last_access'):
                        enrollment.last_access = now
                    enrollments.update(enrollment)
        except Exception as e:
            print(f"Note: Could not update enrollment status: {str(e)}")
        
        # Log the user in
        session['auth'] = user.email
        
        # Redirect to the student dashboard
        return HttpHeader('HX-Redirect', '/student/dashboard')
    except Exception as e:
        print(f"Error in student join: {str(e)}")
        return "Invalid registration request"

# --- Student Dashboard ---
@rt('/student/dashboard')
@student_required
def get(session):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, feedback_card
    
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
    
    # Debug print
    print(f"Student {user.email} has {len(student_enrollments)} enrollments and {len(enrolled_courses)} courses")
    for course in enrolled_courses:
        print(f"  Enrolled in: {course.title} ({course.code})")
    
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
                        str(len(enrolled_courses)), 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Enrolled Courses", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                # Recent feedback summary
                Div(
                    Div(
                        "0", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Pending Assignments", cls="text-gray-600"),
                    cls="flex items-center space-x-2"
                ),
                cls="space-y-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Active courses section
        Div(
            H3("Your Courses", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                *(Div(
                    A(course.title, 
                      href=f"/student/courses/{course.id}",
                      cls="font-medium text-indigo-700 hover:underline"),
                    cls="mb-2"
                ) for course in enrolled_courses)
            ) if enrolled_courses else 
            P("You are not enrolled in any courses yet.", cls="text-gray-500 italic text-sm"),
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
                        H3(str(len(enrolled_courses)), cls="text-4xl font-bold text-indigo-700 mb-2"),
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
            (Div(
                *(Div(
                    Div(
                        H3(course.title, cls="text-xl font-bold text-indigo-800 mb-1"),
                        P(f"Code: {course.code}", cls="text-gray-600 mb-1"),
                        P(f"Term: {course.term}", cls="text-gray-600 mb-1"),
                        Div(
                            Span(course.status.capitalize(), 
                                cls="px-3 py-1 rounded-full text-sm " + 
                                ("bg-green-100 text-green-800" if course.status == "active" else 
                                "bg-gray-100 text-gray-800")),
                            cls="mt-2"
                        ),
                        cls="flex-1"
                    ),
                    Div(
                        Div(
                            action_button("View Course", color="indigo", 
                                        href=f"/student/courses/{course.id}", 
                                        size="small"),
                            action_button("Assignments", color="teal", 
                                        href=f"/student/courses/{course.id}/assignments", 
                                        size="small"),
                            cls="space-y-2"
                        ),
                        cls="ml-auto"
                    ),
                    cls="flex justify-between items-start bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ) for course in enrolled_courses)
            )) if enrolled_courses else
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