"""
AssessmentHandler — declarative description of an assessment type (ADR 012, Phase A3).

Pre-deepening this was an ABC with four abstract methods — ``validate_submission``,
``preprocess``, ``get_prompt_template``, ``format_feedback`` — none of which had
external callers. Behaviour had already migrated:

- prompt construction → ``services.prompt_templates.generate_feedback_prompt``
- file extraction     → ``utils.file_handlers``
- per-source evidence → ``services.evidence`` adapters (LLM, signals, …)

What survives here is the **declaration**: what the type IS (type code, display
name, file constraints) and which evidence sources apply to it. ``evidence_sources``
is the seam — the default returns the canonical mix (one ``LLMEvidenceSource``
per active model x run, plus a ``SignalEvidenceSource``); subclasses or instance
overrides change the mix (e.g. a code type could prepend an AST-signal source
once we add that adapter to the lens family).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.services.evidence import EvidenceSource


@dataclass
class AssessmentHandler:
    """Slim declaration of an assessment type."""

    type_code: str
    display_name: str
    supports_file_upload: bool = True
    supports_text_input: bool = True
    allowed_extensions: tuple[str, ...] = ()
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    requires_external_service: bool = False
    external_service_name: str | None = None

    def evidence_sources(
        self,
        runner: Any,
        active_models: list[Any],
        settings: Any,
    ) -> list[EvidenceSource]:
        """The evidence adapters that produce CategoryScores for this type.

        Default: one ``LLMEvidenceSource`` per ``(active_model, run_number)``
        plus one ``SignalEvidenceSource``. Subclasses override to add or
        remove sources without touching the orchestrator.
        """
        from app.services.evidence import (
            LLMEvidenceSource,
            SignalEvidenceSource,
        )

        num_runs = getattr(settings, "num_runs", 1)
        sources: list[EvidenceSource] = [
            LLMEvidenceSource(runner, model, run_num + 1)
            for model in active_models
            for run_num in range(num_runs)
        ]
        sources.append(SignalEvidenceSource())
        return sources
