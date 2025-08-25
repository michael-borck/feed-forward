#!/usr/bin/env python3
"""
Interactive setup script for configuring API keys for LLM providers
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import ClassVar, Optional

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv, set_key
from litellm import completion


class APIKeySetup:
    """Helper class for setting up and validating API keys"""

    PROVIDERS: ClassVar[dict] = {
        "openai": {
            "name": "OpenAI",
            "env_var": "OPENAI_API_KEY",
            "test_model": "gpt-3.5-turbo",
            "instructions": "Get your API key from https://platform.openai.com/api-keys",
        },
        "anthropic": {
            "name": "Anthropic (Claude)",
            "env_var": "ANTHROPIC_API_KEY",
            "test_model": "claude-3-haiku-20240307",
            "instructions": "Get your API key from https://console.anthropic.com/settings/keys",
        },
        "google": {
            "name": "Google (PaLM/Bard)",
            "env_var": "GOOGLE_API_KEY",
            "test_model": "google/text-bison-001",
            "instructions": "Get your API key from https://makersuite.google.com/app/apikey",
        },
        "gemini": {
            "name": "Google Gemini",
            "env_var": "GEMINI_API_KEY",
            "test_model": "gemini/gemini-1.5-flash",
            "instructions": "Get your API key from https://aistudio.google.com/app/apikey",
        },
        "groq": {
            "name": "Groq",
            "env_var": "GROQ_API_KEY",
            "test_model": "groq/llama-3.1-8b-instant",
            "instructions": "Get your API key from https://console.groq.com/keys",
        },
        "ollama": {
            "name": "Ollama (Local)",
            "env_var": "OLLAMA_API_BASE",
            "env_var_key": "OLLAMA_API_KEY",
            "test_model": "ollama/llama3.2",
            "instructions": "Install Ollama from https://ollama.ai and run: ollama pull llama3.2",
            "default_value": "http://localhost:11434",
            "optional_key": True,
        },
        "openrouter": {
            "name": "OpenRouter",
            "env_var": "OPENROUTER_API_KEY",
            "test_model": "openrouter/auto",
            "instructions": "Get your API key from https://openrouter.ai/keys",
        },
        "custom": {
            "name": "Custom OpenAI-Compatible",
            "env_var": "CUSTOM_LLM_API_KEY",
            "env_var_base": "CUSTOM_LLM_BASE_URL",
            "test_model": "gpt-3.5-turbo",  # Assumes OpenAI-compatible model naming
            "instructions": "Enter your custom endpoint URL and API key",
            "requires_base_url": True,
        },
    }

    def __init__(self):
        self.env_path = Path.cwd() / ".env"
        self.load_existing_env()

    def load_existing_env(self):
        """Load existing environment variables"""
        if self.env_path.exists():
            load_dotenv(self.env_path)
            print(f"✅ Loaded existing .env file from {self.env_path}")
        else:
            print(f"⚠️  No .env file found. Will create one at {self.env_path}")

    async def test_api_key(self, provider: str, api_key: str, base_url: Optional[str] = None) -> bool:
        """Test if an API key works by making a simple completion request"""
        provider_info = self.PROVIDERS[provider]
        test_model = provider_info["test_model"]

        try:
            # Set the API key/URL temporarily
            if provider == "ollama":
                os.environ["OLLAMA_API_BASE"] = api_key
                if provider_info.get("env_var_key"):
                    ollama_key = input("Enter Ollama API key (optional, press Enter to skip): ").strip()
                    if ollama_key:
                        os.environ[provider_info["env_var_key"]] = ollama_key
            elif provider == "custom":
                os.environ[provider_info["env_var"]] = api_key
                if base_url:
                    os.environ[provider_info["env_var_base"]] = base_url
            else:
                os.environ[provider_info["env_var"]] = api_key

            print(f"Testing {provider_info['name']} connection...")

            # Prepare completion parameters
            completion_params = {
                "model": test_model,
                "messages": [
                    {"role": "user", "content": "Say 'test successful' in 3 words"}
                ],
                "max_tokens": 10,
                "temperature": 0,
            }
            
            # Add base URL for custom providers
            if provider == "custom" and base_url:
                completion_params["api_base"] = base_url
            elif provider == "openrouter":
                completion_params["api_base"] = "https://openrouter.ai/api/v1"

            # Make a simple test request
            response = await completion(**completion_params)

            if response and response.choices:
                print(f"✅ {provider_info['name']} API key validated successfully!")
                return True

        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                print(f"❌ Invalid API key for {provider_info['name']}")
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                if provider == "ollama":
                    print(
                        f"❌ Cannot connect to Ollama. Make sure it's running at {api_key}"
                    )
                else:
                    print(
                        f"❌ Connection error for {provider_info['name']}: {error_msg}"
                    )
            else:
                print(f"❌ Error testing {provider_info['name']}: {error_msg}")
            return False

    def save_api_key(self, provider: str, api_key: str, base_url: Optional[str] = None, ollama_key: Optional[str] = None):
        """Save API key to .env file"""
        provider_info = self.PROVIDERS[provider]
        env_var = provider_info["env_var"]

        # Create .env file if it doesn't exist
        if not self.env_path.exists():
            self.env_path.touch()
            print(f"Created new .env file at {self.env_path}")

        # Save the key(s)
        set_key(str(self.env_path), env_var, api_key)
        
        # Save additional keys if needed
        if provider == "ollama" and ollama_key:
            set_key(str(self.env_path), provider_info["env_var_key"], ollama_key)
        elif provider == "custom" and base_url:
            set_key(str(self.env_path), provider_info["env_var_base"], base_url)
            
        print(f"✅ Saved {provider_info['name']} configuration to .env file")

    def get_current_keys(self) -> dict[str, Optional[str]]:
        """Get currently configured API keys"""
        current = {}
        for provider, info in self.PROVIDERS.items():
            env_var = info["env_var"]
            current[provider] = os.environ.get(env_var)
        return current

    async def interactive_setup(self):
        """Run interactive setup process"""
        print("\n" + "=" * 60)
        print("🤖 FeedForward LLM API Key Configuration")
        print("=" * 60)

        # Show current configuration
        current_keys = self.get_current_keys()
        configured = [p for p, k in current_keys.items() if k]

        if configured:
            print("\n📋 Currently configured providers:")
            for provider in configured:
                print(f"  ✅ {self.PROVIDERS[provider]['name']}")
        else:
            print("\n⚠️  No API keys currently configured")

        # Menu
        while True:
            print("\n" + "-" * 40)
            print("Choose an option:")
            print("1. Configure OpenAI")
            print("2. Configure Anthropic (Claude)")
            print("3. Configure Google (PaLM/Bard)")
            print("4. Configure Google Gemini")
            print("5. Configure Groq")
            print("6. Configure Ollama (Local)")
            print("7. Configure OpenRouter")
            print("8. Configure Custom OpenAI-Compatible")
            print("9. Test all configured providers")
            print("10. View current configuration")
            print("0. Exit")

            choice = input("\nEnter your choice (0-10): ").strip()

            if choice == "0":
                print("\n👋 Exiting setup")
                break

            elif choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                provider_map = {
                    "1": "openai",
                    "2": "anthropic",
                    "3": "google",
                    "4": "gemini",
                    "5": "groq",
                    "6": "ollama",
                    "7": "openrouter",
                    "8": "custom",
                }
                provider = provider_map[choice]
                await self.configure_provider(provider)

            elif choice == "9":
                await self.test_all_configured()

            elif choice == "10":
                self.show_configuration()

            else:
                print("❌ Invalid choice. Please try again.")

    async def configure_provider(self, provider: str):
        """Configure a specific provider"""
        info = self.PROVIDERS[provider]

        print(f"\n🔧 Configuring {info['name']}")
        print(f"📖 {info['instructions']}")

        # Check if already configured
        current_value = os.environ.get(info["env_var"])
        if current_value:
            print(f"⚠️  {info['name']} is already configured")
            overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
            if overwrite != "y":
                return

        # Get the API key/URL
        base_url = None
        ollama_key = None
        
        if provider == "ollama":
            default = info.get("default_value", "")
            api_value = input(f"Enter Ollama API URL (default: {default}): ").strip()
            if not api_value:
                api_value = default
            ollama_key = input("Enter Ollama API key (optional, press Enter to skip): ").strip()
        elif provider == "custom":
            base_url = input("Enter the base URL for your OpenAI-compatible endpoint: ").strip()
            if not base_url:
                print("❌ Base URL is required for custom providers. Skipping.")
                return
            api_value = input(f"Enter your {info['name']} API key: ").strip()
        else:
            api_value = input(f"Enter your {info['name']} API key: ").strip()

        if not api_value and provider != "ollama":
            print("❌ No value entered. Skipping.")
            return

        # Test the API key
        print(f"\n🧪 Testing {info['name']} configuration...")
        if await self.test_api_key(provider, api_value, base_url):
            # Save if successful
            self.save_api_key(provider, api_value, base_url, ollama_key)
            print(f"✅ {info['name']} configured successfully!")
        else:
            print(f"❌ Failed to validate {info['name']} configuration")
            save_anyway = (
                input("Do you want to save it anyway? (y/n): ").strip().lower()
            )
            if save_anyway == "y":
                self.save_api_key(provider, api_value)

    async def test_all_configured(self):
        """Test all configured providers"""
        print("\n🧪 Testing all configured providers...")
        current_keys = self.get_current_keys()
        configured = [(p, k) for p, k in current_keys.items() if k]

        if not configured:
            print("❌ No providers configured to test")
            return

        results = []
        for provider, key in configured:
            success = await self.test_api_key(provider, key)
            results.append((provider, success))

        # Summary
        print("\n📊 Test Results:")
        for provider, success in results:
            status = "✅ Working" if success else "❌ Failed"
            print(f"  {self.PROVIDERS[provider]['name']}: {status}")

    def show_configuration(self):
        """Show current configuration status"""
        print("\n📋 Current Configuration:")
        current_keys = self.get_current_keys()

        for provider, info in self.PROVIDERS.items():
            value = current_keys[provider]
            if value:
                if provider == "ollama":
                    print(f"  ✅ {info['name']}: {value}")
                else:
                    # Mask API keys for security
                    masked = (
                        value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                    )
                    print(f"  ✅ {info['name']}: {masked}")
            else:
                print(f"  ❌ {info['name']}: Not configured")


async def main():
    """Main entry point"""
    setup = APIKeySetup()

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            await setup.test_all_configured()
        elif sys.argv[1] == "--show":
            setup.show_configuration()
        else:
            print("Usage: python setup_api_keys.py [--test|--show]")
    else:
        await setup.interactive_setup()


if __name__ == "__main__":
    asyncio.run(main())
