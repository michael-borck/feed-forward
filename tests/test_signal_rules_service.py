"""Tests for instructor signal-rule management (confirm/override)."""

from app.services import signal_rules_service


def _id(res):
    return res.id if hasattr(res, "id") else res


def _seed_rubric(assignment_id, names=("Clarity", "Argument depth")):
    from app.models.assignment import Rubric, RubricCategory, rubric_categories, rubrics

    rid = _id(
        rubrics.insert(
            Rubric(
                assignment_id=assignment_id,
                assessment_type_id=1,
                type_specific_criteria="",
            )
        )
    )
    cats = {}
    for n in names:
        cats[n] = _id(
            rubric_categories.insert(
                RubricCategory(rubric_id=rid, name=n, description="", weight=1.0)
            )
        )
    return cats


def test_rules_view_shows_suggestions_when_none_persisted():
    _seed_rubric(1)
    view = signal_rules_service.rules_view_for_assignment(1)
    by_name = {e["category"].name: e for e in view}
    clarity = by_name["Clarity"]
    assert [r["signal_name"] for r in clarity["rules"]] == ["flesch_score"]
    assert clarity["rules"][0]["persisted"] is False
    assert by_name["Argument depth"]["rules"] == []  # no signal maps here


def test_save_persists_suggestions_and_is_idempotent():
    from app.models.signal_rules import signal_rules

    cats = _seed_rubric(2)
    fields = {f"en_{cats['Clarity']}_flesch_score": "on"}
    n = signal_rules_service.save_rules_for_assignment(2, fields)
    assert n == 1  # only Clarity has a rule
    rules = [r for r in signal_rules() if r.rubric_category_id == cats["Clarity"]]
    assert len(rules) == 1
    assert rules[0].signal_name == "flesch_score"
    assert bool(rules[0].enabled) is True

    signal_rules_service.save_rules_for_assignment(2, fields)  # again
    rules2 = [r for r in signal_rules() if r.rubric_category_id == cats["Clarity"]]
    assert len(rules2) == 1  # updated, not duplicated


def test_save_applies_weight_and_disable():
    from app.models.signal_rules import signal_rules

    cats = _seed_rubric(3)
    cid = cats["Clarity"]
    signal_rules_service.save_rules_for_assignment(
        3, {f"w_{cid}_flesch_score": "2.5"}
    )  # no en_
    rule = next(x for x in signal_rules() if x.rubric_category_id == cid)
    assert rule.weight == 2.5
    assert bool(rule.enabled) is False  # checkbox absent -> disabled


def test_rules_view_prefers_persisted_after_save():
    cats = _seed_rubric(4)
    cid = cats["Clarity"]
    signal_rules_service.save_rules_for_assignment(
        4, {f"en_{cid}_flesch_score": "on", f"w_{cid}_flesch_score": "3"}
    )
    view = signal_rules_service.rules_view_for_assignment(4)
    clarity = next(e for e in view if e["category"].name == "Clarity")
    assert clarity["rules"][0]["persisted"] is True
    assert clarity["rules"][0]["weight"] == 3.0
