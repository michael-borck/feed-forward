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
from app.utils.db_query import by_id, count, where

logger = logging.getLogger(__name__)

SOURCE = "document-analyser"

# Numeric fields we lift out of the /text response, by section.
_NUMERIC_SECTIONS = ("text_metrics", "readability", "writing_quality")
_WORD_FIELDS = ("unique_words", "total_words", "vocabulary_richness")


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


def _already_extracted(draft_id: int) -> bool:
    return count(signals, draft_id=draft_id, source=SOURCE) > 0


def extract_signals_for_draft(draft_id: int) -> bool:
    """
    Extract and persist document-analyser signals for a draft.

    Returns True if signals were stored (or already present), False on any
    failure (draft missing, no content, analyser unreachable).
    """
    draft = by_id(drafts, draft_id)
    if draft is None:
        logger.warning("signal extraction: draft %s not found", draft_id)
        return False

    if _already_extracted(draft_id):
        logger.info("signal extraction: draft %s already has signals; skipping", draft_id)
        return True

    content = (getattr(draft, "content", "") or "").strip()
    if not content:
        logger.info("signal extraction: draft %s has no content to analyse", draft_id)
        return False

    response = analyser_client.analyse_text(content)
    if not response:
        logger.warning(
            "signal extraction: no response for draft %s (analyser down?)", draft_id
        )
        return False

    flat = _flatten_text_response(response)

    # Best-effort sentiment signals (additive; degrades gracefully if unavailable).
    sentiment = analyser_client.analyse_sentiment(content)
    if sentiment:
        flat.update(_flatten_sentiment_response(sentiment))

    if not flat:
        logger.warning("signal extraction: no numeric signals in response for draft %s", draft_id)
        return False

    now = datetime.now().isoformat()
    for name, value in flat.items():
        signals.insert(
            Signal(
                draft_id=draft_id,
                source=SOURCE,
                name=name,
                value=value,
                raw="",
                created_at=now,
            )
        )

    logger.info("signal extraction: stored %d signals for draft %s", len(flat), draft_id)
    return True


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
