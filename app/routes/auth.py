"""
Authentication routes (login, register, verify, password reset, etc.)
"""

import logging
import os
import secrets
from datetime import datetime

logger = logging.getLogger(__name__)

# Production hides dev conveniences (manual verification/reset links shown
# when SMTP is unavailable) — see docker-compose.prod.yml.
_IS_PROD = os.environ.get("FEEDFORWARD_ENV", "dev") == "production"

from fasthtml import common as fh
from fasthtml.common import (
    HttpHeader,
)
from fastlite import NotFoundError

# Get the route table and FastHTML components from the app
from app import rt
from app.models.user import Role, User, users
from app.utils.auth import (
    generate_token_expiry,
    get_password_hash,
    is_institutional_email,
    is_reset_token_valid,
    is_strong_password,
    verify_password,
)
from app.utils.email import (
    APP_DOMAIN,
    generate_verification_token,
    send_password_reset_email,
    send_verification_email,
)

# Import UI components
from app.utils.ui import page_container


# --- Registration Routes ---
@rt("/register")
def get():
    # Create the registration form content
    registration_content = fh.Div(
        fh.Div(
            # Brand logo on registration form
            fh.Div(
                fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                cls="text-3xl mb-4 text-center",
            ),
            fh.H1(
                "Create Your Account",
                cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-6 text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Div(
                        fh.Label(
                            "Name",
                            for_="name",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.Input(
                            id="name",
                            type="text",
                            placeholder="Your full name",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Email",
                            for_="email",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.P(
                            "For instructors only. Some email domains are auto-approved, others require administrator approval.",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        fh.Input(
                            id="email",
                            type="email",
                            placeholder="Your institutional email address",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Password",
                            for_="password",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
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
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Confirm Password",
                            for_="confirm_password",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.Input(
                            id="confirm_password",
                            type="password",
                            placeholder="Confirm your password",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-6",
                    ),
                    fh.Div(
                        fh.Button(
                            "Sign up",
                            type="submit",
                            cls="w-full inline-flex items-center justify-center bg-[#1a2e44] text-[#faf8f2] py-3 rounded hover:bg-[#0f1e30] focus:outline-none focus:ring-2 focus:ring-teal-600 transition-colors font-medium uppercase tracking-[0.15em] text-sm",
                        ),
                        cls="mb-4",
                    ),
                    fh.Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/register",
                    hx_target="#error",
                    cls="w-full",
                ),
                fh.Hr(cls="my-6 border-gray-200"),
                fh.P(
                    "Already have an account? ",
                    fh.A(
                        "Sign in here",
                        href="/login",
                        cls="text-teal-600 hover:underline font-medium",
                    ),
                    cls="text-center text-gray-600",
                ),
                cls="w-full max-w-md",
            ),
            cls="bg-[#fdfcf8] p-8 rounded border border-slate-300",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Sign up - FeedForward", registration_content)


@rt("/register")
def post(name: str, email: str, password: str, confirm_password: str):
    # Validate inputs
    if not name or not email or not password or not confirm_password:
        return "All fields are required"

    if password != confirm_password:
        return "Passwords do not match"

    if not is_strong_password(password):
        return "Password must be at least 8 characters with uppercase, lowercase, number, and special character"

    # Check if email is institutional and get auto-approval status
    is_valid, role, auto_approve = is_institutional_email(email)
    if not is_valid:
        return "Invalid email. Please contact the administrator if you require instructor access."

    # Only instructors can register directly for now (students invited by instructors)
    if role != Role.INSTRUCTOR:
        return "Only instructors can register directly. Students are invited by instructors."

    try:
        # Check if user already exists
        existing_user = users[email]

        # If user exists but is soft-deleted, we can reactivate
        if hasattr(existing_user, "status") and existing_user.status == "deleted":
            # Generate verification token
            token = generate_verification_token(email)

            # Update user data
            existing_user.name = name
            existing_user.password = get_password_hash(password)
            existing_user.verified = False
            existing_user.verification_token = token
            existing_user.approved = auto_approve if role == Role.INSTRUCTOR else True
            existing_user.department = ""
            existing_user.reset_token = ""
            existing_user.reset_token_expiry = ""
            existing_user.status = "active"
            existing_user.last_active = datetime.now().isoformat()

            # Update in database
            users.update(existing_user)

            # Send verification email
            success, message = send_verification_email(email, token)

            # Redirect to confirmation page
            if success:
                message = (
                    "Your account has been reactivated! Please check your email to verify your account."
                    + (
                        ""
                        if auto_approve
                        else " After verification, your account will require administrator approval."
                    )
                )
                return HttpHeader(
                    "HX-Redirect",
                    f"/register/confirmation?message={message}&email={email}",
                )
            else:
                # For security, don't expose the exact error to the user
                print(f"EMAIL ERROR DETAILS: {message}")
                # Provide a way to verify manually for development purposes
                verify_link = f"{APP_DOMAIN}/verify?token={token}"
                return fh.Div(
                    fh.P(
                        "Account reactivated but there was an issue sending the verification email.",
                        cls="text-red-500 mb-2",
                    ),
                    fh.P(
                        "For development purposes, you can verify your account using this link:",
                        cls="mb-2",
                    ),
                    fh.A(
                        verify_link,
                        href=verify_link,
                        cls="text-blue-500 underline break-all",
                        target="_blank",
                    ),
                    fh.P(
                        "Note: "
                        + (
                            ""
                            if auto_approve
                            else "After verification, your account will require administrator approval."
                        ),
                        cls="mt-2 text-gray-600",
                    ),
                    cls="text-center",
                )
        else:
            return (
                "Check your email to continue. If you already have an "
                "account, use Sign in instead."
            )
    except NotFoundError:
        # Generate verification token
        token = generate_verification_token(email)

        # Create new user
        new_user = User(
            email=email,
            name=name,
            password=get_password_hash(password),
            role=role,
            verified=False,
            verification_token=token,
            approved=auto_approve
            if role == Role.INSTRUCTOR
            else True,  # Auto-approve based on domain
            department="",
            reset_token="",
            reset_token_expiry="",
            status="active",
            last_active=datetime.now().isoformat(),
        )

        # Insert into database
        users.insert(new_user)

        # Send verification email
        success, message = send_verification_email(email, token)

        # Redirect to a confirmation page instead of showing a message in-place
        if success:
            message = (
                "Registration successful! Please check your email to verify your account."
                + (
                    ""
                    if auto_approve
                    else " After verification, your account will require administrator approval."
                )
            )
            return HttpHeader(
                "HX-Redirect", f"/register/confirmation?message={message}&email={email}"
            )
        else:
            # For security, don't expose the exact error to the user
            logger.error("Email send failed: %s", message)
            if _IS_PROD:
                return fh.Div(
                    fh.P(
                        "We could not send the email just now. Please try "
                        "again later or contact support.",
                        cls="text-red-700",
                    ),
                    cls="text-center",
                )
            # Provide a way to verify manually for development purposes
            verify_link = f"{APP_DOMAIN}/verify?token={token}"
            return fh.Div(
                fh.P(
                    "Registration successful but there was an issue sending the verification email.",
                    cls="text-red-500 mb-2",
                ),
                fh.P(
                    "For development purposes, you can verify your account using this link:",
                    cls="mb-2",
                ),
                fh.A(
                    verify_link,
                    href=verify_link,
                    cls="text-blue-500 underline break-all",
                    target="_blank",
                ),
                fh.P(
                    "Note: "
                    + (
                        ""
                        if auto_approve
                        else "After verification, your account will require administrator approval."
                    ),
                    cls="mt-2 text-gray-600",
                ),
                cls="text-center",
            )


# --- Registration Confirmation Route ---
@rt("/register/confirmation")
def get(message: str, email: str):
    confirmation_content = fh.Div(
        fh.Div(
            fh.Div(
                # Success icon
                fh.Div(fh.Span("✅", cls="text-5xl block mb-4"), cls="text-center"),
                # Brand logo
                fh.Div(
                    fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                    fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                    cls="text-3xl mb-4 text-center",
                ),
                fh.H2(
                    "Registration Complete!",
                    cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-4 text-center",
                ),
                fh.Div(
                    fh.P(message, cls="text-gray-600 mb-3"),
                    fh.P("We've sent a verification email to: ", cls="text-gray-600"),
                    fh.P(email, cls="font-semibold text-teal-600 mb-6"),
                    cls="text-center",
                ),
                fh.Div(
                    fh.P(
                        "Please check your inbox and click the verification link.",
                        cls="text-gray-600 mb-6",
                    ),
                    cls="text-center",
                ),
                fh.Div(
                    fh.A(
                        "Return to Login",
                        href="/login",
                        cls="inline-block bg-[#1a2e44] text-[#faf8f2] px-6 py-3 rounded font-medium uppercase tracking-[0.15em] text-sm hover:bg-[#0f1e30] transition-colors mr-4",
                    ),
                    fh.A(
                        "Return to Home",
                        href="/",
                        cls="inline-block bg-gray-100 text-gray-800 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                    ),
                    cls="flex justify-center flex-wrap gap-4",
                ),
                cls="text-center",
            ),
            cls="bg-[#fdfcf8] p-8 rounded border border-slate-300 max-w-md w-full",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Registration Complete - FeedForward", confirmation_content)


# --- Email Verification Route ---
@rt("/verify")
def get(token: str):
    # Import UI components

    # Debug print
    # Look for a user with the matching token (constant-time comparison)
    for user in users():
        if user.verification_token and secrets.compare_digest(
            user.verification_token, token
        ):
            user.verified = True
            # Clear the token after successful verification
            user.verification_token = ""
            users.update(user)

            # Success message content
            verify_success_content = fh.Div(
                fh.Div(
                    fh.Div(
                        # Success icon
                        fh.Div(
                            fh.Span("✅", cls="text-5xl block mb-4"), cls="text-center"
                        ),
                        # Brand logo
                        fh.Div(
                            fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                            fh.Span(
                                "Forward", cls="font-serif font-bold text-teal-600"
                            ),
                            cls="text-3xl mb-4 text-center",
                        ),
                        fh.H1(
                            "Email Verified Successfully!",
                            cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-4 text-center",
                        ),
                        fh.P(
                            "Your email has been verified."
                            + (
                                " You can now log in to your account."
                                if user.approved
                                else " Your account requires administrator approval before you can log in."
                            ),
                            cls="text-gray-600 mb-6 text-center",
                        ),
                        fh.Div(
                            fh.A(
                                "Login to Your Account",
                                href="/login",
                                cls="inline-block bg-[#1a2e44] text-[#faf8f2] px-6 py-3 rounded font-medium uppercase tracking-[0.15em] text-sm hover:bg-[#0f1e30] transition-colors",
                            ),
                            cls="text-center",
                        ),
                        cls="text-center",
                    ),
                    cls="bg-[#fdfcf8] p-8 rounded border border-slate-300 max-w-md w-full",
                ),
                cls="flex justify-center items-center py-16 px-4",
            )

            # Return the complete page
            return page_container(
                "Email Verified - FeedForward", verify_success_content
            )

    # Error message content for invalid token
    verify_error_content = fh.Div(
        fh.Div(
            fh.Div(
                # Error icon
                fh.Div(fh.Span("❌", cls="text-5xl block mb-4"), cls="text-center"),
                # Brand logo
                fh.Div(
                    fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                    fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                    cls="text-3xl mb-4 text-center",
                ),
                fh.H1(
                    "Verification Failed",
                    cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-4 text-center",
                ),
                fh.P(
                    "The verification link is invalid or has expired.",
                    cls="text-gray-600 mb-6 text-center",
                ),
                fh.Div(
                    fh.A(
                        "Return to Home",
                        href="/",
                        cls="inline-block bg-[#1a2e44] text-[#faf8f2] px-6 py-3 rounded font-medium uppercase tracking-[0.15em] text-sm hover:bg-[#0f1e30] transition-colors",
                    ),
                    cls="text-center",
                ),
                cls="text-center",
            ),
            cls="bg-[#fdfcf8] p-8 rounded border border-slate-300 max-w-md w-full",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Verification Failed - FeedForward", verify_error_content)


# --- Login Routes ---
@rt("/login")
def get():
    from app.utils.design import COLOR, RADIUS, TEXT, button_classes

    input_cls = (
        f"w-full p-3 bg-white border border-{COLOR['border']} {RADIUS} "
        f"text-{COLOR['text_strong']} focus:outline-none focus:ring-2 "
        f"focus:ring-{COLOR['accent']} focus:border-{COLOR['accent']}"
    )
    label_cls = f"block {TEXT['label']} text-{COLOR['text_muted']} mb-2"

    # Create the login form content
    login_content = fh.Div(
        fh.Div(
            # Brand wordmark on login form
            fh.Div(
                fh.Span(
                    "Feed",
                    cls=f"font-serif font-bold text-{COLOR['wordmark_first']}",
                ),
                fh.Span(
                    "Forward",
                    cls=f"font-serif font-bold text-{COLOR['wordmark_second']}",
                ),
                cls="text-3xl mb-4 text-center",
            ),
            fh.H1(
                "Sign in to your account",
                cls=f"{TEXT['h2']} text-{COLOR['text_strong']} mb-6 text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Div(
                        fh.Label("Email", for_="email", cls=label_cls),
                        fh.Input(
                            id="email",
                            type="email",
                            placeholder="Your email address",
                            required=True,
                            cls=input_cls,
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label("Password", for_="password", cls=label_cls),
                        fh.Input(
                            id="password",
                            type="password",
                            placeholder="Your password",
                            required=True,
                            cls=input_cls,
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.A(
                            "Forgot password?",
                            href="/forgot-password",
                            cls=f"text-{COLOR['accent']} hover:underline text-sm "
                            "font-medium",
                        ),
                        cls="mb-6 text-right",
                    ),
                    fh.Div(
                        fh.Button(
                            "Sign in",
                            type="submit",
                            cls=f"w-full {button_classes('primary', 'lg')}",
                        ),
                        cls="mb-4",
                    ),
                    fh.Span(
                        id="error", cls=f"text-{COLOR['danger']} block text-center"
                    ),
                    hx_post="/login",
                    hx_target="#error",
                    cls="w-full",
                ),
                fh.Hr(cls=f"my-6 border-{COLOR['border']}"),
                fh.P(
                    "Don't have an account? ",
                    fh.A(
                        "Sign up here",
                        href="/register",
                        cls=f"text-{COLOR['accent']} hover:underline font-medium",
                    ),
                    cls=f"text-center text-{COLOR['text_body']}",
                ),
                cls="w-full max-w-md",
            ),
            cls=f"bg-{COLOR['surface']} p-8 {RADIUS} border border-{COLOR['border']}",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Sign in - FeedForward", login_content)


@rt("/login")
def post(session, email: str, password: str):
    """Authenticate against the user store and route to the role's dashboard.

    Previous implementations carried hardcoded "EMERGENCY FIX" credential
    bypasses (admin@example.com, instructor@example.com, Michael's account)
    plus a per-test-account password fallback, and printed the user's role
    and hash prefix to stdout on every attempt. All removed — bcrypt-only
    verification, no credential-shaped strings in logs or error responses.
    """
    try:
        user = users[email]
    except NotFoundError:
        return "Email or password are incorrect"

    if not verify_password(password, user.password):
        return "Email or password are incorrect"

    if not user.verified:
        # Re-issue a verification token so the user can recover from a stale one.
        token = generate_verification_token(email)
        user.verification_token = token
        users.update(user)
        send_verification_email(email, token)
        return fh.Div(
            fh.P(
                "Your email is not verified yet. Please check your inbox or spam folder.",
                cls="text-red-500 mb-2",
            ),
            fh.P(
                "We've sent a new verification email to your address.",
                cls="text-gray-600",
            ),
            cls="text-center",
        )

    if user.role == Role.INSTRUCTOR and not user.approved:
        return "Your account is pending approval. Please contact the administrator."

    session.clear()  # rotate session state on login (fixation defence)
    session["auth"] = user.email
    if user.role == Role.INSTRUCTOR:
        return HttpHeader("HX-Redirect", "/instructor/dashboard")
    if user.role == Role.STUDENT:
        return HttpHeader("HX-Redirect", "/student/dashboard")
    if user.role == Role.ADMIN:
        return HttpHeader("HX-Redirect", "/admin/dashboard")
    return HttpHeader("HX-Redirect", "/dashboard")


# --- Logout Route ---
@rt("/logout")
def post(session):
    if "auth" in session:
        del session["auth"]
    return HttpHeader("HX-Redirect", "/login")


# --- Forgot Password Routes ---
@rt("/forgot-password")
def get():
    # Create the forgot password content
    forgot_password_content = fh.Div(
        fh.Div(
            # Brand logo
            fh.Div(
                fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                cls="text-3xl mb-4 text-center",
            ),
            fh.H1(
                "Reset Your Password",
                cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-4 text-center",
            ),
            fh.P(
                "Enter your email address and we'll send you a link to reset your password.",
                cls="text-gray-600 mb-6 text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Div(
                        fh.Label(
                            "Email",
                            for_="email",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.Input(
                            id="email",
                            type="email",
                            placeholder="Your email address",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-6",
                    ),
                    fh.Div(
                        fh.Button(
                            "Send Reset Link",
                            type="submit",
                            cls="w-full inline-flex items-center justify-center bg-[#1a2e44] text-[#faf8f2] py-3 rounded hover:bg-[#0f1e30] focus:outline-none focus:ring-2 focus:ring-teal-600 transition-colors font-medium uppercase tracking-[0.15em] text-sm",
                        ),
                        cls="mb-4",
                    ),
                    fh.Span(id="message", cls="text-center block"),
                    hx_post="/forgot-password",
                    hx_target="#message",
                    cls="w-full",
                ),
                fh.Hr(cls="my-6 border-gray-200"),
                fh.P(
                    "Remember your password? ",
                    fh.A(
                        "Login here",
                        href="/login",
                        cls="text-teal-600 hover:underline font-medium",
                    ),
                    cls="text-center text-gray-600",
                ),
                cls="w-full max-w-md",
            ),
            cls="bg-[#fdfcf8] p-8 rounded border border-slate-300",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Reset Password - FeedForward", forgot_password_content)


@rt("/forgot-password")
def post(email: str):
    try:
        user = users[email]

        # Generate a password reset token
        reset_token = generate_verification_token(email)

        # Set the token and expiry time (24 hours)
        user.reset_token = reset_token
        user.reset_token_expiry = generate_token_expiry(24)
        users.update(user)

        # Send password reset email
        success, message = send_password_reset_email(email, reset_token)
        if success:
            return fh.Div(
                fh.P(
                    "If your email is registered, you will receive a password reset link.",
                    cls="text-green-500",
                ),
                cls="text-center",
            )
        else:
            # For security, don't expose the exact error to the user
            logger.error("Email send failed: %s", message)
            if _IS_PROD:
                return fh.Div(
                    fh.P(
                        "We could not send the email just now. Please try "
                        "again later or contact support.",
                        cls="text-red-700",
                    ),
                    cls="text-center",
                )
            # Provide a way to reset password manually for development purposes
            reset_link = f"{APP_DOMAIN}/reset-password?token={reset_token}"
            return fh.Div(
                fh.P("Failed to send reset link.", cls="text-red-500 mb-2"),
                fh.P(
                    "For development purposes, you can reset your password using this link:",
                    cls="mb-2",
                ),
                fh.A(
                    reset_link,
                    href=reset_link,
                    cls="text-blue-500 underline break-all",
                    target="_blank",
                ),
                cls="text-center",
            )
    except NotFoundError:
        # Don't reveal if the email exists
        return fh.Div(
            fh.P(
                "If your email is registered, you will receive a password reset link.",
                cls="text-green-500",
            ),
            cls="text-center",
        )


# --- Reset Password Routes ---
@rt("/reset-password")
def get(token: str):
    # Import UI components

    # Validate token
    valid_token = False
    user_email = ""

    for user in users():
        if (
            user.reset_token
            and secrets.compare_digest(user.reset_token, token)
            and is_reset_token_valid(user.reset_token_expiry)
        ):
            valid_token = True
            user_email = user.email
            break

    if not valid_token:
        # Error message content for invalid token
        invalid_token_content = fh.Div(
            fh.Div(
                fh.Div(
                    # Error icon
                    fh.Div(fh.Span("❌", cls="text-5xl block mb-4"), cls="text-center"),
                    # Brand logo
                    fh.Div(
                        fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                        fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                        cls="text-3xl mb-4 text-center",
                    ),
                    fh.H1(
                        "Invalid or Expired Link",
                        cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-4 text-center",
                    ),
                    fh.P(
                        "The password reset link is invalid or has expired.",
                        cls="text-gray-600 mb-6 text-center",
                    ),
                    fh.Div(
                        fh.A(
                            "Request New Link",
                            href="/forgot-password",
                            cls="inline-block bg-[#1a2e44] text-[#faf8f2] px-6 py-3 rounded font-medium uppercase tracking-[0.15em] text-sm hover:bg-[#0f1e30] transition-colors",
                        ),
                        cls="text-center",
                    ),
                    cls="text-center",
                ),
                cls="bg-[#fdfcf8] p-8 rounded border border-slate-300 max-w-md w-full",
            ),
            cls="flex justify-center items-center py-16 px-4",
        )

        # Return the complete page
        return page_container("Invalid Reset Link - FeedForward", invalid_token_content)

    # Valid token, show password reset form
    reset_password_content = fh.Div(
        fh.Div(
            # Brand logo
            fh.Div(
                fh.Span("Feed", cls="font-serif font-bold text-[#1a2e44]"),
                fh.Span("Forward", cls="font-serif font-bold text-teal-600"),
                cls="text-3xl mb-4 text-center",
            ),
            fh.H1(
                "Set New Password",
                cls="font-serif text-2xl font-semibold text-[#1a2e44] mb-6 text-center",
            ),
            fh.Div(
                fh.Form(
                    fh.Input(type="hidden", id="token", value=token),
                    fh.Input(type="hidden", id="email", value=user_email),
                    fh.Div(
                        fh.Label(
                            "New Password",
                            for_="password",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.P(
                            "At least 8 characters with uppercase, lowercase, number, and special character",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        fh.Input(
                            id="password",
                            type="password",
                            placeholder="New password",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-4",
                    ),
                    fh.Div(
                        fh.Label(
                            "Confirm Password",
                            for_="confirm_password",
                            cls="block text-xs uppercase tracking-[0.2em] text-slate-500 mb-2",
                        ),
                        fh.Input(
                            id="confirm_password",
                            type="password",
                            placeholder="Confirm new password",
                            required=True,
                            cls="w-full p-3 bg-white border border-slate-300 rounded text-[#1a2e44] focus:outline-none focus:ring-2 focus:ring-teal-600 focus:border-teal-600",
                        ),
                        cls="mb-6",
                    ),
                    fh.Div(
                        fh.Button(
                            "Reset Password",
                            type="submit",
                            cls="w-full inline-flex items-center justify-center bg-[#1a2e44] text-[#faf8f2] py-3 rounded hover:bg-[#0f1e30] focus:outline-none focus:ring-2 focus:ring-teal-600 transition-colors font-medium uppercase tracking-[0.15em] text-sm",
                        ),
                        cls="mb-4",
                    ),
                    fh.Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/reset-password",
                    hx_target="#error",
                    cls="w-full",
                ),
                cls="w-full max-w-md",
            ),
            cls="bg-[#fdfcf8] p-8 rounded border border-slate-300",
        ),
        cls="flex justify-center items-center py-16 px-4",
    )

    # Return the complete page
    return page_container("Reset Password - FeedForward", reset_password_content)


@rt("/reset-password")
def post(token: str, email: str, password: str, confirm_password: str):
    # Validate inputs
    if password != confirm_password:
        return "Passwords do not match"

    if not is_strong_password(password):
        return "Password must be at least 8 characters with uppercase, lowercase, number, and special character"

    try:
        user = users[email]

        # Validate token
        if not (
            user.reset_token and secrets.compare_digest(user.reset_token, token)
        ) or not is_reset_token_valid(user.reset_token_expiry):
            return "Invalid or expired reset token"

        # Update password
        user.password = get_password_hash(password)

        # Clear reset token
        user.reset_token = ""
        user.reset_token_expiry = ""

        # Save changes
        users.update(user)

        # Redirect to login
        return HttpHeader("HX-Redirect", "/login?message=password_reset_success")

    except NotFoundError:
        return "Invalid user"
