"""
UI Components for the FeedForward application

This module contains reusable UI components like headers, footers, and navigation elements
that are shared across multiple pages in the application.
"""

from fasthtml import common as fh

from app.models.user import Role
from app.utils.design import (
    BODY_VPAD,
    COLOR,
    DASHBOARD_BODY_PAD,
    GAP,
    RADIUS,
    RULE_HEAVY,
    TEXT,
    button_classes,
)


def brand_wordmark(size_cls="text-2xl"):
    """The two-tone serif wordmark — "Feed" in ink navy, "Forward" in teal."""
    return fh.Div(
        fh.Span("Feed", cls=f"font-serif font-bold text-{COLOR['wordmark_first']}"),
        fh.Span("Forward", cls=f"font-serif font-bold text-{COLOR['wordmark_second']}"),
        cls=f"flex items-center {size_cls}",
    )


def page_header(show_auth_buttons=True):
    """
    Return a consistent header component for all pages

    Args:
        show_auth_buttons: Whether to show sign in/sign up buttons in the header
    """
    nav_buttons = (
        fh.Nav(
            fh.A(
                "Sign in",
                href="/login",
                cls=(
                    f"{TEXT['label']} text-{COLOR['text_body']} mr-6 "
                    "hover:underline underline-offset-4"
                ),
            ),
            fh.A("Sign up", href="/register", cls=button_classes("secondary", "md")),
            cls="flex items-center",
        )
        if show_auth_buttons
        else ""
    )

    return fh.Header(
        fh.Div(
            # Left side - Logo and name
            fh.A(
                brand_wordmark(),
                href="/landing",
                cls="flex items-center hover:opacity-90 transition-opacity",
            ),
            # Right side - optional buttons
            nav_buttons,
            cls="container mx-auto flex justify-between items-center px-4",
        ),
        cls=f"bg-{COLOR['surface_alt']} {RULE_HEAVY} py-4",
    )


def page_footer():
    """One-line footer — FeedForward is an internal tool, not a marketing site."""
    from datetime import datetime

    link_cls = (
        f"{TEXT['label']} text-{COLOR['text_muted']} hover:text-{COLOR['primary']}"
    )
    return fh.Footer(
        fh.Div(
            fh.Div(
                fh.Span(
                    "Feed",
                    cls=f"font-serif font-semibold text-{COLOR['wordmark_first']}",
                ),
                fh.Span(
                    "Forward",
                    cls=f"font-serif font-semibold text-{COLOR['wordmark_second']}",
                ),
                fh.Span(
                    f" · © {datetime.now().year} Curtin University",
                    cls="text-slate-500",
                ),
                cls="text-sm",
            ),
            fh.Div(
                fh.A("Privacy", href="/privacy", cls=link_cls),
                fh.A("Terms", href="/terms", cls=link_cls),
                fh.A("Docs", href="/docs", cls=link_cls),
                cls=f"flex gap-{GAP['lg']} items-center",
            ),
            cls=(
                "container mx-auto px-4 py-4 flex flex-col sm:flex-row "
                "items-center justify-between gap-2"
            ),
        ),
        cls=f"bg-{COLOR['surface_alt']} border-t border-{COLOR['border']}",
    )


def page_container(title, content):
    """
    Create a full page with consistent header, footer and styling

    Args:
        title: Page title (for browser tab) - currently not used due to FastHTML limitations
        content: The main content of the page
    """
    # Note: We're not using fh.Titled here as it renders the title as visible text
    # FastHTML handles page titles differently - typically through the app's route decorators
    return fh.Div(
        page_header(),
        fh.Div(
            content,
            cls=f"container mx-auto px-4 {BODY_VPAD} flex justify-center flex-grow",
        ),
        page_footer(),
        cls=f"min-h-screen flex flex-col bg-{COLOR['surface_alt']}",
    )


def dashboard_header(user_role, current_path=None, user=None):
    """
    Return a dashboard header with role-specific navigation

    Args:
        user_role: Role of the current user (student, instructor, admin)
        current_path: Current request path to determine active link
        user: Optional user object — used for the avatar initial
    """
    # Portal name based on role
    portal_name = ""
    nav_links = []

    brand_logo = brand_wordmark()

    if user_role == Role.STUDENT:
        portal_name = "Student Portal"
        nav_links = [
            ("Dashboard", "/student/dashboard", False),
            ("My Submissions", "/student/assignments", False),
            ("Feedback History", "/student/feedback", False),
            ("Profile", "/profile", False),
            ("Help", "/docs", False),
        ]
    elif user_role == Role.INSTRUCTOR:
        portal_name = "Instructor Portal"
        nav_links = [
            ("Dashboard", "/instructor/dashboard", False),
            ("Courses", "/instructor/courses", False),
            ("Students", "/instructor/manage-students", False),
            ("Invite", "/instructor/invite-students", False),
            ("Profile", "/profile", False),
        ]
    elif user_role == Role.ADMIN:
        portal_name = "Admin Portal"
        nav_links = [
            ("Users", "#", False),
            ("Courses", "#", False),
            ("Settings", "#", False),
            ("System", "#", False),
            ("Profile", "/profile", False),
        ]

    # Build navigation links with active state based on current path
    nav_items = []
    for label, href, _ in nav_links:
        # Mark as active if href matches current path
        is_active = False
        if current_path:
            if href == current_path:
                is_active = True
            # Special case for dashboard vs courses (we want the proper one highlighted)
            if label == "Courses" and current_path.startswith("/instructor/courses"):
                is_active = True
            if label == "Dashboard" and current_path == "/instructor/dashboard":
                is_active = True
            if label == "Students" and current_path == "/instructor/manage-students":
                is_active = True
            if label == "Invite" and current_path == "/instructor/invite-students":
                is_active = True

        cls = (
            f"{TEXT['label']} text-{COLOR['text_body']} px-3 py-2 mx-1 "
            f"border-b-2 border-transparent hover:text-{COLOR['primary']} "
            "transition-colors"
        )
        if is_active:
            cls = (
                f"{TEXT['label']} text-{COLOR['primary']} px-3 py-2 mx-1 "
                f"border-b-2 border-{COLOR['primary']} font-semibold"
            )
        nav_items.append(fh.A(label, href=href, cls=cls))

    # Avatar initial: user's email first letter, falling back to the role's
    user_initial = "U"
    if user is not None and getattr(user, "email", ""):
        user_initial = user.email[0].upper()
    elif isinstance(user_role, Role):
        user_initial = user_role.name[0]

    user_menu = fh.Div(
        fh.Div(
            fh.A(
                fh.Div(
                    user_initial,  # First letter as fallback
                    cls=(
                        f"w-8 h-8 rounded-full bg-{COLOR['accent']} text-white "
                        "flex items-center justify-center font-semibold"
                    ),
                ),
                href="/profile",
                title="Profile",
                cls="hover:opacity-80 transition-opacity",
            ),
            fh.Div(
                fh.Button(
                    "Logout",
                    hx_post="/logout",
                    cls=(
                        f"{TEXT['label']} text-{COLOR['text_muted']} ml-4 "
                        f"hover:text-{COLOR['primary']} transition-colors"
                    ),
                ),
                cls="flex items-center",
            ),
            cls="flex items-center",
        ),
        cls="ml-6",
    )

    return fh.Header(
        fh.Div(
            fh.Div(
                fh.A(
                    brand_logo,
                    href="/landing",
                    cls="flex items-center hover:opacity-90 transition-opacity mr-4",
                ),
                fh.Span(
                    portal_name,
                    cls=f"{TEXT['label']} text-{COLOR['text_muted']} mt-1",
                )
                if portal_name
                else "",
                cls="flex items-center",
            ),
            fh.Div(
                fh.Nav(*nav_items, cls="hidden md:flex items-center"),
                user_menu,
                cls="flex items-center",
            ),
            cls="container mx-auto flex justify-between items-center px-4",
        ),
        # Mobile navigation (hamburger menu would be implemented with JavaScript)
        fh.Div(
            fh.Div(
                *[
                    fh.A(
                        label,
                        href=href,
                        cls=f"block py-2 px-4 hover:bg-{COLOR['primary_subtle']}",
                    )
                    for label, href, _ in nav_links
                ],
                cls="hidden py-2",  # Hidden by default, would be shown/hidden with JS
            ),
            cls="md:hidden container mx-auto px-4",
        ),
        cls=f"bg-{COLOR['surface_alt']} {RULE_HEAVY} py-4",
    )


def dashboard_layout(
    title, sidebar, main_content, user_role=Role.STUDENT, user=None, current_path=None
):
    """
    Create a dashboard layout with header, sidebar, main content, and footer

    Args:
        title: Page title - currently not used due to FastHTML limitations
        sidebar: Sidebar content component
        main_content: Main content area component
        user_role: Role of the current user
        user: Optional user object (if available)
        current_path: Current request path to determine active navigation links
    """
    # Note: We're not using fh.Titled here as it renders the title as visible text
    return fh.Div(
        dashboard_header(user_role, current_path, user=user),
        fh.Div(
            fh.Div(
                fh.Div(sidebar, cls="w-full md:w-1/4 mb-4 md:mb-0"),
                fh.Div(main_content, cls="w-full md:w-3/4"),
                cls=f"flex flex-col md:flex-row gap-{GAP['lg']}",
            ),
            cls=f"container mx-auto {DASHBOARD_BODY_PAD}",
        ),
        page_footer(),
        cls=f"min-h-screen flex flex-col bg-{COLOR['surface_alt']}",
    )


def card(content, title=None, padding=4, bg_color=None):
    """
    Create a standard card component with consistent styling.

    Editorial: depth comes from a hairline border on the warm card surface —
    no shadows. Callers that need a roomier card can pass ``padding=6``.

    Args:
        content: Content to display inside the card
        title: Optional card title (serif, over a hairline rule)
        padding: Padding size (default: 4)
        bg_color: Background color class (default: the token card surface)
    """
    bg_color = bg_color or f"bg-{COLOR['surface']}"
    card_content = []
    if title:
        card_content.append(
            fh.Div(
                fh.H3(title, cls=f"{TEXT['h3']} text-{COLOR['text_strong']}"),
                cls=f"mb-3 pb-2 border-b border-{COLOR['border']}",
            )
        )
    card_content.append(content)

    return fh.Div(
        *card_content,
        cls=f"{bg_color} p-{padding} {RADIUS} border border-{COLOR['border']}",
    )


def tabs(items, active_index=0):
    """
    Create a tabbed interface

    Args:
        items: List of (label, href) tuples
        active_index: Index of the active tab
    """
    tab_items = []
    for i, (label, href) in enumerate(items):
        if i == active_index:
            cls = (
                f"flex-1 py-3 px-4 text-center {TEXT['label']} font-semibold "
                f"text-{COLOR['primary']} border-b-2 border-{COLOR['primary']}"
            )
        else:
            cls = (
                f"flex-1 py-3 px-4 text-center {TEXT['label']} "
                f"text-{COLOR['text_muted']} border-b border-{COLOR['border']} "
                f"hover:text-{COLOR['primary']} transition-colors"
            )
        tab_items.append(fh.A(label, href=href, cls=cls))

    return fh.Div(*tab_items, cls=f"bg-{COLOR['surface_alt']} mb-6 flex")


def status_badge(text, color):
    """
    Create a status badge

    Args:
        text: Badge text
        color: Color name (indigo, teal, yellow, red)
    """
    color_map = {
        "blue": "slate",
        "indigo": "slate",
        "purple": "slate",
        "green": "teal",
        "yellow": "amber",
        "red": "red",
        "gray": "slate",
    }

    # Use mapped color or original if not in map
    mapped_color = color_map.get(color, color)

    return fh.Span(
        fh.Span("●", cls=f"text-[8px] mr-1.5 text-{mapped_color}-600"),
        text,
        cls=(
            f"inline-flex items-center bg-{mapped_color}-50 "
            f"text-{mapped_color}-800 border border-{mapped_color}-200 "
            "px-3 py-1 rounded-full text-[11px] font-semibold uppercase "
            "tracking-[0.1em]"
        ),
    )


def data_table(headers, rows):
    """
    Create a data table

    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of cell contents)
    """
    # Create table headers — small-caps over the heavy ink rule
    header_cells = [
        fh.Th(
            h,
            cls=(
                f"text-left py-3 px-6 {TEXT['label']} font-semibold "
                f"text-{COLOR['text_muted']} {RULE_HEAVY}"
            ),
        )
        for h in headers
    ]
    header_row = fh.Tr(*header_cells)

    # Create table rows — hairline dividers
    table_rows = [header_row]
    for i, row_data in enumerate(rows):
        cells = [fh.Td(cell, cls="py-4 px-6") for cell in row_data]
        row_cls = (
            f"border-b border-{COLOR['border']} "
            f"hover:bg-{COLOR['primary_subtle']} transition-colors"
            if i < len(rows) - 1
            else f"hover:bg-{COLOR['primary_subtle']} transition-colors"
        )
        table_rows.append(fh.Tr(*cells, cls=row_cls))

    return fh.Div(
        fh.Table(fh.Thead(header_row), fh.Tbody(*table_rows[1:]), cls="w-full"),
        cls=f"overflow-x-auto bg-{COLOR['surface']} {RADIUS} "
        f"border border-{COLOR['border']}",
    )


def summary_card(content, bg_color="indigo"):
    """
    Create a summary card with colored background

    Args:
        content: Content to display inside the card
        bg_color: Background color (indigo, teal, yellow, red)
    """
    color_map = {
        "blue": "slate",
        "indigo": "slate",
        "purple": "slate",
        "green": "teal",
        "yellow": "amber",
        "red": "red",
    }

    # Use mapped color or original if not in map
    mapped_color = color_map.get(bg_color, bg_color)

    return fh.Div(
        content,
        cls=(
            f"bg-{mapped_color}-50 p-6 {RADIUS} mt-6 "
            f"border-l-2 border-{mapped_color}-600"
        ),
    )


def feedback_card(title, content, color="teal"):
    """
    Create a feedback card with colored indicator bar

    Args:
        title: Card title
        content: Card content
        color: Indicator color (teal, red, indigo, yellow)
    """
    color_map = {
        "blue": "slate",
        "indigo": "slate",
        "purple": "slate",
        "green": "teal",
        "yellow": "amber",
        "red": "red",
    }

    # Use mapped color or original if not in map
    mapped_color = color_map.get(color, color)

    return fh.Div(
        fh.Div(
            fh.Div(cls=f"w-0.5 bg-{mapped_color}-600"),
            fh.Div(
                fh.H4(
                    title,
                    cls=f"font-serif font-semibold text-{COLOR['text_strong']} mb-3",
                ),
                content,
                cls="p-5 flex-1",
            ),
            cls="flex",
        ),
        cls=(
            f"border border-{COLOR['border']} {RADIUS} mb-4 overflow-hidden "
            f"bg-{COLOR['surface']}"
        ),
    )


def action_button(
    text, color="indigo", href="#", icon=None, size="medium", disabled=False
):
    """
    Create an action button

    Args:
        text: Button text
        color: Button color (indigo, teal, red, yellow)
        href: Button link
        icon: Optional icon (e.g., +, ↑, ✓)
        size: Button size (small, medium, large)
        disabled: Whether the button is disabled
    """
    # Legacy colour names map onto the editorial button intents: everything
    # converges on ink-navy primary except destructive (red) actions.
    intent_map = {
        "red": "danger",
        "yellow": "secondary",
        "gray": "secondary",
    }
    intent = intent_map.get(color, "primary")

    size_map = {"small": "sm", "medium": "md", "large": "lg"}
    size_key = size_map.get(size, "md")

    button_content = []
    if icon:
        button_content.append(fh.Span(icon, cls="mr-2"))
    button_content.append(text)

    # Add disabled styling if needed
    if disabled:
        return fh.Span(
            *button_content,
            cls=(
                f"bg-{COLOR['primary_subtle']} text-{COLOR['text_muted']} "
                f"cursor-not-allowed {RADIUS} px-5 py-2.5 text-xs uppercase "
                "tracking-[0.15em] inline-flex items-center justify-center "
                "font-medium"
            ),
        )
    else:
        return fh.A(
            *button_content,
            href=href,
            cls=button_classes(intent, size_key),
        )


def modal_dialog(title, content, footer=None):
    """
    Create a modal dialog component

    Args:
        title: Dialog title
        content: Dialog content
        footer: Optional dialog footer with action buttons
    """
    return fh.Div(
        fh.Div(
            fh.Div(
                fh.H3(title, cls=f"{TEXT['h2']} text-{COLOR['text_strong']}"),
                fh.Button(
                    "x",
                    cls=f"text-{COLOR['text_muted']} hover:text-{COLOR['primary']} "
                    "text-2xl font-bold",
                ),
                cls=f"flex justify-between items-center {RULE_HEAVY} pb-4 mb-6",
            ),
            fh.Div(content, cls="mb-6"),
            fh.Div(footer if footer else "", cls="flex justify-end space-x-4"),
            cls=(
                f"bg-{COLOR['surface']} p-8 {RADIUS} max-w-2xl w-full "
                f"border border-{COLOR['border']}"
            ),
        ),
        cls="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm",
    )


def sidebar_navigation(items, active_index=0):
    """
    Create a sidebar navigation component

    Args:
        items: List of (label, href) tuples
        active_index: Index of the active item
    """
    nav_items = []
    for i, (label, href) in enumerate(items):
        if i == active_index:
            cls = (
                f"p-3 mb-2 border-l-2 border-{COLOR['primary']} "
                f"bg-{COLOR['primary_subtle']} text-{COLOR['primary']} "
                "font-medium flex items-center"
            )
        else:
            cls = (
                f"p-3 mb-2 border-l-2 border-transparent "
                f"hover:bg-{COLOR['primary_subtle']} text-{COLOR['text_body']} "
                "transition-all flex items-center"
            )
        nav_items.append(fh.A(label, href=href, cls=cls))

    return fh.Div(
        *nav_items,
        cls=f"bg-{COLOR['surface']} p-4 {RADIUS} border border-{COLOR['border']}",
    )


def dynamic_header(session=None):
    """
    Return a dynamic header based on user authentication status

    Args:
        session: Current session object to check auth status
    """
    brand_logo = brand_wordmark()

    signin_link_cls = (
        f"{TEXT['label']} text-{COLOR['text_body']} mr-6 "
        "hover:underline underline-offset-4"
    )

    # Right nav content based on auth status
    nav_buttons = ""

    # Check if user is authenticated
    if session and "auth" in session:
        try:
            from app.models.user import Role, users

            user = users[session["auth"]]

            # Determine dashboard link based on role
            dashboard_link = "/"
            if user.role == Role.ADMIN:
                dashboard_link = "/admin/dashboard"
            elif user.role == Role.INSTRUCTOR:
                dashboard_link = "/instructor/dashboard"
            elif user.role == Role.STUDENT:
                dashboard_link = "/student/dashboard"

            # User avatar with first letter
            user_initial = user.email[0].upper() if user.email else "U"

            # Create authenticated nav
            nav_buttons = fh.Nav(
                fh.A(
                    "Dashboard",
                    href=dashboard_link,
                    cls=signin_link_cls,
                ),
                fh.A(
                    fh.Div(
                        fh.Div(
                            user_initial,
                            cls=(
                                f"w-8 h-8 rounded-full bg-{COLOR['accent']} "
                                "text-white flex items-center justify-center "
                                "font-semibold"
                            ),
                        ),
                        cls="mx-2",
                    ),
                    href="/profile",
                    title="Profile",
                    cls="hover:opacity-80 transition-opacity",
                ),
                fh.A(
                    "Sign Out",
                    href="/logout",
                    cls=f"{TEXT['label']} text-{COLOR['text_muted']} ml-4 "
                    f"hover:text-{COLOR['primary']}",
                ),
                cls="flex items-center",
            )
        except Exception:
            # Fallback to default buttons if there's an error
            nav_buttons = fh.Nav(
                fh.A("Sign in", href="/login", cls=signin_link_cls),
                fh.A(
                    "Sign up",
                    href="/register",
                    cls=button_classes("secondary", "md"),
                ),
                cls="flex items-center",
            )
    else:
        # Default buttons for unauthenticated users
        nav_buttons = fh.Nav(
            fh.A("Sign in", href="/login", cls=signin_link_cls),
            fh.A(
                "Sign up",
                href="/register",
                cls=button_classes("secondary", "md"),
            ),
            cls="flex items-center",
        )

    return fh.Header(
        fh.Div(
            # Left side - Logo and name
            fh.A(
                brand_logo,
                href="/landing",  # Always go to landing page, not dashboard
                cls="flex items-center hover:opacity-90 transition-opacity",
            ),
            # Right side - conditional buttons
            nav_buttons,
            cls="container mx-auto flex justify-between items-center px-4",
        ),
        cls=f"bg-{COLOR['surface_alt']} {RULE_HEAVY} py-4",
    )


def bullseye_progress(closeness, size=32, label=None):
    """
    Dartboard progress glyph — a dart that lands closer to the bullseye as a
    student's drafts improve.

    FeedForward does not show numeric scores to students by default (score
    display is a config option, default off). This glyph is the student-facing
    progress cue: concentric ink rings on paper, with a teal dart whose
    distance from the centre encodes ``closeness``.

    Args:
        closeness: 0.0 to 1.0; 1.0 puts the dart on the bullseye. (Work in
            progress: how feedback maps to closeness is still being designed —
            callers should treat this as a qualitative cue, not a score.)
        size: Rendered width/height in px.
        label: Optional accessible label; defaults to a qualitative phrase.
    """
    closeness = max(0.0, min(1.0, closeness))
    # Dart lands along a 45° radial: edge of the outer ring -> centre.
    max_r = 13.0
    r = max_r * (1.0 - closeness)
    offset = r * 0.7071  # cos(45°)
    cx, cy = 16 + offset, 16 - offset
    if label is None:
        label = (
            "On the bullseye"
            if closeness >= 0.95
            else "Closing in on the bullseye"
            if closeness >= 0.6
            else "Moving toward the bullseye"
        )
    ink = "#1a2e44"
    teal = "#0d9488"
    svg = (
        f'<svg width="{size}" height="{size}" viewBox="0 0 32 32" '
        f'role="img" aria-label="{label}" fill="none">'
        f'<circle cx="16" cy="16" r="14" stroke="{ink}" stroke-width="1.5"/>'
        f'<circle cx="16" cy="16" r="9" stroke="{ink}" stroke-width="1" opacity="0.55"/>'
        f'<circle cx="16" cy="16" r="4.5" stroke="{ink}" stroke-width="1" opacity="0.35"/>'
        f'<circle cx="16" cy="16" r="1.6" fill="{ink}"/>'
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="{teal}"/>'
        f'<line x1="{cx + 2.2:.1f}" y1="{cy - 2.2:.1f}" x2="{cx + 6.5:.1f}" '
        f'y2="{cy - 6.5:.1f}" stroke="{teal}" stroke-width="1.8" '
        'stroke-linecap="round"/>'
        "</svg>"
    )
    return fh.NotStr(svg)


def error_card(title, message, error_code="", error_type="Error"):
    """
    Create a branded error card (to be used in error pages)

    Args:
        title: Error title
        message: Error message/description
        error_code: Optional error code (e.g., 404, 403)
        error_type: Optional error type (e.g., "Not Found", "Forbidden")
    """
    return fh.Div(
        # Error code and type
        fh.Div(
            fh.Span(
                error_code, cls=f"font-serif text-6xl font-bold text-{COLOR['border']}"
            ),
            fh.Span(error_type, cls=f"{TEXT['label']} text-{COLOR['text_muted']} ml-4"),
            cls="flex items-center justify-center mb-6",
        ),
        # Error title
        fh.H1(
            title,
            cls=f"{TEXT['h1']} text-{COLOR['text_strong']} mb-4 text-center",
        ),
        # Error message
        fh.P(message, cls=f"text-{COLOR['text_body']} mb-8 text-center"),
        # Action buttons
        fh.Div(
            fh.A(
                "Dashboard",
                href="/",  # This will redirect to proper dashboard based on role in landing page
                cls=f"{button_classes('primary', 'lg')} mr-4",
            ),
            fh.A("Sign Out", href="/logout", cls=button_classes("secondary", "lg")),
            cls="flex justify-center",
        ),
        cls=(
            f"p-10 bg-{COLOR['surface']} {RADIUS} border border-{COLOR['border']} "
            "max-w-md mx-auto"
        ),
    )
