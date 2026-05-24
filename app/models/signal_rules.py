"""
Signal rule model — maps a lens signal to a contribution toward a rubric
category score (ADR 012 / SIGNAL_INTEGRATION_PLAN.md, phase S2).

A rule says: "signal ``signal_name`` from ``signal_source``, passed through
``transform``, contributes (with ``weight``) to rubric category
``rubric_category_id``." The scorer combines all enabled rules for a category
into a single 0-100 estimate.
"""

from app.models.user import db

# Define signal_rules table if it doesn't exist
signal_rules = db.t.signal_rules
if signal_rules not in db.t:
    signal_rules.create(
        {
            "id": int,
            "rubric_category_id": int,
            "signal_source": str,  # e.g. "document-analyser"
            "signal_name": str,  # e.g. "flesch_score"
            # JSON transform mapping a raw value -> 0-100, e.g.
            #   {"type": "band", "bands": [[null, 30, 40], [30, 50, 70], [50, null, 90]]}
            #   {"type": "linear", "in": [0, 100], "out": [0, 100]}
            "transform": str,
            "weight": float,
            "enabled": bool,
        },
        pk="id",
    )
SignalRule = signal_rules.dataclass()
