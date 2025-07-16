"""
Assignment and rubric model definitions
"""

from app.models.user import db

# Define assignments table if it doesn't exist
assignments = db.t.assignments
if assignments not in db.t:
    assignments.create(
        dict(
            id=int,
            course_id=int,
            title=str,
            description=str,
            due_date=str,
            max_drafts=int,
            created_by=str,  # Instructor's email
            status=str,  # 'draft', 'active', 'closed', 'archived', 'deleted'
            assessment_type_id=int,  # Reference to assessment_types table
            type_config=str,  # JSON for type-specific settings
            created_at=str,  # ISO format timestamp
            updated_at=str,  # ISO format timestamp
        ),
        pk="id",
    )
Assignment = assignments.dataclass()

# Define rubrics table if it doesn't exist
rubrics = db.t.rubrics
if rubrics not in db.t:
    rubrics.create(
        dict(
            id=int,
            assignment_id=int,
            assessment_type_id=int,  # Reference to assessment_types table
            type_specific_criteria=str,  # JSON for type-specific evaluation
        ),
        pk="id",
    )
Rubric = rubrics.dataclass()

# Define rubric_categories table if it doesn't exist
rubric_categories = db.t.rubric_categories
if rubric_categories not in db.t:
    rubric_categories.create(
        dict(id=int, rubric_id=int, name=str, description=str, weight=float), pk="id"
    )
RubricCategory = rubric_categories.dataclass()
