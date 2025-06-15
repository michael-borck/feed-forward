"""
Student routes - dashboard, assignment submission, feedback viewing, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse
from starlette.datastructures import UploadFile
from datetime import datetime
import os
import aiofiles
from pathlib import Path

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.feedback import AIModel, Draft, ModelRun, CategoryScore, FeedbackItem, AggregatedFeedback
from app.utils.auth import get_password_hash, verify_password, is_strong_password
from app.utils.email import APP_DOMAIN
from app.utils.file_handlers import extract_file_content, validate_file_size

from app import app, rt, student_required

# --- API Endpoints ---
@rt('/api/feedback-status/{draft_id}')
@student_required
def get(session, draft_id: int):
    """Check the status of feedback generation for a draft"""
    from app.services.background_tasks import get_task_status
    
    # Get current user
    user = users[session['auth']]
    
    # Verify the draft belongs to the student
    try:
        draft = drafts[draft_id]
        if draft.student_email != user.email:
            return {"error": "Unauthorized"}
    except:
        return {"error": "Draft not found"}
    
    # Get task status
    task_status = get_task_status(draft_id)
    
    return {
        "draft_id": draft_id,
        "draft_status": draft.status,
        "task_status": task_status or "not_queued"
    }

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
                        Div(
                            Input(id="tos_accepted", type="checkbox", required=True, 
                                  cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label(
                                Span("I agree to the ", cls="ml-2 text-gray-700"),
                                A("Terms of Service", href="/terms-of-service", target="_blank", 
                                  cls="text-indigo-600 hover:underline"),
                                for_="tos_accepted", cls="flex items-center"
                            ),
                            cls="flex items-start"
                        ),
                        cls="mb-4"
                    ),
                    Div(
                        Div(
                            Input(id="privacy_accepted", type="checkbox", required=True,
                                  cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label(
                                Span("I agree to the ", cls="ml-2 text-gray-700"),
                                A("Privacy Policy", href="/privacy-policy", target="_blank",
                                  cls="text-indigo-600 hover:underline"),
                                for_="privacy_accepted", cls="flex items-center"
                            ),
                            cls="flex items-start"
                        ),
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
def post(session, token: str, email: str, name: str, password: str, confirm_password: str, tos_accepted: bool = False, privacy_accepted: bool = False):
    # Validate inputs
    if not name or not password or not confirm_password:
        return "All fields are required"
    
    # Check ToS and Privacy acceptance
    if not tos_accepted or not privacy_accepted:
        return "You must accept the Terms of Service and Privacy Policy to create an account"
    
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
        user.tos_accepted = True
        user.privacy_accepted = True
        user.acceptance_date = datetime.now().isoformat()
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

# Helper Functions for Student Routes

# Function to generate assignment sidebar for student dashboard
def generate_recent_feedback(student_drafts):
    """Generate the recent feedback section for student dashboard"""
    from fasthtml.common import Div, H2, P
    from app.utils.ui import feedback_card
    from datetime import datetime
    
    # Filter out hidden drafts
    visible_drafts = [draft for draft in student_drafts if not (hasattr(draft, 'hidden_by_student') and draft.hidden_by_student)]
    
    # Main content
    if not visible_drafts:
        return Div(
            H2("Recent Feedback", cls="text-2xl font-bold text-indigo-900 mb-6"),
            P("No recent feedback.", 
              cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
            cls="mb-8"
        )
    
    # Sort drafts by submission date, get 2 most recent
    recent_drafts = sorted(visible_drafts, key=lambda d: d.submission_date, reverse=True)[:2]
    
    # Create feedback cards
    feedback_items = []
    for draft in recent_drafts:
        feedback_items.append(
            Div(
                feedback_card(
                    f"Feedback on Assignment {draft.assignment_id} - Draft {draft.version}",
                    Div(
                        P("No feedback available yet. Your submission is being processed.", 
                          cls="text-gray-600 italic"),
                        cls="py-2"
                    ),
                    color="teal"
                )
            )
        )
    
    return Div(
        H2("Recent Feedback", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(*feedback_items),
        cls="mb-8"
    )
def generate_assignments_sidebar(student_assignments, student_drafts):
    """Generate the assignments sidebar component for student dashboard"""
    from fasthtml.common import Div, H3, P, A, H4
    from app.utils.ui import status_badge
    
    if not student_assignments:
        return Div(
            H3("Active Assignments", cls="font-semibold text-indigo-900 mb-4"),
            P("No active assignments.", cls="text-gray-500 italic text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    
    # Filter out hidden drafts when counting
    visible_drafts = [d for d in student_drafts if not (hasattr(d, 'hidden_by_student') and d.hidden_by_student)]
    
    # Create assignment items
    assignment_items = []
    for assignment_data in student_assignments[:3]:  # Show only 3 most recent
        assignment_items.append(
            Div(
                Div(
                    Div(
                        Div(
                            H4(assignment_data['assignment'].title, 
                               cls="font-medium text-indigo-700"),
                            P(f"{assignment_data['course'].code}: {assignment_data['course'].title}", 
                              cls="text-xs text-gray-500"),
                            cls="flex-1"
                        ),
                        Div(
                            # Calculate draft count for this assignment (both visible and hidden)
                            status_badge(
                                f"Draft {sum(1 for d in student_drafts if d.assignment_id == assignment_data['assignment'].id)}/{assignment_data['assignment'].max_drafts}", 
                                "blue"
                            ),
                            cls=""
                        ),
                        cls="flex justify-between items-start"
                    ),
                    P(f"Due: {assignment_data['assignment'].due_date}", 
                      cls="text-xs text-gray-500 mt-1"),
                    cls="p-3"
                ),
                cls="bg-white border border-gray-200 rounded-md mb-2 hover:border-indigo-300 transition-colors"
            )
        )
    
    # Create the full sidebar component
    return Div(
        H3("Active Assignments", cls="font-semibold text-indigo-900 mb-4"),
        Div(*assignment_items),
        A("View All Assignments", 
          href="/student/assignments",
          cls="text-sm text-indigo-600 hover:underline block mt-2"),
        cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
    )

# Helper Function to Get Assignment with Permission Check
def get_student_assignment(assignment_id, student_email):
    """
    Verify that the student is enrolled in the course containing the assignment.
    Returns (assignment, course, error_message) tuple.
    """
    from app.models.assignment import assignments
    
    # Find the assignment
    target_assignment = None
    for assignment in assignments():
        if assignment.id == assignment_id:
            target_assignment = assignment
            break
            
    if not target_assignment:
        return None, None, "Assignment not found"
    
    # Check if student is enrolled in the course
    course_id = target_assignment.course_id
    
    # Use the course helper to verify enrollment
    course, error = get_student_course(course_id, student_email)
    if error:
        return None, None, error
        
    return target_assignment, course, None

# Helper Function to Get Course with Permission Check
def get_student_course(course_id, student_email):
    """
    Verify that the student is enrolled in the course and return the course.
    Returns (course, error_message) tuple.
    """
    # Find the course
    target_course = None
    try:
        # Get all courses to find the one with matching ID
        for course in courses():
            if course.id == course_id:
                target_course = course
                break
                
        if not target_course:
            return None, "Course not found"
            
        # Check if student is enrolled
        is_enrolled = False
        for enrollment in enrollments():
            if enrollment.course_id == course_id and enrollment.student_email == student_email:
                is_enrolled = True
                break
                
        if not is_enrolled:
            return None, "You are not enrolled in this course"
            
        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {str(e)}"

# --- Student Dashboard ---
@rt('/student/dashboard')
@student_required
def get(session, request):
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
    
    # Get all assignments for the enrolled courses
    from app.models.assignment import Assignment, assignments
    student_assignments = []
    
    for course in enrolled_courses:
        for assignment in assignments():
            if assignment.course_id == course.id and assignment.status == 'active':
                # Add course info to assignment
                assignment_with_course = {
                    'assignment': assignment,
                    'course': course
                }
                student_assignments.append(assignment_with_course)
    
    # Get student drafts
    from app.models.feedback import Draft, drafts
    student_drafts = []
    
    for draft in drafts():
        if draft.student_email == user.email:
            student_drafts.append(draft)
    
    # Count pending assignments (active assignments where max drafts > current draft count)
    pending_assignments = 0
    for assignment_data in student_assignments:
        assignment = assignment_data['assignment']
        draft_count = sum(1 for d in student_drafts if d.assignment_id == assignment.id)
        if draft_count < assignment.max_drafts:
            pending_assignments += 1
    
    # Create each part of the sidebar separately
    welcome_card = Div(
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
            # Pending assignments summary
            Div(
                Div(
                    str(pending_assignments), 
                    cls="text-indigo-700 font-bold"
                ),
                P("Pending Assignments", cls="text-gray-600"),
                cls="flex items-center space-x-2"
            ),
            cls="space-y-2"
        ),
        cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
    )
    
    # Active courses section
    courses_card = Div(
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
    
    # Assignments section from helper function
    assignments_card = generate_assignments_sidebar(student_assignments, student_drafts)
    
    # Combine all sidebar components
    sidebar_content = Div(
        welcome_card,
        courses_card,
        assignments_card
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
                # Active assignments card
                card(
                    Div(
                        H3(str(len(student_assignments)), cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Active Assignments", cls="text-gray-600"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Completed drafts card
                card(
                    Div(
                        H3(str(len(student_drafts)), cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Submitted Drafts", cls="text-gray-600"),
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
                        P(f"Term: {getattr(course, 'term', 'Current')}", cls="text-gray-600 mb-1"),
                        Div(
                            Span(getattr(course, 'status', 'active').capitalize(), 
                                cls="px-3 py-1 rounded-full text-sm " + 
                                ("bg-green-100 text-green-800" if getattr(course, 'status', 'active') == "active" else 
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
            Div(
                *(Div(
                    Div(
                        Div(
                            H3(assignment_data['assignment'].title, cls="text-xl font-bold text-indigo-800 mb-1"),
                            P(f"Course: {assignment_data['course'].title} ({assignment_data['course'].code})", 
                              cls="text-gray-600 mb-1"),
                            P(f"Due: {assignment_data['assignment'].due_date}", 
                              cls="text-gray-600 mb-2"),
                            # Calculate current drafts
                            Div(
                                P(f"Drafts: {sum(1 for d in student_drafts if d.assignment_id == assignment_data['assignment'].id)}/{assignment_data['assignment'].max_drafts}", 
                                  cls="text-sm text-gray-600"),
                                cls="mb-3"
                            ),
                            cls="flex-1"
                        ),
                        Div(
                            action_button("View Assignment", color="indigo", 
                                        href=f"/student/assignments/{assignment_data['assignment'].id}", 
                                        size="small"),
                            action_button("Submit Draft", color="teal", 
                                        href=f"/student/assignments/{assignment_data['assignment'].id}/submit", 
                                        size="small"),
                            cls="space-y-2"
                        ),
                        cls="flex flex-col md:flex-row md:justify-between items-start md:items-center gap-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ) for assignment_data in student_assignments)
            ) if student_assignments else
            P("No upcoming assignments.", 
              cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center"),
            cls="mb-8"
        ),
        
        # Recent feedback section using helper function
        generate_recent_feedback(student_drafts)
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Student Dashboard | FeedForward",
        dashboard_layout(
            "Student Dashboard", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"
        )
    )

# --- Student Course View ---
@rt('/student/courses/{course_id}')
@student_required
def get(session, request, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, feedback_card
    
    # Verify course and enrollment
    course, error = get_student_course(course_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/student/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get assignments for this course
    from app.models.assignment import Assignment, assignments
    course_assignments = []
    
    for assignment in assignments():
        if assignment.course_id == course_id and assignment.status == 'active':
            course_assignments.append(assignment)
    
    # Get student drafts for these assignments
    from app.models.feedback import Draft, drafts
    student_drafts = []
    
    for draft in drafts():
        if draft.student_email == user.email:
            for assignment in course_assignments:
                if draft.assignment_id == assignment.id:
                    student_drafts.append(draft)
    
    # Sidebar content
    sidebar_content = Div(
        # Course info card
        Div(
            H3(course.title, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course Code: {course.code}", cls="text-gray-600 mb-1"),
            P(f"Term: {getattr(course, 'term', 'Current')}", cls="text-gray-600 mb-1"),
            P(f"Status: {getattr(course, 'status', 'active').capitalize()}", cls="text-gray-600 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/student/dashboard", icon="←"),
                action_button("View Assignments", color="indigo", 
                            href=f"/student/courses/{course_id}/assignments"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Course stats
        Div(
            H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Assignments: {len(course_assignments)}", cls="text-gray-600 mb-2"),
            P(f"Submitted Drafts: {len(student_drafts)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
    )
    
    # Main content
    main_content = Div(
        H2(f"Course: {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        
        # Assignments section
        Div(
            H3("Active Assignments", cls="text-xl font-bold text-indigo-900 mb-4"),
            (Div(
                *(Div(
                    Div(
                        Div(
                            H4(assignment.title, cls="text-lg font-semibold text-indigo-800 mb-1"),
                            P(f"Due: {assignment.due_date}", cls="text-gray-600 mb-2"),
                            Div(
                                P(f"Drafts: {sum(1 for d in student_drafts if d.assignment_id == assignment.id)}/{assignment.max_drafts}", 
                                  cls="text-sm text-gray-600 mb-1"),
                                # Get the last draft status if exists
                                Div(
                                    status_badge(
                                        next((d.status.capitalize() for d in sorted(
                                            [d for d in student_drafts if d.assignment_id == assignment.id],
                                            key=lambda x: x.version, 
                                            reverse=True)), "Not Started"),
                                        "green" if any(d.status == "feedback_ready" for d in student_drafts if d.assignment_id == assignment.id) else
                                        "yellow" if any(d.status == "processing" for d in student_drafts if d.assignment_id == assignment.id) else
                                        "blue" if any(d.status == "submitted" for d in student_drafts if d.assignment_id == assignment.id) else
                                        "gray"
                                    ),
                                    cls="mt-1"
                                ),
                                cls=""
                            ),
                            cls="flex-1"
                        ),
                        Div(
                            action_button("View Assignment", color="indigo", 
                                        href=f"/student/assignments/{assignment.id}", 
                                        size="small"),
                            action_button("Submit Draft", color="teal", 
                                        href=f"/student/assignments/{assignment.id}/submit", 
                                        size="small"),
                            cls="flex flex-col gap-3"
                        ),
                        cls="flex flex-col md:flex-row justify-between"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4 hover:shadow-lg transition-shadow"
                ) for assignment in course_assignments)
            )) if course_assignments else
            P("No active assignments in this course.", 
              cls="text-gray-500 italic p-4 bg-white rounded-xl border border-gray-200"),
            cls="mb-8"
        ),
        
        # Recent activity for this course
        Div(
            H3("Recent Activity", cls="text-xl font-bold text-indigo-900 mb-4"),
            (Div(
                *(Div(
                    Div(
                        P(f"Draft {draft.version} submitted for " + 
                          next((a.title for a in course_assignments if a.id == draft.assignment_id), "Assignment"),
                          cls="text-indigo-800 font-medium"),
                        P(f"Submission Date: {draft.submission_date}", cls="text-sm text-gray-500"),
                        P(f"Status: {draft.status.replace('_', ' ').capitalize()}", cls="text-sm text-gray-600 mt-1"),
                        cls="p-4 border-l-4 border-indigo-500 bg-white rounded-r-lg shadow-sm mb-3"
                    )
                ) for draft in sorted(student_drafts, key=lambda d: d.submission_date, reverse=True)[:5])
            )) if student_drafts else
            P("No activity recorded for this course yet.", 
              cls="text-gray-500 italic p-4 bg-white rounded-xl border border-gray-200"),
            cls="mb-6"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        f"{course.title} | FeedForward",
        dashboard_layout(
            f"Course: {course.title}", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard highlighted in nav
        )
    )

# --- Student Assignment View ---
@rt('/student/assignments/{assignment_id}')
@student_required
def get(session, request, assignment_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, feedback_card, tabs
    
    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/student/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get rubric information
    from app.models.assignment import Rubric, RubricCategory, rubrics, rubric_categories
    assignment_rubric = None
    rubric_cats = []
    
    # Find the rubric for this assignment
    for rubric in rubrics():
        if rubric.assignment_id == assignment_id:
            assignment_rubric = rubric
            break
    
    # Get the rubric categories if the rubric exists
    if assignment_rubric:
        for category in rubric_categories():
            if category.rubric_id == assignment_rubric.id:
                rubric_cats.append(category)
    
    # Get drafts for this assignment
    from app.models.feedback import Draft, drafts, AggregatedFeedback, aggregated_feedback
    assignment_drafts = []
    
    for draft in drafts():
        if draft.assignment_id == assignment_id and draft.student_email == user.email:
            assignment_drafts.append(draft)
    
    # Determine if student can submit a new draft
    can_submit = len(assignment_drafts) < assignment.max_drafts
    
    # Get feedback for drafts
    draft_feedback = {}
    
    for draft in assignment_drafts:
        draft_feedback[draft.id] = []
        for feedback in aggregated_feedback():
            if feedback.draft_id == draft.id:
                draft_feedback[draft.id].append(feedback)
    
    # Sort drafts by version
    assignment_drafts.sort(key=lambda d: d.version)
    
    # Sidebar content
    sidebar_content = Div(
        # Assignment info card
        Div(
            H3("Assignment Details", cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course: {course.title} ({course.code})", cls="text-gray-600 mb-2"),
            P(f"Due Date: {assignment.due_date}", cls="text-gray-600 mb-2"),
            P(f"Maximum Drafts: {assignment.max_drafts}", cls="text-gray-600 mb-2"),
            P(f"Your Drafts: {len(assignment_drafts)}", cls="text-gray-600 mb-2"),
            P(f"Status: {assignment.status.capitalize()}", cls="text-gray-600 mb-4"),
            Div(
                action_button("Back to Course", color="gray", 
                            href=f"/student/courses/{course.id}", icon="←"),
                action_button("Submit Draft", color="teal", 
                            href=f"/student/assignments/{assignment_id}/submit",
                            disabled=not can_submit),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Rubric info if available
        (Div(
            H3("Rubric Categories", cls="text-xl font-semibold text-indigo-900 mb-3"),
            Div(
                *(Div(
                    P(f"{category.name} ({int(category.weight)}%)", 
                      cls="font-medium text-indigo-700 mb-1"),
                    P(category.description, cls="text-sm text-gray-600"),
                    cls="mb-3"
                ) for category in sorted(rubric_cats, key=lambda c: c.weight, reverse=True))
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ) if rubric_cats else "")
    )
    
    # Main content
    main_content = Div(
        # Header
        H2(assignment.title, cls="text-2xl font-bold text-indigo-900 mb-2"),
        
        # Assignment description
        card(
            Div(
                H3("Assignment Description", cls="text-xl font-semibold text-indigo-900 mb-4"),
                P(assignment.description, cls="text-gray-700 whitespace-pre-line"),
                cls="prose max-w-none"
            )
        ),
        
        # Draft history and selection
        Div(
            H3("Your Drafts", cls="text-xl font-semibold text-indigo-900 mt-8 mb-4"),
            (Div(
                tabs([
                    (f"Draft {draft.version}", f"#draft-{draft.id}")
                    for draft in assignment_drafts
                ], active_index=len(assignment_drafts)-1),
                
                # Draft content and feedback
                *(Div(
                    Div(
                        # Draft info
                        Div(
                            Div(
                                H4(f"Draft {draft.version}", cls="text-lg font-bold text-indigo-900 mb-2"),
                                P(f"Submitted: {draft.submission_date}", cls="text-sm text-gray-500 mb-2"),
                                Div(
                                    status_badge(
                                        draft.status.replace("_", " ").capitalize(),
                                        "green" if draft.status == "feedback_ready" else
                                        "yellow" if draft.status == "processing" else 
                                        "blue"
                                    ),
                                    cls="mb-4"
                                ),
                                cls="border-b border-gray-200 pb-4 mb-4"
                            ),
                            
                            # Draft content
                            Div(
                                H5("Your Submission", cls="text-md font-semibold text-gray-700 mb-2"),
                                (P("For your privacy, the content of this submission has been removed after feedback was generated.", 
                                 cls="text-amber-600 italic mb-2 text-sm") 
                                 if draft.content == "[Content removed for privacy]" else ""),
                                (P(f"Word count: {getattr(draft, 'word_count', 'N/A')}", 
                                 cls="text-gray-500 text-sm mb-2") 
                                 if hasattr(draft, 'word_count') and draft.word_count else ""),
                                Pre(
                                    draft.content,
                                    cls="bg-gray-50 p-4 rounded-md text-gray-700 text-sm mb-6 whitespace-pre-wrap border border-gray-200 overflow-auto max-h-60"
                                ),
                                cls="mb-6"
                            ),
                            
                            # Feedback if available
                            Div(
                                H5("Feedback", cls="text-md font-semibold text-gray-700 mb-3"),
                                (Div(
                                    *(Div(
                                        feedback_card(
                                            next((c.name for c in rubric_cats if c.id == fb.category_id), "General Feedback"),
                                            Div(
                                                P(fb.feedback_text, cls="text-gray-700"),
                                                P(f"Score: {fb.aggregated_score}/100", 
                                                  cls="text-sm text-gray-500 mt-2 font-medium"),
                                                cls="py-1"
                                            ),
                                            color="green" if fb.aggregated_score >= 80 else
                                                  "yellow" if fb.aggregated_score >= 60 else
                                                  "red"
                                        ),
                                        cls="mb-4"
                                    ) for fb in draft_feedback.get(draft.id, []))
                                )) if draft_feedback.get(draft.id) and draft.status == "feedback_ready" else
                                Div(
                                    P("Feedback is not available yet.", 
                                      cls="text-gray-500 italic text-center p-4 bg-gray-50 rounded-md")
                                ),
                                cls=""
                            )
                        ),
                        id=f"draft-{draft.id}",
                        cls="bg-white p-6 rounded-xl shadow-md"
                    )
                ) for draft in assignment_drafts)
            )) if assignment_drafts else
            Div(
                P("You haven't submitted any drafts for this assignment yet.", 
                  cls="text-gray-500 italic"),
                Div(
                    A("Submit Your First Draft", 
                      href=f"/student/assignments/{assignment_id}/submit",
                      cls="inline-block bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm mt-4"),
                    cls="text-center"
                ),
                cls="text-center bg-white p-8 rounded-xl shadow-md mt-4"
            ),
            cls="mb-8"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        f"{assignment.title} | FeedForward",
        dashboard_layout(
            f"Assignment: {assignment.title}", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard active in nav
        )
    )

# --- Student Draft Submission Interface ---
@rt('/student/assignments/{assignment_id}/submit')
@student_required
def get(session, request, assignment_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge
    from datetime import datetime
    
    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/student/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get existing drafts for this assignment
    from app.models.feedback import Draft, drafts
    assignment_drafts = []
    
    for draft in drafts():
        if draft.assignment_id == assignment_id and draft.student_email == user.email:
            assignment_drafts.append(draft)
    
    # Determine if student can submit a new draft
    if len(assignment_drafts) >= assignment.max_drafts:
        return Div(
            P(f"You have reached the maximum number of drafts ({assignment.max_drafts}) for this assignment.", 
              cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A(f"View Assignment", href=f"/student/assignments/{assignment_id}", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Calculate next draft version
    next_version = len(assignment_drafts) + 1
    
    # Get content from previous draft if available
    previous_content = ""
    if assignment_drafts:
        latest_draft = max(assignment_drafts, key=lambda d: d.version)
        previous_content = latest_draft.content
    
    # Sidebar content
    sidebar_content = Div(
        # Assignment info card
        Div(
            H3("Assignment Details", cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course: {course.title} ({course.code})", cls="text-gray-600 mb-2"),
            P(f"Due Date: {assignment.due_date}", cls="text-gray-600 mb-2"),
            P(f"Maximum Drafts: {assignment.max_drafts}", cls="text-gray-600 mb-2"),
            P(f"Current Draft: {next_version} of {assignment.max_drafts}", 
              cls="text-indigo-700 font-medium mb-4"),
            Div(
                action_button("Cancel", color="gray", 
                            href=f"/student/assignments/{assignment_id}",
                            icon="×"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Submission tips
        Div(
            H3("Submission Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Each submission counts as one draft", cls="text-gray-600 mb-2 text-sm"),
            P("• You cannot edit after submitting", cls="text-gray-600 mb-2 text-sm"),
            P(f"• You have {assignment.max_drafts - next_version + 1} remaining drafts", 
              cls="text-gray-600 mb-2 text-sm"),
            P("• Feedback will be provided after submission", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - Submission form
    main_content = Div(
        H2(f"Submit Draft {next_version} for {assignment.title}", 
           cls="text-2xl font-bold text-indigo-900 mb-6"),
        
        # Submission form
        Form(
            # Hidden fields for POST
            Input(type="hidden", name="assignment_id", value=str(assignment_id)),
            Input(type="hidden", name="version", value=str(next_version)),
            
            # Submission method selection
            Div(
                Label("Submission Method", cls="block text-lg font-semibold text-indigo-900 mb-3"),
                Div(
                    # Text input option
                    Div(
                        Input(
                            type="radio", 
                            name="submission_method", 
                            value="text", 
                            id="method_text", 
                            checked=True,
                            cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                        ),
                        Label(
                            "Enter or paste text",
                            for_="method_text",
                            cls="ml-2 text-gray-700"
                        ),
                        cls="flex items-center"
                    ),
                    # File upload option
                    Div(
                        Input(
                            type="radio", 
                            name="submission_method", 
                            value="file", 
                            id="method_file",
                            cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300"
                        ),
                        Label(
                            "Upload a file",
                            for_="method_file",
                            cls="ml-2 text-gray-700"
                        ),
                        cls="flex items-center mt-2"
                    ),
                    cls="space-y-2 mb-4"
                ),
                cls="mb-6"
            ),
            
            # Draft content textarea (shown when text method selected)
            Div(
                Label("Your Draft", for_="content", 
                      cls="block text-lg font-semibold text-indigo-900 mb-2"),
                P("Enter or paste your draft text below.", 
                  cls="text-gray-600 mb-1"),
                P("Note: For privacy reasons, your submission content will be automatically removed from our system after feedback is generated. Please keep your own copy.", 
                  cls="text-amber-600 text-sm mb-4 font-medium"),
                Textarea(
                    id="content",
                    name="content",
                    value=previous_content,
                    placeholder="Enter your draft here...",
                    rows="20",
                    cls="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 font-mono"
                ),
                id="text_input_section",
                cls="mb-6"
            ),
            
            # File upload section (shown when file method selected)
            Div(
                Label("Upload Your Draft", for_="file", 
                      cls="block text-lg font-semibold text-indigo-900 mb-2"),
                P("Upload a file containing your draft.", 
                  cls="text-gray-600 mb-1"),
                P("Supported formats: .txt, .docx, .pdf", 
                  cls="text-gray-600 mb-1"),
                P("Note: For privacy reasons, your submission content will be automatically removed from our system after feedback is generated. Please keep your own copy.", 
                  cls="text-amber-600 text-sm mb-4 font-medium"),
                Input(
                    type="file",
                    id="file",
                    name="file",
                    accept=".txt,.docx,.pdf",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                ),
                id="file_upload_section",
                cls="mb-6 hidden"
            ),
            
            # Submit button
            Div(
                Button("Submit Draft", type="submit",
                      cls="bg-green-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors shadow-md"),
                cls="text-center"
            ),
            
            # JavaScript to toggle between text and file upload
            Script("""
                document.addEventListener('DOMContentLoaded', function() {
                    const textMethod = document.getElementById('method_text');
                    const fileMethod = document.getElementById('method_file');
                    const textSection = document.getElementById('text_input_section');
                    const fileSection = document.getElementById('file_upload_section');
                    
                    function toggleSections() {
                        if (textMethod.checked) {
                            textSection.classList.remove('hidden');
                            fileSection.classList.add('hidden');
                        } else {
                            textSection.classList.add('hidden');
                            fileSection.classList.remove('hidden');
                        }
                    }
                    
                    textMethod.addEventListener('change', toggleSections);
                    fileMethod.addEventListener('change', toggleSections);
                });
            """),
            
            # Form settings
            method="post",
            action=f"/student/assignments/{assignment_id}/submit",
            enctype="multipart/form-data",
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        f"Submit Draft - {assignment.title} | FeedForward",
        dashboard_layout(
            f"Submit Draft - {assignment.title}", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard active in nav
        )
    )

# --- Student Draft Submission POST handler ---
@rt('/student/assignments/{assignment_id}/submit')
@student_required
async def post(session, assignment_id: int, content: str = "", version: int = 0, submission_method: str = "text", file: UploadFile = None):
    # Get current user
    user = users[session['auth']]
    
    # Verify access to the assignment
    assignment, course, error = get_student_assignment(assignment_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/student/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Process content based on submission method
    if submission_method == "file":
        # Handle file upload
        if not file or file.filename == "":
            return Div(
                P("Please select a file to upload.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                  cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
            )
        
        # Validate file size (10MB limit)
        if not validate_file_size(file, max_size_mb=10):
            return Div(
                P("File size exceeds 10MB limit. Please upload a smaller file.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                  cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
            )
        
        # Extract content from uploaded file
        try:
            content = await extract_file_content(file)
            if not content or content.strip() == "":
                return Div(
                    P("The uploaded file appears to be empty.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                    A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                      cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
                )
        except ValueError as e:
            # Handle unsupported file type
            return Div(
                P(str(e), cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                  cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
            )
        except Exception as e:
            return Div(
                P(f"Error processing file: {str(e)}", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                  cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
            )
    else:
        # Validate text content
        if not content or content.strip() == "":
            return Div(
                P("Draft content cannot be empty.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
                A(f"Try Again", href=f"/student/assignments/{assignment_id}/submit", 
                  cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
            )
    
    # Create a new draft
    from app.models.feedback import Draft, drafts
    from datetime import datetime
    from app.utils.privacy import calculate_word_count
    
    # Calculate word count for statistics
    word_count = calculate_word_count(content)
    
    # Create a new draft submission with additional privacy fields
    new_draft = Draft(
        id=next(d.id for d in drafts()) + 1 if drafts() else 1,
        assignment_id=assignment_id,
        student_email=user.email,
        version=version,
        content=content,
        content_preserved=False,  # Default to not preserving content
        submission_date=datetime.now().isoformat(),
        word_count=word_count,
        status="submitted",  # Initial status, will be updated by feedback system
        content_removed_date="",  # Will be set when content is removed
        # Store file metadata if file was uploaded
        submission_method=submission_method,
        original_filename=file.filename if submission_method == "file" and file else None,
        file_type=Path(file.filename).suffix.lower() if submission_method == "file" and file else None
    )
    
    # Save the draft
    drafts.insert(new_draft)
    
    # Queue feedback generation in the background
    from app.services.background_tasks import queue_feedback_generation
    await queue_feedback_generation(new_draft.id)
    
    # Redirect to the assignment view with a message about privacy
    return RedirectResponse(f"/student/assignments/{assignment_id}", status_code=303)

# --- Student Course Assignments ---
@rt('/student/courses/{course_id}/assignments')
@student_required
def get(session, request, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge
    
    # Verify course and enrollment
    course, error = get_student_course(course_id, user.email)
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/student/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get assignments for this course
    from app.models.assignment import Assignment, assignments
    course_assignments = []
    
    for assignment in assignments():
        if assignment.course_id == course_id:
            # Include all assignments, not just active ones
            course_assignments.append(assignment)
    
    # Get student drafts for these assignments
    from app.models.feedback import Draft, drafts
    student_drafts = {}
    
    for draft in drafts():
        if draft.student_email == user.email:
            for assignment in course_assignments:
                if draft.assignment_id == assignment.id:
                    if assignment.id not in student_drafts:
                        student_drafts[assignment.id] = []
                    student_drafts[assignment.id].append(draft)
    
    # Sidebar content
    sidebar_content = Div(
        # Course info card
        Div(
            H3(course.title, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course Code: {course.code}", cls="text-gray-600 mb-1"),
            P(f"Term: {getattr(course, 'term', 'Current')}", cls="text-gray-600 mb-1"),
            P(f"Status: {getattr(course, 'status', 'active').capitalize()}", cls="text-gray-600 mb-4"),
            Div(
                action_button("Back to Course", color="gray", href=f"/student/courses/{course_id}", icon="←"),
                action_button("Dashboard", color="indigo", href="/student/dashboard"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Assignment status summary
        Div(
            H3("Assignment Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                Div(
                    Div(
                        str(sum(1 for a in course_assignments if a.status == 'active')), 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Active", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                Div(
                    Div(
                        str(sum(1 for a in course_assignments if a.status == 'closed')), 
                        cls="text-yellow-700 font-bold"
                    ),
                    P("Closed", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                Div(
                    Div(
                        str(sum(1 for a in course_assignments if a.status in ['archived', 'deleted'])), 
                        cls="text-gray-700 font-bold"
                    ),
                    P("Archived", cls="text-gray-600"),
                    cls="flex items-center space-x-2"
                ),
                cls="space-y-2"
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content
    main_content = Div(
        H2(f"Assignments for {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        
        # Filter controls (to be implemented later)
        Div(
            Div(
                # Status filter
                Div(
                    A("All", href="#", 
                      cls="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md"),
                    A("Active", href="#", 
                      cls="inline-block px-4 py-2 bg-gray-200 rounded-md ml-2"),
                    A("Completed", href="#", 
                      cls="inline-block px-4 py-2 bg-gray-200 rounded-md ml-2"),
                    cls="mb-4 md:mb-0"
                ),
                # Sort options (to be implemented later)
                Div(
                    Select(
                        Option("Sort by Due Date (newest)", value="due_date_desc", selected=True),
                        Option("Sort by Due Date (oldest)", value="due_date_asc"),
                        Option("Sort by Title (A-Z)", value="title_asc"),
                        cls="border border-gray-300 rounded-md px-3 py-2"
                    ),
                    cls=""
                ),
                cls="flex flex-col md:flex-row md:justify-between mb-6"
            ),
            cls="bg-gray-50 p-4 rounded-lg mb-6"
        ),
        
        # Assignments list
        Div(
            *(Div(
                Div(
                    # Assignment title and status
                    Div(
                        Div(
                            H3(assignment.title, cls="text-xl font-bold text-indigo-800 mb-1"),
                            P(f"Due: {assignment.due_date}", cls="text-gray-600 mb-2"),
                            status_badge(
                                assignment.status.capitalize(),
                                "green" if assignment.status == "active" else 
                                "yellow" if assignment.status == "closed" else
                                "gray"
                            ),
                            cls="flex-1"
                        ),
                        # Draft status
                        Div(
                            P(f"Drafts: {len(student_drafts.get(assignment.id, []))}/{assignment.max_drafts}", 
                              cls="text-sm text-gray-600 mb-2"),
                            # Display the latest draft status if exists
                            Div(
                                status_badge(
                                    "Feedback Ready" if any(d.status == "feedback_ready" for d in student_drafts.get(assignment.id, [])) else
                                    "Processing" if any(d.status == "processing" for d in student_drafts.get(assignment.id, [])) else
                                    "Submitted" if student_drafts.get(assignment.id, []) else
                                    "Not Started",
                                    "green" if any(d.status == "feedback_ready" for d in student_drafts.get(assignment.id, [])) else
                                    "yellow" if any(d.status == "processing" for d in student_drafts.get(assignment.id, [])) else
                                    "blue" if student_drafts.get(assignment.id, []) else
                                    "gray"
                                ),
                                cls=""
                            ),
                            cls="md:text-right"
                        ),
                        cls="flex flex-col md:flex-row justify-between mb-4"
                    ),
                    
                    # Description and actions
                    Div(
                        Div(
                            P(assignment.description[:150] + "..." if len(assignment.description) > 150 else assignment.description, 
                              cls="text-gray-600 mb-4"),
                            cls="flex-1"
                        ),
                        Div(
                            Div(
                                action_button("View Assignment", color="indigo", 
                                            href=f"/student/assignments/{assignment.id}", 
                                            size="small"),
                                action_button("Submit Draft", color="teal", 
                                            href=f"/student/assignments/{assignment.id}/submit", 
                                            size="small",
                                            # Only show submit button if max drafts not reached and assignment active
                                            disabled=len(student_drafts.get(assignment.id, [])) >= assignment.max_drafts or 
                                                    assignment.status != "active"),
                                cls="flex flex-col gap-2"
                            ),
                            cls=""
                        ),
                        cls="flex flex-col md:flex-row justify-between"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6 hover:shadow-lg transition-shadow"
                )
            ) for assignment in sorted(course_assignments, 
                                      key=lambda a: (a.status != "active", a.due_date), 
                                      reverse=False))
            if course_assignments else
            P("No assignments found for this course.", 
              cls="text-gray-500 italic p-6 bg-white rounded-xl border border-gray-200 text-center")
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        f"Assignments - {course.title} | FeedForward",
        dashboard_layout(
            f"Assignments - {course.title}", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard active in nav
        )
    )

# --- Submission History and Management ---
@rt('/student/submissions')
@student_required
def get(session, request):
    """View and manage all student submissions history"""
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, data_table
    
    # Get all student drafts
    from app.models.feedback import Draft, drafts
    student_drafts = []
    
    for draft in drafts():
        if draft.student_email == user.email:
            # Skip drafts that are marked as hidden by student if the flag exists and is True
            if hasattr(draft, 'hidden_by_student') and draft.hidden_by_student:
                continue
            student_drafts.append(draft)
    
    # Sort drafts by submission date (newest first)
    student_drafts.sort(key=lambda d: d.submission_date, reverse=True)
    
    # Group drafts by assignment
    from app.models.assignment import assignments
    from app.models.course import courses
    
    draft_groups = {}
    assignment_info = {}
    course_info = {}
    
    # Get assignment and course information
    for draft in student_drafts:
        if draft.assignment_id not in assignment_info:
            # Find assignment
            for a in assignments():
                if a.id == draft.assignment_id:
                    assignment_info[a.id] = a
                    
                    # Find course for this assignment
                    for c in courses():
                        if c.id == a.course_id:
                            course_info[c.id] = c
                            break
                    break
        
        # Group drafts by assignment
        if draft.assignment_id not in draft_groups:
            draft_groups[draft.assignment_id] = []
        draft_groups[draft.assignment_id].append(draft)
    
    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3("Submission Management", cls="text-xl font-semibold text-indigo-900 mb-2"),
            P("This page allows you to view and manage all your submissions across courses.", cls="text-gray-600 mb-4"),
            P("• Your submission content is removed after feedback is generated", cls="text-gray-600 text-sm mb-1"),
            P("• You can hide submissions you no longer need to see", cls="text-gray-600 text-sm mb-1"),
            P("• Hidden submissions still count toward your draft limits", cls="text-gray-600 text-sm mb-1"),
            P("• Draft statistics are preserved for analytics", cls="text-gray-600 text-sm mb-1"),
            Div(
                action_button("Dashboard", color="gray", href="/student/dashboard", icon="←"),
                cls="mt-4"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Submission stats
        Div(
            H3("Submission Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total Submissions: {len(student_drafts)}", cls="text-gray-600 mb-2"),
            P(f"Active Assignments: {len(draft_groups)}", cls="text-gray-600 mb-2"),
            # Count drafts by status
            P(f"Feedback Available: {sum(1 for d in student_drafts if d.status == 'feedback_ready')}", cls="text-gray-600 mb-2"),
            P(f"Processing: {sum(1 for d in student_drafts if d.status == 'processing')}", cls="text-gray-600 mb-2"),
            A("View Hidden Submissions", 
              hx_get="/student/submissions/hidden",
              hx_target="#main-content",
              cls="text-sm text-indigo-600 hover:underline block mt-4"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - grouped submissions with management options
    main_content = Div(
        H2("Your Submission History", cls="text-2xl font-bold text-indigo-900 mb-6", id="main-content"),
        
        # If no submissions yet
        (P("You haven't submitted any drafts yet.", cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center mb-8") 
         if not student_drafts else ""),
         
        # Submissions by assignment
        *(Div(
            H3(
                Div(
                    Span(assignment_info[assignment_id].title, cls="text-xl font-bold text-indigo-800"),
                    Span(f" ({course_info[assignment_info[assignment_id].course_id].code})", 
                         cls="text-gray-600 font-normal text-base"),
                ),
                cls="mb-4"
            ),
            
            # Table of drafts for this assignment
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Draft", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                            Th("Date", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                            Th("Status", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                            Th("Words", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                            Th("Actions", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100")
                        )
                    ),
                    Tbody(
                        *(Tr(
                            # Draft number
                            Td(str(draft.version), cls="py-3 px-4 font-medium"),
                            # Submission date
                            Td(draft.submission_date.split("T")[0] if "T" in draft.submission_date else draft.submission_date, 
                               cls="py-3 px-4 text-gray-600"),
                            # Status with badge
                            Td(
                                status_badge(
                                    draft.status.replace("_", " ").capitalize(),
                                    "green" if draft.status == "feedback_ready" else
                                    "yellow" if draft.status == "processing" else
                                    "blue"
                                ),
                                cls="py-3 px-4"
                            ),
                            # Word count
                            Td(
                                str(getattr(draft, 'word_count', 'N/A')),
                                cls="py-3 px-4 text-gray-600"
                            ),
                            # Action buttons
                            Td(
                                Div(
                                    A(
                                        "View", 
                                        href=f"/student/assignments/{assignment_id}#draft-{draft.id}",
                                        cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2"
                                    ),
                                    Button(
                                        "Hide", 
                                        hx_post=f"/student/submissions/hide/{draft.id}",
                                        hx_confirm="This will hide the draft from your history. It will still count toward your draft limit. Continue?",
                                        hx_target=f"#draft-row-{draft.id}",
                                        cls="text-xs px-3 py-1 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                                    ),
                                    cls="flex"
                                ),
                                cls="py-3 px-4"
                            ),
                            id=f"draft-row-{draft.id}",
                            cls="border-b border-gray-100 hover:bg-gray-50"
                        ) for draft in sorted(draft_groups[assignment_id], key=lambda d: d.version, reverse=True))
                    ),
                    cls="w-full"
                ),
                cls="bg-white rounded-lg shadow-md border border-gray-100 overflow-x-auto mb-8"
            )
        ) for assignment_id in draft_groups)
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Submission History | FeedForward",
        dashboard_layout(
            "Submission History", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard active in nav
        )
    )

# --- Hide Submission POST Handler ---
@rt('/student/submissions/hide/{draft_id}')
@student_required
def post(session, draft_id: int):
    """Hide a draft from the student's view (soft delete)"""
    # Get current user
    user = users[session['auth']]
    
    # Get the draft
    from app.models.feedback import drafts
    target_draft = None
    
    for draft in drafts():
        if draft.id == draft_id and draft.student_email == user.email:
            target_draft = draft
            break
    
    if not target_draft:
        return Div(
            P("Draft not found or you don't have permission to hide it.", 
              cls="text-red-600 p-3 bg-red-50 rounded")
        )
    
    # Update the draft to mark it as hidden by student
    if not hasattr(target_draft, 'hidden_by_student'):
        # Add the attribute if it doesn't exist
        setattr(target_draft, 'hidden_by_student', True)
    else:
        target_draft.hidden_by_student = True
    drafts.update(target_draft)
    
    # Return a confirmation message that will replace the table row
    return Div(
        Td(
            "Draft hidden", 
            colspan="5",
            cls="py-3 px-4 text-gray-500 italic text-center"
        ),
        cls="border-b border-gray-100 bg-gray-50"
    )

# --- View Hidden Submissions Handler ---
@rt('/student/submissions/hidden')
@student_required
def get(session, request):
    """Show the student's hidden submissions"""
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from fasthtml.common import Div, H2, P, Table, Thead, Tbody, Tr, Td, Th, Button, A, Span
    from app.utils.ui import status_badge
    
    # Get all student hidden drafts
    from app.models.feedback import Draft, drafts
    from app.models.assignment import assignments
    from app.models.course import courses
    
    hidden_drafts = []
    assignment_info = {}
    course_info = {}
    
    for draft in drafts():
        if draft.student_email == user.email and hasattr(draft, 'hidden_by_student') and draft.hidden_by_student:
            hidden_drafts.append(draft)
            
            # Get assignment and course info
            if draft.assignment_id not in assignment_info:
                for a in assignments():
                    if a.id == draft.assignment_id:
                        assignment_info[a.id] = a
                        
                        # Find course for this assignment
                        for c in courses():
                            if c.id == a.course_id:
                                course_info[c.id] = c
                                break
                        break
    
    # Sort drafts by submission date (newest first)
    hidden_drafts.sort(key=lambda d: d.submission_date, reverse=True)
    
    # Return the hidden submissions view
    return Div(
        H2("Hidden Submissions", cls="text-2xl font-bold text-indigo-900 mb-6"),
        
        # Show button to go back
        Div(
            Button(
                "← Back to Visible Submissions", 
                hx_get="/student/submissions",
                hx_target="#main-content",
                cls="mb-6 bg-gray-200 hover:bg-gray-300 text-gray-800 px-4 py-2 rounded-md"
            ),
            cls="mb-6"
        ),
        
        # If no hidden submissions
        (P("You don't have any hidden submissions.", 
           cls="text-gray-500 italic bg-white p-6 rounded-xl border border-gray-200 text-center mb-8") 
         if not hidden_drafts else ""),
        
        # Hidden submissions table
        (Div(
            Table(
                Thead(
                    Tr(
                        Th("Assignment", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                        Th("Draft", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                        Th("Date", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                        Th("Status", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100"),
                        Th("Actions", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b border-indigo-100")
                    )
                ),
                Tbody(
                    *(Tr(
                        # Assignment name
                        Td(
                            Div(
                                P(assignment_info[draft.assignment_id].title, cls="font-medium text-indigo-700"),
                                P(f"{course_info[assignment_info[draft.assignment_id].course_id].code}", 
                                  cls="text-xs text-gray-500"),
                                cls=""
                            ),
                            cls="py-3 px-4"
                        ),
                        # Draft number
                        Td(str(draft.version), cls="py-3 px-4 font-medium"),
                        # Submission date
                        Td(draft.submission_date.split("T")[0] if "T" in draft.submission_date else draft.submission_date, 
                           cls="py-3 px-4 text-gray-600"),
                        # Status with badge
                        Td(
                            status_badge(
                                draft.status.replace("_", " ").capitalize(),
                                "green" if draft.status == "feedback_ready" else
                                "yellow" if draft.status == "processing" else
                                "blue"
                            ),
                            cls="py-3 px-4"
                        ),
                        # Action buttons
                        Td(
                            Div(
                                A(
                                    "View", 
                                    href=f"/student/assignments/{draft.assignment_id}#draft-{draft.id}",
                                    cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2"
                                ),
                                Button(
                                    "Unhide", 
                                    hx_post=f"/student/submissions/unhide/{draft.id}",
                                    hx_target="#main-content",
                                    cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700"
                                ),
                                cls="flex"
                            ),
                            cls="py-3 px-4"
                        ),
                        cls="border-b border-gray-100 hover:bg-gray-50"
                    ) for draft in hidden_drafts)
                ),
                cls="w-full"
            ),
            cls="bg-white rounded-lg shadow-md border border-gray-100 overflow-x-auto mb-8"
        ) if hidden_drafts else "")
    )
    
# --- Unhide Submission POST Handler ---
@rt('/student/submissions/unhide/{draft_id}')
@student_required
def post(session, draft_id: int):
    """Unhide a draft previously hidden by the student"""
    # Get current user
    user = users[session['auth']]
    
    # Get the draft
    from app.models.feedback import drafts
    target_draft = None
    
    for draft in drafts():
        if draft.id == draft_id and draft.student_email == user.email:
            target_draft = draft
            break
    
    if not target_draft:
        return Div(
            P("Draft not found or you don't have permission to unhide it.", 
              cls="text-red-600 p-3 bg-red-50 rounded")
        )
    
    # Update the draft to mark it as not hidden
    if hasattr(target_draft, 'hidden_by_student'):
        target_draft.hidden_by_student = False
        drafts.update(target_draft)
    
    # Redirect back to submissions page
    from fasthtml.common import Div, H2, P, Table, Thead, Tbody, Tr, Td, Th, Button, A, Span
    return Div(
        Div(
            P("Draft unhidden successfully!", cls="text-green-600 p-3 bg-green-50 rounded mb-4"),
            Button(
                "View Submissions", 
                hx_get="/student/submissions",
                hx_target="#main-content",
                cls="mb-6 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md"
            ),
            cls="mb-6 text-center"
        )
    )

# --- All Student Assignments Route ---
@rt('/student/assignments')
@student_required
def get(session, request):
    """View all assignments for the student"""
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button, status_badge, data_table
    
    # Get student's enrollments and courses
    student_enrollments = []
    enrolled_courses = {}
    
    for enrollment in enrollments():
        if enrollment.student_email == user.email:
            student_enrollments.append(enrollment)
            
    # Get course details for each enrollment
    for enrollment in student_enrollments:
        for course in courses():
            if course.id == enrollment.course_id:
                enrolled_courses[course.id] = course
                break
    
    # Get all assignments for the enrolled courses
    from app.models.assignment import Assignment, assignments
    student_assignments = []
    
    for assignment in assignments():
        if assignment.course_id in enrolled_courses:
            # Add course info to assignment
            student_assignments.append({
                'assignment': assignment,
                'course': enrolled_courses[assignment.course_id]
            })
    
    # Get student drafts
    from app.models.feedback import Draft, drafts
    student_drafts = {}
    
    for draft in drafts():
        if draft.student_email == user.email:
            if draft.assignment_id not in student_drafts:
                student_drafts[draft.assignment_id] = []
            student_drafts[draft.assignment_id].append(draft)
    
    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3("Assignment Options", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/student/dashboard", icon="←"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Courses filter
        Div(
            H3("Filter by Course", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                *(Div(
                    A(f"{course.code}: {course.title}", 
                      href=f"/student/courses/{course.id}/assignments",
                      cls="text-indigo-700 hover:underline"),
                    cls="mb-2"
                ) for course in enrolled_courses.values())
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - assignment table
    main_content = Div(
        H2("All Assignments", cls="text-2xl font-bold text-indigo-900 mb-6"),
        
        # Assignments table
        Div(
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Assignment", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Course", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Due Date", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Drafts", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Status", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                        ),
                        cls="bg-indigo-50"
                    ),
                    Tbody(
                        *(Tr(
                            # Assignment title
                            Td(
                                Div(
                                    H4(assignment_data['assignment'].title, cls="font-semibold text-indigo-800"),
                                    P(assignment_data['assignment'].description[:60] + "..." if len(assignment_data['assignment'].description) > 60 else assignment_data['assignment'].description,
                                      cls="text-xs text-gray-500 mt-1"),
                                    cls=""
                                ),
                                cls="py-4 px-6"
                            ),
                            # Course
                            Td(
                                Div(
                                    P(assignment_data['course'].title, cls="font-medium text-gray-700"),
                                    P(assignment_data['course'].code, cls="text-xs text-gray-500"),
                                    cls=""
                                ),
                                cls="py-4 px-6"
                            ),
                            # Due date
                            Td(assignment_data['assignment'].due_date, cls="py-4 px-6 text-gray-700"),
                            # Drafts
                            Td(
                                Div(
                                    f"{len(student_drafts.get(assignment_data['assignment'].id, []))}/{assignment_data['assignment'].max_drafts}",
                                    cls="flex items-center justify-center w-10 h-6 rounded-full text-xs font-medium " +
                                    ("bg-green-100 text-green-800" if len(student_drafts.get(assignment_data['assignment'].id, [])) == assignment_data['assignment'].max_drafts else
                                     "bg-yellow-100 text-yellow-800" if student_drafts.get(assignment_data['assignment'].id, []) else
                                     "bg-gray-100 text-gray-800")
                                ),
                                cls="py-4 px-6"
                            ),
                            # Status
                            Td(
                                Div(
                                    status_badge(
                                        assignment_data['assignment'].status.capitalize(),
                                        "green" if assignment_data['assignment'].status == "active" else
                                        "yellow" if assignment_data['assignment'].status == "closed" else
                                        "gray"
                                    ),
                                    cls=""
                                ),
                                cls="py-4 px-6"
                            ),
                            # Actions
                            Td(
                                Div(
                                    A("View", 
                                      href=f"/student/assignments/{assignment_data['assignment'].id}",
                                      cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2"),
                                    A("Submit", 
                                      href=f"/student/assignments/{assignment_data['assignment'].id}/submit",
                                      cls=f"text-xs px-3 py-1 {'bg-teal-600 text-white' if len(student_drafts.get(assignment_data['assignment'].id, [])) < assignment_data['assignment'].max_drafts and assignment_data['assignment'].status == 'active' else 'bg-gray-300 text-gray-500 cursor-not-allowed'} rounded-md hover:{'bg-teal-700' if len(student_drafts.get(assignment_data['assignment'].id, [])) < assignment_data['assignment'].max_drafts and assignment_data['assignment'].status == 'active' else ''}"),
                                    cls="flex"
                                ),
                                cls="py-4 px-6"
                            )
                        ) for assignment_data in sorted(student_assignments, 
                                                      key=lambda a: (a['assignment'].status != "active", 
                                                                    a['assignment'].due_date)))
                    ),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ) if student_assignments else
            P("No assignments found.", 
              cls="text-gray-500 italic p-6 bg-white rounded-xl border border-gray-200 text-center")
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "All Assignments | FeedForward",
        dashboard_layout(
            "All Assignments", 
            sidebar_content, 
            main_content, 
            user_role=Role.STUDENT,
            current_path="/student/dashboard"  # Keep dashboard active in nav
        )
    )