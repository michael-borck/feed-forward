"""Code assessment — programming submissions."""

from app.assessment.base import AssessmentHandler

CODE = AssessmentHandler(
    type_code="code",
    display_name="Code",
    supports_file_upload=True,
    supports_text_input=True,
    allowed_extensions=(
        ".py", ".js", ".ts", ".java", ".cpp", ".c", ".h",
        ".rb", ".go", ".rs", ".cs", ".swift", ".kt",
    ),
    max_file_size=5 * 1024 * 1024,  # 5MB
)
