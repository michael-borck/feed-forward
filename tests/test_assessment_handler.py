"""Tests for the slim AssessmentHandler (Phase A3 of #13)."""

from app.assessment.base import AssessmentHandler
from app.assessment.handlers import CODE, ESSAY, MATH, VIDEO
from app.assessment.registry import (
    DEFAULT_HANDLER,
    HANDLERS,
    get_assessment_handler,
)
from app.services.evidence import LLMEvidenceSource, SignalEvidenceSource

# ---- declarations ----

def test_essay_handler_constants():
    assert ESSAY.type_code == "essay"
    assert ESSAY.display_name == "Essay"
    assert ".pdf" in ESSAY.allowed_extensions and ".docx" in ESSAY.allowed_extensions
    assert ESSAY.supports_text_input is True
    assert ESSAY.supports_file_upload is True
    assert ESSAY.requires_external_service is False


def test_code_handler_constants():
    assert CODE.type_code == "code"
    assert ".py" in CODE.allowed_extensions and ".java" in CODE.allowed_extensions


def test_math_handler_constants():
    assert MATH.type_code == "math"
    assert ".tex" in MATH.allowed_extensions


def test_video_handler_text_input_disabled():
    assert VIDEO.supports_text_input is False
    assert VIDEO.requires_external_service is True
    assert VIDEO.external_service_name == "video_transcription"


# ---- registry ----

def test_registry_has_four_built_ins():
    assert set(HANDLERS) == {"essay", "code", "math", "video"}


def test_get_handler_unknown_returns_default():
    assert get_assessment_handler("nonsense") is DEFAULT_HANDLER


def test_get_handler_none_returns_default():
    assert get_assessment_handler(None) is DEFAULT_HANDLER


def test_get_handler_known_type():
    assert get_assessment_handler("code") is CODE
    assert get_assessment_handler("essay") is ESSAY


# ---- evidence_sources factory ----

class _Settings:
    num_runs = 2


def test_evidence_sources_default_mix():
    sources = ESSAY.evidence_sources(
        runner=object(), active_models=["m1", "m2"], settings=_Settings(),
    )
    # 2 models x 2 runs = 4 LLM sources + 1 SignalEvidenceSource = 5
    assert len(sources) == 5
    assert sum(1 for s in sources if isinstance(s, LLMEvidenceSource)) == 4
    assert sum(1 for s in sources if isinstance(s, SignalEvidenceSource)) == 1


def test_evidence_sources_no_models_returns_only_signals():
    sources = ESSAY.evidence_sources(
        runner=None, active_models=[], settings=_Settings(),
    )
    assert len(sources) == 1
    assert isinstance(sources[0], SignalEvidenceSource)


def test_evidence_sources_defaults_to_one_run_when_settings_missing_field():
    class S:
        pass
    sources = ESSAY.evidence_sources(runner=None, active_models=["m"], settings=S())
    assert sum(1 for s in sources if isinstance(s, LLMEvidenceSource)) == 1


def test_subclass_can_override_evidence_sources():
    """The seam is real — a subclass returning a different mix flows through unchanged."""

    class OnlyLLM(AssessmentHandler):
        def evidence_sources(self, runner, active_models, settings):
            return [LLMEvidenceSource(runner, m, 1) for m in active_models]

    h = OnlyLLM(type_code="custom", display_name="Custom")
    sources = h.evidence_sources(runner=None, active_models=["m1"], settings=_Settings())
    assert len(sources) == 1 and isinstance(sources[0], LLMEvidenceSource)
