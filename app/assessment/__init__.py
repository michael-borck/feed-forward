"""Assessment framework — slim declarations (ADR 012, Phase A3)."""

from app.assessment.base import AssessmentHandler
from app.assessment.registry import (
    DEFAULT_HANDLER,
    HANDLERS,
    get_assessment_handler,
)

__all__ = [
    "DEFAULT_HANDLER",
    "HANDLERS",
    "AssessmentHandler",
    "get_assessment_handler",
]
