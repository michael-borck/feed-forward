import os
from passlib.context import CryptContext
from dotenv import load_dotenv
from starlette.responses import Response, RedirectResponse
from starlette.exceptions import HTTPException
from fasthtml.common import serve, Titled, Container, Div, H1, H2, H3, P, A, Span, Hr, Button, Img
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

# --- Brand Colors ---
# Primary: Navy/indigo
# Secondary: Light blue
# Accent: Teal
# Gray shades for neutrals

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
            
            # Hero Section with gradient background
            Div(
                Div(
                    Div(
                        # Logo/Wordmark
                        Div(
                            Span("Feed", cls="text-indigo-600 font-bold"),
                            Span("Forward", cls="text-teal-500 font-bold"),
                            cls="text-5xl mb-2"
                        ),
                        H1(
                            "Elevate Your Learning", 
                            cls="text-4xl font-bold text-gray-800 mb-3"
                        ),
                        P(
                            "Transforming feedback into a path to success.",
                            cls="text-lg text-gray-600 mb-8 max-w-xl mx-auto"
                        ),
                        Div(
                            A(
                                "Sign up", 
                                href="/register", 
                                cls="bg-indigo-600 text-white px-6 py-3 rounded-lg text-lg font-medium hover:bg-indigo-700 transition-all shadow-md hover:shadow-lg mr-4 cursor-pointer relative z-20"
                            ),
                            A(
                                "Learn More", 
                                href="#features", 
                                cls="bg-white text-indigo-600 border border-indigo-600 px-6 py-3 rounded-lg text-lg hover:bg-indigo-50 transition-colors cursor-pointer relative z-20"
                            ),
                            cls="flex items-center justify-center relative z-20"
                        ),
                        cls="max-w-2xl mx-auto text-center"
                    ),
                    # Abstract background shapes
                    Div(
                        Div(cls="absolute top-20 right-20 w-20 h-20 rounded-full bg-indigo-200 opacity-50"),
                        Div(cls="absolute bottom-10 left-20 w-32 h-32 rounded-full bg-teal-200 opacity-50"),
                        Div(cls="absolute top-40 left-40 w-16 h-16 rounded-full bg-indigo-300 opacity-30"),
                        cls="absolute inset-0 overflow-hidden pointer-events-none"
                    ),
                    cls="bg-gradient-to-br from-gray-50 to-indigo-50 p-16 rounded-xl shadow-lg relative"
                ),
                cls="container mx-auto px-4 py-20 flex justify-center"
            ),
            
            # Features Section with enhanced styling
            Div(
                Div(
                    Div(
                        H2(
                            "How FeedForward Works", 
                            cls="text-3xl font-bold text-center text-indigo-900 mb-4"
                        ),
                        P(
                            "Our platform makes iterative learning simple and effective.",
                            cls="text-center text-gray-600 mb-12 max-w-2xl mx-auto" 
                        ),
                        Div(
                            # Feature 1
                            Div(
                                Div(
                                    Div(
                                        "1",
                                        cls="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl"
                                    ),
                                    cls="mb-4 flex justify-center"
                                ),
                                H3(
                                    "Submit Your Work", 
                                    cls="text-xl font-semibold text-indigo-900 mb-3 text-center"
                                ),
                                Div(
                                    P("• Upload assignments effortlessly", cls="text-gray-600 mb-1"),
                                    P("• Support for multiple file formats", cls="text-gray-600 mb-1"),
                                    P("• Simple drag-and-drop interface", cls="text-gray-600"),
                                    cls="text-left"
                                ),
                                cls="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border-t-4 border-indigo-600"
                            ),
                            # Feature 2
                            Div(
                                Div(
                                    Div(
                                        "2",
                                        cls="bg-teal-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl"
                                    ),
                                    cls="mb-4 flex justify-center"
                                ),
                                H3(
                                    "Receive Smart Feedback", 
                                    cls="text-xl font-semibold text-indigo-900 mb-3 text-center"
                                ),
                                Div(
                                    P("• Detailed, constructive feedback", cls="text-gray-600 mb-1"),
                                    P("• Tailored to assignment criteria", cls="text-gray-600 mb-1"),
                                    P("• Clear action items for improvement", cls="text-gray-600"),
                                    cls="text-left"
                                ),
                                cls="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border-t-4 border-teal-600"
                            ),
                            # Feature 3
                            Div(
                                Div(
                                    Div(
                                        "3",
                                        cls="bg-indigo-600 text-white w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl"
                                    ),
                                    cls="mb-4 flex justify-center"
                                ),
                                H3(
                                    "Iterative Improvement", 
                                    cls="text-xl font-semibold text-indigo-900 mb-3 text-center"
                                ),
                                Div(
                                    P("• Track progress across drafts", cls="text-gray-600 mb-1"),
                                    P("• Visualize your improvement", cls="text-gray-600 mb-1"),
                                    P("• Build on feedback systematically", cls="text-gray-600"),
                                    cls="text-left"
                                ),
                                cls="bg-white p-8 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border-t-4 border-indigo-600"
                            ),
                            cls="grid md:grid-cols-3 gap-8"
                        ),
                        cls="p-4"
                    ),
                    cls="container mx-auto px-4 py-20"
                ),
                id="features",
                cls="bg-gradient-to-b from-gray-50 to-gray-100"
            ),
            
            # Testimonials Section (optional)
            Div(
                Div(
                    H2(
                        "What Our Users Say",
                        cls="text-3xl font-bold text-center text-indigo-900 mb-12"
                    ),
                    Div(
                        # Testimonial 1
                        Div(
                            P("\"FeedForward helped me improve my writing style significantly. The feedback was actionable and specific.\"", 
                              cls="italic text-gray-700 mb-4"),
                            Div(
                                P("Sarah J.", cls="font-medium text-indigo-800"),
                                P("Literature Student", cls="text-sm text-gray-500"),
                                cls="flex flex-col"
                            ),
                            cls="bg-white p-6 rounded-lg shadow"
                        ),
                        # Testimonial 2
                        Div(
                            P("\"As an instructor, I can now provide consistent, high-quality feedback to all students, even in large classes.\"", 
                              cls="italic text-gray-700 mb-4"),
                            Div(
                                P("Dr. Thomas R.", cls="font-medium text-indigo-800"),
                                P("Computer Science Professor", cls="text-sm text-gray-500"),
                                cls="flex flex-col"
                            ),
                            cls="bg-white p-6 rounded-lg shadow"
                        ),
                        cls="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto"
                    ),
                    cls="container mx-auto px-4 py-16"
                ),
                cls="bg-gradient-to-b from-gray-100 to-indigo-50"
            ),
    )
    
    # Add smooth scrolling JavaScript
    scroll_script = Script("""
    document.addEventListener('DOMContentLoaded', function() {
        // Find anchor links that point to IDs on this page
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    });
    """)
    
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
            scroll_script,
            cls="min-h-screen flex flex-col"
        )
    )

# --- Start the Server ---
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Create temporary upload directory if it doesn't exist
    os.makedirs("data/uploads", exist_ok=True)
    
    # Start the server
    serve()

