"""
Instructor AI models management routes
"""

import json
from datetime import datetime
from typing import Optional

from fasthtml import common as fh

from app import instructor_required, rt
from app.models.config import AIModel, ai_models, model_capabilities
from app.models.instructor_preferences import (
    InstructorModelPref,
    instructor_model_prefs,
)
from app.models.user import users
from app.utils.crypto import encrypt_sensitive_data
from app.utils.ui import action_button, card, dashboard_layout, status_badge


def get_instructor_id(user_email):
    """Get instructor ID from user email"""
    return user_email


@rt("/instructor/models")
@instructor_required
def instructor_models_list(session, request):
    """List all AI models available to instructor"""
    # Get current instructor information
    current_user = users[session["auth"]]
    instructor_id = get_instructor_id(current_user.email)

    # Get instructor's model preferences
    instructor_prefs = {}
    for pref in instructor_model_prefs():
        if pref.instructor_email == current_user.email:
            instructor_prefs[pref.model_id] = pref.is_active

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

            # Check if instructor has a preference for this model
            # If no preference exists, default to model's active status
            is_enabled_for_instructor = instructor_prefs.get(model.id, model.active)

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
                    "active": model.active,  # Model's actual status
                    "enabled_for_instructor": is_enabled_for_instructor,  # Instructor's preference
                }
            )

    # Sidebar content
    sidebar_content = fh.Div(
        # Navigation
        fh.Div(
            fh.H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            fh.Div(
                action_button(
                    "Dashboard", color="gray", href="/instructor/dashboard", icon="←"
                ),
                action_button(
                    "New Model",
                    color="indigo",
                    href="/instructor/models/new",
                    icon="➕",  # noqa: RUF001
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Model stats
        fh.Div(
            fh.H3("Model Statistics", cls="font-semibold text-indigo-900 mb-4"),
            fh.P(f"Total Models: {len(all_models)}", cls="text-gray-600 mb-2"),
            fh.P(
                f"Enabled for You: {sum(1 for m in all_models if m['enabled_for_instructor'])}",
                cls="text-gray-600 mb-2",
            ),
            fh.P(
                f"Your Models: {sum(1 for m in all_models if m['owner_type'] == 'instructor')}",
                cls="text-gray-600",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )

    # Main content
    main_content = fh.Div(
        fh.H2("AI Models Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Models grid
        fh.Div(
            *(
                card(
                    fh.Div(
                        fh.Div(
                            fh.H3(
                                model["name"],
                                cls="text-xl font-bold text-indigo-800 mb-2",
                            ),
                            fh.Div(
                                fh.Span(
                                    model["provider"],
                                    cls="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium",
                                ),
                                fh.Span(
                                    model["model_id"], cls="text-gray-600 text-sm ml-2"
                                ),
                                cls="mb-3",
                            ),
                            cls="mb-4",
                        ),
                        # Capabilities
                        fh.Div(
                            fh.P("Capabilities:", cls="font-medium text-gray-700 mb-2"),
                            fh.Div(
                                *(
                                    fh.Span(
                                        cap,
                                        cls="inline-block px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs mr-2 mb-2",
                                    )
                                    for cap in model["capabilities"]
                                ),
                                cls="mb-4",
                            )
                            if model["capabilities"]
                            else fh.Div(cls="mb-4"),
                            cls="mb-4",
                        ),
                        # Status and actions
                        fh.Div(
                            # Model status (only show if model is inactive)
                            fh.Div(
                                status_badge(
                                    "Model Inactive",
                                    "red",
                                ),
                                cls="mb-2",
                            ) if not model["active"] else "",

                            # Toggle switch for instructor preference
                            fh.Div(
                                fh.Label(
                                    fh.Div(
                                        fh.Span(
                                            "Enabled for your assignments",
                                            cls="text-sm font-medium text-gray-700"
                                        ),
                                        fh.Div(
                                            fh.Input(
                                                type="checkbox",
                                                checked=model["enabled_for_instructor"],
                                                cls="sr-only peer",
                                                hx_post=f"/instructor/models/toggle/{model['id']}",
                                                hx_trigger="change",
                                                hx_swap="none",
                                                disabled=not model["active"],  # Disable if model itself is inactive
                                            ),
                                            fh.Div(
                                                cls="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"
                                                + (" opacity-50" if not model["active"] else "")
                                            ),
                                            cls="relative inline-flex",
                                        ),
                                        cls="flex items-center justify-between",
                                    ),
                                    cls="cursor-pointer" if model["active"] else "cursor-not-allowed",
                                ),
                                cls="mb-3",
                            ),

                            # Owner info
                            fh.Div(
                                fh.Span(
                                    "System Model"
                                    if model["owner_type"] == "system"
                                    else "Your Model",
                                    cls="text-xs text-gray-500",
                                ),
                                cls="mb-2",
                            ),

                            # View details link (only for instructor's own models)
                            fh.Div(
                                fh.A(
                                    "View Details",
                                    href=f"/instructor/models/view/{model['id']}",
                                    cls="text-indigo-600 hover:underline text-sm",
                                ),
                                cls="text-center",
                            )
                            if model["owner_type"] == "instructor"
                            else "",
                            cls="",
                        ),
                        cls="p-4",
                    ),
                    padding=0,
                )
                for model in all_models
            ),
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
        )
        if all_models
        else fh.P(
            "No AI models configured yet.",
            cls="text-gray-500 italic text-center p-8 bg-white rounded-xl border border-gray-200",
        ),
    )

    return dashboard_layout(
            "AI Models Management",
            sidebar_content,
            main_content,
            user_role="instructor",
            current_path="/instructor/models"
    )


@rt("/instructor/models/new")
@instructor_required
def instructor_models_new(session, request):
    """Create new AI model configuration"""
    # Get current instructor
    users[session["auth"]]

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Create New Model", cls="font-semibold text-indigo-900 mb-4"),
            fh.P("Configure a new AI model for your courses.", cls="text-gray-600 mb-4"),
            action_button("Cancel", color="gray", href="/instructor/models", icon="×"),  # noqa: RUF001
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    # Main content - Model creation form
    main_content = fh.Div(
        fh.H2("Configure New AI Model", cls="text-2xl font-bold text-indigo-900 mb-6"),
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
            # Model ID with dynamic loading for Ollama
            fh.Div(
                fh.Label(
                    "Model ID",
                    for_="model_id",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Div(
                    fh.Input(
                        type="text",
                        id="model_id",
                        name="model_id",
                        placeholder="e.g., gpt-4, claude-3-opus, llama2, mistral",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                        required=True,
                    ),
                    id="model-id-container",
                ),
                fh.P(
                    "The specific model identifier for your chosen provider",
                    cls="text-sm text-gray-500 mt-1",
                ),
                fh.Div(
                    fh.Button(
                        "Fetch Available Models",
                        type="button",
                        hx_post="/instructor/models/fetch-ollama",
                        hx_include="[name='base_url']",
                        hx_target="#model-id-container",
                        hx_swap="innerHTML",
                        cls="mt-2 bg-gray-500 text-white px-3 py-1 rounded text-sm hover:bg-gray-600 hidden",
                        id="fetch-models-btn",
                    ),
                    fh.Script("""
                        document.getElementById('provider').addEventListener('change', function() {
                            const btn = document.getElementById('fetch-models-btn');
                            if (this.value === 'ollama') {
                                btn.classList.remove('hidden');
                            } else {
                                btn.classList.add('hidden');
                            }
                        });
                    """),
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
                    placeholder="e.g., GPT-4 Turbo, Claude 3 Opus",
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
            # Test configuration section
            fh.Div(
                fh.H3(
                    "Test Configuration", cls="text-lg font-semibold text-gray-800 mb-3"
                ),
                fh.P(
                    "Test your model configuration before saving:",
                    cls="text-gray-600 mb-3",
                ),
                fh.Button(
                    "Test Connection",
                    type="button",
                    hx_post="/instructor/models/test",
                    hx_include="closest form",
                    hx_target="#test-result",
                    cls="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 transition-colors",
                ),
                fh.Div(id="test-result", cls="mt-4"),
                cls="bg-gray-50 p-4 rounded-lg mb-6",
            ),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Create Model",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                fh.A(
                    "Cancel",
                    href="/instructor/models",
                    cls="ml-4 px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors",
                ),
                cls="flex items-center",
            ),
            action="/instructor/models/create",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    return dashboard_layout(
            "Configure New AI Model",
            sidebar_content,
            main_content,
            user_role="instructor",
            current_path="/instructor/models"
    )


@rt("/instructor/models/create")
@instructor_required
def instructor_models_create(
    session,
    provider: str,
    model_id: str,
    name: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
):
    """Create a new AI model configuration"""
    # Get current instructor
    current_user = users[session["auth"]]
    instructor_id = get_instructor_id(current_user.email)

    # Validate inputs
    if not provider or not model_id or not name:
        return fh.Div(
            fh.P("Missing required fields", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )

    # Build API configuration
    api_config = {}

    # Add API key if provided (encrypt it)
    if api_key and api_key.strip():
        api_config["api_key_encrypted"] = encrypt_sensitive_data(api_key.strip())

    # Add base URL if provided
    if base_url and base_url.strip():
        api_config["base_url"] = base_url.strip()

    # Add provider-specific defaults
    if provider == "ollama" and not base_url:
        api_config["base_url"] = "http://localhost:11434"

    # Create the model
    new_model = AIModel(
        id=None,  # Will be auto-assigned
        name=name,
        provider=provider,
        model_id=model_id,
        api_config=json.dumps(api_config),
        active=True,
        owner_type="instructor",
        owner_id=instructor_id,
    )

    # Save to database
    try:
        model_id = ai_models.insert(new_model)
        return fh.RedirectResponse(f"/instructor/models/view/{model_id}", status_code=303)
    except Exception as e:
        return fh.Div(
            fh.P(f"Error creating model: {e!s}", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )


@rt("/instructor/models/fetch-ollama")
@instructor_required
def fetch_ollama_models(session, base_url: str):
    """Fetch available models from Ollama server"""
    import requests

    try:
        # Clean up the URL
        ollama_url = base_url.strip().rstrip('/') + '/api/tags'

        # Try to fetch models
        resp = requests.get(ollama_url, timeout=5, verify=True)

        if resp.status_code == 200:
            models_data = resp.json()
            models = models_data.get('models', [])

            if models:
                options = [
                    fh.Option(
                        f"{m['name']} ({m.get('size', 'Unknown size')})",
                        value=m['name'].replace(':latest', '')
                    )
                    for m in models
                ]
                return fh.Select(
                    fh.Option("Select a model", value="", selected=True, disabled=True),
                    *options,
                    id="model_id",
                    name="model_id",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    required=True,
                )
            else:
                return fh.Div(
                    fh.P("No models found on server", cls="text-amber-600"),
                    fh.P("Please pull models first using: ollama pull <model-name>", cls="text-sm text-gray-500 mt-1"),
                )
        else:
            return fh.Div(
                fh.P(f"Server responded with status {resp.status_code}", cls="text-red-600"),
            )
    except requests.exceptions.SSLError:
        return fh.Div(
            fh.P("SSL Certificate error", cls="text-red-600"),
            fh.P("For self-signed certificates, you may need to configure certificate verification", cls="text-sm text-gray-500 mt-1"),
        )
    except requests.exceptions.ConnectionError:
        return fh.Div(
            fh.P("Cannot connect to Ollama server", cls="text-red-600"),
            fh.P("Please check the URL and ensure the server is running", cls="text-sm text-gray-500 mt-1"),
        )
    except Exception as e:
        return fh.Div(
            fh.P(f"Error: {e!s}", cls="text-red-600"),
        )


@rt("/instructor/models/test")
@instructor_required
def instructor_models_test(
    session, provider: str, api_key: Optional[str] = None, base_url: Optional[str] = None, model_id: Optional[str] = None
):
    """Test AI model connection"""
    import litellm

    # Validate provider
    if not provider:
        return fh.Div(
            fh.P("Please select a provider", cls="text-red-600"),
            cls="p-4 bg-red-50 rounded-lg",
        )

    # Build test configuration
    test_config = {}
    if api_key and api_key.strip():
        test_config["api_key"] = api_key.strip()
    if base_url and base_url.strip():
        # For Ollama, use api_base instead of base_url
        if provider == "ollama":
            test_config["api_base"] = base_url.strip()
        else:
            test_config["base_url"] = base_url.strip()
    elif provider == "ollama":
        test_config["api_base"] = "http://localhost:11434"

    # Test the connection
    try:
        # For Ollama, first try to get available models
        if provider == "ollama" and base_url:
            try:
                import requests
                # Try to fetch available models from Ollama
                ollama_url = base_url.strip().rstrip('/') + '/api/tags'
                resp = requests.get(ollama_url, timeout=5)
                if resp.status_code == 200:
                    models_data = resp.json()
                    available_models = [m['name'] for m in models_data.get('models', [])]
                    if available_models:
                        # Use the first available model for testing
                        model = f"ollama/{available_models[0].replace(':latest', '')}"
                    else:
                        model = "ollama/llama2"
                else:
                    model = "ollama/llama2"
            except Exception:
                model = "ollama/llama2"
        else:
            # Simple test prompt
            model = "ollama/llama2" if provider == "ollama" else f"{provider}/gpt-3.5-turbo"

        response = litellm.completion(
            model=model,
            messages=[
                {"role": "user", "content": "Say 'test successful' in 3 words or less"}
            ],
            max_tokens=10,
            temperature=0,
            **test_config,
        )

        return fh.Div(
            fh.P("✅ Connection successful!", cls="text-green-600 font-medium"),
            fh.P(
                f"Response: {response.choices[0].message.content}",
                cls="text-gray-600 text-sm mt-1",
            ),
            cls="p-4 bg-green-50 rounded-lg",
        )
    except Exception as e:
        error_msg = str(e)
        if "api_key" in error_msg.lower():
            error_msg = "Invalid or missing API key"
        elif "connection" in error_msg.lower():
            error_msg = "Could not connect to the service"

        return fh.Div(
            fh.P("❌ Connection failed", cls="text-red-600 font-medium"),
            fh.P(f"Error: {error_msg}", cls="text-gray-600 text-sm mt-1"),
            cls="p-4 bg-red-50 rounded-lg",
        )


@rt("/instructor/models/view/{model_id}")
@instructor_required
def instructor_models_view(session, model_id: int):
    """View and edit AI model configuration"""
    # Get current instructor
    current_user = users[session["auth"]]
    instructor_id = get_instructor_id(current_user.email)

    # Get the model
    model = None
    for m in ai_models():
        if m.id == model_id:
            model = m
            break

    if not model:
        return fh.RedirectResponse("/instructor/models", status_code=303)

    # Check ownership
    if model.owner_type != "instructor" or model.owner_id != instructor_id:
        return fh.RedirectResponse("/instructor/models", status_code=303)

    # Parse API config
    api_config = json.loads(model.api_config) if model.api_config else {}
    has_api_key = "api_key_encrypted" in api_config
    base_url = api_config.get("base_url", "")

    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Model Details", cls="font-semibold text-indigo-900 mb-4"),
            fh.P(f"Provider: {model.provider}", cls="text-gray-600 mb-2"),
            fh.P(f"Model ID: {model.model_id}", cls="text-gray-600 mb-2"),
            fh.P(
                f"Status: {'Active' if model.active else 'Inactive'}",
                cls="text-gray-600 mb-4",
            ),
            action_button(
                "Back to Models", color="gray", href="/instructor/models", icon="←"
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )

    # Main content
    main_content = fh.Div(
        fh.H2(f"Model: {model.name}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        # Model configuration form
        fh.Form(
            # Status toggle
            fh.Div(
                fh.Label("Status", cls="block text-sm font-medium text-gray-700 mb-2"),
                fh.Div(
                    fh.Input(
                        type="checkbox",
                        id="active",
                        name="active",
                        checked=model.active,
                        cls="mr-2",
                    ),
                    fh.Label("Active", for_="active", cls="text-gray-700"),
                    cls="flex items-center",
                ),
                cls="mb-4",
            ),
            # Display name
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
                    value=model.name,
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                    required=True,
                ),
                cls="mb-4",
            ),
            # API Key update
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
                    placeholder="Enter new API key to update"
                    if has_api_key
                    else "Enter API key",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                fh.P(
                    "API key is configured. Enter new key to update."
                    if has_api_key
                    else "No API key configured.",
                    cls="text-sm text-gray-500 mt-1",
                ),
                cls="mb-4",
            ),
            # Base URL
            fh.Div(
                fh.Label(
                    "Base URL",
                    for_="base_url",
                    cls="block text-sm font-medium text-gray-700 mb-2",
                ),
                fh.Input(
                    type="url",
                    id="base_url",
                    name="base_url",
                    value=base_url,
                    placeholder="Custom API endpoint (if applicable)",
                    cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500",
                ),
                cls="mb-6",
            ),
            # Hidden fields
            fh.Input(type="hidden", name="model_id", value=str(model.id)),
            # Submit buttons
            fh.Div(
                fh.Button(
                    "Save Changes",
                    type="submit",
                    cls="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors",
                ),
                fh.Button(
                    "Delete Model",
                    type="button",
                    onclick=f"if(confirm('Are you sure you want to delete this model?')) {{ window.location.href = '/instructor/models/delete/{model.id}'; }}",
                    cls="ml-4 bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700 transition-colors",
                ),
                cls="flex items-center",
            ),
            action=f"/instructor/models/update/{model.id}",
            method="post",
            cls="bg-white p-6 rounded-xl shadow-md",
        ),
    )

    return dashboard_layout(
            f"Model: {model.name}",
            sidebar_content,
            main_content,
            user_role="instructor",
            current_path="/instructor/models"
    )


@rt("/instructor/models/toggle/{model_id}")
@instructor_required
def toggle_model_preference(session, model_id: int):
    """Toggle a model's active status for an instructor"""
    current_user = users[session["auth"]]

    # Check if preference already exists
    existing_pref = None
    for pref in instructor_model_prefs():
        if pref.instructor_email == current_user.email and pref.model_id == model_id:
            existing_pref = pref
            break

    if existing_pref:
        # Toggle existing preference
        existing_pref.is_active = not existing_pref.is_active
        existing_pref.updated_at = datetime.now().isoformat()
        instructor_model_prefs.update(existing_pref)
    else:
        # Create new preference (default to enabled)
        # Get next ID
        all_prefs = list(instructor_model_prefs())
        next_id = max([p.id for p in all_prefs], default=0) + 1

        new_pref = InstructorModelPref(
            id=next_id,
            instructor_email=current_user.email,
            model_id=model_id,
            is_active=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )
        instructor_model_prefs.insert(new_pref)

    # Return empty response (HTMX doesn't need content for this toggle)
    return ""
