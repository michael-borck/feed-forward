"""
HTTP client for the lens analyser family (ADR 012).

Analysers run as sidecar services over HTTP so their heavy/ML dependencies never
enter FeedForward's process. This client is deliberately thin and degrades
gracefully: if an analyser is unreachable or errors, callers get ``None`` and the
rest of the pipeline carries on.

Endpoint choice (verified 2026-05-24): we POST already-extracted text to
``/text`` rather than uploading the file to ``/analyse``. FeedForward already
extracts text in ``file_handlers.py``, and ``/text`` returns the richer signal
set (readability + writing quality + vocabulary + NER).
"""

import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_URL = "http://127.0.0.1:8000"
# First request after a cold start loads NLP models; keep the timeout generous.
_DEFAULT_TIMEOUT = float(os.environ.get("DOCUMENT_ANALYSER_TIMEOUT", "60"))


def _base_url() -> str:
    """Base URL of the document-analyser service (override with DOCUMENT_ANALYSER_URL)."""
    return os.environ.get("DOCUMENT_ANALYSER_URL", _DEFAULT_URL).rstrip("/")


def health(timeout: float = 3.0) -> bool:
    """Return True if the document-analyser service answers /health with 200."""
    try:
        resp = requests.get(f"{_base_url()}/health", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException as e:
        logger.warning("document-analyser /health unreachable: %s", e)
        return False


def analyse_text(
    text: str, timeout: float = _DEFAULT_TIMEOUT
) -> Optional[dict[str, Any]]:
    """
    Analyse already-extracted text via document-analyser ``POST /text``.

    Returns the parsed JSON response, or ``None`` on any failure (service down,
    HTTP error, invalid JSON) — callers must treat ``None`` as "no signals".
    """
    if not text or not text.strip():
        return None
    try:
        resp = requests.post(
            f"{_base_url()}/text",
            json={"text": text},
            timeout=timeout,
        )
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result
    except requests.RequestException as e:
        logger.warning("document-analyser /text request failed: %s", e)
        return None
    except ValueError as e:  # JSON decode error
        logger.warning("document-analyser /text returned invalid JSON: %s", e)
        return None
