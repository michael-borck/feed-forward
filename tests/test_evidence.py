"""Tests for the EvidenceSource seam (Phase B deepening of #13)."""

import asyncio
from typing import ClassVar

from app.services.evidence import (
    EvidenceResult,
    EvidenceSource,
    LLMEvidenceSource,
    SignalEvidenceSource,
)

# ---------------------------------------------------------------------------
# A fake adapter — proves the seam is substitutable (the whole point).
# ---------------------------------------------------------------------------


class _FakeSource(EvidenceSource):
    kind: ClassVar[str] = "fake"

    def __init__(self, run_id, success=True, error=None):
        self._run_id = run_id
        self._success = success
        self._error = error
        self.calls = 0

    async def produce(self, draft, assignment, settings) -> EvidenceResult:
        self.calls += 1
        return EvidenceResult(
            kind=self.kind,
            model_run_id=self._run_id,
            success=self._success,
            error=self._error,
        )


def test_evidence_result_dataclass_defaults():
    r = EvidenceResult(kind="llm", model_run_id=5, success=True)
    assert r.kind == "llm" and r.model_run_id == 5 and r.error is None


def test_sources_iterate_uniformly():
    """The orchestrator just gathers ``produce`` from each source — no kind-specific branching."""
    a = _FakeSource(run_id=11)
    b = _FakeSource(run_id=22, success=False, error="boom")

    async def _all():
        return await asyncio.gather(
            *[s.produce(object(), object(), object()) for s in (a, b)]
        )

    results = asyncio.run(_all())
    assert [r.model_run_id for r in results] == [11, 22]
    assert [r.success for r in results] == [True, False]
    assert results[1].error == "boom"
    assert a.calls == 1 and b.calls == 1


# ---------------------------------------------------------------------------
# SignalEvidenceSource — wraps signal_evidence.produce_signal_run.
# ---------------------------------------------------------------------------


def _draft(did=42):
    return type("D", (), {"id": did})()


def test_signal_source_returns_failure_when_run_id_is_none(monkeypatch):
    from app.services import signal_evidence, signal_service

    monkeypatch.setattr(signal_service, "extract_signals_for_draft", lambda _did: True)
    monkeypatch.setattr(signal_evidence, "produce_signal_run", lambda _did: None)

    result = asyncio.run(SignalEvidenceSource().produce(_draft(), None, None))
    assert result.kind == "signals"
    assert result.success is False and result.model_run_id is None


def test_signal_source_propagates_run_id(monkeypatch):
    from app.services import signal_evidence, signal_service

    monkeypatch.setattr(signal_service, "extract_signals_for_draft", lambda _did: True)
    monkeypatch.setattr(signal_evidence, "produce_signal_run", lambda _did: 42)

    result = asyncio.run(SignalEvidenceSource().produce(_draft(), None, None))
    assert (
        result.success is True
        and result.model_run_id == 42
        and result.kind == "signals"
    )


def test_signal_source_swallows_exceptions(monkeypatch):
    """Best-effort: a crash in the analyser path must not raise out — it becomes a failed result."""
    from app.services import signal_evidence, signal_service

    monkeypatch.setattr(signal_service, "extract_signals_for_draft", lambda _did: True)

    def boom(_did):
        raise RuntimeError("analyser exploded")

    monkeypatch.setattr(signal_evidence, "produce_signal_run", boom)

    result = asyncio.run(SignalEvidenceSource().produce(_draft(), None, None))
    assert result.success is False
    assert result.error and "exploded" in result.error


# ---------------------------------------------------------------------------
# LLMEvidenceSource — wraps FeedbackGenerator._run_single_model.
# ---------------------------------------------------------------------------


class _FakeRunner:
    def __init__(self, *, run_id, success, error=None):
        self._next = (run_id, success, error)
        self.calls: list[tuple] = []

    async def _run_single_model(self, draft, assignment, settings, model, run_number):
        self.calls.append((model, run_number))
        from app.services.feedback_generator import FeedbackGenerationResult

        rid, ok, err = self._next
        return FeedbackGenerationResult(model_run_id=rid, success=ok, error_message=err)


def test_llm_source_propagates_run_and_kind():
    runner = _FakeRunner(run_id=7, success=True)
    src = LLMEvidenceSource(runner, model="m1", run_number=1)
    result = asyncio.run(src.produce(_draft(), None, None))
    assert result.kind == "llm" and result.success is True and result.model_run_id == 7
    assert runner.calls == [("m1", 1)]


def test_llm_source_failure_propagates_error():
    runner = _FakeRunner(run_id=8, success=False, error="rate limit")
    src = LLMEvidenceSource(runner, model="m1", run_number=2)
    result = asyncio.run(src.produce(_draft(), None, None))
    assert result.success is False and result.error == "rate limit"


def test_llm_source_catches_raised_exception():
    class Boom:
        async def _run_single_model(self, *a, **kw):
            raise RuntimeError("network down")

    src = LLMEvidenceSource(Boom(), model="m1", run_number=1)
    result = asyncio.run(src.produce(_draft(), None, None))
    assert result.success is False
    assert result.error and "network down" in result.error
