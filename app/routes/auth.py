"""
Authentication routes (login, register, verify, password reset, etc.)
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse
from datetime import datetime

from app.models.user import User, Role, users
from app.utils.email import send_verification_email, send_password_reset_email, generate_verification_token
from app.utils.auth import get_password_hash, verify_password, is_institutional_email, is_strong_password
from app.utils.auth import is_reset_token_valid, generate_token_expiry

# Get the route table and FastHTML components from the app
from app import app, rt
from fasthtml.common import Container, Div, H1, H2, H3, P, A, Span, Hr, Button
from fasthtml.common import Input, Label, Form, Header, Footer, Nav, Script, Style, HttpHeader

# --- Registration Routes ---
@rt('/register')
def get():
    return Container(
        # Header with navigation bar
        Header(
            Div(
                # Left side - Logo and name
                Div(
                    H1("FeedForward", cls="text-2xl font-bold"),
                    cls="flex items-center"
                ),
                # Right side - Login/Register buttons
                Nav(
                    A("Login", href="/login", cls="bg-blue-500 text-white px-4 py-2 rounded-full mx-2 hover:bg-blue-600"),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-800 text-white p-4"
        ),
        
        # Registration form
        Div(
            Div(
                H1("Create Your Account", cls="text-2xl font-bold text-gray-800 mb-6 text-center"),
                Div(
                    Form(
                        Div(
                            Label("Name", for_="name", cls="block text-gray-700 mb-1"),
                            Input(id="name", type="text", placeholder="Your full name", required=True, 
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Email", for_="email", cls="block text-gray-700 mb-1"),
                            P("Must be a Curtin email address (curtin.edu.au)", 
                              cls="text-sm text-gray-500 mb-1"),
                            Input(id="email", type="email", placeholder="Your email address", required=True, 
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Password", for_="password", cls="block text-gray-700 mb-1"),
                            P("At least 8 characters with uppercase, lowercase, number, and special character", 
                              cls="text-sm text-gray-500 mb-1"),
                            Input(id="password", type="password", placeholder="Create a password", required=True,
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Confirm Password", for_="confirm_password", cls="block text-gray-700 mb-1"),
                            Input(id="confirm_password", type="password", placeholder="Confirm your password", required=True,
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-6"
                        ),
                        Div(
                            Button("Register", type="submit", cls="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Span(id="error", cls="text-red-500 block text-center"),
                        hx_post="/register",
                        hx_target="#error",
                        cls="w-full"
                    ),
                    Hr(cls="my-6"),
                    P("Already have an account? ", A("Login here", href="/login", cls="text-blue-500 hover:underline"), 
                      cls="text-center text-gray-600"),
                    cls="w-full max-w-md"
                ),
                cls="bg-white p-8 rounded-lg shadow-md"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gray-100"
        ),
        
        # Footer
        Footer(
            Div(
                P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
                Div(
                    A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    cls="flex"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-100 border-t border-gray-200 py-6"
        )
    )

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
        if send_verification_email(email, token):
            return "Registration successful. Please check your email to verify your account."
        else:
            return "Registration successful but failed to send verification email. Please contact support."

# --- Email Verification Route ---
@rt('/verify')
def get(token: str):
    # Create reusable header component
    header = Header(
        Div(
            # Left side - Logo and name
            Div(
                H1("FeedForward", cls="text-2xl font-bold"),
                cls="flex items-center"
            ),
            # Right side - Login/Register buttons
            Nav(
                A("Login", href="/login", cls="text-white px-4 py-2 rounded-full mx-2 hover:bg-gray-700"),
                A("Sign Up", href="/register", cls="bg-blue-500 text-white px-4 py-2 rounded-full mx-2 hover:bg-blue-600"),
                cls="flex items-center"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-800 text-white p-4"
    )
    
    # Create reusable footer component
    footer = Footer(
        Div(
            P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
            Div(
                A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                cls="flex"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-100 border-t border-gray-200 py-6"
    )
    
    # Look for a user with the matching token
    for user in users():
        if user.verification_token == token:
            user.verified = True
            # Clear the token after successful verification
            user.verification_token = ""
            users.update(user)
            
            # Success message
            return Container(
                header,
                Div(
                    Div(
                        Div(
                            Span("✅", cls="text-5xl block mb-4"),
                            H1("Email Verified Successfully!", cls="text-2xl font-bold text-gray-800 mb-4"),
                            P("Your email has been verified. You can now log in to your account.", cls="text-gray-600 mb-6"),
                            A("Login to Your Account", href="/login", cls="inline-block bg-blue-500 text-white px-6 py-3 rounded-md font-semibold hover:bg-blue-600"),
                            cls="text-center"
                        ),
                        cls="bg-white p-8 rounded-lg shadow-md max-w-md w-full"
                    ),
                    cls="flex justify-center items-center py-16 px-4 bg-gray-100"
                ),
                footer
            )
            
    # Error message for invalid token
    return Container(
        header,
        Div(
            Div(
                Div(
                    Span("❌", cls="text-5xl block mb-4"),
                    H1("Verification Failed", cls="text-2xl font-bold text-gray-800 mb-4"),
                    P("The verification link is invalid or has expired.", cls="text-gray-600 mb-6"),
                    A("Return to Home", href="/", cls="inline-block bg-blue-500 text-white px-6 py-3 rounded-md font-semibold hover:bg-blue-600"),
                    cls="text-center"
                ),
                cls="bg-white p-8 rounded-lg shadow-md max-w-md w-full"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gray-100"
        ),
        footer
    )

# --- Login Routes ---
@rt('/login')
def get():
    return Container(
        # Header with navigation bar
        Header(
            Div(
                # Left side - Logo and name
                Div(
                    H1("FeedForward", cls="text-2xl font-bold"),
                    cls="flex items-center"
                ),
                # Right side - Login/Register buttons
                Nav(
                    A("Sign Up", href="/register", cls="bg-blue-500 text-white px-4 py-2 rounded-full mx-2 hover:bg-blue-600"),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-800 text-white p-4"
        ),
        
        # Login form
        Div(
            Div(
                H1("Login to Your Account", cls="text-2xl font-bold text-gray-800 mb-6 text-center"),
                Div(
                    Form(
                        Div(
                            Label("Email", for_="email", cls="block text-gray-700 mb-1"),
                            Input(id="email", type="email", placeholder="Your email address", required=True, 
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Password", for_="password", cls="block text-gray-700 mb-1"),
                            Input(id="password", type="password", placeholder="Your password", required=True,
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            A("Forgot password?", href="/forgot-password", cls="text-blue-500 hover:underline text-sm"),
                            cls="mb-6 text-right"
                        ),
                        Div(
                            Button("Login", type="submit", cls="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Span(id="error", cls="text-red-500 block text-center"),
                        hx_post="/login",
                        hx_target="#error",
                        cls="w-full"
                    ),
                    Hr(cls="my-6"),
                    P("Don't have an account? ", A("Register here", href="/register", cls="text-blue-500 hover:underline"), 
                      cls="text-center text-gray-600"),
                    cls="w-full max-w-md"
                ),
                cls="bg-white p-8 rounded-lg shadow-md"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gray-100"
        ),
        
        # Footer
        Footer(
            Div(
                P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
                Div(
                    A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    cls="flex"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-100 border-t border-gray-200 py-6"
        )
    )

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
    return Container(
        # Header with navigation bar
        Header(
            Div(
                # Left side - Logo and name
                Div(
                    H1("FeedForward", cls="text-2xl font-bold"),
                    cls="flex items-center"
                ),
                # Right side - Login/Register buttons
                Nav(
                    A("Login", href="/login", cls="text-white px-4 py-2 rounded-full mx-2 hover:bg-gray-700"),
                    A("Sign Up", href="/register", cls="bg-blue-500 text-white px-4 py-2 rounded-full mx-2 hover:bg-blue-600"),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-800 text-white p-4"
        ),
        
        # Forgot password form
        Div(
            Div(
                H1("Reset Your Password", cls="text-2xl font-bold text-gray-800 mb-6 text-center"),
                P("Enter your email address and we'll send you a link to reset your password.", 
                  cls="text-gray-600 mb-6 text-center"),
                Div(
                    Form(
                        Div(
                            Label("Email", for_="email", cls="block text-gray-700 mb-1"),
                            Input(id="email", type="email", placeholder="Your email address", required=True, 
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-6"
                        ),
                        Div(
                            Button("Send Reset Link", type="submit", cls="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Span(id="message", cls="text-center block"),
                        hx_post="/forgot-password",
                        hx_target="#message",
                        cls="w-full"
                    ),
                    Hr(cls="my-6"),
                    P("Remember your password? ", A("Login here", href="/login", cls="text-blue-500 hover:underline"), 
                      cls="text-center text-gray-600"),
                    cls="w-full max-w-md"
                ),
                cls="bg-white p-8 rounded-lg shadow-md"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gray-100"
        ),
        
        # Footer
        Footer(
            Div(
                P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
                Div(
                    A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                    cls="flex"
                ),
                cls="container mx-auto flex justify-between items-center"
            ),
            cls="bg-gray-100 border-t border-gray-200 py-6"
        )
    )

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
        if send_password_reset_email(email, reset_token):
            return Div(
                P("Password reset link sent. Please check your email.", cls="text-green-500"),
                cls="text-center"
            )
        else:
            return Div(
                P("Failed to send reset link. Please try again later.", cls="text-red-500"),
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
    # Create reusable header component
    header = Header(
        Div(
            # Left side - Logo and name
            Div(
                H1("FeedForward", cls="text-2xl font-bold"),
                cls="flex items-center"
            ),
            # Right side - Login/Register buttons
            Nav(
                A("Login", href="/login", cls="text-white px-4 py-2 rounded-full mx-2 hover:bg-gray-700"),
                A("Sign Up", href="/register", cls="bg-blue-500 text-white px-4 py-2 rounded-full mx-2 hover:bg-blue-600"),
                cls="flex items-center"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-800 text-white p-4"
    )
    
    # Create reusable footer component
    footer = Footer(
        Div(
            P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
            Div(
                A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                cls="flex"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-100 border-t border-gray-200 py-6"
    )
    
    # Validate token
    valid_token = False
    user_email = ""
    
    for user in users():
        if user.reset_token == token and is_reset_token_valid(user.reset_token_expiry):
            valid_token = True
            user_email = user.email
            break
    
    if not valid_token:
        return Container(
            header,
            Div(
                Div(
                    Div(
                        Span("❌", cls="text-5xl block mb-4"),
                        H1("Invalid or Expired Link", cls="text-2xl font-bold text-gray-800 mb-4"),
                        P("The password reset link is invalid or has expired.", cls="text-gray-600 mb-6"),
                        A("Request New Link", href="/forgot-password", cls="inline-block bg-blue-500 text-white px-6 py-3 rounded-md font-semibold hover:bg-blue-600"),
                        cls="text-center"
                    ),
                    cls="bg-white p-8 rounded-lg shadow-md max-w-md w-full"
                ),
                cls="flex justify-center items-center py-16 px-4 bg-gray-100"
            ),
            footer
        )
    
    # Valid token, show password reset form
    return Container(
        header,
        Div(
            Div(
                H1("Set New Password", cls="text-2xl font-bold text-gray-800 mb-6 text-center"),
                Div(
                    Form(
                        Input(type="hidden", id="token", value=token),
                        Input(type="hidden", id="email", value=user_email),
                        Div(
                            Label("New Password", for_="password", cls="block text-gray-700 mb-1"),
                            P("At least 8 characters with uppercase, lowercase, number, and special character", 
                              cls="text-sm text-gray-500 mb-1"),
                            Input(id="password", type="password", placeholder="New password", required=True,
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Confirm Password", for_="confirm_password", cls="block text-gray-700 mb-1"),
                            Input(id="confirm_password", type="password", placeholder="Confirm new password", required=True,
                                  cls="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-6"
                        ),
                        Div(
                            Button("Reset Password", type="submit", cls="w-full bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"),
                            cls="mb-4"
                        ),
                        Span(id="error", cls="text-red-500 block text-center"),
                        hx_post="/reset-password",
                        hx_target="#error",
                        cls="w-full"
                    ),
                    cls="w-full max-w-md"
                ),
                cls="bg-white p-8 rounded-lg shadow-md"
            ),
            cls="flex justify-center items-center py-16 px-4 bg-gray-100"
        ),
        footer
    )

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