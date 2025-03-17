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
    return pwd_context.verify(plain_password, hashed_password)

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
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

def is_institutional_email(email: str) -> tuple[bool, str]:
    """
    Check if an email is from an approved institutional domain
    
    Args:
        email: The email address to check
        
    Returns:
        tuple: (is_valid, role)
            - is_valid: True if the email is from an approved domain
            - role: The role based on the domain (student, instructor)
    """
    # Get domain from email
    domain = email.split('@')[-1].lower()
    
    # Define allowed domains and their roles
    instructor_domains = ['curtin.edu.au']
    student_domains = ['student.curtin.edu.au', 'postgraduate.curtin.edu.au']
    
    if domain in instructor_domains:
        return True, "instructor"
    elif domain in student_domains:
        return True, "student"
    else:
        return False, ""

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
    except:
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