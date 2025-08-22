#!/usr/bin/env python3
"""
Health check script for LLM providers
Verifies connectivity and functionality of all configured AI models
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
from litellm import completion
from rich import box
from rich.console import Console
from rich.table import Table

from app.models.feedback import AIModel, ai_models

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Reduce noise from litellm
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()


class LLMHealthChecker:
    """Check health status of all LLM providers"""

    def __init__(self):
        load_dotenv()
        self.results = []

    async def check_provider(self, model: AIModel) -> dict:
        """Check a single provider's health"""
        start_time = datetime.now()

        result = {
            "provider": model.provider,
            "model": model.model_id,
            "name": model.name,
            "status": "checking",
            "response_time": None,
            "error": None,
            "has_api_key": False,
        }

        try:
            # Check for API key
            json.loads(model.api_config)

            # Check environment for API key
            env_var_map = {
                "OpenAI": "OPENAI_API_KEY",
                "Anthropic": "ANTHROPIC_API_KEY",
                "Google": "GOOGLE_API_KEY",
                "Groq": "GROQ_API_KEY",
                "Ollama": "OLLAMA_API_BASE",
            }

            env_var = env_var_map.get(model.provider)
            if env_var:
                api_key = os.environ.get(env_var)
                result["has_api_key"] = bool(api_key)

                if not api_key and model.provider != "Ollama":
                    result["status"] = "no_api_key"
                    result["error"] = f"Missing {env_var}"
                    return result

            # Build model string for LiteLLM
            if model.provider.lower() == "openai":
                model_string = model.model_id
            elif model.provider.lower() == "anthropic":
                model_string = f"anthropic/{model.model_id}"
            elif model.provider.lower() == "google":
                model_string = f"gemini/{model.model_id}"
            elif model.provider.lower() == "groq":
                model_string = f"groq/{model.model_id}"
            elif model.provider.lower() == "ollama":
                model_string = f"ollama/{model.model_id}"
            else:
                model_string = model.model_id

            # Test with a simple prompt
            test_prompt = "Respond with exactly: OK"

            response = await completion(
                model=model_string,
                messages=[{"role": "user", "content": test_prompt}],
                max_tokens=10,
                temperature=0,
                timeout=10,
            )

            # Calculate response time
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()

            if response and response.choices:
                result["status"] = "healthy"
                result["response_time"] = round(response_time, 2)
            else:
                result["status"] = "unhealthy"
                result["error"] = "No response received"

        except Exception as e:
            error_msg = str(e)

            # Categorize the error
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                result["status"] = "auth_error"
                result["error"] = "Invalid API key"
            elif "rate limit" in error_msg.lower():
                result["status"] = "rate_limit"
                result["error"] = "Rate limit exceeded"
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                result["status"] = "connection_error"
                if model.provider.lower() == "ollama":
                    result["error"] = "Ollama not running"
                else:
                    result["error"] = "Connection failed"
            elif "model" in error_msg.lower() and "not found" in error_msg.lower():
                result["status"] = "model_error"
                result["error"] = "Model not available"
            else:
                result["status"] = "error"
                result["error"] = error_msg[:50]  # Truncate long errors

        return result

    async def check_all_providers(self) -> list[dict]:
        """Check all configured providers"""
        models = ai_models()
        active_models = [m for m in models if m.active]

        if not active_models:
            console.print("[yellow]No active AI models configured[/yellow]")
            return []

        # Run checks concurrently
        tasks = [self.check_provider(model) for model in active_models]
        results = await asyncio.gather(*tasks)

        return results

    def display_results(self, results: list[dict]):
        """Display results in a formatted table"""
        table = Table(title="LLM Provider Health Check", box=box.ROUNDED)

        table.add_column("Provider", style="cyan", no_wrap=True)
        table.add_column("Model", style="magenta")
        table.add_column("Status", style="bold")
        table.add_column("Response Time", justify="right")
        table.add_column("API Key", style="dim")
        table.add_column("Error", style="red")

        # Status symbols
        status_symbols = {
            "healthy": "[green]✅ Healthy[/green]",
            "unhealthy": "[red]❌ Unhealthy[/red]",
            "no_api_key": "[yellow]🔑 No API Key[/yellow]",
            "auth_error": "[red]🔒 Auth Error[/red]",
            "rate_limit": "[yellow]⏱️ Rate Limited[/yellow]",
            "connection_error": "[red]🔌 Connection Error[/red]",
            "model_error": "[yellow]❓ Model Error[/yellow]",
            "error": "[red]❌ Error[/red]",
            "checking": "[yellow]🔄 Checking...[/yellow]",
        }

        for result in results:
            status_display = status_symbols.get(result["status"], result["status"])
            response_time = (
                f"{result['response_time']}s" if result["response_time"] else "-"
            )
            api_key_status = "✅" if result["has_api_key"] else "❌"
            error = result["error"] or "-"

            table.add_row(
                result["provider"],
                result["model"],
                status_display,
                response_time,
                api_key_status,
                error,
            )

        console.print(table)

        # Summary statistics
        total = len(results)
        healthy = sum(1 for r in results if r["status"] == "healthy")
        missing_keys = sum(1 for r in results if r["status"] == "no_api_key")
        errors = sum(1 for r in results if r["status"] not in ["healthy", "no_api_key"])

        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Total providers: {total}")
        console.print(f"  [green]Healthy: {healthy}[/green]")
        console.print(f"  [yellow]Missing API keys: {missing_keys}[/yellow]")
        console.print(f"  [red]Errors: {errors}[/red]")

        if missing_keys > 0:
            console.print("\n[yellow]ℹ️  To configure missing API keys, run:[/yellow]")  # noqa: RUF001 - Intentional info emoji
            console.print("    python tools/setup_api_keys.py")

        return healthy == total

    async def continuous_monitoring(self, interval: int = 30):
        """Continuously monitor provider health"""
        console.print(
            f"[bold]Starting continuous health monitoring (checking every {interval} seconds)[/bold]"
        )
        console.print("Press Ctrl+C to stop\n")

        try:
            while True:
                # Clear screen (optional)
                # console.clear()

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"\n[dim]Check performed at: {timestamp}[/dim]")

                results = await self.check_all_providers()
                self.display_results(results)

                # Wait for next check
                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Check health of LLM providers")
    parser.add_argument(
        "--monitor", "-m", action="store_true", help="Enable continuous monitoring"
    )
    parser.add_argument(
        "--interval",
        "-i",
        type=int,
        default=30,
        help="Monitoring interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output results as JSON"
    )

    args = parser.parse_args()

    checker = LLMHealthChecker()

    if args.monitor:
        await checker.continuous_monitoring(args.interval)
    else:
        console.print("[bold]🏥 LLM Provider Health Check[/bold]\n")

        with console.status("[yellow]Checking providers...[/yellow]", spinner="dots"):
            results = await checker.check_all_providers()

        if args.json:
            # Output as JSON for automation
            print(json.dumps(results, indent=2))
        else:
            # Display formatted table
            all_healthy = checker.display_results(results)

            # Exit with appropriate code
            sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    asyncio.run(main())
