"""
Admin AI models management routes
"""

from fasthtml import common as fh

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
    sidebar_content = fh.Div(
        # Quick navigation
        fh.Div(
            fh.H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Dashboard", color="gray", href="/admin/dashboard", icon="←"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Admin actions
        fh.Div(
            fh.H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
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
        fh.Div(
            fh.H3("AI Model Stats", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
                fh.Div(
                    fh.P(f"Total Models: {len(model_list)}", cls="text-gray-700 mb-1"),
                    fh.P(
                        f"Active Models: {sum(1 for m in model_list if m.active)}",
                        cls="text-green-700 mb-1",
                    ),
                    fh.P(
                        f"System Models: {sum(1 for m in model_list if m.owner_type == 'system')}",
                        cls="text-indigo-700 mb-1",
                    ),
                    fh.P(
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
    main_content = fh.Div(
        fh.H1("AI Model Management", cls="text-3xl font-bold text-indigo-900 mb-6"),
        fh.P(
            "Configure AI models available for feedback generation.",
            cls="text-gray-600 mb-8",
        ),
        # AI Model list
        fh.Div(
            fh.H2("Available Models", cls="text-2xl font-bold text-indigo-900 mb-4"),
            fh.Div(
                # Explanatory info
                fh.Div(
                    fh.H3(
                        "Model Configuration",
                        cls="text-lg font-semibold text-indigo-800 mb-2",
                    ),
                    fh.P(
                        "Models can be provided by the system or configured by individual instructors.",
                        cls="text-gray-600 mb-1",
                    ),
                    fh.P(
                        "System models are available to all instructors, while instructor models are private.",
                        cls="text-gray-600 mb-1",
                    ),
                    cls="bg-indigo-50 p-4 rounded-lg mb-6",
                ),
                # Add New Model button
                fh.Div(
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
                    fh.Div(
                        fh.Table(
                            fh.Thead(
                                fh.Tr(
                                    fh.Th(
                                        "Name",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    fh.Th(
                                        "Provider",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    fh.Th(
                                        "Model ID",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    fh.Th(
                                        "Owner",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    fh.Th(
                                        "Status",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                    fh.Th(
                                        "Actions",
                                        cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                    ),
                                ),
                                cls="bg-indigo-50",
                            ),
                            fh.Tbody(
                                *(
                                    fh.Tr(
                                        fh.Td(model.name, cls="py-4 px-6"),
                                        fh.Td(model.provider, cls="py-4 px-6"),
                                        fh.Td(model.model_id, cls="py-4 px-6"),
                                        fh.Td(
                                            fh.Span(
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
                                        fh.Td(
                                            fh.Span(
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
                                        fh.Td(
                                            fh.Div(
                                                fh.A(
                                                    "Edit",
                                                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                                    href=f"/admin/ai-models/edit/{model.id}",
                                                ),
                                                fh.Button(
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
                else fh.Div(
                    fh.P(
                        "No AI models configured. Add your first model to start generating feedback.",
                        cls="text-gray-500 italic text-center py-8",
                    ),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full",
                ),
                cls="mb-8",
            ),
        ),
        # Back button
        fh.Div(
            action_button(
                "Back to Dashboard", color="gray", href="/admin/dashboard", icon="←"
            ),
            cls="mt-4",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
            "AI Model Management", sidebar_content, main_content, user_role=Role.ADMIN,
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
    """Create new system-wide AI model configuration"""
    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Create System Model", cls="font-semibold text-indigo-900 mb-4"),
            fh.P("Configure a new AI model available to all instructors.", cls="text-gray-600 mb-4"),
            action_button("Cancel", color="gray", href="/admin/ai-models", icon="×"),  # noqa: RUF001
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    # Main content - Model creation form
    main_content = fh.Div(
        fh.H2("Configure New System AI Model", cls="text-2xl font-bold text-indigo-900 mb-6"),
        fh.Form(
            # Provider selection
            fh.Div(
                fh.Label(
                    "Provider",
                    for_="provider",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Select(
                    fh.Option("Select a provider", value="", selected=True, disabled=True),
                    fh.Option("OpenAI", value="openai"),
                    fh.Option("Anthropic", value="anthropic"),
                    fh.Option("Google (PaLM/Bard)", value="google"),
                    fh.Option("Google Gemini", value="gemini"),
                    fh.Option("Groq", value="groq"),
                    fh.Option("Cohere", value="cohere"),
                    fh.Option("HuggingFace", value="huggingface"),
                    fh.Option("Ollama (Local)", value="ollama"),
                    fh.Option("OpenRouter", value="openrouter"),
                    fh.Option("Custom OpenAI-Compatible", value="custom"),
                    id="provider",
                    name="provider",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    required=True,
                ),
                cls="mb-4",
            ),
            # Model ID
            fh.Div(
                fh.Label(
                    "Model ID",
                    for_="model_id",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="model_id",
                    name="model_id",
                    placeholder="e.g., gpt-4, claude-3-opus, gemini-pro, llama-3.1-8b",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    required=True,
                ),
                fh.P(
                    "The specific model identifier for your chosen provider",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-4",
            ),
            # Model name
            fh.Div(
                fh.Label(
                    "Display Name",
                    for_="name",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="text",
                    id="name",
                    name="name",
                    placeholder="e.g., GPT-4 Turbo, Claude 3 Opus, Gemini 1.5 Pro",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    required=True,
                ),
                cls="mb-4",
            ),
            # API Key
            fh.Div(
                fh.Label(
                    "API Key",
                    for_="api_key",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="password",
                    id="api_key",
                    name="api_key",
                    placeholder="Your API key (will be encrypted)",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                fh.P(
                    "Required for cloud providers. Optional for Ollama. Get keys from provider's website.",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-4",
            ),
            # Base URL (optional)
            fh.Div(
                fh.Label(
                    "Base URL (Optional)",
                    for_="base_url",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="url",
                    id="base_url",
                    name="base_url",
                    placeholder="Custom API endpoint (if applicable)",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                fh.P(
                    "Required for Custom providers. Optional for Ollama (default: http://localhost:11434). Leave empty for others.",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-6",
            ),
            # Make available to all instructors
            fh.Div(
                fh.Label(
                    fh.Input(
                        type="checkbox",
                        name="active",
                        value="true",
                        checked=True,
                        cls="mr-2",
                    ),
                    "Make this model available to all instructors",
                    cls="inline-flex items-center text-sm font-medium text-gray-700",
                ),
                cls="mb-6",
            ),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Save Model",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors mr-4",
                ),
                fh.A(
                    "Cancel",
                    href="/admin/ai-models",
                    cls="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300 transition-colors inline-block",
                ),
                cls="flex items-center",
            ),
            method="post",
            action="/admin/ai-models/create",
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
        ),
    )

    return dashboard_layout(
        "Create System AI Model",
        sidebar_content,
        main_content,
        user_role=Role.ADMIN,
        current_path="/admin/ai-models",
    )


@rt("/admin/ai-models/create")
@admin_required
def admin_models_create(session):
    """Placeholder for create AI model handler"""
    return fh.Div(fh.P("AI Model creation handler - To be implemented"))


@rt("/admin/ai-models/edit/{id}")
@admin_required
def admin_models_edit_form(session, id: int):
    """Placeholder for edit AI model form"""
    return fh.Div(fh.P(f"AI Model {id} edit form - To be implemented"))


@rt("/admin/ai-models/edit/{id}")
@admin_required
def admin_models_edit_update(session, id: int):
    """Placeholder for update AI model handler"""
    return fh.Div(fh.P(f"AI Model {id} update handler - To be implemented"))


@rt("/admin/ai-models/test")
@admin_required
def admin_models_test(session):
    """Placeholder for test AI model API"""
    return fh.Div(fh.P("AI Model test API - To be implemented"))


@rt("/admin/ai-models/{id}")
@admin_required
def admin_models_delete(session, id: int):
    """Placeholder for delete AI model handler"""
    return fh.Div(fh.P(f"AI Model {id} delete handler - To be implemented"))
