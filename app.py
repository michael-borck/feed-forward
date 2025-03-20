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

# --- Legal Pages ---
@rt('/privacy')
def get():
    """Privacy Policy page"""
    # Create a simplified privacy policy page instead of parsing markdown
    privacy_content = Div(
        H1("FeedForward Privacy Policy", cls="text-3xl font-bold text-indigo-900 mb-6"),
        
        H2("Data Collection and Usage", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("FeedForward is designed with student privacy as a core principle. We collect and process the following data to provide feedback services:", 
          cls="mb-4 text-gray-700"),
        
        H3("Student Information", cls="text-xl font-bold text-indigo-700 mt-6 mb-3"),
        Div(
            Div("• Basic account information (name, email)", cls="ml-6 mb-2 text-gray-700"),
            Div("• Course enrollment details", cls="ml-6 mb-2 text-gray-700"),
            Div("• Assignment metadata (submissions, dates, word counts)", cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H3("Submission Content", cls="text-xl font-bold text-indigo-700 mt-6 mb-3"),
        Div(
            Div("• Temporary storage only: Student submitted work is stored only temporarily while feedback is being generated", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Once feedback is provided, the original submission content is automatically removed from our system", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• We retain only metadata such as word count, submission dates, and generated feedback", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("Data Protection Measures", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        
        H3("Submission Privacy", cls="text-xl font-bold text-indigo-700 mt-6 mb-3"),
        Div(
            Div("1. Temporary Storage: Assignment content is stored only as long as necessary to generate feedback", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("2. Automatic Deletion: After feedback is generated, the content is automatically removed", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("3. Metadata Retention: We keep submission metadata (word count, etc.) for tracking progress", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("4. Student Notification: Students are informed at submission time that their content will be removed", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("Student Rights", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("Students have the following rights regarding their data:", cls="mb-4 text-gray-700"),
        Div(
            Div("1. Transparency: Clear information about how their submissions are processed", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("2. Limited Storage: Assurance that the content of their submissions is not permanently stored", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("3. Retention of Own Work: Students are advised to maintain their own copies of submitted work", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("Policy Updates", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("This privacy policy may be updated periodically to reflect changes in our practices. Major changes will be communicated to users.", 
          cls="mb-4 text-gray-700"),
          
        cls="prose max-w-none"
    )
    
    # Create the main content for the privacy page
    privacy_page_content = Div(
        Div(
            Div(
                Div(privacy_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md"
            ),
            cls="max-w-4xl mx-auto py-12"
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50"
    )
    
    # Return the complete page with header and footer
    return Titled(
        "Privacy Policy | FeedForward",
        Div(
            page_header(show_auth_buttons=True),
            privacy_page_content,
            page_footer(),
            cls="min-h-screen flex flex-col"
        )
    )

@rt('/terms')
def get():
    """Terms of Service page"""
    terms_content = Div(
        H1("FeedForward Terms of Service", cls="text-3xl font-bold text-indigo-900 mb-6"),
        
        H2("1. Acceptance of Terms", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("By accessing or using the FeedForward platform, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using this service.", 
          cls="mb-4 text-gray-700"),
        
        H2("2. Educational Use", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("FeedForward is designed exclusively for educational purposes. The platform should be used by students and educators in accordance with their institution's academic policies.", 
          cls="mb-4 text-gray-700"),
        
        H2("3. User Accounts", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        Div(
            Div("• Users are responsible for maintaining the confidentiality of their account credentials", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Users agree to accept responsibility for all activities that occur under their account", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Users must provide accurate information when creating an account", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("4. Content Ownership", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        Div(
            Div("• Users retain ownership of content they submit to the platform", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Users grant FeedForward a limited license to process their submissions for the purpose of providing feedback", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• As described in our Privacy Policy, submission content is not permanently stored", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("5. Prohibited Use", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("Users may not use FeedForward to:", cls="mb-4 text-gray-700"),
        Div(
            Div("• Submit content that violates intellectual property rights", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Attempt to use the platform as a file storage or backup service", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Engage in any illegal activity", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• Interfere with the proper functioning of the platform", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("6. Service Limitations", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        Div(
            Div("• FeedForward provides automated feedback as an educational tool, not as definitive assessment", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• The accuracy of feedback depends on many factors including the quality of submissions", 
                cls="ml-6 mb-2 text-gray-700"),
            Div("• The platform may occasionally experience downtime for maintenance or updates", 
                cls="ml-6 mb-2 text-gray-700"),
            cls="mb-6"
        ),
        
        H2("7. Termination", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("FeedForward reserves the right to terminate or suspend access to the service without prior notice for conduct that violates these Terms of Service.", 
          cls="mb-4 text-gray-700"),
        
        H2("8. Disclaimer of Warranties", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("The service is provided \"as is\" without warranties of any kind, either express or implied. FeedForward does not warrant that the service will be uninterrupted or error-free.", 
          cls="mb-4 text-gray-700"),
        
        H2("9. Institutional Relationships", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("When FeedForward is deployed by an educational institution, users may also be subject to the policies and terms of that institution.", 
          cls="mb-4 text-gray-700"),
        
        H2("10. Changes to Terms", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("FeedForward reserves the right to modify these terms at any time. Users will be notified of significant changes.", 
          cls="mb-4 text-gray-700"),
        
        H2("11. Governing Law", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("These Terms shall be governed by the laws of Australia, without regard to its conflict of law provisions.", 
          cls="mb-4 text-gray-700"),
        
        P("Last updated: March 20, 2025", cls="text-gray-500 italic mt-8"),
        
        cls="prose max-w-none"
    )
    
    # Create the main content for the terms page
    terms_page_content = Div(
        Div(
            Div(
                Div(terms_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md"
            ),
            cls="max-w-4xl mx-auto py-12"
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50"
    )
    
    # Return the complete page with header and footer
    return Titled(
        "Terms of Service | FeedForward",
        Div(
            page_header(show_auth_buttons=True),
            terms_page_content,
            page_footer(),
            cls="min-h-screen flex flex-col"
        )
    )

@rt('/contact')
def get():
    """Contact page with developer information"""
    contact_content = Div(
        H1("Contact Us", cls="text-3xl font-bold text-indigo-900 mb-6"),
        
        H2("Project Lead", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        Div(
            P("Michael Borck", cls="text-xl font-semibold text-indigo-700 mb-1"),
            P("Email: michael.borck@curtin.edu.au", cls="text-gray-700 mb-2"),
            P("Business AI Research Group (BARG)", cls="text-gray-700 mb-1"),
            P("Faculty of Business and Law", cls="text-gray-700 mb-1"),
            P("Curtin University", cls="text-gray-700 mb-4"),
            cls="mb-6"
        ),
        
        H2("Support", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("For questions or technical support with your institution's FeedForward installation, please contact your local administrators.", 
          cls="text-gray-700 mb-4"),
          
        H2("Contribute", cls="text-2xl font-bold text-indigo-800 mt-8 mb-4"),
        P("FeedForward is an open-source project. If you're interested in contributing or reporting issues, please visit our GitHub repository.", 
          cls="text-gray-700 mb-4"),
        
        cls="prose max-w-none"
    )
    
    # Create the main content for the contact page
    contact_page_content = Div(
        Div(
            Div(
                Div(contact_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md"
            ),
            cls="max-w-4xl mx-auto py-12"
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50"
    )
    
    # Return the complete page with header and footer
    return Titled(
        "Contact Us | FeedForward",
        Div(
            page_header(show_auth_buttons=True),
            contact_page_content,
            page_footer(),
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

