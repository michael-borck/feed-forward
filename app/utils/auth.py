"""
Authentication utility functions
"""

import re
from datetime import datetime, timedelta

from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: The plain text password to hash

    Returns:
        str: The hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        bool: True if the password matches the hash, False otherwise
    """
    # Try both methods to be safe
    try:
        # First try direct bcrypt
        import bcrypt

        bcrypt_result = bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
        print(f"Debug - direct bcrypt verify: {bcrypt_result}")

        if bcrypt_result:
            return True

        # Fall back to passlib if bcrypt fails
        passlib_result = pwd_context.verify(plain_password, hashed_password)
        print(f"Debug - passlib verify: {passlib_result}")

        return passlib_result
    except Exception as e:
        print(f"Password verification error: {e!s}")
        # Last resort - try a direct string comparison (not secure, but for emergencies)
        return False


def is_strong_password(password: str) -> bool:
    """
    Check if a password meets strong password criteria

    Args:
        password: The password to check

    Returns:
        bool: True if the password is strong, False otherwise
    """
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 digit, 1 special character
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))


def is_institutional_email(email: str) -> tuple[bool, str, bool]:
    """
    Check if an email is from an approved institutional domain

    Args:
        email: The email address to check

    Returns:
        tuple: (is_valid, role, auto_approve)
            - is_valid: True if the email is from an approved domain
            - role: The role based on the domain (student, instructor)
            - auto_approve: True if instructors with this domain are auto-approved
    """
    from app.models.config import domain_whitelist

    # Get domain from email
    domain = email.split("@")[-1].lower()

    # Check for student domains (these are hardcoded for now)
    student_domains = ["student.curtin.edu.au", "postgraduate.curtin.edu.au"]
    if domain in student_domains:
        return True, "student", False

    # Check domain whitelist for instructor domains
    whitelisted_domains = list(domain_whitelist())

    # If no domains in whitelist yet, use fallback domains
    if not whitelisted_domains:
        instructor_domains = ["curtin.edu.au", "ecu.edu.au"]
        if domain in instructor_domains:
            return True, "instructor", True
    else:
        # Check against database domains
        for whitelisted in whitelisted_domains:
            if domain == whitelisted.domain:
                return True, "instructor", whitelisted.auto_approve_instructor
            # Check for subdomains
            if domain.endswith("." + whitelisted.domain):
                return True, "instructor", whitelisted.auto_approve_instructor

    # If not in any list, allow as instructor but requires approval
    return True, "instructor", False


def is_reset_token_valid(token_expiry: str) -> bool:
    """
    Check if a reset token is still valid based on expiry time

    Args:
        token_expiry: The token expiry timestamp as a string

    Returns:
        bool: True if the token is still valid, False otherwise
    """
    try:
        expiry_time = datetime.fromisoformat(token_expiry)
        return datetime.now() < expiry_time
    except Exception:
        return False


def generate_token_expiry(hours: int = 24) -> str:
    """
    Generate an expiry timestamp for a token

    Args:
        hours: The number of hours until expiry

    Returns:
        str: The expiry timestamp as an ISO format string
    """
    expiry_time = datetime.now() + timedelta(hours=hours)
    return expiry_time.isoformat()
