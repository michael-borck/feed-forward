#!/usr/bin/env python3
"""
Update system AI models with proper API configuration structure
"""

import json
import os
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.config import ai_models
from app.utils.crypto import encrypt_sensitive_data


def update_system_models():
    """Update existing system models with proper API configuration"""

    print("Updating system AI model configurations...")

    # Model configurations with placeholders
    model_configs = {
        1: {  # GPT-4o
            "provider": "OpenAI",
            "config": {
                "api_key": "YOUR_OPENAI_API_KEY_HERE",
                "temperature": 0.2,
                "max_tokens": 4000,
                "system_prompt": "You are an expert educational assessor providing detailed, constructive feedback on student work based on the provided rubric criteria.",
            },
        },
        2: {  # Claude 3 Sonnet
            "provider": "Anthropic",
            "config": {
                "api_key": "YOUR_ANTHROPIC_API_KEY_HERE",
                "temperature": 0.2,
                "max_tokens": 4000,
                "system_prompt": "You are an expert educational assessor providing detailed, constructive feedback on student work based on the provided rubric criteria.",
            },
        },
        3: {  # Gemini 1.5 Pro
            "provider": "Google",
            "config": {
                "api_key": "YOUR_GOOGLE_API_KEY_HERE",
                "base_url": "",  # Optional for Google
                "temperature": 0.2,
                "max_tokens": 4000,
                "system_prompt": "You are an expert educational assessor providing detailed, constructive feedback on student work based on the provided rubric criteria.",
            },
        },
    }

    updated_count = 0

    for model in ai_models():
        if model.id in model_configs:
            config_data = model_configs[model.id]

            # Encrypt API key if it's a placeholder (not configured yet)
            config = config_data["config"].copy()
            if config.get("api_key") and config["api_key"].startswith("YOUR_"):
                # This is a placeholder - encrypt it as-is so admins know to replace it
                config["api_key"] = encrypt_sensitive_data(config["api_key"])

            # Update the model's API configuration
            new_api_config = json.dumps(config)

            # Update model in database
            model.api_config = new_api_config
            model.updated_at = datetime.now().isoformat()

            # Save changes using FastLite update
            ai_models.update(model)

            print(
                f"✅ Updated {model.name} ({config_data['provider']}) with proper API configuration"
            )
            updated_count += 1
        else:
            print(f"⚠️  Skipped model ID {model.id} - not in configuration list")

    print(f"\n✅ Updated {updated_count} system models")
    print("\n📝 Next Steps:")
    print("1. Login as admin: admin@example.com / Admin123!")
    print("2. Navigate to AI Models management")
    print("3. Edit each model to add your actual API keys")
    print("4. Replace placeholders with real credentials:")
    print("   - OpenAI: YOUR_OPENAI_API_KEY_HERE")
    print("   - Anthropic: YOUR_ANTHROPIC_API_KEY_HERE")
    print("   - Google: YOUR_GOOGLE_API_KEY_HERE")

    return True


def main():
    """Update system model configurations"""
    try:
        update_system_models()
        print("\n🎯 System models are now ready for API key configuration!")

    except Exception as e:
        print(f"❌ Update failed: {e!s}")
        return False

    return True


if __name__ == "__main__":
    main()
