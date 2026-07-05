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


def type_code_for_assignment(assignment_id: int) -> str:
    """Resolve an assignment's assessment type code via ``assessment_types``.

    Falls back to the default handler's code when the assignment has no
    type linkage (most current assignments) or the lookup fails.
    """
    # Local imports: keep this module import-time free of the DB layer.
    from app.models.assessment import assessment_types
    from app.models.assignment import assignments
    from app.utils.db_query import by_id

    assignment = by_id(assignments, assignment_id)
    type_id = getattr(assignment, "assessment_type_id", None) if assignment else None
    if not type_id:
        return DEFAULT_HANDLER.type_code
    atype = by_id(assessment_types, type_id)
    code = getattr(atype, "type_code", None) if atype else None
    return code if code in HANDLERS else DEFAULT_HANDLER.type_code
