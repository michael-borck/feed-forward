"""
Instructor course management routes
"""

from datetime import datetime
from typing import Optional

from fasthtml import common as fh

from app import instructor_required, rt
from app.models.course import Course, courses, enrollments
from app.models.user import Role, users
from app.utils.ui import action_button, dashboard_layout, status_badge


@rt("/instructor/courses")
@instructor_required
def instructor_courses_list(session, request):
    """Course listing page for instructors"""
    # Get current user
    user = users[session["auth"]]

    # Get all courses taught by this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, "status") and course.status == "deleted":
                continue

            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1

            # Add to list with student count
            instructor_courses.append((course, student_count))

    # Sort courses by creation date (newest first)
    instructor_courses.sort(
        key=lambda x: x[0].created_at if hasattr(x[0], "created_at") else "",
        reverse=True,
    )

    # Create the main content
    main_content = fh.Div(
        # Header with action button
        fh.Div(
            fh.H2("Course Management", cls="text-2xl font-bold text-indigo-900"),
            action_button(
                "Create New Course",
                color="indigo",
                href="/instructor/courses/new",
                icon="+",
            ),
            cls="flex justify-between items-center mb-6",
        ),
        # Course listing or empty state
        (
            fh.Div(
                fh.P(
                    f"You have {len(instructor_courses)} {'course' if len(instructor_courses) == 1 else 'courses'}.",
                    cls="text-gray-600 mb-6",
                ),
                # Course table with actions
                fh.Div(
                    fh.Table(
                        fh.Thead(
                            fh.Tr(
                                fh.Th(
                                    "Course Title",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Code",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Term",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Status",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Students",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Actions",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                            ),
                            cls="bg-indigo-50",
                        ),
                        fh.Tbody(
                            *(
                                fh.Tr(
                                    # Course title
                                    fh.Td(course.title, cls="py-4 px-6"),
                                    # Course code
                                    fh.Td(course.code, cls="py-4 px-6"),
                                    # Term
                                    fh.Td(
                                        getattr(course, "term", "Current") or "Current",
                                        cls="py-4 px-6",
                                    ),
                                    # Status badge
                                    fh.Td(
                                        status_badge(
                                            getattr(
                                                course, "status", "active"
                                            ).capitalize()
                                            or "Active",
                                            "green"
                                            if getattr(course, "status", "active")
                                            == "active"
                                            else "yellow"
                                            if getattr(course, "status", "active")
                                            == "closed"
                                            else "gray",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    # Student count
                                    fh.Td(str(student_count), cls="py-4 px-6"),
                                    # Action buttons
                                    fh.Td(
                                        fh.Div(
                                            fh.A(
                                                "Students",
                                                href=f"/instructor/courses/{course.id}/students",
                                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                                            ),
                                            fh.A(
                                                "Edit",
                                                href=f"/instructor/courses/{course.id}/edit",
                                                cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                            ),
                                            fh.A(
                                                "Assignments",
                                                href=f"/instructor/courses/{course.id}/assignments",
                                                cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for course, student_count in instructor_courses
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                ),
                cls="",
            )
            if instructor_courses
            else fh.Div(
                fh.P(
                    "You don't have any courses yet. Create your first course to get started.",
                    cls="text-center text-gray-600 mb-6",
                ),
                fh.Div(
                    fh.A(
                        "Create New Course",
                        href="/instructor/courses/new",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="text-center",
                ),
                cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4",
            )
        ),
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="←"
                ),
                action_button(
                    "Create Course",
                    color="indigo",
                    href="/instructor/courses/new",
                    icon="+",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href="/instructor/manage-students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        fh.Div(
            fh.H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(f"Total Courses: {len(instructor_courses)}", cls="text-gray-600 mb-2"),
            fh.P(
                f"Active Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'active')}",
                cls="text-green-600 mb-2",
            ),
            fh.P(
                f"Closed Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'closed')}",
                cls="text-amber-600 mb-2",
            ),
            fh.P(
                f"Archived Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'archived')}",
                cls="text-gray-600 mb-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Courses | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path,
    )


@rt("/instructor/courses/new")
@instructor_required
def instructor_courses_new(session):
    """Course creation page for instructors"""
    # Get current user
    users[session["auth"]]

    # Main content
    main_content = fh.Div(
        fh.H2("Create New Course", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Course creation form
        fh.Form(
            # Course Title
            fh.Div(
                fh.Label(
                    "Course Title",
                    for_="title",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="title",
                    name="title",
                    placeholder="e.g., Introduction to Computer Science",
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Course Code
            fh.Div(
                fh.Label(
                    "Course Code",
                    for_="code",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="code",
                    name="code",
                    placeholder="e.g., CS101",
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Term
            fh.Div(
                fh.Label(
                    "Term",
                    for_="term",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="term",
                    name="term",
                    placeholder="e.g., Fall 2024",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Description
            fh.Div(
                fh.Label(
                    "Description",
                    for_="description",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Textarea(
                    id="description",
                    name="description",
                    placeholder="Brief description of the course",
                    rows=4,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-6",
            ),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Create Course",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                fh.A(
                    "Cancel",
                    href="/instructor/courses",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action="/instructor/courses/new",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Create Course", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(
                "Fill in the course details to create a new course.",
                cls="text-gray-600 mb-4",
            ),
            action_button(
                "Back to Courses", color="gray", href="/instructor/courses", icon="←"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    return dashboard_layout(
        "Create Course | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path="/instructor/courses/new",
    )


@rt("/instructor/courses/new")
@instructor_required
def instructor_courses_create(
    session, title: str, code: str, term: Optional[str] = None, description: Optional[str] = None
):
    """Create a new course"""
    # Get current user
    user = users[session["auth"]]

    # Validate inputs
    if not title or not code:
        return fh.RedirectResponse("/instructor/courses/new", status_code=303)

    # Create the course
    new_course = Course(
        id=None,  # Will be auto-assigned
        title=title.strip(),
        code=code.strip().upper(),
        term=term.strip() if term else "Current",
        description=description.strip() if description else "",
        instructor_email=user.email,
        status="active",
        created_at=datetime.now(),
    )

    # Save to database
    try:
        course_id = courses.insert(new_course)
        return fh.RedirectResponse(
            f"/instructor/courses/{course_id}/students", status_code=303
        )
    except Exception:
        # Handle duplicate course codes or other errors
        return fh.RedirectResponse("/instructor/courses/new", status_code=303)


@rt("/instructor/courses/{course_id}/edit")
@instructor_required
def instructor_course_edit(session, course_id: int):
    """Edit course page"""
    # Get current user
    user = users[session["auth"]]

    # Get the course
    try:
        course = courses[course_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if course.instructor_email != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Main content
    main_content = fh.Div(
        fh.H2(
            f"Edit Course: {course.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        # Course edit form
        fh.Form(
            # Course Title
            fh.Div(
                fh.Label(
                    "Course Title",
                    for_="title",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="title",
                    name="title",
                    value=course.title,
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Course Code
            fh.Div(
                fh.Label(
                    "Course Code",
                    for_="code",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="code",
                    name="code",
                    value=course.code,
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Term
            fh.Div(
                fh.Label(
                    "Term",
                    for_="term",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="term",
                    name="term",
                    value=getattr(course, "term", "Current") or "Current",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Status
            fh.Div(
                fh.Label(
                    "Status",
                    for_="status",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Select(
                    fh.Option(
                        "Active",
                        value="active",
                        selected=getattr(course, "status", "active") == "active",
                    ),
                    fh.Option(
                        "Closed",
                        value="closed",
                        selected=getattr(course, "status", "active") == "closed",
                    ),
                    fh.Option(
                        "Archived",
                        value="archived",
                        selected=getattr(course, "status", "active") == "archived",
                    ),
                    id="status",
                    name="status",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Description
            fh.Div(
                fh.Label(
                    "Description",
                    for_="description",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Textarea(
                    getattr(course, "description", "") or "",
                    id="description",
                    name="description",
                    rows=4,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-6",
            ),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Save Changes",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                fh.A(
                    "Cancel",
                    href="/instructor/courses",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action=f"/instructor/courses/{course_id}/edit",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Edit Course", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(f"Course Code: {course.code}", cls="text-gray-600 mb-2"),
            fh.P(
                f"Students: {sum(1 for e in enrollments() if e.course_id == course.id)}",
                cls="text-gray-600 mb-4",
            ),
            action_button(
                "View Students",
                color="teal",
                href=f"/instructor/courses/{course_id}/students",
                icon="👥",
            ),
            action_button(
                "View Assignments",
                color="indigo",
                href=f"/instructor/courses/{course_id}/assignments",
                icon="📝",
            ),
            action_button(
                "Back to Courses", color="gray", href="/instructor/courses", icon="←"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100 space-y-3",
        )
    )

    return dashboard_layout(
        f"Edit {course.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/courses/{course_id}/edit",
    )


@rt("/instructor/courses/{course_id}/edit")
@instructor_required
def instructor_course_update(
    session,
    course_id: int,
    title: str,
    code: str,
    term: Optional[str] = None,
    status: Optional[str] = None,
    description: Optional[str] = None,
):
    """Update course details"""
    # Get current user
    user = users[session["auth"]]

    # Get the course
    try:
        course = courses[course_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if course.instructor_email != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Update course details
    course.title = title.strip()
    course.code = code.strip().upper()
    course.term = term.strip() if term else "Current"
    course.status = status if status in ["active", "closed", "archived"] else "active"
    course.description = description.strip() if description else ""

    # Save changes
    courses.update(course)

    return fh.RedirectResponse("/instructor/courses", status_code=303)
