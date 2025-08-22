"""
System configuration and settings model definitions
"""

from app.models.user import db

# Define system configuration table if it doesn't exist
system_config = db.t.system_config
if system_config not in db.t:
    system_config.create({"key": str, "value": str, "description": str}, pk="key")
SystemConfig = system_config.dataclass()

# Define domain whitelist table if it doesn't exist
domain_whitelist = db.t.domain_whitelist
if domain_whitelist not in db.t:
    domain_whitelist.create(
        {
            "id": int,
            "domain": str,
            "auto_approve_instructor": bool,
            "created_at": str,
            "updated_at": str,
        },
        pk="id",
    )
DomainWhitelist = domain_whitelist.dataclass()

# Define aggregation methods table if it doesn't exist
aggregation_methods = db.t.aggregation_methods
if aggregation_methods not in db.t:
    aggregation_methods.create(
        {"id": int, "name": str, "description": str, "is_active": bool}, pk="id"
    )
AggregationMethod = aggregation_methods.dataclass()

# Define feedback styles table if it doesn't exist
feedback_styles = db.t.feedback_styles
if feedback_styles not in db.t:
    feedback_styles.create(
        {"id": int, "name": str, "description": str, "is_active": bool}, pk="id"
    )
FeedbackStyle = feedback_styles.dataclass()

# Define mark display options table if it doesn't exist
mark_display_options = db.t.mark_display_options
if mark_display_options not in db.t:
    mark_display_options.create(
        {
            "id": int,
            "display_type": str,  # 'numeric', 'hidden', 'icon'
            "name": str,
            "description": str,
            "icon_type": str,
            "is_active": bool,
        },
        pk="id",
    )
MarkDisplayOption = mark_display_options.dataclass()

# Define AI models table if it doesn't exist
ai_models = db.t.ai_models
if ai_models not in db.t:
    ai_models.create(
        {
            "id": int,
            "name": str,
            "provider": str,  # OpenAI, Anthropic, Ollama, HuggingFace, etc.
            "model_id": str,  # gpt-4, claude-3, llama-3, etc.
            "model_version": str,
            "description": str,
            "api_config": str,  # JSON string with API configuration
            "owner_type": str,  # 'system' or 'instructor'
            "owner_id": int,  # ID of the instructor if owner_type is 'instructor'
            "capabilities": str,  # JSON array of capabilities: ['text', 'vision', 'code', 'audio']
            "max_context": int,  # Maximum context length
            "active": bool,
            "created_at": str,
            "updated_at": str,
        },
        pk="id",
    )
AIModel = ai_models.dataclass()

# Define model capabilities table for easier querying
model_capabilities = db.t.model_capabilities
if model_capabilities not in db.t:
    model_capabilities.create(
        {
            "id": int,
            "model_id": int,
            "capability": str,  # 'text', 'vision', 'code', 'audio'
            "is_primary": bool,  # Is this the primary use case for this model
        },
        pk="id",
    )
ModelCapability = model_capabilities.dataclass()

# Define assignment settings table if it doesn't exist
assignment_settings = db.t.assignment_settings
if assignment_settings not in db.t:
    assignment_settings.create(
        {
            "id": int,
            "assignment_id": int,
            "primary_ai_model_id": int,  # Model used for aggregation
            "feedback_level": str,  # 'overall', 'criterion', 'both'
            "num_runs": int,
            "aggregation_method_id": int,
            "feedback_style_id": int,
            "require_review": bool,
            "mark_display_option_id": int,
        },
        pk="id",
    )
AssignmentSettings = assignment_settings.dataclass()

# Define assignment model runs table if it doesn't exist
assignment_model_runs = db.t.assignment_model_runs
if assignment_model_runs not in db.t:
    assignment_model_runs.create(
        {"id": int, "assignment_setting_id": int, "ai_model_id": int, "num_runs": int}, pk="id"
    )
AssignmentModelRun = assignment_model_runs.dataclass()
