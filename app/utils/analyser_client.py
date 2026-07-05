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

import contextlib
import logging
import os
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_DEFAULT_URL = "http://127.0.0.1:8000"
_DEFAULT_CODE_URL = "http://127.0.0.1:8004"  # lens contract port for code-analyser
_DEFAULT_CITE_URL = "http://127.0.0.1:3001"  # cite-sight server default port
# First request after a cold start loads NLP models; keep the timeout generous.
_DEFAULT_TIMEOUT = float(os.environ.get("DOCUMENT_ANALYSER_TIMEOUT", "60"))
# Reference verification hits Crossref/OpenAlex with polite rate limiting
# (~0.4s per reference plus URL checks) — needs much more headroom.
_CITE_TIMEOUT = float(os.environ.get("CITE_SIGHT_TIMEOUT", "180"))


def _base_url() -> str:
    """Base URL of the document-analyser service (override with DOCUMENT_ANALYSER_URL)."""
    return os.environ.get("DOCUMENT_ANALYSER_URL", _DEFAULT_URL).rstrip("/")


def _code_base_url() -> str:
    """Base URL of the code-analyser service (override with CODE_ANALYSER_URL)."""
    return os.environ.get("CODE_ANALYSER_URL", _DEFAULT_CODE_URL).rstrip("/")


def _cite_base_url() -> str:
    """Base URL of the cite-sight server (override with CITE_SIGHT_URL)."""
    return os.environ.get("CITE_SIGHT_URL", _DEFAULT_CITE_URL).rstrip("/")


def cite_verification_enabled() -> bool:
    """Whether cite-sight should verify references against Crossref/OpenAlex
    and check URLs (network calls). Disable with CITE_SIGHT_VERIFY=false for
    fast, fully-local extraction (format + cross-reference checks only)."""
    return os.environ.get("CITE_SIGHT_VERIFY", "true").lower() != "false"


def health(timeout: float = 3.0) -> bool:
    """Return True if the document-analyser service answers /health with 200."""
    try:
        resp = requests.get(f"{_base_url()}/health", timeout=timeout)
        return resp.status_code == 200
    except requests.RequestException as e:
        logger.warning("document-analyser /health unreachable: %s", e)
        return False


# The lens analysers FeedForward talks to, in the order they appear on the
# admin health card. Each entry resolves its base URL the same way the
# analyse_* calls do, so the card reports the URL actually used at runtime.
_SERVICES: tuple[tuple[str, Any, str], ...] = (
    ("document-analyser", _base_url, "essay readability, structure, sentiment"),
    ("code-analyser", _code_base_url, "code complexity, lint, docstrings"),
    ("cite-sight", _cite_base_url, "reference integrity, citation format"),
)


def service_health(timeout: float = 3.0) -> list[dict[str, Any]]:
    """Probe every lens analyser's /health and report status for the admin card.

    Each result is ``{name, role, url, ok, version, error}``. Never raises —
    an unreachable service is reported as ``ok: False`` with the error text.
    """
    results: list[dict[str, Any]] = []
    for name, url_fn, role in _SERVICES:
        base = url_fn()
        entry: dict[str, Any] = {
            "name": name,
            "role": role,
            "url": base,
            "ok": False,
            "version": None,
            "error": None,
        }
        try:
            resp = requests.get(f"{base}/health", timeout=timeout)
            entry["ok"] = resp.status_code == 200
            if entry["ok"]:
                with contextlib.suppress(ValueError):
                    entry["version"] = resp.json().get("version")
            else:
                entry["error"] = f"HTTP {resp.status_code}"
        except requests.RequestException as e:
            entry["error"] = str(e)
        results.append(entry)
    return results


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


def analyse_code(
    content: str, filename: str, timeout: float = _DEFAULT_TIMEOUT
) -> Optional[dict[str, Any]]:
    """
    Analyse code via code-analyser ``POST /analyse`` (multipart upload).

    ``filename`` matters: code-analyser detects the language from its extension.
    Returns the parsed JSON response, or ``None`` on any failure (service down,
    unsupported language, HTTP error) — callers must treat ``None`` as "no signals".
    """
    if not content or not content.strip():
        return None
    try:
        resp = requests.post(
            f"{_code_base_url()}/analyse",
            files={"file": (filename, content.encode("utf-8"), "text/plain")},
            timeout=timeout,
        )
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result
    except requests.RequestException as e:
        logger.warning("code-analyser /analyse request failed: %s", e)
        return None
    except ValueError as e:  # JSON decode error
        logger.warning("code-analyser /analyse returned invalid JSON: %s", e)
        return None


def analyse_citations(
    text: str,
    verify: Optional[bool] = None,
    timeout: float = _CITE_TIMEOUT,
) -> Optional[dict[str, Any]]:
    """
    Citation/reference analysis via cite-sight ``POST /analyse`` (lens contract).

    ``verify`` controls the network verification tier (Crossref/OpenAlex DOI
    lookup + URL liveness); defaults to :func:`cite_verification_enabled`.
    In-text/bibliography cross-referencing is local and always on.

    Returns the parsed JSON response, or ``None`` on any failure — callers must
    treat ``None`` as "no signals".
    """
    if not text or not text.strip():
        return None
    if verify is None:
        verify = cite_verification_enabled()
    flag = "true" if verify else "false"
    try:
        resp = requests.post(
            f"{_cite_base_url()}/analyse",
            files={"file": ("submission.txt", text.encode("utf-8"), "text/plain")},
            data={
                "citationStyle": "auto",
                "checkUrls": flag,
                "checkDoi": flag,
                "checkInText": "true",
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result
    except requests.RequestException as e:
        logger.warning("cite-sight /analyse request failed: %s", e)
        return None
    except ValueError as e:  # JSON decode error
        logger.warning("cite-sight /analyse returned invalid JSON: %s", e)
        return None


def analyse_sentiment(
    text: str, timeout: float = _DEFAULT_TIMEOUT
) -> Optional[dict[str, Any]]:
    """
    Document-level sentiment via document-analyser ``POST /semantic/sentiment``.

    Returns the parsed JSON (with ``document_sentiment``), or ``None`` on failure.
    The server degrades to a valid neutral result when its ``[nlp]`` extra is
    absent, so this returns data (neutral) rather than erroring in that case.
    """
    if not text or not text.strip():
        return None
    try:
        resp = requests.post(
            f"{_base_url()}/semantic/sentiment",
            json={"text": text},
            timeout=timeout,
        )
        resp.raise_for_status()
        result: dict[str, Any] = resp.json()
        return result
    except requests.RequestException as e:
        logger.warning("document-analyser /semantic/sentiment request failed: %s", e)
        return None
    except ValueError as e:  # JSON decode error
        logger.warning("document-analyser /semantic/sentiment invalid JSON: %s", e)
        return None
