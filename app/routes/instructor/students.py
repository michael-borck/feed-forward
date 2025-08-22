"""
Instructor student management routes
"""

import random
import string
import urllib.parse
from datetime import datetime

from fasthtml.common import *
from starlette.responses import RedirectResponse

from app import instructor_required, rt
from app.models.course import Enrollment, courses, enrollments
from app.models.user import Role, User, users
from app.utils.email import generate_verification_token, send_student_invitation_email
from app.utils.ui import action_button, card, dashboard_layout, status_badge


def generate_invitation_token(length=40):
    """Generate a random token for student invitations"""
    chars = string.ascii_letters + string.digits + "-_"
    return "".join(random.choice(chars) for _ in range(length))


@rt("/instructor/manage-students")
@instructor_required
def instructor_manage_students(session, request):
    """Overview page for managing students across all courses"""
    # Get current user
    user = users[session["auth"]]

    # Get all courses for this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, "status") and course.status == "deleted":
                continue
            instructor_courses.append(course)

    # Sort courses by creation date
    instructor_courses.sort(
        key=lambda x: x.created_at if hasattr(x, "created_at") else "", reverse=True
    )

    # Get all students across all courses
    all_students = {}  # Use dict to avoid duplicates
    for course in instructor_courses:
        for enrollment in enrollments():
            if enrollment.course_id == course.id:
                try:
                    student = users[enrollment.student_email]
                    # Count courses for each student
                    if student.email not in all_students:
                        all_students[student.email] = {
                            "student": student,
                            "courses": [],
                            "verified": student.verified,
                        }
                    all_students[student.email]["courses"].append(course)
                except:
                    # Handle missing student records
                    if enrollment.student_email not in all_students:
                        all_students[enrollment.student_email] = {
                            "student": None,
                            "email": enrollment.student_email,
                            "courses": [],
                            "verified": False,
                        }
                    all_students[enrollment.student_email]["courses"].append(course)

    # Convert to list and sort
    students_list = list(all_students.values())
    students_list.sort(
        key=lambda s: (
            0 if s["verified"] else 1,
            s["student"].email if s["student"] else s.get("email", ""),
        )
    )

    # Create the main content
    if students_list:
        student_rows = []
        for idx, student_info in enumerate(students_list):
            student = student_info["student"]
            email = student.email if student else student_info.get("email", "Unknown")
            name = student.name if student and student.name else "(Not registered)"
            status = "Enrolled" if student_info["verified"] else "Invited"
            status_color = "green" if student_info["verified"] else "yellow"
            course_count = len(student_info["courses"])
            course_names = ", ".join([c.code for c in student_info["courses"][:3]])
            if course_count > 3:
                course_names += f" (+{course_count - 3} more)"

            row = Tr(
                Td(email, cls="py-4 px-6"),
                Td(name, cls="py-4 px-6"),
                Td(status_badge(status, status_color), cls="py-4 px-6"),
                Td(str(course_count), cls="py-4 px-6 text-center"),
                Td(course_names, cls="py-4 px-6 text-sm text-gray-600"),
                Td(
                    Div(
                        Button(
                            "Resend",
                            hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(email)}&course_id={student_info['courses'][0].id}",
                            hx_target="#message-area",
                            cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                        )
                        if not student_info["verified"]
                        else "",
                        Button(
                            "Remove",
                            hx_post=f"/instructor/remove-student?email={urllib.parse.quote(email)}&course_id={student_info['courses'][0].id}",
                            hx_target="#message-area",
                            hx_confirm=f"Are you sure you want to remove {email} from all courses?",
                            cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                        ),
                        cls="flex",
                    ),
                    cls="py-4 px-6",
                ),
                cls="border-b border-gray-100 hover:bg-gray-50 transition-colors",
            )
            student_rows.append(row)

        main_content = Div(
            H2("All Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(id="message-area", cls="mb-4"),
            Div(
                Table(
                    Thead(
                        Tr(
                            *[
                                Th(
                                    h,
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                )
                                for h in [
                                    "Email",
                                    "Name",
                                    "Status",
                                    "Courses",
                                    "Enrolled In",
                                    "Actions",
                                ]
                            ],
                            cls="bg-indigo-50",
                        )
                    ),
                    Tbody(*student_rows),
                    cls="w-full",
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
            ),
            cls="",
        )
    else:
        main_content = Div(
            H2("All Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P(
                        "You don't have any students enrolled yet.",
                        cls="text-center text-gray-600 mb-6",
                    ),
                    Div(
                        A(
                            "Invite Students",
                            href="/instructor/invite-students",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="text-center",
                    ),
                    cls="py-8",
                )
            ),
        )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Student Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="←"
                ),
                action_button(
                    "Invite Students",
                    color="indigo",
                    href="/instructor/invite-students",
                    icon="✉️",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Statistics", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Total Students: {len(students_list)}", cls="text-gray-600 mb-2"),
            P(
                f"Enrolled: {sum(1 for s in students_list if s['verified'])}",
                cls="text-green-600 mb-2",
            ),
            P(
                f"Invited: {sum(1 for s in students_list if not s['verified'])}",
                cls="text-yellow-600 mb-2",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    return dashboard_layout(
        "Manage Students | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path="/instructor/manage-students",
    )


@rt("/instructor/courses/{course_id}/students")
@instructor_required
def instructor_course_students(session, course_id: int):
    """View and manage students for a specific course"""
    # Get current user
    user = users[session["auth"]]

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

                course_students.append(
                    {
                        "email": student.email,
                        "name": student.name if student.name else "(Not registered)",
                        "status": status,
                        "verified": student.verified,
                    }
                )
            except:
                # Student record might be missing
                course_students.append(
                    {
                        "email": enrollment.student_email,
                        "name": "(Not registered)",
                        "status": "Invited",
                        "verified": False,
                    }
                )

    # Sort students: enrolled first, then invited
    sorted_students = sorted(
        course_students, key=lambda s: (0 if s["verified"] else 1, s["email"])
    )

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
                        Button(
                            "Resend",
                            hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                            hx_target=f"#status-{idx}",
                            cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                        )
                        if not student["verified"]
                        else "",
                        Button(
                            "Remove",
                            hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                            hx_target="#message-area",
                            hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                            cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                        ),
                        cls="flex",
                        id=f"status-{idx}",
                    ),
                    cls="py-4 px-6",
                ),
                id=f"row-{idx}",
                cls="border-b border-gray-100 hover:bg-gray-50 transition-colors",
            )
            student_rows.append(row)

        # Create the student table
        main_content = Div(
            H2(
                f"Students in {target_course.title} ({target_course.code})",
                cls="text-2xl font-bold text-indigo-900 mb-6",
            ),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            Div(
                Table(
                    Thead(
                        Tr(
                            *[
                                Th(
                                    h,
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                )
                                for h in ["#", "Email", "Name", "Status", "Actions"]
                            ],
                            cls="bg-indigo-50",
                        )
                    ),
                    Tbody(*student_rows),
                    cls="w-full",
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
            ),
            Div(
                action_button(
                    "Invite More Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="+",
                ),
                cls="mt-6",
            ),
            cls="",
        )
    else:
        # Show a message if no students enrolled in this course
        main_content = Div(
            H2(
                f"Students in {target_course.title} ({target_course.code})",
                cls="text-2xl font-bold text-indigo-900 mb-6",
            ),
            card(
                Div(
                    P(
                        "You don't have any students enrolled in this course yet.",
                        cls="text-center text-gray-600 mb-6",
                    ),
                    Div(
                        A(
                            "Invite Students",
                            href=f"/instructor/invite-students?course_id={course_id}",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="text-center",
                    ),
                    cls="py-8",
                )
            ),
            cls="",
        )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Invite Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="✉️",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Course Details", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Title: {target_course.title}", cls="text-gray-600 mb-2"),
            P(f"Code: {target_course.code}", cls="text-gray-600 mb-2"),
            P(f"Students: {len(sorted_students)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Students in {target_course.code} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/resend-invitation")
@instructor_required
def instructor_resend_invitation(session, request, email: str, course_id: int):
    """Resend invitation to a student"""
    # Get current user
    user = users[session["auth"]]

    # Verify the course belongs to this instructor
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return Div(
            P("Course not found", cls="text-red-600"), cls="p-3 bg-red-50 rounded-lg"
        )

    # Verify the enrollment exists
    enrollment_exists = False
    for e in enrollments():
        if e.course_id == course_id and e.student_email == email:
            enrollment_exists = True
            break

    if not enrollment_exists:
        return Div(
            P("Student not found in this course", cls="text-red-600"),
            cls="p-3 bg-red-50 rounded-lg",
        )

    # Send the invitation email
    try:
        # Check if student exists
        try:
            student = users[email]
            token = student.verification_token
        except:
            # Create student account if doesn't exist
            token = generate_verification_token()
            new_student = User(
                email=email,
                password_hash="",  # Will be set when they register
                role=Role.STUDENT,
                name=None,
                verified=False,
                verification_token=token,
                created_at=datetime.now(),
            )
            users.insert(new_student)

        # Send invitation email
        send_student_invitation_email(
            student_email=email,
            instructor_name=user.name or user.email,
            course_name=course.title,
            course_code=course.code,
            verification_token=token,
        )

        return Div(
            P(f"Invitation resent to {email}", cls="text-green-600"),
            cls="p-3 bg-green-50 rounded-lg",
        )
    except Exception as e:
        return Div(
            P(f"Failed to send invitation: {e!s}", cls="text-red-600"),
            cls="p-3 bg-red-50 rounded-lg",
        )


@rt("/instructor/remove-student")
@instructor_required
def instructor_remove_student(session, request, email: str, course_id: int):
    """Remove a student from a course"""
    # Get current user
    user = users[session["auth"]]

    # Verify the course belongs to this instructor
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return Div(
            P("Course not found", cls="text-red-600"), cls="p-3 bg-red-50 rounded-lg"
        )

    # Find and remove the enrollment
    enrollment_found = False
    for e in enrollments():
        if e.course_id == course_id and e.student_email == email:
            try:
                enrollments.delete(e.id)
                enrollment_found = True
                break
            except Exception as ex:
                return Div(
                    P(f"Failed to remove student: {ex!s}", cls="text-red-600"),
                    cls="p-3 bg-red-50 rounded-lg",
                )

    if enrollment_found:
        return Div(
            P(f"Student {email} removed from {course.code}", cls="text-green-600"),
            cls="p-3 bg-green-50 rounded-lg",
        )
    else:
        return Div(
            P("Student not found in this course", cls="text-red-600"),
            cls="p-3 bg-red-50 rounded-lg",
        )


@rt("/instructor/invite-students")
@instructor_required
def instructor_invite_students_form(session, request):
    """Show the invite students form"""
    # Get current user
    user = users[session["auth"]]

    # Get course_id from query parameters if provided
    course_id = request.url.params.get("course_id")

    # Get all courses for this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, "status") and course.status == "deleted":
                continue
            instructor_courses.append(course)

    # Sort courses by creation date
    instructor_courses.sort(
        key=lambda x: x.created_at if hasattr(x, "created_at") else "", reverse=True
    )

    # If no courses, redirect to course creation
    if not instructor_courses:
        return RedirectResponse("/instructor/courses/new", status_code=303)

    # Main content
    main_content = Div(
        H2("Invite Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Form(
            # Course selection
            Div(
                Label(
                    "Select Course",
                    for_="course_id",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                Select(
                    *[
                        Option(
                            f"{course.title} ({course.code})",
                            value=str(course.id),
                            selected=(str(course.id) == course_id)
                            if course_id
                            else (i == 0),
                        )
                        for i, course in enumerate(instructor_courses)
                    ],
                    id="course_id",
                    name="course_id",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-4",
            ),
            # Email input
            Div(
                Label(
                    "Student Emails",
                    for_="emails",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                Textarea(
                    id="emails",
                    name="emails",
                    rows=6,
                    placeholder="Enter one email per line\nexample1@email.com\nexample2@email.com",
                    required=True,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                P(
                    "Enter one email address per line. Students will receive an invitation to join your course.",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-6",
            ),
            # Submit buttons
            Div(
                Button(
                    "Send Invitations",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                A(
                    "Cancel",
                    href="/instructor/manage-students",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action="/instructor/invite-students",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Invitation Tips", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P("• Students will receive an email invitation", cls="text-gray-600 mb-2"),
            P("• They must verify their email to enroll", cls="text-gray-600 mb-2"),
            P("• You can resend invitations if needed", cls="text-gray-600 mb-2"),
            P("• Students can submit drafts once enrolled", cls="text-gray-600"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    return dashboard_layout(
        "Invite Students | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path="/instructor/invite-students",
    )


@rt("/instructor/invite-students")
@instructor_required
def instructor_invite_students_process(session, course_id: int, emails: str):
    """Process student invitations"""
    # Get current user
    user = users[session["auth"]]

    # Verify course ownership
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Parse emails
    email_list = [
        email.strip() for email in emails.strip().split("\n") if email.strip()
    ]

    # Remove duplicates
    email_list = list(set(email_list))

    # Track results
    invited = []
    already_enrolled = []
    failed = []

    for email in email_list:
        # Basic email validation
        if "@" not in email or "." not in email:
            failed.append((email, "Invalid email format"))
            continue

        # Check if already enrolled
        enrollment_exists = False
        for e in enrollments():
            if e.course_id == course_id and e.student_email == email:
                enrollment_exists = True
                already_enrolled.append(email)
                break

        if enrollment_exists:
            continue

        try:
            # Check if student exists
            student = None
            try:
                student = users[email]
                token = student.verification_token
            except:
                # Create student account if doesn't exist
                token = generate_verification_token()
                new_student = User(
                    email=email,
                    password_hash="",  # Will be set when they register
                    role=Role.STUDENT,
                    name=None,
                    verified=False,
                    verification_token=token,
                    created_at=datetime.now(),
                )
                users.insert(new_student)

            # Create enrollment
            new_enrollment = Enrollment(
                id=None,
                course_id=course_id,
                student_email=email,
                invitation_token=generate_invitation_token(),
                invited_at=datetime.now(),
                enrolled_at=None,
            )
            enrollments.insert(new_enrollment)

            # Send invitation email
            send_student_invitation_email(
                student_email=email,
                instructor_name=user.name or user.email,
                course_name=course.title,
                course_code=course.code,
                verification_token=token,
            )

            invited.append(email)
        except Exception as e:
            failed.append((email, str(e)))

    # Redirect to course students page with results
    return RedirectResponse(
        f"/instructor/courses/{course_id}/students", status_code=303
    )
