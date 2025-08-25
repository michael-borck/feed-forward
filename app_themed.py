"""
Example of how to refactor app.py to use the centralized theme.
This shows how the landing page would look with the new theme system.
"""

from fasthtml.common import (
    Div, H1, H2, H3, P, A, Span, Script, serve
)
from app.utils.theme import (
    THEME,
    COMPONENT_CLASSES as cls,
    PrimaryButton,
    SecondaryButton,
    Card,
    Alert,
    Badge,
    get_theme_styles
)
from app.utils.ui import dynamic_header, page_footer

# No more inline color definitions!
# Everything comes from the theme

def landing_page_themed(session=None):
    """Landing page using centralized theme."""
    
    landing_content = Div(
        # Hero Section
        Div(
            Div(
                Div(
                    # Logo using theme colors
                    Div(
                        Span("Feed", cls=f"text-{THEME['colors']['primary']} font-bold"),
                        Span("Forward", cls=f"text-{THEME['colors']['secondary']} font-bold"),
                        cls="text-5xl md:text-6xl mb-4",
                    ),
                    H1(
                        "Elevate Your Learning",
                        cls=f"{cls['text_hero']} bg-gradient-to-r from-{THEME['colors']['primary']} to-{THEME['colors']['secondary']} bg-clip-text text-transparent mb-6",
                    ),
                    P(
                        "Transforming feedback into a path to success.",
                        cls=f"{cls['text_body_lg']} mb-10 max-w-2xl mx-auto",
                    ),
                    Div(
                        # Using component builders instead of raw classes
                        A(
                            PrimaryButton("Sign up"),
                            href="/register",
                            cls="mr-6"
                        ),
                        A(
                            SecondaryButton("Learn More"),
                            href="#features"
                        ),
                        cls="flex flex-col sm:flex-row items-center justify-center gap-4",
                    ),
                    cls="max-w-2xl mx-auto text-center",
                ),
                # Abstract background shapes
                Div(
                    Div(cls="absolute top-20 right-20 w-20 h-20 rounded-full bg-blue-200 opacity-40"),
                    Div(cls="absolute bottom-10 left-20 w-32 h-32 rounded-full bg-teal-200 opacity-40"),
                    Div(cls="absolute top-40 left-40 w-16 h-16 rounded-full bg-cyan-200 opacity-30"),
                    cls="absolute inset-0 overflow-hidden pointer-events-none",
                ),
                cls=f"{cls['section_gradient']} p-16 rounded-xl shadow-lg relative",
            ),
            cls="container mx-auto px-4 py-20 flex justify-center",
        ),
        
        # Features Section
        Div(
            Div(
                H2(
                    "How FeedForward Works",
                    cls=f"{cls['text_h1']} text-center mb-6",
                ),
                P(
                    "Our platform makes iterative learning simple and effective.",
                    cls=f"{cls['text_body_lg']} text-center mb-16 max-w-3xl mx-auto",
                ),
                Div(
                    # Feature cards using Card component
                    Card(
                        H3("Submit Your Work", cls=f"{cls['text_h3']} text-center mb-4"),
                        Div(
                            P("• Upload assignments effortlessly", cls=cls['text_body']),
                            P("• Support for multiple file formats", cls=cls['text_body']),
                            P("• Simple drag-and-drop interface", cls=cls['text_body']),
                            cls="text-left space-y-2",
                        ),
                        Badge("Step 1", type='primary'),
                        cls="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    Card(
                        H3("Receive Smart Feedback", cls=f"{cls['text_h3']} text-center mb-4"),
                        Div(
                            P("• Detailed, constructive feedback", cls=cls['text_body']),
                            P("• Tailored to assignment criteria", cls=cls['text_body']),
                            P("• Clear action items for improvement", cls=cls['text_body']),
                            cls="text-left space-y-2",
                        ),
                        Badge("Step 2", type='secondary'),
                        cls="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    Card(
                        H3("Iterative Improvement", cls=f"{cls['text_h3']} text-center mb-4"),
                        Div(
                            P("• Track progress across drafts", cls=cls['text_body']),
                            P("• Visualize your improvement", cls=cls['text_body']),
                            P("• Build on feedback systematically", cls=cls['text_body']),
                            cls="text-left space-y-2",
                        ),
                        Badge("Step 3", type='primary'),
                        cls="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    cls="grid md:grid-cols-3 gap-8",
                ),
                cls="container mx-auto px-4 py-20",
            ),
            id="features",
            cls=cls['section_light'],
        ),
    )
    
    # Return the complete page with theme styles included
    return Div(
        get_theme_styles(),  # Include CSS variables
        dynamic_header(session),
        Div(landing_content, cls="flex-grow"),
        page_footer(),
        cls="min-h-screen flex flex-col",
    )

# Benefits of this approach:
# 1. No more hardcoded colors scattered throughout
# 2. Single source of truth in theme.py
# 3. Easy to change entire color scheme
# 4. Consistent styling across components
# 5. Reusable component builders
# 6. CSS variables for runtime theming