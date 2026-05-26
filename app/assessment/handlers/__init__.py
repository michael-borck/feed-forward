"""Built-in assessment handlers — slim declarations (Phase A3)."""

from app.assessment.handlers.code import CODE
from app.assessment.handlers.essay import ESSAY
from app.assessment.handlers.math import MATH
from app.assessment.handlers.video import VIDEO

__all__ = ["CODE", "ESSAY", "MATH", "VIDEO"]
