"""
Legal document routes (Terms of Service, Privacy Policy)
"""

from fasthtml import common as fh

from app import rt
from app.utils.ui import page_container


@rt("/terms-of-service")
def get():
    """Display the Terms of Service"""
    tos_content = fh.Div(
        fh.Container(
            fh.H1("Terms of Service", cls="text-3xl font-bold text-indigo-900 mb-8"),
            fh.Section(
                fh.H2(
                    "1. Introduction", cls="text-2xl font-semibold text-indigo-800 mb-4"
                ),
                fh.P(
                    "Welcome to FeedForward. These Terms of Service govern your use of the FeedForward educational feedback platform. By accessing or using our Service, you agree to be bound by these Terms.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "2. Service Description",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "FeedForward is an educational technology platform that provides AI-powered feedback on student assignments. The Service is designed to support iterative learning and improvement through timely, constructive feedback.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "3. User Accounts",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.H3("Account Types", cls="text-xl font-medium text-indigo-700 mb-2"),
                fh.Ul(
                    fh.Li("Students: Enrolled through instructor invitation", cls="mb-1"),
                    fh.Li(
                        "Instructors: Register with institutional email addresses",
                        cls="mb-1",
                    ),
                    fh.Li("Administrators: Manage system settings and users", cls="mb-1"),
                    cls="list-disc list-inside mb-4 text-gray-700",
                ),
                fh.H3(
                    "Account Responsibilities",
                    cls="text-xl font-medium text-indigo-700 mb-2",
                ),
                fh.Ul(
                    fh.Li(
                        "You are responsible for maintaining the confidentiality of your account credentials",
                        cls="mb-1",
                    ),
                    fh.Li(
                        "You must provide accurate and complete information during registration",
                        cls="mb-1",
                    ),
                    fh.Li(
                        "You are responsible for all activities that occur under your account",
                        cls="mb-1",
                    ),
                    cls="list-disc list-inside mb-6 text-gray-700",
                ),
            ),
            fh.Section(
                fh.H2(
                    "4. Acceptable Use",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "By using FeedForward, you agree to use the Service only for legitimate educational purposes and to respect the privacy and rights of other users. You must comply with all applicable laws and institutional policies.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "5. Content and Privacy",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "Student submissions are temporarily stored only for feedback generation and are automatically removed after feedback is provided. Students retain ownership of their submitted work.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "6. Limitation of Liability",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "To the maximum extent permitted by law, FeedForward shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of the Service.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "7. Changes to Terms",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "We may modify these Terms at any time. Continued use of the Service after changes constitutes acceptance of the modified Terms.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Div(
                fh.P("Last updated: December 2024", cls="text-sm text-gray-500"),
                cls="mt-8 pt-4 border-t border-gray-200",
            ),
            cls="max-w-4xl mx-auto",
        ),
        cls="py-8 px-4 bg-gray-50 min-h-screen",
    )

    return page_container("Terms of Service - FeedForward", tos_content)


@rt("/privacy-policy")
def get():
    """Display the Privacy Policy"""
    privacy_content = fh.Div(
        fh.Container(
            fh.H1("Privacy Policy", cls="text-3xl font-bold text-indigo-900 mb-8"),
            fh.Section(
                fh.H2(
                    "Data Collection and Usage",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.P(
                    "FeedForward is designed with student privacy as a core principle. We collect and process data solely to provide educational feedback services.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2(
                    "Student Information",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.Ul(
                    fh.Li("Basic account information (name, email)", cls="mb-1"),
                    fh.Li("Course enrollment details", cls="mb-1"),
                    fh.Li(
                        "Assignment metadata (submissions, dates, word counts)",
                        cls="mb-1",
                    ),
                    cls="list-disc list-inside mb-6 text-gray-700",
                ),
            ),
            fh.Section(
                fh.H2(
                    "Submission Content",
                    cls="text-2xl font-semibold text-indigo-800 mb-4",
                ),
                fh.Div(
                    fh.P(
                        fh.Strong("Temporary storage only:"),
                        " Student submitted work is stored only temporarily while feedback is being generated",
                        cls="mb-3 text-gray-700",
                    ),
                    fh.P(
                        "Once feedback is provided, the original submission content is ",
                        fh.Strong("automatically removed"),
                        " from our system",
                        cls="mb-3 text-gray-700",
                    ),
                    fh.P(
                        "We retain only metadata such as word count, submission dates, and generated feedback",
                        cls="mb-6 text-gray-700",
                    ),
                    cls="bg-blue-50 p-4 rounded-lg border border-blue-200",
                ),
            ),
            fh.Section(
                fh.H2(
                    "Data Protection Measures",
                    cls="text-2xl font-semibold text-indigo-800 mb-4 mt-6",
                ),
                fh.H3(
                    "Technical Measures", cls="text-xl font-medium text-indigo-700 mb-2"
                ),
                fh.Ul(
                    fh.Li(
                        "Database Security: All data is securely stored using industry-standard practices",
                        cls="mb-1",
                    ),
                    fh.Li(
                        "Secure Processing: Content is securely processed during feedback generation",
                        cls="mb-1",
                    ),
                    fh.Li(
                        "Data Minimization: We collect only what is necessary for educational purposes",
                        cls="mb-1",
                    ),
                    cls="list-disc list-inside mb-6 text-gray-700",
                ),
            ),
            fh.Section(
                fh.H2("Student Rights", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                fh.P(
                    "Students have the right to transparency about how their submissions are processed and assurance that content is not permanently stored. Students are advised to maintain their own copies of submitted work.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Section(
                fh.H2("Policy Updates", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                fh.P(
                    "This privacy policy may be updated periodically. Major changes will be communicated to users.",
                    cls="mb-6 text-gray-700 leading-relaxed",
                ),
            ),
            fh.Div(
                fh.P("Last updated: December 2024", cls="text-sm text-gray-500"),
                cls="mt-8 pt-4 border-t border-gray-200",
            ),
            cls="max-w-4xl mx-auto",
        ),
        cls="py-8 px-4 bg-gray-50 min-h-screen",
    )

    return page_container("Privacy Policy - FeedForward", privacy_content)
