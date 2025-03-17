import os
from passlib.context import CryptContext
from dotenv import load_dotenv
from starlette.responses import Response, RedirectResponse
from starlette.exceptions import HTTPException
from fasthtml.common import serve, Titled, Container, Div, H1, H2, H3, P, A, Span, Hr, Button
from fasthtml.common import Input, Label, Form, Header, Footer, Nav, Script, Style, HttpHeader

# Import app instance
from app import app, rt

# Register all routes
from app.routes import register_routes
register_routes()

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

# Import UI components
from app.utils.ui import page_header, page_footer, page_container

# --- Landing Page ---
@rt('/')
def get():
    """Root route redirects to landing page"""
    return RedirectResponse('/landing', status_code=303)

@rt('/landing')
def get():
    """Landing page for FeedForward"""
    # Create the main content for the landing page
    landing_content = Div(
            
            # Hero Section
            Div(
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
                                "Sign up", 
                                href="/register", 
                                cls="bg-blue-500 text-white px-6 py-3 rounded-lg text-lg hover:bg-blue-600 transition-colors mr-4"
                            ),
                            A(
                                "Learn More", 
                                href="#features", 
                                cls="text-blue-500 hover:text-blue-700 text-lg transition-colors"
                            ),
                            cls="flex items-center justify-center"
                        ),
                        cls="max-w-2xl mx-auto text-center"
                    ),
                    cls="bg-gray-50 p-8 rounded-lg shadow-md"
                ),
                cls="container mx-auto px-4 py-16 flex justify-center bg-gray-100"
            ),
            
            # Features Section
            Div(
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
                                    cls="bg-blue-500 text-white w-10 h-10 rounded-lg flex items-center justify-center font-bold mb-4"
                                ),
                                H3(
                                    "Submit Your Work", 
                                    cls="text-xl font-semibold text-gray-800 mb-2"
                                ),
                                P(
                                    "Upload assignments easily with our intuitive interface.",
                                    cls="text-gray-600"
                                ),
                                cls="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                            ),
                            # Feature 2
                            Div(
                                Div(
                                    "2",
                                    cls="bg-green-500 text-white w-10 h-10 rounded-lg flex items-center justify-center font-bold mb-4"
                                ),
                                H3(
                                    "Receive Smart Feedback", 
                                    cls="text-xl font-semibold text-gray-800 mb-2"
                                ),
                                P(
                                    "Get detailed, constructive feedback based on your specific assignment criteria.",
                                    cls="text-gray-600"
                                ),
                                cls="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                            ),
                            # Feature 3
                            Div(
                                Div(
                                    "3",
                                    cls="bg-purple-500 text-white w-10 h-10 rounded-lg flex items-center justify-center font-bold mb-4"
                                ),
                                H3(
                                    "Iterative Improvement", 
                                    cls="text-xl font-semibold text-gray-800 mb-2"
                                ),
                                P(
                                    "Track your progress and refine your work through multiple drafts.",
                                    cls="text-gray-600"
                                ),
                                cls="bg-gray-50 p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow"
                            ),
                            cls="grid md:grid-cols-3 gap-8"
                        ),
                        cls="bg-gray-50 p-8 rounded-lg shadow-md"
                    ),
                    cls="container mx-auto px-4 py-16"
                ),
                id="features",
                cls="bg-gray-100"
            ),
    )
    
    # Return the complete page with header and footer
    return Titled(
        "FeedForward: Elevate Your Learning",
        Div(
            page_header(show_auth_buttons=True),
            Div(
                landing_content,
                cls="flex-grow"
            ),
            page_footer(),
            cls="min-h-screen flex flex-col"
        )
    )

# --- Start the Server ---
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Start the server
    serve()

