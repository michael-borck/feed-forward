"""
In-app documentation viewer for FeedForward.
Renders markdown documentation files directly in the application.
"""

import re
from pathlib import Path

import markdown
from fasthtml.common import *


def setup_routes(app, rt, db, User):
    """Set up documentation routes."""

    # @lru_cache(maxsize=128)  # Disabled for development
    def load_markdown_file(filepath):
        """Load and parse a markdown file, with caching."""
        try:
            with open(filepath) as f:
                content = f.read()

            # Remove Jekyll front matter
            content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

            # Convert markdown to HTML (basic conversion)
            # In production, consider using a proper markdown parser
            content = convert_markdown_to_html(content)

            return content
        except FileNotFoundError:
            return None

    def convert_markdown_to_html(md_content):
        """Convert markdown to HTML using the markdown library."""
        # Pre-process Jekyll-specific syntax
        # Convert Jekyll TOC syntax to Python markdown TOC syntax
        md_content = re.sub(r'{:\s*\.no_toc\s*(?:\.text-delta)?\s*}', '', md_content)
        md_content = re.sub(r'1\.\s+TOC\s*\n\s*{:toc}', '[TOC]', md_content)

        # Remove other Jekyll-specific class assignments
        md_content = re.sub(r'{:\s*\.[^}]+}', '', md_content)

        # Configure markdown extensions
        md = markdown.Markdown(extensions=[
            'markdown.extensions.fenced_code',
            'markdown.extensions.tables',
            'markdown.extensions.nl2br',
            'markdown.extensions.sane_lists',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc'
        ])

        # Convert markdown to HTML
        html = md.convert(md_content)

        # Post-process to fix any internal links
        # Convert .md links to proper routes
        html = re.sub(r'href="\./([^"]+)\.md"', r'href="/docs/\1"', html)
        html = re.sub(r'href="([^"]+)\.md"', r'href="/docs/\1"', html)

        return html

    def get_doc_structure():
        """Get the documentation structure for navigation."""
        docs_path = Path('docs')
        structure = {
            'Quick Access': [
                ('Student Guide', 'user-guides/student/index'),
                ('Instructor Guide', 'user-guides/instructor/index'),
                ('Admin Guide', 'user-guides/admin/index'),
            ],
            'Getting Started': [
                ('Installation', 'getting-started/installation'),
                ('Configuration', 'getting-started/configuration'),
                ('Quick Start', 'getting-started/quick-start'),
            ],
            'User Guides': {
                'Students': [
                    ('Overview', 'user-guides/student/index'),
                    ('Getting Started', 'user-guides/student/getting-started'),
                    ('Submitting Work', 'user-guides/student/submissions'),
                    ('Viewing Feedback', 'user-guides/student/viewing-feedback'),
                    ('Tracking Progress', 'user-guides/student/progress'),
                ],
                'Instructors': [
                    ('Overview', 'user-guides/instructor/index'),
                    ('Course Management', 'user-guides/instructor/course-management'),
                    ('Creating Assignments', 'user-guides/instructor/assignments'),
                    ('Using Rubrics', 'user-guides/instructor/rubrics'),
                    ('Managing Students', 'user-guides/instructor/student-invites'),
                    ('Reviewing Feedback', 'user-guides/instructor/feedback-review'),
                ],
                'Administrators': [
                    ('Overview', 'user-guides/admin/index'),
                    ('Initial Setup', 'user-guides/admin/initial-setup'),
                    ('User Management', 'user-guides/admin/user-management'),
                    ('AI Configuration', 'user-guides/admin/ai-configuration'),
                    ('Maintenance', 'user-guides/admin/maintenance'),
                ],
            },
            'Deployment': [
                ('Requirements', 'deployment/requirements'),
                ('Installation', 'deployment/installation'),
                ('Configuration', 'deployment/configuration'),
                ('Troubleshooting', 'deployment/troubleshooting'),
            ],
            'Technical': [
                ('Architecture', 'technical/architecture'),
                ('Database Schema', 'technical/database-schema'),
                ('API Reference', 'technical/api-reference'),
                ('Privacy & Security', 'technical/privacy-security'),
            ],
        }
        return structure

    def render_doc_nav(current_path=None):
        """Render the documentation navigation sidebar."""
        structure = get_doc_structure()
        nav_items = []

        # Add navigation links at the top
        nav_items.append(
            Div(
                A(
                    "← Back to App",
                    href="/",
                    cls="block px-3 py-2 text-green-600 hover:bg-green-50 rounded font-medium mb-2"
                ),
                A(
                    "← Documentation Home",
                    href="/docs",
                    cls="block px-3 py-2 text-blue-600 hover:bg-blue-50 rounded font-medium mb-4"
                ),
                cls="border-b border-gray-200 pb-4 mb-4"
            )
        )

        for section, items in structure.items():
            # Special styling for Quick Access section
            if section == 'Quick Access':
                links = []
                for title, path in items:
                    active = path == current_path
                    icon = "🎓" if "student" in path else "👩‍🏫" if "instructor" in path else "⚙️"
                    links.append(
                        Li(
                            A(
                                f"{icon} {title}",
                                href=f'/docs/{path}',
                                cls=f"block w-full px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded font-medium {'bg-blue-100 text-blue-700' if active else ''}"
                            ),
                            cls="block mb-2"
                        )
                    )
                nav_items.append(
                    Div(
                        H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                        Ul(*links, cls="list-none block"),
                        cls="mb-4 pb-4 border-b border-gray-200"
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
                            Li(
                                A(
                                    title,
                                    href=f'/docs/{path}',
                                    cls=f"block px-4 py-1 text-sm hover:bg-gray-100 {'bg-blue-50 text-blue-600' if active else ''}"
                                )
                            )
                        )
                    section_items.append(
                        Div(
                            H4(subsection, cls="font-medium text-gray-700 px-3 py-1 text-sm"),
                            Ul(*sub_links, cls="list-none space-y-1 ml-4"),
                            cls="mb-3"
                        )
                    )
                nav_items.append(
                    Div(
                        H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                        Div(
                            *section_items,
                            cls="space-y-3"
                        ),
                        cls="mb-4"
                    )
                )
            else:
                # Simple list
                links = []
                for title, path in items:
                    active = path == current_path
                    links.append(
                        Li(
                            A(
                                title,
                                href=f'/docs/{path}',
                                cls=f"block px-4 py-1 hover:bg-gray-100 {'bg-blue-50 text-blue-600' if active else ''}"
                            )
                        )
                    )
                nav_items.append(
                    Div(
                        H3(section, cls="font-semibold text-gray-900 px-3 py-2"),
                        Ul(*links, cls="list-none space-y-1 block"),
                        cls="mb-4"
                    )
                )

        return Nav(
            Div(
                *nav_items,
                cls="space-y-4"
            ),
            cls="w-64 bg-white border-r border-gray-200 h-full overflow-y-auto p-4 flex-shrink-0"
        )

    @rt('/docs')
    def get(session):
        """Documentation home page."""
        return Titled(
            "Documentation",
            Div(
                render_doc_nav(),
                Div(
                    H1("FeedForward Documentation", cls="text-3xl font-bold mb-4"),
                    P("Welcome to the FeedForward documentation. Select a topic from the navigation menu to get started.",
                      cls="text-lg text-gray-600 mb-6"),

                    Div(
                        H2("Quick Links", cls="text-2xl font-semibold mb-3"),
                        Div(
                            Card(
                                H3("For Students", cls="text-xl font-semibold mb-2"),
                                P("Learn how to submit work and view feedback"),
                                A("Get Started →", href="/docs/user-guides/student/getting-started",
                                  cls="text-blue-600 hover:underline")
                            ),
                            Card(
                                H3("For Instructors", cls="text-xl font-semibold mb-2"),
                                P("Create courses, assignments, and review feedback"),
                                A("Get Started →", href="/docs/user-guides/instructor/course-management",
                                  cls="text-blue-600 hover:underline")
                            ),
                            Card(
                                H3("For Administrators", cls="text-xl font-semibold mb-2"),
                                P("Configure and maintain your FeedForward instance"),
                                A("Get Started →", href="/docs/user-guides/admin/initial-setup",
                                  cls="text-blue-600 hover:underline")
                            ),
                            cls="grid grid-cols-1 md:grid-cols-3 gap-4"
                        )
                    ),
                    cls="flex-1 p-8 overflow-y-auto"
                ),
                cls="flex h-screen overflow-hidden"
            )
        )

    @rt('/docs/{path:path}')
    def get_doc_page(session, path: str):
        """Display a specific documentation page."""
        # Sanitize path to prevent directory traversal
        path = path.replace('..', '')

        # Load the markdown file
        doc_path = Path(f'docs/{path}.md')
        content = load_markdown_file(doc_path)

        if content is None:
            return Titled(
                "Documentation Not Found",
                Div(
                    render_doc_nav(path),
                    Div(
                        H1("Page Not Found", cls="text-3xl font-bold mb-4"),
                        P(f"The documentation page '{path}' could not be found.", cls="text-gray-600"),
                        A("← Back to Documentation", href="/docs", cls="text-blue-600 hover:underline"),
                        cls="flex-1 p-8"
                    ),
                    cls="flex h-screen overflow-hidden"
                )
            )

        # Extract title from content (first H1)
        title_match = re.search(r'<h1>(.*?)</h1>', content)
        title = title_match.group(1) if title_match else "Documentation"

        return Titled(
            title,
            Div(
                render_doc_nav(path),
                Div(
                    Div(
                        NotStr(content),
                        cls="prose prose-lg max-w-none"
                    ),
                    cls="flex-1 p-8 overflow-y-auto"
                ),
                cls="flex h-screen overflow-hidden"
            ),
            # Add some CSS for better markdown rendering
            Style("""
                .prose h1 { font-size: 2.25rem; font-weight: 700; margin-bottom: 1rem; }
                .prose h2 { font-size: 1.875rem; font-weight: 600; margin-top: 2rem; margin-bottom: 1rem; }
                .prose h3 { font-size: 1.5rem; font-weight: 600; margin-top: 1.5rem; margin-bottom: 0.75rem; }
                .prose p { margin-bottom: 1rem; line-height: 1.75; }
                .prose ul { list-style-type: disc; padding-left: 2rem; margin-bottom: 1rem; }
                .prose ol { list-style-type: decimal; padding-left: 2rem; margin-bottom: 1rem; }
                .prose li { margin-bottom: 0.5rem; }
                .prose code { background-color: #f3f4f6; padding: 0.125rem 0.25rem; border-radius: 0.25rem; font-size: 0.875rem; }
                .prose pre { background-color: #1f2937; color: white; padding: 1rem; border-radius: 0.5rem; overflow-x: auto; margin-bottom: 1rem; }
                .prose pre code { background-color: transparent; padding: 0; }
                .prose a { color: #2563eb; text-decoration: underline; }
                .prose a:hover { color: #1d4ed8; }
                .prose strong { font-weight: 600; }
                .prose em { font-style: italic; }
                .prose blockquote { border-left: 4px solid #e5e7eb; padding-left: 1rem; margin-left: 0; font-style: italic; }
                .prose table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
                .prose th, .prose td { border: 1px solid #e5e7eb; padding: 0.5rem; }
                .prose th { background-color: #f9fafb; font-weight: 600; }
                /* Table of Contents styling */
                .prose .toc { 
                    background-color: #f9fafb; 
                    border: 1px solid #e5e7eb; 
                    border-radius: 0.5rem; 
                    padding: 1rem; 
                    margin-bottom: 2rem; 
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
                    margin-bottom: 0.25rem; 
                }
                .prose .toc a { 
                    text-decoration: none; 
                    color: #4b5563; 
                }
                .prose .toc a:hover { 
                    color: #2563eb; 
                    text-decoration: underline; 
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
                /* Ensure vertical stacking */
                .list-none { 
                    display: block !important;
                }
                .list-none li {
                    display: block !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                /* Remove any flex or inline styles that might be inherited */
                nav * {
                    flex-direction: column !important;
                }
                nav ul li {
                    display: list-item !important;
                    float: none !important;
                    clear: both !important;
                }
                .space-y-1 > * { margin-top: 0 !important; margin-bottom: 0.25rem !important; }
                .space-y-3 > * { margin-top: 0 !important; margin-bottom: 0.75rem !important; }
                .space-y-4 > * { margin-top: 0 !important; margin-bottom: 1rem !important; }
            """)
        )
