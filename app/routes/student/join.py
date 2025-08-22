"""
Student join routes for course enrollment
"""

import logging
from datetime import datetime

from fasthtml import common as fh

from app import rt
from app.models.course import enrollments
from app.models.user import Role, users
from app.utils.auth import get_password_hash, is_strong_password
from app.utils.ui import page_container

logger = logging.getLogger(__name__)


@rt("/student/join")
def student_join_form(token: str):
    """Student join form from invitation token"""
    # Check if token is valid
    found_user = None
    for user in users():
        if user.verification_token == token and user.role == Role.STUDENT:
            found_user = user
            break

    if not found_user:
        # Invalid token
        error_content = fh.Div(
            fh.Div(
                fh.Div(
                    # Error icon
                    fh.Div(fh.Span("❌", cls="text-5xl block mb-4"), cls="text-center"),
                    # Brand logo
                    fh.Div(
                        fh.Span("Feed", cls="text-indigo-600 font-bold"),
                        fh.Span("Forward", cls="text-teal-500 font-bold"),
                        cls="text-3xl mb-4 text-center",
                    ),
                    fh.H1(
                        "Invalid Invitation Link",
                        cls="text-2xl font-bold text-indigo-900 mb-4 text-center",
                    ),
                    fh.P(
                        "The invitation link is invalid or has expired.",
                        cls="text-gray-600 mb-6 text-center",
                    ),
                    fh.Div(
                        fh.A(
                            "Return to Home",
                            href="/",
                            cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="text-center",
                    ),
                    cls="text-center",
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 max-w-md w-full",
            ),
            cls="flex justify-center items-center py-16 px-4",
        )

        return page_container("Invalid Invitation - FeedForward", error_content)

    # Valid token, show registration form
    registration_content = fh.Div(
        fh.Div(
            # Brand logo on registration form
            fh.Div(
                fh.Span("Feed", cls="text-indigo-600 font-bold"),
                fh.Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center",
            ),
            fh.H1(
                "Complete Your Registration",
                cls="text-2xl font-bold text-indigo-900 mb-6 text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Input(type="hidden", id="token", value=token),
                    fh.Input(type="hidden", id="email", value=found_user.email),
                    fh.Div(
                        fh.Label(
                            "Email",
                            for_="display_email",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        fh.Input(
                            id="display_email",
                            type="email",
                            value=found_user.email,
                            disabled=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg bg-gray-100",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Name",
                            for_="name",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        fh.Input(
                            id="name",
                            type="text",
                            placeholder="Your full name",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Password",
                            for_="password",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        fh.P(
                            "At least 8 characters with uppercase, lowercase, number, and special character",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        fh.Input(
                            id="password",
                            type="password",
                            placeholder="Create a password",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Confirm Password",
                            for_="confirm_password",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        fh.Input(
                            id="confirm_password",
                            type="password",
                            placeholder="Confirm your password",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6",
                    ),
                    fh.Div(
                        fh.Button(
                            "Complete Registration",
                            type="submit",
                            cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm",
                        ),
                        cls="mb-4",
                    ),
                    fh.Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/student/join",
                    hx_target="#error",
                    cls="w-full",
                ),
                cls="w-full max-w-md",
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50",
    )

    return page_container("Complete Registration - FeedForward", registration_content)


@rt("/student/join")
def student_join_process(
    session, token: str, email: str, name: str, password: str, confirm_password: str
):
    """Student join POST handler"""
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
                    if hasattr(enrollment, "status") and enrollment.status == "pending":
                        enrollment.status = "active"
                    if (
                        hasattr(enrollment, "date_enrolled")
                        and not enrollment.date_enrolled
                    ):
                        enrollment.date_enrolled = now
                    if hasattr(enrollment, "last_access"):
                        enrollment.last_access = now
                    enrollments.update(enrollment)
        except Exception as e:
            print(f"Note: Could not update enrollment status: {e!s}")

        # Log the user in
        session["auth"] = user.email

        # Redirect to the student dashboard
        return fh.HttpHeader("HX-Redirect", "/student/dashboard")
    except Exception as e:
        print(f"Error in student join: {e!s}")
        return "Invalid registration request"
