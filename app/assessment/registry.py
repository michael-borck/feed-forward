"""
Registry for managing assessment type handlers
"""

import importlib
import logging
from typing import Optional

from app.assessment.base import AssessmentHandler
from app.models.assessment import AssessmentType, assessment_types

logger = logging.getLogger(__name__)


class AssessmentRegistry:
    """
    Singleton registry for assessment type handlers.

    This registry manages the discovery and instantiation of assessment handlers
    based on the configuration in the database.
    """

    _instance = None
    _handlers: dict[str, type[AssessmentHandler]] = {}
    _handler_instances: dict[str, AssessmentHandler] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._load_built_in_handlers()
        self._load_handlers_from_db()

    def _load_built_in_handlers(self):
        """Load built-in assessment handlers."""
        # Import built-in handlers
        built_in_handlers = [
            ("essay", "app.assessment.handlers.essay", "EssayAssessmentHandler"),
            ("code", "app.assessment.handlers.code", "CodeAssessmentHandler"),
            ("math", "app.assessment.handlers.math", "MathAssessmentHandler"),
            ("video", "app.assessment.handlers.video", "VideoAssessmentHandler"),
        ]

        for type_code, module_path, class_name in built_in_handlers:
            try:
                module = importlib.import_module(module_path)
                handler_class = getattr(module, class_name)
                self.register_handler(type_code, handler_class)
                logger.info(f"Loaded built-in handler: {type_code}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not load built-in handler {type_code}: {e}")

    def _load_handlers_from_db(self):
        """Load and instantiate handlers based on database configuration."""
        try:
            for assessment_type in assessment_types():
                if assessment_type.is_active:
                    self._create_handler_instance(assessment_type)
        except Exception as e:
            logger.error(f"Error loading handlers from database: {e}")

    def _create_handler_instance(self, assessment_type: AssessmentType):
        """Create an instance of a handler for an assessment type."""
        type_code = assessment_type.type_code

        if type_code not in self._handlers:
            logger.warning(f"No handler registered for assessment type: {type_code}")
            return

        try:
            # Convert database model to dict for handler initialization
            config = {
                "type_code": assessment_type.type_code,
                "display_name": assessment_type.display_name,
                "description": assessment_type.description,
                "file_extensions": assessment_type.file_extensions,
                "max_file_size": assessment_type.max_file_size,
                "requires_file": assessment_type.requires_file,
                "supports_text_input": assessment_type.supports_text_input,
                "configuration": assessment_type.configuration,
            }

            handler_instance = self._handlers[type_code](config)
            self._handler_instances[type_code] = handler_instance
            logger.info(f"Created handler instance for: {type_code}")
        except Exception as e:
            logger.error(f"Error creating handler instance for {type_code}: {e}")

    def register_handler(self, type_code: str, handler_class: type[AssessmentHandler]):
        """
        Register a handler class for an assessment type.

        Args:
            type_code: The assessment type code (e.g., 'essay', 'code')
            handler_class: The handler class (not instance)
        """
        if not issubclass(handler_class, AssessmentHandler):
            raise ValueError(f"{handler_class} must be a subclass of AssessmentHandler")

        self._handlers[type_code] = handler_class
        logger.info(f"Registered handler for type: {type_code}")

        # If there's already a config for this type in the DB, create an instance
        try:
            assessment_type = next(
                (
                    at
                    for at in assessment_types()
                    if at.type_code == type_code and at.is_active
                ),
                None,
            )
            if assessment_type:
                self._create_handler_instance(assessment_type)
        except Exception as e:
            logger.warning(
                f"Could not check database for assessment type {type_code}: {e}"
            )

    def get_handler(self, type_code: str) -> Optional[AssessmentHandler]:
        """
        Get a handler instance for an assessment type.

        Args:
            type_code: The assessment type code

        Returns:
            Handler instance or None if not found
        """
        return self._handler_instances.get(type_code)

    def get_active_types(self) -> list[dict[str, any]]:
        """
        Get list of active assessment types with their handlers.

        Returns:
            List of dictionaries with type information
        """
        active_types = []

        for type_code, handler in self._handler_instances.items():
            active_types.append(
                {
                    "type_code": type_code,
                    "display_name": handler.display_name,
                    "supports_file": handler.supports_file_upload(),
                    "supports_text": handler.supports_text_input(),
                    "allowed_extensions": handler.get_allowed_extensions(),
                    "max_file_size": handler.get_max_file_size(),
                    "requires_external_service": handler.requires_external_service(),
                }
            )

        return active_types

    def reload(self):
        """Reload all handlers from the database."""
        self._handler_instances.clear()
        self._load_handlers_from_db()
        logger.info("Reloaded assessment handlers")

    @classmethod
    def get_instance(cls) -> "AssessmentRegistry":
        """Get the singleton instance of the registry."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Convenience function
def get_assessment_handler(type_code: str) -> Optional[AssessmentHandler]:
    """
    Get an assessment handler by type code.

    Args:
        type_code: The assessment type code (e.g., 'essay', 'code')

    Returns:
        Handler instance or None if not found
    """
    registry = AssessmentRegistry.get_instance()
    return registry.get_handler(type_code)
