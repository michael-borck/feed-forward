"""Model providers for practice feedback.

One OpenAI-compatible chat client covers all three supported setups:

- **Local Ollama** — base_url http://localhost:11434/v1, no key
- **Remote Ollama** (e.g. a department GPU box behind a proxy) — any base
  URL plus a bearer key
- **BYOK** — any OpenAI-compatible endpoint (OpenAI, Anthropic's
  compatibility endpoint, OpenRouter, Groq, ...) with the student's own key

Configuration via arguments or environment:
FEEDFORWARD_PRACTICE_BASE_URL, FEEDFORWARD_PRACTICE_API_KEY,
FEEDFORWARD_PRACTICE_MODEL.
"""

import os
from dataclasses import dataclass

import httpx

DEFAULT_BASE_URL = "http://localhost:11434/v1"  # local Ollama
DEFAULT_TIMEOUT = 180.0


class ProviderError(RuntimeError):
    """The model endpoint could not produce a completion."""


@dataclass
class ProviderConfig:
    base_url: str = DEFAULT_BASE_URL
    api_key: str = ""
    model: str = ""

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        return cls(
            base_url=os.environ.get("FEEDFORWARD_PRACTICE_BASE_URL", DEFAULT_BASE_URL),
            api_key=os.environ.get("FEEDFORWARD_PRACTICE_API_KEY", ""),
            model=os.environ.get("FEEDFORWARD_PRACTICE_MODEL", ""),
        )

    def merged(self, overrides: dict | None) -> "ProviderConfig":
        overrides = overrides or {}
        return ProviderConfig(
            base_url=(overrides.get("base_url") or self.base_url).rstrip("/"),
            api_key=overrides.get("api_key") or self.api_key,
            model=overrides.get("model") or self.model,
        )


def _headers(config: ProviderConfig) -> dict:
    headers = {"Content-Type": "application/json"}
    if config.api_key:
        headers["Authorization"] = f"Bearer {config.api_key}"
    return headers


def list_models(config: ProviderConfig) -> list[str]:
    """Model ids from the endpoint's /models (works for Ollama and OpenAI)."""
    try:
        resp = httpx.get(
            f"{config.base_url}/models", headers=_headers(config), timeout=15.0
        )
        resp.raise_for_status()
        return [m["id"] for m in resp.json().get("data", [])]
    except httpx.HTTPError as e:
        raise ProviderError(f"Could not list models at {config.base_url}: {e}") from e


def chat(config: ProviderConfig, system: str, user: str) -> str:
    """One chat completion; returns the assistant text."""
    if not config.model:
        raise ProviderError("No model configured")
    payload = {
        "model": config.model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.4,
    }
    try:
        resp = httpx.post(
            f"{config.base_url}/chat/completions",
            headers=_headers(config),
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        detail = e.response.text[:300]
        raise ProviderError(
            f"Model endpoint returned {e.response.status_code}: {detail}"
        ) from e
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as e:
        raise ProviderError(f"Model call failed: {e}") from e
