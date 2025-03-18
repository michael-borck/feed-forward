"""
UI Components for the FeedForward application

This module contains reusable UI components like headers, footers, and navigation elements
that are shared across multiple pages in the application.
"""
from fasthtml.common import *
from app.models.user import Role

def page_header(show_auth_buttons=True):
    """
    Return a consistent header component for all pages
    
    Args:
        show_auth_buttons: Whether to show sign in/sign up buttons in the header
    """
    # Branded logo/wordmark for header
    brand_logo = Div(
        Span("Feed", cls="text-indigo-300 font-bold"),
        Span("Forward", cls="text-teal-300 font-bold"),
        cls="flex items-center text-2xl"
    )
    
    nav_buttons = Nav(
        A("Sign in", href="/login", cls="text-white px-4 py-2 rounded-lg mx-2 hover:bg-indigo-800 transition-colors"),
        A("Sign up", href="/register", cls="bg-teal-500 text-white px-5 py-2 rounded-lg mx-2 hover:bg-teal-600 shadow-sm transition-all"),
        cls="flex items-center"
    ) if show_auth_buttons else ""
    
    return Header(
        Div(
            # Left side - Logo and name
            A(
                brand_logo,
                href="/",
                cls="flex items-center hover:opacity-90 transition-opacity"
            ),
            # Right side - optional buttons
            nav_buttons,
            cls="container mx-auto flex justify-between items-center px-4"
        ),
        cls="bg-indigo-900 text-white py-4 shadow-md"
    )

def page_footer():
    """Return a consistent footer component for all pages"""
    current_year = "2025"  # In a real app, you'd use datetime.now().year
    
    return Footer(
        Div(
            Div(
                # Footer logo
                Div(
                    Span("Feed", cls="text-indigo-600 font-bold"),
                    Span("Forward", cls="text-teal-500 font-bold"),
                    cls="text-2xl mb-3"
                ),
                P("Transforming the feedback experience for students and educators.", 
                  cls="text-gray-600 max-w-xs"),
                cls="md:w-1/3"
            ),
            Div(
                # Quick links
                Div(
                    H3("Resources", cls="font-semibold text-indigo-800 mb-3"),
                    A("Documentation", href="#", cls="block text-gray-600 hover:text-indigo-600 mb-2"),
                    A("Tutorials", href="#", cls="block text-gray-600 hover:text-indigo-600 mb-2"),
                    A("FAQs", href="#", cls="block text-gray-600 hover:text-indigo-600"),
                    cls="mb-6 md:mb-0"
                ),
                # Legal
                Div(
                    H3("Legal", cls="font-semibold text-indigo-800 mb-3"),
                    A("Terms", href="#", cls="block text-gray-600 hover:text-indigo-600 mb-2"),
                    A("Privacy", href="#", cls="block text-gray-600 hover:text-indigo-600 mb-2"),
                    A("Contact", href="#", cls="block text-gray-600 hover:text-indigo-600"),
                ),
                cls="md:w-1/3 flex gap-12"
            ),
            cls="container mx-auto px-4 py-8 flex flex-col md:flex-row justify-between"
        ),
        Div(
            P(f"© {current_year} FeedForward. All rights reserved.", 
              cls="text-center text-gray-500 text-sm"),
            cls="container mx-auto px-4 py-4 border-t border-gray-200"
        ),
        cls="bg-gray-50"
    )

def page_container(title, content):
    """
    Create a full page with consistent header, footer and styling
    
    Args:
        title: Page title (for browser tab)
        content: The main content of the page
    """
    return Titled(
        title,
        Div(
            page_header(),
            Div(
                content,
                cls="container mx-auto px-4 py-16 flex justify-center bg-gray-100"
            ),
            page_footer(),
            cls="min-h-screen flex flex-col"
        )
    )

def dashboard_header(user_role):
    """
    Return a dashboard header with role-specific navigation
    
    Args:
        user_role: Role of the current user (student, instructor, admin)
    """
    # Portal name based on role
    portal_name = ""
    nav_links = []
    
    # Branded logo/wordmark for header
    brand_logo = Div(
        Span("Feed", cls="text-indigo-300 font-bold"),
        Span("Forward", cls="text-teal-300 font-bold"),
        cls="flex items-center text-2xl"
    )
    
    if user_role == Role.STUDENT:
        portal_name = "Student Portal"
        nav_links = [
            ("Dashboard", "#", True),
            ("My Submissions", "#", False),
            ("Feedback History", "#", False),
            ("Help", "#", False)
        ]
    elif user_role == Role.INSTRUCTOR:
        portal_name = "Instructor Portal"
        nav_links = [
            ("Courses", "#", True),
            ("Assignments", "#", False),
            ("Analytics", "#", False),
            ("Settings", "#", False)
        ]
    elif user_role == Role.ADMIN:
        portal_name = "Admin Portal"
        nav_links = [
            ("Users", "#", True),
            ("Courses", "#", False),
            ("Settings", "#", False),
            ("System", "#", False)
        ]
    
    # Build navigation links
    nav_items = []
    for label, href, is_active in nav_links:
        cls = "text-white px-4 py-2 mx-1 transition-colors hover:text-indigo-200"
        if is_active:
            cls = "text-white bg-indigo-700 px-4 py-2 rounded-lg mx-1 font-medium shadow-sm"
        nav_items.append(A(label, href=href, cls=cls))
    
    # User profile/avatar with logout button
    # Get first letter of email as avatar
    user_initial = user_role.name[0] if isinstance(user_role, Role) else "U"
    
    user_menu = Div(
        Div(
            Div(
                user_initial,  # First letter as fallback
                cls="w-8 h-8 rounded-full bg-teal-500 text-white flex items-center justify-center font-semibold"
            ),
            Div(
                Button(
                    "Logout", 
                    hx_post="/logout", 
                    cls="text-white hover:text-teal-200 transition-colors ml-4 font-medium"
                ),
                cls="flex items-center"
            ),
            cls="flex items-center"
        ),
        cls="ml-6"
    )
    
    return Header(
        Div(
            Div(
                A(
                    brand_logo,
                    href="/",
                    cls="flex items-center hover:opacity-90 transition-opacity mr-4"
                ),
                Span(portal_name, cls="text-gray-300 text-sm md:text-base tracking-wide") if portal_name else "",
                cls="flex items-center"
            ),
            Div(
                Nav(
                    *nav_items,
                    cls="hidden md:flex items-center"
                ),
                user_menu,
                cls="flex items-center"
            ),
            cls="container mx-auto flex justify-between items-center px-4"
        ),
        # Mobile navigation (hamburger menu would be implemented with JavaScript)
        Div(
            Div(
                *[A(label, href=href, cls="block py-2 px-4 hover:bg-indigo-800") for label, href, _ in nav_links],
                cls="hidden py-2"  # Hidden by default, would be shown/hidden with JS
            ),
            cls="md:hidden container mx-auto px-4"
        ),
        cls="bg-indigo-900 text-white py-4 shadow-md"
    )

def dashboard_layout(title, sidebar, main_content, user_role=Role.STUDENT, user=None):
    """
    Create a dashboard layout with header, sidebar, main content, and footer
    
    Args:
        title: Page title
        sidebar: Sidebar content component
        main_content: Main content area component
        user_role: Role of the current user
        user: Optional user object (if available)
    """
    return Titled(
        title,
        Div(
            dashboard_header(user_role),
            Div(
                Div(
                    Div(
                        sidebar,
                        cls="w-full md:w-1/4 mb-6 md:mb-0"
                    ),
                    Div(
                        main_content,
                        cls="w-full md:w-3/4"
                    ),
                    cls="flex flex-col md:flex-row gap-8"
                ),
                cls="container mx-auto p-6"
            ),
            page_footer(),
            cls="min-h-screen flex flex-col bg-gradient-to-br from-gray-50 to-indigo-50"
        )
    )

def card(content, title=None, padding=6, bg_color="bg-white"):
    """
    Create a standard card component with consistent styling
    
    Args:
        content: Content to display inside the card
        title: Optional card title
        padding: Padding size (default: 6)
        bg_color: Background color class (default: bg-white)
    """
    card_content = []
    if title:
        card_content.append(
            Div(
                H3(title, cls="text-lg font-bold text-indigo-900"),
                cls="mb-4 pb-3 border-b border-gray-100"
            )
        )
    card_content.append(content)
    
    return Div(
        *card_content,
        cls=f"{bg_color} p-{padding} rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100"
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
            cls = "flex-1 py-3 px-4 text-center bg-indigo-600 text-white rounded-t-lg font-medium shadow-sm"
        else:
            cls = "flex-1 py-3 px-4 text-center text-gray-600 hover:bg-gray-100 transition-colors border-b border-gray-200"
        tab_items.append(A(label, href=href, cls=cls))
    
    return Div(
        *tab_items,
        cls="bg-white rounded-lg mb-6 flex overflow-hidden shadow-sm"
    )

def status_badge(text, color):
    """
    Create a status badge
    
    Args:
        text: Badge text
        color: Color name (indigo, teal, yellow, red)
    """
    color_map = {
        "blue": "indigo",
        "green": "teal",
        "yellow": "yellow",
        "red": "red",
        "purple": "indigo",
        "gray": "gray"
    }
    
    # Use mapped color or original if not in map
    mapped_color = color_map.get(color, color)
    
    return Span(
        text,
        cls=f"bg-{mapped_color}-100 text-{mapped_color}-700 px-3 py-1 rounded-full text-xs font-semibold shadow-sm"
    )

def data_table(headers, rows):
    """
    Create a data table
    
    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of cell contents)
    """
    # Create table headers
    header_cells = [Th(h, cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100") for h in headers]
    header_row = Tr(*header_cells, cls="bg-indigo-50")
    
    # Create table rows
    table_rows = [header_row]
    for i, row_data in enumerate(rows):
        cells = [Td(cell, cls="py-4 px-6") for cell in row_data]
        row_cls = "border-b border-gray-100 hover:bg-gray-50 transition-colors" if i < len(rows) - 1 else "hover:bg-gray-50 transition-colors"
        table_rows.append(Tr(*cells, cls=row_cls))
    
    return Div(
        Table(
            Thead(header_row),
            Tbody(*table_rows[1:]),
            cls="w-full"
        ),
        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
    )

def summary_card(content, bg_color="indigo"):
    """
    Create a summary card with colored background
    
    Args:
        content: Content to display inside the card
        bg_color: Background color (indigo, teal, yellow, red)
    """
    color_map = {
        "blue": "indigo",
        "green": "teal",
        "yellow": "yellow",
        "red": "red",
        "purple": "indigo"
    }
    
    # Use mapped color or original if not in map
    mapped_color = color_map.get(bg_color, bg_color)
    
    return Div(
        content,
        cls=f"bg-{mapped_color}-50 p-6 rounded-xl mt-6 border border-{mapped_color}-200 shadow-sm"
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
        "blue": "indigo",
        "green": "teal",
        "yellow": "yellow",
        "red": "red",
        "purple": "indigo"
    }
    
    # Use mapped color or original if not in map
    mapped_color = color_map.get(color, color)
    
    return Div(
        Div(
            Div(
                cls=f"w-2 bg-{mapped_color}-500 rounded-l"
            ),
            Div(
                H4(title, cls="font-semibold text-indigo-900 mb-3"),
                content,
                cls="p-5 flex-1"
            ),
            cls="flex"
        ),
        cls="border border-gray-200 rounded-xl mb-4 overflow-hidden bg-white shadow-md hover:shadow-lg transition-shadow"
    )

def action_button(text, color="indigo", href="#", icon=None, size="medium"):
    """
    Create an action button
    
    Args:
        text: Button text
        color: Button color (indigo, teal, red, yellow)
        href: Button link
        icon: Optional icon (e.g., +, ↑, ✓)
        size: Button size (small, medium, large)
    """
    color_map = {
        "blue": "indigo",
        "green": "teal",
        "yellow": "yellow",
        "red": "red",
        "purple": "indigo"
    }
    
    # Use mapped color or original if not in map
    mapped_color = color_map.get(color, color)
    
    # Size mapping
    size_classes = {
        "small": "px-3 py-1 text-sm",
        "medium": "px-5 py-2",
        "large": "px-6 py-3 text-lg"
    }
    padding = size_classes.get(size, "px-5 py-2")
    
    button_content = []
    if icon:
        button_content.append(Span(icon, cls="mr-2"))
    button_content.append(text)
    
    return A(
        *button_content,
        href=href,
        cls=f"bg-{mapped_color}-600 text-white {padding} rounded-lg inline-flex items-center justify-center hover:bg-{mapped_color}-700 transition-all shadow-sm hover:shadow font-medium"
    )

def modal_dialog(title, content, footer=None):
    """
    Create a modal dialog component
    
    Args:
        title: Dialog title
        content: Dialog content
        footer: Optional dialog footer with action buttons
    """
    return Div(
        Div(
            Div(
                H3(title, cls="text-xl font-bold text-indigo-900"),
                Button("×", cls="text-gray-500 hover:text-gray-700 text-2xl font-bold"),
                cls="flex justify-between items-center border-b border-gray-200 pb-4 mb-6"
            ),
            Div(
                content,
                cls="mb-6"
            ),
            Div(
                footer if footer else "",
                cls="flex justify-end space-x-4"
            ),
            cls="bg-white p-8 rounded-xl shadow-xl max-w-2xl w-full border border-gray-100"
        ),
        cls="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 backdrop-blur-sm"
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
            cls = "bg-indigo-100 p-3 rounded-lg mb-2 text-indigo-700 font-medium flex items-center"
        else:
            cls = "p-3 mb-2 hover:bg-gray-100 rounded-lg text-gray-600 transition-all flex items-center"
        nav_items.append(A(
            label,
            href=href,
            cls=cls
        ))
    
    return Div(
        *nav_items,
        cls="bg-white p-4 rounded-xl shadow-md border border-gray-100"
    )