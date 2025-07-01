"""
Admin domain whitelist management routes
"""

from datetime import datetime

from fasthtml.common import *

from app import admin_required, rt
from app.models.config import DomainWhitelist, domain_whitelist
from app.models.user import Role
from app.utils.ui import action_button, dashboard_layout


@rt("/admin/domains")
@admin_required
def admin_domains_list(session):
    """Admin domain whitelist management view"""
    # Note: user variable removed as it's not used in this function

    # Get all domains from the whitelist
    all_domains = list(domain_whitelist())

    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/admin/dashboard", icon="←"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Admin actions
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Approve Instructors",
                    color="indigo",
                    href="/admin/instructors/approve",
                    icon="✓",
                ),
                action_button(
                    "Manage Users", color="teal", href="/admin/users", icon="👥"
                ),
                action_button(
                    "System Settings", color="indigo", href="/admin/settings", icon="⚙️"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Domain whitelist management
    main_content = Div(
        H1(
            "Domain Whitelist Management", cls="text-3xl font-bold text-indigo-900 mb-6"
        ),
        P(
            "Configure which domains are allowed for instructor registration and whether they're auto-approved.",
            cls="text-gray-600 mb-8",
        ),
        # Add new domain form
        Div(
            H2("Add New Domain", cls="text-2xl font-bold text-indigo-900 mb-4"),
            Form(
                Div(
                    Div(
                        Label(
                            "Domain",
                            for_="domain",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "e.g. 'curtin.edu.au' (without 'http://' or '@')",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            id="domain",
                            type="text",
                            placeholder="Domain name",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-4 w-full",
                    ),
                    Div(
                        Div(
                            Input(
                                type="checkbox",
                                id="auto_approve",
                                cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Auto-approve instructors from this domain",
                                for_="auto_approve",
                                cls="ml-2 block text-indigo-900 font-medium",
                            ),
                            cls="flex items-center",
                        ),
                        cls="mb-6",
                    ),
                    Div(
                        Button(
                            "Add Domain",
                            type="submit",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="mb-4",
                    ),
                    Span(id="domain_result", cls="block text-center"),
                    cls="flex flex-wrap",
                ),
                hx_post="/admin/domains/add",
                hx_target="#domain_result",
                hx_swap="innerHTML",
                cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-8",
            ),
        ),
        # Domain list
        Div(
            H2("Current Domains", cls="text-2xl font-bold text-indigo-900 mb-4"),
            # Check if there are domains
            (
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th(
                                    "Domain",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Auto-approve",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Actions",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                            ),
                            cls="bg-indigo-50",
                        ),
                        Tbody(
                            *(
                                Tr(
                                    Td(domain["domain"], cls="py-4 px-6"),
                                    Td(
                                        Span(
                                            "✅ Yes"
                                            if domain["auto_approve_instructor"]
                                            else "❌ No",
                                            cls="px-3 py-1 rounded-full text-sm "
                                            + (
                                                "bg-green-100 text-green-800"
                                                if domain["auto_approve_instructor"]
                                                else "bg-red-100 text-red-800"
                                            ),
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    Td(
                                        Div(
                                            Button(
                                                "Toggle Auto-approve",
                                                cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                                                hx_post=f"/admin/domains/toggle/{domain['id']}",
                                                hx_target="closest tr",
                                                hx_swap="outerHTML",
                                            ),
                                            Button(
                                                "Delete",
                                                cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                hx_post=f"/admin/domains/delete/{domain['id']}",
                                                hx_target="closest tr",
                                                hx_swap="outerHTML",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for domain in all_domains
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                )
            )
            if all_domains
            else Div(
                P(
                    "No domains in the whitelist. Add some domains to allow instructor registration.",
                    cls="text-gray-500 italic text-center py-8",
                ),
                cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
            ),
            cls="mb-8",
        ),
        # Back button
        Div(
            action_button(
                "Back to Dashboard", color="gray", href="/admin/dashboard", icon="←"
            ),
            cls="mt-4",
        ),
    )

    # Use the dashboard layout with our components
    return Titled(
        "Domain Whitelist | FeedForward",
        dashboard_layout(
            "Domain Whitelist", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


@rt("/admin/domains/add")
@admin_required
def admin_domain_add(session, domain: str, auto_approve: bool = False):
    """Add domain to whitelist POST handler"""
    # Basic validation
    if not domain:
        return Div(P("Domain name is required", cls="text-red-500"))

    # Clean up domain
    domain = domain.strip().lower()

    # Remove any protocol or @ symbol
    domain = domain.replace("http://", "").replace("https://", "").replace("@", "")

    # Check if domain already exists
    for existing in domain_whitelist.select():
        if existing["domain"] == domain:
            return Div(
                P(
                    f"Domain '{domain}' already exists in the whitelist",
                    cls="text-amber-500",
                )
            )

    try:
        # Get next available ID
        next_id = 1
        existing_ids = [d["id"] for d in domain_whitelist.select()]
        if existing_ids:
            next_id = max(existing_ids) + 1

        # Create timestamp
        now = datetime.now().isoformat()

        # Create new domain entry
        new_domain = DomainWhitelist(
            id=next_id,
            domain=domain,
            auto_approve_instructor=auto_approve,
            created_at=now,
            updated_at=now,
        )

        # Add to database
        domain_whitelist.insert(new_domain)

        # Return success message with page reload
        return Div(
            P(f"Added domain '{domain}' to the whitelist", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        )
    except Exception as e:
        # Return error message
        return Div(P(f"Error adding domain: {e!s}", cls="text-red-500"))


@rt("/admin/domains/toggle/{id}")
@admin_required
def admin_domain_toggle(session, id: int):
    """Toggle domain auto-approve POST handler"""
    try:
        # Find the domain
        domain_record = None
        for d in domain_whitelist.select():
            if d["id"] == id:
                domain_record = d
                break

        if not domain_record:
            return "Domain not found"

        # Toggle auto-approve
        domain_record["auto_approve_instructor"] = not domain_record[
            "auto_approve_instructor"
        ]

        # Update timestamp
        domain_record["updated_at"] = datetime.now().isoformat()

        # Save changes
        domain_whitelist.update(domain_record)

        # Return updated row
        return Tr(
            Td(domain_record["domain"], cls="py-4 px-6"),
            Td(
                Span(
                    "✅ Yes"
                    if domain_record["auto_approve_instructor"]
                    else "❌ No",
                    cls="px-3 py-1 rounded-full text-sm "
                    + (
                        "bg-green-100 text-green-800"
                        if domain_record["auto_approve_instructor"]
                        else "bg-red-100 text-red-800"
                    ),
                ),
                cls="py-4 px-6",
            ),
            Td(
                Div(
                    Button(
                        "Toggle Auto-approve",
                        cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                        hx_post=f"/admin/domains/toggle/{domain_record['id']}",
                        hx_target="closest tr",
                        hx_swap="outerHTML",
                    ),
                    Button(
                        "Delete",
                        cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                        hx_post=f"/admin/domains/delete/{domain_record['id']}",
                        hx_target="closest tr",
                        hx_swap="outerHTML",
                    ),
                    cls="flex",
                ),
                cls="py-4 px-6",
            ),
        )
    except Exception as e:
        return Div(P(f"Error toggling domain: {e!s}", cls="text-red-500"))


@rt("/admin/domains/delete/{id}")
@admin_required
def admin_domain_delete(session, id: int):
    """Delete domain from whitelist POST handler"""
    try:
        # Find and delete the domain
        domain_record = None
        for d in domain_whitelist.select():
            if d["id"] == id:
                domain_record = d
                break

        if not domain_record:
            return "Domain not found"

        # Delete from database
        domain_whitelist.delete(id)

        # Return empty (removes the row)
        return ""
    except Exception as e:
        return Div(P(f"Error deleting domain: {e!s}", cls="text-red-500"))
