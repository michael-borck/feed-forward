"""Mathematics assessment — proofs, derivations, LaTeX content."""

from app.assessment.base import AssessmentHandler

MATH = AssessmentHandler(
    type_code="math",
    display_name="Mathematics",
    supports_file_upload=True,
    supports_text_input=True,
    allowed_extensions=(".pdf", ".tex", ".md", ".txt"),
    max_file_size=10 * 1024 * 1024,  # 10MB
)
