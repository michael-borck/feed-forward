"""
Email utility functions for sending emails and generating tokens
"""
import os
import smtplib
import secrets
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SMTP_SERVER   = os.environ.get("SMTP_SERVER", "smtp.example.com")
SMTP_PORT     = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER     = os.environ.get("SMTP_USER", "user@example.com")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "yourpassword")
SMTP_FROM     = os.environ.get("SMTP_FROM", "noreply@example.com")
APP_DOMAIN    = os.environ.get("APP_DOMAIN", "http://localhost:5001")

def send_verification_email(user_email: str, token: str) -> bool:
    """
    Send an email verification link to the user
    
    Args:
        user_email: The user's email address
        token: The verification token
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        msg = EmailMessage()
        verify_link = f"{APP_DOMAIN}/verify?token={token}"
        msg.set_content(f"Please click the following link to verify your email:\n{verify_link}")
        msg["Subject"] = "Verify Your Email"
        msg["From"] = SMTP_FROM
        msg["To"] = user_email

        # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for other ports
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send verification email: {str(e)}")
        return False

def send_password_reset_email(user_email: str, token: str) -> bool:
    """
    Send a password reset link to the user
    
    Args:
        user_email: The user's email address
        token: The reset token
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        msg = EmailMessage()
        reset_link = f"{APP_DOMAIN}/reset-password?token={token}"
        msg.set_content(f"Please click the following link to reset your password:\n{reset_link}\n\nThis link will expire in 24 hours.")
        msg["Subject"] = "Reset Your Password"
        msg["From"] = SMTP_FROM
        msg["To"] = user_email

        # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for other ports
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {str(e)}")
        return False

def send_student_invitation_email(student_email: str, instructor_name: str, course_name: str, token: str) -> bool:
    """
    Send an invitation email to a student to join a course
    
    Args:
        student_email: The student's email address
        instructor_name: The name of the instructor
        course_name: The name of the course
        token: The invitation token
        
    Returns:
        bool: True if the email was sent successfully, False otherwise
    """
    try:
        msg = EmailMessage()
        invitation_link = f"{APP_DOMAIN}/student/join?token={token}"
        msg.set_content(
            f"You have been invited by {instructor_name} to join the course '{course_name}' on FeedForward.\n\n"
            f"FeedForward is a platform that provides AI-powered feedback on your assignments.\n\n"
            f"Please click the following link to accept the invitation and create your account:\n{invitation_link}"
        )
        msg["Subject"] = f"Invitation to join '{course_name}' on FeedForward"
        msg["From"] = SMTP_FROM
        msg["To"] = student_email

        # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for other ports
        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send student invitation email: {str(e)}")
        return False

def generate_verification_token(email: str) -> str:
    """
    Generate a secure token for email verification
    
    Args:
        email: The user's email address (not used in token generation but included for future reference)
        
    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(32)

def generate_password_reset_token() -> str:
    """
    Generate a secure token for password reset
    
    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(32)

def generate_invitation_token() -> str:
    """
    Generate a secure token for student invitation
    
    Returns:
        str: A secure random token
    """
    return secrets.token_urlsafe(32)