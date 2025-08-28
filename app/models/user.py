"""
User model definitions
"""

# Initialize database
import os
from enum import Enum

from fasthtml.common import database

# Use absolute path in Docker, relative path for local development
if os.path.exists('/app'):
    db_path = os.environ.get('DATABASE_PATH', '/app/data/users.db')
else:
    db_path = os.environ.get('DATABASE_PATH', 'data/users.db')
    # Create directory only for local development
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
db = database(db_path)


class Role(str, Enum):
    """User roles in the application."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"


# Define users table if it doesn't exist
users = db.t.users
if users not in db.t:
    users.create(
        {
            "email": str,
            "name": str,
            "password": str,
            "role": str,
            "verified": bool,
            "verification_token": str,
            "approved": bool,
            "department": str,
            "reset_token": str,
            "reset_token_expiry": str,
            "status": str,  # 'active', 'inactive', 'archived', 'deleted'
            "last_active": str,  # ISO format timestamp of last login/activity
        },
        pk="email",
    )

# Create user dataclass
User = users.dataclass()
