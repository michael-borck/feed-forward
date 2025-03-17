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
    nav_buttons = Nav(
        A("Sign in", href="/login", cls="text-white px-4 py-2 rounded-lg mx-2 hover:bg-gray-700"),
        A("Sign up", href="/register", cls="bg-blue-500 text-white px-4 py-2 rounded-lg mx-2 hover:bg-blue-600"),
        cls="flex items-center"
    ) if show_auth_buttons else ""
    
    return Header(
        Div(
            # Left side - Logo and name
            Div(
                H1("FeedForward", cls="text-2xl font-bold"),
                cls="flex items-center"
            ),
            # Right side - optional buttons
            nav_buttons,
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-800 text-white p-4"
    )

def page_footer():
    """Return a consistent footer component for all pages"""
    return Footer(
        Div(
            P("© 2025 FeedForward. All rights reserved.", cls="text-gray-500"),
            Div(
                A("Terms", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Privacy", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                A("Contact", href="#", cls="text-gray-500 hover:text-gray-700 mx-2"),
                cls="flex"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-100 border-t border-gray-200 py-6"
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
        cls = "text-white px-3 font-medium"
        if is_active:
            cls += " bg-blue-500 bg-opacity-30 rounded-lg py-1 px-4"
        nav_items.append(A(label, href=href, cls=cls))
    
    return Header(
        Div(
            Div(
                H1("FeedForward", cls="text-2xl font-bold"),
                Span(portal_name, cls="ml-3 text-gray-300") if portal_name else "",
                cls="flex items-center"
            ),
            Nav(
                *nav_items,
                cls="bg-gray-700 rounded-lg px-4 py-2"
            ),
            cls="container mx-auto flex justify-between items-center"
        ),
        cls="bg-gray-800 text-white p-4"
    )

def dashboard_layout(title, sidebar, main_content, user_role=Role.STUDENT):
    """
    Create a dashboard layout with header, sidebar, main content, and footer
    
    Args:
        title: Page title
        sidebar: Sidebar content component
        main_content: Main content area component
        user_role: Role of the current user
    """
    return Titled(
        title,
        Div(
            dashboard_header(user_role),
            Div(
                Div(
                    Div(
                        sidebar,
                        cls="w-full md:w-1/4"
                    ),
                    Div(
                        main_content,
                        cls="w-full md:w-3/4"
                    ),
                    cls="flex flex-col md:flex-row gap-6"
                ),
                cls="container mx-auto p-4"
            ),
            page_footer(),
            cls="min-h-screen flex flex-col bg-gray-100"
        )
    )

def card(content, title=None, padding=4, bg_color="bg-gray-50"):
    """
    Create a standard card component with consistent styling
    
    Args:
        content: Content to display inside the card
        title: Optional card title
        padding: Padding size (default: 4)
        bg_color: Background color class (default: bg-gray-50)
    """
    card_content = []
    if title:
        card_content.append(H3(title, cls="text-lg font-bold text-gray-700 mb-2"))
    card_content.append(content)
    
    return Div(
        *card_content,
        cls=f"{bg_color} p-{padding} rounded-lg shadow-md"
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
            cls = "flex-1 py-3 px-4 text-center bg-blue-500 text-white rounded-lg"
        else:
            cls = "flex-1 py-3 px-4 text-center text-gray-500 hover:bg-gray-200"
        tab_items.append(A(label, href=href, cls=cls))
    
    return Div(
        *tab_items,
        cls="bg-gray-100 rounded-lg mb-6 flex"
    )

def status_badge(text, color):
    """
    Create a status badge
    
    Args:
        text: Badge text
        color: Color name (blue, green, yellow, red)
    """
    return Span(
        text,
        cls=f"bg-{color}-100 text-{color}-600 px-3 py-1 rounded-lg text-xs font-semibold"
    )

def data_table(headers, rows):
    """
    Create a data table
    
    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of cell contents)
    """
    # Create table headers
    header_cells = [Th(h, cls="text-left py-3 px-4 font-semibold text-gray-700") for h in headers]
    header_row = Tr(*header_cells, cls="bg-gray-100")
    
    # Create table rows
    table_rows = [header_row]
    for i, row_data in enumerate(rows):
        cells = [Td(cell, cls="py-4 px-4") for cell in row_data]
        row_cls = "border-b border-gray-200" if i < len(rows) - 1 else ""
        table_rows.append(Tr(*cells, cls=row_cls))
    
    return Div(
        Table(
            Thead(header_row),
            Tbody(*table_rows[1:]),
            cls="w-full"
        ),
        cls="overflow-x-auto"
    )

def summary_card(content, bg_color="blue"):
    """
    Create a summary card with colored background
    
    Args:
        content: Content to display inside the card
        bg_color: Background color (blue, green, yellow, red)
    """
    return Div(
        content,
        cls=f"bg-{bg_color}-50 p-4 rounded-lg mt-6 border border-{bg_color}-100"
    )

def feedback_card(title, content, color="green"):
    """
    Create a feedback card with colored indicator bar
    
    Args:
        title: Card title
        content: Card content
        color: Indicator color (green, red, blue, yellow)
    """
    return Div(
        Div(
            Div(
                cls=f"w-1 bg-{color}-500"
            ),
            Div(
                H4(title, cls="font-semibold text-gray-700 mb-2"),
                content,
                cls="p-4 flex-1"
            ),
            cls="flex"
        ),
        cls="border border-gray-200 rounded-lg mb-4 overflow-hidden"
    )

def action_button(text, color="blue", href="#", icon=None):
    """
    Create an action button
    
    Args:
        text: Button text
        color: Button color (blue, green, red, yellow)
        href: Button link
        icon: Optional icon (e.g., +, ↑, ✓)
    """
    button_content = []
    if icon:
        button_content.append(Span(icon, cls="mr-1"))
    button_content.append(text)
    
    return A(
        *button_content,
        href=href,
        cls=f"bg-{color}-500 text-white px-4 py-2 rounded-lg inline-flex items-center justify-center hover:bg-{color}-600 transition-colors"
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
                H3(title, cls="text-lg font-bold text-gray-700"),
                Button("×", cls="text-gray-500 hover:text-gray-700 text-2xl font-bold"),
                cls="flex justify-between items-center border-b border-gray-200 pb-3 mb-4"
            ),
            Div(
                content,
                cls="mb-6"
            ),
            Div(
                footer if footer else "",
                cls="flex justify-end space-x-3"
            ),
            cls="bg-gray-50 p-6 rounded-lg shadow-lg max-w-2xl w-full"
        ),
        cls="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
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
            cls = "bg-gray-100 p-3 rounded-lg mb-3"
        else:
            cls = "p-3 mb-3 border border-transparent hover:border-gray-200 hover:bg-gray-50 rounded-lg"
        nav_items.append(A(
            label,
            href=href,
            cls=cls
        ))
    
    return Div(
        *nav_items,
        cls="space-y-1"
    )