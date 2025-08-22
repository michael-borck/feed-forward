"""
Assessment framework for extensible assessment types
"""

from app.assessment.base import AssessmentHandler
from app.assessment.registry import AssessmentRegistry

__all__ = ["AssessmentHandler", "AssessmentRegistry"]
