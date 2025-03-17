"""
UI Components for the FeedForward application

This module contains reusable UI components like headers, footers, and navigation elements
that are shared across multiple pages in the application.
"""
from fasthtml.common import *

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