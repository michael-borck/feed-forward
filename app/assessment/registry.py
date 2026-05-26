"""
Assessment handler registry (ADR 012, Phase A3).

Just a dict. The slim handlers are module-level constants in
``app.assessment.handlers``; nothing to load lazily from the DB and no
abstract behaviour to instantiate. ``DEFAULT_HANDLER`` is the fallback when
an assignment has no explicit assessment-type linkage in the data model
(which is the case for most current assignments).
"""

from __future__ import annotations

from app.assessment.base import AssessmentHandler
from app.assessment.handlers import CODE, ESSAY, MATH, VIDEO

HANDLERS: dict[str, AssessmentHandler] = {
    h.type_code: h for h in (ESSAY, CODE, MATH, VIDEO)
}

DEFAULT_HANDLER: AssessmentHandler = ESSAY


def get_assessment_handler(type_code: str | None) -> AssessmentHandler:
    """Return the handler for ``type_code``, or ``DEFAULT_HANDLER`` if unknown."""
    if not type_code:
        return DEFAULT_HANDLER
    return HANDLERS.get(type_code, DEFAULT_HANDLER)
