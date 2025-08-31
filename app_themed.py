"""
Example of how to refactor app.py to use the centralized theme.
This shows how the landing page would look with the new theme system.
"""

from fasthtml.common import H1, H2, H3, A, Div, P, Span

from app.utils.theme import (
    COMPONENT_CLASSES,
    THEME,
    badge,
    card,
    get_theme_styles,
    primary_button,
    secondary_button,
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
                        Span("Feed", COMPONENT_CLASSES=f"text-{THEME['colors']['primary']} font-bold"),
                        Span("Forward", COMPONENT_CLASSES=f"text-{THEME['colors']['secondary']} font-bold"),
                        COMPONENT_CLASSES="text-5xl md:text-6xl mb-4",
                    ),
                    H1(
                        "Elevate Your Learning",
                        COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_hero']} bg-gradient-to-r from-{THEME['colors']['primary']} to-{THEME['colors']['secondary']} bg-clip-text text-transparent mb-6",
                    ),
                    P(
                        "Transforming feedback into a path to success.",
                        COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_body_lg']} mb-10 max-w-2xl mx-auto",
                    ),
                    Div(
                        # Using component builders instead of raw classes
                        A(
                            primary_button("Sign up"),
                            href="/register",
                            COMPONENT_CLASSES="mr-6"
                        ),
                        A(
                            secondary_button("Learn More"),
                            href="#features"
                        ),
                        COMPONENT_CLASSES="flex flex-col sm:flex-row items-center justify-center gap-4",
                    ),
                    COMPONENT_CLASSES="max-w-2xl mx-auto text-center",
                ),
                # Abstract background shapes
                Div(
                    Div(COMPONENT_CLASSES="absolute top-20 right-20 w-20 h-20 rounded-full bg-blue-200 opacity-40"),
                    Div(COMPONENT_CLASSES="absolute bottom-10 left-20 w-32 h-32 rounded-full bg-teal-200 opacity-40"),
                    Div(COMPONENT_CLASSES="absolute top-40 left-40 w-16 h-16 rounded-full bg-cyan-200 opacity-30"),
                    COMPONENT_CLASSES="absolute inset-0 overflow-hidden pointer-events-none",
                ),
                COMPONENT_CLASSES=f"{COMPONENT_CLASSES['section_gradient']} p-16 rounded-xl shadow-lg relative",
            ),
            COMPONENT_CLASSES="container mx-auto px-4 py-20 flex justify-center",
        ),

        # Features Section
        Div(
            Div(
                H2(
                    "How FeedForward Works",
                    COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_h1']} text-center mb-6",
                ),
                P(
                    "Our platform makes iterative learning simple and effective.",
                    COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_body_lg']} text-center mb-16 max-w-3xl mx-auto",
                ),
                Div(
                    # Feature cards using card component
                    card(
                        H3("Submit Your Work", COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_h3']} text-center mb-4"),
                        Div(
                            P("• Upload assignments effortlessly", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Support for multiple file formats", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Simple drag-and-drop interface", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            COMPONENT_CLASSES="text-left space-y-2",
                        ),
                        badge("Step 1", type='primary'),
                        COMPONENT_CLASSES="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    card(
                        H3("Receive Smart Feedback", COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_h3']} text-center mb-4"),
                        Div(
                            P("• Detailed, constructive feedback", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Tailored to assignment criteria", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Clear action items for improvement", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            COMPONENT_CLASSES="text-left space-y-2",
                        ),
                        badge("Step 2", type='secondary'),
                        COMPONENT_CLASSES="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    card(
                        H3("Iterative Improvement", COMPONENT_CLASSES=f"{COMPONENT_CLASSES['text_h3']} text-center mb-4"),
                        Div(
                            P("• Track progress across drafts", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Visualize your improvement", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            P("• Build on feedback systematically", COMPONENT_CLASSES=COMPONENT_CLASSES['text_body']),
                            COMPONENT_CLASSES="text-left space-y-2",
                        ),
                        badge("Step 3", type='primary'),
                        COMPONENT_CLASSES="hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2"
                    ),
                    COMPONENT_CLASSES="grid md:grid-cols-3 gap-8",
                ),
                COMPONENT_CLASSES="container mx-auto px-4 py-20",
            ),
            id="features",
            COMPONENT_CLASSES=COMPONENT_CLASSES['section_light'],
        ),
    )

    # Return the complete page with theme styles included
    return Div(
        get_theme_styles(),  # Include CSS variables
        dynamic_header(session),
        Div(landing_content, COMPONENT_CLASSES="flex-grow"),
        page_footer(),
        COMPONENT_CLASSES="min-h-screen flex flex-col",
    )

# Benefits of this approach:
# 1. No more hardcoded colors scattered throughout
# 2. Single source of truth in theme.py
# 3. Easy to change entire color scheme
# 4. Consistent styling across components
# 5. Reusable component builders
# 6. CSS variables for runtime theming
