"""
Assessment type and service model definitions
"""

from app.models.user import db

# Define assessment_types table
assessment_types = db.t.assessment_types
if assessment_types not in db.t:
    assessment_types.create(
        dict(
            id=int,
            type_code=str,  # 'essay', 'code', 'math', 'video', etc.
            display_name=str,
            description=str,
            handler_class=str,  # Python class name for the handler
            file_extensions=str,  # JSON array of allowed extensions
            max_file_size=int,  # Max size in bytes
            requires_file=bool,
            supports_text_input=bool,
            configuration=str,  # JSON configuration specific to type
            is_active=bool,
            created_at=str,
            updated_at=str,
        ),
        pk="id",
    )
AssessmentType = assessment_types.dataclass()

# Define assessment_services table
assessment_services = db.t.assessment_services
if assessment_services not in db.t:
    assessment_services.create(
        dict(
            id=int,
            service_name=str,
            service_url=str,
            api_key=str,  # Will be encrypted
            assessment_types=str,  # JSON array of supported type_codes
            capabilities=str,  # JSON object describing service capabilities
            health_check_url=str,
            timeout_seconds=int,
            is_active=bool,
            last_health_check=str,
            health_status=str,  # 'healthy', 'unhealthy', 'unknown'
            created_at=str,
            updated_at=str,
        ),
        pk="id",
    )
AssessmentService = assessment_services.dataclass()

# Define submission_files table
submission_files = db.t.submission_files
if submission_files not in db.t:
    submission_files.create(
        dict(
            id=int,
            draft_id=int,
            filename=str,
            original_filename=str,
            file_path=str,  # Relative path in storage
            file_size=int,
            mime_type=str,
            checksum=str,  # SHA256 hash
            uploaded_at=str,
            removed_at=str,  # When file was deleted (privacy compliance)
        ),
        pk="id",
    )
SubmissionFile = submission_files.dataclass()
