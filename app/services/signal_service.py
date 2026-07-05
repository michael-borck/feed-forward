"""
Signal extraction service (ADR 012 / SIGNAL_INTEGRATION_PLAN.md, phase S1).

Reads a draft's content, asks the document-analyser sidecar for signals via
``/text``, flattens the response into ``signals`` rows. Read-only: this does NOT
score, aggregate, or touch the feedback generator.

Run in the background at submission time, while ``draft.content`` still exists
(content is cleared after feedback per ADR 002 / 008).
"""

import logging
import threading
from datetime import datetime
from typing import Any

from app.models.feedback import drafts
from app.models.signals import Signal, signals
from app.utils import analyser_client
from app.utils.db_query import by_id, count, first, where

logger = logging.getLogger(__name__)

SOURCE = "document-analyser"
SOURCE_CODE = "code-analyser"
SOURCE_CITATIONS = "cite-sight"

# Numeric fields we lift out of the /text response, by section.
_NUMERIC_SECTIONS = ("text_metrics", "readability", "writing_quality")
_WORD_FIELDS = ("unique_words", "total_words", "vocabulary_richness")

# Fallback filename extensions for text-only code submissions, sniffed from
# content (code-analyser detects language from the extension). Order matters.
_CODE_SNIFF: tuple[tuple[str, str], ...] = (
    ("def ", ".py"),
    ("import ", ".py"),
    ("function ", ".js"),
    ("const ", ".js"),
    ("SELECT ", ".sql"),
    ("<html", ".html"),
)


def _flatten_text_response(response: dict[str, Any]) -> dict[str, float]:
    """Pull numeric signals out of document-analyser's /text response."""
    analysis = response.get("analysis", {})
    flat: dict[str, float] = {}

    for section in _NUMERIC_SECTIONS:
        for name, value in analysis.get(section, {}).items():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                flat[name] = float(value)

    word_analysis = analysis.get("word_analysis", {})
    for name in _WORD_FIELDS:
        value = word_analysis.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            flat[name] = float(value)

    return flat


def _flatten_sentiment_response(response: dict[str, Any]) -> dict[str, float]:
    """Pull document-level sentiment signals out of /semantic/sentiment."""
    doc = response.get("document_sentiment") or {}
    flat: dict[str, float] = {}
    for name in ("positive", "negative", "neutral", "compound"):
        value = doc.get(name)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            flat[f"sentiment_{name}"] = float(value)
    return flat


def _flatten_code_response(response: dict[str, Any]) -> dict[str, float]:
    """Pull numeric signals out of code-analyser's /analyse response.

    Uses the first analysed file's metrics (FeedForward code submissions are a
    single file), plus the cross-file file count. Booleans that carry assessment
    meaning (``syntax_valid``, ``has_main_guard``) are kept as 0/1 signals.
    """
    files = response.get("files") or []
    metrics = (files[0].get("metrics") or {}) if files else {}
    flat: dict[str, float] = {}

    for name, value in metrics.items():
        if name in ("syntax_valid", "has_main_guard"):
            flat[name] = 1.0 if value else 0.0
        elif isinstance(value, bool):
            continue
        elif isinstance(value, (int, float)):
            flat[name] = float(value)

    file_count = response.get("file_count")
    if isinstance(file_count, (int, float)):
        flat["file_count"] = float(file_count)
    return flat


def _code_filename(draft: Any) -> str:
    """Filename to present to code-analyser (its language detection is by extension).

    Prefer the uploaded file's original name; for text-only submissions, sniff
    the content for a likely extension (defaulting to ``.py``).
    """
    from app.models.assessment import submission_files

    upload = first(submission_files, draft_id=draft.id)
    original = getattr(upload, "original_filename", "") if upload else ""
    if original and "." in original:
        return original

    content = getattr(draft, "content", "") or ""
    for marker, ext in _CODE_SNIFF:
        if marker in content:
            return f"submission{ext}"
    return "submission.py"


def _flatten_citation_response(response: dict[str, Any]) -> dict[str, float]:
    """Pull reference-integrity signals out of cite-sight's /analyse response.

    Verification-dependent signals (verified/suspicious/not-found counts and
    the integrity percentage) are only emitted when at least one reference was
    actually checked against an external source — with verification disabled
    every reference reports ``format_only`` and a zero verified-count would
    read as "all citations bogus".
    """
    refs = response.get("references") or {}
    flat: dict[str, float] = {}

    total = refs.get("totalReferences")
    if not isinstance(total, (int, float)):
        return flat
    flat["total_references"] = float(total)

    cross = refs.get("crossReference") or {}
    flat["orphaned_reference_count"] = float(
        len(cross.get("unmatchedBibliography") or [])
    )
    flat["uncited_reference_count"] = float(len(cross.get("unmatchedInText") or []))

    verifications = refs.get("verifications") or []
    flat["citation_format_issue_count"] = float(
        sum(len(v.get("formatIssues") or []) for v in verifications)
    )

    statuses = {v.get("status") for v in verifications}
    was_verified = bool(statuses - {"format_only", None})
    if was_verified and total > 0:
        verified = float(refs.get("verifiedCount") or 0)
        flat["verified_reference_count"] = verified
        flat["suspicious_reference_count"] = float(refs.get("suspiciousCount") or 0)
        flat["not_found_reference_count"] = float(refs.get("notFoundCount") or 0)
        flat["broken_url_count"] = float(refs.get("brokenUrlCount") or 0)
        flat["citation_integrity_pct"] = round(100.0 * verified / total, 1)

    return flat


def _already_extracted(draft_id: int, source: str) -> bool:
    return count(signals, draft_id=draft_id, source=source) > 0


def _document_signals(draft: Any) -> dict[str, float]:
    """Prose signals: document-analyser /text plus best-effort sentiment."""
    response = analyser_client.analyse_text(draft.content)
    if not response:
        return {}
    flat = _flatten_text_response(response)
    sentiment = analyser_client.analyse_sentiment(draft.content)
    if sentiment:
        flat.update(_flatten_sentiment_response(sentiment))
    return flat


def _citation_signals(draft: Any) -> dict[str, float]:
    response = analyser_client.analyse_citations(draft.content)
    return _flatten_citation_response(response) if response else {}


def _code_signals(draft: Any) -> dict[str, float]:
    response = analyser_client.analyse_code(draft.content, _code_filename(draft))
    return _flatten_code_response(response) if response else {}


def _sources_for_type(type_code: str) -> list[tuple[str, Any]]:
    """The lens sources that apply to an assessment type, as (source, extractor)."""
    if type_code == "code":
        return [(SOURCE_CODE, _code_signals)]
    # Default: prose analysis + reference integrity (essay and any type
    # without a dedicated analyser).
    return [(SOURCE, _document_signals), (SOURCE_CITATIONS, _citation_signals)]


def extract_signals_for_draft(draft_id: int) -> bool:
    """
    Extract and persist lens signals for a draft. The assignment's assessment
    type picks the sources: essay → document-analyser + cite-sight, code →
    code-analyser. Each source is idempotent and degrades independently — one
    analyser being down doesn't block the others' signals.

    Returns True if any source's signals are stored (or already present),
    False otherwise (draft missing, no content, all analysers unreachable).
    """
    from app.assessment.registry import type_code_for_assignment

    draft = by_id(drafts, draft_id)
    if draft is None:
        logger.warning("signal extraction: draft %s not found", draft_id)
        return False

    content = (getattr(draft, "content", "") or "").strip()
    if not content:
        logger.info("signal extraction: draft %s has no content to analyse", draft_id)
        return False

    type_code = type_code_for_assignment(draft.assignment_id)
    now = datetime.now().isoformat()
    stored_any = False

    for source, extractor in _sources_for_type(type_code):
        if _already_extracted(draft_id, source):
            logger.info(
                "signal extraction: draft %s already has %s signals; skipping",
                draft_id,
                source,
            )
            stored_any = True
            continue

        flat = extractor(draft)
        if not flat:
            logger.warning(
                "signal extraction: no %s signals for draft %s (analyser down "
                "or unsupported submission?)",
                source,
                draft_id,
            )
            continue

        for name, value in flat.items():
            signals.insert(
                Signal(
                    draft_id=draft_id,
                    source=source,
                    name=name,
                    value=value,
                    raw="",
                    created_at=now,
                )
            )
        logger.info(
            "signal extraction: stored %d %s signals for draft %s",
            len(flat),
            source,
            draft_id,
        )
        stored_any = True

    return stored_any


def get_signals_for_draft(draft_id: int) -> list[Signal]:
    """Return stored signals for a draft (read side, used by the instructor view)."""
    return where(signals, draft_id=draft_id)


def queue_signal_extraction(draft_id: int) -> None:
    """Fire-and-forget signal extraction in a daemon thread (non-blocking)."""
    threading.Thread(
        target=extract_signals_for_draft,
        args=(draft_id,),
        daemon=True,
    ).start()
