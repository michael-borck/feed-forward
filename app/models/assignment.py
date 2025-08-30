"""
Assignment and rubric model definitions
"""

from app.models.user import db

# Define assignments table if it doesn't exist
assignments = db.t.assignments
if assignments not in db.t:
    assignments.create(
        {
            "id": int,
            "course_id": int,
            "title": str,
            "description": str,
            "instructions": str,  # Brief instructions for students
            "spec_file_path": str,  # Path to uploaded assignment specification
            "spec_file_name": str,  # Original filename of specification
            "spec_content": str,  # Extracted text content for AI reference
            "due_date": str,
            "max_drafts": int,
            "created_by": str,  # Instructor's email
            "status": str,  # 'draft', 'active', 'closed', 'archived', 'deleted'
            "assessment_type_id": int,  # Reference to assessment_types table
            "type_config": str,  # JSON for type-specific settings
            "feedback_tone": str,  # 'encouraging', 'neutral', 'direct', 'critical'
            "feedback_detail": str,  # 'brief', 'standard', 'comprehensive'
            "feedback_focus": str,  # JSON array of focus areas
            "icon_theme": str,  # 'emoji', 'none', 'minimal'
            "created_at": str,  # ISO format timestamp
            "updated_at": str,  # ISO format timestamp
        },
        pk="id",
    )
Assignment = assignments.dataclass()

# Define rubrics table if it doesn't exist
rubrics = db.t.rubrics
if rubrics not in db.t:
    rubrics.create(
        {
            "id": int,
            "assignment_id": int,
            "assessment_type_id": int,  # Reference to assessment_types table
            "type_specific_criteria": str,  # JSON for type-specific evaluation
        },
        pk="id",
    )
Rubric = rubrics.dataclass()

# Define rubric_categories table if it doesn't exist
rubric_categories = db.t.rubric_categories
if rubric_categories not in db.t:
    rubric_categories.create(
        {"id": int, "rubric_id": int, "name": str, "description": str, "weight": float}, pk="id"
    )
RubricCategory = rubric_categories.dataclass()
