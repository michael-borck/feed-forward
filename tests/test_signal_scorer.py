"""Tests for the signal scorer (transforms + per-category scoring)."""

import json
from types import SimpleNamespace

from app.services import signal_scorer


def _rule(name, transform, weight=1.0, enabled=True):
    return SimpleNamespace(
        signal_name=name, transform=transform, weight=weight, enabled=enabled
    )


# ---- apply_transform: band ----

def test_band_selects_matching_band():
    t = {"type": "band", "bands": [[None, 30, 40], [30, 50, 70], [50, None, 90]]}
    assert signal_scorer.apply_transform(20, t) == 40.0
    assert signal_scorer.apply_transform(40, t) == 70.0
    assert signal_scorer.apply_transform(60, t) == 90.0
    assert signal_scorer.apply_transform(30, t) == 70.0  # hi is exclusive


def test_band_no_match_returns_none():
    t = {"type": "band", "bands": [[30, 50, 70]]}
    assert signal_scorer.apply_transform(10, t) is None
    assert signal_scorer.apply_transform(80, t) is None


# ---- apply_transform: linear ----

def test_linear_maps_and_clamps():
    t = {"type": "linear", "in": [0, 100], "out": [0, 100]}
    assert signal_scorer.apply_transform(50, t) == 50.0
    assert signal_scorer.apply_transform(-10, t) == 0.0
    assert signal_scorer.apply_transform(150, t) == 100.0


def test_linear_inverted_mapping():
    # "more is worse" signal (e.g. passive voice %): 0 -> 100, 40 -> 0
    t = {"type": "linear", "in": [0, 40], "out": [100, 0]}
    assert signal_scorer.apply_transform(0, t) == 100.0
    assert signal_scorer.apply_transform(40, t) == 0.0
    assert signal_scorer.apply_transform(20, t) == 50.0
    assert signal_scorer.apply_transform(60, t) == 0.0  # clamp


def test_unknown_or_empty_transform_returns_none():
    assert signal_scorer.apply_transform(50, {"type": "nope"}) is None
    assert signal_scorer.apply_transform(50, {}) is None


# ---- score_category ----

def test_score_category_weighted_average():
    rules = [
        _rule("flesch", {"type": "linear", "in": [0, 100], "out": [0, 100]}, weight=3),
        _rule("vocab", {"type": "linear", "in": [0, 100], "out": [0, 100]}, weight=1),
    ]
    score, conf = signal_scorer.score_category(rules, {"flesch": 40, "vocab": 80})
    assert score == (40 * 3 + 80 * 1) / 4  # 50.0
    assert conf == 1.0


def test_score_category_missing_signal_lowers_confidence():
    rules = [
        _rule("flesch", {"type": "linear", "in": [0, 100], "out": [0, 100]}),
        _rule("vocab", {"type": "linear", "in": [0, 100], "out": [0, 100]}),
    ]
    score, conf = signal_scorer.score_category(rules, {"flesch": 60})  # vocab absent
    assert score == 60.0
    assert conf == 0.5


def test_score_category_disabled_rule_ignored():
    rules = [
        _rule("flesch", {"type": "linear", "in": [0, 100], "out": [0, 100]}),
        _rule("vocab", {"type": "linear", "in": [0, 100], "out": [0, 100]}, enabled=False),
    ]
    score, conf = signal_scorer.score_category(rules, {"flesch": 70, "vocab": 90})
    assert score == 70.0
    assert conf == 1.0


def test_score_category_no_rule_fires_returns_none():
    rules = [_rule("missing", {"type": "linear", "in": [0, 100], "out": [0, 100]})]
    assert signal_scorer.score_category(rules, {"other": 50}) == (None, 0.0)


# ---- estimate_scores_for_draft (temp DB) ----

def test_estimate_scores_for_draft():
    from app.models.signal_rules import SignalRule, signal_rules
    from app.models.signals import Signal, signals

    did = 42
    signals.insert(Signal(draft_id=did, source="document-analyser",
                          name="flesch_score", value=60.0, raw="", created_at="t"))
    signals.insert(Signal(draft_id=did, source="document-analyser",
                          name="vocabulary_richness", value=80.0, raw="", created_at="t"))
    lin = json.dumps({"type": "linear", "in": [0, 100], "out": [0, 100]})
    signal_rules.insert(SignalRule(rubric_category_id=1, signal_source="document-analyser",
                                   signal_name="flesch_score", transform=lin,
                                   weight=1.0, enabled=True))
    signal_rules.insert(SignalRule(rubric_category_id=2, signal_source="document-analyser",
                                   signal_name="vocabulary_richness", transform=lin,
                                   weight=1.0, enabled=True))

    est = signal_scorer.estimate_scores_for_draft(did)
    assert est[1]["score"] == 60.0
    assert est[1]["confidence"] == 1.0
    assert est[2]["score"] == 80.0


# ---- auto-match (suggest_rules_for_category / category_estimates) ----

def test_suggest_matches_keywords():
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Clarity")] == ["flesch_score"]
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Structure & Organisation")] == [
        "paragraph_count", "sentence_variety"]
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Vocabulary")] == ["vocabulary_richness"]
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Writing style")] == [
        "passive_voice_percentage", "transition_words"]


def test_suggest_no_match_returns_empty():
    assert signal_scorer.suggest_rules_for_category("Argument depth") == []
    assert signal_scorer.suggest_rules_for_category("") == []


def test_suggest_matches_tone_to_sentiment():
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Tone")] == [
        "sentiment_positive"]
    assert [r.signal_name for r in signal_scorer.suggest_rules_for_category("Engagement")] == [
        "sentiment_positive"]


def test_category_estimates_auto_match():
    from app.models.signals import Signal, signals

    did = 7
    signals.insert(Signal(draft_id=did, source="document-analyser",
                          name="flesch_score", value=45.0, raw="", created_at="t"))
    cats = [SimpleNamespace(id=1, name="Clarity"), SimpleNamespace(id=2, name="Argument depth")]
    est = signal_scorer.category_estimates(did, cats)
    assert est[1]["suggested"] is True
    assert est[1]["score"] == 72.0  # flesch 45 -> band [30,50) -> 72
    assert 2 not in est  # no signal maps to "Argument depth"


def test_category_estimates_prefers_persisted():
    from app.models.signal_rules import SignalRule, signal_rules
    from app.models.signals import Signal, signals

    did = 8
    signals.insert(Signal(draft_id=did, source="document-analyser",
                          name="flesch_score", value=45.0, raw="", created_at="t"))
    signal_rules.insert(SignalRule(
        rubric_category_id=1, signal_source="document-analyser", signal_name="flesch_score",
        transform=json.dumps({"type": "linear", "in": [0, 100], "out": [0, 100]}),
        weight=1.0, enabled=True))
    est = signal_scorer.category_estimates(did, [SimpleNamespace(id=1, name="Clarity")])
    assert est[1]["suggested"] is False
    assert est[1]["score"] == 45.0  # persisted linear (45) overrides suggested band (72)
