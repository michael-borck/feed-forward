"""
Base class for all assessment type handlers
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class AssessmentHandler(ABC):
    """
    Abstract base class for assessment type handlers.

    Each assessment type (essay, code, math, video, etc.) must implement
    this interface to integrate with the FeedForward platform.
    """

    def __init__(self, assessment_type_config: dict[str, Any]):
        """
        Initialize the handler with type-specific configuration.

        Args:
            assessment_type_config: Configuration from the assessment_types table
        """
        self.config = assessment_type_config
        self.type_code = assessment_type_config.get("type_code")
        self.display_name = assessment_type_config.get("display_name")

    @abstractmethod
    def validate_submission(
        self, content: Any, metadata: dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """
        Validate that the submission meets the requirements for this assessment type.

        Args:
            content: The submission content (text, file path, etc.)
            metadata: Additional metadata about the submission

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if submission is valid
            - error_message: Error message if invalid, None if valid
        """
        pass

    @abstractmethod
    def preprocess(self, content: Any, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Preprocess the submission for AI evaluation.

        This method should convert the submission into a format suitable for
        LLM processing. For example:
        - Video: Extract transcript and key frames
        - Code: Add syntax highlighting, extract structure
        - Math: Convert LaTeX to readable format

        Args:
            content: The submission content
            metadata: Additional metadata about the submission

        Returns:
            Dictionary containing:
            - processed_text: Text representation for LLM
            - additional_context: Any additional context for the prompt
            - metadata: Updated metadata
        """
        pass

    @abstractmethod
    def get_prompt_template(
        self, rubric: dict[str, Any], processed_content: dict[str, Any]
    ) -> str:
        """
        Generate the prompt template for this assessment type.

        Args:
            rubric: The rubric configuration
            processed_content: Output from preprocess method

        Returns:
            The complete prompt to send to the LLM
        """
        pass

    @abstractmethod
    def format_feedback(
        self, raw_feedback: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Format the raw LLM feedback for display.

        This method can add type-specific formatting, such as:
        - Code: Syntax highlighting for code snippets in feedback
        - Math: LaTeX rendering for mathematical expressions
        - Video: Timestamps for specific feedback points

        Args:
            raw_feedback: The raw feedback from the LLM
            metadata: Submission metadata

        Returns:
            Formatted feedback ready for display
        """
        pass

    def supports_file_upload(self) -> bool:
        """Check if this assessment type supports file uploads."""
        return bool(self.config.get("requires_file", False) or self.config.get(
            "supports_file_upload", True
        ))

    def supports_text_input(self) -> bool:
        """Check if this assessment type supports direct text input."""
        return bool(self.config.get("supports_text_input", True))

    def get_allowed_extensions(self) -> list[str]:
        """Get list of allowed file extensions for this assessment type."""
        import json

        extensions_json = self.config.get("file_extensions", "[]")
        return json.loads(extensions_json) if extensions_json else []

    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes."""
        return int(self.config.get("max_file_size", 10485760))  # Default 10MB

    def requires_external_service(self) -> bool:
        """Check if this assessment type requires an external service."""
        import json

        config_json = self.config.get("configuration", "{}")
        config = json.loads(config_json) if config_json else {}
        return bool(config.get("requires_external_service", False))

    def get_external_service_name(self) -> Optional[str]:
        """Get the name of the required external service."""
        import json

        config_json = self.config.get("configuration", "{}")
        config = json.loads(config_json) if config_json else {}
        return config.get("service_name")

    def get_display_components(self) -> dict[str, str]:
        """
        Get UI component names for this assessment type.

        Returns:
            Dictionary with component names:
            - submission_form: Component for submission input
            - feedback_display: Component for displaying feedback
            - preview: Component for previewing submissions
        """
        return {
            "submission_form": f"{self.type_code}_submission_form",
            "feedback_display": f"{self.type_code}_feedback_display",
            "preview": f"{self.type_code}_preview",
        }

    def get_rubric_template(self) -> dict[str, Any]:
        """
        Get a template rubric for this assessment type.

        Returns:
            Dictionary with suggested rubric categories and weights
        """
        # Default rubric template - subclasses can override
        return {
            "categories": [
                {
                    "name": "Content Quality",
                    "description": "Quality and accuracy of the content",
                    "weight": 0.4,
                },
                {
                    "name": "Structure and Organization",
                    "description": "How well the submission is organized",
                    "weight": 0.3,
                },
                {
                    "name": "Technical Proficiency",
                    "description": "Technical aspects specific to this assessment type",
                    "weight": 0.3,
                },
            ]
        }
