"""
Signal model — deterministic metrics extracted from a submission by the lens
analyser family (ADR 012 / SIGNAL_INTEGRATION_PLAN.md).

Signals are non-identifying numbers, so they persist beyond the draft content
deletion lifecycle (ADR 002 / 008).
"""

from app.models.user import db

# Define signals table if it doesn't exist
signals = db.t.signals
if signals not in db.t:
    signals.create(
        {
            "id": int,
            "draft_id": int,
            "source": str,  # which analyser produced it, e.g. "document-analyser"
            "name": str,  # signal name, e.g. "flesch_score"
            "value": float,  # numeric metric value
            "raw": str,  # optional raw/string form (e.g. an interpretation label)
            "created_at": str,
        },
        pk="id",
    )
Signal = signals.dataclass()
