#!/usr/bin/env python3
"""
Interactive setup script for configuring API keys for LLM providers
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv, set_key
from litellm import completion


class APIKeySetup:
    """Helper class for setting up and validating API keys"""

    PROVIDERS = {
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
            "name": "Google (Gemini)",
            "env_var": "GOOGLE_API_KEY",
            "test_model": "gemini/gemini-1.5-flash",
            "instructions": "Get your API key from https://makersuite.google.com/app/apikey",
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
            "test_model": "ollama/llama3.2",
            "instructions": "Install Ollama from https://ollama.ai and run: ollama pull llama3.2",
            "default_value": "http://localhost:11434",
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

    async def test_api_key(self, provider: str, api_key: str) -> bool:
        """Test if an API key works by making a simple completion request"""
        provider_info = self.PROVIDERS[provider]
        test_model = provider_info["test_model"]

        try:
            # Set the API key temporarily
            if provider == "ollama":
                os.environ["OLLAMA_API_BASE"] = api_key
            else:
                os.environ[provider_info["env_var"]] = api_key

            print(f"Testing {provider_info['name']} connection...")

            # Make a simple test request
            response = await completion(
                model=test_model,
                messages=[
                    {"role": "user", "content": "Say 'test successful' in 3 words"}
                ],
                max_tokens=10,
                temperature=0,
            )

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

    def save_api_key(self, provider: str, api_key: str):
        """Save API key to .env file"""
        provider_info = self.PROVIDERS[provider]
        env_var = provider_info["env_var"]

        # Create .env file if it doesn't exist
        if not self.env_path.exists():
            self.env_path.touch()
            print(f"Created new .env file at {self.env_path}")

        # Save the key
        set_key(str(self.env_path), env_var, api_key)
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
            print("3. Configure Google (Gemini)")
            print("4. Configure Groq")
            print("5. Configure Ollama (Local)")
            print("6. Test all configured providers")
            print("7. View current configuration")
            print("0. Exit")

            choice = input("\nEnter your choice (0-7): ").strip()

            if choice == "0":
                print("\n👋 Exiting setup")
                break

            elif choice in ["1", "2", "3", "4", "5"]:
                provider_map = {
                    "1": "openai",
                    "2": "anthropic",
                    "3": "google",
                    "4": "groq",
                    "5": "ollama",
                }
                provider = provider_map[choice]
                await self.configure_provider(provider)

            elif choice == "6":
                await self.test_all_configured()

            elif choice == "7":
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
        if provider == "ollama":
            default = info.get("default_value", "")
            api_value = input(f"Enter Ollama API URL (default: {default}): ").strip()
            if not api_value:
                api_value = default
        else:
            api_value = input(f"Enter your {info['name']} API key: ").strip()

        if not api_value:
            print("❌ No value entered. Skipping.")
            return

        # Test the API key
        print(f"\n🧪 Testing {info['name']} configuration...")
        if await self.test_api_key(provider, api_value):
            # Save if successful
            self.save_api_key(provider, api_value)
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
