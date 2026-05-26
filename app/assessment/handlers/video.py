"""Video assessment — recorded presentations (transcription via external service)."""

from app.assessment.base import AssessmentHandler

VIDEO = AssessmentHandler(
    type_code="video",
    display_name="Video Presentation",
    supports_file_upload=True,
    supports_text_input=False,  # video can't be pasted in
    allowed_extensions=(".mp4", ".mov", ".webm", ".m4v"),
    max_file_size=500 * 1024 * 1024,  # 500MB
    requires_external_service=True,
    external_service_name="video_transcription",
)
