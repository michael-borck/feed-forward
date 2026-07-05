import os

from dotenv import load_dotenv
from fasthtml.common import (
    H1,
    H2,
    H3,
    A,
    Div,
    P,
    Span,
    serve,
)
from starlette.responses import RedirectResponse

# Import app instance
from app import rt

# Register all routes
from app.routes import register_routes

register_routes()

# Import app models

# Import utils and services

# Load environment variables
load_dotenv()
APP_DOMAIN = os.environ.get("APP_DOMAIN", "http://localhost:5001")

# Import authentication decorators
from typing import Optional

# --- Legacy style dicts ---
# Still referenced by the 404/403 error pages below. Values now point at the
# Editorial vocabulary (see app/utils/design.py) so those pages match the
# 2026-07 direction; migrating the call sites to design.py tokens directly is
# a follow-up cleanup.
from app.utils.design import TEXT as _TEXT
from app.utils.design import button_classes as _button_classes

# Import UI components
from app.utils.ui import dynamic_header, page_footer

BRAND_COLORS = {
    "primary": "[#1a2e44]",
    "primary-dark": "[#0f1e30]",
    "primary-light": "slate-600",
    "secondary": "teal-600",
    "secondary-dark": "teal-700",
    "secondary-light": "teal-500",
    "accent": "[#edeae1]",
    "accent-light": "[#faf8f2]",
    "text-primary": "[#1a2e44]",
    "text-secondary": "slate-700",
    "text-muted": "slate-500",
    "success": "teal-600",
    "warning": "amber-700",
    "error": "red-700",
    "border": "slate-300",
    "border-hover": "slate-400",
}

TYPOGRAPHY = {
    "hero": _TEXT["hero"],
    "h1": _TEXT["h1"],
    "h2": _TEXT["h2"],
    "h3": _TEXT["h3"],
    "body-lg": _TEXT["body"],
    "body": _TEXT["body"],
    "body-sm": _TEXT["body_sm"],
    "caption": _TEXT["meta"],
}

BUTTON_STYLES = {
    "primary": _button_classes("primary", "md"),
    "secondary": _button_classes("secondary", "md"),
    "ghost": _button_classes("ghost", "md"),
}


# --- Root Route with Smart Redirection ---
@rt("/")
def root_redirect(session=None):
    """Smart root route that redirects based on authentication status"""
    # Check for authenticated user
    if session and "auth" in session:
        try:
            # Import here to avoid circular imports
            from app.models.user import Role, users

            user = users[session["auth"]]

            # Redirect to appropriate dashboard based on role
            if user.role == Role.ADMIN:
                return RedirectResponse("/admin/dashboard", status_code=303)
            elif user.role == Role.INSTRUCTOR:
                return RedirectResponse("/instructor/dashboard", status_code=303)
            elif user.role == Role.STUDENT:
                return RedirectResponse("/student/dashboard", status_code=303)
        except Exception:
            # If there's an error, fall back to landing page
            pass

    # Default to landing page for unauthenticated users
    return RedirectResponse("/landing", status_code=303)


@rt("/landing")
def landing_page(session=None):
    """Landing page for FeedForward with dynamic header based on auth status"""
    from app.utils.design import COLOR, TEXT, button_classes

    steps = (
        (
            "01",
            "Submit a draft",
            "Upload your work or paste it in — essays, code, and more.",
        ),
        (
            "02",
            "Get rubric-aligned feedback",
            "AI feedback against your instructor's rubric, reviewed by them "
            "before you see it.",
        ),
        (
            "03",
            "Revise and resubmit",
            "Watch your aim improve with each draft — every revision lands "
            "closer to the bullseye.",
        ),
    )
    # Journal-style contents list: numbered entries over hairline rules.
    step_rows = [
        Div(
            Div(
                num,
                cls=f"font-serif text-lg text-{COLOR['text_muted']} w-10 shrink-0",
            ),
            Div(
                H3(title, cls=f"{TEXT['h3']} text-{COLOR['text_strong']}"),
                P(desc, cls=f"{TEXT['body_sm']} text-{COLOR['text_body']} mt-0.5"),
            ),
            cls=f"flex gap-3 py-4 border-t border-{COLOR['border']}",
        )
        for num, title, desc in steps
    ]

    landing_content = Div(
        # Editorial hero — asymmetric: serif headline left, ruled
        # journal-style contents right. Hairlines, no shadows, no gradients.
        Div(
            Div(
                Div(
                    "Curtin University · Formative assessment",
                    cls=f"{TEXT['label']} text-{COLOR['text_muted']} mb-5",
                ),
                H1(
                    "Better drafts, one revision at a time.",
                    cls=f"{TEXT['hero']} text-{COLOR['text_strong']}",
                ),
                P(
                    "Formative feedback on student drafts — AI-assisted, "
                    "rubric-aligned, instructor-reviewed.",
                    cls=f"text-lg text-{COLOR['text_body']} mt-6 max-w-md "
                    "leading-relaxed",
                ),
                Div(
                    A("Sign in", href="/login", cls=button_classes("primary", "lg")),
                    A(
                        "Create account →",
                        href="/register",
                        cls=(
                            f"{TEXT['label']} text-{COLOR['accent']} underline "
                            "underline-offset-8 decoration-2 px-2 py-3"
                        ),
                    ),
                    cls="flex flex-wrap items-center gap-5 mt-8",
                ),
                cls="md:col-span-7",
            ),
            Div(
                Div(
                    "How it works",
                    cls=f"{TEXT['label']} text-{COLOR['text_muted']} pb-3",
                ),
                *step_rows,
                cls=(f"md:col-span-5 md:pl-10 md:border-l border-{COLOR['border']}"),
            ),
            cls="max-w-5xl mx-auto px-6 py-16 grid md:grid-cols-12 gap-10",
        ),
    )

    return Div(
        dynamic_header(session),
        Div(landing_content, cls="flex-grow"),
        page_footer(),
        cls=f"min-h-screen flex flex-col bg-{COLOR['surface_alt']}",
    )


# --- Legal Pages ---
@rt("/privacy")
def privacy_page(session=None):
    """Privacy Policy page"""
    # Create a simplified privacy policy page instead of parsing markdown
    privacy_content = Div(
        H1("FeedForward Privacy Policy", cls="text-3xl font-bold text-slate-800 mb-6"),
        H2(
            "Data Collection and Usage",
            cls="text-2xl font-bold text-slate-700 mt-8 mb-4",
        ),
        P(
            "FeedForward is designed with student privacy as a core principle. We collect and process the following data to provide feedback services:",
            cls="mb-4 text-gray-700",
        ),
        H3("Student Information", cls="text-xl font-bold text-blue-700 mt-6 mb-3"),
        Div(
            Div(
                "• Basic account information (name, email)",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div("• Course enrollment details", cls="ml-6 mb-2 text-gray-700"),
            Div(
                "• Assignment metadata (submissions, dates, word counts)",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H3("Submission Content", cls="text-xl font-bold text-blue-700 mt-6 mb-3"),
        Div(
            Div(
                "• Temporary storage only: Student submitted work is stored only temporarily while feedback is being generated",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• Once feedback is provided, the original submission content is automatically removed from our system",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• We retain only metadata such as word count, submission dates, and generated feedback",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2(
            "Data Protection Measures",
            cls="text-2xl font-bold text-slate-700 mt-8 mb-4",
        ),
        H3("Submission Privacy", cls="text-xl font-bold text-blue-700 mt-6 mb-3"),
        Div(
            Div(
                "1. Temporary Storage: Assignment content is stored only as long as necessary to generate feedback",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "2. Automatic Deletion: After feedback is generated, the content is automatically removed",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "3. Metadata Retention: We keep submission metadata (word count, etc.) for tracking progress",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "4. Student Notification: Students are informed at submission time that their content will be removed",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("Student Rights", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "Students have the following rights regarding their data:",
            cls="mb-4 text-gray-700",
        ),
        Div(
            Div(
                "1. Transparency: Clear information about how their submissions are processed",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "2. Limited Storage: Assurance that the content of their submissions is not permanently stored",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "3. Retention of Own Work: Students are advised to maintain their own copies of submitted work",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("Policy Updates", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "This privacy policy may be updated periodically to reflect changes in our practices. Major changes will be communicated to users.",
            cls="mb-4 text-gray-700",
        ),
        cls="prose max-w-none",
    )

    # Create the main content for the privacy page
    privacy_page_content = Div(
        Div(
            Div(
                Div(privacy_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md",
            ),
            cls="max-w-4xl mx-auto py-12",
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50",
    )

    # Return the complete page with dynamic header based on auth status
    return Div(
        dynamic_header(session),
        privacy_page_content,
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


@rt("/terms")
def terms_page(session=None):
    """Terms of Service page"""
    terms_content = Div(
        H1(
            "FeedForward Terms of Service",
            cls="text-3xl font-bold text-slate-800 mb-6",
        ),
        H2("1. Acceptance of Terms", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "By accessing or using the FeedForward platform, you agree to be bound by these Terms of Service and all applicable laws and regulations. If you do not agree with any of these terms, you are prohibited from using this service.",
            cls="mb-4 text-gray-700",
        ),
        H2("2. Educational Use", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "FeedForward is designed exclusively for educational purposes. The platform should be used by students and educators in accordance with their institution's academic policies.",
            cls="mb-4 text-gray-700",
        ),
        H2("3. User Accounts", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        Div(
            Div(
                "• Users are responsible for maintaining the confidentiality of their account credentials",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• Users agree to accept responsibility for all activities that occur under their account",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• Users must provide accurate information when creating an account",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("4. Content Ownership", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        Div(
            Div(
                "• Users retain ownership of content they submit to the platform",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• Users grant FeedForward a limited license to process their submissions for the purpose of providing feedback",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• As described in our Privacy Policy, submission content is not permanently stored",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("5. Prohibited Use", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P("Users may not use FeedForward to:", cls="mb-4 text-gray-700"),
        Div(
            Div(
                "• Submit content that violates intellectual property rights",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• Attempt to use the platform as a file storage or backup service",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div("• Engage in any illegal activity", cls="ml-6 mb-2 text-gray-700"),
            Div(
                "• Interfere with the proper functioning of the platform",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("6. Service Limitations", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        Div(
            Div(
                "• FeedForward provides automated feedback as an educational tool, not as definitive assessment",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• The accuracy of feedback depends on many factors including the quality of submissions",
                cls="ml-6 mb-2 text-gray-700",
            ),
            Div(
                "• The platform may occasionally experience downtime for maintenance or updates",
                cls="ml-6 mb-2 text-gray-700",
            ),
            cls="mb-6",
        ),
        H2("7. Termination", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "FeedForward reserves the right to terminate or suspend access to the service without prior notice for conduct that violates these Terms of Service.",
            cls="mb-4 text-gray-700",
        ),
        H2(
            "8. Disclaimer of Warranties",
            cls="text-2xl font-bold text-slate-700 mt-8 mb-4",
        ),
        P(
            'The service is provided "as is" without warranties of any kind, either express or implied. FeedForward does not warrant that the service will be uninterrupted or error-free.',
            cls="mb-4 text-gray-700",
        ),
        H2(
            "9. Institutional Relationships",
            cls="text-2xl font-bold text-slate-700 mt-8 mb-4",
        ),
        P(
            "When FeedForward is deployed by an educational institution, users may also be subject to the policies and terms of that institution.",
            cls="mb-4 text-gray-700",
        ),
        H2("10. Changes to Terms", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "FeedForward reserves the right to modify these terms at any time. Users will be notified of significant changes.",
            cls="mb-4 text-gray-700",
        ),
        H2("11. Governing Law", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "These Terms shall be governed by the laws of Australia, without regard to its conflict of law provisions.",
            cls="mb-4 text-gray-700",
        ),
        P("Last updated: March 20, 2025", cls="text-gray-500 italic mt-8"),
        cls="prose max-w-none",
    )

    # Create the main content for the terms page
    terms_page_content = Div(
        Div(
            Div(
                Div(terms_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md",
            ),
            cls="max-w-4xl mx-auto py-12",
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50",
    )

    # Return the complete page with dynamic header based on auth status
    return Div(
        dynamic_header(session),
        terms_page_content,
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


@rt("/contact")
def contact_page(session=None):
    """Contact page with developer information"""
    contact_content = Div(
        H1("Contact Us", cls="text-3xl font-bold text-slate-800 mb-6"),
        H2("Project Lead", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        Div(
            P("Michael Borck", cls="text-xl font-semibold text-blue-700 mb-1"),
            P("Email: michael.borck@curtin.edu.au", cls="text-gray-700 mb-2"),
            P("Business AI Research Group (BARG)", cls="text-gray-700 mb-1"),
            P("Faculty of Business and Law", cls="text-gray-700 mb-1"),
            P("Curtin University", cls="text-gray-700 mb-4"),
            cls="mb-6",
        ),
        H2("Support", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "For questions or technical support with your institution's FeedForward installation, please contact your local administrators.",
            cls="text-gray-700 mb-4",
        ),
        H2("Contribute", cls="text-2xl font-bold text-slate-700 mt-8 mb-4"),
        P(
            "FeedForward is an open-source project. If you're interested in contributing or reporting issues, please visit our GitHub repository.",
            cls="text-gray-700 mb-4",
        ),
        cls="prose max-w-none",
    )

    # Create the main content for the contact page
    contact_page_content = Div(
        Div(
            Div(
                Div(contact_content, cls="prose max-w-none"),
                cls="bg-white p-8 rounded-xl shadow-md",
            ),
            cls="max-w-4xl mx-auto py-12",
        ),
        cls="container mx-auto px-4 py-8 bg-gray-50",
    )

    # Return the complete page with dynamic header based on auth status
    return Div(
        dynamic_header(session),
        contact_page_content,
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


# --- Error Pages ---
@rt("/error/404")
def error_404_page(session=None, message: Optional[str] = None):
    """Custom 404 error page"""
    error_message = (
        message or "The page you are looking for doesn't exist or has been moved."
    )

    # Create error card content
    error_content = Div(
        Div(
            Div(
                Div(
                    # Error code and type
                    Div(
                        Span(
                            "404",
                            cls=f"text-7xl font-bold text-{BRAND_COLORS['primary']} opacity-80",
                        ),
                        Span(
                            "Not Found",
                            cls=f"{TYPOGRAPHY['h3']} text-{BRAND_COLORS['text-secondary']} ml-6",
                        ),
                        cls="flex items-center justify-center mb-8",
                    ),
                    # Error title
                    H1(
                        "Page Not Found",
                        cls=f"{TYPOGRAPHY['h1']} text-{BRAND_COLORS['text-primary']} mb-6 text-center",
                    ),
                    # Error message
                    P(
                        error_message,
                        cls=f"{TYPOGRAPHY['body-lg']} text-{BRAND_COLORS['text-secondary']} mb-6 text-center max-w-md",
                    ),
                    # Action buttons
                    Div(
                        A(
                            "Dashboard",
                            href="/",  # This will redirect to proper dashboard based on role in landing page
                            cls=f"{BUTTON_STYLES['primary']} mr-4",
                        ),
                        A(
                            "Sign Out",
                            href="/logout",
                            cls=BUTTON_STYLES["secondary"],
                        ),
                        cls="flex flex-col sm:flex-row justify-center gap-4",
                    ),
                    cls=f"p-12 bg-white rounded-2xl shadow-2xl border border-{BRAND_COLORS['border']} max-w-lg mx-auto",
                ),
                cls="container mx-auto px-4 py-8",
            ),
            cls="flex-grow bg-gradient-to-b from-gray-50 to-indigo-50 flex items-center",
        )
    )

    return Div(
        dynamic_header(session),
        error_content,
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


@rt("/error/403")
def error_403_page(session=None, message: Optional[str] = None):
    """Custom 403 error page"""
    error_message = message or "You don't have permission to access this page."

    # Create error card content
    error_content = Div(
        Div(
            Div(
                Div(
                    # Error code and type
                    Div(
                        Span(
                            "403",
                            cls=f"text-7xl font-bold text-{BRAND_COLORS['error']} opacity-80",
                        ),
                        Span(
                            "Forbidden",
                            cls=f"{TYPOGRAPHY['h3']} text-{BRAND_COLORS['text-secondary']} ml-6",
                        ),
                        cls="flex items-center justify-center mb-8",
                    ),
                    # Error title
                    H1(
                        "Access Denied",
                        cls=f"{TYPOGRAPHY['h1']} text-{BRAND_COLORS['text-primary']} mb-6 text-center",
                    ),
                    # Error message
                    P(
                        error_message,
                        cls=f"{TYPOGRAPHY['body-lg']} text-{BRAND_COLORS['text-secondary']} mb-6 text-center max-w-md",
                    ),
                    # Action buttons
                    Div(
                        A(
                            "Dashboard",
                            href="/",  # This will redirect to proper dashboard based on role in landing page
                            cls=f"{BUTTON_STYLES['primary']} mr-4",
                        ),
                        A(
                            "Sign Out",
                            href="/logout",
                            cls=BUTTON_STYLES["secondary"],
                        ),
                        cls="flex flex-col sm:flex-row justify-center gap-4",
                    ),
                    cls=f"p-12 bg-white rounded-2xl shadow-2xl border border-{BRAND_COLORS['border']} max-w-lg mx-auto",
                ),
                cls="container mx-auto px-4 py-8",
            ),
            cls="flex-grow bg-gradient-to-b from-gray-50 to-indigo-50 flex items-center",
        )
    )

    return Div(
        dynamic_header(session),
        error_content,
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


# --- Catchall for 404 errors ---
@rt("/{path:path}")
def catch_all_404(path: str, session=None):
    """Catch-all route for 404 errors"""
    # Check if the path exists in the routing table
    # If not, redirect to the 404 error page
    return RedirectResponse("/error/404", status_code=303)


# --- Start the Server ---
if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Create temporary upload directory if it doesn't exist
    os.makedirs("data/uploads", exist_ok=True)

    # Start the server
    serve()
