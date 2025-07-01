"""
Legal document routes (Terms of Service, Privacy Policy)
"""
from fasthtml.common import *

from app import rt
from app.utils.ui import page_container


@rt('/terms-of-service')
def get():
    """Display the Terms of Service"""
    tos_content = Div(
        Container(
            H1("Terms of Service", cls="text-3xl font-bold text-indigo-900 mb-8"),

            Section(
                H2("1. Introduction", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("Welcome to FeedForward. These Terms of Service govern your use of the FeedForward educational feedback platform. By accessing or using our Service, you agree to be bound by these Terms.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("2. Service Description", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("FeedForward is an educational technology platform that provides AI-powered feedback on student assignments. The Service is designed to support iterative learning and improvement through timely, constructive feedback.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("3. User Accounts", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                H3("Account Types", cls="text-xl font-medium text-indigo-700 mb-2"),
                Ul(
                    Li("Students: Enrolled through instructor invitation", cls="mb-1"),
                    Li("Instructors: Register with institutional email addresses", cls="mb-1"),
                    Li("Administrators: Manage system settings and users", cls="mb-1"),
                    cls="list-disc list-inside mb-4 text-gray-700"
                ),
                H3("Account Responsibilities", cls="text-xl font-medium text-indigo-700 mb-2"),
                Ul(
                    Li("You are responsible for maintaining the confidentiality of your account credentials", cls="mb-1"),
                    Li("You must provide accurate and complete information during registration", cls="mb-1"),
                    Li("You are responsible for all activities that occur under your account", cls="mb-1"),
                    cls="list-disc list-inside mb-6 text-gray-700"
                ),
            ),

            Section(
                H2("4. Acceptable Use", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("By using FeedForward, you agree to use the Service only for legitimate educational purposes and to respect the privacy and rights of other users. You must comply with all applicable laws and institutional policies.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("5. Content and Privacy", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("Student submissions are temporarily stored only for feedback generation and are automatically removed after feedback is provided. Students retain ownership of their submitted work.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("6. Limitation of Liability", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("To the maximum extent permitted by law, FeedForward shall not be liable for any indirect, incidental, special, consequential, or punitive damages resulting from your use of the Service.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("7. Changes to Terms", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("We may modify these Terms at any time. Continued use of the Service after changes constitutes acceptance of the modified Terms.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Div(
                P("Last updated: December 2024", cls="text-sm text-gray-500"),
                cls="mt-8 pt-4 border-t border-gray-200"
            ),

            cls="max-w-4xl mx-auto"
        ),
        cls="py-8 px-4 bg-gray-50 min-h-screen"
    )

    return page_container("Terms of Service - FeedForward", tos_content)

@rt('/privacy-policy')
def get():
    """Display the Privacy Policy"""
    privacy_content = Div(
        Container(
            H1("Privacy Policy", cls="text-3xl font-bold text-indigo-900 mb-8"),

            Section(
                H2("Data Collection and Usage", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("FeedForward is designed with student privacy as a core principle. We collect and process data solely to provide educational feedback services.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("Student Information", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                Ul(
                    Li("Basic account information (name, email)", cls="mb-1"),
                    Li("Course enrollment details", cls="mb-1"),
                    Li("Assignment metadata (submissions, dates, word counts)", cls="mb-1"),
                    cls="list-disc list-inside mb-6 text-gray-700"
                ),
            ),

            Section(
                H2("Submission Content", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                Div(
                    P(Strong("Temporary storage only:"), " Student submitted work is stored only temporarily while feedback is being generated",
                      cls="mb-3 text-gray-700"),
                    P("Once feedback is provided, the original submission content is ", Strong("automatically removed"), " from our system",
                      cls="mb-3 text-gray-700"),
                    P("We retain only metadata such as word count, submission dates, and generated feedback",
                      cls="mb-6 text-gray-700"),
                    cls="bg-blue-50 p-4 rounded-lg border border-blue-200"
                ),
            ),

            Section(
                H2("Data Protection Measures", cls="text-2xl font-semibold text-indigo-800 mb-4 mt-6"),
                H3("Technical Measures", cls="text-xl font-medium text-indigo-700 mb-2"),
                Ul(
                    Li("Database Security: All data is securely stored using industry-standard practices", cls="mb-1"),
                    Li("Secure Processing: Content is securely processed during feedback generation", cls="mb-1"),
                    Li("Data Minimization: We collect only what is necessary for educational purposes", cls="mb-1"),
                    cls="list-disc list-inside mb-6 text-gray-700"
                ),
            ),

            Section(
                H2("Student Rights", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("Students have the right to transparency about how their submissions are processed and assurance that content is not permanently stored. Students are advised to maintain their own copies of submitted work.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Section(
                H2("Policy Updates", cls="text-2xl font-semibold text-indigo-800 mb-4"),
                P("This privacy policy may be updated periodically. Major changes will be communicated to users.",
                  cls="mb-6 text-gray-700 leading-relaxed"),
            ),

            Div(
                P("Last updated: December 2024", cls="text-sm text-gray-500"),
                cls="mt-8 pt-4 border-t border-gray-200"
            ),

            cls="max-w-4xl mx-auto"
        ),
        cls="py-8 px-4 bg-gray-50 min-h-screen"
    )

    return page_container("Privacy Policy - FeedForward", privacy_content)
