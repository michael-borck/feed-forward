"""
Signal scorer (ADR 012 / SIGNAL_INTEGRATION_PLAN.md, phase S2).

Maps stored lens signals to per-rubric-category 0-100 estimates via configurable
``signal_rules``. Pure and deterministic; no network, no LLM. These estimates are
*evidence the instructor reviews and adjusts*, never a final mark.

Transforms (the ``transform`` JSON on a rule):
- ``{"type": "band", "bands": [[lo, hi, score], ...]}`` — first band whose
  ``lo <= value < hi`` wins (``null`` bound = open-ended). No band -> no contribution.
- ``{"type": "linear", "in": [lo, hi], "out": [olo, ohi]}`` — linear map of value
  from the input range to the output range, clamped to the output range.
"""

import json
import logging
from typing import Any, Optional

from app.utils.db_query import where

logger = logging.getLogger(__name__)


def apply_transform(value: float, transform: dict[str, Any]) -> Optional[float]:
    """Map a raw signal value to a 0-100 contribution, or None if it can't apply."""
    ttype = transform.get("type")

    if ttype == "band":
        for band in transform.get("bands", []):
            try:
                lo, hi, score = band
            except (ValueError, TypeError):
                continue
            if (lo is None or value >= lo) and (hi is None or value < hi):
                return float(score)
        return None

    if ttype == "linear":
        in_lo, in_hi = transform.get("in", [0.0, 100.0])
        out_lo, out_hi = transform.get("out", [0.0, 100.0])
        if in_hi == in_lo:
            return float(out_lo)
        frac = (value - in_lo) / (in_hi - in_lo)
        frac = max(0.0, min(1.0, frac))  # clamp into the input range
        return float(out_lo + frac * (out_hi - out_lo))

    return None


def _parse_transform(rule: Any) -> dict[str, Any]:
    raw = getattr(rule, "transform", None)
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw) if raw else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def score_category(
    rules: list[Any], signals_by_name: dict[str, float]
) -> tuple[Optional[float], float]:
    """
    Combine a category's rules + the draft's signals into one estimate.

    Returns ``(score, confidence)`` where score is a weighted 0-100 value (or
    None if no rule produced a contribution) and confidence is coverage: the
    fraction of enabled rules that actually fired.
    """
    weighted_sum = 0.0
    total_weight = 0.0
    considered = 0
    fired = 0

    for rule in rules:
        if not getattr(rule, "enabled", True):
            continue
        considered += 1
        value = signals_by_name.get(getattr(rule, "signal_name", None))
        if value is None:
            continue
        contribution = apply_transform(value, _parse_transform(rule))
        if contribution is None:
            continue
        weight = float(getattr(rule, "weight", 1.0) or 1.0)
        weighted_sum += contribution * weight
        total_weight += weight
        fired += 1

    if total_weight == 0:
        return None, 0.0
    score = weighted_sum / total_weight
    confidence = fired / considered if considered else 0.0
    return score, confidence


def estimate_scores_for_draft(draft_id: int) -> dict[int, dict[str, float]]:
    """
    Estimate per-rubric-category scores for a draft from its stored signals.

    Returns ``{rubric_category_id: {"score": float, "confidence": float}}`` for
    every category that has at least one rule that fired.
    """
    from app.models.signal_rules import signal_rules
    from app.models.signals import signals

    signals_by_name = {s.name: s.value for s in where(signals, draft_id=draft_id)}

    rules_by_category: dict[int, list[Any]] = {}
    for rule in signal_rules():
        rules_by_category.setdefault(rule.rubric_category_id, []).append(rule)

    estimates: dict[int, dict[str, float]] = {}
    for category_id, rules in rules_by_category.items():
        score, confidence = score_category(rules, signals_by_name)
        if score is not None:
            estimates[category_id] = {
                "score": round(score, 1),
                "confidence": round(confidence, 2),
            }
    return estimates


# ---------------------------------------------------------------------------
# Auto-match: propose signal->category rules from a rubric category's name.
# Instructors confirm / override these (ADR 012 "instructor-controlled").
# ---------------------------------------------------------------------------

# Keyword(s) in a rubric category name -> (signal_name, transform) suggestions.
_SUGGESTIONS: list[tuple[tuple[str, ...], list[tuple[str, dict[str, Any]]]]] = [
    (("clarity", "readab", "clear"),
     [("flesch_score",
       {"type": "band", "bands": [[None, 30, 55], [30, 50, 72], [50, 70, 85], [70, None, 92]]})]),
    (("structure", "organi", "cohesion", "coheren"),
     [("paragraph_count",
       {"type": "band", "bands": [[None, 3, 50], [3, 5, 75], [5, None, 90]]}),
      ("sentence_variety", {"type": "linear", "in": [0, 100], "out": [0, 100]})]),
    (("vocab", "lexic", "word choice", "diction"),
     [("vocabulary_richness", {"type": "linear", "in": [0, 100], "out": [0, 100]})]),
    (("style", "writing", "grammar", "mechanic", "expression"),
     [("passive_voice_percentage", {"type": "linear", "in": [0, 40], "out": [100, 0]}),
      ("transition_words", {"type": "linear", "in": [0, 60], "out": [40, 100]})]),
    (("tone", "sentiment", "engagement", "voice"),
     [("sentiment_positive", {"type": "linear", "in": [0, 1], "out": [0, 100]})]),
]


def suggest_rules_for_category(category_name: str) -> list[Any]:
    """Auto-matched (unsaved) rules for a rubric category, by name keywords.

    Returns rule-shaped objects (``.signal_name``/``.transform``/``.weight``/
    ``.enabled``) the scorer can consume directly; empty if nothing matches
    (e.g. "Argument depth" — a category signals can't assess on the surface).
    """
    from types import SimpleNamespace

    name = (category_name or "").lower()
    for keywords, sigs in _SUGGESTIONS:
        if any(k in name for k in keywords):
            return [
                SimpleNamespace(
                    signal_source="document-analyser",
                    signal_name=signal_name,
                    transform=transform,
                    weight=1.0,
                    enabled=True,
                )
                for signal_name, transform in sigs
            ]
    return []


def category_estimates(draft_id: int, categories: Any) -> dict[int, dict[str, Any]]:
    """
    Per-category estimates for a draft. Prefers persisted ``signal_rules`` for a
    category; otherwise falls back to auto-matched suggestions.

    ``categories`` is any iterable of objects with ``.id`` and ``.name``.
    Returns ``{category_id: {"score", "confidence", "suggested"}}`` for every
    category that produced an estimate.
    """
    from app.models.signal_rules import signal_rules
    from app.models.signals import signals

    signals_by_name = {s.name: s.value for s in where(signals, draft_id=draft_id)}

    persisted: dict[int, list[Any]] = {}
    for rule in signal_rules():
        persisted.setdefault(rule.rubric_category_id, []).append(rule)

    out: dict[int, dict[str, Any]] = {}
    for category in categories:
        is_suggested = category.id not in persisted
        rules = persisted.get(category.id) or suggest_rules_for_category(category.name)
        score, confidence = score_category(rules, signals_by_name)
        if score is not None:
            out[category.id] = {
                "score": round(score, 1),
                "confidence": round(confidence, 2),
                "suggested": is_suggested,
            }
    return out
