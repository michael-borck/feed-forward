"""
Instructor routes (dashboard, courses, students, etc.)
"""

import json
import random
import string
import urllib.parse
from datetime import datetime

from fasthtml.common import *
from fastlite import NotFoundError
from starlette.responses import RedirectResponse

# Get the route table from the app
# Import authentication decorators
from app import (
    instructor_required,
    rt,
)
from app.models.config import AIModel, ModelCapability, ai_models, model_capabilities
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.user import Role, User, users
from app.utils.crypto import encrypt_sensitive_data
from app.utils.email import (
    generate_verification_token,
    send_student_invitation_email,
)
from app.utils.ui import action_button, card, dashboard_layout, status_badge


# --- Utility Functions ---
def generate_invitation_token(length=40):
    """Generate a random token for student invitations"""
    chars = string.ascii_letters + string.digits + "-_"
    return "".join(random.choice(chars) for _ in range(length))


def get_instructor_id(user_email):
    """Get instructor ID from user email"""
    # In this database schema, email is used as the primary key/ID for users
    # So we'll just return the email as the instructor ID
    return user_email


# --- Instructor Models Management ---
@rt("/instructor/models")
@instructor_required
def get(session, request):
    # Get current instructor information
    current_user = users[session["auth"]]
    instructor_id = get_instructor_id(current_user.email)

    # Get all available models (system models + instructor's own models)
    all_models = []
    for model in ai_models():
        # Include if system model or owned by this instructor
        if model.owner_type == "system" or (
            model.owner_type == "instructor" and model.owner_id == instructor_id
        ):
            # Get capabilities for this model
            capabilities = []
            primary_capability = None

            for cap in model_capabilities():
                if cap.model_id == model.id:
                    capabilities.append(cap.capability)
                    if cap.is_primary:
                        primary_capability = cap.capability

            all_models.append(
                {
                    "id": model.id,
                    "name": model.name,
                    "provider": model.provider,
                    "model_id": model.model_id,
                    "version": "",
                    "description": "",
                    "capabilities": capabilities,
                    "primary_capability": primary_capability,
                    "owner_type": model.owner_type,
                    "active": model.active,
                }
            )

    # Sidebar content
    sidebar_content = Div(
        # Course navigation
        Div(
            H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="←"
                ),
                action_button(
                    "New Model",
                    color="indigo",
                    href="/instructor/models/new",
                    icon="➕",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Model Stats
        Div(
            H3("Model Stats", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                P(
                    f"System Models: {sum(1 for m in all_models if m['owner_type'] == 'system')}",
                    cls="text-gray-600 mb-2",
                ),
                P(
                    f"Your Models: {sum(1 for m in all_models if m['owner_type'] == 'instructor')}",
                    cls="text-indigo-600 mb-2",
                ),
                P(
                    f"Active Models: {sum(1 for m in all_models if m['active'])}",
                    cls="text-green-600 mb-2",
                ),
                cls="space-y-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = Div(
        H1("AI Models Management", cls="text-3xl font-bold text-indigo-900 mb-4"),
        P("Configure AI models for assessment feedback.", cls="text-gray-600 mb-6"),
        # Models explanation
        Div(
            H3("Using AI Models", cls="text-lg font-semibold text-indigo-800 mb-2"),
            P(
                "AI models are used to generate feedback for student assignments.",
                cls="text-gray-600 mb-1",
            ),
            P(
                "System models are available to all instructors.",
                cls="text-gray-600 mb-1",
            ),
            P(
                "You can also create your own models with your API keys.",
                cls="text-gray-600 mb-1",
            ),
            cls="bg-indigo-50 p-4 rounded-lg mb-6",
        ),
        # Add model button
        Div(
            action_button(
                "Add New Model",
                color="indigo",
                href="/instructor/models/new",
                icon="➕",
                size="regular",
            ),
            cls="mb-6",
        ),
        # Model table
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
                            "Capabilities",
                            cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                        ),
                        Th(
                            "Type",
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
                            Td(model["name"], cls="py-4 px-6"),
                            Td(model["provider"], cls="py-4 px-6"),
                            Td(model["model_id"], cls="py-4 px-6"),
                            Td(", ".join(model["capabilities"]), cls="py-4 px-6"),
                            Td(
                                Span(
                                    "System"
                                    if model["owner_type"] == "system"
                                    else "Your Model",
                                    cls="px-3 py-1 rounded-full text-xs "
                                    + (
                                        "bg-indigo-100 text-indigo-800"
                                        if model["owner_type"] == "system"
                                        else "bg-teal-100 text-teal-800"
                                    ),
                                ),
                                cls="py-4 px-6",
                            ),
                            Td(
                                Span(
                                    "Active" if model["active"] else "Inactive",
                                    cls="px-3 py-1 rounded-full text-xs "
                                    + (
                                        "bg-green-100 text-green-800"
                                        if model["active"]
                                        else "bg-gray-100 text-gray-800"
                                    ),
                                ),
                                cls="py-4 px-6",
                            ),
                            Td(
                                Div(
                                    *(
                                        [
                                            A(
                                                "Edit",
                                                cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                                href=f"/instructor/models/edit/{model['id']}",
                                            )
                                        ]
                                        if model["owner_type"] == "instructor"
                                        else [
                                            A(
                                                "View",
                                                cls="bg-blue-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-blue-700 transition-colors shadow-sm",
                                                href=f"/instructor/models/view/{model['id']}",
                                            )
                                        ]
                                    ),
                                    cls="flex",
                                ),
                                cls="py-4 px-6",
                            ),
                        )
                        for model in all_models
                    )
                ),
                cls="w-full border-collapse",
            ),
            cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100 mt-4",
        ),
    )

    return Titled(
        "AI Models Management | FeedForward",
        dashboard_layout(
            "AI Models", sidebar_content, main_content, user_role=Role.INSTRUCTOR
        ),
    )


# --- New AI Model Form for Instructors ---
@rt("/instructor/models/new")
@instructor_required
def get(session, request):
    # Get current user information
    current_user = users[session["auth"]]
    instructor_id = get_instructor_id(current_user.email)

    # Sidebar content
    sidebar_content = Div(
        # Navigation
        Div(
            H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Models", color="gray", href="/instructor/models", icon="←"
                ),
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="🏠"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Help section
        Div(
            H3("Provider Help", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                # Provider cards
                Div(
                    H4("OpenAI", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: gpt-4, gpt-3.5-turbo", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Anthropic", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P(
                        "Models: claude-3-opus, claude-3-sonnet",
                        cls="text-gray-600 text-sm",
                    ),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Google", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P(
                        "Models: gemini-pro, gemini-1.5-pro",
                        cls="text-gray-600 text-sm",
                    ),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Ollama", cls="font-semibold text-indigo-800 mb-1"),
                    P("Server URL required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: llama3, mistral", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("HuggingFace", cls="font-semibold text-indigo-800 mb-1"),
                    P(
                        "API Key optional, URL for custom endpoints",
                        cls="text-gray-600 mb-1 text-sm",
                    ),
                    P("Models: microsoft/DialoGPT-large", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                Div(
                    H4("Other/Custom", cls="font-semibold text-indigo-800 mb-1"),
                    P("Custom endpoint URL required", cls="text-gray-600 mb-1 text-sm"),
                    P("Compatible with OpenAI-style APIs", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg",
                ),
                cls="space-y-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content - Add new AI Model form
    main_content = Div(
        H1("Add New AI Model", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P(
            "Configure a new AI model for assignment feedback.",
            cls="text-gray-600 mb-8",
        ),
        # Model configuration form
        Form(
            # Basic model information
            Div(
                H2("Model Information", cls="text-2xl font-bold text-indigo-900 mb-6"),
                Div(
                    Div(
                        Label(
                            "Model Name",
                            for_="name",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Display name for this model",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="name",
                            name="name",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Provider",
                            for_="provider",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("AI model provider", cls="text-sm text-gray-500 mb-1"),
                        Select(
                            Option(
                                "Select a provider",
                                value="",
                                disabled=True,
                                selected=True,
                            ),
                            Option("OpenAI", value="OpenAI"),
                            Option("Anthropic", value="Anthropic"),
                            Option("Google", value="Google"),
                            Option("Ollama", value="Ollama"),
                            Option("HuggingFace", value="HuggingFace"),
                            Option("Other", value="Other"),
                            id="provider",
                            name="provider",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Model ID",
                            for_="model_id",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Specific model identifier (e.g., gpt-4, claude-3-opus)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="model_id",
                            name="model_id",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Version",
                            for_="version",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Version information (optional)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="version",
                            name="version",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Description",
                            for_="description",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Brief description of this model's capabilities",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Textarea(
                            id="description",
                            name="description",
                            rows=3,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    Div(
                        Label(
                            "Maximum Context Length",
                            for_="max_context",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Maximum token length this model can process",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="number",
                            id="max_context",
                            name="max_context",
                            value="8192",
                            min="1024",
                            step="1024",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "Status",
                            for_="active",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Select(
                            Option("Active", value="true", selected=True),
                            Option("Inactive", value="false"),
                            id="active",
                            name="active",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    # Create a hidden field for instructor_id
                    Input(
                        type="hidden",
                        id="owner_id",
                        name="owner_id",
                        value=str(instructor_id),
                    ),
                    Input(
                        type="hidden",
                        id="owner_type",
                        name="owner_type",
                        value="instructor",
                    ),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # Model capabilities section
                H2(
                    "Model Capabilities",
                    cls="text-2xl font-bold text-indigo-900 mb-6 mt-8",
                ),
                Div(
                    P(
                        "Select which capabilities this model supports:",
                        cls="text-gray-600 mb-4",
                    ),
                    Div(
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_text",
                                name="capabilities",
                                value="text",
                                checked=True,
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Text",
                                for_="capability_text",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_code",
                                name="capabilities",
                                value="code",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Code",
                                for_="capability_code",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_vision",
                                name="capabilities",
                                value="vision",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Vision",
                                for_="capability_vision",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        Div(
                            Input(
                                type="checkbox",
                                id="capability_audio",
                                name="capabilities",
                                value="audio",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                            ),
                            Label(
                                "Audio",
                                for_="capability_audio",
                                cls="ml-2 text-indigo-900",
                            ),
                            cls="flex items-center mb-2",
                        ),
                        cls="mb-6",
                    ),
                    H3(
                        "Primary Capability",
                        cls="text-xl font-bold text-indigo-900 mb-2",
                    ),
                    P(
                        "Select the primary capability this model is optimized for:",
                        cls="text-gray-600 mb-4",
                    ),
                    Div(
                        Select(
                            Option("Text", value="text", selected=True),
                            Option("Code", value="code"),
                            Option("Vision", value="vision"),
                            Option("Audio", value="audio"),
                            id="primary_capability",
                            name="primary_capability",
                            required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # API Configuration section
                H2(
                    "API Configuration",
                    cls="text-2xl font-bold text-indigo-900 mb-6 mt-8",
                ),
                Div(
                    # OpenAI Config
                    Div(
                        Label(
                            "API Key",
                            for_="openai_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("OpenAI API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="openai_api_key",
                            name="openai_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="openai-config",
                        cls="w-full",
                    ),
                    # Anthropic Config
                    Div(
                        Label(
                            "API Key",
                            for_="anthropic_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("Anthropic API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="anthropic_api_key",
                            name="anthropic_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="anthropic-config",
                        cls="w-full hidden",
                    ),
                    # Google Config
                    Div(
                        Label(
                            "API Key",
                            for_="google_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P("Google AI API key", cls="text-sm text-gray-500 mb-1"),
                        Input(
                            type="password",
                            id="google_api_key",
                            name="google_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="google_base_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Google AI endpoint URL (optional, leave empty for default)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="google_base_url",
                            name="google_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="google-config",
                        cls="w-full hidden",
                    ),
                    # Ollama Config
                    Div(
                        Label(
                            "Server URL",
                            for_="ollama_base_url",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Ollama server URL (e.g., http://localhost:11434)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="ollama_base_url",
                            name="ollama_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: No API key required for local Ollama",
                            cls="text-xs text-green-600 mt-1",
                        ),
                        id="ollama-config",
                        cls="w-full hidden",
                    ),
                    # HuggingFace Config
                    Div(
                        Label(
                            "API Key",
                            for_="huggingface_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "HuggingFace API key (optional for public models)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="password",
                            id="huggingface_api_key",
                            name="huggingface_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="huggingface_base_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Custom endpoint URL (optional, leave empty for default)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="huggingface_base_url",
                            name="huggingface_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="huggingface-config",
                        cls="w-full hidden",
                    ),
                    # Other/Custom Config
                    Div(
                        Label(
                            "API Key",
                            for_="custom_api_key",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Custom provider API key (if required)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="password",
                            id="custom_api_key",
                            name="custom_api_key",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        Label(
                            "Base URL",
                            for_="custom_base_url",
                            cls="block text-indigo-900 font-medium mb-1 mt-4",
                        ),
                        P(
                            "Custom endpoint URL (required for custom providers)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="text",
                            id="custom_base_url",
                            name="custom_base_url",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        P(
                            "Note: API keys are stored encrypted in the database",
                            cls="text-xs text-amber-600 mt-1",
                        ),
                        id="other-config",
                        cls="w-full hidden",
                    ),
                    # Common settings
                    Div(
                        Label(
                            "Temperature",
                            for_="temperature",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Controls randomness (0.0-1.0)",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Input(
                            type="number",
                            id="temperature",
                            name="temperature",
                            value="0.2",
                            min="0",
                            max="1",
                            step="0.1",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full md:w-1/2",
                    ),
                    Div(
                        Label(
                            "System Prompt",
                            for_="system_prompt",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        P(
                            "Default system prompt for educational assessment",
                            cls="text-sm text-gray-500 mb-1",
                        ),
                        Textarea(
                            id="system_prompt",
                            name="system_prompt",
                            rows=3,
                            value="You are an expert educational assessor providing detailed, constructive feedback on student work.",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="mb-6 w-full",
                    ),
                    # Provider selection script
                    Script("""
                    document.getElementById('provider').addEventListener('change', function() {
                        // Hide all config sections
                        document.getElementById('openai-config').classList.add('hidden');
                        document.getElementById('anthropic-config').classList.add('hidden');
                        document.getElementById('google-config').classList.add('hidden');
                        document.getElementById('ollama-config').classList.add('hidden');
                        document.getElementById('huggingface-config').classList.add('hidden');
                        document.getElementById('other-config').classList.add('hidden');
                        
                        // Show selected provider config
                        if (this.value === 'OpenAI') {
                            document.getElementById('openai-config').classList.remove('hidden');
                        } else if (this.value === 'Anthropic') {
                            document.getElementById('anthropic-config').classList.remove('hidden');
                        } else if (this.value === 'Google') {
                            document.getElementById('google-config').classList.remove('hidden');
                        } else if (this.value === 'Ollama') {
                            document.getElementById('ollama-config').classList.remove('hidden');
                        } else if (this.value === 'HuggingFace') {
                            document.getElementById('huggingface-config').classList.remove('hidden');
                        } else if (this.value === 'Other') {
                            document.getElementById('other-config').classList.remove('hidden');
                        }
                    });
                    """),
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100",
                ),
                # Test Connection and Form submission
                Div(
                    Div(id="test-result", cls="mb-4"),
                    Div(id="form-message", cls="mb-4"),
                    Div(
                        Button(
                            "Test Connection",
                            type="button",
                            id="test-connection-btn",
                            cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm mr-4",
                            onclick="testInstructorConnection()",
                        ),
                        Button(
                            "Cancel",
                            type="button",
                            onClick="window.location='/instructor/models'",
                            cls="bg-gray-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm mr-4",
                        ),
                        Button(
                            "Save Model",
                            type="submit",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="flex",
                    ),
                    cls="mt-6",
                ),
                # Test Connection Script for Instructor
                Script("""
                function testInstructorConnection() {
                    const provider = document.getElementById('provider').value;
                    if (!provider) {
                        document.getElementById('test-result').innerHTML = '<div class="bg-red-50 p-4 rounded-lg"><p class="text-red-500">Please select a provider first</p></div>';
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('provider', provider);
                    
                    // Get API key and URL based on provider
                    if (provider === 'OpenAI') {
                        formData.append('api_key', document.getElementById('openai_api_key').value);
                    } else if (provider === 'Anthropic') {
                        formData.append('api_key', document.getElementById('anthropic_api_key').value);
                    } else if (provider === 'Google') {
                        formData.append('api_key', document.getElementById('google_api_key').value);
                        formData.append('base_url', document.getElementById('google_base_url').value);
                    } else if (provider === 'Ollama') {
                        formData.append('base_url', document.getElementById('ollama_base_url').value);
                    } else if (provider === 'HuggingFace') {
                        formData.append('api_key', document.getElementById('huggingface_api_key').value);
                        formData.append('base_url', document.getElementById('huggingface_base_url').value);
                    } else if (provider === 'Other') {
                        formData.append('api_key', document.getElementById('custom_api_key').value);
                        formData.append('base_url', document.getElementById('custom_base_url').value);
                    }
                    
                    // Show loading state
                    document.getElementById('test-result').innerHTML = '<div class="bg-blue-50 p-4 rounded-lg"><p class="text-blue-600">Testing connection...</p></div>';
                    
                    // Make the request
                    fetch('/instructor/models/test', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.text())
                    .then(html => {
                        document.getElementById('test-result').innerHTML = html;
                    })
                    .catch(error => {
                        document.getElementById('test-result').innerHTML = '<div class="bg-red-50 p-4 rounded-lg"><p class="text-red-500">Error: ' + error + '</p></div>';
                    });
                }
                """),
                cls="mb-8",
            ),
            hx_post="/instructor/models/create",
            hx_target="#form-message",
        ),
    )

    return Titled(
        "Add New AI Model | FeedForward",
        dashboard_layout(
            "Add New Model", sidebar_content, main_content, user_role=Role.INSTRUCTOR
        ),
    )


# --- Create New AI Model (Instructor) ---
@rt("/instructor/models/create")
@instructor_required
def post(
    session,
    name: str,
    provider: str,
    model_id: str,
    version: str = "",
    description: str = "",
    max_context: int = 8192,
    owner_type: str = "instructor",
    owner_id: int = 0,
    active: str = "true",
    capabilities: list = None,
    primary_capability: str = "text",
    temperature: float = 0.2,
    system_prompt: str = "You are an expert educational assessor providing detailed, constructive feedback on student work.",
    openai_api_key: str = None,
    anthropic_api_key: str = None,
    ollama_base_url: str = None,
    google_api_key: str = None,
    google_base_url: str = None,
    huggingface_api_key: str = None,
    huggingface_base_url: str = None,
    custom_api_key: str = None,
    custom_base_url: str = None,
):
    try:
        # Verify current user is the owner or an admin
        current_user = users[session["auth"]]
        instructor_id = get_instructor_id(current_user.email)

        # Security check - ensure owner_id matches instructor_id
        owner_id = instructor_id
        owner_type = "instructor"  # Instructors can only create instructor-owned models

        # Convert capabilities to list if it's a single value
        if capabilities and not isinstance(capabilities, list):
            capabilities = [capabilities]

        # Default to text if no capabilities selected
        if not capabilities:
            capabilities = ["text"]

        # Create API config based on provider
        api_config = {}
        if provider == "OpenAI":
            api_config = {
                "api_key": openai_api_key,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Anthropic":
            api_config = {
                "api_key": anthropic_api_key,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Ollama":
            api_config = {
                "base_url": ollama_base_url,
                "temperature": float(temperature),
            }
        elif provider == "Google":
            api_config = {
                "api_key": google_api_key,
                "base_url": google_base_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "HuggingFace":
            api_config = {
                "api_key": huggingface_api_key,
                "base_url": huggingface_base_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }
        elif provider == "Other":
            api_config = {
                "api_key": custom_api_key,
                "base_url": custom_base_url,
                "temperature": float(temperature),
                "system_prompt": system_prompt,
            }

        # For security, encrypt API keys if present
        for key in api_config:
            if key.endswith("api_key") and api_config[key]:
                api_config[key] = encrypt_sensitive_data(api_config[key])

        # Convert api_config to JSON string
        api_config_str = json.dumps(api_config)

        # Get next available ID
        next_id = 1
        existing_ids = [m.id for m in ai_models()]
        if existing_ids:
            next_id = max(existing_ids) + 1

        # Create timestamp
        now = datetime.now().isoformat()

        # Create new AI model
        new_model = AIModel(
            id=next_id,
            name=name,
            provider=provider,
            model_id=model_id,
            model_version=version,
            description=description,
            api_config=api_config_str,
            owner_type=owner_type,
            owner_id=owner_id,
            capabilities=json.dumps(capabilities),
            max_context=int(max_context),
            active=active.lower() == "true",
            created_at=now,
            updated_at=now,
        )

        # Add to database
        ai_models.insert(new_model)

        # Create capability entries for each capability
        for capability in capabilities:
            # Get next available ID for capability
            next_cap_id = 1
            existing_cap_ids = [c.id for c in model_capabilities()]
            if existing_cap_ids:
                next_cap_id = max(existing_cap_ids) + 1

            # Create capability record
            cap = ModelCapability(
                id=next_cap_id,
                model_id=next_id,
                capability=capability,
                is_primary=(capability == primary_capability),
            )
            model_capabilities.insert(cap)

        # Return success message with redirect
        return Div(
            P(f"AI Model '{name}' created successfully!", cls="text-green-500 mb-2"),
            Script(
                "setTimeout(function() { window.location = '/instructor/models'; }, 1500);"
            ),
            cls="bg-green-50 p-4 rounded-lg",
        )
    except Exception as e:
        # Return error message
        return Div(
            P(f"Error creating AI model: {e!s}", cls="text-red-500"),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- Test AI Model Connection (Instructor) ---
@rt("/instructor/models/test")
@instructor_required
def post(session, provider: str, api_key: str = None, base_url: str = None):
    """Test AI model connection for instructors"""
    try:
        import litellm

        # Create temporary config
        config = {"temperature": 0.2, "system_prompt": "You are a test assistant."}

        # Add provider-specific configuration
        if provider in ["OpenAI", "Anthropic", "Google"]:
            if not api_key:
                return Div(
                    P(f"{provider} requires an API key", cls="text-red-500"),
                    cls="bg-red-50 p-4 rounded-lg",
                )
            config["api_key"] = api_key

        if provider in ["Google", "HuggingFace", "Other"] and base_url:
            config["base_url"] = base_url
        elif provider == "Ollama":
            if not base_url:
                return Div(
                    P("Ollama requires a server URL", cls="text-red-500"),
                    cls="bg-red-50 p-4 rounded-lg",
                )
            config["base_url"] = base_url

        # Test model ID based on provider
        test_models = {
            "OpenAI": "gpt-3.5-turbo",
            "Anthropic": "claude-3-haiku-20240307",
            "Google": "gemini-1.5-flash",
            "Ollama": "llama3",
            "HuggingFace": "microsoft/DialoGPT-small",
            "Other": "gpt-3.5-turbo",
        }

        model_id = test_models.get(provider, "gpt-3.5-turbo")

        # Build model string for litellm
        if provider == "OpenAI" or provider == "Anthropic":
            model_string = model_id
        elif provider == "Google":
            model_string = f"gemini/{model_id.replace('gemini-', '')}"
        elif provider == "Ollama":
            model_string = f"ollama/{model_id}"
        elif provider == "HuggingFace":
            model_string = f"huggingface/{model_id}"
        else:
            model_string = model_id

        # Set up litellm parameters
        kwargs = {
            "model": model_string,
            "messages": [
                {
                    "role": "user",
                    "content": "Say 'Connection successful' in exactly 3 words.",
                }
            ],
            "max_tokens": 10,
            "temperature": config.get("temperature", 0.2),
        }

        # Add API key if present
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]

        # Add base URL if present
        if config.get("base_url"):
            if provider == "Ollama":
                kwargs["api_base"] = config["base_url"]
            elif provider in ["Google", "HuggingFace", "Other"]:
                kwargs["base_url"] = config["base_url"]

        # Test connection
        try:
            response = litellm.completion(**kwargs)

            if response and response.choices:
                content = response.choices[0].message.content
                return Div(
                    P(
                        f"✅ {provider} connection successful!",
                        cls="text-green-600 font-medium",
                    ),
                    P(f"Response: {content}", cls="text-gray-600 text-sm mt-2"),
                    cls="bg-green-50 p-4 rounded-lg",
                )
            else:
                return Div(
                    P(
                        f"❌ {provider} connection failed - no response",
                        cls="text-red-500",
                    ),
                    cls="bg-red-50 p-4 rounded-lg",
                )

        except Exception as e:
            error_msg = str(e)
            # Clean up error messages
            if "api_key" in error_msg.lower():
                error_msg = "Invalid or missing API key"
            elif "connection" in error_msg.lower():
                error_msg = "Could not connect to server"
            elif "unauthorized" in error_msg.lower():
                error_msg = "Authentication failed - check API key"

            return Div(
                P(f"❌ {provider} connection failed", cls="text-red-500 font-medium"),
                P(f"Error: {error_msg}", cls="text-gray-600 text-sm mt-2"),
                cls="bg-red-50 p-4 rounded-lg",
            )

    except Exception as e:
        return Div(
            P(f"Error testing connection: {e!s}", cls="text-red-500"),
            cls="bg-red-50 p-4 rounded-lg",
        )


# --- View AI Model Details (Instructor) ---
@rt("/instructor/models/view/{model_id}")
@instructor_required
def get(session, model_id: int):
    try:
        # Get current user
        current_user = users[session["auth"]]
        instructor_id = get_instructor_id(current_user.email)

        # Get the specific model
        model = None
        for m in ai_models():
            if m.id == model_id:
                model = m
                break

        if not model:
            return RedirectResponse("/error/404")

        # Security check - only allow viewing own models or system models
        if model.owner_type == "instructor" and model.owner_id != instructor_id:
            return RedirectResponse("/error/403")

        # Parse model configuration
        import json

        try:
            config = json.loads(model.api_config) if model.api_config else {}
        except:
            config = {}

        try:
            capabilities = json.loads(model.capabilities) if model.capabilities else []
        except:
            capabilities = []

        from app.utils.ui import card, dashboard_layout

        # Sidebar content
        sidebar_content = Div(
            card(
                Div(
                    H3("AI Models", cls="font-semibold text-indigo-900 mb-4"),
                    A(
                        "← Back to Models",
                        href="/instructor/models",
                        cls="text-indigo-600 hover:text-indigo-800 text-sm",
                    ),
                    A(
                        "Create New Model",
                        href="/instructor/models/new",
                        cls="block mt-4 bg-indigo-600 text-white px-4 py-2 rounded-lg text-center hover:bg-indigo-700 transition-colors",
                    ),
                )
            )
        )

        # Main content
        main_content = Div(
            H1("AI Model Details", cls="text-3xl font-bold text-indigo-900 mb-6"),
            # Model Information Card
            card(
                Div(
                    H2(
                        "Model Information",
                        cls="text-xl font-bold text-indigo-900 mb-4",
                    ),
                    Div(
                        Div(
                            Label("Name:", cls="font-medium text-indigo-900"),
                            P(model.name, cls="text-gray-700"),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Provider:", cls="font-medium text-indigo-900"),
                            P(model.provider, cls="text-gray-700"),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Model ID:", cls="font-medium text-indigo-900"),
                            P(model.model_id, cls="text-gray-700"),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Version:", cls="font-medium text-indigo-900"),
                            P(
                                model.model_version or "Not specified",
                                cls="text-gray-700",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Description:", cls="font-medium text-indigo-900"),
                            P(
                                model.description or "No description provided",
                                cls="text-gray-700",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Status:", cls="font-medium text-indigo-900"),
                            P(
                                "Active" if model.active else "Inactive",
                                cls="text-green-600"
                                if model.active
                                else "text-red-600",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Owner:", cls="font-medium text-indigo-900"),
                            P(
                                f"{model.owner_type.title()}: {model.owner_id}",
                                cls="text-gray-700",
                            ),
                            cls="mb-4",
                        ),
                        cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                ),
                title="Basic Information",
            ),
            # Configuration Card
            card(
                Div(
                    H2("Configuration", cls="text-xl font-bold text-indigo-900 mb-4"),
                    Div(
                        Div(
                            Label("Temperature:", cls="font-medium text-indigo-900"),
                            P(
                                str(config.get("temperature", "Not set")),
                                cls="text-gray-700",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Max Context:", cls="font-medium text-indigo-900"),
                            P(str(model.max_context), cls="text-gray-700"),
                            cls="mb-4",
                        ),
                        Div(
                            Label("Capabilities:", cls="font-medium text-indigo-900"),
                            P(
                                ", ".join(capabilities)
                                if capabilities
                                else "None specified",
                                cls="text-gray-700",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label(
                                "API Configuration:", cls="font-medium text-indigo-900"
                            ),
                            P(
                                "Configured"
                                if config.get("api_key") or config.get("base_url")
                                else "Not configured",
                                cls="text-green-600"
                                if config.get("api_key") or config.get("base_url")
                                else "text-red-600",
                            ),
                            cls="mb-4",
                        ),
                        cls="grid grid-cols-1 md:grid-cols-2 gap-4",
                    ),
                    # System Prompt (if available)
                    Div(
                        Label(
                            "System Prompt:",
                            cls="font-medium text-indigo-900 block mb-2",
                        ),
                        Div(
                            P(
                                config.get(
                                    "system_prompt", "No system prompt configured"
                                ),
                                cls="text-gray-700 bg-gray-50 p-3 rounded-lg",
                            ),
                            cls="mb-4",
                        ),
                    )
                    if config.get("system_prompt")
                    else "",
                ),
                title="Technical Configuration",
            ),
            # Actions
            Div(
                A(
                    "Edit Model",
                    href=f"/instructor/models/edit/{model_id}",
                    cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm mr-4",
                ),
                A(
                    "Back to Models",
                    href="/instructor/models",
                    cls="bg-gray-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm",
                ),
                cls="mt-8",
            ),
        )

        return dashboard_layout(
            title=f"AI Model: {model.name}",
            sidebar=sidebar_content,
            main_content=main_content,
            user_role=current_user.role,
            user=current_user,
            current_path=request.url.path,
        )

    except Exception:
        return RedirectResponse("/error/500")


# --- Instructor Dashboard ---
@rt("/instructor/dashboard")
@instructor_required
def get(session, request):
    # Get components directly from top-level imports

    # Get current user
    user = users[session["auth"]]

    # Add AI Models section to the dashboard
    from app.utils.ui import card

    ai_models_section = Div(
        H2("AI Models", cls="text-xl font-bold text-indigo-900 mb-4"),
        P("Configure AI models for assessment feedback.", cls="text-gray-600 mb-4"),
        # Model management card
        Div(
            Div(
                H3("Model Management", cls="font-semibold text-indigo-800 mb-2"),
                P(
                    "Add, view, and manage AI models for assessment.",
                    cls="text-gray-600 mb-2",
                ),
                action_button(
                    "Manage Models",
                    color="indigo",
                    href="/instructor/models",
                    icon="⚙️",
                    size="small",
                ),
                cls="p-4",
            ),
            cls="bg-white rounded-xl shadow-md border border-gray-100 mb-4 hover:shadow-lg transition-shadow",
        ),
    )

    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1

            # Add to courses with student count
            instructor_courses.append((course, student_count))

    # Create dashboard content
    if instructor_courses:
        # Show courses if the instructor has any
        courses_content = Div(
            Div(
                H2("Your Courses", cls="text-2xl font-bold text-indigo-900"),
                A(
                    "View All Courses",
                    href="/instructor/courses",
                    cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium",
                ),
                cls="flex justify-between items-center mb-6",
            ),
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                H3(
                                    course.title,
                                    cls="text-xl font-bold text-indigo-900 mb-1",
                                ),
                                P(f"Course Code: {course.code}", cls="text-gray-600"),
                                P(f"Students: {student_count}", cls="text-gray-600"),
                                cls="mb-4",
                            ),
                            Div(
                                A(
                                    "View Students",
                                    href=f"/instructor/courses/{course.id}/students",
                                    cls="text-indigo-600 hover:text-indigo-800 mr-3 font-medium",
                                ),
                                A(
                                    "Manage Assignments",
                                    href=f"/instructor/courses/{course.id}/assignments",
                                    cls="text-teal-600 hover:text-teal-800 font-medium",
                                ),
                                cls="flex",
                            ),
                            cls="",
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100",
                    )
                    for course, student_count in instructor_courses
                ],
                cls="grid grid-cols-1 md:grid-cols-2 gap-6",
            ),
            cls="",
        )
    else:
        # Show a message if no courses yet
        courses_content = card(
            Div(
                P(
                    "You don't have any courses yet. Create your first course to get started.",
                    cls="text-center text-gray-600 mb-6",
                ),
                Div(
                    A(
                        "Create New Course",
                        href="/instructor/courses/new",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="text-center",
                ),
                cls="py-8",
            ),
            title="Welcome to the Instructor Dashboard",
        )

    # Quick action cards
    action_cards = Div(
        H2("Quick Actions", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            # Create Course card
            card(
                Div(
                    Div(
                        Span("🏫", cls="text-4xl"),
                        P(
                            "Create a new course for your students",
                            cls="mt-2 text-gray-600",
                        ),
                        cls="text-center py-4",
                    ),
                    Div(
                        A(
                            "Create Course",
                            href="/instructor/courses/new",
                            cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block",
                        ),
                        cls="mt-4",
                    ),
                    cls="h-full flex flex-col justify-between",
                )
            ),
            # Manage Courses card
            card(
                Div(
                    Div(
                        Span("📚", cls="text-4xl"),
                        P("View and manage all your courses", cls="mt-2 text-gray-600"),
                        cls="text-center py-4",
                    ),
                    Div(
                        A(
                            "Manage Courses",
                            href="/instructor/courses",
                            cls="bg-amber-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-amber-700 transition-colors shadow-sm w-full text-center block",
                        ),
                        cls="mt-4",
                    ),
                    cls="h-full flex flex-col justify-between",
                )
            ),
            # Invite Students card
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P(
                            "Invite students to join your course",
                            cls="mt-2 text-gray-600",
                        ),
                        cls="text-center py-4",
                    ),
                    Div(
                        A(
                            "Invite Students",
                            href="/instructor/invite-students",
                            cls="bg-teal-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm w-full text-center block",
                        ),
                        cls="mt-4",
                    ),
                    cls="h-full flex flex-col justify-between",
                )
            ),
            # Manage Students card
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P("Manage your enrolled students", cls="mt-2 text-gray-600"),
                        cls="text-center py-4",
                    ),
                    Div(
                        A(
                            "Manage Students",
                            href="/instructor/manage-students",
                            cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block",
                        ),
                        cls="mt-4",
                    ),
                    cls="h-full flex flex-col justify-between",
                )
            ),
            # TODO: Add more action cards as features are developed
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
        ),
        cls="mt-10",
    )

    # Main content with courses, AI models section, and action cards
    main_content = Div(courses_content, ai_models_section, action_cards, cls="")

    # Sidebar content
    sidebar_content = Div(
        # Instructor info card
        card(
            Div(
                Div(
                    Div(
                        user.name[0] if user.name else "?",
                        cls="w-16 h-16 rounded-full bg-indigo-600 text-white flex items-center justify-center text-2xl font-bold",
                    ),
                    cls="flex justify-center mb-4",
                ),
                H3(user.name, cls="text-lg font-bold text-center text-indigo-900"),
                P(user.email, cls="text-center text-gray-600 mb-4"),
                Hr(cls="my-4"),
                Div(
                    P(f"Courses: {len(instructor_courses)}", cls="text-gray-600"),
                    P(
                        f"Department: {user.department if user.department else 'Not set'}",
                        cls="text-gray-600",
                    ),
                    cls="text-sm",
                ),
                cls="p-2",
            ),
            title="Profile",
        ),
        # Recent activity or tips
        card(
            Div(
                Div(
                    P("✓ Complete your profile information", cls="mb-2 text-green-600"),
                    P("✓ Create your first course", cls="mb-2 text-green-600")
                    if instructor_courses
                    else P("○ Create your first course", cls="mb-2 text-gray-600"),
                    P("○ Invite students to your course", cls="mb-2 text-gray-600"),
                    P("○ Create your first assignment", cls="mb-2 text-gray-600"),
                    cls="text-sm",
                ),
                cls="p-2",
            ),
            title="Getting Started",
        ),
        cls="space-y-6",
    )

    # Use the dashboard layout with our components
    from app.utils.ui import dashboard_layout

    return dashboard_layout(
        "Instructor Dashboard | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path,
    )


# --- Assignment Management ---
# Helper function to get an assignment by ID with instructor permission check
def get_instructor_assignment(assignment_id, instructor_email):
    """
    Get an assignment by ID, checking that it belongs to the instructor.
    Returns (assignment, error_message) tuple.
    """
    # Import assignments model
    from app.models.assignment import assignments

    # Find the assignment
    target_assignment = None
    try:
        for assignment in assignments():
            if assignment.id == assignment_id:
                target_assignment = assignment
                break

        if not target_assignment:
            return None, "Assignment not found."

        # Check if this instructor owns the assignment
        if target_assignment.created_by != instructor_email:
            return None, "You don't have permission to access this assignment."

        # Skip deleted assignments
        if (
            hasattr(target_assignment, "status")
            and target_assignment.status == "deleted"
        ):
            return None, "This assignment has been deleted."

        return target_assignment, None
    except Exception as e:
        return None, f"Error accessing assignment: {e!s}"


@rt("/instructor/courses/{course_id}/assignments")
@instructor_required
def get(session, course_id: int):
    """Shows all assignments for a specific course"""
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Import assignments model
    from app.models.assignment import assignments

    # Get all assignments for this course
    course_assignments = []
    for assignment in assignments():
        if assignment.course_id == course_id and assignment.created_by == user.email:
            # Skip deleted assignments
            if hasattr(assignment, "status") and assignment.status == "deleted":
                continue
            course_assignments.append(assignment)

    # Sort assignments by creation date (newest first)
    course_assignments.sort(
        key=lambda x: x.created_at if hasattr(x, "created_at") else "", reverse=True
    )

    # Create the main content
    main_content = Div(
        # Header with action button
        Div(
            H2(
                f"Assignments for {course.title}",
                cls="text-2xl font-bold text-indigo-900",
            ),
            action_button(
                "Create New Assignment",
                color="indigo",
                href=f"/instructor/courses/{course_id}/assignments/new",
                icon="+",
            ),
            cls="flex justify-between items-center mb-6",
        ),
        # Assignment listing or empty state
        (
            Div(
                P(
                    f"This course has {len(course_assignments)} {'assignment' if len(course_assignments) == 1 else 'assignments'}.",
                    cls="text-gray-600 mb-6",
                ),
                # Assignment table with actions
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th(
                                    "Title",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Status",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Due Date",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Drafts",
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
                                    # Assignment title
                                    Td(assignment.title, cls="py-4 px-6"),
                                    # Status badge
                                    Td(
                                        status_badge(
                                            getattr(
                                                assignment, "status", "draft"
                                            ).capitalize(),
                                            "gray"
                                            if getattr(assignment, "status", "draft")
                                            == "draft"
                                            else "green"
                                            if getattr(assignment, "status", "draft")
                                            == "active"
                                            else "yellow"
                                            if getattr(assignment, "status", "draft")
                                            == "closed"
                                            else "blue"
                                            if getattr(assignment, "status", "draft")
                                            == "archived"
                                            else "red",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    # Due date
                                    Td(
                                        getattr(assignment, "due_date", "Not set")
                                        or "Not set",
                                        cls="py-4 px-6",
                                    ),
                                    # Max drafts allowed
                                    Td(
                                        str(getattr(assignment, "max_drafts", 1) or 1),
                                        cls="py-4 px-6",
                                    ),
                                    # Action buttons
                                    Td(
                                        Div(
                                            A(
                                                "Edit",
                                                href=f"/instructor/assignments/{assignment.id}/edit",
                                                cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                            ),
                                            A(
                                                "Rubric",
                                                href=f"/instructor/assignments/{assignment.id}/rubric",
                                                cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700 mr-2",
                                            ),
                                            A(
                                                "Submissions",
                                                href=f"/instructor/assignments/{assignment.id}/submissions",
                                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for assignment in course_assignments
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                ),
                cls="",
            )
            if course_assignments
            else Div(
                P(
                    "This course doesn't have any assignments yet. Create your first assignment to get started.",
                    cls="text-center text-gray-600 mb-6",
                ),
                Div(
                    A(
                        "Create New Assignment",
                        href=f"/instructor/courses/{course_id}/assignments/new",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="text-center",
                ),
                cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4",
            )
        ),
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Courses",
                    color="gray",
                    href="/instructor/courses",
                    icon="←",
                ),
                action_button(
                    "Course Details",
                    color="blue",
                    href=f"/instructor/courses/{course_id}/edit",
                    icon="📝",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href=f"/instructor/courses/{course_id}/students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Assignment Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Create Assignment",
                    color="indigo",
                    href=f"/instructor/courses/{course_id}/assignments/new",
                    icon="+",
                ),
                cls="space-y-3",
            ),
            P(
                "Assignment Statuses:",
                cls="text-sm text-gray-600 font-medium mt-4 mb-2",
            ),
            P("Draft: Only visible to you", cls="text-xs text-gray-600 mb-1"),
            P("Active: Available to students", cls="text-xs text-gray-600 mb-1"),
            P("Closed: No new submissions", cls="text-xs text-gray-600 mb-1"),
            P("Archived: Hidden from students", cls="text-xs text-gray-600 mb-1"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return dashboard_layout(
        f"Assignments for {course.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/courses/{course_id}/assignments/new")
@instructor_required
def get(session, course_id: int):
    """Form to create a new assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Check course status - don't allow new assignments for closed/archived/deleted courses
    if hasattr(course, "status") and course.status in ["closed", "archived", "deleted"]:
        return Div(
            H2("Course Not Active", cls="text-2xl font-bold text-amber-700 mb-4"),
            P(
                f"This course is currently '{course.status}'. You cannot add new assignments to a {course.status} course.",
                cls="text-gray-700 mb-4",
            ),
            A(
                "Back to Course",
                href=f"/instructor/courses/{course_id}/assignments",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-amber-50 rounded-xl shadow-md border-2 border-amber-200 text-center",
        )

    # Form to create a new assignment
    form_content = Div(
        H2(
            f"Create New Assignment for {course.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        P(
            "Complete the form below to create a new assignment for your students.",
            cls="text-gray-600 mb-6",
        ),
        Form(
            # Title field
            Div(
                Label(
                    "Assignment Title",
                    for_="title",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Input(
                    id="title",
                    name="title",
                    type="text",
                    placeholder="e.g. Midterm Essay",
                    required=True,
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-4",
            ),
            # Description field
            Div(
                Label(
                    "Assignment Description",
                    for_="description",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Textarea(
                    id="description",
                    name="description",
                    placeholder="Provide detailed instructions for the assignment",
                    rows="6",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-4",
            ),
            # Due date and max drafts
            Div(
                Div(
                    Label(
                        "Due Date (Optional)",
                        for_="due_date",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="due_date",
                        name="due_date",
                        type="date",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="w-1/2 pr-2",
                ),
                Div(
                    Label(
                        "Maximum Drafts",
                        for_="max_drafts",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="max_drafts",
                        name="max_drafts",
                        type="number",
                        min="1",
                        value="3",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="w-1/2 pl-2",
                ),
                cls="flex mb-4",
            ),
            # Status selection
            Div(
                Label(
                    "Assignment Status",
                    for_="status",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Select(
                    Option("Draft - Only visible to you", value="draft", selected=True),
                    Option("Active - Available to students", value="active"),
                    id="status",
                    name="status",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-6",
            ),
            # Submit button
            Div(
                Button(
                    "Create Assignment",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                ),
                cls="mb-4",
            ),
            # Result placeholder
            Div(id="result"),
            # Form submission details
            hx_post=f"/instructor/courses/{course_id}/assignments/new",
            hx_target="#result",
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
        ),
        cls="",
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Assignment Creation", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Assignments",
                    color="gray",
                    href=f"/instructor/courses/{course_id}/assignments",
                    icon="←",
                ),
                action_button(
                    "Course Details",
                    color="blue",
                    href=f"/instructor/courses/{course_id}/edit",
                    icon="📝",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Assignment Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Provide clear expectations and grading criteria",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Set draft limits based on your feedback capacity",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Leave in 'Draft' mode until ready for students",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Create a detailed rubric after assignment creation",
                cls="text-gray-600 text-sm",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return dashboard_layout(
        f"Create Assignment | {course.title} | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/courses/{course_id}/assignments/new")
@instructor_required
def post(
    session,
    course_id: int,
    title: str,
    description: str,
    due_date: str = "",
    max_drafts: int = 3,
    status: str = "draft",
):
    """Handle new assignment creation"""
    # Get current user
    user = users[session["auth"]]

    # Validate required fields
    if not title:
        return "Assignment title is required."

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return f"Error: {error}"

    # Check course status - don't allow new assignments for closed/archived/deleted courses
    if hasattr(course, "status") and course.status in ["closed", "archived", "deleted"]:
        return f"Cannot add new assignments to a {course.status} course."

    # Import assignments model
    from app.models.assignment import Assignment, assignments

    # Validate max_drafts
    try:
        max_drafts = int(max_drafts)
        if max_drafts < 1:
            max_drafts = 1
    except:
        max_drafts = 3  # Default to 3 if invalid

    # Validate status
    if status not in ["draft", "active", "closed", "archived"]:
        status = "draft"  # Default to draft if invalid

    # Get next assignment ID
    next_assignment_id = 1
    try:
        assignment_ids = [a.id for a in assignments()]
        if assignment_ids:
            next_assignment_id = max(assignment_ids) + 1
    except:
        next_assignment_id = 1

    # Create timestamp
    from datetime import datetime

    now = datetime.now().isoformat()

    # Create new assignment
    new_assignment = Assignment(
        id=next_assignment_id,
        course_id=course_id,
        title=title,
        description=description,
        due_date=due_date,
        max_drafts=max_drafts,
        created_by=user.email,
        status=status,
        created_at=now,
        updated_at=now,
    )

    # Insert into database
    assignments.insert(new_assignment)

    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3(
                        "Assignment Created Successfully!",
                        cls="text-xl font-bold text-green-700 mb-1",
                    ),
                    P(
                        f'Your assignment "{title}" has been created.',
                        cls="text-gray-600",
                    ),
                    cls="",
                ),
                cls="flex items-center mb-6",
            ),
            Div(
                A(
                    "Back to Assignments",
                    href=f"/instructor/courses/{course_id}/assignments",
                    cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200",
                ),
                A(
                    "Create Rubric",
                    href=f"/instructor/assignments/{next_assignment_id}/rubric",
                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4",
                ),
                A(
                    "View Assignment",
                    href=f"/instructor/assignments/{next_assignment_id}",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                ),
                cls="flex justify-center gap-4",
            ),
            cls="text-center",
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4",
    )


@rt("/instructor/assignments/{assignment_id}")
@instructor_required
def get(session, assignment_id: int):
    """View individual assignment details"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get the course this assignment belongs to
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get submissions for this assignment if any
    from app.models.feedback import drafts

    # Check if there are any drafts/submissions
    submission_count = 0
    for draft in drafts():
        if draft.assignment_id == assignment_id:
            submission_count += 1

    # Create main content with assignment details
    main_content = Div(
        # Top banner showing status
        Div(
            Div(
                Span(
                    getattr(assignment, "status", "draft").capitalize(),
                    cls="text-xl font-semibold "
                    + (
                        "text-gray-700"
                        if getattr(assignment, "status", "draft") == "draft"
                        else "text-green-700"
                        if getattr(assignment, "status", "draft") == "active"
                        else "text-amber-700"
                        if getattr(assignment, "status", "draft") == "closed"
                        else "text-blue-700"
                    ),
                ),
                P("Assignment Status", cls="text-gray-600"),
                cls="py-2 px-6",
            ),
            Div(
                Span(
                    getattr(assignment, "due_date", "Not set") or "Not set",
                    cls="text-xl font-semibold text-indigo-700",
                ),
                P("Due Date", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200",
            ),
            Div(
                Span(
                    str(getattr(assignment, "max_drafts", 1) or 1) + " drafts",
                    cls="text-xl font-semibold text-indigo-700",
                ),
                P("Maximum Drafts", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200",
            ),
            Div(
                Span(
                    f"{submission_count} submissions",
                    cls="text-xl font-semibold text-indigo-700",
                ),
                P("Student Submissions", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200",
            ),
            cls="flex justify-between mb-6 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Assignment details
        Div(
            H2(assignment.title, cls="text-2xl font-bold text-indigo-900 mb-4"),
            # Description
            Div(
                H3(
                    "Assignment Description",
                    cls="text-lg font-semibold text-indigo-800 mb-3",
                ),
                Div(
                    P(
                        assignment.description.replace("\n", "<br>")
                        if assignment.description
                        else "No description provided.",
                        cls="text-gray-700 whitespace-pre-line",
                    ),
                    cls="py-4",
                ),
                cls="mb-6 bg-white rounded-xl shadow-md border border-gray-100 p-4",
            ),
            # Actions
            Div(
                H3(
                    "Assignment Actions",
                    cls="text-lg font-semibold text-indigo-800 mb-3",
                ),
                Div(
                    A(
                        "Edit Assignment",
                        href=f"/instructor/assignments/{assignment_id}/edit",
                        cls="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 mr-4",
                    ),
                    A(
                        "Manage Rubric",
                        href=f"/instructor/assignments/{assignment_id}/rubric",
                        cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4",
                    ),
                    A(
                        "View Submissions",
                        href=f"/instructor/assignments/{assignment_id}/submissions",
                        cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                    ),
                    cls="flex",
                ),
                cls="mb-6 bg-white rounded-xl shadow-md border border-gray-100 p-4",
            ),
            # Status change
            Div(
                H3(
                    "Change Assignment Status",
                    cls="text-lg font-semibold text-indigo-800 mb-3",
                ),
                Form(
                    P(
                        "Changing the assignment status affects student access and submission ability.",
                        cls="text-gray-600 mb-3",
                    ),
                    Div(
                        Select(
                            Option(
                                "Draft - Only visible to you",
                                value="draft",
                                selected=getattr(assignment, "status", "draft")
                                == "draft",
                            ),
                            Option(
                                "Active - Available to students",
                                value="active",
                                selected=getattr(assignment, "status", "draft")
                                == "active",
                            ),
                            Option(
                                "Closed - No new submissions",
                                value="closed",
                                selected=getattr(assignment, "status", "draft")
                                == "closed",
                            ),
                            Option(
                                "Archived - Hidden from students",
                                value="archived",
                                selected=getattr(assignment, "status", "draft")
                                == "archived",
                            ),
                            name="status",
                            cls="p-3 border border-gray-300 rounded-lg mr-3",
                        ),
                        Button(
                            "Update Status",
                            type="submit",
                            cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                        ),
                        cls="flex items-center",
                    ),
                    Div(id="status-result", cls="mt-3"),
                    hx_post=f"/instructor/assignments/{assignment_id}/status",
                    hx_target="#status-result",
                    cls="",
                ),
                cls="bg-white rounded-xl shadow-md border border-gray-100 p-4",
            ),
            cls="",
        ),
        cls="",
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3(
                "Assignment Navigation",
                cls="text-xl font-semibold text-indigo-900 mb-4",
            ),
            Div(
                action_button(
                    "Back to Course",
                    color="gray",
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    icon="←",
                ),
                action_button(
                    "Edit Assignment",
                    color="amber",
                    href=f"/instructor/assignments/{assignment_id}/edit",
                    icon="✏️",
                ),
                action_button(
                    "Manage Rubric",
                    color="teal",
                    href=f"/instructor/assignments/{assignment_id}/rubric",
                    icon="📊",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Course Details", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Course: {course.title}", cls="text-gray-700 font-medium mb-2"),
            P(f"Code: {course.code}", cls="text-gray-600 mb-2"),
            P(
                f"Status: {getattr(course, 'status', 'active').capitalize()}",
                cls="text-gray-600 mb-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Student Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Submissions: {submission_count}", cls="text-gray-700 font-medium mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return dashboard_layout(
        f"{assignment.title} | {course.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/assignments/{assignment_id}/status")
@instructor_required
def post(session, assignment_id: int, status: str):
    """Update assignment status"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Validate status
    if status not in ["draft", "active", "closed", "archived", "deleted"]:
        return "Invalid status. Please select a valid status."

    # Check course status - don't allow active assignments for closed/archived/deleted courses
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return f"Error: {course_error}"

    if (
        status == "active"
        and hasattr(course, "status")
        and course.status in ["closed", "archived", "deleted"]
    ):
        return (
            f"Cannot set assignment to 'active' when the course is '{course.status}'."
        )

    # Update timestamp
    from datetime import datetime

    now = datetime.now().isoformat()

    # Update assignment status
    from app.models.assignment import assignments

    old_status = assignment.status if hasattr(assignment, "status") else "draft"
    assignment.status = status
    assignment.updated_at = now

    # Save to database
    assignments.update(assignment)

    # Return success message with auto-refresh
    return Div(
        P(
            f"Assignment status updated from '{old_status}' to '{status}'.",
            cls="text-green-600",
        ),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-3 rounded-lg",
    )


@rt("/instructor/assignments/{assignment_id}/edit")
@instructor_required
def get(session, assignment_id: int):
    """Form to edit an existing assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get the course
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Form to edit the assignment
    form_content = Div(
        H2("Edit Assignment", cls="text-2xl font-bold text-indigo-900 mb-6"),
        P(
            f"Update the details for your assignment in {course.title}.",
            cls="text-gray-600 mb-6",
        ),
        Form(
            # Title field
            Div(
                Label(
                    "Assignment Title",
                    for_="title",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Input(
                    id="title",
                    name="title",
                    type="text",
                    value=assignment.title,
                    required=True,
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-4",
            ),
            # Description field
            Div(
                Label(
                    "Assignment Description",
                    for_="description",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Textarea(
                    id="description",
                    name="description",
                    rows="6",
                    value=getattr(assignment, "description", ""),
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-4",
            ),
            # Due date and max drafts
            Div(
                Div(
                    Label(
                        "Due Date (Optional)",
                        for_="due_date",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="due_date",
                        name="due_date",
                        type="date",
                        value=getattr(assignment, "due_date", ""),
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="w-1/2 pr-2",
                ),
                Div(
                    Label(
                        "Maximum Drafts",
                        for_="max_drafts",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="max_drafts",
                        name="max_drafts",
                        type="number",
                        min="1",
                        value=getattr(assignment, "max_drafts", 3) or 3,
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="w-1/2 pl-2",
                ),
                cls="flex mb-4",
            ),
            # Status selection
            Div(
                Label(
                    "Assignment Status",
                    for_="status",
                    cls="block text-indigo-900 font-medium mb-1",
                ),
                Select(
                    Option(
                        "Draft - Only visible to you",
                        value="draft",
                        selected=getattr(assignment, "status", "draft") == "draft",
                    ),
                    Option(
                        "Active - Available to students",
                        value="active",
                        selected=getattr(assignment, "status", "draft") == "active",
                    ),
                    Option(
                        "Closed - No new submissions",
                        value="closed",
                        selected=getattr(assignment, "status", "draft") == "closed",
                    ),
                    Option(
                        "Archived - Hidden from students",
                        value="archived",
                        selected=getattr(assignment, "status", "draft") == "archived",
                    ),
                    id="status",
                    name="status",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                ),
                cls="mb-6",
            ),
            # Submit button
            Div(
                Button(
                    "Update Assignment",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                ),
                cls="mb-4",
            ),
            # Result placeholder
            Div(id="result"),
            # Form submission details
            hx_post=f"/instructor/assignments/{assignment_id}/edit",
            hx_target="#result",
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
        ),
        cls="",
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Assignment Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Assignment",
                    color="gray",
                    href=f"/instructor/assignments/{assignment_id}",
                    icon="←",
                ),
                action_button(
                    "Course Assignments",
                    color="indigo",
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    icon="📚",
                ),
                action_button(
                    "Manage Rubric",
                    color="teal",
                    href=f"/instructor/assignments/{assignment_id}/rubric",
                    icon="📊",
                ),
                action_button(
                    "View Submissions",
                    color="amber",
                    href=f"/instructor/assignments/{assignment_id}/submissions",
                    icon="📝",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Editing Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Clear instructions help students understand expectations",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Set realistic draft limits for meaningful feedback",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Consider creating a rubric for structured feedback",
                cls="text-gray-600 text-sm",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Return the complete page
    return dashboard_layout(
        f"Edit Assignment | {course.title} | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/assignments/{assignment_id}/edit")
@instructor_required
def post(
    session,
    assignment_id: int,
    title: str,
    description: str,
    due_date: str = "",
    max_drafts: int = 3,
    status: str = "draft",
):
    """Handle assignment update"""
    # Get current user
    user = users[session["auth"]]

    # Validate required fields
    if not title:
        return "Assignment title is required."

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Get the course
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return f"Error: {course_error}"

    # Validate max_drafts
    try:
        max_drafts = int(max_drafts)
        if max_drafts < 1:
            max_drafts = 1
    except:
        max_drafts = 3  # Default to 3 if invalid

    # Validate status
    if status not in ["draft", "active", "closed", "archived", "deleted"]:
        status = "draft"  # Default to draft if invalid

    # Check course status - don't allow active assignments for closed/archived/deleted courses
    if (
        status == "active"
        and hasattr(course, "status")
        and course.status in ["closed", "archived", "deleted"]
    ):
        return (
            f"Cannot set assignment to 'active' when the course is '{course.status}'."
        )

    # Update timestamp
    from datetime import datetime

    now = datetime.now().isoformat()

    # Update assignment fields
    assignment.title = title
    assignment.description = description
    assignment.due_date = due_date
    assignment.max_drafts = max_drafts
    assignment.status = status
    assignment.updated_at = now

    # Save to database
    from app.models.assignment import assignments

    assignments.update(assignment)

    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3(
                        "Assignment Updated Successfully!",
                        cls="text-xl font-bold text-green-700 mb-1",
                    ),
                    P(
                        f'Your assignment "{title}" has been updated.',
                        cls="text-gray-600",
                    ),
                    cls="",
                ),
                cls="flex items-center mb-6",
            ),
            Div(
                A(
                    "Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200",
                ),
                A(
                    "Manage Rubric",
                    href=f"/instructor/assignments/{assignment_id}/rubric",
                    cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4",
                ),
                A(
                    "View Submissions",
                    href=f"/instructor/assignments/{assignment_id}/submissions",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                ),
                cls="flex justify-center gap-4",
            ),
            cls="text-center",
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4",
    )


# --- Rubric Management ---
@rt("/instructor/assignments/{assignment_id}/rubric")
@instructor_required
def get(session, assignment_id: int):
    """View and manage rubric for an assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Get the course this assignment belongs to
    course, course_error = get_instructor_course(assignment.course_id, user.email)

    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Import rubric models
    from app.models.assignment import rubric_categories, rubrics

    # Check if rubric exists for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break

    # Get rubric categories if rubric exists
    categories = []
    if rubric:
        for category in rubric_categories():
            if category.rubric_id == rubric.id:
                categories.append(category)

        # Sort categories by ID for consistent display
        categories.sort(key=lambda x: x.id)

    # Prepare form for creating/editing rubric
    if rubric:
        # Rubric exists - show edit form
        form_content = Div(
            H2(
                f"Manage Rubric for: {assignment.title}",
                cls="text-2xl font-bold text-indigo-900 mb-4",
            ),
            P(
                "Edit the rubric categories and their weights. The weights should sum to 100%.",
                cls="text-gray-600 mb-6",
            ),
            # Existing categories display and edit form
            Div(
                # Header section with assignment info
                Div(
                    P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    P(
                        f"Status: {getattr(assignment, 'status', 'draft').capitalize()}",
                        cls="text-gray-600",
                    ),
                    cls="mb-4",
                ),
                # Current categories
                H3(
                    "Current Rubric Categories",
                    cls="text-xl font-semibold text-indigo-800 mb-3",
                ),
                # Category display and edit section
                (
                    Div(
                        Div(
                            Table(
                                Thead(
                                    Tr(
                                        Th(
                                            "Category Name",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        Th(
                                            "Description",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        Th(
                                            "Weight (%)",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                        Th(
                                            "Actions",
                                            cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        ),
                                    ),
                                    cls="bg-indigo-50",
                                ),
                                Tbody(
                                    *[
                                        Tr(
                                            Td(
                                                category.name,
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            Td(
                                                Div(
                                                    P(
                                                        category.description,
                                                        cls="text-gray-700 max-w-md",
                                                    ),
                                                    cls="max-h-24 overflow-y-auto",
                                                ),
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            Td(
                                                f"{category.weight}%",
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            Td(
                                                Div(
                                                    Button(
                                                        "Edit",
                                                        hx_get=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/edit",
                                                        hx_target="#category-edit-form",
                                                        cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                                    ),
                                                    Button(
                                                        "Delete",
                                                        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/delete",
                                                        hx_confirm=f"Are you sure you want to delete the category '{category.name}'?",
                                                        hx_target="#rubric-result",
                                                        cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                                                    ),
                                                    cls="flex",
                                                ),
                                                cls="py-3 px-4 border-b border-gray-100",
                                            ),
                                            # Add unique id to each row for potential HTMX interactions
                                            id=f"category-row-{category.id}",
                                            cls="hover:bg-gray-50",
                                        )
                                        for category in categories
                                    ]
                                ),
                                cls="w-full",
                            ),
                            cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100 mb-6",
                        )
                        if categories
                        else P(
                            "No rubric categories have been created yet. Use the form below to add categories to your rubric.",
                            cls="bg-amber-50 p-4 rounded-lg border border-amber-200 text-amber-800 mb-6",
                        )
                    )
                ),
                # Add new category section
                Div(
                    H3(
                        "Add New Category",
                        cls="text-xl font-semibold text-indigo-800 mb-3",
                    ),
                    Div(id="category-edit-form", cls="mb-4"),
                    Form(
                        Input(type="hidden", name="category_id", value=""),
                        Div(
                            Label(
                                "Category Name",
                                for_="name",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            Input(
                                id="name",
                                name="name",
                                type="text",
                                placeholder="e.g. Content",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label(
                                "Description",
                                for_="description",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            Textarea(
                                id="description",
                                name="description",
                                rows="3",
                                placeholder="Describe what this category evaluates...",
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Label(
                                "Weight (%)",
                                for_="weight",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            Input(
                                id="weight",
                                name="weight",
                                type="number",
                                min="1",
                                max="100",
                                step="0.1",
                                placeholder="e.g. 25",
                                required=True,
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        Div(
                            Button(
                                "Add Category",
                                type="submit",
                                cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                            ),
                            cls="mb-4",
                        ),
                        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/add",
                        hx_target="#rubric-result",
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6",
                    ),
                ),
                # Result placeholder for form submissions
                Div(id="rubric-result", cls="mb-6"),
                # Action buttons
                Div(
                    A(
                        "Back to Assignment",
                        href=f"/instructor/assignments/{assignment_id}",
                        cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4",
                    ),
                    cls="flex",
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
            ),
            cls="",
        )
    else:
        # No rubric exists - show creation form
        form_content = Div(
            H2(
                f"Create Rubric for: {assignment.title}",
                cls="text-2xl font-bold text-indigo-900 mb-4",
            ),
            P(
                "A rubric helps provide structured feedback for students. Create a rubric by defining categories and their weights.",
                cls="text-gray-600 mb-6",
            ),
            # Rubric creation form
            Div(
                # Header section with assignment info
                Div(
                    P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    P(
                        f"Status: {getattr(assignment, 'status', 'draft').capitalize()}",
                        cls="text-gray-600",
                    ),
                    cls="mb-6",
                ),
                # Initialize rubric form
                Form(
                    H3(
                        "Initialize Rubric",
                        cls="text-xl font-semibold text-indigo-800 mb-3",
                    ),
                    P(
                        "Create a rubric for this assignment to define evaluation criteria.",
                        cls="text-gray-600 mb-4",
                    ),
                    Div(
                        Button(
                            "Create Rubric",
                            type="submit",
                            cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm",
                        ),
                        cls="mb-4",
                    ),
                    Div(id="create-rubric-result", cls="mt-4"),
                    hx_post=f"/instructor/assignments/{assignment_id}/rubric/create",
                    hx_target="#create-rubric-result",
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6",
                ),
                # Action buttons
                Div(
                    A(
                        "Back to Assignment",
                        href=f"/instructor/assignments/{assignment_id}",
                        cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4",
                    ),
                    cls="flex",
                ),
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
            ),
            cls="",
        )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Rubric Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Assignment",
                    color="gray",
                    href=f"/instructor/assignments/{assignment_id}",
                    icon="←",
                ),
                action_button(
                    "Assignment List",
                    color="indigo",
                    href=f"/instructor/courses/{assignment.course_id}/assignments",
                    icon="📚",
                ),
                action_button(
                    "Edit Assignment",
                    color="amber",
                    href=f"/instructor/assignments/{assignment_id}/edit",
                    icon="✏️",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Rubric Tips", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(
                "• Create 3-5 categories for a balanced rubric",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P("• Ensure weights add up to 100%", cls="text-gray-600 mb-2 text-sm"),
            P(
                "• Use clear descriptions that guide students",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Consider including examples in descriptions",
                cls="text-gray-600 text-sm",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Template Library", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                Button(
                    "Essay Rubric Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/essay",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left",
                ),
                Button(
                    "Research Paper Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/research",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left",
                ),
                Button(
                    "Presentation Template",
                    hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/presentation",
                    hx_target="#rubric-result",
                    cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 w-full text-left",
                ),
                cls="space-y-2",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        cls="space-y-6",
    )

    # Return complete page
    return dashboard_layout(
        f"Rubric for {assignment.title} | {course.title} | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/assignments/{assignment_id}/rubric/create")
@instructor_required
def post(session, assignment_id: int):
    """Create a new rubric for an assignment"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Import rubric models
    from app.models.assignment import Rubric, rubrics

    # Check if rubric already exists
    for rubric in rubrics():
        if rubric.assignment_id == assignment_id:
            return Div(
                P("A rubric already exists for this assignment.", cls="text-amber-600"),
                cls="bg-amber-50 p-4 rounded-lg",
            )

    # Get next rubric ID
    next_rubric_id = 1
    try:
        rubric_ids = [r.id for r in rubrics()]
        if rubric_ids:
            next_rubric_id = max(rubric_ids) + 1
    except Exception as e:
        print(f"Error getting next rubric ID: {e}")
        next_rubric_id = 1

    # Create new rubric
    new_rubric = Rubric(id=next_rubric_id, assignment_id=assignment_id)

    # Insert into database
    rubrics.insert(new_rubric)

    # Return success message with page refresh
    return Div(
        P(
            "Rubric created successfully! You can now add categories.",
            cls="text-green-600 font-medium",
        ),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-4 rounded-lg",
    )


@rt("/instructor/assignments/{assignment_id}/rubric/categories/add")
@instructor_required
def post(
    session,
    assignment_id: int,
    name: str,
    description: str = "",
    weight: float = 0,
    category_id: int = None,
):
    """Add a new category to a rubric or update an existing one"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Import rubric models
    from app.models.assignment import RubricCategory, rubric_categories, rubrics

    # Find the rubric for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break

    if not rubric:
        return Div(
            P(
                "Error: No rubric found for this assignment. Please create a rubric first.",
                cls="text-red-600",
            ),
            cls="bg-red-50 p-4 rounded-lg",
        )

    # Validate inputs
    if not name:
        return Div(
            P("Error: Category name is required.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )

    try:
        weight = float(weight)
        if weight <= 0 or weight > 100:
            return Div(
                P("Error: Weight must be between 0 and 100.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg",
            )
    except:
        return Div(
            P("Error: Invalid weight value.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )

    # Check if we're updating existing category or adding new one
    if category_id:
        # Updating existing category
        for category in rubric_categories():
            if category.id == category_id and category.rubric_id == rubric.id:
                # Update category
                category.name = name
                category.description = description
                category.weight = weight
                rubric_categories.update(category)

                return Div(
                    P(f"Category '{name}' updated successfully!", cls="text-green-600"),
                    Script(
                        "setTimeout(function() { window.location.reload(); }, 1000);"
                    ),
                    cls="bg-green-50 p-4 rounded-lg",
                )

        return Div(
            P(
                "Error: Category not found or doesn't belong to this rubric.",
                cls="text-red-600",
            ),
            cls="bg-red-50 p-4 rounded-lg",
        )

    # Adding new category
    # Get next category ID
    next_category_id = 1
    try:
        category_ids = [c.id for c in rubric_categories()]
        if category_ids:
            next_category_id = max(category_ids) + 1
    except Exception as e:
        print(f"Error getting next category ID: {e}")
        next_category_id = 1

    # Create new category
    new_category = RubricCategory(
        id=next_category_id,
        rubric_id=rubric.id,
        name=name,
        description=description,
        weight=weight,
    )

    # Insert into database
    rubric_categories.insert(new_category)

    # Return success message with form reset
    return Div(
        P(f"Category '{name}' added successfully!", cls="text-green-600"),
        Script("""
            document.getElementById('name').value = '';
            document.getElementById('description').value = '';
            document.getElementById('weight').value = '';
            document.getElementById('category_id').value = '';
            setTimeout(function() { window.location.reload(); }, 1000);
        """),
        cls="bg-green-50 p-4 rounded-lg",
    )


@rt("/instructor/assignments/{assignment_id}/rubric/categories/{category_id}/edit")
@instructor_required
def get(session, assignment_id: int, category_id: int):
    """Get the form for editing a rubric category"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Import rubric models
    from app.models.assignment import rubric_categories

    # Find the category
    category = None
    for c in rubric_categories():
        if c.id == category_id:
            category = c
            break

    if not category:
        return "Category not found."

    # Return edit form
    return Form(
        H3("Edit Category", cls="text-xl font-semibold text-indigo-800 mb-3"),
        Input(type="hidden", name="category_id", value=str(category.id)),
        Div(
            Label(
                "Category Name",
                for_="name",
                cls="block text-indigo-900 font-medium mb-1",
            ),
            Input(
                id="name",
                name="name",
                type="text",
                value=category.name,
                required=True,
                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
            ),
            cls="mb-4",
        ),
        Div(
            Label(
                "Description",
                for_="description",
                cls="block text-indigo-900 font-medium mb-1",
            ),
            Textarea(
                id="description",
                name="description",
                rows="3",
                value=category.description,
                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
            ),
            cls="mb-4",
        ),
        Div(
            Label(
                "Weight (%)",
                for_="weight",
                cls="block text-indigo-900 font-medium mb-1",
            ),
            Input(
                id="weight",
                name="weight",
                type="number",
                min="1",
                max="100",
                step="0.1",
                value=str(category.weight),
                required=True,
                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
            ),
            cls="mb-4",
        ),
        Div(
            Button(
                "Update Category",
                type="submit",
                cls="bg-amber-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-amber-700 transition-colors shadow-sm",
            ),
            Button(
                "Cancel",
                hx_get=f"/instructor/assignments/{assignment_id}/rubric/categories/cancel",
                hx_target="#category-edit-form",
                cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors shadow-sm ml-3",
            ),
            cls="mb-4",
        ),
        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/add",
        hx_target="#rubric-result",
        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6",
    )


@rt("/instructor/assignments/{assignment_id}/rubric/categories/cancel")
@instructor_required
def get(session, assignment_id: int):
    """Cancel category editing"""
    return ""


@rt("/instructor/assignments/{assignment_id}/rubric/categories/{category_id}/delete")
@instructor_required
def post(session, assignment_id: int, category_id: int):
    """Delete a rubric category"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Import rubric models
    from app.models.assignment import rubric_categories

    # Find the category
    category_name = "Unknown"
    for c in rubric_categories():
        if c.id == category_id:
            category_name = c.name
            # Delete the category
            rubric_categories.delete(c.id)
            break

    # Return success message with page refresh
    return Div(
        P(f"Category '{category_name}' deleted successfully.", cls="text-green-600"),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-4 rounded-lg",
    )


@rt("/instructor/assignments/{assignment_id}/rubric/template/{template_type}")
@instructor_required
def get(session, assignment_id: int, template_type: str):
    """Apply a rubric template"""
    # Get current user
    user = users[session["auth"]]

    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)

    if error:
        return f"Error: {error}"

    # Import rubric models
    from app.models.assignment import RubricCategory, rubric_categories, rubrics

    # Find the rubric for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break

    if not rubric:
        return Div(
            P(
                "Error: No rubric found for this assignment. Please create a rubric first.",
                cls="text-red-600",
            ),
            cls="bg-red-50 p-4 rounded-lg",
        )

    # Check if rubric already has categories
    existing_categories = []
    for c in rubric_categories():
        if c.rubric_id == rubric.id:
            existing_categories.append(c)

    if existing_categories:
        return Div(
            P(
                "This rubric already has categories. Templates can only be applied to empty rubrics.",
                cls="text-amber-600",
            ),
            cls="bg-amber-50 p-4 rounded-lg",
        )

    # Define template categories based on type
    template_categories = []
    if template_type == "essay":
        template_categories = [
            {
                "name": "Content",
                "description": "The essay addresses the assigned topic thoroughly and presents a clear thesis statement. Arguments are well-developed with relevant evidence and examples.",
                "weight": 30,
            },
            {
                "name": "Organization",
                "description": "The essay follows a logical structure with clear introduction, body paragraphs, and conclusion. Ideas flow smoothly with effective transitions.",
                "weight": 25,
            },
            {
                "name": "Analysis",
                "description": "The essay demonstrates critical thinking and insightful analysis. Arguments are thoughtful and demonstrate understanding of the topic's complexity.",
                "weight": 20,
            },
            {
                "name": "Style & Language",
                "description": "Writing is clear, concise, and appropriate for academic context. Grammar, punctuation, and spelling are correct. Vocabulary is varied and precise.",
                "weight": 15,
            },
            {
                "name": "Citations & References",
                "description": "Sources are properly cited using the required citation style. References are relevant, credible, and integrated effectively.",
                "weight": 10,
            },
        ]
    elif template_type == "research":
        template_categories = [
            {
                "name": "Research Question",
                "description": "Clear, focused research question or hypothesis. Demonstrates significance and originality within the field.",
                "weight": 15,
            },
            {
                "name": "Literature Review",
                "description": "Comprehensive review of relevant literature. Synthesizes prior research and identifies gaps.",
                "weight": 20,
            },
            {
                "name": "Methodology",
                "description": "Research design and methods are appropriate, clearly described, and aligned with research questions.",
                "weight": 20,
            },
            {
                "name": "Data Analysis & Results",
                "description": "Data is accurately analyzed using appropriate methods. Results are presented clearly with relevant tables/figures.",
                "weight": 25,
            },
            {
                "name": "Discussion & Conclusion",
                "description": "Interpretation of results is insightful and connected to the literature. Limitations are acknowledged and future research directions suggested.",
                "weight": 15,
            },
            {
                "name": "Citations & Format",
                "description": "Follows required citation style and formatting guidelines. References are accurate and complete.",
                "weight": 5,
            },
        ]
    elif template_type == "presentation":
        template_categories = [
            {
                "name": "Content",
                "description": "Presentation covers topic thoroughly with accurate, relevant information. Key points are supported with evidence.",
                "weight": 30,
            },
            {
                "name": "Organization",
                "description": "Clear structure with logical flow. Includes effective introduction, well-organized body, and strong conclusion.",
                "weight": 20,
            },
            {
                "name": "Visual Elements",
                "description": "Slides are clear, readable, and visually appealing. Graphics enhance understanding without overwhelming.",
                "weight": 15,
            },
            {
                "name": "Delivery",
                "description": "Speaker demonstrates confidence, maintains good pace, and uses appropriate voice projection. Engages audience and maintains eye contact.",
                "weight": 25,
            },
            {
                "name": "Q&A Handling",
                "description": "Responds to questions clearly and accurately. Demonstrates depth of knowledge on the topic.",
                "weight": 10,
            },
        ]
    else:
        return Div(
            P(f"Unknown template type: {template_type}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )

    # Get next category ID
    next_category_id = 1
    try:
        category_ids = [c.id for c in rubric_categories()]
        if category_ids:
            next_category_id = max(category_ids) + 1
    except Exception as e:
        print(f"Error getting next category ID: {e}")
        next_category_id = 1

    # Add template categories to rubric
    for template in template_categories:
        new_category = RubricCategory(
            id=next_category_id,
            rubric_id=rubric.id,
            name=template["name"],
            description=template["description"],
            weight=template["weight"],
        )
        rubric_categories.insert(new_category)
        next_category_id += 1

    # Return success message with page refresh
    template_names = {
        "essay": "Essay",
        "research": "Research Paper",
        "presentation": "Presentation",
    }

    return Div(
        P(
            f"{template_names.get(template_type, template_type.title())} template applied successfully!",
            cls="text-green-600",
        ),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-4 rounded-lg",
    )


# --- Course Management ---
# Helper function to get a course by ID with instructor permission check
def get_instructor_course(course_id, instructor_email):
    """
    Get a course by ID, checking that it belongs to the instructor.
    Returns (course, error_message) tuple.
    """
    # Find the course
    target_course = None
    try:
        for course in courses():
            if course.id == course_id:
                target_course = course
                break

        if not target_course:
            return None, "Course not found."

        # Check if this instructor owns the course
        if target_course.instructor_email != instructor_email:
            return None, "You don't have permission to access this course."

        # Skip deleted courses
        if hasattr(target_course, "status") and target_course.status == "deleted":
            return None, "This course has been deleted."

        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {e!s}"


@rt("/instructor/courses")
@instructor_required
def get(session, request):
    """Course listing page for instructors"""
    # Get current user
    user = users[session["auth"]]

    # Get all courses taught by this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, "status") and course.status == "deleted":
                continue

            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1

            # Add to list with student count
            instructor_courses.append((course, student_count))

    # Sort courses by creation date (newest first)
    instructor_courses.sort(
        key=lambda x: x[0].created_at if hasattr(x[0], "created_at") else "",
        reverse=True,
    )

    # Create the main content
    main_content = Div(
        # Header with action button
        Div(
            H2("Course Management", cls="text-2xl font-bold text-indigo-900"),
            action_button(
                "Create New Course",
                color="indigo",
                href="/instructor/courses/new",
                icon="+",
            ),
            cls="flex justify-between items-center mb-6",
        ),
        # Course listing or empty state
        (
            Div(
                P(
                    f"You have {len(instructor_courses)} {'course' if len(instructor_courses) == 1 else 'courses'}.",
                    cls="text-gray-600 mb-6",
                ),
                # Course table with actions
                Div(
                    Table(
                        Thead(
                            Tr(
                                Th(
                                    "Course Title",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Code",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Term",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Status",
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                ),
                                Th(
                                    "Students",
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
                                    # Course title
                                    Td(course.title, cls="py-4 px-6"),
                                    # Course code
                                    Td(course.code, cls="py-4 px-6"),
                                    # Term
                                    Td(
                                        getattr(course, "term", "Current") or "Current",
                                        cls="py-4 px-6",
                                    ),
                                    # Status badge
                                    Td(
                                        status_badge(
                                            getattr(
                                                course, "status", "active"
                                            ).capitalize()
                                            or "Active",
                                            "green"
                                            if getattr(course, "status", "active")
                                            == "active"
                                            else "yellow"
                                            if getattr(course, "status", "active")
                                            == "closed"
                                            else "gray",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                    # Student count
                                    Td(str(student_count), cls="py-4 px-6"),
                                    # Action buttons
                                    Td(
                                        Div(
                                            A(
                                                "Students",
                                                href=f"/instructor/courses/{course.id}/students",
                                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                                            ),
                                            A(
                                                "Edit",
                                                href=f"/instructor/courses/{course.id}/edit",
                                                cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2",
                                            ),
                                            A(
                                                "Assignments",
                                                href=f"/instructor/courses/{course.id}/assignments",
                                                cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700",
                                            ),
                                            cls="flex",
                                        ),
                                        cls="py-4 px-6",
                                    ),
                                )
                                for course, student_count in instructor_courses
                            )
                        ),
                        cls="w-full",
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                ),
                cls="",
            )
            if instructor_courses
            else Div(
                P(
                    "You don't have any courses yet. Create your first course to get started.",
                    cls="text-center text-gray-600 mb-6",
                ),
                Div(
                    A(
                        "Create New Course",
                        href="/instructor/courses/new",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="text-center",
                ),
                cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4",
            )
        ),
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="←"
                ),
                action_button(
                    "Create Course",
                    color="indigo",
                    href="/instructor/courses/new",
                    icon="+",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href="/instructor/manage-students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total Courses: {len(instructor_courses)}", cls="text-gray-600 mb-2"),
            P(
                f"Active Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'active')}",
                cls="text-green-600 mb-2",
            ),
            P(
                f"Closed Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'closed')}",
                cls="text-amber-600 mb-2",
            ),
            P(
                f"Archived Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'archived')}",
                cls="text-gray-600 mb-2",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Courses | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path,
    )


@rt("/instructor/courses/new")
@instructor_required
def get(session):
    # Get components directly from top-level imports

    # Get current user
    user = users[session["auth"]]

    # Create the form content
    form_content = Div(
        H2("Create New Course", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P(
                "Complete the form below to create a new course for your students.",
                cls="mb-6 text-gray-600",
            ),
            Form(
                Div(
                    Label(
                        "Course Title",
                        for_="title",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="title",
                        name="title",
                        type="text",
                        placeholder="e.g. Introduction to Computer Science",
                        required=True,
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                Div(
                    Label(
                        "Course Code",
                        for_="code",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="code",
                        name="code",
                        type="text",
                        placeholder="e.g. CS101",
                        required=True,
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                # Add new fields for term, department, and status
                Div(
                    Div(
                        Label(
                            "Term",
                            for_="term",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Input(
                            id="term",
                            name="term",
                            type="text",
                            placeholder="e.g. Fall 2023",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="w-1/2 pr-2",
                    ),
                    Div(
                        Label(
                            "Department",
                            for_="department",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Input(
                            id="department",
                            name="department",
                            type="text",
                            placeholder="e.g. Computer Science",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="w-1/2 pl-2",
                    ),
                    cls="flex mb-4",
                ),
                Div(
                    Label(
                        "Status",
                        for_="status",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Select(
                        Option("Active", value="active", selected=True),
                        Option("Closed", value="closed"),
                        Option("Archived", value="archived"),
                        id="status",
                        name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                Div(
                    Label(
                        "Description",
                        for_="description",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Textarea(
                        id="description",
                        name="description",
                        placeholder="Provide a brief description of the course",
                        rows="4",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-6",
                ),
                Div(
                    Button(
                        "Create Course",
                        type="submit",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="mb-4",
                ),
                Div(id="result", cls=""),
                hx_post="/instructor/courses/new",
                hx_target="#result",
                cls="w-full",
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
        ),
        cls="",
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Manage Courses",
                    color="indigo",
                    href="/instructor/courses",
                    icon="📚",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Choose a clear, descriptive course title",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Use official course codes when possible",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Include key information in the description",
                cls="text-gray-600 text-sm",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Create Course | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/courses/new")
@instructor_required
def post(
    session,
    title: str,
    code: str,
    term: str = "",
    department: str = "",
    status: str = "active",
    description: str = "",
):
    # Get current user
    user = users[session["auth"]]

    # Validate input
    if not title or not code:
        return "Course title and code are required."

    # Check for duplicate course code
    for course in courses():
        if course.code == code and course.instructor_email == user.email:
            # Only check for duplicates from the same instructor
            # If the course is deleted, allow reuse of code
            if not hasattr(course, "status") or course.status != "deleted":
                return "You already have a course with this code. Please use a different code."

    # Validate status
    if status not in ["active", "closed", "archived"]:
        status = "active"  # Default to active if invalid

    # Get next course ID
    next_course_id = 1
    try:
        course_ids = [c.id for c in courses()]
        if course_ids:
            next_course_id = max(course_ids) + 1
    except:
        next_course_id = 1

    # Create timestamp
    now = datetime.now().isoformat()

    # Create new course
    new_course = Course(
        id=next_course_id,
        title=title,
        code=code,
        term=term,
        department=department,
        status=status,
        instructor_email=user.email,
        created_at=now,
        updated_at=now,
    )

    # Insert into database
    courses.insert(new_course)

    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3(
                        "Course Created Successfully!",
                        cls="text-xl font-bold text-green-700 mb-1",
                    ),
                    P(f'Your course "{title}" has been created.', cls="text-gray-600"),
                    cls="",
                ),
                cls="flex items-center mb-6",
            ),
            Div(
                A(
                    "Return to Dashboard",
                    href="/instructor/dashboard",
                    cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200",
                ),
                A(
                    "Manage Courses",
                    href="/instructor/courses",
                    cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-4 hover:bg-amber-700",
                ),
                A(
                    "Invite Students",
                    href=f"/instructor/invite-students?course_id={next_course_id}",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                ),
                cls="flex justify-center gap-4",
            ),
            cls="text-center",
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4",
    )


# --- Edit Course Route ---
@rt("/instructor/courses/{course_id}/edit")
@instructor_required
def get(session, course_id: int):
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A(
                "Back to Courses",
                href="/instructor/courses",
                cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
            ),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center",
        )

    # Create the form content
    form_content = Div(
        H2(
            f"Edit Course: {course.title}",
            cls="text-2xl font-bold text-indigo-900 mb-6",
        ),
        Div(
            P("Update your course details below.", cls="mb-6 text-gray-600"),
            Form(
                Div(
                    Label(
                        "Course Title",
                        for_="title",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="title",
                        name="title",
                        type="text",
                        placeholder="e.g. Introduction to Computer Science",
                        value=course.title,
                        required=True,
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                Div(
                    Label(
                        "Course Code",
                        for_="code",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Input(
                        id="code",
                        name="code",
                        type="text",
                        placeholder="e.g. CS101",
                        value=course.code,
                        required=True,
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                # Term and department fields
                Div(
                    Div(
                        Label(
                            "Term",
                            for_="term",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Input(
                            id="term",
                            name="term",
                            type="text",
                            placeholder="e.g. Fall 2023",
                            value=getattr(course, "term", ""),
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="w-1/2 pr-2",
                    ),
                    Div(
                        Label(
                            "Department",
                            for_="department",
                            cls="block text-indigo-900 font-medium mb-1",
                        ),
                        Input(
                            id="department",
                            name="department",
                            type="text",
                            placeholder="e.g. Computer Science",
                            value=getattr(course, "department", ""),
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                        ),
                        cls="w-1/2 pl-2",
                    ),
                    cls="flex mb-4",
                ),
                # Status field
                Div(
                    Label(
                        "Status",
                        for_="status",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Select(
                        Option(
                            "Active",
                            value="active",
                            selected=getattr(course, "status", "active") == "active",
                        ),
                        Option(
                            "Closed",
                            value="closed",
                            selected=getattr(course, "status", "active") == "closed",
                        ),
                        Option(
                            "Archived",
                            value="archived",
                            selected=getattr(course, "status", "active") == "archived",
                        ),
                        id="status",
                        name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                Div(
                    Label(
                        "Description",
                        for_="description",
                        cls="block text-indigo-900 font-medium mb-1",
                    ),
                    Textarea(
                        id="description",
                        name="description",
                        placeholder="Provide a brief description of the course",
                        value=getattr(course, "description", ""),
                        rows="4",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-6",
                ),
                Div(
                    Button(
                        "Update Course",
                        type="submit",
                        cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                    ),
                    cls="mb-4",
                ),
                Div(id="result", cls=""),
                hx_post=f"/instructor/courses/{course_id}/edit",
                hx_target="#result",
                cls="w-full",
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100",
        ),
        cls="",
    )

    # Sidebar content with course actions
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Courses",
                    color="gray",
                    href="/instructor/courses",
                    icon="←",
                ),
                action_button(
                    "View Students",
                    color="indigo",
                    href=f"/instructor/courses/{course_id}/students",
                    icon="👨‍👩‍👧‍👦",
                ),
                action_button(
                    "Assignments",
                    color="teal",
                    href=f"/instructor/courses/{course_id}/assignments",
                    icon="📝",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Course Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(
                f"Current Status: {getattr(course, 'status', 'active').capitalize()}",
                cls="font-medium "
                + (
                    "text-green-600"
                    if getattr(course, "status", "active") == "active"
                    else "text-amber-600"
                    if getattr(course, "status", "active") == "closed"
                    else "text-gray-600"
                ),
            ),
            P(
                "Active: Students can be invited and can access course materials",
                cls="text-gray-600 text-sm mt-4 mb-1",
            ),
            P(
                "Closed: No new enrollments, but existing students can access",
                cls="text-gray-600 text-sm mb-1",
            ),
            P(
                "Archived: Hidden from all users but preserves data",
                cls="text-gray-600 text-sm mb-1",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Edit Course: {course.title} | FeedForward",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/courses/{course_id}/edit")
@instructor_required
def post(
    session,
    course_id: int,
    title: str,
    code: str,
    term: str = "",
    department: str = "",
    status: str = "active",
    description: str = "",
):
    # Get current user
    user = users[session["auth"]]

    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)

    if error:
        return f"Error: {error}"

    # Validate input
    if not title or not code:
        return "Course title and code are required."

    # Check for duplicate course code (but don't count the current course)
    for c in courses():
        if c.code == code and c.instructor_email == user.email and c.id != course_id:
            # Only check for duplicates from the same instructor
            if not hasattr(c, "status") or c.status != "deleted":
                return "You already have another course with this code. Please use a different code."

    # Validate status
    if status not in ["active", "closed", "archived"]:
        status = "active"  # Default to active if invalid

    # Create timestamp
    now = datetime.now().isoformat()

    # Update course fields
    course.title = title
    course.code = code
    course.term = term
    course.department = department
    course.status = status
    course.description = description if hasattr(course, "description") else None
    course.updated_at = now

    # Update the course in the database
    courses.update(course)

    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3(
                        "Course Updated Successfully!",
                        cls="text-xl font-bold text-green-700 mb-1",
                    ),
                    P(f'Your course "{title}" has been updated.', cls="text-gray-600"),
                    cls="",
                ),
                cls="flex items-center mb-6",
            ),
            Div(
                A(
                    "Back to Courses",
                    href="/instructor/courses",
                    cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200",
                ),
                A(
                    "Manage Students",
                    href=f"/instructor/courses/{course_id}/students",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                ),
                cls="flex justify-center gap-4",
            ),
            cls="text-center",
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4",
    )


@rt("/instructor/manage-students")
@instructor_required
def get(session, request):
    # Get components directly from top-level imports

    # Get current user
    user = users[session["auth"]]

    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            instructor_courses.append(course)

    # Process each course and get student enrollments
    courses_with_students = []

    for course in instructor_courses:
        students = []
        for enrollment in enrollments():
            if enrollment.course_id == course.id:
                # Get the student details
                try:
                    student = users[enrollment.student_email]

                    # Determine enrollment status
                    status = "Invited" if not student.verified else "Enrolled"

                    students.append(
                        {
                            "email": student.email,
                            "name": student.name
                            if student.name
                            else "(Not registered)",
                            "status": status,
                            "verified": student.verified,
                        }
                    )
                except NotFoundError:
                    # Student record might be missing
                    students.append(
                        {
                            "email": enrollment.student_email,
                            "name": "(Not registered)",
                            "status": "Invited",
                            "verified": False,
                        }
                    )

        if students:
            courses_with_students.append({"course": course, "students": students})

    # Create the main content
    if courses_with_students:
        # Create tables for each course with students
        course_tables = []

        for course_data in courses_with_students:
            course = course_data["course"]
            students = course_data["students"]

            # Sort students: enrolled first, then invited
            sorted_students = sorted(
                students, key=lambda s: (0 if s["verified"] else 1, s["email"])
            )

            # Create student rows
            student_rows = []
            for idx, student in enumerate(sorted_students):
                status_color = "green" if student["verified"] else "yellow"
                status_text = "Enrolled" if student["verified"] else "Invited"

                # Create row with actions
                row = Tr(
                    Td(f"{idx + 1}", cls="py-4 px-6"),
                    Td(student["email"], cls="py-4 px-6"),
                    Td(student["name"], cls="py-4 px-6"),
                    Td(status_badge(status_text, status_color), cls="py-4 px-6"),
                    Td(
                        Div(
                            Button(
                                "Resend",
                                hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                                hx_target=f"#status-{course.id}-{idx}",
                                cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                            )
                            if not student["verified"]
                            else "",
                            Button(
                                "Remove",
                                hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                                hx_target="#message-area",
                                hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                                cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                            ),
                            cls="flex",
                            id=f"status-{course.id}-{idx}",
                        ),
                        cls="py-4 px-6",
                    ),
                    id=f"row-{course.id}-{idx}",
                    cls="border-b border-gray-100 hover:bg-gray-50 transition-colors",
                )
                student_rows.append(row)

            # Create the course card with student table
            course_tables.append(
                Div(
                    H3(
                        f"{course.title} ({course.code})",
                        cls="text-xl font-bold text-indigo-900 mb-4",
                    ),
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    *[
                                        Th(
                                            h,
                                            cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                        )
                                        for h in [
                                            "#",
                                            "Email",
                                            "Name",
                                            "Status",
                                            "Actions",
                                        ]
                                    ],
                                    cls="bg-indigo-50",
                                )
                            ),
                            Tbody(*student_rows),
                            cls="w-full",
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
                    ),
                    Div(
                        action_button(
                            "Invite More Students",
                            color="indigo",
                            href=f"/instructor/invite-students?course_id={course.id}",
                            icon="+",
                        ),
                        cls="mt-4",
                    ),
                    cls="mb-8",
                )
            )

        # Main content with all course tables
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            *course_tables,
            cls="",
        )
    else:
        # Show a message if no students enrolled in any courses
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P(
                        "You don't have any students enrolled in your courses yet.",
                        cls="text-center text-gray-600 mb-6",
                    ),
                    Div(
                        A(
                            "Invite Students",
                            href="/instructor/invite-students",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="text-center",
                    ),
                    cls="py-8",
                )
            ),
            cls="",
        )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Student Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Invite Students",
                    color="indigo",
                    href="/instructor/invite-students",
                    icon="+",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Resend invitations if students haven't registered",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Remove students who are no longer in your course",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• Students must verify their email to access the course",
                cls="text-gray-600 text-sm",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Students | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path,
    )


@rt("/instructor/courses/{course_id}/students")
@instructor_required
def get(session, course_id: int):
    # Get components directly from top-level imports

    # Get current user
    user = users[session["auth"]]

    # Get the course
    target_course = None
    for course in courses():
        if course.id == course_id and course.instructor_email == user.email:
            target_course = course
            break

    if not target_course:
        return "Course not found or you don't have permission to access it."

    # Get students for this course
    course_students = []
    for enrollment in enrollments():
        if enrollment.course_id == course_id:
            # Get the student details
            try:
                student = users[enrollment.student_email]

                # Determine enrollment status
                status = "Invited" if not student.verified else "Enrolled"

                course_students.append(
                    {
                        "email": student.email,
                        "name": student.name if student.name else "(Not registered)",
                        "status": status,
                        "verified": student.verified,
                    }
                )
            except:
                # Student record might be missing
                course_students.append(
                    {
                        "email": enrollment.student_email,
                        "name": "(Not registered)",
                        "status": "Invited",
                        "verified": False,
                    }
                )

    # Sort students: enrolled first, then invited
    sorted_students = sorted(
        course_students, key=lambda s: (0 if s["verified"] else 1, s["email"])
    )

    # Create the main content
    if sorted_students:
        # Create student rows
        student_rows = []
        for idx, student in enumerate(sorted_students):
            status_color = "green" if student["verified"] else "yellow"
            status_text = "Enrolled" if student["verified"] else "Invited"

            # Create row with actions
            row = Tr(
                Td(f"{idx + 1}", cls="py-4 px-6"),
                Td(student["email"], cls="py-4 px-6"),
                Td(student["name"], cls="py-4 px-6"),
                Td(status_badge(status_text, status_color), cls="py-4 px-6"),
                Td(
                    Div(
                        Button(
                            "Resend",
                            hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                            hx_target=f"#status-{idx}",
                            cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2",
                        )
                        if not student["verified"]
                        else "",
                        Button(
                            "Remove",
                            hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                            hx_target="#message-area",
                            hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                            cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                        ),
                        cls="flex",
                        id=f"status-{idx}",
                    ),
                    cls="py-4 px-6",
                ),
                id=f"row-{idx}",
                cls="border-b border-gray-100 hover:bg-gray-50 transition-colors",
            )
            student_rows.append(row)

        # Create the student table
        main_content = Div(
            H2(
                f"Students in {target_course.title} ({target_course.code})",
                cls="text-2xl font-bold text-indigo-900 mb-6",
            ),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            Div(
                Table(
                    Thead(
                        Tr(
                            *[
                                Th(
                                    h,
                                    cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100",
                                )
                                for h in ["#", "Email", "Name", "Status", "Actions"]
                            ],
                            cls="bg-indigo-50",
                        )
                    ),
                    Tbody(*student_rows),
                    cls="w-full",
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100",
            ),
            Div(
                action_button(
                    "Invite More Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="+",
                ),
                cls="mt-6",
            ),
            cls="",
        )
    else:
        # Show a message if no students enrolled in this course
        main_content = Div(
            H2(
                f"Students in {target_course.title} ({target_course.code})",
                cls="text-2xl font-bold text-indigo-900 mb-6",
            ),
            card(
                Div(
                    P(
                        "You don't have any students enrolled in this course yet.",
                        cls="text-center text-gray-600 mb-6",
                    ),
                    Div(
                        A(
                            "Invite Students",
                            href=f"/instructor/invite-students?course_id={course_id}",
                            cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                        ),
                        cls="text-center",
                    ),
                    cls="py-8",
                )
            ),
            cls="",
        )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Invite Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="✉️",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Course Details", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Title: {target_course.title}", cls="text-gray-600 mb-2"),
            P(f"Code: {target_course.code}", cls="text-gray-600 mb-2"),
            P(f"Students: {len(sorted_students)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Students in {target_course.code} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
    )


@rt("/instructor/resend-invitation")
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session["auth"]]

    # URL-decode the email to handle special characters like +
    email = urllib.parse.unquote(email)

    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return "Course not found or you don't have permission to manage it."

    # Check if the student is enrolled in this course
    is_enrolled = False
    for enrollment in enrollments():
        if enrollment.course_id == course_id and enrollment.student_email == email:
            is_enrolled = True
            break

    if not is_enrolled:
        return "Student is not enrolled in this course."

    # Generate a token
    token = generate_verification_token(email)

    # Update the student's verification token
    try:
        student = users[email]
        student.verification_token = token
        users.update(student)
    except:
        # Student doesn't exist in the users table yet
        new_student = User(
            email=email,
            name="",
            password="",
            role=Role.STUDENT,
            verified=False,
            verification_token=token,
            approved=True,
            department="",
            reset_token="",
            reset_token_expiry="",
        )
        users.insert(new_student)

    # Send invitation email
    success, message = send_student_invitation_email(
        email, user.name, course.title, token
    )

    if success:
        return Div(
            P("Invitation sent successfully", cls="text-green-600"),
            Div(cls="mt-1 text-xs text-gray-500"),
        )
    else:
        return Div(
            P("Failed to send invitation", cls="text-red-600"),
            Div(message, cls="mt-1 text-xs text-gray-500"),
        )


@rt("/instructor/remove-student")
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session["auth"]]

    # URL-decode the email to handle special characters like +
    email = urllib.parse.unquote(email)

    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return Div(
            P(
                "Course not found or you don't have permission to manage it.",
                cls="text-red-600 font-medium",
            ),
            cls="p-4 bg-red-50 rounded-lg",
        )

    try:
        # Import datetime for timestamp updates
        from datetime import datetime

        # Simpler direct deletion approach
        deleted_count = 0

        # Convert to ensure we're comparing the right types
        course_id_int = int(course_id)

        # Find and delete matching enrollments directly
        for e in list(enrollments()):
            e_course_id = int(e.course_id)
            if e_course_id == course_id_int and e.student_email == email:
                print(
                    f"Deleting enrollment: {e.id}, Course: {e.course_id}, Student: {e.student_email}"
                )
                enrollments.delete(e.id)
                deleted_count += 1

        # Check if we deleted anything
        if deleted_count == 0:
            return Div(
                P(f"Student {email} not found in this course.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg",
            )

        # Update the student account status only if this was their only enrollment
        student_has_other_enrollments = False
        for e in enrollments():
            if e.student_email == email:
                student_has_other_enrollments = True
                break

        # If student has no other enrollments, mark their account as inactive
        if not student_has_other_enrollments:
            try:
                student = users[email]
                if student.role == Role.STUDENT and hasattr(student, "status"):
                    student.status = "inactive"
                    student.last_active = datetime.now().isoformat()
                    users.update(student)
            except:
                # If we can't find the student, that's okay - they might not have registered yet
                pass

        # Return success with auto-refresh
        return Div(
            P(
                f"Student {email} has been removed from the course.",
                cls="text-green-600",
            ),
            Script("""
                console.log('Student removal successful');
                setTimeout(function() { 
                    console.log('Reloading page...');
                    window.location.href = window.location.href; 
                }, 1500);
            """),
            cls="bg-green-50 p-4 rounded-lg",
        )
    except Exception as e:
        return Div(
            P(f"Error removing student: {e!s}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg",
        )


@rt("/instructor/invite-students")
@instructor_required
def get(session, request, course_id: int = None):
    """Shows the form to invite students to a course"""
    # Get current user
    user = users[session["auth"]]

    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            instructor_courses.append(course)

    # Create invitation form
    form_content = Div(
        H2("Invite Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P(
                "Invite students to join your course. Students will receive an email with instructions to create their account.",
                cls="mb-6 text-gray-600",
            ),
            # Main content with courses check
            (
                Div(
                    Form(
                        # Course selection
                        Div(
                            Label(
                                "Course",
                                for_="course_id",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            Select(
                                Option(
                                    "Select a course",
                                    value="",
                                    selected=True if not course_id else False,
                                    disabled=True,
                                ),
                                *[
                                    Option(
                                        f"{c.title} ({c.code})",
                                        value=str(c.id),
                                        selected=(
                                            c.id == course_id if course_id else False
                                        ),
                                    )
                                    for c in instructor_courses
                                ],
                                id="course_id",
                                name="course_id",
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        # Student emails textarea
                        Div(
                            Label(
                                "Student Emails",
                                for_="student_emails",
                                cls="block text-indigo-900 font-medium mb-1",
                            ),
                            P(
                                "Enter one email address per line",
                                cls="text-sm text-gray-500 mb-1",
                            ),
                            Textarea(
                                id="student_emails",
                                name="student_emails",
                                rows="6",
                                placeholder="student1@example.com\nstudent2@example.com\nstudent3@example.com",
                                cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                            ),
                            cls="mb-4",
                        ),
                        # Submit button
                        Div(
                            Button(
                                "Send Invitations",
                                type="submit",
                                cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                            ),
                            cls="mb-5",
                        ),
                        # Simple file upload section
                        Div(
                            Hr(cls="my-4 border-gray-300"),
                            P(
                                "Or upload a file with email addresses:",
                                cls="block text-indigo-900 font-medium mb-2",
                            ),
                            P(
                                "File should have one email per line or be a CSV with an email column",
                                cls="text-sm text-gray-500 mb-3",
                            ),
                            # File input
                            Div(
                                Label(
                                    "Select File",
                                    for_="email_file",
                                    cls="block text-indigo-900 font-medium mb-1",
                                ),
                                Input(
                                    id="email_file",
                                    type="file",
                                    accept=".csv,.tsv,.txt",
                                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500",
                                ),
                                cls="mb-3",
                            ),
                            # Button to load file
                            Button(
                                "Load Emails from File",
                                id="load-emails",
                                type="button",
                                cls="bg-teal-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm",
                            ),
                            # Simple JavaScript to read file and add to textarea
                            Script("""
                            document.addEventListener('DOMContentLoaded', function() {
                                const fileInput = document.getElementById('email_file');
                                const loadButton = document.getElementById('load-emails');
                                const textarea = document.getElementById('student_emails');
                                
                                loadButton.addEventListener('click', function() {
                                    if (!fileInput.files || fileInput.files.length === 0) {
                                        alert('Please select a file first');
                                        return;
                                    }
                                    
                                    const file = fileInput.files[0];
                                    const reader = new FileReader();
                                    
                                    reader.onload = function(e) {
                                        const content = e.target.result;
                                        const lines = content.split(/\\r?\\n/);
                                        const emails = [];
                                        
                                        // Very simple email extraction
                                        const emailPattern = /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}/g;
                                        
                                        // Look for emails in each line
                                        lines.forEach(line => {
                                            const matches = line.match(emailPattern);
                                            if (matches) {
                                                emails.push(...matches);
                                            }
                                        });
                                        
                                        if (emails.length === 0) {
                                            alert('No email addresses found in the file');
                                            return;
                                        }
                                        
                                        // Add to textarea
                                        const uniqueEmails = [...new Set(emails)];
                                        if (textarea.value.trim()) {
                                            textarea.value += '\\n' + uniqueEmails.join('\\n');
                                        } else {
                                            textarea.value = uniqueEmails.join('\\n');
                                        }
                                        
                                        alert(`Added ${uniqueEmails.length} email addresses from the file`);
                                    };
                                    
                                    reader.onerror = function() {
                                        alert('Error reading file');
                                    };
                                    
                                    reader.readAsText(file);
                                });
                            });
                        """),
                            cls="mb-6",
                        ),
                        # Result placeholder
                        Div(id="invite-result", cls="mt-4"),
                        # Form submission details
                        id="invite-form",
                        method="post",
                        action="/instructor/invite-students",
                        cls="bg-white p-6 rounded-lg border border-gray-200",
                    )
                )
            )
            if instructor_courses
            # No courses message
            else Div(
                P("You don't have any courses yet.", cls="text-red-500 mb-4"),
                P(
                    "Please create a course first before inviting students.",
                    cls="text-gray-600 mb-4",
                ),
                A(
                    "Create a New Course",
                    href="/instructor/courses/new",
                    cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm",
                ),
                cls="text-center py-8 bg-white rounded-lg border border-gray-200",
            ),
            cls="w-full",
        ),
        cls="",
    )

    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href="/instructor/manage-students",
                    icon="👨‍👩‍👧‍👦",
                ),
                action_button(
                    "Create Course",
                    color="indigo",
                    href="/instructor/courses/new",
                    icon="+",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P(
                "• Students will receive an email with instructions to join",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• They can set up their account after clicking the email link",
                cls="text-gray-600 mb-2 text-sm",
            ),
            P(
                "• You can upload emails in different formats:",
                cls="text-gray-600 mb-1 text-sm",
            ),
            P(
                "  - Simple text file with one email per line",
                cls="text-gray-600 mb-1 text-sm ml-2",
            ),
            P(
                "  - CSV/TSV with headers (we'll find the email column)",
                cls="text-gray-600 mb-1 text-sm ml-2",
            ),
            P(
                "  - Any format where we can detect email addresses",
                cls="text-gray-600 text-sm ml-2",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Use the dashboard layout with our components
    return dashboard_layout(
        "Invite Students",
        sidebar_content,
        form_content,
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path,
    )


@rt("/instructor/invite-students")
@instructor_required
def post(session, course_id: str = None, student_emails: str = None):
    """Handle the student invitation form submission"""
    # Debug info
    print("Invite students - POST received")
    print(f"Invite students - course_id: {course_id}, student_emails: {student_emails}")

    # Convert course_id to integer if provided
    if course_id:
        try:
            course_id = int(course_id)
        except (ValueError, TypeError):
            return Div(
                P(
                    "Invalid course ID. Please select a valid course.",
                    cls="text-red-600 font-medium",
                ),
                cls="p-4 bg-red-50 rounded-lg",
            )

    # Get current user
    user = users[session["auth"]]

    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break

    if not course:
        return Div(
            P(
                "Course not found or you don't have permission to invite students to this course.",
                cls="text-red-600 font-medium",
            ),
            cls="p-4 bg-red-50 rounded-lg",
        )

    # Process student emails
    emails = [email.strip() for email in student_emails.split("\n") if email.strip()]

    if not emails:
        return Div(
            P(
                "Please enter at least one student email.",
                cls="text-amber-600 font-medium",
            ),
            cls="p-4 bg-amber-50 rounded-lg",
        )

    # Simple tracking lists
    sent_emails = []
    already_enrolled_emails = []
    error_emails = []

    # Get next enrollment ID
    next_id = 1
    try:
        enrollment_ids = [e.id for e in enrollments()]
        if enrollment_ids:
            next_id = max(enrollment_ids) + 1
    except Exception as e:
        print(f"Error getting next enrollment ID: {e}")

    # Process each email
    for email in emails:
        # Check if already enrolled
        is_enrolled = False
        for enrollment in enrollments():
            if (
                hasattr(enrollment, "student_email")
                and enrollment.student_email == email
                and enrollment.course_id == course_id
            ):
                is_enrolled = True
                break

        if is_enrolled:
            already_enrolled_emails.append(email)
            continue

        # Generate token for the invitation
        token = generate_verification_token(email)

        # Check if user exists
        try:
            users[email]  # Just check if exists
        except:
            # Create new student account if doesn't exist
            new_student = User(
                email=email,
                name="",  # Will be set during registration
                password="",  # Will be set during registration
                role=Role.STUDENT,
                verified=False,
                verification_token=token,
                approved=True,  # Students are auto-approved
                department="",
                reset_token="",
                reset_token_expiry="",
            )
            users.insert(new_student)

        # Create enrollment record
        new_enrollment = Enrollment(
            id=next_id, course_id=course_id, student_email=email
        )
        enrollments.insert(new_enrollment)
        next_id += 1

        # Send invitation email
        success, message = send_student_invitation_email(
            email, user.name, course.title, token
        )

        if success:
            sent_emails.append(email)
        else:
            error_emails.append(f"{email} (Email error: {message})")

    # Get components directly from top-level imports

    # Generate summary message
    message_parts = []
    if sent_emails:
        message_parts.append(
            f"{len(sent_emails)} student{'' if len(sent_emails) == 1 else 's'} invited successfully"
        )
    if already_enrolled_emails:
        message_parts.append(f"{len(already_enrolled_emails)} already enrolled")
    if error_emails:
        message_parts.append(
            f"{len(error_emails)} invitation{'' if len(error_emails) == 1 else 's'} failed"
        )

    summary = ", ".join(message_parts)

    # Build complete page with confirmation message
    confirmation_content = Div(
        # Success Banner
        Div(
            Div(
                Span("✅", cls="text-5xl mr-5"),
                Div(
                    H2(
                        "Student Invitations Sent!",
                        cls="text-2xl font-bold text-green-700 mb-2",
                    ),
                    P(summary, cls="text-xl text-gray-700"),
                    cls="",
                ),
                cls="flex items-center",
            ),
            cls="bg-green-50 p-8 rounded-xl shadow-md border-2 border-green-500 mb-6 text-center",
        ),
        # Detailed Results
        Div(
            H3("Invitation Results", cls="text-xl font-bold text-indigo-900 mb-4"),
            # Successfully sent
            (
                Div(
                    Div(
                        Span("✅", cls="text-2xl mr-3"),
                        Div(
                            H4(
                                "Invitations Sent",
                                cls="text-lg font-bold text-green-700",
                            ),
                            P(
                                f"{len(sent_emails)} student{'' if len(sent_emails) == 1 else 's'} invited successfully",
                                cls="text-gray-700",
                            ),
                            cls="",
                        ),
                        cls="flex items-start mb-3",
                    ),
                    Div(
                        *[P(email, cls="mb-1") for email in sent_emails[:8]],
                        P(
                            f"... and {len(sent_emails) - 8} more"
                            if len(sent_emails) > 8
                            else "",
                            cls="text-gray-500 italic mt-1",
                        ),
                        cls="ml-10 text-sm",
                    )
                    if sent_emails
                    else "",
                    cls="mb-5",
                )
                if sent_emails
                else ""
            ),
            # Already enrolled
            (
                Div(
                    Div(
                        Span("ℹ️", cls="text-2xl mr-3"),
                        Div(
                            H4(
                                "Already Enrolled",
                                cls="text-lg font-bold text-amber-700",
                            ),
                            P(
                                f"{len(already_enrolled_emails)} student{'' if len(already_enrolled_emails) == 1 else 's'} already in this course",
                                cls="text-gray-700",
                            ),
                            cls="",
                        ),
                        cls="flex items-start mb-3",
                    ),
                    Div(
                        *[
                            P(email, cls="mb-1")
                            for email in already_enrolled_emails[:8]
                        ],
                        P(
                            f"... and {len(already_enrolled_emails) - 8} more"
                            if len(already_enrolled_emails) > 8
                            else "",
                            cls="text-gray-500 italic mt-1",
                        ),
                        cls="ml-10 text-sm",
                    )
                    if already_enrolled_emails and len(already_enrolled_emails) <= 15
                    else "",
                    cls="mb-5",
                )
                if already_enrolled_emails
                else ""
            ),
            # Errors
            (
                Div(
                    Div(
                        Span("❌", cls="text-2xl mr-3"),
                        Div(
                            H4(
                                "Failed Invitations",
                                cls="text-lg font-bold text-red-700",
                            ),
                            P(
                                f"{len(error_emails)} invitation{'' if len(error_emails) == 1 else 's'} failed to send",
                                cls="text-gray-700",
                            ),
                            cls="",
                        ),
                        cls="flex items-start mb-3",
                    ),
                    Div(
                        *[P(error, cls="mb-1") for error in error_emails],
                        cls="ml-10 text-sm",
                    )
                    if error_emails
                    else "",
                    (
                        P(
                            "Note: Check your SMTP settings in the .env file.",
                            cls="text-xs text-gray-500 mt-2 ml-12",
                        )
                    )
                    if error_emails
                    else "",
                    cls="mb-5",
                )
                if error_emails
                else ""
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 mb-6",
        ),
        # Action buttons
        Div(
            Div(
                A(
                    "Return to Dashboard",
                    href="/instructor/dashboard",
                    cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-200 mr-4 font-medium",
                ),
                A(
                    "Invite More Students",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 mr-4 font-medium",
                ),
                A(
                    "View All Students",
                    href="/instructor/manage-students",
                    cls="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 font-medium",
                ),
                cls="flex justify-center flex-wrap gap-4",
            ),
            cls="text-center",
        ),
        cls="max-w-4xl mx-auto px-4",
    )

    # Return as full page rather than just updating a div
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Invite More Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="+",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href="/instructor/manage-students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    # Create a full confirmation page
    confirmation_content = Div(
        H2("Invitation Results", cls="text-2xl font-bold text-green-700 mb-4"),
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3(
                        "Invitations Sent Successfully!",
                        cls="text-xl font-bold text-green-700 mb-2",
                    ),
                    P(
                        f"Invited {len(sent_emails)} students to {course.title}",
                        cls="text-gray-700",
                    ),
                    cls="",
                ),
                cls="flex items-center mb-6",
            ),
            # Successfully sent
            (
                Div(
                    H4("Invitations Sent", cls="text-lg font-bold text-green-700 mb-2"),
                    Div(
                        *[P(email, cls="mb-1") for email in sent_emails[:10]],
                        P(
                            f"...and {len(sent_emails) - 10} more"
                            if len(sent_emails) > 10
                            else "",
                            cls="text-gray-500 italic mt-1",
                        ),
                        cls="ml-4 mb-4",
                    ),
                )
                if sent_emails
                else ""
            ),
            # Already enrolled
            (
                Div(
                    H4("Already Enrolled", cls="text-lg font-bold text-amber-700 mb-2"),
                    P(
                        f"{len(already_enrolled_emails)} student(s) were already enrolled in this course",
                        cls="mb-2",
                    ),
                    Div(
                        *[
                            P(email, cls="mb-1")
                            for email in already_enrolled_emails[:5]
                        ],
                        P(
                            f"...and {len(already_enrolled_emails) - 5} more"
                            if len(already_enrolled_emails) > 5
                            else "",
                            cls="text-gray-500 italic mt-1",
                        ),
                        cls="ml-4 mb-4",
                    )
                    if already_enrolled_emails and len(already_enrolled_emails) <= 15
                    else "",
                    cls="mb-4",
                )
                if already_enrolled_emails
                else ""
            ),
            # Errors
            (
                Div(
                    H4("Failed Invitations", cls="text-lg font-bold text-red-700 mb-2"),
                    P(f"{len(error_emails)} invitation(s) failed to send", cls="mb-2"),
                    Div(
                        *[P(error, cls="mb-1") for error in error_emails],
                        cls="ml-4 mb-4",
                    )
                    if error_emails
                    else "",
                    cls="mb-4",
                )
                if error_emails
                else ""
            ),
            # Action buttons
            Div(
                A(
                    "Back to Dashboard",
                    href="/instructor/dashboard",
                    cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-3",
                ),
                A(
                    "Invite More Students",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700",
                ),
                cls="mt-4",
            ),
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100",
        ),
        cls="mt-4",
    )

    # Sidebar content for the confirmation page
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button(
                    "Back to Dashboard",
                    color="gray",
                    href="/instructor/dashboard",
                    icon="←",
                ),
                action_button(
                    "Invite More Students",
                    color="indigo",
                    href=f"/instructor/invite-students?course_id={course_id}",
                    icon="✉️",
                ),
                action_button(
                    "Manage Students",
                    color="teal",
                    href="/instructor/manage-students",
                    icon="👨‍👩‍👧‍👦",
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    # Return a complete dashboard layout for the confirmation
    return dashboard_layout(
        "Invitation Results | FeedForward",
        sidebar_content,
        confirmation_content,
        user_role=Role.INSTRUCTOR,
    )


# --- CSV Import Routes ---
# This route has been removed since we're now using a simpler approach without special templates

# This route has been replaced by client-side JavaScript processing

# Confirmation is now directly handled in the POST route

# =============================================
# INSTRUCTOR FEEDBACK VIEWING INTERFACES
# =============================================


# --- Assignment Submissions Listing ---
@rt("/instructor/assignments/{assignment_id}/submissions")
@instructor_required
def get(session, assignment_id: int):
    """List all submissions for an assignment with feedback status"""
    from app.models.assignment import assignments
    from app.models.feedback import aggregated_feedback, drafts, model_runs

    # Get current user
    user = users[session["auth"]]

    # Get assignment and verify ownership
    try:
        assignment = assignments[assignment_id]
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get course and verify instructor owns it
    try:
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all drafts for this assignment
    all_drafts = drafts()
    assignment_drafts = [d for d in all_drafts if d.assignment_id == assignment_id]

    # Get aggregated feedback for status
    all_agg_feedback = aggregated_feedback()
    agg_feedback_map = {}
    for af in all_agg_feedback:
        if af.draft_id not in agg_feedback_map:
            agg_feedback_map[af.draft_id] = []
        agg_feedback_map[af.draft_id].append(af)

    # Get model runs for additional stats
    all_runs = model_runs()
    runs_map = {}
    for run in all_runs:
        if run.draft_id not in runs_map:
            runs_map[run.draft_id] = []
        runs_map[run.draft_id].append(run)

    # Build submissions data
    submissions_data = []
    for draft in assignment_drafts:
        # Get feedback status
        feedback_list = agg_feedback_map.get(draft.id, [])
        runs_list = runs_map.get(draft.id, [])

        # Calculate status
        if draft.status == "submitted":
            status = "pending"
            status_color = "yellow"
        elif draft.status == "processing":
            status = "processing"
            status_color = "blue"
        elif draft.status == "feedback_ready":
            if feedback_list and any(
                af.status == "pending_review" for af in feedback_list
            ):
                status = "needs_review"
                status_color = "orange"
            elif feedback_list and any(af.status == "approved" for af in feedback_list):
                status = "approved"
                status_color = "green"
            else:
                status = "ready"
                status_color = "green"
        elif draft.status == "error":
            status = "error"
            status_color = "red"
        else:
            status = draft.status
            status_color = "gray"

        # Calculate AI model stats
        total_runs = len(runs_list)
        successful_runs = len([r for r in runs_list if r.status == "complete"])
        failed_runs = len([r for r in runs_list if r.status == "error"])

        submissions_data.append(
            {
                "draft": draft,
                "status": status,
                "status_color": status_color,
                "total_runs": total_runs,
                "successful_runs": successful_runs,
                "failed_runs": failed_runs,
                "has_feedback": len(feedback_list) > 0,
                "feedback_status": feedback_list[0].status if feedback_list else "none",
            }
        )

    # Sort by submission date (newest first)
    submissions_data.sort(key=lambda x: x["draft"].submission_date, reverse=True)

    # Build submissions table
    if submissions_data:
        table_rows = []
        for sub in submissions_data:
            draft = sub["draft"]

            # Status badge
            status_badge_elem = Span(
                sub["status"].replace("_", " ").title(),
                cls=f"px-2 py-1 text-xs font-medium rounded-full bg-{sub['status_color']}-100 text-{sub['status_color']}-800",
            )

            # AI Models info
            if sub["total_runs"] > 0:
                models_info = f"{sub['successful_runs']}/{sub['total_runs']} models"
                if sub["failed_runs"] > 0:
                    models_info += f" ({sub['failed_runs']} failed)"
            else:
                models_info = "No runs"

            # Action buttons
            actions = Div(
                A(
                    "View Details",
                    href=f"/instructor/submissions/{draft.id}",
                    cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium mr-3",
                ),
                cls="flex items-center",
            )

            # Add review/approve actions if needed
            if sub["status"] == "needs_review":
                actions.children.insert(
                    0,
                    A(
                        "Review Feedback",
                        href=f"/instructor/submissions/{draft.id}/review",
                        cls="text-orange-600 hover:text-orange-800 text-sm font-medium mr-3",
                    ),
                )

            table_rows.append(
                Tr(
                    Td(draft.student_email, cls="px-4 py-3 text-sm"),
                    Td(f"Version {draft.version}", cls="px-4 py-3 text-sm"),
                    Td(f"{draft.word_count} words", cls="px-4 py-3 text-sm"),
                    Td(
                        datetime.fromisoformat(draft.submission_date).strftime(
                            "%b %d, %Y %I:%M %p"
                        ),
                        cls="px-4 py-3 text-sm",
                    ),
                    Td(status_badge_elem, cls="px-4 py-3"),
                    Td(models_info, cls="px-4 py-3 text-sm text-gray-600"),
                    Td(actions, cls="px-4 py-3"),
                )
            )

        submissions_table = Div(
            Table(
                Thead(
                    Tr(
                        Th(
                            "Student",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Version",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Length",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Submitted",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Status",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "AI Models",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                        Th(
                            "Actions",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                        ),
                    )
                ),
                Tbody(*table_rows, cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg",
        )
    else:
        submissions_table = Div(
            P("No submissions yet.", cls="text-gray-500 text-center py-8"),
            cls="bg-white rounded-lg shadow",
        )

    # Stats summary
    total_submissions = len(submissions_data)
    pending_review = len([s for s in submissions_data if s["status"] == "needs_review"])
    completed = len(
        [s for s in submissions_data if s["status"] in ["approved", "ready"]]
    )

    stats_cards = Div(
        Div(
            Div(
                P("Total Submissions", cls="text-sm font-medium text-gray-500"),
                P(str(total_submissions), cls="text-2xl font-bold text-gray-900"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Pending Review", cls="text-sm font-medium text-gray-500"),
                P(str(pending_review), cls="text-2xl font-bold text-orange-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Completed", cls="text-sm font-medium text-gray-500"),
                P(str(completed), cls="text-2xl font-bold text-green-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
    )

    # Build page content
    main_content = Div(
        # Header
        Div(
            Div(
                H1(
                    f"Submissions: {assignment.title}",
                    cls="text-2xl font-bold text-gray-900",
                ),
                P(f"Course: {course.name}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                A(
                    "Analytics",
                    href=f"/instructor/assignments/{assignment_id}/analytics",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Stats
        stats_cards,
        # Submissions table
        submissions_table,
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Quick Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            A(
                "Export Data",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Bulk Review",
                href="#",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Assignment Settings",
                href=f"/instructor/assignments/{assignment_id}/edit",
                cls="block text-indigo-600 hover:text-indigo-800",
            ),
        ),
    )

    return dashboard_layout(
        f"Submissions: {assignment.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/submissions",
    )


# --- Individual Submission Detail View ---
@rt("/instructor/submissions/{draft_id}")
@instructor_required
def get(session, draft_id: int):
    """Detailed view of individual submission with LLM breakdown"""
    from app.models.assignment import assignments, rubric_categories
    from app.models.feedback import (
        aggregated_feedback,
        ai_models,
        category_scores,
        drafts,
        feedback_items,
        model_runs,
    )

    # Get current user
    user = users[session["auth"]]

    # Get draft and verify access
    try:
        draft = drafts[draft_id]
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get assignment and verify instructor owns it
    try:
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all related data
    rubric_cats = rubric_categories()
    assignment_rubric = [
        cat for cat in rubric_cats if cat.assignment_id == assignment.id
    ]

    # Get all model runs for this draft
    all_runs = model_runs()
    draft_runs = [run for run in all_runs if run.draft_id == draft_id]
    draft_runs.sort(key=lambda x: x.timestamp)

    # Get all AI models info
    all_ai_models = ai_models()
    models_map = {model.id: model for model in all_ai_models}

    # Get category scores for each run
    all_scores = category_scores()
    scores_by_run = {}
    for score in all_scores:
        if score.model_run_id not in scores_by_run:
            scores_by_run[score.model_run_id] = []
        scores_by_run[score.model_run_id].append(score)

    # Get feedback items for each run
    all_feedback = feedback_items()
    feedback_by_run = {}
    for feedback in all_feedback:
        if feedback.model_run_id not in feedback_by_run:
            feedback_by_run[feedback.model_run_id] = []
        feedback_by_run[feedback.model_run_id].append(feedback)

    # Get aggregated feedback
    all_agg = aggregated_feedback()
    agg_feedback_list = [af for af in all_agg if af.draft_id == draft_id]

    # Build individual model results
    model_results = []
    for run in draft_runs:
        if run.id not in models_map:
            continue

        model = models_map.get(run.model_id, None)
        if not model:
            continue

        run_scores = scores_by_run.get(run.id, [])
        run_feedback = feedback_by_run.get(run.id, [])

        # Organize scores by category
        scores_by_category = {}
        for score in run_scores:
            category = next(
                (cat for cat in assignment_rubric if cat.id == score.category_id), None
            )
            if category:
                scores_by_category[category.name] = {
                    "score": score.score,
                    "confidence": score.confidence,
                }

        # Organize feedback by type
        strengths = [f.content for f in run_feedback if f.type == "strength"]
        improvements = [f.content for f in run_feedback if f.type == "improvement"]
        general = [f.content for f in run_feedback if f.type == "general"]

        model_results.append(
            {
                "run": run,
                "model": model,
                "scores": scores_by_category,
                "strengths": strengths,
                "improvements": improvements,
                "general": general,
                "success": run.status == "complete",
            }
        )

    # Build LLM comparison table
    if model_results:
        # Header row with model names
        header_cells = [
            Th(
                "Category",
                cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase",
            )
        ]
        for result in model_results:
            status_indicator = "✅" if result["success"] else "❌"
            model_name = f"{result['model'].name} {status_indicator}"
            header_cells.append(
                Th(
                    model_name,
                    cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase text-center",
                )
            )

        # Add aggregated column
        header_cells.append(
            Th(
                "Aggregated",
                cls="px-4 py-3 text-left text-xs font-medium text-indigo-600 uppercase text-center font-bold",
            )
        )

        table_rows = [Tr(*header_cells)]

        # Score rows for each rubric category
        for category in assignment_rubric:
            row_cells = [Td(category.name, cls="px-4 py-3 font-medium")]

            # Individual model scores
            for result in model_results:
                if result["success"] and category.name in result["scores"]:
                    score_data = result["scores"][category.name]
                    score_cell = Div(
                        Div(f"{score_data['score']:.1f}/100", cls="font-semibold"),
                        Div(
                            f"Conf: {score_data['confidence']:.2f}",
                            cls="text-xs text-gray-500",
                        ),
                        cls="text-center",
                    )
                else:
                    score_cell = Div("—", cls="text-center text-gray-400")
                row_cells.append(Td(score_cell, cls="px-4 py-3"))

            # Aggregated score
            agg_score = next(
                (af for af in agg_feedback_list if af.category_id == category.id), None
            )
            if agg_score:
                agg_cell = Div(
                    f"{agg_score.aggregated_score:.1f}/100",
                    cls="font-bold text-gray-800 text-center",
                )
            else:
                agg_cell = Div("—", cls="text-center text-gray-400")
            row_cells.append(Td(agg_cell, cls="px-4 py-3 bg-gray-100"))

            table_rows.append(Tr(*row_cells))

        comparison_table = Div(
            H3("Score Comparison by AI Model", cls="text-lg font-semibold mb-4"),
            Table(Tbody(*table_rows), cls="min-w-full divide-y divide-gray-200"),
            cls="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 md:rounded-lg bg-white",
        )
    else:
        comparison_table = Div(
            P(
                "No model runs found for this submission.",
                cls="text-gray-500 text-center py-8",
            ),
            cls="bg-white rounded-lg shadow",
        )

    # Build individual model details
    model_details = []
    for i, result in enumerate(model_results):
        if not result["success"]:
            # Error state
            model_card = Div(
                H4(
                    f"{result['model'].name} ({result['model'].provider})",
                    cls="text-lg font-semibold mb-2 text-red-600",
                ),
                P(f"Status: {result['run'].status}", cls="text-red-500 mb-2"),
                P("Error in processing", cls="text-gray-600"),
                Details(
                    Summary(
                        "View Error Details",
                        cls="cursor-pointer text-red-600 hover:text-red-800",
                    ),
                    Pre(
                        result["run"].raw_response or "No error details available",
                        cls="text-sm bg-red-50 p-3 rounded mt-2 overflow-x-auto",
                    ),
                ),
                cls="bg-white p-6 rounded-lg shadow border-l-4 border-red-500",
            )
        else:
            # Success state
            strengths_section = ""
            if result["strengths"]:
                strengths_items = [
                    Li(strength, cls="mb-1") for strength in result["strengths"]
                ]
                strengths_section = Div(
                    H5("Strengths:", cls="font-semibold text-green-600 mb-2"),
                    Ul(*strengths_items, cls="list-disc list-inside text-sm mb-4"),
                )

            improvements_section = ""
            if result["improvements"]:
                improvements_items = [
                    Li(improvement, cls="mb-1")
                    for improvement in result["improvements"]
                ]
                improvements_section = Div(
                    H5(
                        "Areas for Improvement:",
                        cls="font-semibold text-orange-600 mb-2",
                    ),
                    Ul(*improvements_items, cls="list-disc list-inside text-sm mb-4"),
                )

            general_section = ""
            if result["general"]:
                general_section = Div(
                    H5("General Feedback:", cls="font-semibold text-blue-600 mb-2"),
                    P(result["general"][0], cls="text-sm text-gray-700 mb-4"),
                )

            model_card = Div(
                H4(
                    f"{result['model'].name} ({result['model'].provider})",
                    cls="text-lg font-semibold mb-4 text-green-600",
                ),
                # Feedback content
                strengths_section,
                improvements_section,
                general_section,
                # Raw response toggle
                Details(
                    Summary(
                        "View Raw AI Response",
                        cls="cursor-pointer text-gray-600 hover:text-gray-800 text-sm",
                    ),
                    Pre(
                        result["run"].raw_response or "No response available",
                        cls="text-xs bg-gray-50 p-3 rounded mt-2 overflow-x-auto max-h-64",
                    ),
                ),
                cls="bg-white p-6 rounded-lg shadow border-l-4 border-green-500",
            )

        model_details.append(model_card)

    # Build aggregated feedback section
    if agg_feedback_list:
        agg_cards = []
        for agg in agg_feedback_list:
            category = next(
                (cat for cat in assignment_rubric if cat.id == agg.category_id), None
            )
            category_name = category.name if category else "General"

            status_badge = Span(
                agg.status.replace("_", " ").title(),
                cls="px-2 py-1 text-xs font-medium rounded-full "
                + (
                    "bg-orange-100 text-orange-800"
                    if agg.status == "pending_review"
                    else "bg-green-100 text-green-800"
                    if agg.status == "approved"
                    else "bg-blue-100 text-blue-800"
                ),
            )

            agg_card = Div(
                Div(
                    H4(
                        f"{category_name}: {agg.aggregated_score:.1f}/100",
                        cls="text-lg font-semibold",
                    ),
                    status_badge,
                    cls="flex items-center justify-between mb-3",
                ),
                Div(agg.feedback_text, cls="text-sm text-gray-700 whitespace-pre-line"),
                cls="bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500",
            )
            agg_cards.append(agg_card)

        aggregated_section = Div(
            H3("Aggregated Feedback (Final Results)", cls="text-lg font-semibold mb-4"),
            *agg_cards,
            cls="mb-8",
        )
    else:
        aggregated_section = Div(
            P(
                "No aggregated feedback available yet.",
                cls="text-gray-500 text-center py-8",
            ),
            cls="bg-white rounded-lg shadow mb-8",
        )

    # Main content
    main_content = Div(
        # Header
        Div(
            Div(
                H1("Submission Details", cls="text-2xl font-bold text-gray-900"),
                P(
                    f"Student: {draft.student_email} | Version {draft.version}",
                    cls="text-gray-600",
                ),
                P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Submissions",
                    href=f"/instructor/assignments/{assignment.id}/submissions",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                A(
                    "Review Feedback",
                    href=f"/instructor/submissions/{draft_id}/review",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Submission info
        Div(
            H3("Submission Information", cls="text-lg font-semibold mb-4"),
            Div(
                Div(
                    P("Word Count", cls="text-sm font-medium text-gray-500"),
                    P(str(draft.word_count), cls="text-lg font-semibold"),
                ),
                Div(
                    P("Submitted", cls="text-sm font-medium text-gray-500"),
                    P(
                        datetime.fromisoformat(draft.submission_date).strftime(
                            "%b %d, %Y %I:%M %p"
                        ),
                        cls="text-lg font-semibold",
                    ),
                ),
                Div(
                    P("Status", cls="text-sm font-medium text-gray-500"),
                    P(
                        draft.status.replace("_", " ").title(),
                        cls="text-lg font-semibold",
                    ),
                ),
                Div(
                    P("AI Models Run", cls="text-sm font-medium text-gray-500"),
                    P(
                        f"{len([r for r in model_results if r['success']])}/{len(model_results)}",
                        cls="text-lg font-semibold",
                    ),
                ),
                cls="grid grid-cols-2 md:grid-cols-4 gap-4",
            ),
            cls="bg-white p-6 rounded-lg shadow mb-8",
        ),
        # Score comparison table
        comparison_table,
        Div(cls="mb-8"),
        # Aggregated feedback
        aggregated_section,
        # Individual model details
        Div(
            H3("Individual AI Model Results", cls="text-lg font-semibold mb-4"),
            Div(*model_details, cls="space-y-6")
            if model_details
            else P("No model results available.", cls="text-gray-500"),
            cls="mb-8",
        ),
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Actions", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            A(
                "Edit Feedback",
                href=f"/instructor/submissions/{draft_id}/edit",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "Export Results",
                href=f"/instructor/submissions/{draft_id}/export",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            A(
                "View Student View",
                href=f"/student/assignments/{assignment.id}",
                cls="block text-indigo-600 hover:text-indigo-800 mb-2",
            ),
            Hr(cls="my-4"),
            H4("Model Performance", cls="font-semibold text-gray-700 mb-2"),
            P(
                f"Success Rate: {len([r for r in model_results if r['success']])}/{len(model_results)}",
                cls="text-sm text-gray-600 mb-1",
            ),
        ),
    )

    return dashboard_layout(
        f"Submission: {draft.student_email} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}",
    )


# --- Feedback Review and Approval Interface ---
@rt("/instructor/submissions/{draft_id}/review")
@instructor_required
def get(session, draft_id: int):
    """Review and approve/edit aggregated feedback before release to students"""
    from app.models.assignment import assignments, rubric_categories
    from app.models.feedback import aggregated_feedback, drafts

    # Get current user
    user = users[session["auth"]]

    # Get draft and verify access
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get aggregated feedback
    all_agg = aggregated_feedback()
    agg_feedback_list = [af for af in all_agg if af.draft_id == draft_id]

    if not agg_feedback_list:
        return RedirectResponse(f"/instructor/submissions/{draft_id}", status_code=303)

    # Get rubric categories
    rubric_cats = rubric_categories()
    assignment_rubric = [
        cat for cat in rubric_cats if cat.assignment_id == assignment.id
    ]

    # Build review form
    review_forms = []
    for agg in agg_feedback_list:
        category = next(
            (cat for cat in assignment_rubric if cat.id == agg.category_id), None
        )
        category_name = category.name if category else "General"

        # Status indicator
        status_color = {
            "pending_review": "orange",
            "approved": "green",
            "released": "blue",
        }.get(agg.status, "gray")

        review_form = Div(
            # Header with category and score
            Div(
                H3(f"{category_name}", cls="text-lg font-semibold"),
                Div(
                    Span(
                        f"Score: {agg.aggregated_score:.1f}/100",
                        cls="text-lg font-bold text-indigo-600 mr-4",
                    ),
                    Span(
                        agg.status.replace("_", " ").title(),
                        cls=f"px-3 py-1 text-sm font-medium rounded-full bg-{status_color}-100 text-{status_color}-800",
                    ),
                    cls="flex items-center",
                ),
                cls="flex items-center justify-between mb-4",
            ),
            # Edit form
            Form(
                # Score adjustment
                Div(
                    Label(
                        "Adjusted Score (0-100):",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    Input(
                        type="number",
                        name=f"score_{agg.id}",
                        value=str(agg.aggregated_score),
                        min="0",
                        max="100",
                        step="0.1",
                        cls="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                # Feedback text editing
                Div(
                    Label(
                        "Feedback Text:",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    Textarea(
                        agg.feedback_text,
                        name=f"feedback_{agg.id}",
                        rows="8",
                        cls="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500",
                    ),
                    cls="mb-4",
                ),
                # Action buttons
                Div(
                    Button(
                        "Save Changes",
                        type="submit",
                        name="action",
                        value=f"save_{agg.id}",
                        cls="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 transition-colors mr-3",
                    ),
                    Button(
                        "Approve & Release",
                        type="submit",
                        name="action",
                        value=f"approve_{agg.id}",
                        cls="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors mr-3",
                    ),
                    Button(
                        "Mark as Reviewed",
                        type="submit",
                        name="action",
                        value=f"mark_reviewed_{agg.id}",
                        cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors",
                    ),
                    cls="flex items-center",
                ),
                method="post",
                action=f"/instructor/submissions/{draft_id}/review",
            ),
            cls="bg-white p-6 rounded-lg shadow border-l-4 border-indigo-500 mb-6",
        )
        review_forms.append(review_form)

    # Bulk actions
    bulk_actions = Div(
        H3("Bulk Actions", cls="text-lg font-semibold mb-4"),
        Form(
            Div(
                Button(
                    "Approve All Categories",
                    type="submit",
                    name="bulk_action",
                    value="approve_all",
                    cls="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 transition-colors mr-3",
                ),
                Button(
                    "Mark All as Reviewed",
                    type="submit",
                    name="bulk_action",
                    value="review_all",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors mr-3",
                ),
                Button(
                    "Reset to Pending",
                    type="submit",
                    name="bulk_action",
                    value="reset_all",
                    cls="bg-gray-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-700 transition-colors",
                ),
                cls="flex items-center",
            ),
            method="post",
            action=f"/instructor/submissions/{draft_id}/review",
        ),
        cls="bg-gray-50 p-6 rounded-lg mb-6",
    )

    # Main content
    main_content = Div(
        # Header
        Div(
            Div(
                H1("Review Feedback", cls="text-2xl font-bold text-gray-900"),
                P(
                    f"Student: {draft.student_email} | Assignment: {assignment.title}",
                    cls="text-gray-600",
                ),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Submission",
                    href=f"/instructor/submissions/{draft_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Instructions
        Div(
            H3("Review Instructions", cls="text-lg font-semibold mb-2"),
            Ul(
                Li(
                    "Review AI-generated scores and feedback for accuracy and appropriateness",
                    cls="mb-1",
                ),
                Li("Edit scores and feedback text as needed", cls="mb-1"),
                Li("Approve individual categories or use bulk actions", cls="mb-1"),
                Li(
                    "Released feedback becomes visible to students immediately",
                    cls="mb-1",
                ),
                cls="list-disc list-inside text-sm text-gray-600",
            ),
            cls="bg-blue-50 p-4 rounded-lg mb-6",
        ),
        # Bulk actions
        bulk_actions,
        # Individual category reviews
        Div(
            H3("Category Reviews", cls="text-lg font-semibold mb-4"),
            *review_forms,
        ),
        cls="max-w-4xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Review Status", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            *[
                Div(
                    P(
                        f"{next((cat.name for cat in assignment_rubric if cat.id == agg.category_id), 'General')}",
                        cls="font-medium",
                    ),
                    P(
                        agg.status.replace("_", " ").title(),
                        cls=f"text-sm text-{status_color}-600",
                    ),
                    cls="mb-3",
                )
                for agg in agg_feedback_list
                for status_color in [
                    {
                        "pending_review": "orange",
                        "approved": "green",
                        "released": "blue",
                    }.get(agg.status, "gray")
                ]
            ]
        ),
        Hr(cls="my-4"),
        H4("Quick Actions", cls="font-semibold text-gray-700 mb-2"),
        A(
            "View Student Perspective",
            href=f"/student/assignments/{assignment.id}",
            cls="block text-indigo-600 hover:text-indigo-800 text-sm mb-2",
        ),
        A(
            "Assignment Analytics",
            href=f"/instructor/assignments/{assignment.id}/analytics",
            cls="block text-indigo-600 hover:text-indigo-800 text-sm",
        ),
    )

    return dashboard_layout(
        f"Review Feedback: {draft.student_email} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/submissions/{draft_id}/review",
    )


@rt("/instructor/submissions/{draft_id}/review")
@instructor_required
def post(session, draft_id: int, **form_data):
    """Handle feedback review form submissions"""
    from datetime import datetime

    from app.models.assignment import assignments
    from app.models.feedback import aggregated_feedback, drafts

    # Get current user
    user = users[session["auth"]]

    # Verify access
    try:
        draft = drafts[draft_id]
        assignment = assignments[draft.assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get aggregated feedback
    all_agg = aggregated_feedback()
    agg_feedback_list = [af for af in all_agg if af.draft_id == draft_id]

    # Handle bulk actions
    if "bulk_action" in form_data:
        bulk_action = form_data["bulk_action"]

        for agg in agg_feedback_list:
            if bulk_action == "approve_all":
                aggregated_feedback.update(
                    agg.id,
                    {
                        "status": "approved",
                        "edited_by_instructor": True,
                        "instructor_email": user.email,
                        "release_date": datetime.now().isoformat(),
                    },
                )
            elif bulk_action == "review_all":
                aggregated_feedback.update(
                    agg.id,
                    {
                        "status": "approved",
                        "edited_by_instructor": True,
                        "instructor_email": user.email,
                    },
                )
            elif bulk_action == "reset_all":
                aggregated_feedback.update(
                    agg.id,
                    {
                        "status": "pending_review",
                        "edited_by_instructor": False,
                        "instructor_email": "",
                        "release_date": "",
                    },
                )

        return RedirectResponse(
            f"/instructor/submissions/{draft_id}/review", status_code=303
        )

    # Handle individual actions
    if "action" in form_data:
        action_parts = form_data["action"].split("_", 1)
        if len(action_parts) >= 2:
            action_type = action_parts[0]
            agg_id = int(action_parts[1])

            # Find the aggregated feedback item
            agg_item = next((af for af in agg_feedback_list if af.id == agg_id), None)
            if not agg_item:
                return RedirectResponse(
                    f"/instructor/submissions/{draft_id}/review", status_code=303
                )

            # Get updated values from form
            new_score = float(
                form_data.get(f"score_{agg_id}", agg_item.aggregated_score)
            )
            new_feedback = form_data.get(f"feedback_{agg_id}", agg_item.feedback_text)

            # Update based on action type
            update_data = {
                "aggregated_score": new_score,
                "feedback_text": new_feedback,
                "edited_by_instructor": True,
                "instructor_email": user.email,
            }

            if action_type == "approve":
                update_data.update(
                    {"status": "approved", "release_date": datetime.now().isoformat()}
                )
            elif action_type in ["save", "mark"]:
                update_data["status"] = "approved"

            aggregated_feedback.update(agg_id, update_data)

    return RedirectResponse(
        f"/instructor/submissions/{draft_id}/review", status_code=303
    )


# --- Assignment Analytics Dashboard ---
@rt("/instructor/assignments/{assignment_id}/analytics")
@instructor_required
def get(session, assignment_id: int):
    """Analytics dashboard for assignment performance and LLM effectiveness"""
    import statistics

    from app.models.assignment import assignments, rubric_categories
    from app.models.feedback import (
        aggregated_feedback,
        ai_models,
        category_scores,
        drafts,
        model_runs,
    )

    # Get current user and verify access
    user = users[session["auth"]]

    try:
        assignment = assignments[assignment_id]
        course = courses[assignment.course_id]
        if course.instructor_email != user.email:
            return RedirectResponse("/instructor/dashboard", status_code=303)
    except NotFoundError:
        return RedirectResponse("/instructor/dashboard", status_code=303)

    # Get all drafts for this assignment
    all_drafts = drafts()
    assignment_drafts = [d for d in all_drafts if d.assignment_id == assignment_id]

    # Get rubric categories
    rubric_cats = rubric_categories()
    assignment_rubric = [
        cat for cat in rubric_cats if cat.assignment_id == assignment_id
    ]

    # Get all model runs
    all_runs = model_runs()
    assignment_runs = [
        run for run in all_runs if any(d.id == run.draft_id for d in assignment_drafts)
    ]

    # Get all AI models
    all_ai_models = ai_models()
    models_map = {model.id: model for model in all_ai_models}

    # Get scores and aggregated feedback
    all_scores = category_scores()
    all_agg = aggregated_feedback()

    # Calculate submission statistics
    total_submissions = len(assignment_drafts)
    completed_feedback = len(
        [d for d in assignment_drafts if d.status == "feedback_ready"]
    )
    processing = len([d for d in assignment_drafts if d.status == "processing"])
    errors = len([d for d in assignment_drafts if d.status == "error"])

    # Calculate LLM performance statistics
    llm_stats = {}
    for run in assignment_runs:
        model = models_map.get(run.model_id)
        if not model:
            continue

        model_key = f"{model.name} ({model.provider})"
        if model_key not in llm_stats:
            llm_stats[model_key] = {
                "total_runs": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "avg_response_time": 0,
                "scores": [],
            }

        llm_stats[model_key]["total_runs"] += 1
        if run.status == "complete":
            llm_stats[model_key]["successful_runs"] += 1

            # Get scores for this run
            run_scores = [score for score in all_scores if score.model_run_id == run.id]
            if run_scores:
                avg_score = statistics.mean([score.score for score in run_scores])
                llm_stats[model_key]["scores"].append(avg_score)
        else:
            llm_stats[model_key]["failed_runs"] += 1

    # Calculate category performance
    category_performance = {}
    for category in assignment_rubric:
        category_scores_list = [
            score.score
            for score in all_scores
            if score.category_id == category.id
            and any(
                run.id == score.model_run_id and run.status == "complete"
                for run in assignment_runs
            )
        ]

        if category_scores_list:
            category_performance[category.name] = {
                "avg_score": statistics.mean(category_scores_list),
                "min_score": min(category_scores_list),
                "max_score": max(category_scores_list),
                "std_dev": statistics.stdev(category_scores_list)
                if len(category_scores_list) > 1
                else 0,
                "count": len(category_scores_list),
            }

    # Build LLM comparison table
    llm_comparison_rows = []
    for model_name, stats in llm_stats.items():
        success_rate = (
            (stats["successful_runs"] / stats["total_runs"] * 100)
            if stats["total_runs"] > 0
            else 0
        )
        avg_score = statistics.mean(stats["scores"]) if stats["scores"] else 0

        # Success rate color coding
        if success_rate >= 90:
            rate_color = "text-green-600"
        elif success_rate >= 70:
            rate_color = "text-yellow-600"
        else:
            rate_color = "text-red-600"

        llm_comparison_rows.append(
            Tr(
                Td(model_name, cls="px-4 py-3 font-medium"),
                Td(f"{stats['total_runs']}", cls="px-4 py-3 text-center"),
                Td(
                    f"{success_rate:.1f}%",
                    cls=f"px-4 py-3 text-center {rate_color} font-semibold",
                ),
                Td(
                    f"{avg_score:.1f}/100" if avg_score > 0 else "—",
                    cls="px-4 py-3 text-center",
                ),
                Td(
                    f"{len(stats['scores'])}", cls="px-4 py-3 text-center text-gray-600"
                ),
            )
        )

    llm_comparison_table = (
        Div(
            H3("AI Model Performance Comparison", cls="text-lg font-semibold mb-4"),
            Table(
                Thead(
                    Tr(
                        Th(
                            "Model",
                            cls="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Total Runs",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Success Rate",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Avg Score",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                        Th(
                            "Scored Runs",
                            cls="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase",
                        ),
                    )
                ),
                Tbody(*llm_comparison_rows, cls="bg-white divide-y divide-gray-200"),
                cls="min-w-full divide-y divide-gray-200",
            ),
            cls="bg-white rounded-lg shadow overflow-hidden mb-8",
        )
        if llm_comparison_rows
        else Div(
            P(
                "No model performance data available yet.",
                cls="text-gray-500 text-center py-8",
            ),
            cls="bg-white rounded-lg shadow mb-8",
        )
    )

    # Build category performance chart
    category_chart_bars = []
    for category_name, perf in category_performance.items():
        # Calculate bar width based on score (0-100 -> 0-100%)
        bar_width = perf["avg_score"]

        # Color coding based on score
        if bar_width >= 80:
            bar_color = "bg-green-500"
        elif bar_width >= 60:
            bar_color = "bg-yellow-500"
        else:
            bar_color = "bg-red-500"

        category_chart_bars.append(
            Div(
                Div(
                    Div(
                        P(category_name, cls="font-medium text-gray-900"),
                        P(
                            f"{perf['avg_score']:.1f}/100 avg ({perf['count']} submissions)",
                            cls="text-sm text-gray-600",
                        ),
                        cls="mb-2",
                    ),
                    Div(
                        Div(
                            cls=f"h-4 {bar_color} rounded", style=f"width: {bar_width}%"
                        ),
                        cls="w-full bg-gray-200 rounded-full h-4",
                    ),
                    cls="mb-4",
                ),
                cls="bg-white p-4 rounded-lg",
            )
        )

    category_performance_section = Div(
        H3("Rubric Category Performance", cls="text-lg font-semibold mb-4"),
        Div(*category_chart_bars, cls="space-y-4")
        if category_chart_bars
        else P(
            "No category performance data available.",
            cls="text-gray-500 text-center py-8",
        ),
        cls="mb-8",
    )

    # Summary statistics cards
    stats_cards = Div(
        Div(
            Div(
                P("Total Submissions", cls="text-sm font-medium text-gray-500"),
                P(str(total_submissions), cls="text-3xl font-bold text-gray-900"),
                P("Student drafts", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Feedback Complete", cls="text-sm font-medium text-gray-500"),
                P(str(completed_feedback), cls="text-3xl font-bold text-green-600"),
                P(
                    f"{(completed_feedback / total_submissions * 100):.1f}% complete"
                    if total_submissions > 0
                    else "0% complete",
                    cls="text-sm text-gray-600",
                ),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Processing", cls="text-sm font-medium text-gray-500"),
                P(str(processing), cls="text-3xl font-bold text-blue-600"),
                P("Currently running", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        Div(
            Div(
                P("Errors", cls="text-sm font-medium text-gray-500"),
                P(str(errors), cls="text-3xl font-bold text-red-600"),
                P("Need attention", cls="text-sm text-gray-600"),
            ),
            cls="bg-white p-6 rounded-lg shadow",
        ),
        cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
    )

    # Main content
    main_content = Div(
        # Header
        Div(
            Div(
                H1(
                    f"Analytics: {assignment.title}",
                    cls="text-2xl font-bold text-gray-900",
                ),
                P(f"Course: {course.name}", cls="text-gray-600"),
                cls="flex-1",
            ),
            Div(
                A(
                    "← Back to Assignment",
                    href=f"/instructor/assignments/{assignment_id}",
                    cls="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors",
                ),
                A(
                    "View Submissions",
                    href=f"/instructor/assignments/{assignment_id}/submissions",
                    cls="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors ml-3",
                ),
                cls="flex items-center",
            ),
            cls="flex items-center justify-between mb-6",
        ),
        # Summary stats
        stats_cards,
        # LLM performance comparison
        llm_comparison_table,
        # Category performance
        category_performance_section,
        cls="max-w-7xl mx-auto px-4 py-6",
    )

    # Sidebar content
    sidebar_content = Div(
        H3("Insights", cls="text-lg font-semibold text-gray-900 mb-4"),
        Div(
            H4("Top Performing Model", cls="font-semibold text-gray-700 mb-2"),
            P("GPT-4 (95% success)", cls="text-sm text-gray-600 mb-4")
            if llm_stats
            else P("No data yet", cls="text-sm text-gray-600 mb-4"),
            H4("Category Insights", cls="font-semibold text-gray-700 mb-2"),
            P("Writing Quality: Above average", cls="text-sm text-gray-600 mb-1")
            if category_performance
            else P("No data yet", cls="text-sm text-gray-600 mb-4"),
            P("Evidence & Support: Needs work", cls="text-sm text-gray-600 mb-4")
            if category_performance
            else "",
            H4("Recommendations", cls="font-semibold text-gray-700 mb-2"),
            Ul(
                Li(
                    "Consider adjusting rubric weights",
                    cls="text-sm text-gray-600 mb-1",
                ),
                Li("Review low-performing models", cls="text-sm text-gray-600 mb-1"),
                Li("Provide targeted feedback guidance", cls="text-sm text-gray-600"),
                cls="list-disc list-inside",
            ),
        ),
    )

    return dashboard_layout(
        f"Analytics: {assignment.title} | FeedForward",
        sidebar_content,
        main_content,
        user_role=Role.INSTRUCTOR,
        current_path=f"/instructor/assignments/{assignment_id}/analytics",
    )
