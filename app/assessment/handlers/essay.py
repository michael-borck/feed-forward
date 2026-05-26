"""Essay assessment — text-based submissions."""

from app.assessment.base import AssessmentHandler

ESSAY = AssessmentHandler(
    type_code="essay",
    display_name="Essay",
    supports_file_upload=True,
    supports_text_input=True,
    allowed_extensions=(".pdf", ".docx", ".txt", ".md"),
    max_file_size=20 * 1024 * 1024,  # 20MB
)
