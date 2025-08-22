"""
Admin AI models management routes
"""

from fasthtml.common import *

from app import admin_required, rt
from app.models.config import ai_models
from app.models.user import Role
from app.utils.ui import action_button, dashboard_layout


@rt("/admin/ai-models")
@admin_required
def admin_models_list(session):
    """Admin AI models management list view"""
    # Note: user variable removed as it's not used in this function

    # Get all AI models
    model_list = list(ai_models())

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
                    "Add New Model",
                    color="indigo",
                    href="/admin/ai-models/new",
                    icon="+",
                ),
                action_button(
                    "System Settings", color="teal", href="/admin/settings", icon="⚙️"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Model stats section
        Div(
            H3("AI Model Stats", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                Div(
                    P(f"Total Models: {len(model_list)}", cls="text-gray-700 mb-1"),
                    P(
                        f"Active Models: {sum(1 for m in model_list if m.active)}",
                        cls="text-green-700 mb-1",
                    ),
                    P(
                        f"System Models: {sum(1 for m in model_list if m.owner_type == 'system')}",
                        cls="text-indigo-700 mb-1",
                    ),
                    P(
                        f"Instructor Models: {sum(1 for m in model_list if m.owner_type == 'instructor')}",
                        cls="text-teal-700",
                    ),
                ),
                cls="space-y-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - AI Model management
    main_content = Div(
        H1("AI Model Management", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P(
            "Configure AI models available for feedback generation.",
            cls="text-gray-600 mb-8",
        ),
        # AI Model list
        Div(
            H2("Available Models", cls="text-2xl font-bold text-indigo-900 mb-4"),
            Div(
                # Explanatory info
                Div(
                    H3(
                        "Model Configuration",
                        cls="text-lg font-semibold text-indigo-800 mb-2",
                    ),
                    P(
                        "Models can be provided by the system or configured by individual instructors.",
                        cls="text-gray-600 mb-1",
                    ),
                    P(
                        "System models are available to all instructors, while instructor models are private.",
                        cls="text-gray-600 mb-1",
                    ),
                    cls="bg-indigo-50 p-4 rounded-lg mb-6",
                ),
                # Add New Model button
                Div(
                    action_button(
                        "Add New Model",
                        color="indigo",
                        href="/admin/ai-models/new",
                        icon="+",
                        size="regular",
                    ),
                    cls="mb-6",
                ),
                # Model table
                (
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    Th(
                                        "Name",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Provider",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Model ID",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Owner",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    Th(
                                        "Status",
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
                                        Td(model.name, cls="py-4 px-6"),
                                        Td(model.provider, cls="py-4 px-6"),
                                        Td(model.model_id, cls="py-4 px-6"),
                                        Td(
                                            Span(
                                                "System"
                                                if model.owner_type == "system"
                                                else "Instructor",
                                                cls="px-3 py-1 rounded-full text-xs "
                                                + (
                                                    "bg-indigo-100 text-indigo-800"
                                                    if model.owner_type == "system"
                                                    else "bg-teal-100 text-teal-800"
                                                ),
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Span(
                                                "Active"
                                                if model.active
                                                else "Inactive",
                                                cls="px-3 py-1 rounded-full text-xs "
                                                + (
                                                    "bg-green-100 text-green-800"
                                                    if model.active
                                                    else "bg-gray-100 text-gray-800"
                                                ),
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                        Td(
                                            Div(
                                                A(
                                                    "Edit",
                                                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                                    href=f"/admin/ai-models/edit/{model.id}",
                                                ),
                                                Button(
                                                    "Delete",
                                                    cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                                    hx_delete=f"/admin/ai-models/{model.id}",
                                                    hx_confirm=f"Are you sure you want to delete the model '{model.name}'?",
                                                    hx_target="closest tr",
                                                    hx_swap="outerHTML",
                                                ),
                                                cls="flex",
                                            ),
                                            cls="py-4 px-6",
                                        ),
                                    )
                                    for model in model_list
                                )
                            ),
                            cls="w-full",
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                    )
                )
                if model_list
                else Div(
                    P(
                        "No AI models configured. Add your first model to start generating feedback.",
                        cls="text-gray-500 italic text-center py-8",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
                ),
                cls="mb-8",
            ),
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
        "AI Model Management | FeedForward",
        dashboard_layout(
            "AI Model Management", sidebar_content, main_content, user_role=Role.ADMIN
        ),
    )


# Placeholder for other AI model routes to be added
# Note: Due to the large size of the AI model management code,
# this is a simplified version. The full implementation would include:
# - admin_models_new() - new model form
# - admin_models_create() - create model POST handler
# - admin_models_edit() - edit model form
# - admin_models_update() - update model POST handler
# - admin_models_test() - test model API
# - admin_models_delete() - delete model handler


@rt("/admin/ai-models/new")
@admin_required
def admin_models_new(session):
    """Placeholder for new AI model form"""
    return Div(P("AI Model creation form - To be implemented"))


@rt("/admin/ai-models/create")
@admin_required
def admin_models_create(session):
    """Placeholder for create AI model handler"""
    return Div(P("AI Model creation handler - To be implemented"))


@rt("/admin/ai-models/edit/{id}")
@admin_required
def admin_models_edit_form(session, id: int):
    """Placeholder for edit AI model form"""
    return Div(P(f"AI Model {id} edit form - To be implemented"))


@rt("/admin/ai-models/edit/{id}")
@admin_required
def admin_models_edit_update(session, id: int):
    """Placeholder for update AI model handler"""
    return Div(P(f"AI Model {id} update handler - To be implemented"))


@rt("/admin/ai-models/test")
@admin_required
def admin_models_test(session):
    """Placeholder for test AI model API"""
    return Div(P("AI Model test API - To be implemented"))


@rt("/admin/ai-models/{id}")
@admin_required
def admin_models_delete(session, id: int):
    """Placeholder for delete AI model handler"""
    return Div(P(f"AI Model {id} delete handler - To be implemented"))
