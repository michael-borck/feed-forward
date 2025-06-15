"""
User model definitions
"""
from enum import Enum
from fasthtml.common import database

# Initialize database
db = database('data/users.db')

class Role(str, Enum):
    """User roles in the application."""
    STUDENT = "student"
    INSTRUCTOR = "instructor" 
    ADMIN = "admin"

# Define users table if it doesn't exist
users = db.t.users
if users not in db.t:
    users.create(dict(
        email=str, 
        name=str,
        password=str, 
        role=str,
        verified=bool,
        verification_token=str,
        approved=bool,
        department=str,
        reset_token=str,
        reset_token_expiry=str,
        status=str,  # 'active', 'inactive', 'archived', 'deleted'
        last_active=str,  # ISO format timestamp of last login/activity
        tos_accepted=bool,  # Terms of Service acceptance
        privacy_accepted=bool,  # Privacy Policy acceptance
        acceptance_date=str  # ISO format timestamp of when ToS/Privacy were accepted
    ), pk='email')

# Create user dataclass
User = users.dataclass()