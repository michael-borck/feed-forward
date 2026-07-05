"""
Instructor management of signal -> rubric rules (ADR 012, phase S2).

Auto-matched rules are proposed per rubric category; the instructor confirms them
(persists to ``signal_rules``) and overrides weight / enabled. Persisted rules take
precedence over suggestions everywhere (see ``signal_scorer.category_estimates``).
"""

import contextlib
import json
from typing import Any

from app.assessment.registry import type_code_for_assignment
from app.models.assignment import rubric_categories, rubrics
from app.models.signal_rules import SignalRule, signal_rules
from app.services import signal_scorer
from app.utils.db_query import first, where


def _assignment_categories(assignment_id: int) -> list[Any]:
    rubric = first(rubrics, assignment_id=assignment_id)
    if rubric is None:
        return []
    return where(rubric_categories, rubric_id=rubric.id)


def rules_view_for_assignment(assignment_id: int) -> list[dict[str, Any]]:
    """
    Per rubric category, the rules to show in the editor: persisted rules if any,
    otherwise the auto-matched suggestions (marked ``persisted=False``). Each rule
    carries ``transform`` as a JSON string ready to persist.
    """
    persisted_by_cat: dict[int, list[Any]] = {}
    for rule in signal_rules():
        persisted_by_cat.setdefault(rule.rubric_category_id, []).append(rule)

    type_code = type_code_for_assignment(assignment_id)
    view = []
    for cat in _assignment_categories(assignment_id):
        persisted = persisted_by_cat.get(cat.id)
        if persisted:
            rules = [
                {
                    "signal_name": r.signal_name,
                    "signal_source": r.signal_source,
                    "transform": r.transform,
                    "weight": r.weight,
                    "enabled": bool(r.enabled),
                    "persisted": True,
                }
                for r in persisted
            ]
        else:
            rules = [
                {
                    "signal_name": s.signal_name,
                    "signal_source": s.signal_source,
                    "transform": json.dumps(s.transform),
                    "weight": s.weight,
                    "enabled": s.enabled,
                    "persisted": False,
                }
                for s in signal_scorer.suggest_rules_for_category(cat.name, type_code)
            ]
        view.append({"category": cat, "rules": rules})
    return view


def save_rules_for_assignment(assignment_id: int, fields: dict[str, Any]) -> int:
    """
    Upsert rules for an assignment from submitted form fields.

    Fields are keyed by category id + signal name: ``w_<cat>_<signal>`` (weight) and
    ``en_<cat>_<signal>`` (checkbox; present means enabled). Returns rows upserted.
    """
    existing = {(r.rubric_category_id, r.signal_name): r for r in signal_rules()}
    count = 0
    for entry in rules_view_for_assignment(assignment_id):
        cat = entry["category"]
        for rule in entry["rules"]:
            sig = rule["signal_name"]
            weight = rule["weight"]
            w_raw = fields.get(f"w_{cat.id}_{sig}")
            if w_raw not in (None, ""):
                with contextlib.suppress(TypeError, ValueError):
                    weight = float(w_raw)
            enabled = fields.get(f"en_{cat.id}_{sig}") is not None

            key = (cat.id, sig)
            if key in existing:
                er = existing[key]
                er.weight = weight
                er.enabled = enabled
                signal_rules.update(er)
            else:
                signal_rules.insert(
                    SignalRule(
                        rubric_category_id=cat.id,
                        signal_source=rule["signal_source"],
                        signal_name=sig,
                        transform=rule["transform"],
                        weight=weight,
                        enabled=enabled,
                    )
                )
            count += 1
    return count
