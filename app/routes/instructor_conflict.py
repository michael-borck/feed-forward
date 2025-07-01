"""
Instructor routes - refactored into modules

All instructor routes have been organized into logical modules:
- dashboard: Main instructor dashboard
- models: AI model management
- courses: Course creation and management
- assignments: Assignment creation and rubric management
- submissions: Submission review and feedback approval
- students: Student enrollment and invitation management
- analytics: Performance analytics and reporting

This file imports all routes from the modules to maintain compatibility.
"""

# Import all routes from instructor modules
from app.routes.instructor.dashboard import *
from app.routes.instructor.models import *
from app.routes.instructor.courses import *
from app.routes.instructor.assignments import *
from app.routes.instructor.submissions import *
from app.routes.instructor.students import *
from app.routes.instructor.analytics import *
from app import basic_auth, role_required, instructor_required, student_required, admin_required

# --- Utility Functions ---
def generate_invitation_token(length=40):
    """Generate a random token for student invitations"""
    chars = string.ascii_letters + string.digits + '-_'
    return ''.join(random.choice(chars) for _ in range(length))
    
def get_instructor_id(user_email):
    """Get instructor ID from user email"""
    # In this database schema, email is used as the primary key/ID for users
    # So we'll just return the email as the instructor ID
    return user_email

# --- Instructor Models Management ---
@rt('/instructor/models')
@instructor_required
def get(session, request):
    # Get current instructor information
    current_user = users[session['auth']]
    instructor_id = get_instructor_id(current_user.email)
    
    # Get all available models (system models + instructor's own models)
    all_models = []
    for model in ai_models():
        # Include if system model or owned by this instructor
        if model.owner_type == 'system' or (model.owner_type == 'instructor' and model.owner_id == instructor_id):
            # Get capabilities for this model
            capabilities = []
            primary_capability = None
            
            for cap in model_capabilities():
                if cap.model_id == model.id:
                    capabilities.append(cap.capability)
                    if cap.is_primary:
                        primary_capability = cap.capability
            
            all_models.append({
                'id': model.id,
                'name': model.name,
                'provider': model.provider,
                'model_id': model.model_id,
                'version': "",
                'description': "",
                'capabilities': capabilities,
                'primary_capability': primary_capability,
                'owner_type': model.owner_type,
                'active': model.active
            })
    
    # Sidebar content
    sidebar_content = Div(
        # Course navigation
        Div(
            H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("New Model", color="indigo", href="/instructor/models/new", icon="➕"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Model Stats
        Div(
            H3("Model Stats", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                P(f"System Models: {sum(1 for m in all_models if m['owner_type'] == 'system')}", cls="text-gray-600 mb-2"),
                P(f"Your Models: {sum(1 for m in all_models if m['owner_type'] == 'instructor')}", cls="text-indigo-600 mb-2"),
                P(f"Active Models: {sum(1 for m in all_models if m['active'])}", cls="text-green-600 mb-2"),
                cls="space-y-1"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content
    main_content = Div(
        H1("AI Models Management", cls="text-3xl font-bold text-indigo-900 mb-4"),
        P("Configure AI models for assessment feedback.", cls="text-gray-600 mb-6"),
        
        # Models explanation
        Div(
            H3("Using AI Models", cls="text-lg font-semibold text-indigo-800 mb-2"),
            P("AI models are used to generate feedback for student assignments.", cls="text-gray-600 mb-1"),
            P("System models are available to all instructors.", cls="text-gray-600 mb-1"),
            P("You can also create your own models with your API keys.", cls="text-gray-600 mb-1"),
            cls="bg-indigo-50 p-4 rounded-lg mb-6"
        ),
        
        # Add model button
        Div(
            action_button("Add New Model", color="indigo", href="/instructor/models/new", icon="➕", size="regular"),
            cls="mb-6"
        ),
        
        # Model table
        Div(
            Table(
                Thead(
                    Tr(
                        Th("Name", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Provider", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Model ID", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Capabilities", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Type", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Status", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                        Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                    ),
                    cls="bg-indigo-50"
                ),
                Tbody(
                    *(Tr(
                        Td(model['name'], cls="py-4 px-6"),
                        Td(model['provider'], cls="py-4 px-6"),
                        Td(model['model_id'], cls="py-4 px-6"),
                        Td(
                            ", ".join(model['capabilities']), 
                            cls="py-4 px-6"
                        ),
                        Td(
                            Span("System" if model['owner_type'] == 'system' else "Your Model", 
                                 cls="px-3 py-1 rounded-full text-xs " + 
                                 ("bg-indigo-100 text-indigo-800" if model['owner_type'] == 'system' else 
                                  "bg-teal-100 text-teal-800")),
                            cls="py-4 px-6"
                        ),
                        Td(
                            Span("Active" if model['active'] else "Inactive", 
                                 cls="px-3 py-1 rounded-full text-xs " + 
                                 ("bg-green-100 text-green-800" if model['active'] else 
                                  "bg-gray-100 text-gray-800")),
                            cls="py-4 px-6"
                        ),
                        Td(
                            Div(
                                *(
                                    [A("Edit", 
                                      cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                      href=f"/instructor/models/edit/{model['id']}")] 
                                    if model['owner_type'] == 'instructor' else
                                    [A("View", 
                                      cls="bg-blue-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-blue-700 transition-colors shadow-sm",
                                      href=f"/instructor/models/view/{model['id']}")]
                                ),
                                cls="flex"
                            ),
                            cls="py-4 px-6"
                        )
                    ) for model in all_models)
                ),
                cls="w-full border-collapse"
            ),
            cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100 mt-4"
        ),
    )
    
    return Titled(
        "AI Models Management | FeedForward",
        dashboard_layout("AI Models", sidebar_content, main_content, user_role=Role.INSTRUCTOR)
    )
    
# --- New AI Model Form for Instructors ---
@rt('/instructor/models/new')
@instructor_required
def get(session, request):
    # Get current user information
    current_user = users[session['auth']]
    instructor_id = get_instructor_id(current_user.email)
    
    # Sidebar content
    sidebar_content = Div(
        # Navigation
        Div(
            H3("Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Models", color="gray", href="/instructor/models", icon="←"),
                action_button("Dashboard", color="gray", href="/instructor/dashboard", icon="🏠"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
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
                    cls="mb-4 p-3 bg-gray-50 rounded-lg"
                ),
                Div(
                    H4("Anthropic", cls="font-semibold text-indigo-800 mb-1"),
                    P("API Key required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: claude-3-opus, claude-3-sonnet", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg"
                ),
                Div(
                    H4("Ollama", cls="font-semibold text-indigo-800 mb-1"),
                    P("Server URL required", cls="text-gray-600 mb-1 text-sm"),
                    P("Models: llama3, mistral", cls="text-gray-600 text-sm"),
                    cls="mb-4 p-3 bg-gray-50 rounded-lg"
                ),
                cls="space-y-1"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - Add new AI Model form
    main_content = Div(
        H1("Add New AI Model", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P("Configure a new AI model for assignment feedback.", cls="text-gray-600 mb-8"),
        
        # Model configuration form
        Form(
            # Basic model information
            Div(
                H2("Model Information", cls="text-2xl font-bold text-indigo-900 mb-6"),
                Div(
                    Div(
                        Label("Model Name", for_="name", cls="block text-indigo-900 font-medium mb-1"),
                        P("Display name for this model", cls="text-sm text-gray-500 mb-1"),
                        Input(type="text", id="name", name="name", required=True, 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("Provider", for_="provider", cls="block text-indigo-900 font-medium mb-1"),
                        P("AI model provider", cls="text-sm text-gray-500 mb-1"),
                        Select(
                            Option("Select a provider", value="", disabled=True, selected=True),
                            Option("OpenAI", value="OpenAI"),
                            Option("Anthropic", value="Anthropic"),
                            Option("Ollama", value="Ollama"),
                            Option("HuggingFace", value="HuggingFace"),
                            Option("Other", value="Other"),
                            id="provider", name="provider", required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        ),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("Model ID", for_="model_id", cls="block text-indigo-900 font-medium mb-1"),
                        P("Specific model identifier (e.g., gpt-4, claude-3-opus)", cls="text-sm text-gray-500 mb-1"),
                        Input(type="text", id="model_id", name="model_id", required=True, 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("Version", for_="version", cls="block text-indigo-900 font-medium mb-1"),
                        P("Version information (optional)", cls="text-sm text-gray-500 mb-1"),
                        Input(type="text", id="version", name="version", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                        P("Brief description of this model's capabilities", cls="text-sm text-gray-500 mb-1"),
                        Textarea(id="description", name="description", rows=3,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full"
                    ),
                    
                    Div(
                        Label("Maximum Context Length", for_="max_context", cls="block text-indigo-900 font-medium mb-1"),
                        P("Maximum token length this model can process", cls="text-sm text-gray-500 mb-1"),
                        Input(type="number", id="max_context", name="max_context", value="8192", min="1024", step="1024",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("Status", for_="active", cls="block text-indigo-900 font-medium mb-1"),
                        Select(
                            Option("Active", value="true", selected=True),
                            Option("Inactive", value="false"),
                            id="active", name="active", required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        ),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    # Create a hidden field for instructor_id
                    Input(type="hidden", id="owner_id", name="owner_id", value=str(instructor_id)),
                    Input(type="hidden", id="owner_type", name="owner_type", value="instructor"),
                    
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                
                # Model capabilities section
                H2("Model Capabilities", cls="text-2xl font-bold text-indigo-900 mb-6 mt-8"),
                Div(
                    P("Select which capabilities this model supports:", cls="text-gray-600 mb-4"),
                    
                    Div(
                        Div(
                            Input(type="checkbox", id="capability_text", name="capabilities", value="text", checked=True,
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label("Text", for_="capability_text", cls="ml-2 text-indigo-900"),
                            cls="flex items-center mb-2"
                        ),
                        Div(
                            Input(type="checkbox", id="capability_code", name="capabilities", value="code",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label("Code", for_="capability_code", cls="ml-2 text-indigo-900"),
                            cls="flex items-center mb-2"
                        ),
                        Div(
                            Input(type="checkbox", id="capability_vision", name="capabilities", value="vision",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label("Vision", for_="capability_vision", cls="ml-2 text-indigo-900"),
                            cls="flex items-center mb-2"
                        ),
                        Div(
                            Input(type="checkbox", id="capability_audio", name="capabilities", value="audio",
                                cls="h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label("Audio", for_="capability_audio", cls="ml-2 text-indigo-900"),
                            cls="flex items-center mb-2"
                        ),
                        cls="mb-6"
                    ),
                    
                    H3("Primary Capability", cls="text-xl font-bold text-indigo-900 mb-2"),
                    P("Select the primary capability this model is optimized for:", cls="text-gray-600 mb-4"),
                    
                    Div(
                        Select(
                            Option("Text", value="text", selected=True),
                            Option("Code", value="code"),
                            Option("Vision", value="vision"),
                            Option("Audio", value="audio"),
                            id="primary_capability", name="primary_capability", required=True,
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        ),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                
                # API Configuration section
                H2("API Configuration", cls="text-2xl font-bold text-indigo-900 mb-6 mt-8"),
                Div(
                    Div(id="openai-config", cls="w-full"),
                    Div(id="anthropic-config", cls="w-full hidden"),
                    Div(id="ollama-config", cls="w-full hidden"),
                    Div(id="huggingface-config", cls="w-full hidden"),
                    Div(id="other-config", cls="w-full hidden"),
                    
                    # OpenAI Config
                    Div(
                        Label("API Key", for_="openai_api_key", cls="block text-indigo-900 font-medium mb-1"),
                        P("OpenAI API key", cls="text-sm text-gray-500 mb-1"),
                        Input(type="password", id="openai_api_key", name="openai_api_key", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        P("Note: API keys are stored encrypted in the database", cls="text-xs text-amber-600 mt-1"),
                        cls="mb-6 w-full"
                    ),
                    
                    # Anthropic Config
                    Div(
                        Label("API Key", for_="anthropic_api_key", cls="block text-indigo-900 font-medium mb-1"),
                        P("Anthropic API key", cls="text-sm text-gray-500 mb-1"),
                        Input(type="password", id="anthropic_api_key", name="anthropic_api_key", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        P("Note: API keys are stored encrypted in the database", cls="text-xs text-amber-600 mt-1"),
                        cls="mb-6 w-full hidden", id="anthropic-config"
                    ),
                    
                    # Ollama Config
                    Div(
                        Label("Server URL", for_="ollama_base_url", cls="block text-indigo-900 font-medium mb-1"),
                        P("Ollama server URL (e.g., http://localhost:11434)", cls="text-sm text-gray-500 mb-1"),
                        Input(type="text", id="ollama_base_url", name="ollama_base_url", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full hidden", id="ollama-config"
                    ),
                    
                    # Common settings
                    Div(
                        Label("Temperature", for_="temperature", cls="block text-indigo-900 font-medium mb-1"),
                        P("Controls randomness (0.0-1.0)", cls="text-sm text-gray-500 mb-1"),
                        Input(type="number", id="temperature", name="temperature", value="0.2", min="0", max="1", step="0.1",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full md:w-1/2"
                    ),
                    
                    Div(
                        Label("System Prompt", for_="system_prompt", cls="block text-indigo-900 font-medium mb-1"),
                        P("Default system prompt for educational assessment", cls="text-sm text-gray-500 mb-1"),
                        Textarea(id="system_prompt", name="system_prompt", rows=3,
                            value="You are an expert educational assessor providing detailed, constructive feedback on student work.",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-6 w-full"
                    ),
                    
                    # Provider selection script
                    Script("""
                    document.getElementById('provider').addEventListener('change', function() {
                        // Hide all config sections
                        document.getElementById('openai-config').classList.add('hidden');
                        document.getElementById('anthropic-config').classList.add('hidden');
                        document.getElementById('ollama-config').classList.add('hidden');
                        document.getElementById('huggingface-config').classList.add('hidden');
                        document.getElementById('other-config').classList.add('hidden');
                        
                        // Show selected provider config
                        if (this.value === 'OpenAI') {
                            document.getElementById('openai-config').classList.remove('hidden');
                        } else if (this.value === 'Anthropic') {
                            document.getElementById('anthropic-config').classList.remove('hidden');
                        } else if (this.value === 'Ollama') {
                            document.getElementById('ollama-config').classList.remove('hidden');
                        } else if (this.value === 'HuggingFace') {
                            document.getElementById('huggingface-config').classList.remove('hidden');
                        } else if (this.value === 'Other') {
                            document.getElementById('other-config').classList.remove('hidden');
                        }
                    });
                    """),
                    
                    cls="flex flex-wrap -mx-3 mb-8 bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                
                # Form submission
                Div(
                    Div(id="form-message", cls="mb-4"),
                    Div(
                        Button("Cancel", type="button", onClick="window.location='/instructor/models'",
                               cls="bg-gray-500 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-600 transition-colors shadow-sm mr-4"),
                        Button("Save Model", type="submit",
                               cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="flex"
                    ),
                    cls="mt-6"
                ),
                
                cls="mb-8"
            ),
            hx_post="/instructor/models/create",
            hx_target="#form-message",
        )
    )
    
    return Titled(
        "Add New AI Model | FeedForward",
        dashboard_layout("Add New Model", sidebar_content, main_content, user_role=Role.INSTRUCTOR)
    )

# --- Create New AI Model (Instructor) ---
@rt('/instructor/models/create')
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
    ollama_base_url: str = None
):
    try:
        # Verify current user is the owner or an admin
        current_user = users[session['auth']]
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
                "system_prompt": system_prompt
            }
        elif provider == "Anthropic":
            api_config = {
                "api_key": anthropic_api_key,
                "temperature": float(temperature),
                "system_prompt": system_prompt
            }
        elif provider == "Ollama":
            api_config = {
                "base_url": ollama_base_url,
                "temperature": float(temperature)
            }
        
        # For security, encrypt API keys if present
        for key in api_config:
            if key.endswith('api_key') and api_config[key]:
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
            updated_at=now
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
                is_primary=(capability == primary_capability)
            )
            model_capabilities.insert(cap)
        
        # Return success message with redirect
        return Div(
            P(f"AI Model '{name}' created successfully!", cls="text-green-500 mb-2"),
            Script("setTimeout(function() { window.location = '/instructor/models'; }, 1500);"),
            cls="bg-green-50 p-4 rounded-lg"
        )
    except Exception as e:
        # Return error message
        return Div(
            P(f"Error creating AI model: {str(e)}", cls="text-red-500"),
            cls="bg-red-50 p-4 rounded-lg"
        )

# --- Instructor Dashboard ---
@rt('/instructor/dashboard')
@instructor_required
def get(session, request):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Add AI Models section to the dashboard
    from app.utils.ui import card
    ai_models_section = Div(
        H2("AI Models", cls="text-xl font-bold text-indigo-900 mb-4"),
        P("Configure AI models for assessment feedback.", cls="text-gray-600 mb-4"),
        
        # Model management card
        Div(
            Div(
                H3("Model Management", cls="font-semibold text-indigo-800 mb-2"),
                P("Add, view, and manage AI models for assessment.", cls="text-gray-600 mb-2"),
                action_button("Manage Models", color="indigo", href="/instructor/models", icon="⚙️", size="small"),
                cls="p-4"
            ),
            cls="bg-white rounded-xl shadow-md border border-gray-100 mb-4 hover:shadow-lg transition-shadow"
        )
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
                A("View All Courses", href="/instructor/courses", 
                  cls="text-indigo-600 hover:text-indigo-800 text-sm font-medium"),
                cls="flex justify-between items-center mb-6"
            ),
            Div(
                *[
                    Div(
                        Div(
                            Div(
                                H3(course.title, cls="text-xl font-bold text-indigo-900 mb-1"),
                                P(f"Course Code: {course.code}", cls="text-gray-600"),
                                P(f"Students: {student_count}", cls="text-gray-600"),
                                cls="mb-4"
                            ),
                            Div(
                                A("View Students", href=f"/instructor/courses/{course.id}/students", 
                                  cls="text-indigo-600 hover:text-indigo-800 mr-3 font-medium"),
                                A("Manage Assignments", href=f"/instructor/courses/{course.id}/assignments", 
                                  cls="text-teal-600 hover:text-teal-800 font-medium"),
                                cls="flex"
                            ),
                            cls=""
                        ),
                        cls="bg-white p-6 rounded-xl shadow-md hover:shadow-lg transition-shadow border border-gray-100"
                    )
                    for course, student_count in instructor_courses
                ],
                cls="grid grid-cols-1 md:grid-cols-2 gap-6"
            ),
            cls=""
        )
    else:
        # Show a message if no courses yet
        courses_content = card(
            Div(
                P("You don't have any courses yet. Create your first course to get started.", 
                  cls="text-center text-gray-600 mb-6"),
                Div(
                    A("Create New Course", href="/instructor/courses/new", 
                      cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="text-center"
                ),
                cls="py-8"
            ),
            title="Welcome to the Instructor Dashboard"
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
                        P("Create a new course for your students", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Create Course", href="/instructor/courses/new", 
                          cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Manage Courses card
            card(
                Div(
                    Div(
                        Span("📚", cls="text-4xl"),
                        P("View and manage all your courses", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Manage Courses", href="/instructor/courses", 
                          cls="bg-amber-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-amber-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Invite Students card
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P("Invite students to join your course", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Invite Students", href="/instructor/invite-students", 
                          cls="bg-teal-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # Manage Students card 
            card(
                Div(
                    Div(
                        Span("👨‍👩‍👧‍👦", cls="text-4xl"),
                        P("Manage your enrolled students", cls="mt-2 text-gray-600"),
                        cls="text-center py-4"
                    ),
                    Div(
                        A("Manage Students", href="/instructor/manage-students", 
                          cls="bg-indigo-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm w-full text-center block"),
                        cls="mt-4"
                    ),
                    cls="h-full flex flex-col justify-between"
                )
            ),
            # TODO: Add more action cards as features are developed
            cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        ),
        cls="mt-10"
    )
    
    # Main content with courses, AI models section, and action cards
    main_content = Div(
        courses_content,
        ai_models_section,
        action_cards,
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        # Instructor info card
        card(
            Div(
                Div(
                    Div(
                        user.name[0] if user.name else "?",
                        cls="w-16 h-16 rounded-full bg-indigo-600 text-white flex items-center justify-center text-2xl font-bold"
                    ),
                    cls="flex justify-center mb-4"
                ),
                H3(user.name, cls="text-lg font-bold text-center text-indigo-900"),
                P(user.email, cls="text-center text-gray-600 mb-4"),
                Hr(cls="my-4"),
                Div(
                    P(f"Courses: {len(instructor_courses)}", cls="text-gray-600"),
                    P(f"Department: {user.department if user.department else 'Not set'}", cls="text-gray-600"),
                    cls="text-sm"
                ),
                cls="p-2"
            ),
            title="Profile"
        ),
        # Recent activity or tips
        card(
            Div(
                Div(
                    P("✓ Complete your profile information", cls="mb-2 text-green-600"),
                    P("✓ Create your first course", cls="mb-2 text-green-600") if instructor_courses else P("○ Create your first course", cls="mb-2 text-gray-600"),
                    P("○ Invite students to your course", cls="mb-2 text-gray-600"),
                    P("○ Create your first assignment", cls="mb-2 text-gray-600"),
                    cls="text-sm"
                ),
                cls="p-2"
            ),
            title="Getting Started"
        ),
        cls="space-y-6"
    )
    
    # Use the dashboard layout with our components
    from app.utils.ui import dashboard_layout
    return dashboard_layout(
        "Instructor Dashboard | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path
    )

# --- Assignment Management ---
# Helper function to get an assignment by ID with instructor permission check
def get_instructor_assignment(assignment_id, instructor_email):
    """
    Get an assignment by ID, checking that it belongs to the instructor.
    Returns (assignment, error_message) tuple.
    """
    # Import assignments model
    from app.models.assignment import Assignment, assignments
    
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
        if hasattr(target_assignment, 'status') and target_assignment.status == "deleted":
            return None, "This assignment has been deleted."
            
        return target_assignment, None
    except Exception as e:
        return None, f"Error accessing assignment: {str(e)}"
@rt('/instructor/courses/{course_id}/assignments')
@instructor_required
def get(session, course_id: int):
    """Shows all assignments for a specific course"""
    # Get current user
    user = users[session['auth']]
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Import assignments model
    from app.models.assignment import Assignment, assignments
    
    # Get all assignments for this course
    course_assignments = []
    for assignment in assignments():
        if assignment.course_id == course_id and assignment.created_by == user.email:
            # Skip deleted assignments
            if hasattr(assignment, 'status') and assignment.status == "deleted":
                continue
            course_assignments.append(assignment)
    
    # Sort assignments by creation date (newest first)
    course_assignments.sort(key=lambda x: x.created_at if hasattr(x, 'created_at') else "", reverse=True)
    
    # Create the main content
    main_content = Div(
        # Header with action button
        Div(
            H2(f"Assignments for {course.title}", cls="text-2xl font-bold text-indigo-900"),
            action_button("Create New Assignment", color="indigo", href=f"/instructor/courses/{course_id}/assignments/new", icon="+"),
            cls="flex justify-between items-center mb-6"
        ),
        
        # Assignment listing or empty state
        (Div(
            P(f"This course has {len(course_assignments)} {'assignment' if len(course_assignments) == 1 else 'assignments'}.", 
              cls="text-gray-600 mb-6"),
            
            # Assignment table with actions
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Title", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Status", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Due Date", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Drafts", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                        ),
                        cls="bg-indigo-50"
                    ),
                    Tbody(
                        *(Tr(
                            # Assignment title
                            Td(assignment.title, cls="py-4 px-6"),
                            # Status badge
                            Td(
                                status_badge(
                                    getattr(assignment, 'status', 'draft').capitalize(),
                                    "gray" if getattr(assignment, 'status', 'draft') == 'draft' else
                                    "green" if getattr(assignment, 'status', 'draft') == 'active' else
                                    "yellow" if getattr(assignment, 'status', 'draft') == 'closed' else
                                    "blue" if getattr(assignment, 'status', 'draft') == 'archived' else
                                    "red"
                                ),
                                cls="py-4 px-6"
                            ),
                            # Due date
                            Td(getattr(assignment, 'due_date', 'Not set') or 'Not set', cls="py-4 px-6"),
                            # Max drafts allowed
                            Td(str(getattr(assignment, 'max_drafts', 1) or 1), cls="py-4 px-6"),
                            # Action buttons
                            Td(
                                Div(
                                    A("Edit", 
                                      href=f"/instructor/assignments/{assignment.id}/edit",
                                      cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2"),
                                    A("Rubric", 
                                      href=f"/instructor/assignments/{assignment.id}/rubric",
                                      cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700 mr-2"),
                                    A("Submissions", 
                                      href=f"/instructor/assignments/{assignment.id}/submissions",
                                      cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"),
                                    cls="flex"
                                ),
                                cls="py-4 px-6"
                            )
                        ) for assignment in course_assignments)
                    ),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ),
            cls=""
        ) if course_assignments else
        Div(
            P("This course doesn't have any assignments yet. Create your first assignment to get started.", 
              cls="text-center text-gray-600 mb-6"),
            Div(
                A("Create New Assignment", href=f"/instructor/courses/{course_id}/assignments/new", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="text-center"
            ),
            cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4"
        ))
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Courses", color="gray", href="/instructor/courses", icon="←"),
                action_button("Course Details", color="blue", href=f"/instructor/courses/{course_id}/edit", icon="📝"),
                action_button("Manage Students", color="teal", href=f"/instructor/courses/{course_id}/students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Assignment Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Create Assignment", color="indigo", href=f"/instructor/courses/{course_id}/assignments/new", icon="+"),
                cls="space-y-3"
            ),
            P("Assignment Statuses:", cls="text-sm text-gray-600 font-medium mt-4 mb-2"),
            P("Draft: Only visible to you", cls="text-xs text-gray-600 mb-1"),
            P("Active: Available to students", cls="text-xs text-gray-600 mb-1"),
            P("Closed: No new submissions", cls="text-xs text-gray-600 mb-1"),
            P("Archived: Hidden from students", cls="text-xs text-gray-600 mb-1"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return the complete page
    return dashboard_layout(
        f"Assignments for {course.title} | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/{course_id}/assignments/new')
@instructor_required
def get(session, course_id: int):
    """Form to create a new assignment"""
    # Get current user
    user = users[session['auth']]
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Check course status - don't allow new assignments for closed/archived/deleted courses
    if hasattr(course, 'status') and course.status in ['closed', 'archived', 'deleted']:
        return Div(
            H2("Course Not Active", cls="text-2xl font-bold text-amber-700 mb-4"),
            P(f"This course is currently '{course.status}'. You cannot add new assignments to a {course.status} course.", 
              cls="text-gray-700 mb-4"),
            A("Back to Course", href=f"/instructor/courses/{course_id}/assignments", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-amber-50 rounded-xl shadow-md border-2 border-amber-200 text-center"
        )
    
    # Form to create a new assignment
    form_content = Div(
        H2(f"Create New Assignment for {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        P("Complete the form below to create a new assignment for your students.", cls="text-gray-600 mb-6"),
        
        Form(
            # Title field
            Div(
                Label("Assignment Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                Input(id="title", name="title", type="text", placeholder="e.g. Midterm Essay",
                      required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                cls="mb-4"
            ),
            
            # Description field
            Div(
                Label("Assignment Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                Textarea(id="description", name="description", placeholder="Provide detailed instructions for the assignment",
                         rows="6", cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                cls="mb-4"
            ),
            
            # Due date and max drafts
            Div(
                Div(
                    Label("Due Date (Optional)", for_="due_date", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="due_date", name="due_date", type="date", 
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="w-1/2 pr-2"
                ),
                Div(
                    Label("Maximum Drafts", for_="max_drafts", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="max_drafts", name="max_drafts", type="number", min="1", value="3",
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="w-1/2 pl-2"
                ),
                cls="flex mb-4"
            ),
            
            # Status selection
            Div(
                Label("Assignment Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                Select(
                    Option("Draft - Only visible to you", value="draft", selected=True),
                    Option("Active - Available to students", value="active"),
                    id="status", name="status",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                ),
                cls="mb-6"
            ),
            
            # Submit button
            Div(
                Button("Create Assignment", type="submit", 
                       cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="mb-4"
            ),
            
            # Result placeholder
            Div(id="result"),
            
            # Form submission details
            hx_post=f"/instructor/courses/{course_id}/assignments/new",
            hx_target="#result",
            
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Assignment Creation", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Assignments", color="gray", href=f"/instructor/courses/{course_id}/assignments", icon="←"),
                action_button("Course Details", color="blue", href=f"/instructor/courses/{course_id}/edit", icon="📝"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Assignment Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Provide clear expectations and grading criteria", cls="text-gray-600 mb-2 text-sm"),
            P("• Set draft limits based on your feedback capacity", cls="text-gray-600 mb-2 text-sm"),
            P("• Leave in 'Draft' mode until ready for students", cls="text-gray-600 mb-2 text-sm"),
            P("• Create a detailed rubric after assignment creation", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return the complete page
    return dashboard_layout(
        f"Create Assignment | {course.title} | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/{course_id}/assignments/new')
@instructor_required
def post(session, course_id: int, title: str, description: str, due_date: str = "", 
        max_drafts: int = 3, status: str = "draft"):
    """Handle new assignment creation"""
    # Get current user
    user = users[session['auth']]
    
    # Validate required fields
    if not title:
        return "Assignment title is required."
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Check course status - don't allow new assignments for closed/archived/deleted courses
    if hasattr(course, 'status') and course.status in ['closed', 'archived', 'deleted']:
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
    if status not in ['draft', 'active', 'closed', 'archived']:
        status = 'draft'  # Default to draft if invalid
    
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
        updated_at=now
    )
    
    # Insert into database
    assignments.insert(new_assignment)
    
    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Assignment Created Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your assignment \"{title}\" has been created.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Back to Assignments", href=f"/instructor/courses/{course_id}/assignments", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Create Rubric", href=f"/instructor/assignments/{next_assignment_id}/rubric", 
                  cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4"),
                A("View Assignment", href=f"/instructor/assignments/{next_assignment_id}", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )

@rt('/instructor/assignments/{assignment_id}')
@instructor_required
def get(session, assignment_id: int):
    """View individual assignment details"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Get the course this assignment belongs to
    course, course_error = get_instructor_course(assignment.course_id, user.email)
    
    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Get submissions for this assignment if any
    from app.models.feedback import Draft, drafts
    
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
                    getattr(assignment, 'status', 'draft').capitalize(),
                    cls="text-xl font-semibold " + 
                    ("text-gray-700" if getattr(assignment, 'status', 'draft') == 'draft' else
                     "text-green-700" if getattr(assignment, 'status', 'draft') == 'active' else
                     "text-amber-700" if getattr(assignment, 'status', 'draft') == 'closed' else
                     "text-blue-700")
                ),
                P("Assignment Status", cls="text-gray-600"),
                cls="py-2 px-6"
            ),
            Div(
                Span(getattr(assignment, 'due_date', 'Not set') or 'Not set', 
                     cls="text-xl font-semibold text-indigo-700"),
                P("Due Date", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200"
            ),
            Div(
                Span(str(getattr(assignment, 'max_drafts', 1) or 1) + " drafts", 
                     cls="text-xl font-semibold text-indigo-700"),
                P("Maximum Drafts", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200"
            ),
            Div(
                Span(f"{submission_count} submissions", 
                     cls="text-xl font-semibold text-indigo-700"),
                P("Student Submissions", cls="text-gray-600"),
                cls="py-2 px-6 border-l border-gray-200"
            ),
            cls="flex justify-between mb-6 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Assignment details
        Div(
            H2(assignment.title, cls="text-2xl font-bold text-indigo-900 mb-4"),
            
            # Description
            Div(
                H3("Assignment Description", cls="text-lg font-semibold text-indigo-800 mb-3"),
                Div(
                    P(assignment.description.replace('\n', '<br>') if assignment.description else "No description provided.", 
                      cls="text-gray-700 whitespace-pre-line"),
                    cls="py-4"
                ),
                cls="mb-6 bg-white rounded-xl shadow-md border border-gray-100 p-4"
            ),
            
            # Actions
            Div(
                H3("Assignment Actions", cls="text-lg font-semibold text-indigo-800 mb-3"),
                Div(
                    A("Edit Assignment", href=f"/instructor/assignments/{assignment_id}/edit", 
                      cls="bg-amber-600 text-white px-4 py-2 rounded-lg hover:bg-amber-700 mr-4"),
                    A("Manage Rubric", href=f"/instructor/assignments/{assignment_id}/rubric", 
                      cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4"),
                    A("Review Feedback", href=f"/instructor/assignments/{assignment_id}/feedback", 
                      cls="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 mr-4"),
                    A("View Submissions", href=f"/instructor/assignments/{assignment_id}/submissions", 
                      cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                    cls="flex"
                ),
                cls="mb-6 bg-white rounded-xl shadow-md border border-gray-100 p-4"
            ),
            
            # Status change
            Div(
                H3("Change Assignment Status", cls="text-lg font-semibold text-indigo-800 mb-3"),
                Form(
                    P("Changing the assignment status affects student access and submission ability.", 
                      cls="text-gray-600 mb-3"),
                    Div(
                        Select(
                            Option("Draft - Only visible to you", value="draft", 
                                  selected=getattr(assignment, 'status', 'draft') == 'draft'),
                            Option("Active - Available to students", value="active",
                                  selected=getattr(assignment, 'status', 'draft') == 'active'),
                            Option("Closed - No new submissions", value="closed",
                                  selected=getattr(assignment, 'status', 'draft') == 'closed'),
                            Option("Archived - Hidden from students", value="archived",
                                  selected=getattr(assignment, 'status', 'draft') == 'archived'),
                            name="status",
                            cls="p-3 border border-gray-300 rounded-lg mr-3"
                        ),
                        Button("Update Status", type="submit",
                              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                        cls="flex items-center"
                    ),
                    Div(id="status-result", cls="mt-3"),
                    hx_post=f"/instructor/assignments/{assignment_id}/status",
                    hx_target="#status-result",
                    cls=""
                ),
                cls="bg-white rounded-xl shadow-md border border-gray-100 p-4"
            ),
            
            cls=""
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Assignment Navigation", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Course", color="gray", 
                              href=f"/instructor/courses/{assignment.course_id}/assignments", icon="←"),
                action_button("Edit Assignment", color="amber", 
                              href=f"/instructor/assignments/{assignment_id}/edit", icon="✏️"),
                action_button("Manage Rubric", color="teal", 
                              href=f"/instructor/assignments/{assignment_id}/rubric", icon="📊"),
                action_button("Review Feedback", color="purple", 
                              href=f"/instructor/assignments/{assignment_id}/feedback", icon="👁"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Details", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Course: {course.title}", cls="text-gray-700 font-medium mb-2"),
            P(f"Code: {course.code}", cls="text-gray-600 mb-2"),
            P(f"Status: {getattr(course, 'status', 'active').capitalize()}", cls="text-gray-600 mb-2"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Student Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Submissions: {submission_count}", cls="text-gray-700 font-medium mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return the complete page
    return dashboard_layout(
        f"{assignment.title} | {course.title} | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/assignments/{assignment_id}/status')
@instructor_required
def post(session, assignment_id: int, status: str):
    """Update assignment status"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Validate status
    if status not in ['draft', 'active', 'closed', 'archived', 'deleted']:
        return "Invalid status. Please select a valid status."
    
    # Check course status - don't allow active assignments for closed/archived/deleted courses
    course, course_error = get_instructor_course(assignment.course_id, user.email)
    
    if course_error:
        return f"Error: {course_error}"
    
    if status == 'active' and hasattr(course, 'status') and course.status in ['closed', 'archived', 'deleted']:
        return f"Cannot set assignment to 'active' when the course is '{course.status}'."
    
    # Update timestamp
    from datetime import datetime
    now = datetime.now().isoformat()
    
    # Update assignment status
    from app.models.assignment import Assignment, assignments
    
    old_status = assignment.status if hasattr(assignment, 'status') else 'draft'
    assignment.status = status
    assignment.updated_at = now
    
    # Save to database
    assignments.update(assignment)
    
    # Return success message with auto-refresh
    return Div(
        P(f"Assignment status updated from '{old_status}' to '{status}'.", cls="text-green-600"),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-3 rounded-lg"
    )

@rt('/instructor/assignments/{assignment_id}/edit')
@instructor_required
def get(session, assignment_id: int):
    """Form to edit an existing assignment"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Get the course
    course, course_error = get_instructor_course(assignment.course_id, user.email)
    
    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Form to edit the assignment
    form_content = Div(
        H2(f"Edit Assignment", cls="text-2xl font-bold text-indigo-900 mb-6"),
        P(f"Update the details for your assignment in {course.title}.", cls="text-gray-600 mb-6"),
        
        Form(
            # Title field
            Div(
                Label("Assignment Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                Input(id="title", name="title", type="text", value=assignment.title,
                      required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                cls="mb-4"
            ),
            
            # Description field
            Div(
                Label("Assignment Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                Textarea(id="description", name="description", rows="6", 
                         value=getattr(assignment, 'description', ''),
                         cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                cls="mb-4"
            ),
            
            # Due date and max drafts
            Div(
                Div(
                    Label("Due Date (Optional)", for_="due_date", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="due_date", name="due_date", type="date", 
                          value=getattr(assignment, 'due_date', ''),
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="w-1/2 pr-2"
                ),
                Div(
                    Label("Maximum Drafts", for_="max_drafts", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="max_drafts", name="max_drafts", type="number", min="1",
                          value=getattr(assignment, 'max_drafts', 3) or 3,
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="w-1/2 pl-2"
                ),
                cls="flex mb-4"
            ),
            
            # Status selection
            Div(
                Label("Assignment Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                Select(
                    Option("Draft - Only visible to you", value="draft", 
                          selected=getattr(assignment, 'status', 'draft') == 'draft'),
                    Option("Active - Available to students", value="active",
                          selected=getattr(assignment, 'status', 'draft') == 'active'),
                    Option("Closed - No new submissions", value="closed",
                          selected=getattr(assignment, 'status', 'draft') == 'closed'),
                    Option("Archived - Hidden from students", value="archived",
                          selected=getattr(assignment, 'status', 'draft') == 'archived'),
                    id="status", name="status",
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                ),
                cls="mb-6"
            ),
            
            # Submit button
            Div(
                Button("Update Assignment", type="submit", 
                       cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="mb-4"
            ),
            
            # Result placeholder
            Div(id="result"),
            
            # Form submission details
            hx_post=f"/instructor/assignments/{assignment_id}/edit",
            hx_target="#result",
            
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Assignment Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Assignment", color="gray", 
                              href=f"/instructor/assignments/{assignment_id}", icon="←"),
                action_button("Course Assignments", color="indigo", 
                              href=f"/instructor/courses/{assignment.course_id}/assignments", icon="📚"),
                action_button("Manage Rubric", color="teal", 
                              href=f"/instructor/assignments/{assignment_id}/rubric", icon="📊"),
                action_button("View Submissions", color="amber", 
                              href=f"/instructor/assignments/{assignment_id}/submissions", icon="📝"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Editing Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Clear instructions help students understand expectations", cls="text-gray-600 mb-2 text-sm"),
            P("• Set realistic draft limits for meaningful feedback", cls="text-gray-600 mb-2 text-sm"),
            P("• Consider creating a rubric for structured feedback", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return the complete page
    return dashboard_layout(
        f"Edit Assignment | {course.title} | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/assignments/{assignment_id}/edit')
@instructor_required
def post(session, assignment_id: int, title: str, description: str, due_date: str = "", 
        max_drafts: int = 3, status: str = "draft"):
    """Handle assignment update"""
    # Get current user
    user = users[session['auth']]
    
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
    if status not in ['draft', 'active', 'closed', 'archived', 'deleted']:
        status = 'draft'  # Default to draft if invalid
    
    # Check course status - don't allow active assignments for closed/archived/deleted courses
    if status == 'active' and hasattr(course, 'status') and course.status in ['closed', 'archived', 'deleted']:
        return f"Cannot set assignment to 'active' when the course is '{course.status}'."
    
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
                    H3("Assignment Updated Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your assignment \"{title}\" has been updated.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Back to Assignment", href=f"/instructor/assignments/{assignment_id}", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Manage Rubric", href=f"/instructor/assignments/{assignment_id}/rubric", 
                  cls="bg-teal-600 text-white px-4 py-2 rounded-lg hover:bg-teal-700 mr-4"),
                A("View Submissions", href=f"/instructor/assignments/{assignment_id}/submissions", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )
    
# --- Rubric Management ---
@rt('/instructor/assignments/{assignment_id}/rubric')
@instructor_required
def get(session, assignment_id: int):
    """View and manage rubric for an assignment"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Get the course this assignment belongs to
    course, course_error = get_instructor_course(assignment.course_id, user.email)
    
    if course_error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(course_error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Import rubric models
    from app.models.assignment import Rubric, RubricCategory, rubrics, rubric_categories
    
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
            H2(f"Manage Rubric for: {assignment.title}", cls="text-2xl font-bold text-indigo-900 mb-4"),
            P("Edit the rubric categories and their weights. The weights should sum to 100%.", 
              cls="text-gray-600 mb-6"),
            
            # Existing categories display and edit form
            Div(
                # Header section with assignment info
                Div(
                    P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    P(f"Status: {getattr(assignment, 'status', 'draft').capitalize()}", cls="text-gray-600"),
                    cls="mb-4"
                ),
                
                # Current categories
                H3("Current Rubric Categories", cls="text-xl font-semibold text-indigo-800 mb-3"),
                
                # Category display and edit section
                (Div(
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    Th("Category Name", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                    Th("Description", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                    Th("Weight (%)", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                    Th("Actions", cls="text-left py-3 px-4 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                                ),
                                cls="bg-indigo-50"
                            ),
                            Tbody(
                                *[Tr(
                                    Td(category.name, cls="py-3 px-4 border-b border-gray-100"),
                                    Td(
                                        Div(
                                            P(category.description, cls="text-gray-700 max-w-md"),
                                            cls="max-h-24 overflow-y-auto"
                                        ),
                                        cls="py-3 px-4 border-b border-gray-100"
                                    ),
                                    Td(f"{category.weight}%", cls="py-3 px-4 border-b border-gray-100"),
                                    Td(
                                        Div(
                                            Button("Edit", 
                                                  hx_get=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/edit",
                                                  hx_target="#category-edit-form",
                                                  cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2"),
                                            Button("Delete", 
                                                  hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/{category.id}/delete",
                                                  hx_confirm=f"Are you sure you want to delete the category '{category.name}'?",
                                                  hx_target="#rubric-result",
                                                  cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"),
                                            cls="flex"
                                        ),
                                        cls="py-3 px-4 border-b border-gray-100"
                                    ),
                                    # Add unique id to each row for potential HTMX interactions
                                    id=f"category-row-{category.id}",
                                    cls="hover:bg-gray-50"
                                ) for category in categories]
                            ),
                            cls="w-full"
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100 mb-6"
                    ) if categories else
                    P("No rubric categories have been created yet. Use the form below to add categories to your rubric.", 
                      cls="bg-amber-50 p-4 rounded-lg border border-amber-200 text-amber-800 mb-6")
                )),
                
                # Add new category section
                Div(
                    H3("Add New Category", cls="text-xl font-semibold text-indigo-800 mb-3"),
                    Div(id="category-edit-form", cls="mb-4"),
                    Form(
                        Input(type="hidden", name="category_id", value=""),
                        Div(
                            Label("Category Name", for_="name", cls="block text-indigo-900 font-medium mb-1"),
                            Input(id="name", name="name", type="text", placeholder="e.g. Content", 
                                  required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                            Textarea(id="description", name="description", rows="3", placeholder="Describe what this category evaluates...",
                                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Label("Weight (%)", for_="weight", cls="block text-indigo-900 font-medium mb-1"),
                            Input(id="weight", name="weight", type="number", min="1", max="100", step="0.1", placeholder="e.g. 25",
                                  required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                            cls="mb-4"
                        ),
                        Div(
                            Button("Add Category", type="submit", 
                                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                            cls="mb-4"
                        ),
                        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/add",
                        hx_target="#rubric-result",
                        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6"
                    ),
                ),
                
                # Result placeholder for form submissions
                Div(id="rubric-result", cls="mb-6"),
                
                # Action buttons
                Div(
                    A("Back to Assignment", href=f"/instructor/assignments/{assignment_id}", 
                      cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4"),
                    cls="flex"
                ),
                
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
            ),
            cls=""
        )
    else:
        # No rubric exists - show creation form
        form_content = Div(
            H2(f"Create Rubric for: {assignment.title}", cls="text-2xl font-bold text-indigo-900 mb-4"),
            P("A rubric helps provide structured feedback for students. Create a rubric by defining categories and their weights.", 
              cls="text-gray-600 mb-6"),
            
            # Rubric creation form
            Div(
                # Header section with assignment info
                Div(
                    P(f"Assignment: {assignment.title}", cls="text-gray-600"),
                    P(f"Status: {getattr(assignment, 'status', 'draft').capitalize()}", cls="text-gray-600"),
                    cls="mb-6"
                ),
                
                # Initialize rubric form
                Form(
                    H3("Initialize Rubric", cls="text-xl font-semibold text-indigo-800 mb-3"),
                    P("Create a rubric for this assignment to define evaluation criteria.", cls="text-gray-600 mb-4"),
                    
                    Div(
                        Button("Create Rubric", type="submit", 
                              cls="bg-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm"),
                        cls="mb-4"
                    ),
                    
                    Div(id="create-rubric-result", cls="mt-4"),
                    
                    hx_post=f"/instructor/assignments/{assignment_id}/rubric/create",
                    hx_target="#create-rubric-result",
                    
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6"
                ),
                
                # Action buttons
                Div(
                    A("Back to Assignment", href=f"/instructor/assignments/{assignment_id}", 
                      cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-4"),
                    cls="flex"
                ),
                
                cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
            ),
            cls=""
        )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Rubric Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Assignment", color="gray", 
                              href=f"/instructor/assignments/{assignment_id}", icon="←"),
                action_button("Assignment List", color="indigo", 
                              href=f"/instructor/courses/{assignment.course_id}/assignments", icon="📚"),
                action_button("Edit Assignment", color="amber", 
                              href=f"/instructor/assignments/{assignment_id}/edit", icon="✏️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Rubric Tips", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P("• Create 3-5 categories for a balanced rubric", cls="text-gray-600 mb-2 text-sm"),
            P("• Ensure weights add up to 100%", cls="text-gray-600 mb-2 text-sm"),
            P("• Use clear descriptions that guide students", cls="text-gray-600 mb-2 text-sm"),
            P("• Consider including examples in descriptions", cls="text-gray-600 text-sm"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Template Library", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                Button("Essay Rubric Template", 
                      hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/essay",
                      hx_target="#rubric-result",
                      cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left"),
                Button("Research Paper Template", 
                      hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/research",
                      hx_target="#rubric-result",
                      cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mb-2 w-full text-left"),
                Button("Presentation Template", 
                      hx_get=f"/instructor/assignments/{assignment_id}/rubric/template/presentation",
                      hx_target="#rubric-result",
                      cls="text-sm px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 w-full text-left"),
                cls="space-y-2"
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        cls="space-y-6"
    )
    
    # Return complete page
    return dashboard_layout(
        f"Rubric for {assignment.title} | {course.title} | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/assignments/{assignment_id}/rubric/create')
@instructor_required
def post(session, assignment_id: int):
    """Create a new rubric for an assignment"""
    # Get current user
    user = users[session['auth']]
    
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
                cls="bg-amber-50 p-4 rounded-lg"
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
    new_rubric = Rubric(
        id=next_rubric_id,
        assignment_id=assignment_id
    )
    
    # Insert into database
    rubrics.insert(new_rubric)
    
    # Return success message with page refresh
    return Div(
        P("Rubric created successfully! You can now add categories.", cls="text-green-600 font-medium"),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-4 rounded-lg"
    )

@rt('/instructor/assignments/{assignment_id}/rubric/categories/add')
@instructor_required
def post(session, assignment_id: int, name: str, description: str = "", weight: float = 0, category_id: int = None):
    """Add a new category to a rubric or update an existing one"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Import rubric models
    from app.models.assignment import Rubric, RubricCategory, rubrics, rubric_categories
    
    # Find the rubric for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break
    
    if not rubric:
        return Div(
            P("Error: No rubric found for this assignment. Please create a rubric first.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )
    
    # Validate inputs
    if not name:
        return Div(
            P("Error: Category name is required.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )
    
    try:
        weight = float(weight)
        if weight <= 0 or weight > 100:
            return Div(
                P("Error: Weight must be between 0 and 100.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg"
            )
    except:
        return Div(
            P("Error: Invalid weight value.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
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
                    Script("setTimeout(function() { window.location.reload(); }, 1000);"),
                    cls="bg-green-50 p-4 rounded-lg"
                )
        
        return Div(
            P("Error: Category not found or doesn't belong to this rubric.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
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
        weight=weight
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
        cls="bg-green-50 p-4 rounded-lg"
    )

@rt('/instructor/assignments/{assignment_id}/rubric/categories/{category_id}/edit')
@instructor_required
def get(session, assignment_id: int, category_id: int):
    """Get the form for editing a rubric category"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Import rubric models
    from app.models.assignment import RubricCategory, rubric_categories
    
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
            Label("Category Name", for_="name", cls="block text-indigo-900 font-medium mb-1"),
            Input(id="name", name="name", type="text", value=category.name,
                  required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
            cls="mb-4"
        ),
        Div(
            Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
            Textarea(id="description", name="description", rows="3", value=category.description,
                    cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
            cls="mb-4"
        ),
        Div(
            Label("Weight (%)", for_="weight", cls="block text-indigo-900 font-medium mb-1"),
            Input(id="weight", name="weight", type="number", min="1", max="100", step="0.1", value=str(category.weight),
                  required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
            cls="mb-4"
        ),
        Div(
            Button("Update Category", type="submit", 
                  cls="bg-amber-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-amber-700 transition-colors shadow-sm"),
            Button("Cancel", 
                  hx_get=f"/instructor/assignments/{assignment_id}/rubric/categories/cancel",
                  hx_target="#category-edit-form",
                  cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors shadow-sm ml-3"),
            cls="mb-4"
        ),
        hx_post=f"/instructor/assignments/{assignment_id}/rubric/categories/add",
        hx_target="#rubric-result",
        cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6"
    )

@rt('/instructor/assignments/{assignment_id}/rubric/categories/cancel')
@instructor_required
def get(session, assignment_id: int):
    """Cancel category editing"""
    return ""

@rt('/instructor/assignments/{assignment_id}/rubric/categories/{category_id}/delete')
@instructor_required
def post(session, assignment_id: int, category_id: int):
    """Delete a rubric category"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Import rubric models
    from app.models.assignment import RubricCategory, rubric_categories
    
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
        cls="bg-green-50 p-4 rounded-lg"
    )

@rt('/instructor/assignments/{assignment_id}/rubric/template/{template_type}')
@instructor_required
def get(session, assignment_id: int, template_type: str):
    """Apply a rubric template"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return f"Error: {error}"
    
    # Import rubric models
    from app.models.assignment import Rubric, RubricCategory, rubrics, rubric_categories
    
    # Find the rubric for this assignment
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment_id:
            rubric = r
            break
    
    if not rubric:
        return Div(
            P("Error: No rubric found for this assignment. Please create a rubric first.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )
    
    # Check if rubric already has categories
    existing_categories = []
    for c in rubric_categories():
        if c.rubric_id == rubric.id:
            existing_categories.append(c)
    
    if existing_categories:
        return Div(
            P("This rubric already has categories. Templates can only be applied to empty rubrics.", cls="text-amber-600"),
            cls="bg-amber-50 p-4 rounded-lg"
        )
    
    # Define template categories based on type
    template_categories = []
    if template_type == "essay":
        template_categories = [
            {"name": "Content", "description": "The essay addresses the assigned topic thoroughly and presents a clear thesis statement. Arguments are well-developed with relevant evidence and examples.", "weight": 30},
            {"name": "Organization", "description": "The essay follows a logical structure with clear introduction, body paragraphs, and conclusion. Ideas flow smoothly with effective transitions.", "weight": 25},
            {"name": "Analysis", "description": "The essay demonstrates critical thinking and insightful analysis. Arguments are thoughtful and demonstrate understanding of the topic's complexity.", "weight": 20},
            {"name": "Style & Language", "description": "Writing is clear, concise, and appropriate for academic context. Grammar, punctuation, and spelling are correct. Vocabulary is varied and precise.", "weight": 15},
            {"name": "Citations & References", "description": "Sources are properly cited using the required citation style. References are relevant, credible, and integrated effectively.", "weight": 10}
        ]
    elif template_type == "research":
        template_categories = [
            {"name": "Research Question", "description": "Clear, focused research question or hypothesis. Demonstrates significance and originality within the field.", "weight": 15},
            {"name": "Literature Review", "description": "Comprehensive review of relevant literature. Synthesizes prior research and identifies gaps.", "weight": 20},
            {"name": "Methodology", "description": "Research design and methods are appropriate, clearly described, and aligned with research questions.", "weight": 20},
            {"name": "Data Analysis & Results", "description": "Data is accurately analyzed using appropriate methods. Results are presented clearly with relevant tables/figures.", "weight": 25},
            {"name": "Discussion & Conclusion", "description": "Interpretation of results is insightful and connected to the literature. Limitations are acknowledged and future research directions suggested.", "weight": 15},
            {"name": "Citations & Format", "description": "Follows required citation style and formatting guidelines. References are accurate and complete.", "weight": 5}
        ]
    elif template_type == "presentation":
        template_categories = [
            {"name": "Content", "description": "Presentation covers topic thoroughly with accurate, relevant information. Key points are supported with evidence.", "weight": 30},
            {"name": "Organization", "description": "Clear structure with logical flow. Includes effective introduction, well-organized body, and strong conclusion.", "weight": 20},
            {"name": "Visual Elements", "description": "Slides are clear, readable, and visually appealing. Graphics enhance understanding without overwhelming.", "weight": 15},
            {"name": "Delivery", "description": "Speaker demonstrates confidence, maintains good pace, and uses appropriate voice projection. Engages audience and maintains eye contact.", "weight": 25},
            {"name": "Q&A Handling", "description": "Responds to questions clearly and accurately. Demonstrates depth of knowledge on the topic.", "weight": 10}
        ]
    else:
        return Div(
            P(f"Unknown template type: {template_type}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
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
            weight=template["weight"]
        )
        rubric_categories.insert(new_category)
        next_category_id += 1
    
    # Return success message with page refresh
    template_names = {
        "essay": "Essay",
        "research": "Research Paper",
        "presentation": "Presentation"
    }
    
    return Div(
        P(f"{template_names.get(template_type, template_type.title())} template applied successfully!", cls="text-green-600"),
        Script("setTimeout(function() { window.location.reload(); }, 1000);"),
        cls="bg-green-50 p-4 rounded-lg"
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
        if hasattr(target_course, 'status') and target_course.status == "deleted":
            return None, "This course has been deleted."
            
        return target_course, None
    except Exception as e:
        return None, f"Error accessing course: {str(e)}"
@rt('/instructor/courses')
@instructor_required
def get(session, request):
    """Course listing page for instructors"""
    # Get current user
    user = users[session['auth']]
    
    # Get all courses taught by this instructor
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            # Skip deleted courses
            if hasattr(course, 'status') and course.status == "deleted":
                continue
                
            # Get student count for this course
            student_count = 0
            for enrollment in enrollments():
                if enrollment.course_id == course.id:
                    student_count += 1
            
            # Add to list with student count
            instructor_courses.append((course, student_count))
    
    # Sort courses by creation date (newest first)
    instructor_courses.sort(key=lambda x: x[0].created_at if hasattr(x[0], 'created_at') else "", reverse=True)
    
    # Create the main content
    main_content = Div(
        # Header with action button
        Div(
            H2("Course Management", cls="text-2xl font-bold text-indigo-900"),
            action_button("Create New Course", color="indigo", href="/instructor/courses/new", icon="+"),
            cls="flex justify-between items-center mb-6"
        ),
        
        # Course listing or empty state
        (Div(
            P(f"You have {len(instructor_courses)} {'course' if len(instructor_courses) == 1 else 'courses'}.", 
              cls="text-gray-600 mb-6"),
            
            # Course table with actions
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Course Title", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Code", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Term", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Status", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Students", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                        ),
                        cls="bg-indigo-50"
                    ),
                    Tbody(
                        *(Tr(
                            # Course title
                            Td(course.title, cls="py-4 px-6"),
                            # Course code
                            Td(course.code, cls="py-4 px-6"),
                            # Term
                            Td(getattr(course, 'term', 'Current') or 'Current', cls="py-4 px-6"),
                            # Status badge
                            Td(
                                status_badge(
                                    getattr(course, 'status', 'active').capitalize() or 'Active',
                                    "green" if getattr(course, 'status', 'active') == 'active' else
                                    "yellow" if getattr(course, 'status', 'active') == 'closed' else
                                    "gray"
                                ),
                                cls="py-4 px-6"
                            ),
                            # Student count
                            Td(str(student_count), cls="py-4 px-6"),
                            # Action buttons
                            Td(
                                Div(
                                    A("Students", 
                                      href=f"/instructor/courses/{course.id}/students",
                                      cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2"),
                                    A("Edit", 
                                      href=f"/instructor/courses/{course.id}/edit",
                                      cls="text-xs px-3 py-1 bg-amber-600 text-white rounded-md hover:bg-amber-700 mr-2"),
                                    A("Assignments", 
                                      href=f"/instructor/courses/{course.id}/assignments",
                                      cls="text-xs px-3 py-1 bg-teal-600 text-white rounded-md hover:bg-teal-700"),
                                    cls="flex"
                                ),
                                cls="py-4 px-6"
                            )
                        ) for course, student_count in instructor_courses)
                    ),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ),
            cls=""
        ) if instructor_courses else
        Div(
            P("You don't have any courses yet. Create your first course to get started.", 
              cls="text-center text-gray-600 mb-6"),
            Div(
                A("Create New Course", href="/instructor/courses/new", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="text-center"
            ),
            cls="py-8 bg-white rounded-lg shadow-md border border-gray-100 mt-4"
        ))
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Create Course", color="indigo", href="/instructor/courses/new", icon="+"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Statistics", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total Courses: {len(instructor_courses)}", cls="text-gray-600 mb-2"),
            P(f"Active Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'active')}", 
              cls="text-green-600 mb-2"),
            P(f"Closed Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'closed')}", 
              cls="text-amber-600 mb-2"),
            P(f"Archived Courses: {sum(1 for c, _ in instructor_courses if getattr(c, 'status', 'active') == 'archived')}", 
              cls="text-gray-600 mb-2"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Courses | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path
    )

@rt('/instructor/courses/new')
@instructor_required
def get(session):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
    # Create the form content
    form_content = Div(
        H2("Create New Course", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Complete the form below to create a new course for your students.", 
              cls="mb-6 text-gray-600"),
            Form(
                Div(
                    Label("Course Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="title", name="title", type="text", placeholder="e.g. Introduction to Computer Science",
                          required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                Div(
                    Label("Course Code", for_="code", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="code", name="code", type="text", placeholder="e.g. CS101",
                          required=True, cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                # Add new fields for term, department, and status
                Div(
                    Div(
                        Label("Term", for_="term", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="term", name="term", type="text", placeholder="e.g. Fall 2023",
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pr-2"
                    ),
                    Div(
                        Label("Department", for_="department", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="department", name="department", type="text", placeholder="e.g. Computer Science",
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pl-2"
                    ),
                    cls="flex mb-4"
                ),
                Div(
                    Label("Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                    Select(
                        Option("Active", value="active", selected=True),
                        Option("Closed", value="closed"),
                        Option("Archived", value="archived"),
                        id="status", name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                    Textarea(id="description", name="description", placeholder="Provide a brief description of the course",
                            rows="4", cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-6"
                ),
                Div(
                    Button("Create Course", type="submit", cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="mb-4"
                ),
                Div(id="result", cls=""),
                hx_post="/instructor/courses/new",
                hx_target="#result",
                cls="w-full"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Manage Courses", color="indigo", href="/instructor/courses", icon="📚"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Choose a clear, descriptive course title", cls="text-gray-600 mb-2 text-sm"),
            P("• Use official course codes when possible", cls="text-gray-600 mb-2 text-sm"),
            P("• Include key information in the description", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Create Course | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/new')
@instructor_required
def post(session, title: str, code: str, term: str = "", department: str = "", status: str = "active", description: str = ""):
    # Get current user
    user = users[session['auth']]
    
    # Validate input
    if not title or not code:
        return "Course title and code are required."
    
    # Check for duplicate course code
    for course in courses():
        if course.code == code and course.instructor_email == user.email:
            # Only check for duplicates from the same instructor
            # If the course is deleted, allow reuse of code
            if not hasattr(course, 'status') or course.status != "deleted":
                return "You already have a course with this code. Please use a different code."
    
    # Validate status
    if status not in ['active', 'closed', 'archived']:
        status = 'active'  # Default to active if invalid
    
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
        updated_at=now
    )
    
    # Insert into database
    courses.insert(new_course)
    
    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Course Created Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your course \"{title}\" has been created.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Return to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Manage Courses", href="/instructor/courses", 
                  cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-4 hover:bg-amber-700"),
                A("Invite Students", href=f"/instructor/invite-students?course_id={next_course_id}", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )

# --- Edit Course Route ---
@rt('/instructor/courses/{course_id}/edit')
@instructor_required
def get(session, course_id: int):
    # Get current user
    user = users[session['auth']]
    
    # Get the course with permission check
    course, error = get_instructor_course(course_id, user.email)
    
    if error:
        return Div(
            H2("Error", cls="text-2xl font-bold text-red-700 mb-4"),
            P(error, cls="text-gray-700 mb-4"),
            A("Back to Courses", href="/instructor/courses", 
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
            cls="p-8 bg-red-50 rounded-xl shadow-md border-2 border-red-200 text-center"
        )
    
    # Create the form content
    form_content = Div(
        H2(f"Edit Course: {course.title}", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Update your course details below.", 
              cls="mb-6 text-gray-600"),
            Form(
                Div(
                    Label("Course Title", for_="title", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="title", name="title", type="text", placeholder="e.g. Introduction to Computer Science",
                          value=course.title, required=True, 
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                Div(
                    Label("Course Code", for_="code", cls="block text-indigo-900 font-medium mb-1"),
                    Input(id="code", name="code", type="text", placeholder="e.g. CS101",
                          value=course.code, required=True, 
                          cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-4"
                ),
                # Term and department fields
                Div(
                    Div(
                        Label("Term", for_="term", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="term", name="term", type="text", placeholder="e.g. Fall 2023",
                              value=getattr(course, 'term', ''),
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pr-2"
                    ),
                    Div(
                        Label("Department", for_="department", cls="block text-indigo-900 font-medium mb-1"),
                        Input(id="department", name="department", type="text", placeholder="e.g. Computer Science",
                              value=getattr(course, 'department', ''),
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="w-1/2 pl-2"
                    ),
                    cls="flex mb-4"
                ),
                # Status field
                Div(
                    Label("Status", for_="status", cls="block text-indigo-900 font-medium mb-1"),
                    Select(
                        Option("Active", value="active", selected=getattr(course, 'status', 'active') == 'active'),
                        Option("Closed", value="closed", selected=getattr(course, 'status', 'active') == 'closed'),
                        Option("Archived", value="archived", selected=getattr(course, 'status', 'active') == 'archived'),
                        id="status", name="status",
                        cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                Div(
                    Label("Description", for_="description", cls="block text-indigo-900 font-medium mb-1"),
                    Textarea(id="description", name="description", placeholder="Provide a brief description of the course",
                            value=getattr(course, 'description', ''), rows="4", 
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                    cls="mb-6"
                ),
                Div(
                    Button("Update Course", type="submit", cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                    cls="mb-4"
                ),
                Div(id="result", cls=""),
                hx_post=f"/instructor/courses/{course_id}/edit",
                hx_target="#result",
                cls="w-full"
            ),
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100"
        ),
        cls=""
    )
    
    # Sidebar content with course actions
    sidebar_content = Div(
        Div(
            H3("Course Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Courses", color="gray", href="/instructor/courses", icon="←"),
                action_button("View Students", color="indigo", href=f"/instructor/courses/{course_id}/students", icon="👨‍👩‍👧‍👦"),
                action_button("Assignments", color="teal", href=f"/instructor/courses/{course_id}/assignments", icon="📝"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Current Status: {getattr(course, 'status', 'active').capitalize()}", 
              cls="font-medium " + 
              ("text-green-600" if getattr(course, 'status', 'active') == 'active' else 
               "text-amber-600" if getattr(course, 'status', 'active') == 'closed' else 
               "text-gray-600")),
            P("Active: Students can be invited and can access course materials", cls="text-gray-600 text-sm mt-4 mb-1"),
            P("Closed: No new enrollments, but existing students can access", cls="text-gray-600 text-sm mb-1"),
            P("Archived: Hidden from all users but preserves data", cls="text-gray-600 text-sm mb-1"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Edit Course: {course.title} | FeedForward", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/courses/{course_id}/edit')
@instructor_required
def post(session, course_id: int, title: str, code: str, term: str = "", department: str = "", 
         status: str = "active", description: str = ""):
    # Get current user
    user = users[session['auth']]
    
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
            if not hasattr(c, 'status') or c.status != "deleted":
                return "You already have another course with this code. Please use a different code."
    
    # Validate status
    if status not in ['active', 'closed', 'archived']:
        status = 'active'  # Default to active if invalid
    
    # Create timestamp
    now = datetime.now().isoformat()
    
    # Update course fields
    course.title = title
    course.code = code
    course.term = term
    course.department = department
    course.status = status
    course.description = description if hasattr(course, 'description') else None
    course.updated_at = now
    
    # Update the course in the database
    courses.update(course)
    
    # Return success message
    return Div(
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Course Updated Successfully!", cls="text-xl font-bold text-green-700 mb-1"),
                    P(f"Your course \"{title}\" has been updated.", cls="text-gray-600"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            Div(
                A("Back to Courses", href="/instructor/courses", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg mr-4 hover:bg-gray-200"),
                A("Manage Students", href=f"/instructor/courses/{course_id}/students", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="flex justify-center gap-4"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-6 rounded-lg border border-green-200 mt-4"
    )

@rt('/instructor/manage-students')
@instructor_required
def get(session, request):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
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
                    
                    students.append({
                        "email": student.email,
                        "name": student.name if student.name else "(Not registered)",
                        "status": status,
                        "verified": student.verified
                    })
                except NotFoundError:
                    # Student record might be missing
                    students.append({
                        "email": enrollment.student_email,
                        "name": "(Not registered)",
                        "status": "Invited",
                        "verified": False
                    })
        
        if students:
            courses_with_students.append({
                "course": course,
                "students": students
            })
    
    # Create the main content
    if courses_with_students:
        # Create tables for each course with students
        course_tables = []
        
        for course_data in courses_with_students:
            course = course_data["course"]
            students = course_data["students"]
            
            # Sort students: enrolled first, then invited
            sorted_students = sorted(students, key=lambda s: (0 if s["verified"] else 1, s["email"]))
            
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
                            Button("Resend", 
                               hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                               hx_target=f"#status-{course.id}-{idx}",
                               cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2") if not student["verified"] else "",
                            Button("Remove", 
                               hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course.id}",
                               hx_target="#message-area",
                               hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                               cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"),
                            cls="flex",
                            id=f"status-{course.id}-{idx}"
                        ),
                        cls="py-4 px-6"
                    ),
                    id=f"row-{course.id}-{idx}",
                    cls="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                )
                student_rows.append(row)
            
            # Create the course card with student table
            course_tables.append(
                Div(
                    H3(f"{course.title} ({course.code})", cls="text-xl font-bold text-indigo-900 mb-4"),
                    Div(
                        Table(
                            Thead(
                                Tr(
                                    *[Th(h, cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100") for h in ["#", "Email", "Name", "Status", "Actions"]],
                                    cls="bg-indigo-50"
                                )
                            ),
                            Tbody(*student_rows),
                            cls="w-full"
                        ),
                        cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
                    ),
                    Div(
                        action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course.id}", icon="+"),
                        cls="mt-4"
                    ),
                    cls="mb-8"
                )
            )
        
        # Main content with all course tables
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            *course_tables,
            cls=""
        )
    else:
        # Show a message if no students enrolled in any courses
        main_content = Div(
            H2("Manage Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P("You don't have any students enrolled in your courses yet.", 
                      cls="text-center text-gray-600 mb-6"),
                    Div(
                        A("Invite Students", href="/instructor/invite-students", 
                          cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="py-8"
                )
            ),
            cls=""
        )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Student Management", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite Students", color="indigo", href="/instructor/invite-students", icon="+"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Resend invitations if students haven't registered", cls="text-gray-600 mb-2 text-sm"),
            P("• Remove students who are no longer in your course", cls="text-gray-600 mb-2 text-sm"),
            P("• Students must verify their email to access the course", cls="text-gray-600 text-sm"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Manage Students | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path
    )

@rt('/instructor/courses/{course_id}/students')
@instructor_required
def get(session, course_id: int):
    # Get components directly from top-level imports
    
    # Get current user
    user = users[session['auth']]
    
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
                
                course_students.append({
                    "email": student.email,
                    "name": student.name if student.name else "(Not registered)",
                    "status": status,
                    "verified": student.verified
                })
            except:
                # Student record might be missing
                course_students.append({
                    "email": enrollment.student_email,
                    "name": "(Not registered)",
                    "status": "Invited",
                    "verified": False
                })
    
    # Sort students: enrolled first, then invited
    sorted_students = sorted(course_students, key=lambda s: (0 if s["verified"] else 1, s["email"]))
    
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
                        Button("Resend", 
                          hx_post=f"/instructor/resend-invitation?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                          hx_target=f"#status-{idx}",
                          cls="text-xs px-3 py-1 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 mr-2") if not student["verified"] else "",
                        Button("Remove", 
                          hx_post=f"/instructor/remove-student?email={urllib.parse.quote(student['email'])}&course_id={course_id}",
                          hx_target="#message-area",
                          hx_confirm=f"Are you sure you want to remove student {student['email']} from this course?",
                          cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"),
                        cls="flex",
                        id=f"status-{idx}"
                    ),
                    cls="py-4 px-6"
                ),
                id=f"row-{idx}",
                cls="border-b border-gray-100 hover:bg-gray-50 transition-colors"
            )
            student_rows.append(row)
        
        # Create the student table
        main_content = Div(
            H2(f"Students in {target_course.title} ({target_course.code})", cls="text-2xl font-bold text-indigo-900 mb-6"),
            # Add message area for delete confirmations
            Div(id="message-area", cls="mb-4"),
            Div(
                Table(
                    Thead(
                        Tr(
                            *[Th(h, cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100") for h in ["#", "Email", "Name", "Status", "Actions"]],
                            cls="bg-indigo-50"
                        )
                    ),
                    Tbody(*student_rows),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            ),
            Div(
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="+"),
                cls="mt-6"
            ),
            cls=""
        )
    else:
        # Show a message if no students enrolled in this course
        main_content = Div(
            H2(f"Students in {target_course.title} ({target_course.code})", cls="text-2xl font-bold text-indigo-900 mb-6"),
            card(
                Div(
                    P("You don't have any students enrolled in this course yet.", 
                      cls="text-center text-gray-600 mb-6"),
                    Div(
                        A("Invite Students", href=f"/instructor/invite-students?course_id={course_id}", 
                          cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="text-center"
                    ),
                    cls="py-8"
                )
            ),
            cls=""
        )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Course Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="✉️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Course Details", cls="font-semibold text-indigo-900 mb-4"),
            P(f"Title: {target_course.title}", cls="text-gray-600 mb-2"),
            P(f"Code: {target_course.code}", cls="text-gray-600 mb-2"),
            P(f"Students: {len(sorted_students)}", cls="text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        f"Students in {target_course.code} | FeedForward", 
        sidebar_content, 
        main_content, 
        user_role=Role.INSTRUCTOR
    )

@rt('/instructor/resend-invitation')
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session['auth']]
    
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
            reset_token_expiry=""
        )
        users.insert(new_student)
    
    # Send invitation email
    success, message = send_student_invitation_email(
        email, user.name, course.title, token
    )
    
    if success:
        return Div(
            P("Invitation sent successfully", cls="text-green-600"),
            Div(cls="mt-1 text-xs text-gray-500")
        )
    else:
        return Div(
            P("Failed to send invitation", cls="text-red-600"),
            Div(message, cls="mt-1 text-xs text-gray-500")
        )

@rt('/instructor/remove-student')
@instructor_required
def post(session, email: str, course_id: int):
    # Get current user
    user = users[session['auth']]
    
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
            P("Course not found or you don't have permission to manage it.", cls="text-red-600 font-medium"),
            cls="p-4 bg-red-50 rounded-lg"
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
                print(f"Deleting enrollment: {e.id}, Course: {e.course_id}, Student: {e.student_email}")
                enrollments.delete(e.id)
                deleted_count += 1
        
        # Check if we deleted anything
        if deleted_count == 0:
            return Div(
                P(f"Student {email} not found in this course.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg"
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
                if student.role == Role.STUDENT and hasattr(student, 'status'):
                    student.status = "inactive"
                    student.last_active = datetime.now().isoformat()
                    users.update(student)
            except:
                # If we can't find the student, that's okay - they might not have registered yet
                pass
        
        # Return success with auto-refresh
        return Div(
            P(f"Student {email} has been removed from the course.", cls="text-green-600"),
            Script("""
                console.log('Student removal successful');
                setTimeout(function() { 
                    console.log('Reloading page...');
                    window.location.href = window.location.href; 
                }, 1500);
            """),
            cls="bg-green-50 p-4 rounded-lg"
        )
    except Exception as e:
        return Div(
            P(f"Error removing student: {str(e)}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )

@rt('/instructor/invite-students')
@instructor_required
def get(session, request, course_id: int = None):
    """Shows the form to invite students to a course"""
    # Get current user
    user = users[session['auth']]
    
    # Get instructor's courses
    instructor_courses = []
    for course in courses():
        if course.instructor_email == user.email:
            instructor_courses.append(course)
    
    # Create invitation form
    form_content = Div(
        H2("Invite Students", cls="text-2xl font-bold text-indigo-900 mb-6"),
        Div(
            P("Invite students to join your course. Students will receive an email with instructions to create their account.", 
              cls="mb-6 text-gray-600"),
            
            # Main content with courses check
            (Div(
                Form(
                    # Course selection
                    Div(
                        Label("Course", for_="course_id", cls="block text-indigo-900 font-medium mb-1"),
                        Select(
                            Option(f"Select a course", value="", selected=True if not course_id else False, disabled=True),
                            *[Option(f"{c.title} ({c.code})", value=str(c.id), selected=(c.id == course_id if course_id else False)) for c in instructor_courses],
                            id="course_id",
                            name="course_id",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        ),
                        cls="mb-4"
                    ),
                    
                    # Student emails textarea
                    Div(
                        Label("Student Emails", for_="student_emails", cls="block text-indigo-900 font-medium mb-1"),
                        P("Enter one email address per line", cls="text-sm text-gray-500 mb-1"),
                        Textarea(
                            id="student_emails",
                            name="student_emails",
                            rows="6",
                            placeholder="student1@example.com\nstudent2@example.com\nstudent3@example.com",
                            cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                        ),
                        cls="mb-4"
                    ),
                    
                    # Submit button
                    Div(
                        Button("Send Invitations", type="submit", 
                              cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="mb-5"
                    ),
                    
                    # Simple file upload section
                    Div(
                        Hr(cls="my-4 border-gray-300"),
                        P("Or upload a file with email addresses:", cls="block text-indigo-900 font-medium mb-2"),
                        P("File should have one email per line or be a CSV with an email column", cls="text-sm text-gray-500 mb-3"),
                        
                        # File input
                        Div(
                            Label("Select File", for_="email_file", cls="block text-indigo-900 font-medium mb-1"),
                            Input(id="email_file", type="file", accept=".csv,.tsv,.txt", 
                                  cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                            cls="mb-3"
                        ),
                        
                        # Button to load file
                        Button("Load Emails from File", id="load-emails", type="button",
                              cls="bg-teal-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm"),
                        
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
                        cls="mb-6"
                    ),
                    
                    # Result placeholder
                    Div(id="invite-result", cls="mt-4"),
                    
                    # Form submission details 
                    id="invite-form",
                    method="post",
                    action="/instructor/invite-students",
                    cls="bg-white p-6 rounded-lg border border-gray-200"
                )
            )) if instructor_courses else 
            # No courses message
            Div(
                P("You don't have any courses yet.", cls="text-red-500 mb-4"),
                P("Please create a course first before inviting students.", cls="text-gray-600 mb-4"),
                A("Create a New Course", href="/instructor/courses/new", 
                  cls="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                cls="text-center py-8 bg-white rounded-lg border border-gray-200"
            ),
            cls="w-full"
        ),
        cls=""
    )
    
    # Sidebar content
    sidebar_content = Div(
        Div(
            H3("Instructor Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                action_button("Create Course", color="indigo", href="/instructor/courses/new", icon="+"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Tips", cls="font-semibold text-indigo-900 mb-4"),
            P("• Students will receive an email with instructions to join", cls="text-gray-600 mb-2 text-sm"),
            P("• They can set up their account after clicking the email link", cls="text-gray-600 mb-2 text-sm"),
            P("• You can upload emails in different formats:", cls="text-gray-600 mb-1 text-sm"),
            P("  - Simple text file with one email per line", cls="text-gray-600 mb-1 text-sm ml-2"),
            P("  - CSV/TSV with headers (we'll find the email column)", cls="text-gray-600 mb-1 text-sm ml-2"),
            P("  - Any format where we can detect email addresses", cls="text-gray-600 text-sm ml-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Use the dashboard layout with our components
    return dashboard_layout(
        "Invite Students", 
        sidebar_content, 
        form_content, 
        user_role=Role.INSTRUCTOR,
        current_path=request.url.path
    )

@rt('/instructor/invite-students')
@instructor_required
def post(session, course_id: str = None, student_emails: str = None):
    """Handle the student invitation form submission"""
    # Debug info
    print(f"Invite students - POST received")
    print(f"Invite students - course_id: {course_id}, student_emails: {student_emails}")
    
    # Convert course_id to integer if provided
    if course_id:
        try:
            course_id = int(course_id)
        except (ValueError, TypeError):
            return Div(
                P("Invalid course ID. Please select a valid course.",
                  cls="text-red-600 font-medium"),
                cls="p-4 bg-red-50 rounded-lg"
            )
    
    # Get current user 
    user = users[session['auth']]
    
    # Get the course
    course = None
    for c in courses():
        if c.id == course_id and c.instructor_email == user.email:
            course = c
            break
    
    if not course:
        return Div(
            P("Course not found or you don't have permission to invite students to this course.",
              cls="text-red-600 font-medium"),
            cls="p-4 bg-red-50 rounded-lg"
        )
    
    # Process student emails
    emails = [email.strip() for email in student_emails.split('\n') if email.strip()]
    
    if not emails:
        return Div(
            P("Please enter at least one student email.",
              cls="text-amber-600 font-medium"),
            cls="p-4 bg-amber-50 rounded-lg"
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
            if hasattr(enrollment, 'student_email') and enrollment.student_email == email and enrollment.course_id == course_id:
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
                reset_token_expiry=""
            )
            users.insert(new_student)
        
        # Create enrollment record
        new_enrollment = Enrollment(
            id=next_id,
            course_id=course_id,
            student_email=email
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
        message_parts.append(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully")
    if already_enrolled_emails:
        message_parts.append(f"{len(already_enrolled_emails)} already enrolled")
    if error_emails:
        message_parts.append(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed")
    
    summary = ", ".join(message_parts)
    
    # Build complete page with confirmation message
    confirmation_content = Div(
        # Success Banner
        Div(
            Div(
                Span("✅", cls="text-5xl mr-5"),
                Div(
                    H2("Student Invitations Sent!", cls="text-2xl font-bold text-green-700 mb-2"),
                    P(summary, cls="text-xl text-gray-700"),
                    cls=""
                ),
                cls="flex items-center"
            ),
            cls="bg-green-50 p-8 rounded-xl shadow-md border-2 border-green-500 mb-6 text-center"
        ),
        
        # Detailed Results
        Div(
            H3("Invitation Results", cls="text-xl font-bold text-indigo-900 mb-4"),
            # Successfully sent
            (Div(
                Div(
                    Span("✅", cls="text-2xl mr-3"),
                    Div(
                        H4("Invitations Sent", cls="text-lg font-bold text-green-700"),
                        P(f"{len(sent_emails)} student{'' if len(sent_emails)==1 else 's'} invited successfully", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in sent_emails[:8]],
                    P(f"... and {len(sent_emails) - 8} more" if len(sent_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if sent_emails else "",
                cls="mb-5"
            ) if sent_emails else ""),
            
            # Already enrolled
            (Div(
                Div(
                    Span("ℹ️", cls="text-2xl mr-3"),
                    Div(
                        H4("Already Enrolled", cls="text-lg font-bold text-amber-700"),
                        P(f"{len(already_enrolled_emails)} student{'' if len(already_enrolled_emails)==1 else 's'} already in this course", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(email, cls="mb-1") for email in already_enrolled_emails[:8]],
                    P(f"... and {len(already_enrolled_emails) - 8} more" if len(already_enrolled_emails) > 8 else "", 
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-10 text-sm"
                ) if already_enrolled_emails and len(already_enrolled_emails) <= 15 else "",
                cls="mb-5"
            ) if already_enrolled_emails else ""),
            
            # Errors
            (Div(
                Div(
                    Span("❌", cls="text-2xl mr-3"),
                    Div(
                        H4("Failed Invitations", cls="text-lg font-bold text-red-700"),
                        P(f"{len(error_emails)} invitation{'' if len(error_emails)==1 else 's'} failed to send", 
                          cls="text-gray-700"),
                        cls=""
                    ),
                    cls="flex items-start mb-3"
                ),
                Div(
                    *[P(error, cls="mb-1") for error in error_emails],
                    cls="ml-10 text-sm"
                ) if error_emails else "",
                (P("Note: Check your SMTP settings in the .env file.", 
                  cls="text-xs text-gray-500 mt-2 ml-12")) if error_emails else "",
                cls="mb-5"
            ) if error_emails else ""),
            
            cls="bg-white p-8 rounded-xl shadow-md border border-gray-100 mb-6"
        ),
        
        # Action buttons
        Div(
            Div(
                A("Return to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-200 mr-4 font-medium"),
                A("Invite More Students", href=f"/instructor/invite-students?course_id={course_id}", 
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 mr-4 font-medium"),
                A("View All Students", href="/instructor/manage-students", 
                  cls="bg-teal-600 text-white px-6 py-3 rounded-lg hover:bg-teal-700 font-medium"),
                cls="flex justify-center flex-wrap gap-4"
            ),
            cls="text-center"
        ),
        
        cls="max-w-4xl mx-auto px-4"
    )
    
    # Return as full page rather than just updating a div
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="+"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Create a full confirmation page
    confirmation_content = Div(
        H2("Invitation Results", cls="text-2xl font-bold text-green-700 mb-4"),
        Div(
            Div(
                Span("✅", cls="text-4xl mr-4"),
                Div(
                    H3("Invitations Sent Successfully!", cls="text-xl font-bold text-green-700 mb-2"),
                    P(f"Invited {len(sent_emails)} students to {course.title}", cls="text-gray-700"),
                    cls=""
                ),
                cls="flex items-center mb-6"
            ),
            
            # Successfully sent
            (Div(
                H4("Invitations Sent", cls="text-lg font-bold text-green-700 mb-2"),
                Div(
                    *[P(email, cls="mb-1") for email in sent_emails[:10]],
                    P(f"...and {len(sent_emails) - 10} more" if len(sent_emails) > 10 else "",
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-4 mb-4"
                )
            ) if sent_emails else ""),
            
            # Already enrolled
            (Div(
                H4("Already Enrolled", cls="text-lg font-bold text-amber-700 mb-2"),
                P(f"{len(already_enrolled_emails)} student(s) were already enrolled in this course", cls="mb-2"),
                Div(
                    *[P(email, cls="mb-1") for email in already_enrolled_emails[:5]],
                    P(f"...and {len(already_enrolled_emails) - 5} more" if len(already_enrolled_emails) > 5 else "",
                      cls="text-gray-500 italic mt-1"),
                    cls="ml-4 mb-4"
                ) if already_enrolled_emails and len(already_enrolled_emails) <= 15 else "",
                cls="mb-4"
            ) if already_enrolled_emails else ""),
            
            # Errors
            (Div(
                H4("Failed Invitations", cls="text-lg font-bold text-red-700 mb-2"),
                P(f"{len(error_emails)} invitation(s) failed to send", cls="mb-2"),
                Div(
                    *[P(error, cls="mb-1") for error in error_emails],
                    cls="ml-4 mb-4"
                ) if error_emails else "",
                cls="mb-4"
            ) if error_emails else ""),
            
            # Action buttons
            Div(
                A("Back to Dashboard", href="/instructor/dashboard", 
                  cls="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-200 mr-3"),
                A("Invite More Students", href=f"/instructor/invite-students?course_id={course_id}", 
                  cls="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"),
                cls="mt-4"
            ),
            
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
        ),
        cls="mt-4"
    )
    
    # Sidebar content for the confirmation page
    sidebar_content = Div(
        Div(
            H3("Invitation Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Back to Dashboard", color="gray", href="/instructor/dashboard", icon="←"),
                action_button("Invite More Students", color="indigo", href=f"/instructor/invite-students?course_id={course_id}", icon="✉️"),
                action_button("Manage Students", color="teal", href="/instructor/manage-students", icon="👨‍👩‍👧‍👦"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return a complete dashboard layout for the confirmation
    return dashboard_layout(
        "Invitation Results | FeedForward",
        sidebar_content,
        confirmation_content,
        user_role=Role.INSTRUCTOR
    )
    
# --- CSV Import Routes ---
# This route has been removed since we're now using a simpler approach without special templates

# This route has been replaced by client-side JavaScript processing

# Confirmation is now directly handled in the POST route

# --- Instructor Feedback Review Routes ---

@rt('/instructor/assignments/{assignment_id}/feedback')
@instructor_required
def get(session, assignment_id: int):
    """View all student submissions and feedback for an assignment"""
    # Get current user
    user = users[session['auth']]
    
    # Get the assignment with permission check
    assignment, error = get_instructor_assignment(assignment_id, user.email)
    
    if error:
        return Div(
            P(error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get the course
    course, course_error = get_instructor_course(assignment.course_id, user.email)
    
    if course_error:
        return Div(
            P(course_error, cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get assignment settings
    from app.models.config import AssignmentSettings, assignment_settings
    setting = None
    for s in assignment_settings():
        if s.assignment_id == assignment_id:
            setting = s
            break
    
    # Get all drafts for this assignment
    from app.models.feedback import Draft, drafts
    assignment_drafts = []
    for draft in drafts():
        if draft.assignment_id == assignment_id:
            # Get student info
            student_name = "Unknown Student"
            try:
                student = users[draft.student_email]
                student_name = student.name
            except:
                pass
            
            assignment_drafts.append({
                'draft': draft,
                'student_name': student_name,
                'student_email': draft.student_email
            })
    
    # Sort by submission date (newest first)
    assignment_drafts.sort(key=lambda x: x['draft'].submission_date, reverse=True)
    
    # Group drafts by status
    # Check if the aggregated feedback has been approved yet
    from app.models.feedback import AggregatedFeedback, aggregated_feedback
    
    pending_review = []
    approved = []
    
    for d in assignment_drafts:
        if d['draft'].status == 'feedback_ready':
            # Check if feedback has been approved
            is_approved = False
            if setting and setting.require_review:
                # Check aggregated feedback for approval status
                for fb in aggregated_feedback():
                    if fb.draft_id == d['draft'].id and fb.status == 'approved':
                        is_approved = True
                        break
                
                if is_approved:
                    approved.append(d)
                else:
                    pending_review.append(d)
            else:
                # No review required, all ready feedback is approved
                approved.append(d)
    
    processing = [d for d in assignment_drafts if d['draft'].status in ['submitted', 'processing']]
    error_drafts = [d for d in assignment_drafts if d['draft'].status == 'error']
    
    # Sidebar content
    sidebar_content = Div(
        # Assignment info
        Div(
            H3(assignment.title, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P(f"Course: {course.title}", cls="text-gray-600 mb-1"),
            P(f"Total Submissions: {len(assignment_drafts)}", cls="text-gray-600 mb-4"),
            Div(
                action_button("Back to Assignment", color="gray", 
                            href=f"/instructor/assignments/{assignment_id}", icon="←"),
                action_button("Assignment Settings", color="indigo", 
                            href=f"/instructor/assignments/{assignment_id}/settings"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Status summary
        Div(
            H3("Submission Status", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Pending Review: {len(pending_review)}", 
              cls="text-yellow-600 font-medium mb-2" if pending_review else "text-gray-600 mb-2"),
            P(f"Processing: {len(processing)}", cls="text-blue-600 mb-2"),
            P(f"Approved: {len(approved)}", cls="text-green-600 mb-2"),
            P(f"Errors: {len(error_drafts)}", 
              cls="text-red-600 font-medium mb-2" if error_drafts else "text-gray-600 mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
    )
    
    # Main content
    main_content = Div(
        H1(f"Feedback Review - {assignment.title}", 
           cls="text-3xl font-bold text-indigo-900 mb-6"),
        
        # Pending Review Section (if review is required)
        (Div(
            H2("Pending Review", cls="text-2xl font-semibold text-yellow-700 mb-4"),
            (Div(
                *[Div(
                    Div(
                        Div(
                            H4(f"{d['student_name']} - Draft {d['draft'].version}", 
                               cls="text-lg font-medium text-indigo-800"),
                            P(f"Submitted: {d['draft'].submission_date}", 
                              cls="text-sm text-gray-600"),
                            cls="flex-1"
                        ),
                        Div(
                            status_badge("Pending Review", "yellow"),
                            cls="ml-4"
                        ),
                        cls="flex items-start justify-between mb-3"
                    ),
                    Div(
                        action_button("Review Feedback", color="teal", 
                                    href=f"/instructor/drafts/{d['draft'].id}/review",
                                    icon="👁"),
                        cls="mt-2"
                    ),
                    cls="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-3"
                ) for d in pending_review]
            ) if pending_review else 
            P("No submissions pending review.", cls="text-gray-500 italic")),
            cls="mb-8"
        ) if setting and setting.require_review else ""),
        
        # Processing Section
        Div(
            H2("Processing", cls="text-2xl font-semibold text-blue-700 mb-4"),
            (Div(
                *[Div(
                    Div(
                        Div(
                            H4(f"{d['student_name']} - Draft {d['draft'].version}", 
                               cls="text-lg font-medium text-indigo-800"),
                            P(f"Submitted: {d['draft'].submission_date}", 
                              cls="text-sm text-gray-600"),
                            cls="flex-1"
                        ),
                        Div(
                            Div(cls="animate-spin h-5 w-5 border-b-2 border-blue-600"),
                            cls="ml-4"
                        ),
                        cls="flex items-start justify-between"
                    ),
                    P("Feedback is being generated...", cls="text-gray-600 text-sm mt-2"),
                    cls="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-3"
                ) for d in processing]
            ) if processing else 
            P("No submissions currently being processed.", cls="text-gray-500 italic")),
            cls="mb-8"
        ),
        
        # Approved/Released Section
        Div(
            H2("Released to Students", cls="text-2xl font-semibold text-green-700 mb-4"),
            (Div(
                *[Div(
                    Div(
                        Div(
                            H4(f"{d['student_name']} - Draft {d['draft'].version}", 
                               cls="text-lg font-medium text-indigo-800"),
                            P(f"Submitted: {d['draft'].submission_date}", 
                              cls="text-sm text-gray-600"),
                            cls="flex-1"
                        ),
                        Div(
                            status_badge("Released", "green"),
                            cls="ml-4"
                        ),
                        cls="flex items-start justify-between mb-3"
                    ),
                    Div(
                        action_button("View Feedback", color="indigo", 
                                    href=f"/instructor/drafts/{d['draft'].id}/view",
                                    size="small"),
                        cls="mt-2"
                    ),
                    cls="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-3"
                ) for d in approved]
            ) if approved else 
            P("No feedback has been released yet.", cls="text-gray-500 italic")),
            cls="mb-8"
        ),
        
        # Error Section
        (Div(
            H2("Errors", cls="text-2xl font-semibold text-red-700 mb-4"),
            Div(
                *[Div(
                    Div(
                        Div(
                            H4(f"{d['student_name']} - Draft {d['draft'].version}", 
                               cls="text-lg font-medium text-red-800"),
                            P(f"Submitted: {d['draft'].submission_date}", 
                              cls="text-sm text-gray-600"),
                            cls="flex-1"
                        ),
                        Div(
                            status_badge("Error", "red"),
                            cls="ml-4"
                        ),
                        cls="flex items-start justify-between mb-3"
                    ),
                    P("Failed to generate feedback", cls="text-red-600 text-sm mt-2"),
                    Div(
                        action_button("Retry Generation", color="yellow", 
                                    href=f"/instructor/drafts/{d['draft'].id}/retry",
                                    size="small"),
                        cls="mt-2"
                    ),
                    cls="bg-white p-4 rounded-lg shadow-sm border border-red-200 mb-3"
                ) for d in error_drafts]
            ),
            cls="mb-8"
        ) if error_drafts else ""),
    )
    
    # Use the dashboard layout
    return Titled(
        f"Feedback Review - {assignment.title} | FeedForward",
        dashboard_layout(
            "Feedback Review", 
            sidebar_content, 
            main_content, 
            user_role=Role.INSTRUCTOR,
            current_path="/instructor/dashboard"
        )
    )

@rt('/instructor/drafts/{draft_id}/review')
@instructor_required
def get(session, draft_id: int):
    """Review and approve/edit feedback for a specific draft"""
    # Get current user
    user = users[session['auth']]
    
    # Import necessary models
    from app.models.feedback import Draft, drafts, AggregatedFeedback, aggregated_feedback
    from app.models.assignment import Assignment, assignments, Rubric, rubrics, RubricCategory, rubric_categories
    
    # Get the draft
    try:
        draft = drafts[draft_id]
    except:
        return Div(
            P("Draft not found.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get the assignment and verify instructor owns it
    assignment, error = get_instructor_assignment(draft.assignment_id, user.email)
    
    if error:
        return Div(
            P("You don't have permission to review this feedback.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get student info
    student_name = "Unknown Student"
    try:
        student = users[draft.student_email]
        student_name = student.name
    except:
        pass
    
    # Get aggregated feedback for this draft
    draft_feedback = []
    for feedback in aggregated_feedback():
        if feedback.draft_id == draft_id:
            draft_feedback.append(feedback)
    
    # Get rubric categories for context
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment.id:
            rubric = r
            break
    
    categories = {}
    if rubric:
        for cat in rubric_categories():
            if cat.rubric_id == rubric.id:
                categories[cat.id] = cat
    
    # Sidebar content
    sidebar_content = Div(
        # Draft info
        Div(
            H3("Draft Information", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Student: {student_name}", cls="text-gray-700 mb-2"),
            P(f"Assignment: {assignment.title}", cls="text-gray-700 mb-2"),
            P(f"Draft: {draft.version} of {assignment.max_drafts}", cls="text-gray-700 mb-2"),
            P(f"Submitted: {draft.submission_date}", cls="text-gray-700 mb-2"),
            P(f"Word Count: {draft.word_count if hasattr(draft, 'word_count') else 'N/A'}", 
              cls="text-gray-700 mb-4"),
            Div(
                action_button("Back to Feedback List", color="gray", 
                            href=f"/instructor/assignments/{assignment.id}/feedback", icon="←"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Review actions
        Div(
            H3("Review Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Form(
                Button("Approve & Release", 
                       type="submit",
                       name="action",
                       value="approve",
                       cls="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 mb-3"),
                Button("Request Changes", 
                       type="submit",
                       name="action",
                       value="request_changes",
                       cls="w-full bg-yellow-600 text-white px-4 py-2 rounded-lg hover:bg-yellow-700"),
                method="post",
                action=f"/instructor/drafts/{draft_id}/review"
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
    )
    
    # Main content - show the draft and feedback for review
    main_content = Div(
        H1(f"Review Feedback - {student_name}", 
           cls="text-3xl font-bold text-indigo-900 mb-6"),
        
        # Draft content (if not removed for privacy)
        Div(
            H2("Student Submission", cls="text-2xl font-semibold text-indigo-800 mb-4"),
            (P("Note: Content has been removed for privacy after feedback generation.", 
               cls="text-amber-600 italic mb-4") 
             if draft.content == "[Content removed for privacy]" else
             Pre(
                draft.content,
                cls="bg-gray-50 p-4 rounded-lg text-gray-700 text-sm whitespace-pre-wrap border border-gray-200 overflow-auto max-h-96 mb-6"
            )),
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6"
        ),
        
        # Feedback sections for review
        H2("Generated Feedback", cls="text-2xl font-semibold text-indigo-800 mb-4"),
        
        # Overall score calculation
        (Div(
            H3("Overall Score", cls="text-xl font-semibold text-indigo-700 mb-3"),
            (Div(
                P(f"{sum(fb.aggregated_score * categories[fb.category_id].weight for fb in draft_feedback if fb.category_id in categories) / sum(categories[fb.category_id].weight for fb in draft_feedback if fb.category_id in categories):.1f}%", 
                  cls="text-3xl font-bold text-indigo-600"),
                cls="text-center mb-4"
            ) if draft_feedback and categories else P("No score available", cls="text-gray-500 italic")),
            cls="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-4"
        ) if draft_feedback else ""),
        
        # Category-specific feedback for editing
        Form(
            *(Div(
                Div(
                    H3(categories[feedback.category_id].name if feedback.category_id in categories else "General Feedback", 
                       cls="text-lg font-semibold text-indigo-700 mb-2"),
                    P(categories[feedback.category_id].description if feedback.category_id in categories else "", 
                      cls="text-sm text-gray-600 mb-3"),
                    cls="mb-4"
                ),
                
                # Score input
                Div(
                    Label("Score:", For=f"score_{feedback.id}", cls="block text-sm font-medium text-gray-700 mb-1"),
                    Input(
                        type="number",
                        name=f"score_{feedback.id}",
                        value=str(feedback.aggregated_score),
                        min="0",
                        max="100",
                        step="0.1",
                        cls="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    Span(" / 100", cls="ml-2 text-gray-600"),
                    cls="mb-4"
                ),
                
                # Feedback text
                Div(
                    Label("Feedback:", For=f"feedback_{feedback.id}", cls="block text-sm font-medium text-gray-700 mb-1"),
                    Textarea(
                        feedback.feedback_text,
                        name=f"feedback_{feedback.id}",
                        rows="6",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                    ),
                    cls="mb-4"
                ),
                
                # Hidden field for feedback ID
                Input(type="hidden", name=f"feedback_id_{i}", value=str(feedback.id)),
                
                cls="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-4"
            ) for i, feedback in enumerate(draft_feedback)),
            
            # Hidden field for total feedback count
            Input(type="hidden", name="feedback_count", value=str(len(draft_feedback))),
            
            # Save changes button
            Div(
                Button("Save Changes", 
                       type="submit",
                       cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 font-medium"),
                cls="text-center mt-6"
            ),
            
            method="post",
            action=f"/instructor/drafts/{draft_id}/edit-feedback"
        ),
    )
    
    # Use the dashboard layout
    return Titled(
        f"Review Feedback - {student_name} | FeedForward",
        dashboard_layout(
            "Review Feedback", 
            sidebar_content, 
            main_content, 
            user_role=Role.INSTRUCTOR,
            current_path="/instructor/dashboard"
        )
    )

@rt('/instructor/drafts/{draft_id}/review')
@instructor_required
def post(session, draft_id: int, action: str):
    """Handle feedback approval or rejection"""
    # Get current user
    user = users[session['auth']]
    
    # Import necessary models
    from app.models.feedback import Draft, drafts, AggregatedFeedback, aggregated_feedback
    from app.models.assignment import assignments
    
    # Get the draft
    try:
        draft = drafts[draft_id]
    except:
        return "Draft not found."
    
    # Verify instructor owns the assignment
    assignment, error = get_instructor_assignment(draft.assignment_id, user.email)
    
    if error:
        return "You don't have permission to review this feedback."
    
    # Handle the action
    if action == "approve":
        # Update all aggregated feedback to approved status
        for feedback in aggregated_feedback():
            if feedback.draft_id == draft_id:
                feedback.status = "approved"
                feedback.edited_by_instructor = True
                feedback.instructor_email = user.email
                feedback.release_date = datetime.now().isoformat()
                aggregated_feedback.update(feedback)
        
        # Update draft status to show feedback is ready
        draft.status = "feedback_ready"
        drafts.update(draft)
        
        # Redirect back to feedback list
        return RedirectResponse(f"/instructor/assignments/{assignment.id}/feedback", status_code=303)
    
    elif action == "request_changes":
        # This would typically trigger a workflow to regenerate or manually edit feedback
        # For now, we'll just redirect back with a message
        return Div(
            P("Feature coming soon: Request changes to AI-generated feedback.", 
              cls="text-yellow-600 bg-yellow-50 p-4 rounded-lg mb-4"),
            A("Back to Review", href=f"/instructor/drafts/{draft_id}/review",
              cls="bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    return "Invalid action."

@rt('/instructor/drafts/{draft_id}/edit-feedback')
@instructor_required
def post(session, draft_id: int, feedback_count: int = 0, **kwargs):
    """Save edited feedback"""
    # Get current user
    user = users[session['auth']]
    
    # Import necessary models
    from app.models.feedback import Draft, drafts, AggregatedFeedback, aggregated_feedback
    
    # Get the draft
    try:
        draft = drafts[draft_id]
    except:
        return "Draft not found."
    
    # Verify instructor owns the assignment
    assignment, error = get_instructor_assignment(draft.assignment_id, user.email)
    
    if error:
        return "You don't have permission to edit this feedback."
    
    # Process the edited feedback
    try:
        feedback_count = int(feedback_count)
    except:
        feedback_count = 0
    
    # Update each feedback item
    for i in range(feedback_count):
        feedback_id_key = f"feedback_id_{i}"
        score_key = f"score_{kwargs.get(feedback_id_key, '')}"
        feedback_key = f"feedback_{kwargs.get(feedback_id_key, '')}"
        
        if feedback_id_key in kwargs and score_key in kwargs and feedback_key in kwargs:
            try:
                feedback_id = int(kwargs[feedback_id_key])
                new_score = float(kwargs[score_key])
                new_text = kwargs[feedback_key]
                
                # Find and update the feedback
                for feedback in aggregated_feedback():
                    if feedback.id == feedback_id and feedback.draft_id == draft_id:
                        feedback.aggregated_score = new_score
                        feedback.feedback_text = new_text
                        feedback.edited_by_instructor = True
                        feedback.instructor_email = user.email
                        aggregated_feedback.update(feedback)
                        break
                        
            except Exception as e:
                print(f"Error updating feedback {i}: {e}")
    
    # Success message and redirect
    return Div(
        Div(
            P("✓ Feedback updated successfully!", cls="text-green-700 font-medium mb-4"),
            P("The changes have been saved. You can now approve the feedback for release to the student.", 
              cls="text-gray-700 mb-4"),
            Div(
                A("Continue Review", href=f"/instructor/drafts/{draft_id}/review",
                  cls="bg-indigo-600 text-white px-6 py-3 rounded-lg hover:bg-indigo-700 mr-3"),
                A("Back to List", href=f"/instructor/assignments/{assignment.id}/feedback",
                  cls="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300"),
                cls="flex gap-3 justify-center"
            ),
            cls="text-center"
        ),
        cls="bg-green-50 p-8 rounded-xl border border-green-200 max-w-2xl mx-auto mt-8"
    )

@rt('/instructor/drafts/{draft_id}/view')
@instructor_required
def get(session, draft_id: int):
    """View released feedback (read-only)"""
    # Get current user
    user = users[session['auth']]
    
    # Import necessary models
    from app.models.feedback import Draft, drafts, AggregatedFeedback, aggregated_feedback
    from app.models.assignment import assignments, rubrics, rubric_categories
    
    # Get the draft
    try:
        draft = drafts[draft_id]
    except:
        return Div(
            P("Draft not found.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Verify instructor owns the assignment
    assignment, error = get_instructor_assignment(draft.assignment_id, user.email)
    
    if error:
        return Div(
            P("You don't have permission to view this feedback.", cls="text-red-600 bg-red-50 p-4 rounded-lg"),
            A("Return to Dashboard", href="/instructor/dashboard", 
              cls="mt-4 inline-block bg-indigo-600 text-white px-4 py-2 rounded-lg")
        )
    
    # Get student info
    student_name = "Unknown Student"
    try:
        student = users[draft.student_email]
        student_name = student.name
    except:
        pass
    
    # Get aggregated feedback
    draft_feedback = []
    for feedback in aggregated_feedback():
        if feedback.draft_id == draft_id:
            draft_feedback.append(feedback)
    
    # Get rubric categories
    rubric = None
    for r in rubrics():
        if r.assignment_id == assignment.id:
            rubric = r
            break
    
    categories = {}
    if rubric:
        for cat in rubric_categories():
            if cat.rubric_id == rubric.id:
                categories[cat.id] = cat
    
    # Calculate overall score
    total_score = 0
    total_weight = 0
    if draft_feedback and categories:
        for feedback in draft_feedback:
            if feedback.category_id in categories:
                cat = categories[feedback.category_id]
                total_score += feedback.aggregated_score * cat.weight
                total_weight += cat.weight
    
    overall_score = total_score / total_weight if total_weight > 0 else 0
    
    # Main content
    main_content = Div(
        # Header
        Div(
            H1(f"Feedback for {student_name}", cls="text-3xl font-bold text-indigo-900 mb-2"),
            P(f"{assignment.title} - Draft {draft.version}", cls="text-xl text-gray-600"),
            cls="mb-6"
        ),
        
        # Overall score card
        Div(
            H2("Overall Score", cls="text-xl font-semibold text-indigo-800 mb-3"),
            P(f"{overall_score:.1f}%", cls="text-4xl font-bold text-indigo-600 text-center"),
            cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-6"
        ),
        
        # Category feedback
        H2("Detailed Feedback", cls="text-xl font-semibold text-indigo-800 mb-4"),
        *(Div(
            Div(
                H3(categories[feedback.category_id].name if feedback.category_id in categories else "General", 
                   cls="text-lg font-semibold text-indigo-700 mb-2"),
                P(f"Score: {feedback.aggregated_score:.1f}%", 
                  cls="text-lg font-medium text-indigo-600 mb-3"),
                cls="mb-4"
            ),
            Div(
                *[P(line, cls="mb-2") for line in feedback.feedback_text.split('\n') if line.strip()],
                cls="text-gray-700"
            ),
            (P(f"Edited by: {feedback.instructor_email}", 
               cls="text-sm text-gray-500 italic mt-4") 
             if feedback.edited_by_instructor else ""),
            cls="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-4"
        ) for feedback in draft_feedback),
        
        # Actions
        Div(
            A("Back to Feedback List", 
              href=f"/instructor/assignments/{assignment.id}/feedback",
              cls="bg-gray-200 text-gray-800 px-6 py-3 rounded-lg hover:bg-gray-300"),
            cls="text-center mt-8"
        )
    )
    
    # Sidebar
    sidebar_content = Div(
        Div(
            H3("Feedback Details", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Student: {student_name}", cls="text-gray-700 mb-2"),
            P(f"Submitted: {draft.submission_date}", cls="text-gray-700 mb-2"),
            P(f"Status: Released", cls="text-green-700 font-medium mb-2"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    return Titled(
        f"View Feedback - {student_name} | FeedForward",
        dashboard_layout(
            "View Feedback",
            sidebar_content,
            main_content,
            user_role=Role.INSTRUCTOR,
            current_path="/instructor/dashboard"
        )
    )
=======
# Import all routes from instructor modules
from app.routes.instructor.dashboard import *
from app.routes.instructor.models import *
from app.routes.instructor.courses import *
from app.routes.instructor.assignments import *
from app.routes.instructor.submissions import *
from app.routes.instructor.students import *
from app.routes.instructor.analytics import *
>>>>>>> 4b1b19e (Refactor instructor routes into modular structure)
