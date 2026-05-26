"""
EvidenceSource seam (ADR 012, architectural deepening phase B).

Each adapter writes a ``model_run`` + per-category ``category_scores`` rows and
returns the new ``model_run`` id (or ``None`` on failure). The aggregator keys
off ``CategoryScore.model_run_id`` only, so every source kind blends through the
same aggregation pipeline.

Two adapters today (this is what makes the seam real, not theoretical):

- ``LLMEvidenceSource`` — one LLM run (model x run_number). Delegates to
  ``FeedbackGenerator._run_single_model`` for the LLM call itself; the seam
  doesn't try to re-home that 800-line module yet — it just gives the "one
  evidence source" concept a name.
- ``SignalEvidenceSource`` — synthetic Signal Engine run via
  ``signal_evidence.produce_signal_run`` (lens signals + scorer).

Adding a third evidence source (e.g. similarity checker, ML rubric) is an
"implement ``EvidenceSource``, add to the list" change — no edits to the
orchestrator.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


@dataclass
class EvidenceResult:
    """The outcome of one ``EvidenceSource.produce()`` call.

    ``kind`` is the source flavour (``"llm"`` / ``"signals"``); the orchestrator
    keys policy off it (e.g. "require ≥1 successful LLM run before aggregating").
    """

    kind: str
    model_run_id: int | None
    success: bool
    error: str | None = None


class EvidenceSource(ABC):
    """A source of category-score evidence for a draft."""

    kind: ClassVar[str]

    @abstractmethod
    async def produce(
        self, draft: Any, assignment: Any, settings: Any
    ) -> EvidenceResult:
        """Write a model_run + category_scores for the draft; return the outcome."""


class SignalEvidenceSource(EvidenceSource):
    """Synthetic Signal Engine run from lens-extracted signals (ADR 012 §4)."""

    kind: ClassVar[str] = "signals"

    async def produce(
        self, draft: Any, assignment: Any, settings: Any
    ) -> EvidenceResult:
        try:
            # Local imports keep this module independent of the rest of services
            # at import time (avoids any chance of circular import).
            from app.services import signal_evidence, signal_service

            loop = asyncio.get_event_loop()
            # Idempotent — extracts only if the background pass hasn't finished.
            await loop.run_in_executor(
                None, signal_service.extract_signals_for_draft, draft.id
            )
            run_id = await loop.run_in_executor(
                None, signal_evidence.produce_signal_run, draft.id
            )
            return EvidenceResult(
                kind=self.kind,
                model_run_id=run_id,
                success=run_id is not None,
            )
        except Exception as e:  # best-effort source — must never block LLM feedback
            logger.warning("Signal evidence failed for draft %s: %s", draft.id, e)
            return EvidenceResult(
                kind=self.kind, model_run_id=None, success=False, error=str(e)
            )


class LLMEvidenceSource(EvidenceSource):
    """One LLM run for a draft (model x run_number)."""

    kind: ClassVar[str] = "llm"

    def __init__(self, runner: Any, model: Any, run_number: int):
        # ``runner`` is a FeedbackGenerator instance — captures the LLM call
        # logic; the seam doesn't try to re-home that module yet.
        self._runner = runner
        self._model = model
        self._run_number = run_number

    async def produce(
        self, draft: Any, assignment: Any, settings: Any
    ) -> EvidenceResult:
        try:
            result = await self._runner._run_single_model(
                draft, assignment, settings, self._model, self._run_number
            )
            return EvidenceResult(
                kind=self.kind,
                model_run_id=result.model_run_id,
                success=bool(result.success),
                error=result.error_message,
            )
        except Exception as e:  # _run_single_model normally handles its own errors
            logger.error("LLM evidence source raised: %s", e)
            return EvidenceResult(
                kind=self.kind, model_run_id=None, success=False, error=str(e)
            )
