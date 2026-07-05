"""
Course and enrollment model definitions
"""

from app.models.user import db

# Define courses table if it doesn't exist
courses = db.t.courses
if courses not in db.t:
    courses.create(
        {
            "id": int,
            "code": str,
            "title": str,
            "term": str,
            "department": str,
            "description": str,
            "instructor_email": str,
            "status": str,  # 'active', 'closed', 'archived', 'deleted'
            "created_at": str,  # ISO format timestamp
            "updated_at": str,  # ISO format timestamp
        },
        pk="id",
    )
elif "description" not in {c.name for c in courses.columns}:
    # Migration: the course forms always offered a Description field, but the
    # column was never created, so the create/update handlers crashed.
    courses.add_column("description", str)
Course = courses.dataclass()

# Define enrollments table if it doesn't exist
enrollments = db.t.enrollments
if enrollments not in db.t:
    enrollments.create({"id": int, "course_id": int, "student_email": str}, pk="id")
Enrollment = enrollments.dataclass()
