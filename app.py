import os
from passlib.context import CryptContext
from dotenv import load_dotenv
from starlette.responses import Response, RedirectResponse
from starlette.exceptions import HTTPException
from fasthtml.common import serve, Titled, Container, Div, H1, P, A, Span, Hr, Button
from fasthtml.common import Input, Label, Form, Header, Footer, Nav, Script, Style, HttpHeader

# Import app instance
from app import app, rt

# Import app models
from app.models.user import User, Role, db, users
from app.models.course import Course, Enrollment
from app.models.assignment import Assignment, Rubric, RubricCategory
from app.models.feedback import AIModel, Draft, ModelRun, CategoryScore, FeedbackItem, AggregatedFeedback
from app.models.config import SystemConfig, AggregationMethod, FeedbackStyle, MarkDisplayOption, AssignmentSettings

# Import utils and services
from app.utils.email import send_verification_email, generate_verification_token
from app.utils.auth import get_password_hash, verify_password

# Load environment variables
load_dotenv()
APP_DOMAIN = os.environ.get("APP_DOMAIN", "http://localhost:5001")

# Import authentication decorators
from app import basic_auth, role_required, instructor_required, student_required, admin_required

# --- Landing Page ---
@rt('/')
def get():
    """Root route redirects to landing page"""
    return RedirectResponse('/landing', status_code=303)

@rt('/landing')
def get():
    """Landing page for FeedForward"""
    return Titled(
        "FeedForward - Intelligent Learning Feedback",
        Div(
            # Navigation with Sign In and Sign Up
            Div(
                Div(
                    A("FeedForward", href="/", cls="text-2xl font-bold text-blue-600"),
                    cls="flex items-center"
                ),
                Div(
                    A(
                        "Sign In", 
                        href="/login", 
                        cls="mr-4 text-blue-600 hover:text-blue-800 transition-colors"
                    ),
                    A(
                        "Sign Up", 
                        href="/register", 
                        cls="bg-blue-500 text-white px-4 py-2 rounded-full hover:bg-blue-600 transition-colors"
                    ),
                    cls="flex items-center"
                ),
                cls="container mx-auto flex justify-between items-center p-4"
            ),
            
            # Hero Section
            Div(
                Div(
                    H1(
                        "FeedForward: Elevate Your Learning", 
                        cls="text-4xl font-bold text-gray-800 mb-6"
                    ),
                    P(
                        "Transforming feedback into a path to success.",
                        cls="text-xl text-gray-600 mb-8"
                    ),
                    Div(
                        A(
                            "Get Started", 
                            href="/register", 
                            cls="bg-blue-500 text-white px-6 py-3 rounded-full text-lg hover:bg-blue-600 transition-colors mr-4"
                        ),
                        A(
                            "Learn More", 
                            href="#features", 
                            cls="text-blue-500 hover:text-blue-700 text-lg transition-colors"
                        ),
                        cls="flex items-center"
                    ),
                    cls="max-w-2xl mx-auto text-center"
                ),
                cls="container mx-auto px-4 py-16 text-center"
            ),
            
            # Features Section
            Div(
                Div(
                    H2(
                        "How FeedForward Works", 
                        cls="text-3xl font-bold text-center text-gray-800 mb-12"
                    ),
                    Div(
                        # Feature 1
                        Div(
                            Div(
                                "1",
                                cls="bg-blue-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold mb-4"
                            ),
                            H3(
                                "Submit Your Work", 
                                cls="text-xl font-semibold text-gray-800 mb-2"
                            ),
                            P(
                                "Upload assignments easily with our intuitive interface.",
                                cls="text-gray-600"
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                        ),
                        # Feature 2
                        Div(
                            Div(
                                "2",
                                cls="bg-green-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold mb-4"
                            ),
                            H3(
                                "Receive Smart Feedback", 
                                cls="text-xl font-semibold text-gray-800 mb-2"
                            ),
                            P(
                                "Get detailed, constructive feedback based on your specific assignment criteria.",
                                cls="text-gray-600"
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                        ),
                        # Feature 3
                        Div(
                            Div(
                                "3",
                                cls="bg-purple-500 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold mb-4"
                            ),
                            H3(
                                "Iterative Improvement", 
                                cls="text-xl font-semibold text-gray-800 mb-2"
                            ),
                            P(
                                "Track your progress and refine your work through multiple drafts.",
                                cls="text-gray-600"
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                        ),
                        cls="grid md:grid-cols-3 gap-8"
                    ),
                    cls="container mx-auto px-4 py-16"
                ),
                id="features",
                cls="bg-gray-100"
            ),
            
            # Footer
            Div(
                Div(
                    Div(
                        P(
                            "© 2025 FeedForward. All rights reserved.", 
                            cls="text-gray-500"
                        ),
                        cls="text-center"
                    ),
                    cls="container mx-auto py-8"
                ),
                cls="bg-gray-100"
            ),
            
            cls="min-h-screen flex flex-col"
        )
    )

# --- Start the Server ---
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Import route modules
    from app.routes import auth, student, instructor, admin
    
    # Start the server
    serve()

