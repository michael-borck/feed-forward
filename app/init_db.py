"""
Initialize the database with default data and an admin user
"""

import json
import os
import sys
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.assessment import AssessmentType, assessment_types
from app.models.config import (
    AggregationMethod,
    AIModel,
    DomainWhitelist,
    FeedbackStyle,
    MarkDisplayOption,
    SystemConfig,
    aggregation_methods,
    ai_models,
    domain_whitelist,
    feedback_styles,
    mark_display_options,
    system_config,
)
from app.models.user import Role, User, users
from app.utils.auth import get_password_hash


def init_db():
    """Initialize the database with default data"""

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Initialize assessment types
    now = datetime.now().isoformat()
    default_assessment_types = [
        {
            "id": 1,
            "type_code": "essay",
            "display_name": "Essay",
            "description": "Traditional text-based essay assessment",
            "handler_class": "EssayAssessmentHandler",
            "file_extensions": json.dumps([".txt", ".docx", ".pdf"]),
            "max_file_size": 10485760,  # 10MB
            "requires_file": False,
            "supports_text_input": True,
            "configuration": json.dumps(
                {
                    "min_words": 100,
                    "max_words": 5000,
                    "allowed_formats": ["plain_text", "markdown"],
                }
            ),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": 2,
            "type_code": "code",
            "display_name": "Code",
            "description": "Programming code assessment",
            "handler_class": "CodeAssessmentHandler",
            "file_extensions": json.dumps(
                [".py", ".js", ".java", ".cpp", ".c", ".html", ".css"]
            ),
            "max_file_size": 1048576,  # 1MB
            "requires_file": False,
            "supports_text_input": True,
            "configuration": json.dumps(
                {
                    "supported_languages": [
                        "python",
                        "javascript",
                        "java",
                        "cpp",
                        "c",
                        "html",
                        "css",
                    ],
                    "syntax_highlighting": True,
                    "execution_enabled": False,
                }
            ),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": 3,
            "type_code": "math",
            "display_name": "Mathematics",
            "description": "Mathematical proofs and calculations",
            "handler_class": "MathAssessmentHandler",
            "file_extensions": json.dumps([".tex", ".pdf"]),
            "max_file_size": 5242880,  # 5MB
            "requires_file": False,
            "supports_text_input": True,
            "configuration": json.dumps(
                {"latex_support": True, "equation_rendering": True}
            ),
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": 4,
            "type_code": "video",
            "display_name": "Video Presentation",
            "description": "Video-based presentations and demonstrations",
            "handler_class": "VideoAssessmentHandler",
            "file_extensions": json.dumps([".mp4", ".avi", ".mov", ".webm"]),
            "max_file_size": 104857600,  # 100MB
            "requires_file": True,
            "supports_text_input": False,
            "configuration": json.dumps(
                {
                    "max_duration_seconds": 600,  # 10 minutes
                    "requires_external_service": True,
                    "service_name": "video_analyzer",
                }
            ),
            "is_active": False,  # Disabled by default until service is configured
            "created_at": now,
            "updated_at": now,
        },
    ]

    for type_config in default_assessment_types:
        try:
            # Check if type exists by ID
            existing_types = [
                t for t in assessment_types() if t.id == type_config["id"]
            ]
            if existing_types:
                print(f"Assessment type {type_config['display_name']} already exists")
                continue

            # Create assessment type
            assessment_type = AssessmentType(**type_config)
            assessment_types.insert(assessment_type)
            print(f"Created assessment type: {type_config['display_name']}")
        except Exception as e:
            print(
                f"Error creating assessment type {type_config['display_name']}: {e!s}"
            )

    # Create admin user if it doesn't exist
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")

    try:
        # Check if admin exists
        users[admin_email]
        print(f"Admin user {admin_email} already exists")
    except Exception:
        # Create admin user
        admin = User(
            email=admin_email,
            name="Admin User",
            password=get_password_hash(admin_password),
            role=Role.ADMIN,
            verified=True,
            verification_token="",
            approved=True,
            department="Administration",
            reset_token="",
            reset_token_expiry="",
        )
        users.insert(admin)
        print(f"Created admin user: {admin_email}")

    # Initialize system configuration
    config_items = [
        (
            "default_max_drafts",
            "3",
            "Default maximum number of drafts allowed per assignment",
        ),
        ("default_num_runs", "3", "Default number of AI model runs per submission"),
        (
            "instructor_approval_required",
            "true",
            "Whether instructors need approval from admin",
        ),
    ]

    for key, value, description in config_items:
        try:
            # Check if config exists
            _ = system_config[key]
            print(f"Config {key} already exists")
        except Exception:
            # Create config
            config = SystemConfig(key=key, value=value, description=description)
            system_config.insert(config)
            print(f"Created config: {key}")

    # Initialize AI models
    ai_model_configs = [
        {
            "id": 1,
            "name": "GPT-4o",
            "provider": "OpenAI",
            "model_id": "gpt-4o",
            "api_config": json.dumps(
                {
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "system_prompt": "You are an educational feedback assistant specializing in providing constructive, formative feedback on student assignments.",
                }
            ),
            "active": True,
        },
        {
            "id": 2,
            "name": "Claude 3 Sonnet",
            "provider": "Anthropic",
            "model_id": "claude-3-sonnet-20240229",
            "api_config": json.dumps(
                {
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "system_prompt": "You are an educational feedback assistant specializing in providing constructive, formative feedback on student assignments.",
                }
            ),
            "active": True,
        },
        {
            "id": 3,
            "name": "Gemini 1.5 Pro",
            "provider": "Google",
            "model_id": "gemini-1.5-pro",
            "api_config": json.dumps(
                {
                    "temperature": 0.2,
                    "max_tokens": 4000,
                    "system_prompt": "You are an educational feedback assistant specializing in providing constructive, formative feedback on student assignments.",
                }
            ),
            "active": True,
        },
    ]

    for config in ai_model_configs:
        try:
            # Check if model exists by ID
            existing_models = [m for m in ai_models() if m.id == config["id"]]
            if existing_models:
                print(f"AI Model {config['name']} already exists")
                continue

            # Create model
            model = AIModel(
                id=config["id"],
                name=config["name"],
                provider=config["provider"],
                model_id=config["model_id"],
                api_config=config["api_config"],
                owner_type="system",
                owner_id=0,
                active=config["active"],
            )
            ai_models.insert(model)
            print(f"Created AI model: {config['name']}")
        except Exception as e:
            print(f"Error creating AI model {config['name']}: {e!s}")

    # Initialize aggregation methods
    agg_methods = [
        (1, "Mean", "Simple average of all scores", True),
        (2, "Weighted Mean", "Weighted average based on confidence scores", True),
        (3, "Median", "Middle value of all scores", True),
        (4, "Trimmed Mean", "Average after removing highest and lowest scores", True),
    ]

    for id, name, description, is_active in agg_methods:
        try:
            # Check if method exists by ID
            existing_methods = [m for m in aggregation_methods() if m.id == id]
            if existing_methods:
                print(f"Aggregation method {name} already exists")
                continue

            # Create method
            method = AggregationMethod(
                id=id, name=name, description=description, is_active=is_active
            )
            aggregation_methods.insert(method)
            print(f"Created aggregation method: {name}")
        except Exception as e:
            print(f"Error creating aggregation method {name}: {e!s}")

    # Initialize feedback styles
    styles = [
        (1, "Balanced", "Equal focus on strengths and areas for improvement", True),
        (
            2,
            "Encouraging",
            "More emphasis on strengths with gentle areas for improvement",
            True,
        ),
        (3, "Critical", "More emphasis on areas for improvement", True),
        (4, "Detailed", "In-depth analysis with specific recommendations", True),
    ]

    for id, name, description, is_active in styles:
        try:
            # Check if style exists by ID
            existing_styles = [s for s in feedback_styles() if s.id == id]
            if existing_styles:
                print(f"Feedback style {name} already exists")
                continue

            # Create style
            style = FeedbackStyle(
                id=id, name=name, description=description, is_active=is_active
            )
            feedback_styles.insert(style)
            print(f"Created feedback style: {name}")
        except Exception as e:
            print(f"Error creating feedback style {name}: {e!s}")

    # Initialize mark display options
    display_options = [
        (1, "numeric", "Numeric Score", "Display as a percentage", "", True),
        (2, "hidden", "No Score", "Hide numerical scores", "", True),
        (
            3,
            "icon",
            "Bullseye Icons",
            "Visual representation using bullseye icons",
            "bullseye",
            True,
        ),
        (
            4,
            "icon",
            "Track Icons",
            "Visual representation showing progress",
            "track",
            True,
        ),
    ]

    for id, display_type, name, description, icon_type, is_active in display_options:
        try:
            # Check if option exists by ID
            existing_options = [o for o in mark_display_options() if o.id == id]
            if existing_options:
                print(f"Mark display option {name} already exists")
                continue

            # Create option
            option = MarkDisplayOption(
                id=id,
                display_type=display_type,
                name=name,
                description=description,
                icon_type=icon_type,
                is_active=is_active,
            )
            mark_display_options.insert(option)
            print(f"Created mark display option: {name}")
        except Exception as e:
            print(f"Error creating mark display option {name}: {e!s}")

    # Initialize domain whitelist
    domains = [
        (1, "curtin.edu.au", True),
        (2, "ecu.edu.au", True),
        (3, "uwa.edu.au", True),
        (4, "murdoch.edu.au", True),
        (5, "notre-dame.edu.au", False),
    ]

    now = datetime.now().isoformat()
    for id, domain, auto_approve in domains:
        try:
            # Check if domain exists
            existing_domains = [d for d in domain_whitelist() if d.domain == domain]
            if existing_domains:
                print(f"Domain {domain} already exists in whitelist")
                continue

            # Create domain entry
            domain_entry = DomainWhitelist(
                id=id,
                domain=domain,
                auto_approve_instructor=auto_approve,
                created_at=now,
                updated_at=now,
            )
            domain_whitelist.insert(domain_entry)
            print(f"Added domain to whitelist: {domain} (auto-approve: {auto_approve})")
        except Exception as e:
            print(f"Error adding domain {domain} to whitelist: {e!s}")

    print("Database initialization complete!")


if __name__ == "__main__":
    init_db()
