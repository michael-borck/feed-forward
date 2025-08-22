"""
Instructor assignment management routes
"""

from datetime import datetime
from typing import Optional

from fasthtml import common as fh

from app import instructor_required, rt
from app.models.assignment import (
    Assignment,
    Rubric,
    RubricCategory,
    assignments,
    rubric_categories,
    rubrics,
)
from app.models.course import courses
from app.models.user import Role, users
from app.utils.ui import action_button, dashboard_layout, status_badge


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
        if hasattr(target_course, "status") and target_course.status == "deleted":
            return None, "This course has been deleted."

        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {e!s}"


@rt("/instructor/courses/{course_id}/assignments")
@instructor_required
def instructor_assignments_list(session, course_id: int):
    """Shows all assignments for a specific course"""
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return fh.Div(
            fh.H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            fh.P(error, cls="text-gray-700 mb-4"),
            fh.A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get all assignments for this course
    course_assignments = []
    for assignment in assignments():
        if assignment.course_id == course_id and assignment.created_by == user.email:
            # Skip deleted assignments
            if hasattr(assignment, "status") and assignment.status == "deleted":
                continue
            course_assignments.append(assignment)

    # Sort assignments by creation date (newest first)
    course_assignments.sort(
        key=lambda x: x.created_at if hasattr(x, "created_at") else "", reverse=True
    )

    # Create the main content
    main_content = fh.Div(
        # Header with action button
        fh.Div(
            fh.H2(
                f"Assignments for {course.title}",
                cls="text-2xl font-bold text-indigo-900",
            ),
            action_button(
                "Create New Assignment",
                color="indigo",
                href=f"/instructor/courses/{course_id}/assignments/new",
                icon="+",
            ),
            cls="flex justify-between items-center mb-6",
        ),
        # Assignment listing or empty state
        (
            fh.Div(
                fh.P(
                    f"This course has {len(course_assignments)} {'assignment' if len(course_assignments) == 1 else 'assignments'}.",
                    cls="text-gray-600 mb-6",
                ),
                # Assignment table with actions
                fh.Div(
                    fh.Table(
                        fh.Thead(
                            fh.Tr(
                                fh.Th(
                                    "Title",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Status",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Due Date",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                fh.Th(
                                    "Drafts",
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
                                    # Assignment title
                                    fh.Td(assignment.title, cls="py-4 px-6"),
                                    # Status badge
                                    fh.Td(
                                        status_badge(
                                            getattr(
                                                assignment, "status", "draft"
                                            ).capitalize(),
                                            "gray"
                                            if getattr(assignment, "status", "draft")
                                            == "draft"
                                            else "green"
                                            if getattr(assignment, "status", "draft")
                                            == "active"
                                            else "yellow"
                                            if getattr(assignment, "status", "draft")
                                            == "closed"
                                            else "blue"
                                            if getattr(assignment, "status", "draft")
                                            == "archived"
                                            else "red",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    # Due date
                                    fh.Td(
                                        getattr(assignment, "due_date", "Not set")
                                        or "Not set",
                                        cls="py-4 px-6",
                                    ),
                                    # Max drafts allowed
                                    fh.Td(
                                        str(getattr(assignment, "max_drafts", 1) or 1),
                                        cls="py-4 px-6",
                                    ),
                                    # Action buttons
                                    fh.Td(
                                        fh.Div(
                                            fh.A(
                                                "Edit",
                                                href=f"/instructor/assignments/{assignment.id}/edit",
                                                cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                            ),
                                            fh.A(
                                                "Rubric",
                                                href=f"/instructor/assignments/{assignment.id}/rubric",
                                                cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700 mr-2",
                                            ),
                                            fh.A(
                                                "Submissions",
                                                href=f"/instructor/assignments/{assignment.id}/submissions",
                                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for assignment in course_assignments
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                ),
                cls="",
            )
            if course_assignments
            else fh.Div(
                fh.P(
                    "This course doesn't have any assignments yet. Create your first assignment to get started.",
                    cls="text-center text-gray-600 mb-6",
                ),
                fh.Div(
                    fh.A(
                        "Create New Assignment",
                        href=f"/instructor/courses/{course_id}/assignments/new",
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
                    "Back to Courses",
                    color="gray",
                    href="/instructor/courses",
                    icon="←",
                ),
                action_button(
                    "Course Details",
                    color="blue",
                    href=f"/instructor/courses/{course_id}/edit",
                    icon="📝",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href=f"/instructor/courses/{course_id}/students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        fh.Div(
            fh.H3("Assignment Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Create Assignment",
                    color="indigo",
                    href=f"/instructor/courses/{course_id}/assignments/new",
                    icon="+",
                ),
                cls="space-y-3",
            ),
            fh.P(
                "Assignment Statuses:",
                cls="text-sm text-gray-600 font-medium mt-4 mb-2",
            ),
            fh.P("Draft: Only visible to you", cls="text-xs text-gray-600 mb-1"),
            fh.P("Active: Available to students", cls="text-xs text-gray-600 mb-1"),
            fh.P("Closed: No new submissions", cls="text-xs text-gray-600 mb-1"),
            fh.P("Archived: Hidden from students", cls="text-xs text-gray-600 mb-1"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return dashboard_layout(
        f"Assignments for {course.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/courses/{course_id}/assignments/new")
@instructor_required
def instructor_assignments_new(session, course_id: int):
    """Create new assignment page"""
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    if error:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Main content
    main_content = fh.Div(
        fh.H2("Create New Assignment", cls="text-2xl font-bold text-indigo-900 mb-6"),
        fh.Form(
            # Assignment Title
            fh.Div(
                fh.Label(
                    "Assignment Title",
                    for_="title",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="title",
                    name="title",
                    placeholder="e.g., Essay on Climate Change",
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Instructions
            fh.Div(
                fh.Label(
                    "Instructions",
                    for_="instructions",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Textarea(
                    id="instructions",
                    name="instructions",
                    placeholder="Provide clear instructions for the assignment",
                    rows=6,
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Due Date
            fh.Div(
                fh.Label(
                    "Due Date",
                    for_="due_date",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="datetime-local",
                    id="due_date",
                    name="due_date",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Max Drafts
            fh.Div(
                fh.Label(
                    "Maximum Drafts Allowed",
                    for_="max_drafts",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="number",
                    id="max_drafts",
                    name="max_drafts",
                    value="3",
                    min="1",
                    max="10",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                fh.P(
                    "Students can submit multiple drafts for feedback",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-6",
            ),
            # Hidden course ID
            fh.Input(type="hidden", name="course_id", value=str(course_id)),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Create Assignment",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                fh.A(
                    "Cancel",
                    href=f"/instructor/courses/{course_id}/assignments",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action=f"/instructor/courses/{course_id}/assignments/new",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Create Assignment", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(f"Course: {course.title}", cls="text-gray-600 mb-4"),
            action_button(
                "Back to Assignments",
                color="gray",
                href=f"/instructor/courses/{course_id}/assignments",
                icon="←",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    return dashboard_layout(
        "Create Assignment | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/courses/{course_id}/assignments/new",
    )


@rt("/instructor/courses/{course_id}/assignments/new")
@instructor_required
def instructor_assignments_create(
    session,
    course_id: int,
    title: str,
    instructions: str,
    due_date: Optional[str] = None,
    max_drafts: int = 3,
):
    """Create a new assignment"""
    # Get current user
    user = users[session["auth"]]

    # Verify course ownership
    course, error = get_instructor_course(course_id, user.email)
    if error:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Create the assignment
    new_assignment = Assignment(
        id=None,  # Will be auto-assigned
        course_id=course_id,
        title=title.strip(),
        instructions=instructions.strip(),
        due_date=due_date if due_date else None,
        max_drafts=max_drafts,
        status="draft",
        created_by=user.email,
        created_at=datetime.now(),
    )

    # Save to database
    try:
        assignment_id = assignments.insert(new_assignment)
        return fh.RedirectResponse(
            f"/instructor/assignments/{assignment_id}/edit", status_code=303
        )
    except Exception:
        return fh.RedirectResponse(
            f"/instructor/courses/{course_id}/assignments/new", status_code=303
        )


@rt("/instructor/assignments/{assignment_id}")
@instructor_required
def instructor_assignment_view(session, assignment_id: int):
    """View assignment details"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment
    try:
        assignment = assignments[assignment_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if assignment.created_by != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Get the course
    course = None
    for c in courses():
        if c.id == assignment.course_id:
            course = c
            break

    if not course:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Redirect to edit page for now
    return fh.RedirectResponse(
        f"/instructor/assignments/{assignment_id}/edit", status_code=303
    )


@rt("/instructor/assignments/{assignment_id}/status")
@instructor_required
def instructor_assignment_update_status(session, assignment_id: int, status: str):
    """Update assignment status"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment
    try:
        assignment = assignments[assignment_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if assignment.created_by != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Update status
    valid_statuses = ["draft", "active", "closed", "archived"]
    if status in valid_statuses:
        assignment.status = status
        assignments.update(assignment)

    # Get course for redirect
    course_id = assignment.course_id
    return fh.RedirectResponse(
        f"/instructor/courses/{course_id}/assignments", status_code=303
    )


@rt("/instructor/assignments/{assignment_id}/edit")
@instructor_required
def instructor_assignment_edit(session, assignment_id: int):
    """Edit assignment page"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment
    try:
        assignment = assignments[assignment_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if assignment.created_by != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Get the course
    course = None
    for c in courses():
        if c.id == assignment.course_id:
            course = c
            break

    if not course:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Main content
    main_content = fh.Div(
        fh.H2(
            f"Edit Assignment: {assignment.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        fh.Form(
            # Assignment Title
            fh.Div(
                fh.Label(
                    "Assignment Title",
                    for_="title",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="title",
                    name="title",
                    value=assignment.title,
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Instructions
            fh.Div(
                fh.Label(
                    "Instructions",
                    for_="instructions",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Textarea(
                    assignment.instructions,
                    id="instructions",
                    name="instructions",
                    rows=6,
                    required=True,
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
                        "Draft",
                        value="draft",
                        selected=getattr(assignment, "status", "draft") == "draft",
                    ),
                    fh.Option(
                        "Active",
                        value="active",
                        selected=getattr(assignment, "status", "draft") == "active",
                    ),
                    fh.Option(
                        "Closed",
                        value="closed",
                        selected=getattr(assignment, "status", "draft") == "closed",
                    ),
                    fh.Option(
                        "Archived",
                        value="archived",
                        selected=getattr(assignment, "status", "draft") == "archived",
                    ),
                    id="status",
                    name="status",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Due Date
            fh.Div(
                fh.Label(
                    "Due Date",
                    for_="due_date",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="datetime-local",
                    id="due_date",
                    name="due_date",
                    value=getattr(assignment, "due_date", "") or "",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Max Drafts
            fh.Div(
                fh.Label(
                    "Maximum Drafts Allowed",
                    for_="max_drafts",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="number",
                    id="max_drafts",
                    name="max_drafts",
                    value=str(getattr(assignment, "max_drafts", 3) or 3),
                    min="1",
                    max="10",
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
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action=f"/instructor/assignments/{assignment_id}/edit",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Assignment Details", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(f"Course: {course.title}", cls="text-gray-600 mb-2"),
            fh.P(
                f"Created: {assignment.created_at.strftime('%B %d, %Y') if hasattr(assignment, 'created_at') and assignment.created_at else 'Unknown'}",
                cls="text-gray-600 mb-4",
            ),
            fh.Div(
                action_button(
                    "View Rubric",
                    color="teal",
                    href=f"/instructor/assignments/{assignment_id}/rubric",
                    icon="📊",
                ),
                action_button(
                    "View Submissions",
                    color="indigo",
                    href=f"/instructor/assignments/{assignment_id}/submissions",
                    icon="📝",
                ),
                action_button(
                    "Back to Assignments",
                    color="gray",
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    icon="←",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    return dashboard_layout(
        f"Edit {assignment.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/edit",
    )


@rt("/instructor/assignments/{assignment_id}/edit")
@instructor_required
def instructor_assignment_update(
    session,
    assignment_id: int,
    title: str,
    instructions: str,
    status: str = "draft",
    due_date: Optional[str] = None,
    max_drafts: int = 3,
):
    """Update assignment details"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment
    try:
        assignment = assignments[assignment_id]
    except Exception:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Verify ownership
    if assignment.created_by != user.email:
        return fh.RedirectResponse("/instructor/courses", status_code=303)

    # Update assignment
    assignment.title = title.strip()
    assignment.instructions = instructions.strip()
    assignment.status = (
        status if status in ["draft", "active", "closed", "archived"] else "draft"
    )
    assignment.due_date = due_date if due_date else None
    assignment.max_drafts = max_drafts

    # Save changes
    assignments.update(assignment)

    return fh.RedirectResponse(
        f"/instructor/courses/{assignment.course_id}/assignments", status_code=303
    )


def get_instructor_assignment(assignment_id, instructor_email):
    """
    Get an assignment by ID, checking that it belongs to the instructor.
    Returns (assignment, error_message) tuple.
    """
    # Find the assignment
    target_assignment = None
    try:
        for assignment in assignments():
            if assignment.id == assignment_id:
                target_assignment = assignment
                break

        if not target_assignment:
            return None, "Assignment not found."

        # Check if this instructor owns the assignment
        if target_assignment.created_by != instructor_email:
            return None, "You don't have permission to access this assignment."

        # Skip deleted assignments
        if (
            hasattr(target_assignment, "status")
            and target_assignment.status == "deleted"
        ):
            return None, "This assignment has been deleted."

        return target_assignment, None
    except Exception as e:
        return None, f"Error accessing assignment: {e!s}"


@rt("/instructor/assignments/{assignment_id}/rubric")
@instructor_required
def instructor_rubric_view(session, assignment_id: int):
    """View and manage rubric for an assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return fh.Div(
            fh.H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            fh.P(error, cls="text-gray-700 mb-4"),
            fh.A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get the course this assignment belongs to
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return fh.Div(
            fh.H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            fh.P(course_error, cls="text-gray-700 mb-4"),
            fh.A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Check if rubric exists for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break

    # Get rubric categories if rubric exists
    categories = []
    if rubric:
        for category in rubric_categories():
            if category.rubric_id == rubric.id:
                categories.append(category)

        # Sort categories by ID for consistent display
        categories.sort(key=lambda x: x.id)

    # Prepare form for creating/editing rubric
    if rubric:
        # Rubric exists - show edit form
        form_content = fh.Div(
            fh.H2(
                f"Manage Rubric for: {assignment.title}",
                cls="text-2xl font-bold text-indigo-900 mb-4",
            ),
            fh.P(
                "Edit the rubric categories and their weights. The weights should sum to 100%.",
                cls="text-gray-600 mb-6",
            ),
            # Existing categories display and edit form
            fh.Div(
                # Header section with assignment info
                fh.Div(
                    fh.P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    fh.P(
                        f"Status: {getattr(assignment, 'status', 'draft').capitalize()}",
                        cls="text-gray-600",
                    ),
                    cls="mb-4",
                ),
                # Current categories
                fh.H3(
                    "Current Rubric Categories",
                    cls="text-xl font-semibold text-indigo-800 mb-3",
                ),
                # Category display and edit section
                (
                    fh.Div(
                        fh.Div(
                            fh.Table(
                                fh.Thead(
                                    fh.Tr(
                                        fh.Th(
                                            "Category Name",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        fh.Th(
                                            "Description",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        fh.Th(
                                            "Weight (%)",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        fh.Th(
                                            "Actions",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                    ),
                                    cls="bg-indigo-50",
                                ),
                                fh.Tbody(
                                    *[
                                        fh.Tr(
                                            fh.Td(
                                                category.name,
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            fh.Td(
                                                fh.Div(
                                                    fh.P(
                                                        category.description,
                                                        cls="text-gray-700 max-w-md",
                                                    ),
                                                    cls="max-h-24 overflow-y-auto",
                                                ),
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            fh.Td(
                                                f"{category.weight}%",
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            fh.Td(
                                                fh.Div(
                                                    fh.Button(
                                                        "Edit",
                                                        hx_get=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/edit",
                                                        hx_target="#category-edit-form",
                                                        cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                                    ),
                                                    fh.Button(
                                                        "Delete",
                                                        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/delete",
                                                        hx_confirm=f"Are you sure you want to delete the category '{category.name}'?",
                                                        hx_target="#rubric-result",
                                                        cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                                                    ),
                                                    cls="flex",
                                                ),
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            # Add unique id to each row for potential HTMX interactions
                                            id=f"category-row-{category.id}",
                                            cls="hover:bg-gray-50",
                                        )
                                        for category in categories
                                    ]
                                ),
                                cls="w-full",
                            ),
                            cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100 mb-6",
                        )
                        if categories
                        else fh.P(
                            "No rubric categories have been created yet. Use the form below to add categories to your rubric.",
                            cls="bg-amber-50 p-4 rounded-lg border border-amber-200 text-amber-800 mb-6",
                        )
                    )
                ),
                # Add new category section
                fh.Div(
                    fh.H3(
                        "Add New Category",
                        cls="text-xl font-semibold text-indigo-800 mb-3",
                    ),
                    fh.Div(id="category-edit-form", cls="mb-4"),
                    fh.Form(
                        fh.Input(type="hidden", name="category_id", value=""),
                        fh.Div(
                            fh.Label(
                                "Category Name",
                                for_="name",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            fh.Input(
                                id="name",
                                name="name",
                                type="text",
                                placeholder="e.g. Content",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        fh.Div(
                            fh.Label(
                                "Description",
                                for_="description",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            fh.Textarea(
                                id="description",
                                name="description",
                                rows="3",
                                placeholder="Describe what this category evaluates...",
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        fh.Div(
                            fh.Label(
                                "Weight (%)",
                                for_="weight",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            fh.Input(
                                id="weight",
                                name="weight",
                                type="number",
                                min="1",
                                max="100",
                                step="0.1",
                                placeholder="e.g. 25",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        fh.Div(
                            fh.Button(
                                "Add Category",
                                type="submit",
                                cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                            ),
                            cls="mb-4",
                        ),
                        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/add",
                        hx_target="#rubric-result",
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6",
                    ),
                ),
                # Result placeholder for form submissions
                fh.Div(id="rubric-result", cls="mb-6"),
                # Action buttons
                fh.Div(
                    fh.A(
                        "Back to Assignment",
                        href=f"/instructor/assignments/{assignment_id}",
                        cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4",
                    ),
                    cls="flex",
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
            ),
            cls="",
        )
    else:
        # No rubric exists - show creation form
        form_content = fh.Div(
            fh.H2(
                f"Create Rubric for: {assignment.title}",
                cls="text-2xl font-bold text-indigo-900 mb-4",
            ),
            fh.P(
                "A rubric helps provide structured feedback for students. Create a rubric by defining categories and their weights.",
                cls="text-gray-600 mb-6",
            ),
            # Rubric creation form
            fh.Div(
                # Header section with assignment info
                fh.Div(
                    fh.P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    fh.P(
                        f"Status: {getattr(assignment, 'status', 'draft').capitalize()}",
                        cls="text-gray-600",
                    ),
                    cls="mb-6",
                ),
                # Initialize rubric form
                fh.Form(
                    fh.H3(
                        "Initialize Rubric",
                        cls="text-xl font-semibold text-indigo-800 mb-3",
                    ),
                    fh.P(
                        "Create a rubric for this assignment to define evaluation criteria.",
                        cls="text-gray-600 mb-4",
                    ),
                    fh.Div(
                        fh.Button(
                            "Create Rubric",
                            type="submit",
                            cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(id="create-rubric-result", cls="mt-4"),
                    hx_post=f"/instructor/assignments/{assignment_id}/rubric/create",
                    hx_target="#create-rubric-result",
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6",
                ),
                # Action buttons
                fh.Div(
                    fh.A(
                        "Back to Assignment",
                        href=f"/instructor/assignments/{assignment_id}",
                        cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4",
                    ),
                    cls="flex",
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
            ),
            cls="",
        )

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Rubric Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Back to Assignment",
                    color="gray",
                    href=f"/instructor/assignments/{assignment_id}",
                    icon="←",
                ),
                action_button(
                    "Assignment List",
                    color="indigo",
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    icon="📚",
                ),
                action_button(
                    "Edit Assignment",
                    color="amber",
                    href=f"/instructor/assignments/{assignment_id}/edit",
                    icon="✏️",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        fh.Div(
            fh.H3("Rubric Tips", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.P(
                "• Create 3-5 categories for a balanced rubric",
                cls="text-gray-600 mb-2 text-sm",
            ),
            fh.P("• Ensure weights add up to 100%", cls="text-gray-600 mb-2 text-sm"),
            fh.P(
                "• Use clear descriptions that guide students",
                cls="text-gray-600 mb-2 text-sm",
            ),
            fh.P(
                "• Consider including examples in descriptions",
                cls="text-gray-600 text-sm",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        fh.Div(
            fh.H3("Template Library", cls="text-xl font-semibold text-indigo-900 mb-4"),
            fh.Div(
                fh.Button(
                    "Essay Rubric Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/essay",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left",
                ),
                fh.Button(
                    "Research Paper Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/research",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left",
                ),
                fh.Button(
                    "Presentation Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/presentation",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 w-full text-left",
                ),
                cls="space-y-2",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        cls="space-y-6",
    )

    # Return complete page
    return dashboard_layout(
        f"Rubric for {assignment.title} | {course.title} | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/assignments/{assignment_id}/rubric/create")
@instructor_required
def instructor_rubric_create(session, assignment_id: int):
    """Create a new rubric for an assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    if error:
        return fh.Div(
            fh.P("Error: " + error, cls="text-red-600"), cls="p-4 bg-red-50 rounded-lg"
        )

    # Check if rubric already exists
    for r in rubrics():
        if r.assignment_id == assignment_id:
            return fh.Div(
                fh.P("A rubric already exists for this assignment.", cls="text-amber-600"),
                cls="p-4 bg-amber-50 rounded-lg",
            )

    # Create new rubric
    new_rubric = Rubric(
        id=None,  # Will be auto-assigned
        assignment_id=assignment_id,
        created_at=datetime.now(),
    )

    # Save to database
    try:
        rubrics.insert(new_rubric)
        # Redirect to refresh the page
        return fh.RedirectResponse(
            f"/instructor/assignments/{assignment_id}/rubric", status_code=303
        )
    except Exception as e:
        return fh.Div(
            fh.P(f"Error creating rubric: {e!s}", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )


@rt("/instructor/assignments/{assignment_id}/rubric/categories/add")
@instructor_required
def instructor_rubric_category_add(
    session, assignment_id: int, name: str, description: Optional[str] = None, weight: float = 0
):
    """Add a new category to a rubric"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    if error:
        return fh.Div(
            fh.P("Error: " + error, cls="text-red-600"), cls="p-4 bg-red-50 rounded-lg"
        )

    # Get the rubric
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break

    if not rubric:
        return fh.Div(
            fh.P("No rubric exists for this assignment.", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )

    # Validate weight
    try:
        weight = float(weight)
        if weight < 0 or weight > 100:
            raise ValueError("Weight must be between 0 and 100")
    except ValueError:
        return fh.Div(
            fh.P("Invalid weight value. Must be between 0 and 100.", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )

    # Create new category
    new_category = RubricCategory(
        id=None,  # Will be auto-assigned
        rubric_id=rubric.id,
        name=name.strip(),
        description=description.strip() if description else "",
        weight=weight,
    )

    # Save to database
    try:
        rubric_categories.insert(new_category)
        # Redirect to refresh the page
        return fh.RedirectResponse(
            f"/instructor/assignments/{assignment_id}/rubric", status_code=303
        )
    except Exception as e:
        return fh.Div(
            fh.P(f"Error adding category: {e!s}", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )
