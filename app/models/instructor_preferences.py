"""
Instructor preferences for AI models
"""

from app.models.user import db

# Define instructor_model_preferences table
instructor_model_prefs = db.t.instructor_model_preferences
if instructor_model_prefs not in db.t:
    instructor_model_prefs.create(
        {
            "id": int,
            "instructor_email": str,  # Reference to users.email
            "model_id": int,  # Reference to ai_models.id
            "is_active": bool,  # Whether this model is active for this instructor
            "created_at": str,  # ISO format timestamp
            "updated_at": str,  # ISO format timestamp
        },
        pk="id",
    )
InstructorModelPref = instructor_model_prefs.dataclass()
