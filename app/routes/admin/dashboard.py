"""
Admin dashboard routes
"""

from fasthtml import common as fh

from app import admin_required, rt
from app.models.user import Role, users
from app.utils import analyser_client
from app.utils.ui import action_button, card, dashboard_layout


def _signal_services_card():
    """Dashboard summary card: how many lens analysers are currently reachable."""
    services = analyser_client.service_health()
    up = sum(1 for s in services if s["ok"])
    total = len(services)
    colour = (
        "text-green-600"
        if up == total
        else ("text-amber-600" if up else "text-red-600")
    )
    return card(
        fh.Div(
            fh.H3(f"{up}/{total}", cls="text-4xl font-bold text-indigo-700 mb-2"),
            fh.P("Signal Services", cls="text-gray-600"),
            fh.P(
                "all analysers reachable"
                if up == total
                else f"{total - up} analyser(s) unreachable",
                cls=f"text-xs {colour} mt-2",
            ),
            fh.A(
                "Details →",
                href="/admin/signal-services",
                cls="text-xs text-indigo-600 hover:text-indigo-800 mt-2 inline-block",
            ),
            cls="text-center p-4",
        ),
        padding=0,
    )


@rt("/admin/dashboard")
@admin_required
def admin_dashboard(session):
    """Admin dashboard view"""
    # Get current user
    user = users[session["auth"]]

    # Sidebar content
    sidebar_content = fh.Div(
        # User welcome card
        fh.Div(
            fh.H3(
                "Welcome, " + user.name,
                cls="text-xl font-semibold text-indigo-900 mb-2",
            ),
            fh.P("Admin Account", cls="text-gray-600 mb-4"),
            fh.Div(
                # System stats summary
                fh.Div(
                    fh.Div("3", cls="text-indigo-700 font-bold"),
                    fh.P("Total Users", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2",
                ),
                # Pending approvals summary
                fh.Div(
                    fh.Div("0", cls="text-indigo-700 font-bold"),
                    fh.P("Pending Approvals", cls="text-gray-600"),
                    cls="flex items-center space-x-2",
                ),
                cls="space-y-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Quick actions section
        fh.Div(
            fh.H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Approve Instructors",
                    color="indigo",
                    href="/admin/instructors/approve",
                    icon="✓",
                ),
                action_button(
                    "Manage Instructors",
                    color="teal",
                    href="/admin/instructors",
                    icon="👨‍🏫",
                ),
                action_button(
                    "Manage Users", color="teal", href="/admin/users", icon="👥"
                ),
                action_button(
                    "Domain Whitelist", color="amber", href="/admin/domains", icon="🔑"
                ),
                action_button(
                    "System Settings", color="indigo", href="/admin/settings", icon="⚙️"
                ),
                action_button(
                    "LLM Usage & Cost", color="amber", href="/admin/usage", icon="💰"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = fh.Div(
        # System stats
        fh.Div(
            fh.Div(
                # Users card
                card(
                    fh.Div(
                        fh.H3("3", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        fh.P("Total Users", cls="text-gray-600"),
                        fh.P("Last updated today", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Courses card
                card(
                    fh.Div(
                        fh.H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        fh.P("Active Courses", cls="text-gray-600"),
                        fh.P(
                            "Across all instructors", cls="text-xs text-gray-500 mt-2"
                        ),
                        cls="text-center p-4",
                    ),
                    padding=0,
                ),
                # Signal-services health card (live probe of the lens analysers)
                _signal_services_card(),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
            )
        ),
        # User Management
        fh.Div(
            fh.H2("User Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
            fh.Div(
                fh.Div(
                    fh.H3(
                        "Instructor Approval",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    fh.P(
                        "No pending instructor approvals.", cls="text-gray-500 italic"
                    ),
                    fh.Div(
                        action_button(
                            "View All",
                            color="indigo",
                            href="/admin/instructors/approve",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                ),
                fh.Div(
                    fh.H3(
                        "Recent Users", cls="text-lg font-semibold text-indigo-800 mb-4"
                    ),
                    fh.P("3 users registered in the system.", cls="text-gray-600 mb-2"),
                    fh.Div(
                        action_button(
                            "Manage Users",
                            color="teal",
                            href="/admin/users",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                cls="mb-8",
            ),
        ),
        # System Configuration
        fh.Div(
            fh.H2(
                "System Configuration", cls="text-2xl font-bold text-indigo-900 mb-6"
            ),
            fh.Div(
                fh.Div(
                    fh.H3(
                        "AI Models", cls="text-lg font-semibold text-indigo-800 mb-4"
                    ),
                    fh.P(
                        "Configure the AI models used for feedback generation.",
                        cls="text-gray-600 mb-2",
                    ),
                    fh.Div(
                        action_button(
                            "Configure Models",
                            color="indigo",
                            href="/admin/ai-models",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4",
                ),
                fh.Div(
                    fh.H3(
                        "Feedback Settings",
                        cls="text-lg font-semibold text-indigo-800 mb-4",
                    ),
                    fh.P(
                        "Adjust global feedback settings and templates.",
                        cls="text-gray-600 mb-2",
                    ),
                    fh.Div(
                        action_button(
                            "Adjust Settings",
                            color="teal",
                            href="/admin/feedback-settings",
                            size="small",
                        ),
                        cls="mt-4",
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                cls="mb-8",
            ),
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Admin Dashboard", sidebar_content, main_content, user_role=Role.ADMIN
    )


@rt("/admin/signal-services")
@admin_required
def admin_signal_services(session):
    """Live health of the lens analyser sidecars (ADR 012).

    Probes each analyser's /health so an operator can see, at a glance, whether
    signals will be extracted — and which sidecar to start if not.
    """
    services = analyser_client.service_health()

    rows = []
    for s in services:
        if s["ok"]:
            status = fh.Span("● reachable", cls="text-sm font-semibold text-green-600")
            detail = fh.Span(
                f"v{s['version']}" if s["version"] else "running",
                cls="text-xs text-gray-500",
            )
        else:
            status = fh.Span("● down", cls="text-sm font-semibold text-red-600")
            detail = fh.Span(s["error"] or "unreachable", cls="text-xs text-gray-500")
        rows.append(
            fh.Div(
                fh.Div(
                    fh.Span(s["name"], cls="font-medium text-gray-900"),
                    fh.Span(s["role"], cls="text-xs text-gray-500 ml-2"),
                    cls="flex-1",
                ),
                fh.Div(
                    fh.Code(s["url"], cls="text-xs text-gray-400 mr-4"),
                    detail,
                    status,
                    cls="flex items-center gap-3",
                ),
                cls="flex items-center justify-between py-3 border-b border-gray-100 last:border-0",
            )
        )

    main_content = fh.Div(
        fh.Div(
            fh.H1("Signal Services", cls="text-2xl font-bold text-gray-900"),
            fh.A(
                "← Back to Dashboard",
                href="/admin/dashboard",
                cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        fh.P(
            "Lens analyser sidecars that produce deterministic signals (ADR 012). "
            "When one is down, its signals are silently skipped — start it and "
            "re-run extraction. Override a service URL with its environment "
            "variable (DOCUMENT_ANALYSER_URL / CODE_ANALYSER_URL / CITE_SIGHT_URL).",
            cls="text-sm text-gray-500 mb-4",
        ),
        fh.Div(*rows, cls="bg-white p-6 rounded-lg shadow mb-6"),
        fh.P(
            "Start all three locally with: ",
            fh.Code("make sidecars", cls="text-xs bg-gray-100 px-2 py-1 rounded"),
            cls="text-sm text-gray-500",
        ),
        cls="max-w-3xl mx-auto px-4 py-6",
    )
    return dashboard_layout(
        "Signal Services | FeedForward",
        fh.Div(),
        main_content,
        user_role=Role.ADMIN,
        current_path="/admin/signal-services",
    )


@rt("/admin/usage")
@admin_required
def admin_usage(session):
    """LLM token usage and estimated cost, per course (Phase 3).

    'What does this cost per cohort' — totals are summed from the per-run token
    counts and cost captured on model_runs during feedback generation.
    """
    from app.services import usage_report

    rows = usage_report.usage_by_course()
    grand = {
        "llm_runs": sum(r["llm_runs"] for r in rows),
        "input_tokens": sum(r["input_tokens"] for r in rows),
        "output_tokens": sum(r["output_tokens"] for r in rows),
        "cost_usd": round(sum(r["cost_usd"] for r in rows), 4),
    }

    def _num(v):
        return fh.Span(f"{v:,}", cls="text-sm text-gray-700 font-mono tabular-nums")

    header = fh.Div(
        *[
            fh.Span(label, cls="text-xs font-semibold text-gray-500 uppercase")
            for label in ("Course", "Runs", "Input tok", "Output tok", "Cost (USD)")
        ],
        cls="grid grid-cols-5 gap-2 pb-2 border-b border-gray-200",
    )

    body_rows = [
        fh.Div(
            fh.Span(
                f"{r['course_code']} · {r['course_title']}",
                cls="text-sm text-gray-900",
            ),
            _num(r["llm_runs"]),
            _num(r["input_tokens"]),
            _num(r["output_tokens"]),
            fh.Span(
                f"${r['cost_usd']:.4f}",
                cls="text-sm text-gray-900 font-mono tabular-nums",
            ),
            cls="grid grid-cols-5 gap-2 py-2 border-b border-gray-100 last:border-0",
        )
        for r in rows
    ] or [fh.P("No feedback has been generated yet.", cls="text-gray-500 py-4")]

    grand_row = (
        fh.Div(
            fh.Span("All courses", cls="text-sm font-semibold text-gray-900"),
            _num(grand["llm_runs"]),
            _num(grand["input_tokens"]),
            _num(grand["output_tokens"]),
            fh.Span(
                f"${grand['cost_usd']:.4f}",
                cls="text-sm font-semibold text-gray-900 font-mono tabular-nums",
            ),
            cls="grid grid-cols-5 gap-2 pt-3 mt-1 border-t-2 border-gray-300",
        )
        if rows
        else fh.Div()
    )

    main_content = fh.Div(
        fh.Div(
            fh.H1("LLM Usage & Cost", cls="text-2xl font-bold text-gray-900"),
            fh.A(
                "← Back to Dashboard",
                href="/admin/dashboard",
                cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        fh.P(
            "Token usage and estimated cost from AI feedback generation, summed "
            "per course. Cost is LiteLLM's estimate from each provider's price "
            "map; providers that don't report usage contribute zero. Signal-engine "
            "and mock runs are excluded.",
            cls="text-sm text-gray-500 mb-4",
        ),
        fh.Div(
            header, *body_rows, grand_row, cls="bg-white p-6 rounded-lg shadow mb-6"
        ),
        cls="max-w-3xl mx-auto px-4 py-6",
    )
    return dashboard_layout(
        "LLM Usage | FeedForward",
        fh.Div(),
        main_content,
        user_role=Role.ADMIN,
        current_path="/admin/usage",
    )
