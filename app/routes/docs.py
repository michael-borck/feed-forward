"""
In-app documentation viewer for FeedForward.
Renders markdown documentation files directly in the application.
"""

import re
from pathlib import Path

import markdown
from fasthtml import common as fh

from app import rt
from app.utils.ui import dynamic_header, page_footer


def load_markdown_file(filepath):
    """Load and parse a markdown file, with caching."""
    try:
        with open(filepath) as f:
            content = f.read()

        # Remove Jekyll front matter
        content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)

        # Convert markdown to HTML (basic conversion)
        # In production, consider using a proper markdown parser
        content = convert_markdown_to_html(content)

        return content
    except FileNotFoundError:
        return None


def convert_markdown_to_html(md_content):
    """Convert markdown to HTML using the markdown library with enhanced processing."""
    # Pre-process Jekyll-specific syntax
    # Remove Jekyll-specific class assignments and TOC markers
    md_content = re.sub(r"{:\s*\.no_toc\s*(?:\.text-delta)?\s*}", "", md_content)
    md_content = re.sub(r"1\.\s+TOC\s*\n\s*{:toc}", "", md_content)
    
    # Process callout blocks - convert Jekyll syntax to HTML
    md_content = re.sub(r'{:\s*\.warning\s*}', '', md_content)
    md_content = re.sub(r'{:\s*\.note\s*}', '', md_content)
    md_content = re.sub(r'{:\s*\.tip\s*}', '', md_content)
    md_content = re.sub(r'{:\s*\.important\s*}', '', md_content)
    md_content = re.sub(r'{:\s*\.[^}]+}', '', md_content)
    
    # Convert blockquotes with Jekyll classes to styled divs
    def process_blockquote(match):
        content = match.group(1)
        # Check what came before to determine type
        lines_before = md_content[:match.start()].split('\n')
        if lines_before and '{: .warning' in lines_before[-1]:
            return f'<div class="callout callout-warning"><span class="callout-icon">⚠️</span><div class="callout-content">{content}</div></div>'
        elif lines_before and '{: .tip' in lines_before[-1]:
            return f'<div class="callout callout-tip"><span class="callout-icon">💡</span><div class="callout-content">{content}</div></div>'
        elif lines_before and '{: .important' in lines_before[-1]:
            return f'<div class="callout callout-important"><span class="callout-icon">❗</span><div class="callout-content">{content}</div></div>'
        elif lines_before and '{: .note' in lines_before[-1]:
            return f'<div class="callout callout-note"><span class="callout-icon">ℹ️</span><div class="callout-content">{content}</div></div>'
        else:
            return f'<blockquote>{content}</blockquote>'
    
    # Process standard blockquotes
    md_content = re.sub(r'^>\s*(.+?)$', process_blockquote, md_content, flags=re.MULTILINE)

    # Configure markdown extensions for better rendering
    md = markdown.Markdown(
        extensions=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.tables",
            "markdown.extensions.sane_lists",
            "markdown.extensions.codehilite",
            "markdown.extensions.toc",
            "markdown.extensions.attr_list",
            "markdown.extensions.def_list",
            "markdown.extensions.footnotes",
            "markdown.extensions.md_in_html",
            "markdown.extensions.admonition",
        ],
        extension_configs={
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
            },
            'toc': {
                'permalink': True,
                'permalink_class': 'toc-link',
                'toc_depth': 3,
            }
        }
    )

    # Convert markdown to HTML
    html = md.convert(md_content)

    # Post-process to fix any internal links
    html = re.sub(r'href="\./([^"]+)\.md"', r'href="/docs/\1"', html)
    html = re.sub(r'href="([^"]+)\.md"', r'href="/docs/\1"', html)
    
    # Add IDs to headers for better navigation
    html = re.sub(
        r'<h([1-6])>(.+?)</h\1>',
        lambda m: f'<h{m.group(1)} id="{re.sub(r"[^\w\s-]", "", m.group(2).lower()).replace(" ", "-")}">{m.group(2)}</h{m.group(1)}>',
        html
    )

    return html


def get_doc_structure():
    """Get the documentation structure for navigation."""
    Path("docs")
    structure = {
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
    return structure


def render_doc_nav(current_path=None):
    """Render the documentation navigation sidebar."""
    structure = get_doc_structure()
    nav_items = []

    # Add navigation links at the top
    nav_items.append(
        fh.Div(
            fh.A(
                "← Back to App",
                href="/",
                cls="block px-3 py-2 text-green-600 hover:bg-green-50 rounded font-medium mb-2",
            ),
            fh.A(
                "← Documentation Home",
                href="/docs",
                cls="block px-3 py-2 text-blue-600 hover:bg-blue-50 rounded font-medium mb-4",
            ),
            cls="border-b border-gray-200 pb-4 mb-4",
        )
    )

    for section, items in structure.items():
        # Special styling for Quick Access section
        if section == "Quick Access":
            links = []
            for title, path in items:
                active = path == current_path
                icon = (
                    "🎓"
                    if "student" in path
                    else "👩‍🏫"
                    if "instructor" in path
                    else "⚙️"
                )
                links.append(
                    fh.Li(
                        fh.A(
                            f"{icon} {title}",
                            href=f"/docs/{path}",
                            cls=f"block w-full px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded font-medium {'bg-blue-100 text-blue-700' if active else ''}",
                        ),
                        cls="block mb-2",
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                    fh.Ul(*links, cls="list-none block"),
                    cls="mb-4 pb-4 border-b border-gray-200",
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
                                cls=f"block px-4 py-1 text-sm hover:bg-gray-100 {'bg-blue-50 text-blue-600' if active else ''}",
                            )
                        )
                    )
                section_items.append(
                    fh.Div(
                        fh.H4(
                            subsection,
                            cls="font-medium text-gray-700 px-3 py-1 text-sm",
                        ),
                        fh.Ul(*sub_links, cls="list-none space-y-1 ml-4"),
                        cls="mb-3",
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                    fh.Div(*section_items, cls="space-y-3"),
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
                            cls=f"block px-4 py-1 hover:bg-gray-100 {'bg-blue-50 text-blue-600' if active else ''}",
                        )
                    )
                )
            nav_items.append(
                fh.Div(
                    fh.H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                    fh.Ul(*links, cls="list-none space-y-1 block"),
                    cls="mb-4",
                )
            )

    return fh.Nav(
        fh.Div(*nav_items, cls="space-y-4"),
        cls="w-64 bg-white border-r border-gray-200 h-full overflow-y-auto p-4 flex-shrink-0",
    )


@rt("/docs")
def get(session):
    """Documentation home page."""
    return fh.Div(
        dynamic_header(session),
        fh.Div(
            render_doc_nav(),
            fh.Div(
                fh.H1("FeedForward Documentation", cls="text-3xl font-bold mb-4"),
                fh.P(
                    "Welcome to the FeedForward documentation. Select a topic from the navigation menu to get started.",
                    cls="text-lg text-gray-600 mb-6",
                ),
                fh.Div(
                    fh.H2("Quick Links", cls="text-2xl font-semibold mb-3"),
                    fh.Div(
                        fh.Div(
                            fh.H3("For Students", cls="text-xl font-semibold mb-2"),
                            fh.P("Learn how to submit work and view feedback", cls="text-gray-600 mb-3"),
                            fh.A(
                                "Get Started →",
                                href="/docs/user-guides/student/getting-started",
                                cls="text-blue-600 hover:underline font-medium",
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md border border-gray-100",
                        ),
                        fh.Div(
                            fh.H3("For Instructors", cls="text-xl font-semibold mb-2"),
                            fh.P("Create courses, assignments, and review feedback", cls="text-gray-600 mb-3"),
                            fh.A(
                                "Get Started →",
                                href="/docs/user-guides/instructor/course-management",
                                cls="text-blue-600 hover:underline font-medium",
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md border border-gray-100",
                        ),
                        fh.Div(
                            fh.H3("For Administrators", cls="text-xl font-semibold mb-2"),
                            fh.P("Configure and maintain your FeedForward instance", cls="text-gray-600 mb-3"),
                            fh.A(
                                "Get Started →",
                                href="/docs/user-guides/admin/initial-setup",
                                cls="text-blue-600 hover:underline font-medium",
                            ),
                            cls="bg-white p-6 rounded-lg shadow-md border border-gray-100",
                        ),
                        cls="grid grid-cols-1 md:grid-cols-3 gap-4",
                    ),
                ),
                cls="flex-1 p-8 overflow-y-auto",
            ),
            cls="flex h-screen overflow-hidden",
        ),
        page_footer(),
        cls="min-h-screen flex flex-col",
    )


@rt("/docs/{path:path}")
def get_doc_page(session, path: str):
    """Display a specific documentation page."""
    # Sanitize path to prevent directory traversal
    path = path.replace("..", "")

    # Load the markdown file
    doc_path = Path(f"docs/{path}.md")
    content = load_markdown_file(doc_path)

    if content is None:
        return fh.Div(
            dynamic_header(session),
            fh.Div(
                render_doc_nav(path),
                fh.Div(
                    fh.H1("Page Not Found", cls="text-3xl font-bold mb-4"),
                    fh.P(
                        f"The documentation page '{path}' could not be found.",
                        cls="text-gray-600",
                    ),
                    fh.A(
                        "← Back to Documentation",
                        href="/docs",
                        cls="text-blue-600 hover:underline",
                    ),
                    cls="flex-1 p-8",
                ),
                cls="flex h-screen overflow-hidden",
            ),
            page_footer(),
            cls="min-h-screen flex flex-col",
        )

    # Extract title from content (first H1)
    title_match = re.search(r"<h1>(.*?)</h1>", content)
    title = title_match.group(1) if title_match else "Documentation"

    return fh.Div(
        dynamic_header(session),
        fh.Div(
            render_doc_nav(path),
            fh.Div(
                fh.Div(fh.NotStr(content), cls="prose prose-lg max-w-none"),
                cls="flex-1 p-8 overflow-y-auto",
            ),
            cls="flex h-screen overflow-hidden",
        ),
        page_footer(),
        cls="min-h-screen flex flex-col",
        # Add comprehensive CSS for better markdown rendering
        style="""
            /* Base Typography */
            .prose {
                max-width: none;
                color: #1f2937;
                line-height: 1.75;
                font-size: 1rem;
            }
            
            /* Headings */
            .prose h1 { 
                font-size: 2.5rem; 
                font-weight: 700; 
                margin-bottom: 1.5rem;
                margin-top: 0;
                color: #111827;
                border-bottom: 3px solid #e5e7eb;
                padding-bottom: 0.75rem;
            }
            .prose h2 { 
                font-size: 2rem; 
                font-weight: 600; 
                margin-top: 3rem; 
                margin-bottom: 1.5rem;
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
            
            /* Paragraphs and Text */
            .prose p { 
                margin-bottom: 1.25rem; 
                line-height: 1.75;
                color: #374151;
            }
            .prose strong { 
                font-weight: 700;
                color: #111827;
            }
            .prose em { 
                font-style: italic; 
            }
            
            /* Lists */
            .prose ul { 
                list-style-type: disc; 
                padding-left: 1.5rem; 
                margin-bottom: 1.25rem;
                margin-top: 1.25rem;
            }
            .prose ol { 
                list-style-type: decimal; 
                padding-left: 1.5rem; 
                margin-bottom: 1.25rem;
                margin-top: 1.25rem;
            }
            .prose li { 
                margin-bottom: 0.5rem;
                line-height: 1.75;
            }
            .prose li > ul,
            .prose li > ol {
                margin-top: 0.5rem;
                margin-bottom: 0.5rem;
            }
            
            /* Links */
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
            
            /* Code */
            .prose code { 
                background-color: #f3f4f6; 
                color: #dc2626;
                padding: 0.125rem 0.375rem; 
                border-radius: 0.375rem; 
                font-size: 0.875rem;
                font-family: 'Consolas', 'Monaco', monospace;
                font-weight: 500;
            }
            .prose pre { 
                background-color: #1e293b; 
                color: #e2e8f0; 
                padding: 1.25rem; 
                border-radius: 0.5rem; 
                overflow-x: auto; 
                margin-bottom: 1.5rem;
                margin-top: 1.5rem;
                font-size: 0.875rem;
                line-height: 1.625;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .prose pre code { 
                background-color: transparent; 
                color: inherit;
                padding: 0;
                font-weight: normal;
            }
            
            /* Syntax Highlighting */
            .highlight pre {
                background-color: #1e293b !important;
            }
            .highlight .hll { background-color: #49483e }
            .highlight .c { color: #75715e } /* Comment */
            .highlight .err { color: #960050; background-color: #1e0010 } /* Error */
            .highlight .k { color: #66d9ef } /* Keyword */
            .highlight .l { color: #ae81ff } /* Literal */
            .highlight .n { color: #f8f8f2 } /* Name */
            .highlight .o { color: #f92672 } /* Operator */
            .highlight .p { color: #f8f8f2 } /* Punctuation */
            .highlight .s { color: #e6db74 } /* String */
            
            /* Blockquotes */
            .prose blockquote { 
                border-left: 4px solid #6366f1; 
                padding: 1rem 1.25rem;
                margin-left: 0;
                margin-right: 0;
                margin-bottom: 1.5rem;
                font-style: italic;
                background-color: #f9fafb;
                border-radius: 0 0.5rem 0.5rem 0;
                color: #4b5563;
            }
            .prose blockquote p {
                margin-bottom: 0;
            }
            
            /* Tables */
            .prose table { 
                width: 100%; 
                border-collapse: separate;
                border-spacing: 0;
                margin-bottom: 1.5rem;
                margin-top: 1.5rem;
                font-size: 0.9rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-radius: 0.5rem;
                overflow: hidden;
            }
            .prose th, .prose td { 
                padding: 0.75rem 1rem;
                text-align: left;
            }
            .prose th { 
                background-color: #f8fafc; 
                font-weight: 600;
                border-bottom: 2px solid #e5e7eb;
                color: #1f2937;
            }
            .prose td {
                border-bottom: 1px solid #f3f4f6;
            }
            .prose tbody tr:last-child td {
                border-bottom: none;
            }
            .prose tbody tr:hover {
                background-color: #f9fafb;
            }
            
            /* Callout Boxes */
            .callout {
                padding: 1rem 1.25rem;
                margin-bottom: 1.5rem;
                margin-top: 1.5rem;
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
            .prose .toc {
                background-color: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                padding: 1.25rem;
                margin-bottom: 2rem;
                margin-top: 1rem;
            }
            .prose .toc > ul {
                list-style: none;
                padding-left: 0;
                margin: 0;
            }
            .prose .toc ul ul {
                list-style: none;
                padding-left: 1.5rem;
                margin-top: 0.25rem;
            }
            .prose .toc li {
                margin-bottom: 0.5rem;
            }
            .prose .toc a {
                text-decoration: none;
                color: #6b7280;
                display: block;
                padding: 0.25rem 0;
                transition: all 0.2s;
                border-left: 2px solid transparent;
                padding-left: 0.5rem;
            }
            .prose .toc a:hover {
                color: #2563eb;
                border-left-color: #2563eb;
                background-color: #eff6ff;
            }
            
            /* Admonitions */
            .admonition {
                padding: 1rem 1.25rem;
                margin-bottom: 1.5rem;
                margin-top: 1.5rem;
                border-radius: 0.5rem;
                border-left: 4px solid #3b82f6;
                background-color: #eff6ff;
            }
            .admonition-title {
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #1e40af;
            }
            
            /* Definition Lists */
            .prose dl {
                margin-bottom: 1.5rem;
            }
            .prose dt {
                font-weight: 600;
                margin-bottom: 0.25rem;
                color: #1f2937;
            }
            .prose dd {
                margin-left: 1.5rem;
                margin-bottom: 0.75rem;
                color: #4b5563;
            }
            
            /* Horizontal Rules */
            .prose hr {
                border: 0;
                height: 2px;
                background-color: #e5e7eb;
                margin: 2rem 0;
            }
            
            /* Fix navigation layout */
            nav { display: block !important; }
            nav > div { display: block !important; }
            nav div { display: block !important; }
            nav ul {
                display: block !important;
                list-style: none !important;
                padding: 0 !important;
                margin: 0 !important;
                width: 100% !important;
            }
            nav li {
                display: block !important;
                list-style: none !important;
                margin: 0 !important;
                padding: 0 !important;
                width: 100% !important;
            }
            nav a {
                display: block !important;
                white-space: normal !important;
                word-wrap: break-word !important;
                text-decoration: none !important;
                width: 100% !important;
            }
            nav h3, nav h4 {
                display: block !important;
                margin-bottom: 0.5rem !important;
            }
            
            /* Spacing utilities */
            .space-y-1 > * { margin-top: 0 !important; margin-bottom: 0.25rem !important; }
            .space-y-3 > * { margin-top: 0 !important; margin-bottom: 0.75rem !important; }
            .space-y-4 > * { margin-top: 0 !important; margin-bottom: 1rem !important; }
            
            /* Print styles */
            @media print {
                .prose pre {
                    background-color: #f3f4f6;
                    color: #1f2937;
                    border: 1px solid #e5e7eb;
                }
            }
        """,
    )
