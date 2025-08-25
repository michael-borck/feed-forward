"""
Enhanced documentation viewer for FeedForward.
Renders markdown documentation with improved formatting and UI/UX.
"""

import re
from pathlib import Path
from typing import Optional, Tuple

from fasthtml import common as fh
from markdown2 import Markdown

from app import rt
from app.utils.ui import dynamic_header, page_footer


def load_and_process_markdown(filepath: Path) -> Optional[Tuple[str, str]]:
    """
    Load and process a markdown file with enhanced rendering.
    Returns tuple of (html_content, title) or None if file not found.
    """
    try:
        with open(filepath) as f:
            content = f.read()
        
        # Remove Jekyll front matter
        content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)
        
        # Extract title before processing
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Documentation"
        
        # Pre-process Jekyll-specific syntax
        # Remove Jekyll-specific class assignments and TOC markers
        content = re.sub(r"{:\s*\.no_toc\s*(?:\.text-delta)?\s*}", "", content)
        content = re.sub(r"{:\s*\.note\s*}", "", content)
        content = re.sub(r"{:\s*\.tip\s*}", "", content)
        content = re.sub(r"{:\s*\.warning\s*}", "", content)
        content = re.sub(r"{:\s*\.important\s*}", "", content)
        content = re.sub(r"{:\s*\.[^}]+}", "", content)
        
        # Convert Jekyll TOC syntax
        content = re.sub(r"1\.\s+TOC\s*\n\s*{:toc}", "", content)
        
        # Convert callout blocks (> text after {: .note }) to styled divs
        def replace_callout(match):
            callout_type = match.group(1) if match.group(1) else 'note'
            callout_text = match.group(2)
            # Determine icon and color based on type
            if 'tip' in callout_type:
                icon = '💡'
                css_class = 'callout-tip'
            elif 'warning' in callout_type:
                icon = '⚠️'
                css_class = 'callout-warning'
            elif 'important' in callout_type:
                icon = '❗'
                css_class = 'callout-important'
            else:  # note
                icon = 'ℹ️'
                css_class = 'callout-note'
            return f'<div class="callout {css_class}"><span class="callout-icon">{icon}</span><div class="callout-content">{callout_text}</div></div>'
        
        # Process callouts that appear after blockquotes
        content = re.sub(
            r'>\s*(.+?)(?:\n>.*?)*\n*{:\s*\.(\w+)\s*}',
            lambda m: replace_callout(m),
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Configure markdown2 with enhanced extras
        markdowner = Markdown(extras=[
            'fenced-code-blocks',
            'tables',
            'break-on-newline',
            'code-friendly',
            'cuddled-lists',
            'footnotes',
            'header-ids',
            'markdown-in-html',
            'smarty-pants',
            'strike',
            'target-blank-links',
            'task_list',
            'wiki-tables',
        ])
        
        # Convert markdown to HTML
        html = markdowner.convert(content)
        
        # Post-process to fix internal links
        html = re.sub(r'href="\./([^"]+)\.md"', r'href="/docs/\1"', html)
        html = re.sub(r'href="([^"]+)\.md"', r'href="/docs/\1"', html)
        
        # Add IDs to headers for navigation
        html = re.sub(
            r'<h([1-6])>(.+?)</h\1>',
            lambda m: f'<h{m.group(1)} id="{re.sub(r"[^\w\s-]", "", m.group(2).lower()).replace(" ", "-")}">{m.group(2)}</h{m.group(1)}>',
            html
        )
        
        return html, title
        
    except FileNotFoundError:
        return None, None


def generate_toc(html_content: str) -> str:
    """Generate a table of contents from HTML headers."""
    headers = re.findall(r'<h([2-3])[^>]*id="([^"]+)"[^>]*>(.+?)</h\1>', html_content)
    
    if not headers:
        return ""
    
    toc_items = []
    for level, id_attr, text in headers:
        indent = "ml-4" if level == "3" else ""
        toc_items.append(
            fh.Li(
                fh.A(
                    text,
                    href=f"#{id_attr}",
                    cls=f"toc-link {indent}",
                    onclick="event.preventDefault(); document.getElementById('" + id_attr + "').scrollIntoView({behavior: 'smooth'});"
                ),
                cls="toc-item"
            )
        )
    
    return fh.Div(
        fh.H3("On this page", cls="toc-title"),
        fh.Ul(*toc_items, cls="toc-list"),
        cls="table-of-contents",
        id="toc"
    )


def get_enhanced_styles():
    """Return enhanced CSS styles for documentation."""
    return fh.Style("""
        /* Enhanced Typography */
        .prose {
            max-width: 65ch;
            color: #1f2937;
            line-height: 1.75;
        }
        
        .prose h1 {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 1.5rem;
            color: #111827;
            border-bottom: 3px solid #e5e7eb;
            padding-bottom: 0.75rem;
        }
        
        .prose h2 {
            font-size: 2rem;
            font-weight: 700;
            margin-top: 3rem;
            margin-bottom: 1.25rem;
            color: #1f2937;
            border-bottom: 2px solid #f3f4f6;
            padding-bottom: 0.5rem;
        }
        
        .prose h3 {
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: 2rem;
            margin-bottom: 1rem;
            color: #374151;
        }
        
        .prose h4 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: 1.5rem;
            margin-bottom: 0.75rem;
            color: #4b5563;
        }
        
        .prose p {
            margin-bottom: 1.25rem;
        }
        
        .prose a {
            color: #2563eb;
            text-decoration: none;
            border-bottom: 1px solid #93c5fd;
            transition: all 0.2s;
        }
        
        .prose a:hover {
            color: #1d4ed8;
            border-bottom-color: #2563eb;
            background-color: #eff6ff;
        }
        
        /* Lists */
        .prose ul, .prose ol {
            margin-bottom: 1.25rem;
            padding-left: 1.5rem;
        }
        
        .prose ul {
            list-style-type: disc;
        }
        
        .prose ol {
            list-style-type: decimal;
        }
        
        .prose li {
            margin-bottom: 0.5rem;
            line-height: 1.75;
        }
        
        .prose li > ul, .prose li > ol {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Code Blocks */
        .prose code {
            background-color: #f3f4f6;
            color: #dc2626;
            padding: 0.125rem 0.375rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            font-family: 'Fira Code', 'Consolas', monospace;
            font-weight: 500;
        }
        
        .prose pre {
            background-color: #1e293b;
            color: #e2e8f0;
            padding: 1.25rem;
            border-radius: 0.5rem;
            overflow-x: auto;
            margin-bottom: 1.5rem;
            font-size: 0.875rem;
            line-height: 1.625;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .prose pre code {
            background-color: transparent;
            color: inherit;
            padding: 0;
            font-size: inherit;
        }
        
        /* Tables */
        .prose table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            border-radius: 0.5rem;
            overflow: hidden;
        }
        
        .prose th {
            background-color: #f8fafc;
            font-weight: 600;
            text-align: left;
            padding: 0.75rem 1rem;
            border-bottom: 2px solid #e5e7eb;
            color: #1f2937;
        }
        
        .prose td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .prose tbody tr:last-child td {
            border-bottom: none;
        }
        
        .prose tbody tr:hover {
            background-color: #f9fafb;
        }
        
        /* Blockquotes */
        .prose blockquote {
            border-left: 4px solid #6366f1;
            padding-left: 1.25rem;
            margin-left: 0;
            margin-bottom: 1.5rem;
            font-style: italic;
            color: #4b5563;
            background-color: #f9fafb;
            padding: 1rem 1.25rem;
            border-radius: 0 0.5rem 0.5rem 0;
        }
        
        /* Callout Boxes */
        .callout {
            padding: 1rem 1.25rem;
            margin-bottom: 1.5rem;
            border-radius: 0.5rem;
            border-left: 4px solid;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .callout-icon {
            font-size: 1.25rem;
            flex-shrink: 0;
            margin-top: 0.125rem;
        }
        
        .callout-content {
            flex-grow: 1;
        }
        
        .callout-content p {
            margin-bottom: 0;
        }
        
        .callout-note {
            background-color: #eff6ff;
            border-left-color: #3b82f6;
            color: #1e40af;
        }
        
        .callout-tip {
            background-color: #f0fdf4;
            border-left-color: #22c55e;
            color: #166534;
        }
        
        .callout-warning {
            background-color: #fef3c7;
            border-left-color: #f59e0b;
            color: #92400e;
        }
        
        .callout-important {
            background-color: #fef2f2;
            border-left-color: #ef4444;
            color: #991b1b;
        }
        
        /* Table of Contents */
        .table-of-contents {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            padding: 1.25rem;
            margin-bottom: 2rem;
        }
        
        .toc-title {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #374151;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .toc-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .toc-item {
            margin-bottom: 0.5rem;
        }
        
        .toc-link {
            color: #6b7280;
            text-decoration: none;
            display: block;
            padding: 0.25rem 0;
            transition: all 0.2s;
            border-left: 2px solid transparent;
            padding-left: 0.5rem;
        }
        
        .toc-link:hover {
            color: #2563eb;
            border-left-color: #2563eb;
            background-color: #eff6ff;
        }
        
        .toc-link.ml-4 {
            margin-left: 1.5rem;
            font-size: 0.9rem;
        }
        
        /* Navigation Sidebar */
        .doc-nav {
            background-color: #ffffff;
            border-right: 1px solid #e5e7eb;
            height: 100%;
            overflow-y: auto;
            padding: 1.5rem;
        }
        
        .doc-nav h3 {
            font-size: 0.875rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #4b5563;
            margin-bottom: 0.75rem;
            margin-top: 1.5rem;
        }
        
        .doc-nav h3:first-child {
            margin-top: 0;
        }
        
        .doc-nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .doc-nav li {
            margin-bottom: 0.25rem;
        }
        
        .doc-nav a {
            display: block;
            padding: 0.5rem 0.75rem;
            color: #6b7280;
            text-decoration: none;
            border-radius: 0.375rem;
            transition: all 0.2s;
            font-size: 0.9rem;
        }
        
        .doc-nav a:hover {
            background-color: #f3f4f6;
            color: #1f2937;
        }
        
        .doc-nav a.active {
            background-color: #eff6ff;
            color: #2563eb;
            font-weight: 500;
        }
        
        /* Quick Access Cards */
        .quick-access-card {
            background-color: #f9fafb;
            border: 1px solid #e5e7eb;
            border-radius: 0.5rem;
            padding: 1rem 1.25rem;
            margin-bottom: 0.75rem;
            transition: all 0.2s;
            display: block;
            text-decoration: none;
        }
        
        .quick-access-card:hover {
            background-color: #eff6ff;
            border-color: #93c5fd;
            transform: translateX(0.25rem);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .prose {
                max-width: none;
            }
            
            .table-of-contents {
                position: static;
                width: 100%;
                margin-bottom: 2rem;
            }
        }
        
        /* Smooth Scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Print Styles */
        @media print {
            .doc-nav, .table-of-contents, .page-footer {
                display: none;
            }
            
            .prose {
                max-width: none;
            }
        }
    """)


@rt("/docs")
def get(session):
    """Enhanced documentation home page."""
    return fh.Div(
        dynamic_header(session),
        fh.Div(
            render_doc_nav(),
            fh.Div(
                fh.H1("📚 FeedForward Documentation", cls="text-4xl font-bold mb-2 text-indigo-900"),
                fh.P(
                    "Welcome to the FeedForward documentation. Get started quickly with our guides below.",
                    cls="text-lg text-gray-600 mb-8",
                ),
                
                # Quick Start Section
                fh.Div(
                    fh.H2("🚀 Quick Start", cls="text-2xl font-bold mb-4 text-gray-800"),
                    fh.Div(
                        # Student Card
                        fh.A(
                            fh.Div(
                                fh.Span("🎓", cls="text-3xl mb-2"),
                                fh.H3("For Students", cls="text-xl font-semibold mb-2 text-gray-800"),
                                fh.P("Learn how to submit assignments and receive AI-powered feedback", cls="text-gray-600"),
                                cls="quick-access-card"
                            ),
                            href="/docs/user-guides/student/getting-started",
                            cls="block"
                        ),
                        
                        # Instructor Card
                        fh.A(
                            fh.Div(
                                fh.Span("👩‍🏫", cls="text-3xl mb-2"),
                                fh.H3("For Instructors", cls="text-xl font-semibold mb-2 text-gray-800"),
                                fh.P("Create courses, design assignments, and review AI feedback", cls="text-gray-600"),
                                cls="quick-access-card"
                            ),
                            href="/docs/user-guides/instructor/course-management",
                            cls="block"
                        ),
                        
                        # Admin Card
                        fh.A(
                            fh.Div(
                                fh.Span("⚙️", cls="text-3xl mb-2"),
                                fh.H3("For Administrators", cls="text-xl font-semibold mb-2 text-gray-800"),
                                fh.P("Configure system settings and manage your FeedForward instance", cls="text-gray-600"),
                                cls="quick-access-card"
                            ),
                            href="/docs/user-guides/admin/initial-setup",
                            cls="block"
                        ),
                        cls="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
                    ),
                ),
                
                # Popular Topics
                fh.Div(
                    fh.H2("📖 Popular Topics", cls="text-2xl font-bold mb-4 text-gray-800"),
                    fh.Div(
                        fh.Div(
                            fh.H4("Getting Started", cls="font-semibold text-gray-700 mb-2"),
                            fh.Ul(
                                fh.Li(fh.A("Installation Guide", href="/docs/getting-started/installation", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("Configuration", href="/docs/getting-started/configuration", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("Quick Start Tutorial", href="/docs/getting-started/quick-start", cls="text-blue-600 hover:underline")),
                                cls="list-disc list-inside space-y-1"
                            ),
                            cls="bg-white p-4 rounded-lg border border-gray-200"
                        ),
                        fh.Div(
                            fh.H4("Technical Documentation", cls="font-semibold text-gray-700 mb-2"),
                            fh.Ul(
                                fh.Li(fh.A("System Architecture", href="/docs/technical/architecture", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("API Reference", href="/docs/technical/api-reference", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("Database Schema", href="/docs/technical/database-schema", cls="text-blue-600 hover:underline")),
                                cls="list-disc list-inside space-y-1"
                            ),
                            cls="bg-white p-4 rounded-lg border border-gray-200"
                        ),
                        fh.Div(
                            fh.H4("Deployment", cls="font-semibold text-gray-700 mb-2"),
                            fh.Ul(
                                fh.Li(fh.A("Requirements", href="/docs/deployment/requirements", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("Installation Steps", href="/docs/deployment/installation", cls="text-blue-600 hover:underline")),
                                fh.Li(fh.A("Troubleshooting", href="/docs/deployment/troubleshooting", cls="text-blue-600 hover:underline")),
                                cls="list-disc list-inside space-y-1"
                            ),
                            cls="bg-white p-4 rounded-lg border border-gray-200"
                        ),
                        cls="grid grid-cols-1 md:grid-cols-3 gap-4"
                    ),
                ),
                cls="flex-1 p-8 overflow-y-auto max-w-6xl mx-auto"
            ),
            cls="flex h-screen overflow-hidden bg-gray-50"
        ),
        get_enhanced_styles(),
        page_footer(),
        cls="min-h-screen flex flex-col"
    )


@rt("/docs/{path:path}")
def get_doc_page(session, path: str):
    """Display a specific documentation page with enhanced rendering."""
    # Sanitize path
    path = path.replace("..", "")
    
    # Load the markdown file
    doc_path = Path(f"docs/{path}.md")
    html_content, title = load_and_process_markdown(doc_path)
    
    if html_content is None:
        return fh.Div(
            dynamic_header(session),
            fh.Div(
                render_doc_nav(path),
                fh.Div(
                    fh.Div(
                        fh.H1("📄 Page Not Found", cls="text-3xl font-bold mb-4 text-red-600"),
                        fh.P(
                            f"The documentation page '{path}' could not be found.",
                            cls="text-gray-600 mb-4",
                        ),
                        fh.P(
                            "This might be because:",
                            cls="text-gray-600 mb-2"
                        ),
                        fh.Ul(
                            fh.Li("The page has been moved or renamed"),
                            fh.Li("The URL was typed incorrectly"),
                            fh.Li("The documentation is still being written"),
                            cls="list-disc list-inside text-gray-600 mb-6"
                        ),
                        fh.A(
                            "← Back to Documentation Home",
                            href="/docs",
                            cls="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors",
                        ),
                        cls="bg-white p-8 rounded-lg shadow-md"
                    ),
                    cls="flex-1 p-8 max-w-4xl mx-auto"
                ),
                cls="flex h-screen overflow-hidden bg-gray-50"
            ),
            get_enhanced_styles(),
            page_footer(),
            cls="min-h-screen flex flex-col"
        )
    
    # Generate table of contents
    toc = generate_toc(html_content)
    
    return fh.Div(
        dynamic_header(session),
        fh.Div(
            render_doc_nav(path),
            fh.Div(
                # Breadcrumb
                fh.Div(
                    fh.A("Documentation", href="/docs", cls="text-blue-600 hover:underline"),
                    fh.Span(" / ", cls="text-gray-400 mx-2"),
                    fh.Span(title, cls="text-gray-600"),
                    cls="text-sm mb-4"
                ),
                
                # Table of Contents (if headers exist)
                toc if toc else "",
                
                # Main content
                fh.Div(
                    fh.Div(fh.NotStr(html_content), cls="prose prose-lg max-w-none"),
                    cls="bg-white p-8 rounded-lg shadow-sm"
                ),
                
                # Navigation buttons
                fh.Div(
                    fh.A(
                        "← Back to Documentation",
                        href="/docs",
                        cls="text-blue-600 hover:underline",
                    ),
                    cls="mt-8 pt-4 border-t border-gray-200"
                ),
                cls="flex-1 p-8 overflow-y-auto max-w-4xl mx-auto"
            ),
            cls="flex h-screen overflow-hidden bg-gray-50"
        ),
        get_enhanced_styles(),
        page_footer(),
        cls="min-h-screen flex flex-col"
    )


def render_doc_nav(current_path=None):
    """Enhanced documentation navigation sidebar."""
    structure = get_doc_structure()
    nav_items = []
    
    # Navigation header
    nav_items.append(
        fh.Div(
            fh.A(
                fh.Div(
                    fh.Span("←", cls="mr-2"),
                    "Back to App",
                    cls="flex items-center"
                ),
                href="/",
                cls="block px-3 py-2 text-green-600 hover:bg-green-50 rounded font-medium mb-2 transition-colors",
            ),
            fh.A(
                fh.Div(
                    fh.Span("🏠", cls="mr-2"),
                    "Documentation Home",
                    cls="flex items-center"
                ),
                href="/docs",
                cls="block px-3 py-2 text-blue-600 hover:bg-blue-50 rounded font-medium mb-4 transition-colors",
            ),
            cls="border-b border-gray-200 pb-4 mb-4",
        )
    )
    
    for section, items in structure.items():
        if section == "Quick Access":
            # Special styling for Quick Access
            links = []
            for title, path in items:
                active = path == current_path
                icon = "🎓" if "student" in path else "👩‍🏫" if "instructor" in path else "⚙️"
                links.append(
                    fh.Li(
                        fh.A(
                            fh.Div(
                                fh.Span(icon, cls="mr-2"),
                                title,
                                cls="flex items-center"
                            ),
                            href=f"/docs/{path}",
                            cls=f"quick-access-card {'active' if active else ''}",
                        ),
                        cls="block"
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                    fh.Ul(*links, cls="list-none space-y-2"),
                    cls="mb-6 pb-4 border-b border-gray-200",
                )
            )
        elif isinstance(items, dict):
            # Nested structure
            section_items = []
            for subsection, subitems in items.items():
                sub_links = []
                for title, path in subitems:
                    active = path == current_path
                    sub_links.append(
                        fh.Li(
                            fh.A(
                                title,
                                href=f"/docs/{path}",
                                cls=f"doc-nav a {'active' if active else ''}",
                            )
                        )
                    )
                section_items.append(
                    fh.Div(
                        fh.H4(subsection, cls="font-medium text-gray-700 px-3 py-1 text-sm"),
                        fh.Ul(*sub_links, cls="list-none ml-3"),
                        cls="mb-3",
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section),
                    fh.Div(*section_items),
                    cls="mb-4",
                )
            )
        else:
            # Simple list
            links = []
            for title, path in items:
                active = path == current_path
                links.append(
                    fh.Li(
                        fh.A(
                            title,
                            href=f"/docs/{path}",
                            cls=f"doc-nav a {'active' if active else ''}",
                        )
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section),
                    fh.Ul(*links, cls="list-none"),
                    cls="mb-4",
                )
            )
    
    return fh.Nav(
        fh.Div(*nav_items),
        cls="doc-nav w-72 flex-shrink-0",
    )


def get_doc_structure():
    """Enhanced documentation structure."""
    return {
        "Quick Access": [
            ("Student Guide", "user-guides/student/index"),
            ("Instructor Guide", "user-guides/instructor/index"),
            ("Admin Guide", "user-guides/admin/index"),
        ],
        "Getting Started": [
            ("Installation", "getting-started/installation"),
            ("Configuration", "getting-started/configuration"),
            ("Quick Start", "getting-started/quick-start"),
        ],
        "User Guides": {
            "Students": [
                ("Overview", "user-guides/student/index"),
                ("Getting Started", "user-guides/student/getting-started"),
                ("Submitting Work", "user-guides/student/submissions"),
                ("Viewing Feedback", "user-guides/student/viewing-feedback"),
                ("Tracking Progress", "user-guides/student/progress"),
            ],
            "Instructors": [
                ("Overview", "user-guides/instructor/index"),
                ("Course Management", "user-guides/instructor/course-management"),
                ("Creating Assignments", "user-guides/instructor/assignments"),
                ("Using Rubrics", "user-guides/instructor/rubrics"),
                ("Managing Students", "user-guides/instructor/student-invites"),
                ("Reviewing Feedback", "user-guides/instructor/feedback-review"),
            ],
            "Administrators": [
                ("Overview", "user-guides/admin/index"),
                ("Initial Setup", "user-guides/admin/initial-setup"),
                ("User Management", "user-guides/admin/user-management"),
                ("AI Configuration", "user-guides/admin/ai-configuration"),
                ("Maintenance", "user-guides/admin/maintenance"),
            ],
        },
        "Deployment": [
            ("Requirements", "deployment/requirements"),
            ("Installation", "deployment/installation"),
            ("Configuration", "deployment/configuration"),
            ("Troubleshooting", "deployment/troubleshooting"),
        ],
        "Technical": [
            ("Architecture", "technical/architecture"),
            ("Database Schema", "technical/database-schema"),
            ("API Reference", "technical/api-reference"),
            ("Privacy & Security", "technical/privacy-security"),
        ],
    }