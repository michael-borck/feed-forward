"""
Example of how to use the centralized theme system.
This shows the before/after comparison.
"""

from fasthtml import common as fh

from app.utils.theme import COMPONENT_CLASSES as CLS
from app.utils.theme import (
    alert,
    badge,
    card,
    form_input,
    get_theme_styles,
    primary_button,
    secondary_button,
)


# ============= BEFORE (Current approach) =============
def old_approach():
    """Current approach with hardcoded Tailwind classes everywhere."""
    return fh.Div(
        # Hardcoded button with inline classes
        fh.Button(
            "Sign up",
            cls="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
        ),

        # Hardcoded card
        fh.Div(
            fh.H3("Title", cls="text-lg font-bold text-slate-800"),
            fh.P("Content", cls="text-gray-600"),
            cls="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow border border-gray-100"
        ),

        # Hardcoded alert
        fh.Div(
            "Success message",
            cls="bg-green-100 text-green-700 p-3 rounded-lg"
        ),

        # Hardcoded form input
        fh.Div(
            fh.Label("Email", cls="block text-sm font-medium text-gray-700 mb-1"),
            fh.Input(
                type="email",
                cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            ),
            cls="mb-4"
        )
    )

# ============= AFTER (Centralized theme approach) =============
def new_approach():
    """New approach using centralized theme."""
    return fh.Div(
        # Option 1: Use component builders
        primary_button("Sign up"),

        # Option 2: Use themed classes from dictionary
        fh.Button("Learn More", cls=CLS['btn_secondary']),

        # Use card component
        card(
            "Title",
            fh.P("Content", cls=CLS['text_body'])
        ),

        # Use alert component
        alert("Success message", type='success'),

        # Use badge component
        badge("New", type='primary'),

        # Use form_input component
        form_input(
            name="email",
            label="Email Address",
            type="email",
            required=True,
            placeholder="you@example.com"
        ),

        # Include theme styles in the page
        get_theme_styles()
    )

# ============= Page Layout Example =============
def themed_page():
    """Example of a full page using the theme system."""
    return fh.Html(
        fh.Head(
            fh.Title("FeedForward"),
            get_theme_styles(),  # Include CSS variables
        ),
        fh.Body(
            # Header using theme classes
            fh.Header(
                fh.Div(
                    fh.Span("FeedForward", cls=CLS['text_h1']),
                    fh.Nav(
                        fh.A("Home", href="/", cls=CLS['nav_link']),
                        fh.A("About", href="/about", cls=CLS['nav_link_active']),
                    ),
                    cls="container mx-auto flex justify-between items-center px-4"
                ),
                cls=CLS['header_main']
            ),

            # Main content
            fh.Main(
                fh.Section(
                    fh.Div(
                        fh.H1("Welcome", cls=CLS['text_hero']),
                        fh.P("Description", cls=CLS['text_body_lg']),
                        fh.Div(
                            primary_button("Get Started"),
                            secondary_button("Learn More"),
                            cls="flex gap-4 mt-4"
                        ),
                        cls="container mx-auto px-4 py-12"
                    ),
                    cls=CLS['section_gradient']
                ),

                fh.Section(
                    fh.Div(
                        card(
                            "Feature 1",
                            fh.P("Feature description", cls=CLS['text_body']),
                            badge("New", type='success')
                        ),
                        cls="container mx-auto px-4 py-8"
                    ),
                    cls=CLS['section_white']
                )
            ),

            # Footer
            fh.Footer(
                fh.Div(
                    fh.P("© 2025 FeedForward", cls=CLS['text_muted']),
                    cls="container mx-auto px-4 py-8"
                ),
                cls=CLS['footer_main']
            )
        )
    )

# ============= Benefits of this approach =============
"""
1. SINGLE SOURCE OF TRUTH: Colors and styles defined in one place
2. CONSISTENCY: Use predefined component classes
3. MAINTAINABILITY: Change colors in one place, affects entire app
4. TYPE SAFETY: IDE can autocomplete from COMPONENT_CLASSES dictionary
5. FLEXIBILITY: Can still override with additional classes when needed
6. CSS VARIABLES: Can change theme dynamically at runtime
7. DARK MODE READY: Easy to add dark mode support with CSS variables

Limitations with Tailwind:
- Can't use dynamic class construction like f"bg-{color}-600"
- Tailwind only includes classes it finds in source at build time
- Must use complete class names that exist in the source

Solutions:
1. Use predefined complete class names (what we're doing)
2. Use CSS variables for truly dynamic colors
3. Use inline styles for dynamic values
4. Include all possible classes in a safelist
"""
