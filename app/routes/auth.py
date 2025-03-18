"""
Authentication routes (login, register, verify, password reset, etc.)
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse
from datetime import datetime
from fastlite import NotFoundError

from app.models.user import User, Role, users
from app.utils.email import send_verification_email, send_password_reset_email, generate_verification_token, APP_DOMAIN
from app.utils.auth import get_password_hash, verify_password, is_institutional_email, is_strong_password
from app.utils.auth import is_reset_token_valid, generate_token_expiry

# Get the route table and FastHTML components from the app
from app import app, rt
from fasthtml.common import Container, Div, H1, H2, H3, P, A, Span, Hr, Button
from fasthtml.common import Input, Label, Form, Header, Footer, Nav, Script, Style, HttpHeader

# Import UI components
from app.utils.ui import page_header, page_footer, page_container

# --- Registration Routes ---
@rt('/register')
def get():
    # Create the registration form content
    registration_content = Div(
        Div(
            # Brand logo on registration form
            Div(
                Span("Feed", cls="text-indigo-600 font-bold"),
                Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center"
            ),
            H1("Create Your Account", cls="text-2xl font-bold text-indigo-900 mb-6 text-center"),
            Div(
                Form(
                    Div(
                        Label("Name", for_="name", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="name", type="text", placeholder="Your full name", required=True, 
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Email", for_="email", cls="block text-indigo-900 font-medium mb-1"),
                        P("Must be a Curtin email address (curtin.edu.au)", 
                          cls="text-sm text-gray-500 mb-1"),
                        Input(id="email", type="email", placeholder="Your email address", required=True, 
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
                        Button("Sign up", type="submit", cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/register",
                    hx_target="#error",
                    cls="w-full"
                ),
                Hr(cls="my-6 border-gray-200"),
                P("Already have an account? ", A("Sign in here", href="/login", cls="text-indigo-600 hover:underline font-medium"), 
                  cls="text-center text-gray-600"),
                cls="w-full max-w-md"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
    )
    
    # Return the complete page
    return page_container("Sign up - FeedForward", registration_content)

@rt('/register')
def post(name: str, email: str, password: str, confirm_password: str):
    # Validate inputs
    if not name or not email or not password or not confirm_password:
        return "All fields are required"
    
    if password != confirm_password:
        return "Passwords do not match"
    
    if not is_strong_password(password):
        return "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
    
    # Check if email is institutional
    is_valid, role = is_institutional_email(email)
    if not is_valid:
        return "Please use a valid Curtin email address (curtin.edu.au)"
    
    # Only instructors can register directly for now (students invited by instructors)
    if role != Role.INSTRUCTOR:
        return "Only instructors can register directly. Students are invited by instructors."
    
    try:
        # Check if user already exists
        users[email]
        return "User already exists"
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
            approved=False if role == Role.INSTRUCTOR else True,  # Instructors need approval
            department="",
            reset_token="",
            reset_token_expiry=""
        )
        
        # Insert into database
        users.insert(new_user)
        
        # Send verification email
        success, message = send_verification_email(email, token)
        if success:
            return "Registration successful. Please check your email to verify your account."
        else:
            # For security, don't expose the exact error to the user
            print(f"EMAIL ERROR DETAILS: {message}")
            # Provide a way to verify manually for development purposes
            verify_link = f"{APP_DOMAIN}/verify?token={token}"
            return Div(
                P("Registration successful but there was an issue sending the verification email.", cls="text-red-500 mb-2"),
                P("For development purposes, you can verify your account using this link:", cls="mb-2"),
                A(verify_link, href=verify_link, cls="text-blue-500 underline break-all", target="_blank"),
                cls="text-center"
            )

# --- Email Verification Route ---
@rt('/verify')
def get(token: str):
    # Import UI components
    from app.utils.ui import page_header, page_footer
    
    # Debug print
    import logging
    logging.basicConfig(level=logging.DEBUG)
    logging.debug(f"Verifying token: {token}")
    
    # Look for a user with the matching token
    for user in users():
        logging.debug(f"Checking user: {user.email}, token: {user.verification_token}")
        if user.verification_token == token:
            user.verified = True
            # Clear the token after successful verification
            user.verification_token = ""
            users.update(user)
            
            # Success message content
            verify_success_content = Div(
                Div(
                    Div(
                        # Success icon
                        Div(
                            Span("✅", cls="text-5xl block mb-4"),
                            cls="text-center"
                        ),
                        # Brand logo
                        Div(
                            Span("Feed", cls="text-indigo-600 font-bold"),
                            Span("Forward", cls="text-teal-500 font-bold"),
                            cls="text-3xl mb-4 text-center"
                        ),
                        H1("Email Verified Successfully!", cls="text-2xl font-bold text-indigo-900 mb-4 text-center"),
                        P("Your email has been verified. You can now log in to your account.", cls="text-gray-600 mb-6 text-center"),
                        Div(
                            A("Login to Your Account", href="/login", 
                              cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                            cls="text-center"
                        ),
                        cls="text-center"
                    ),
                    cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 max-w-md w-full"
                ),
                cls="flex justify-center items-center py-16 px-4"
            )
            
            # Return the complete page
            return page_container("Email Verified - FeedForward", verify_success_content)
            
    # Error message content for invalid token
    verify_error_content = Div(
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
                H1("Verification Failed", cls="text-2xl font-bold text-indigo-900 mb-4 text-center"),
                P("The verification link is invalid or has expired.", cls="text-gray-600 mb-6 text-center"),
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
    
    # Return the complete page
    return page_container("Verification Failed - FeedForward", verify_error_content)

# --- Login Routes ---
@rt('/login')
def get():
    # Create the login form content
    login_content = Div(
        Div(
            # Brand logo on login form
            Div(
                Span("Feed", cls="text-indigo-600 font-bold"),
                Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center"
            ),
            H1("Sign in to Your Account", cls="text-2xl font-bold text-indigo-900 mb-6 text-center"),
            Div(
                Form(
                    Div(
                        Label("Email", for_="email", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="email", type="email", placeholder="Your email address", required=True, 
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Password", for_="password", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="password", type="password", placeholder="Your password", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        A("Forgot password?", href="/forgot-password", cls="text-indigo-600 hover:underline text-sm font-medium"),
                        cls="mb-6 text-right"
                    ),
                    Div(
                        Button("Sign in", type="submit", cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/login",
                    hx_target="#error",
                    cls="w-full"
                ),
                Hr(cls="my-6 border-gray-200"),
                P("Don't have an account? ", A("Sign up here", href="/register", cls="text-indigo-600 hover:underline font-medium"), 
                  cls="text-center text-gray-600"),
                cls="w-full max-w-md"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
    )
    
    # Return the complete page
    return page_container("Sign in - FeedForward", login_content)

@rt('/login')
def post(session, email: str, password: str):
    try:
        user = users[email]
    except NotFoundError:
        return "Email or password are incorrect"
    
    if not user.verified:
        return "Please verify your email before logging in."
    
    # For instructors, check if they're approved
    if user.role == Role.INSTRUCTOR and not user.approved:
        return "Your account is pending approval. Please contact the administrator."
    
    if not verify_password(password, user.password):
        return "Email or password are incorrect"

    # Store user info in session
    session['auth'] = user.email
    
    # Redirect to appropriate dashboard based on role
    if user.role == Role.INSTRUCTOR:
        return HttpHeader('HX-Redirect', '/instructor/dashboard')
    elif user.role == Role.STUDENT:
        return HttpHeader('HX-Redirect', '/student/dashboard')
    elif user.role == Role.ADMIN:
        return HttpHeader('HX-Redirect', '/admin/dashboard')
    else:
        return HttpHeader('HX-Redirect', '/dashboard')

# --- Logout Route ---
@rt('/logout')
def post(session):
    if 'auth' in session:
        del session['auth']
    return HttpHeader('HX-Redirect', '/login')

# --- Forgot Password Routes ---
@rt('/forgot-password')
def get():
    # Create the forgot password content
    forgot_password_content = Div(
        Div(
            # Brand logo 
            Div(
                Span("Feed", cls="text-indigo-600 font-bold"),
                Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center"
            ),
            H1("Reset Your Password", cls="text-2xl font-bold text-indigo-900 mb-4 text-center"),
            P("Enter your email address and we'll send you a link to reset your password.", 
              cls="text-gray-600 mb-6 text-center"),
            Div(
                Form(
                    Div(
                        Label("Email", for_="email", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="email", type="email", placeholder="Your email address", required=True, 
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6"
                    ),
                    Div(
                        Button("Send Reset Link", type="submit", cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="message", cls="text-center block"),
                    hx_post="/forgot-password",
                    hx_target="#message",
                    cls="w-full"
                ),
                Hr(cls="my-6 border-gray-200"),
                P("Remember your password? ", A("Login here", href="/login", cls="text-indigo-600 hover:underline font-medium"), 
                  cls="text-center text-gray-600"),
                cls="w-full max-w-md"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
    )
    
    # Return the complete page
    return page_container("Reset Password - FeedForward", forgot_password_content)

@rt('/forgot-password')
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
            return Div(
                P("Password reset link sent. Please check your email.", cls="text-green-500"),
                cls="text-center"
            )
        else:
            # For security, don't expose the exact error to the user
            print(f"EMAIL ERROR DETAILS: {message}")
            # Provide a way to reset password manually for development purposes
            reset_link = f"{APP_DOMAIN}/reset-password?token={reset_token}"
            return Div(
                P("Failed to send reset link.", cls="text-red-500 mb-2"),
                P("For development purposes, you can reset your password using this link:", cls="mb-2"),
                A(reset_link, href=reset_link, cls="text-blue-500 underline break-all", target="_blank"),
                cls="text-center"
            )
    except NotFoundError:
        # Don't reveal if the email exists
        return Div(
            P("If your email is registered, you will receive a password reset link.", cls="text-green-500"),
            cls="text-center"
        )

# --- Reset Password Routes ---
@rt('/reset-password')
def get(token: str):
    # Import UI components
    from app.utils.ui import page_header, page_footer
    
    # Validate token
    valid_token = False
    user_email = ""
    
    for user in users():
        if user.reset_token == token and is_reset_token_valid(user.reset_token_expiry):
            valid_token = True
            user_email = user.email
            break
    
    if not valid_token:
        # Error message content for invalid token
        invalid_token_content = Div(
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
                    H1("Invalid or Expired Link", cls="text-2xl font-bold text-indigo-900 mb-4 text-center"),
                    P("The password reset link is invalid or has expired.", cls="text-gray-600 mb-6 text-center"),
                    Div(
                        A("Request New Link", href="/forgot-password", 
                          cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="text-center"
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 max-w-md w-full"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
        )
        
        # Return the complete page
        return page_container("Invalid Reset Link - FeedForward", invalid_token_content)
    
    # Valid token, show password reset form
    reset_password_content = Div(
        Div(
            # Brand logo
            Div(
                Span("Feed", cls="text-indigo-600 font-bold"),
                Span("Forward", cls="text-teal-500 font-bold"),
                cls="text-3xl mb-4 text-center"
            ),
            H1("Set New Password", cls="text-2xl font-bold text-indigo-900 mb-6 text-center"),
            Div(
                Form(
                    Input(type="hidden", id="token", value=token),
                    Input(type="hidden", id="email", value=user_email),
                    Div(
                        Label("New Password", for_="password", cls="block text-indigo-900 font-medium mb-1"),
                        P("At least 8 characters with uppercase, lowercase, number, and special character", 
                          cls="text-sm text-gray-500 mb-1"),
                        Input(id="password", type="password", placeholder="New password", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4"
                    ),
                    Div(
                        Label("Confirm Password", for_="confirm_password", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="confirm_password", type="password", placeholder="Confirm new password", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6"
                    ),
                    Div(
                        Button("Reset Password", type="submit", cls="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors font-medium shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="error", cls="text-red-500 block text-center"),
                    hx_post="/reset-password",
                    hx_target="#error",
                    cls="w-full"
                ),
                cls="w-full max-w-md"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls="flex justify-center items-center py-16 px-4 bg-gradient-to-br from-gray-50 to-indigo-50"
    )
    
    # Return the complete page
    return page_container("Reset Password - FeedForward", reset_password_content)

@rt('/reset-password')
def post(token: str, email: str, password: str, confirm_password: str):
    # Validate inputs
    if password != confirm_password:
        return "Passwords do not match"
    
    if not is_strong_password(password):
        return "Password must be at least 8 characters with uppercase, lowercase, number, and special character"
    
    try:
        user = users[email]
        
        # Validate token
        if user.reset_token != token or not is_reset_token_valid(user.reset_token_expiry):
            return "Invalid or expired reset token"
        
        # Update password
        user.password = get_password_hash(password)
        
        # Clear reset token
        user.reset_token = ""
        user.reset_token_expiry = ""
        
        # Save changes
        users.update(user)
        
        # Redirect to login
        return HttpHeader('HX-Redirect', '/login?message=password_reset_success')
    
    except NotFoundError:
        return "Invalid user"