"""
Instructor routes (dashboard, courses, students, etc.)
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse
from datetime import datetime
from fastlite import NotFoundError
import string
import random
import urllib.parse

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment, courses, enrollments

from app.utils.email import send_verification_email, send_student_invitation_email, generate_verification_token
from app.utils.auth import get_password_hash, verify_password
from app.utils.ui import dashboard_layout, card, data_table, status_badge, action_button

# Get the route table from the app
from app import app, rt

# Import authentication decorators
from app import basic_auth, role_required, instructor_required, student_required, admin_required

# --- Utility Functions ---
def generate_invitation_token(length=40):
    """Generate a random token for student invitations"""
    chars = string.ascii_letters + string.digits + '-_'
    return ''.join(random.choice(chars) for _ in range(length))

# --- Instructor Dashboard ---
@rt('/instructor/dashboard')
@instructor_required
def get(session):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1
            
            # Add to courses with student count
            instructor_courses.append((course, student_count))
    
    # Create dashboard content
    if instructor_courses:
        # Show courses if the instructor has any
        courses_content = Div(
            Div(
                H2("Your Courses", cls="text-2xl font-bold text-indigo-900"),
                A("View All Courses", href="/instructor/courses", 
                  cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium"),
                cls="flex justify-between items-center mb-6"
            ),
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                H3(course.title, cls="text-xl font-bold text-indigo-900 mb-1"),
                                P(f"Course Code: {course.code}", cls="text-gray-600"),
                                P(f"Students: {student_count}", cls="text-gray-600"),
                                cls="mb-4"
                            ),
                            Div(
                                A("View Students", href=f"/instructor/courses/{course.id}/students", 
                                  cls="text-indigo-600 hover:text-indigo-800 mr-3 font-medium"),
                                A("Manage Assignments", href="#", 
                                  cls="text-teal-600 hover:text-teal-800 font-medium"),
                                cls="flex"
                            ),
                            cls=""
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100"
                    )
                    for course, student_count in instructor_courses
                ],
                cls="grid grid-cols-1 md:grid-cols-2 gap-6"
            ),
            cls=""
        )
    else:
        # Show a message if no courses yet
        courses_content = card(
            Div(
                P("You don't have any courses yet. Create your first course to get started.", 
                  cls="text-center text-gray-600 mb-6"),
                Div(
                    A("Create New Course", href="/instructor/courses/new", 
                      cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="text-center"
                ),
                cls="py-8"
            ),
            title="Welcome to the Instructor Dashboard"
        )
    
    # Quick action cards
    action_cards = Div(
        H2("Quick Actions", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            # Create Course card
            card(
                Div(
                    Div(
                        Span("🏫", cls="text-4xl"),
                        P("Create a new course for your students", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Create Course", href="/instructor/courses/new", 
                          cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Manage Courses card
            card(
                Div(
                    Div(
                        Span("📚", cls="text-4xl"),
                        P("View and manage all your courses", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Manage Courses", href="/instructor/courses", 
                          cls="bg-amber-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-amber-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Invite Students card
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P("Invite students to join your course", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Invite Students", href="/instructor/invite-students", 
                          cls="bg-teal-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Manage Students card 
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P("Manage your enrolled students", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Manage Students", href="/instructor/manage-students", 
                          cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # TODO: Add more action cards as features are developed
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        ),
        cls="mt-10"
    )
    
    # Main content with courses and action cards
    main_content = Div(
        courses_content,
        action_cards,
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        # Instructor info card
        card(
            Div(
                Div(
                    Div(
                        user.name[0] if user.name else "?",
                        cls="w-16 h-16 rounded-full bg-indigo-600 text-white flex items-center justify-center text-2xl font-bold"
                    ),
                    cls="flex justify-center mb-4"
                ),
                H3(user.name, cls="text-lg font-bold text-center text-indigo-900"),
                P(user.email, cls="text-center text-gray-600 mb-4"),
                Hr(cls="my-4"),
                Div(
                    P(f"Courses: {len(instructor_courses)}", cls="text-gray-600"),
                    P(f"Department: {user.department if user.department else 'Not set'}", cls="text-gray-600"),
                    cls="text-sm"
                ),
                cls="p-2"
            ),
            title="Profile"
        ),
        # Recent activity or tips
        card(
            Div(
                Div(
                    P("✓ Complete your profile information", cls="mb-2 text-green-600"),
                    P("✓ Create your first course", cls="mb-2 text-green-600") if instructor_courses else P("○ Create your first course", cls="mb-2 text-gray-600"),
                    P("○ Invite students to your course", cls="mb-2 text-gray-600"),
                    P("○ Create your first assignment", cls="mb-2 text-gray-600"),
                    cls="text-sm"
                ),
                cls="p-2"
            ),
            title="Getting Started"
        ),
        cls="space-y-6"
    )
    
    # Use the dashboard layout with our components
    from app.utils.ui import dashboard_layout
    return dashboard_layout(
        "Instructor Dashboard | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

# --- Course Management ---
# Helper function to get a course by ID with instructor permission check
def get_instructor_course(course_id, instructor_email):
    """
    Get a course by ID, checking that it belongs to the instructor.
    Returns (course, error_message) tuple.
    """
    # Find the course
    target_course = None
    try:
        for course in courses():
            if course.id == course_id:
                target_course = course
                break
                
        if not target_course:
            return None, "Course not found."
            
        # Check if this instructor owns the course
        if target_course.instructor_email != instructor_email:
            return None, "You don't have permission to access this course."
            
        # Skip deleted courses
        if hasattr(target_course, 'status') and target_course.status == "deleted":
            return None, "This course has been deleted."
            
        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {str(e)}"
@rt('/instructor/courses')
@instructor_required
def get(session):
    """Course listing page for instructors"""
    # Get current user
    user = users[session['auth']]
    
    # Get all courses taught by this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, 'status') and course.status == "deleted":
                continue
                
            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1
            
            # Add to list with student count
            instructor_courses.append((course, student_count))
    
    # Sort courses by creation date (newest first)
    instructor_courses.sort(key=lambda x: x[0].created_at if hasattr(x[0], 'created_at') else "", reverse=True)
    
    # Create the main content
    main_content = Div(
        # Header with action button
        Div(
            H2("Course Management", cls="text-2xl font-bold text-indigo-900"),
            action_button("Create New Course", color="indigo", href="/instructor/courses/new", icon="+"),
            cls="flex justify-between items-center mb-6"
        ),
        
        # Course listing or empty state
        (Div(
            P(f"You have {len(instructor_courses)} {'course' if len(instructor_courses) == 1 else 'courses'}.", 
              cls="text-gray-600 mb-6"),
            
            # Course table with actions
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Course Title", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Code", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Term", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Status", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Students", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                        ),
                        cls="bg-indigo-50"
                    ),
                    Tbody(
                        *(Tr(
                            # Course title
                            Td(course.title, cls="py-4 px-6"),
                            # Course code
                            Td(course.code, cls="py-4 px-6"),
                            # Term
                            Td(getattr(course, 'term', 'Current') or 'Current', cls="py-4 px-6"),
                            # Status badge
                            Td(
                                status_badge(
                                    getattr(course, 'status', 'active').capitalize() or 'Active',
                                    "green" if getattr(course, 'status', 'active') == 'active' else
                                    "yellow" if getattr(course, 'status', 'active') == 'closed' else
                                    "gray"
                                ),
                                cls="py-4 px-6"
                            ),
                            # Student count
                            Td(str(student_count), cls="py-4 px-6"),
                            # Action buttons
                            Td(
                                Div(
                                    A("Students", 
                                      href=f"/instructor/courses/{course.id}/students",
                                      cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2"),
                                    A("Edit", 
                                      href=f"/instructor/courses/{course.id}/edit",
                                      cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2"),
                                    A("Assignments", 
                                      href=f"/instructor/courses/{course.id}/assignments",
                                      cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700"),
                                    cls="flex"
                                ),
                                cls="py-4 px-6"
                            )
                        ) for course, student_count in instructor_courses)
                    ),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ),
            cls=""
        ) if instructor_courses else
        Div(
            P("You don't have any courses yet. Create your first course to get started.", 
              cls="text-center text-gray-600 mb-6"),
            Div(
                A("Create New Course", href="/instructor/courses/new", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="text-center"
            ),
            cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4"
        ))
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Create Course", color="indigo", href="/instructor/courses/new", icon="+"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total Courses: {len(instructor_courses)}", cls="text-gray-600 mb-2"),
            P(f"Active Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'active')}", 
              cls="text-green-600 mb-2"),
            P(f"Closed Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'closed')}", 
              cls="text-amber-600 mb-2"),
            P(f"Archived Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'archived')}", 
              cls="text-gray-600 mb-2"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Courses | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/new')
@instructor_required
def get(session):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Create the form content
    form_content = Div(
        H2("Create New Course", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Complete the form below to create a new course for your students.", 
              cls="mb-6 text-gray-600"),
            Form(
                Div(
                    Label("Course Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="title", name="title", type="text", placeholder="e.g. Introduction to Computer Science",
                          required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                Div(
                    Label("Course Code", for_="code", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="code", name="code", type="text", placeholder="e.g. CS101",
                          required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                # Add new fields for term, department, and status
                Div(
                    Div(
                        Label("Term", for_="term", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="term", name="term", type="text", placeholder="e.g. Fall 2023",
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pr-2"
                    ),
                    Div(
                        Label("Department", for_="department", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="department", name="department", type="text", placeholder="e.g. Computer Science",
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pl-2"
                    ),
                    cls="flex mb-4"
                ),
                Div(
                    Label("Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                    Select(
                        Option("Active", value="active", selected=True),
                        Option("Closed", value="closed"),
                        Option("Archived", value="archived"),
                        id="status", name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                    Textarea(id="description", name="description", placeholder="Provide a brief description of the course",
                            rows="4", cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-6"
                ),
                Div(
                    Button("Create Course", type="submit", cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="mb-4"
                ),
                Div(id="result", cls=""),
                hx_post="/instructor/courses/new",
                hx_target="#result",
                cls="w-full"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Manage Courses", color="indigo", href="/instructor/courses", icon="📚"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Choose a clear, descriptive course title", cls="text-gray-600 mb-2 text-sm"),
            P("• Use official course codes when possible", cls="text-gray-600 mb-2 text-sm"),
            P("• Include key information in the description", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Create Course | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/new')
@instructor_required
def post(session, title: str, code: str, term: str = "", department: str = "", status: str = "active", description: str = ""):
    # Get current user
    user = users[session['auth']]
    
    # Validate input
    if not title or not code:
        return "Course title and code are required."
    
    # Check for duplicate course code
    for course in courses():
        if course.code == code and course.instructor_email == user.email:
            # Only check for duplicates from the same instructor
            # If the course is deleted, allow reuse of code
            if not hasattr(course, 'status') or course.status != "deleted":
                return "You already have a course with this code. Please use a different code."
    
    # Validate status
    if status not in ['active', 'closed', 'archived']:
        status = 'active'  # Default to active if invalid
    
    # Get next course ID
    next_course_id = 1
    try:
        course_ids = [c.id for c in courses()]
        if course_ids:
            next_course_id = max(course_ids) + 1
    except:
        next_course_id = 1
    
    # Create timestamp
    now = datetime.now().isoformat()
    
    # Create new course
    new_course = Course(
        id=next_course_id,
        title=title,
        code=code,
        term=term,
        department=department,
        status=status,
        instructor_email=user.email,
        created_at=now,
        updated_at=now
    )
    
    # Insert into database
    courses.insert(new_course)
    
    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Course Created Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your course \"{title}\" has been created.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Return to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Manage Courses", href="/instructor/courses", 
                  cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-4 hover:bg-amber-700"),
                A("Invite Students", href=f"/instructor/invite-students?course_id={next_course_id}", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )

# --- Edit Course Route ---
@rt('/instructor/courses/{course_id}/edit')
@instructor_required
def get(session, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Create the form content
    form_content = Div(
        H2(f"Edit Course: {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Update your course details below.", 
              cls="mb-6 text-gray-600"),
            Form(
                Div(
                    Label("Course Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="title", name="title", type="text", placeholder="e.g. Introduction to Computer Science",
                          value=course.title, required=True, 
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                Div(
                    Label("Course Code", for_="code", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="code", name="code", type="text", placeholder="e.g. CS101",
                          value=course.code, required=True, 
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                # Term and department fields
                Div(
                    Div(
                        Label("Term", for_="term", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="term", name="term", type="text", placeholder="e.g. Fall 2023",
                              value=getattr(course, 'term', ''),
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pr-2"
                    ),
                    Div(
                        Label("Department", for_="department", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="department", name="department", type="text", placeholder="e.g. Computer Science",
                              value=getattr(course, 'department', ''),
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pl-2"
                    ),
                    cls="flex mb-4"
                ),
                # Status field
                Div(
                    Label("Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                    Select(
                        Option("Active", value="active", selected=getattr(course, 'status', 'active') == 'active'),
                        Option("Closed", value="closed", selected=getattr(course, 'status', 'active') == 'closed'),
                        Option("Archived", value="archived", selected=getattr(course, 'status', 'active') == 'archived'),
                        id="status", name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                    Textarea(id="description", name="description", placeholder="Provide a brief description of the course",
                            value=getattr(course, 'description', ''), rows="4", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-6"
                ),
                Div(
                    Button("Update Course", type="submit", cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="mb-4"
                ),
                Div(id="result", cls=""),
                hx_post=f"/instructor/courses/{course_id}/edit",
                hx_target="#result",
                cls="w-full"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content with course actions
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Courses", color="gray", href="/instructor/courses", icon="←"),
                action_button("View Students", color="indigo", href=f"/instructor/courses/{course_id}/students", icon="👨‍👩‍👧‍👦"),
                action_button("Assignments", color="teal", href=f"/instructor/courses/{course_id}/assignments", icon="📝"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Current Status: {getattr(course, 'status', 'active').capitalize()}", 
              cls="font-medium " + 
              ("text-green-600" if getattr(course, 'status', 'active') == 'active' else 
               "text-amber-600" if getattr(course, 'status', 'active') == 'closed' else 
               "text-gray-600")),
            P("Active: Students can be invited and can access course materials", cls="text-gray-600 text-sm mt-4 mb-1"),
            P("Closed: No new enrollments, but existing students can access", cls="text-gray-600 text-sm mb-1"),
            P("Archived: Hidden from all users but preserves data", cls="text-gray-600 text-sm mb-1"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Edit Course: {course.title} | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/{course_id}/edit')
@instructor_required
def post(session, course_id: int, title: str, code: str, term: str = "", department: str = "", 
         status: str = "active", description: str = ""):
    # Get current user
    user = users[session['auth']]
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Validate input
    if not title or not code:
        return "Course title and code are required."
    
    # Check for duplicate course code (but don't count the current course)
    for c in courses():
        if c.code == code and c.instructor_email == user.email and c.id != course_id:
            # Only check for duplicates from the same instructor
            if not hasattr(c, 'status') or c.status != "deleted":
                return "You already have another course with this code. Please use a different code."
    
    # Validate status
    if status not in ['active', 'closed', 'archived']:
        status = 'active'  # Default to active if invalid
    
    # Create timestamp
    now = datetime.now().isoformat()
    
    # Update course fields
    course.title = title
    course.code = code
    course.term = term
    course.department = department
    course.status = status
    course.description = description if hasattr(course, 'description') else None
    course.updated_at = now
    
    # Update the course in the database
    courses.update(course)
    
    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Course Updated Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your course \"{title}\" has been updated.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Back to Courses", href="/instructor/courses", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Manage Students", href=f"/instructor/courses/{course_id}/students", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )

@rt('/instructor/manage-students')
@instructor_required
def get(session):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            instructor_courses.append(course)
    
    # Process each course and get student enrollments
    courses_with_students = []
    
    for course in instructor_courses:
        students = []
        for enrollment in enrollments():
            if enrollment.course_id == course.id:
                # Get the student details
                try:
                    student = users[enrollment.student_email]
                    
                    # Determine enrollment status
                    status = "Invited" if not student.verified else "Enrolled"
                    
                    students.append({
                        "email": student.email,
                        "name": student.name if student.name else "(Not registered)",
                        "status": status,
                        "verified": student.verified
                    })
                except NotFoundError:
                    # Student record might be missing
                    students.append({
                        "email": enrollment.student_email,
                        "name": "(Not registered)",
                        "status": "Invited",
                        "verified": False
                    })
        
        if students:
            courses_with_students.append({
                "course": course,
                "students": students
            })
    
    # Create the main content
    if courses_with_students:
        # Create tables for each course with students
        course_tables = []
        
        for course_data in courses_with_students:
            course = course_data["course"]
            students = course_data["students"]
            
            # Sort students: enrolled first, then invited
            sorted_students = sorted(students, key=lambda s: (0 if s["verified"] else 1, s["email"]))
            
            # Create student rows
            student_rows = []
            for idx, student in enumerate(sorted_students):
                status_color = "green" if student["verified"] else "yellow"
                status_text = "Enrolled" if student["verified"] else "Invited"
                
                # Create row with actions
                row = Tr(
                    Td(f"{idx + 1}", cls="py-4 px-6"),
                    Td(student["email"], cls="py-4 px-6"),
                    Td(student["name"], cls="py-4 px-6"),
                    Td(status_badge(status_text, status_color), cls="py-4 px-6"),
                    Td(
                        Div(
                            Button("Resend", 
                               hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                               hx_target=f"#status-{course.id}-{idx}",
                               cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2") if not student["verified"] else "",
                            Button("Remove", 
                               hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                               hx_target="#message-area",
                               hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                               cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"),
                            cls="flex",
                            id=f"status-{course.id}-{idx}"
                        ),
                        cls="py-4 px-6"
                    ),
                    id=f"row-{course.id}-{idx}",
                    cls="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                )
                student_rows.append(row)
            
            # Create the course card with student table
            course_tables.append(
                Div(
                    H3(f"{course.title} ({course.code})", cls="text-xl font-bold text-indigo-900 mb-4"),
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    *[Th(h, cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100") for h in ["#", "Email", "Name", "Status", "Actions"]],
                                    cls="bg-indigo-50"
                                )
                            ),
                            Tbody(*student_rows),
                            cls="w-full"
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
                    ),
                    Div(
                        action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course.id}", icon="+"),
                        cls="mt-4"
                    ),
                    cls="mb-8"
                )
            )
        
        # Main content with all course tables
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            *course_tables,
            cls=""
        )
    else:
        # Show a message if no students enrolled in any courses
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P("You don't have any students enrolled in your courses yet.", 
                      cls="text-center text-gray-600 mb-6"),
                    Div(
                        A("Invite Students", href="/instructor/invite-students", 
                          cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="py-8"
                )
            ),
            cls=""
        )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Student Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite Students", color="indigo", href="/instructor/invite-students", icon="+"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Resend invitations if students haven't registered", cls="text-gray-600 mb-2 text-sm"),
            P("• Remove students who are no longer in your course", cls="text-gray-600 mb-2 text-sm"),
            P("• Students must verify their email to access the course", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Students | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/{course_id}/students')
@instructor_required
def get(session, course_id: int):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Get the course
    target_course = None
    for course in courses():
        if course.id == course_id and course.instructor_email == user.email:
            target_course = course
            break
    
    if not target_course:
        return "Course not found or you don't have permission to access it."
    
    # Get students for this course
    course_students = []
    for enrollment in enrollments():
        if enrollment.course_id == course_id:
            # Get the student details
            try:
                student = users[enrollment.student_email]
                
                # Determine enrollment status
                status = "Invited" if not student.verified else "Enrolled"
                
                course_students.append({
                    "email": student.email,
                    "name": student.name if student.name else "(Not registered)",
                    "status": status,
                    "verified": student.verified
                })
            except:
                # Student record might be missing
                course_students.append({
                    "email": enrollment.student_email,
                    "name": "(Not registered)",
                    "status": "Invited",
                    "verified": False
                })
    
    # Sort students: enrolled first, then invited
    sorted_students = sorted(course_students, key=lambda s: (0 if s["verified"] else 1, s["email"]))
    
    # Create the main content
    if sorted_students:
        # Create student rows
        student_rows = []
        for idx, student in enumerate(sorted_students):
            status_color = "green" if student["verified"] else "yellow"
            status_text = "Enrolled" if student["verified"] else "Invited"
            
            # Create row with actions
            row = Tr(
                Td(f"{idx + 1}", cls="py-4 px-6"),
                Td(student["email"], cls="py-4 px-6"),
                Td(student["name"], cls="py-4 px-6"),
                Td(status_badge(status_text, status_color), cls="py-4 px-6"),
                Td(
                    Div(
                        Button("Resend", 
                          hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                          hx_target=f"#status-{idx}",
                          cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2") if not student["verified"] else "",
                        Button("Remove", 
                          hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                          hx_target="#message-area",
                          hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                          cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"),
                        cls="flex",
                        id=f"status-{idx}"
                    ),
                    cls="py-4 px-6"
                ),
                id=f"row-{idx}",
                cls="border-b border-gray-100 hover:bg-gray-50 transition-colors"
            )
            student_rows.append(row)
        
        # Create the student table
        main_content = Div(
            H2(f"Students in {target_course.title} ({target_course.code})", cls="text-2xl font-bold text-indigo-900 mb-6"),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            Div(
                Table(
                    Thead(
                        Tr(
                            *[Th(h, cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100") for h in ["#", "Email", "Name", "Status", "Actions"]],
                            cls="bg-indigo-50"
                        )
                    ),
                    Tbody(*student_rows),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ),
            Div(
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="+"),
                cls="mt-6"
            ),
            cls=""
        )
    else:
        # Show a message if no students enrolled in this course
        main_content = Div(
            H2(f"Students in {target_course.title} ({target_course.code})", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P("You don't have any students enrolled in this course yet.", 
                      cls="text-center text-gray-600 mb-6"),
                    Div(
                        A("Invite Students", href=f"/instructor/invite-students?course_id={course_id}", 
                          cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="py-8"
                )
            ),
            cls=""
        )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="✉️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Details", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Title: {target_course.title}", cls="text-gray-600 mb-2"),
            P(f"Code: {target_course.code}", cls="text-gray-600 mb-2"),
            P(f"Students: {len(sorted_students)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Students in {target_course.code} | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/resend-invitation')
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # URL-decode the email to handle special characters like +
    email = urllib.parse.unquote(email)
    
    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break
    
    if not course:
        return "Course not found or you don't have permission to manage it."
    
    # Check if the student is enrolled in this course
    is_enrolled = False
    for enrollment in enrollments():
        if enrollment.course_id == course_id and enrollment.student_email == email:
            is_enrolled = True
            break
    
    if not is_enrolled:
        return "Student is not enrolled in this course."
    
    # Generate a token
    token = generate_verification_token(email)
    
    # Update the student's verification token
    try:
        student = users[email]
        student.verification_token = token
        users.update(student)
    except:
        # Student doesn't exist in the users table yet
        new_student = User(
            email=email,
            name="",
            password="",
            role=Role.STUDENT,
            verified=False,
            verification_token=token,
            approved=True,
            department="",
            reset_token="",
            reset_token_expiry=""
        )
        users.insert(new_student)
    
    # Send invitation email
    success, message = send_student_invitation_email(
        email, user.name, course.title, token
    )
    
    if success:
        return Div(
            P("Invitation sent successfully", cls="text-green-600"),
            Div(cls="mt-1 text-xs text-gray-500")
        )
    else:
        return Div(
            P("Failed to send invitation", cls="text-red-600"),
            Div(message, cls="mt-1 text-xs text-gray-500")
        )

@rt('/instructor/remove-student')
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # URL-decode the email to handle special characters like +
    email = urllib.parse.unquote(email)
    
    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break
    
    if not course:
        return Div(
            P("Course not found or you don't have permission to manage it.", cls="text-red-600 font-medium"),
            cls="p-4 bg-red-50 rounded-lg"
        )
    
    try:
        # Import datetime for timestamp updates
        from datetime import datetime
        
        # Simpler direct deletion approach
        deleted_count = 0
        
        # Convert to ensure we're comparing the right types
        course_id_int = int(course_id)
        
        # Find and delete matching enrollments directly
        for e in list(enrollments()):
            e_course_id = int(e.course_id)
            if e_course_id == course_id_int and e.student_email == email:
                print(f"Deleting enrollment: {e.id}, Course: {e.course_id}, Student: {e.student_email}")
                enrollments.delete(e.id)
                deleted_count += 1
        
        # Check if we deleted anything
        if deleted_count == 0:
            return Div(
                P(f"Student {email} not found in this course.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg"
            )
        
        # Update the student account status only if this was their only enrollment
        student_has_other_enrollments = False
        for e in enrollments():
            if e.student_email == email:
                student_has_other_enrollments = True
                break
        
        # If student has no other enrollments, mark their account as inactive
        if not student_has_other_enrollments:
            try:
                student = users[email]
                if student.role == Role.STUDENT and hasattr(student, 'status'):
                    student.status = "inactive"
                    student.last_active = datetime.now().isoformat()
                    users.update(student)
            except:
                # If we can't find the student, that's okay - they might not have registered yet
                pass
        
        # Return success with auto-refresh
        return Div(
            P(f"Student {email} has been removed from the course.", cls="text-green-600"),
            Script("""
                console.log('Student removal successful');
                setTimeout(function() { 
                    console.log('Reloading page...');
                    window.location.href = window.location.href; 
                }, 1500);
            """),
            cls="bg-green-50 p-4 rounded-lg"
        )
    except Exception as e:
        return Div(
            P(f"Error removing student: {str(e)}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )

@rt('/instructor/invite-students')
@instructor_required
def get(session, course_id: int = None):
    # Get current user
    user = users[session['auth']]
    
    # Get components directly from top-level imports
    
    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            instructor_courses.append(course)
    
    # Debug print
    print(f"Found {len(instructor_courses)} courses for instructor {user.email}")
    for c in instructor_courses:
        print(f"  Course: {c.id} - {c.title} ({c.code})")
    
    # Create invitation form
    form_content = Div(
        H2("Invite Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Invite students to join your course. Students will receive an email with instructions to create their account.", 
              cls="mb-6 text-gray-600"),
            
            # Show a message if there are no courses
            (Form(
                Div(
                    Label("Course", for_="course_id", cls="block text-indigo-900 font-medium mb-1"),
                    Select(
                        Option(f"Select a course", value="", selected=True if not course_id else False, disabled=True),
                        *[Option(f"{c.title} ({c.code})", value=str(c.id), selected=(c.id == course_id if course_id else False)) for c in instructor_courses],
                        id="course_id",
                        name="course_id",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Student Emails", for_="student_emails", cls="block text-indigo-900 font-medium mb-1"),
                    P("Enter one email address per line", cls="text-sm text-gray-500 mb-1"),
                    Textarea(
                        id="student_emails",
                        name="student_emails",
                        rows="5",
                        placeholder="student1@example.com\nstudent2@example.com",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-6"
                ),
                Div(
                    Button("Send Invitations", type="submit", cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="mb-4"
                ),
                Div(id="form-result", cls="mt-3 w-full"),
                hx_post="/instructor/invite-students",
                hx_target="#form-result",
                hx_swap="innerHTML",
                cls="w-full"
            ) if instructor_courses else 
            Div(
                P("You don't have any courses yet.", cls="text-red-500 mb-4"),
                P("Please create a course first before inviting students.", cls="text-gray-600 mb-4"),
                A("Create a New Course", href="/instructor/courses/new", 
                  cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="text-center py-8"
            )),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Create Course", color="indigo", href="/instructor/courses/new", icon="+"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Students will receive an email with instructions to join", cls="text-gray-600 mb-2 text-sm"),
            P("• They can set up their account after clicking the email link", cls="text-gray-600 mb-2 text-sm"),
            P("• Upload a CSV file to invite many students at once", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Invite Students", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/invite-students')
@instructor_required
def post(session, course_id: int, student_emails: str, refresh_form: bool = False):
    """
    Handle the student invitation form submission.
    Returns a clear confirmation message after invitations are sent.
    """
    # Get current user and course
    user = users[session['auth']]
    
    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break
    
    if not course:
        return Div(
            P("Course not found or you don't have permission to invite students to this course.",
              cls="text-red-600 font-medium"),
            cls="p-4 bg-red-50 rounded-lg"
        )
    
    # Process student emails
    emails = [email.strip() for email in student_emails.split('\n') if email.strip()]
    
    if not emails:
        return Div(
            P("Please enter at least one student email.",
              cls="text-amber-600 font-medium"),
            cls="p-4 bg-amber-50 rounded-lg"
        )
    
    # Simple tracking lists
    sent_emails = []
    already_enrolled_emails = []
    error_emails = []
    
    # Get next enrollment ID
    next_id = 1
    try:
        enrollment_ids = [e.id for e in enrollments()]
        if enrollment_ids:
            next_id = max(enrollment_ids) + 1
    except Exception as e:
        print(f"Error getting next enrollment ID: {e}")
    
    # Process each email
    for email in emails:
        # Check if already enrolled
        is_enrolled = False
        for enrollment in enrollments():
            if hasattr(enrollment, 'student_email') and enrollment.student_email == email and enrollment.course_id == course_id:
                is_enrolled = True
                break
        
        if is_enrolled:
            already_enrolled_emails.append(email)
            continue
        
        # Generate token for the invitation
        token = generate_verification_token(email)
        
        # Check if user exists
        try:
            users[email]  # Just check if exists
        except:
            # Create new student account if doesn't exist
            new_student = User(
                email=email,
                name="",  # Will be set during registration
                password="",  # Will be set during registration
                role=Role.STUDENT,
                verified=False,
                verification_token=token,
                approved=True,  # Students are auto-approved
                department="",
                reset_token="",
                reset_token_expiry=""
            )
            users.insert(new_student)
        
        # Create enrollment record
        new_enrollment = Enrollment(
            id=next_id,
            course_id=course_id,
            student_email=email
        )
        enrollments.insert(new_enrollment)
        next_id += 1
        
        # Send invitation email
        success, message = send_student_invitation_email(
            email, user.name, course.title, token
        )
        
        if success:
            sent_emails.append(email)
        else:
            error_emails.append(f"{email} (Email error: {message})")
    
    # Get components directly from top-level imports
    
    # Generate summary message
    message_parts = []
    if sent_emails:
        message_parts.append(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully")
    if already_enrolled_emails:
        message_parts.append(f"{len(already_enrolled_emails)} already enrolled")
    if error_emails:
        message_parts.append(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed")
    
    summary = ", ".join(message_parts)
    
    # Build complete page with confirmation message
    confirmation_content = Div(
        # Success Banner
        Div(
            Div(
                Span("✅", cls="text-5xl mr-5"),
                Div(
                    H2("Student Invitations Sent!", cls="text-2xl font-bold text-green-700 mb-2"),
                    P(summary, cls="text-xl text-gray-700"),
                    cls=""
                ),
                cls="flex items-center"
            ),
            cls="bg-green-50 p-8 rounded-xl shadow-md border-2 border-green-500 mb-6 text-center"
        ),
        
        # Detailed Results
        Div(
            H3("Invitation Results", cls="text-xl font-bold text-indigo-900 mb-4"),
            # Successfully sent
            (Div(
                Div(
                    Span("✅", cls="text-2xl mr-3"),
                    Div(
                        H4("Invitations Sent", cls="text-lg font-bold text-green-700"),
                        P(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in sent_emails[:8]],
                    P(f"... and {len(sent_emails) - 8} more" if len(sent_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if sent_emails else "",
                cls="mb-5"
            ) if sent_emails else ""),
            
            # Already enrolled
            (Div(
                Div(
                    Span("ℹ️", cls="text-2xl mr-3"),
                    Div(
                        H4("Already Enrolled", cls="text-lg font-bold text-amber-700"),
                        P(f"{len(already_enrolled_emails)} student{'' if len(already_enrolled_emails)==1 else 's'} already in this course", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in already_enrolled_emails[:8]],
                    P(f"... and {len(already_enrolled_emails) - 8} more" if len(already_enrolled_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if already_enrolled_emails and len(already_enrolled_emails) <= 15 else "",
                cls="mb-5"
            ) if already_enrolled_emails else ""),
            
            # Errors
            (Div(
                Div(
                    Span("❌", cls="text-2xl mr-3"),
                    Div(
                        H4("Failed Invitations", cls="text-lg font-bold text-red-700"),
                        P(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed to send", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(error, cls="mb-1") for error in error_emails],
                    cls="ml-10 text-sm"
                ) if error_emails else "",
                (P("Note: Check your SMTP settings in the .env file.", 
                  cls="text-xs text-gray-500 mt-2 ml-12")) if error_emails else "",
                cls="mb-5"
            ) if error_emails else ""),
            
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 mb-6"
        ),
        
        # Action buttons
        Div(
            Div(
                A("Return to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-200 mr-4 font-medium"),
                A("Invite More Students", href=f"/instructor/invite-students?course_id={course_id}", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 mr-4 font-medium"),
                A("View All Students", href="/instructor/manage-students", 
                  cls="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 font-medium"),
                cls="flex justify-center flex-wrap gap-4"
            ),
            cls="text-center"
        ),
        
        cls="max-w-4xl mx-auto px-4"
    )
    
    # Return as full page rather than just updating a div
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="+"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Redirect to a dedicated confirmation page instead of returning the HTML directly
    # Store the information in the session for retrieval by the confirmation route
    session['invitation_results'] = {
        'sent_emails': sent_emails,
        'already_enrolled_emails': already_enrolled_emails, 
        'error_emails': error_emails,
        'course_id': course_id,
        'course_title': course.title
    }
    
    # Redirect to the dedicated confirmation page
    return HttpHeader('HX-Redirect', '/instructor/invite-students/confirmation')
    
# --- Invitation Confirmation Route ---
@rt('/instructor/invite-students/confirmation')
@instructor_required
def get(session):
    """Display invitation results in a dedicated page"""
    # Get components directly from top-level imports
    
    # Get the invitation results from the session
    results = session.get('invitation_results', {})
    if not results:
        # If there are no results, redirect to the invitation page
        return RedirectResponse('/instructor/invite-students', status_code=303)
    
    sent_emails = results.get('sent_emails', [])
    already_enrolled_emails = results.get('already_enrolled_emails', [])
    error_emails = results.get('error_emails', [])
    course_id = results.get('course_id')
    course_title = results.get('course_title', 'Unknown Course')
    
    # Generate summary message
    message_parts = []
    if sent_emails:
        message_parts.append(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully")
    if already_enrolled_emails:
        message_parts.append(f"{len(already_enrolled_emails)} already enrolled")
    if error_emails:
        message_parts.append(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed")
    
    summary = ", ".join(message_parts)
    
    # Build complete page with confirmation message
    confirmation_content = Div(
        # Success Banner
        Div(
            Div(
                Span("✅", cls="text-5xl mr-5"),
                Div(
                    H2("Student Invitations Sent!", cls="text-2xl font-bold text-green-700 mb-2"),
                    P(summary, cls="text-xl text-gray-700"),
                    cls=""
                ),
                cls="flex items-center"
            ),
            cls="bg-green-50 p-8 rounded-xl shadow-md border-2 border-green-500 mb-6 text-center"
        ),
        
        # Detailed Results
        Div(
            H3("Invitation Results", cls="text-xl font-bold text-indigo-900 mb-4"),
            # Successfully sent
            (Div(
                Div(
                    Span("✅", cls="text-2xl mr-3"),
                    Div(
                        H4("Invitations Sent", cls="text-lg font-bold text-green-700"),
                        P(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in sent_emails[:8]],
                    P(f"... and {len(sent_emails) - 8} more" if len(sent_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if sent_emails else "",
                cls="mb-5"
            ) if sent_emails else ""),
            
            # Already enrolled
            (Div(
                Div(
                    Span("ℹ️", cls="text-2xl mr-3"),
                    Div(
                        H4("Already Enrolled", cls="text-lg font-bold text-amber-700"),
                        P(f"{len(already_enrolled_emails)} student{'' if len(already_enrolled_emails)==1 else 's'} already in this course", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in already_enrolled_emails[:8]],
                    P(f"... and {len(already_enrolled_emails) - 8} more" if len(already_enrolled_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if already_enrolled_emails and len(already_enrolled_emails) <= 15 else "",
                cls="mb-5"
            ) if already_enrolled_emails else ""),
            
            # Errors
            (Div(
                Div(
                    Span("❌", cls="text-2xl mr-3"),
                    Div(
                        H4("Failed Invitations", cls="text-lg font-bold text-red-700"),
                        P(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed to send", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(error, cls="mb-1") for error in error_emails],
                    cls="ml-10 text-sm"
                ) if error_emails else "",
                (P("Note: Check your SMTP settings in the .env file.", 
                  cls="text-xs text-gray-500 mt-2 ml-12")) if error_emails else "",
                cls="mb-5"
            ) if error_emails else ""),
            
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 mb-6"
        ),
        
        # Action buttons
        Div(
            Div(
                A("Return to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-200 mr-4 font-medium"),
                A("Invite More Students", href=f"/instructor/invite-students?course_id={course_id}", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 mr-4 font-medium"),
                A("View All Students", href="/instructor/manage-students", 
                  cls="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 font-medium"),
                cls="flex justify-center flex-wrap gap-4"
            ),
            cls="text-center"
        ),
        
        cls="max-w-4xl mx-auto px-4"
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="+"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return a complete page with the confirmation
    return dashboard_layout(
        "Invitation Results | FeedForward",
        sidebar_content,
        confirmation_content,
        user_role=Role.INSTRUCTOR
    )