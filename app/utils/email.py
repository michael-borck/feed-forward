"""
Email utility functions for sending emails and generating tokens
"""

import logging
import os
import pathlib
import secrets
import smtplib
import threading
from email.message import EmailMessage

from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables from project root. A missing .env must not
# crash the import (CI, fresh clones, tests) — email sending fails with a
# clear error at send time instead.
project_root = pathlib.Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

env_file_content = ""
if env_path.exists():
    env_file_content = env_path.read_text()

# Check .env file vs environment variables
env_smtp_server = os.getenv("SMTP_SERVER", "")
env_file_smtp_server = ""
for line in env_file_content.splitlines():
    if line.strip().startswith("SMTP_SERVER"):
        env_file_smtp_server = line.split("=")[1].strip()
        break

if env_smtp_server and env_file_smtp_server and env_smtp_server != env_file_smtp_server:
    logger.warning(
        f"WARNING: Environment variable SMTP_SERVER ({env_smtp_server}) "
        f"is overriding .env file setting ({env_file_smtp_server})"
    )

# SMTP settings from environment variables. Empty when unconfigured;
# send_with_smtp refuses to send in that case.
SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", "")

# Use these settings for local SMTP if AWS SES isn't working yet
# SMTP_SERVER   = "mail.borck.me"
# SMTP_PORT     = 465
# SMTP_USER     = "michael@borck.me"
# SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "yourpassword")
# SMTP_FROM     = "noreply@feedforward.au"

# Check for APP_DOMAIN environment variable vs .env file
env_app_domain = os.getenv("APP_DOMAIN", "")
env_file_app_domain = ""
for line in env_file_content.splitlines():
    if line.strip().startswith("APP_DOMAIN"):
        env_file_app_domain = line.split("=")[1].strip()
        break

if env_app_domain and env_file_app_domain and env_app_domain != env_file_app_domain:
    logger.warning(
        f"WARNING: Environment variable APP_DOMAIN ({env_app_domain}) "
        f"is overriding .env file setting ({env_file_app_domain})"
    )

# Application domain for email links (used in verification links)
APP_DOMAIN = os.environ.get("APP_DOMAIN", "https://feedforward.serveur.au:5001")

# Email sending is done via SMTP only


def send_email_async(send_fn, *args) -> None:
    """Fire-and-forget email send on a daemon thread.

    Account emails (verification, password reset) are sent out-of-band so
    request timing never reveals whether an address exists, and requests
    don't block on SMTP. Failures are logged by the send function itself.
    """
    threading.Thread(target=send_fn, args=args, daemon=True).start()


def send_verification_email(user_email: str, token: str) -> tuple[bool, str]:
    """
    Send an email verification link to the user

    Args:
        user_email: The user's email address
        token: The verification token

    Returns:
        tuple: (success, message)
            - success: True if the email was sent successfully, False otherwise
            - message: Success message or error details
    """
    verify_link = f"{APP_DOMAIN}/verify?token={token}"
    subject = "Verify Your FeedForward Account"
    content = f"""
Hello,

Thank you for signing up for FeedForward! To complete your registration and verify your email address, please click the link below:

{verify_link}

If you did not sign up for FeedForward, you can safely ignore this email.

Best regards,
The FeedForward Team
"""

    # Log debugging information
    logger.info(f"Sending verification email to {user_email}")

    # We always use SMTP
    return send_with_smtp(user_email, subject, content)


# Mailgun function removed


def send_with_smtp(to_email: str, subject: str, content: str) -> tuple[bool, str]:
    """
    Send an email using SMTP

    Args:
        to_email: Recipient email address
        subject: Email subject
        content: Email content (text)

    Returns:
        tuple: (success, message)
    """
    if not SMTP_SERVER:
        logger.error("SMTP is not configured (SMTP_SERVER unset) — cannot send email")
        return False, "Email is not configured on this server"

    error_msg = ""
    try:
        # Log debugging information
        logger.debug(f"Using SMTP to send email to {to_email}")
        logger.debug(
            f"SMTP Settings: Server={SMTP_SERVER}, Port={SMTP_PORT}, User={SMTP_USER}"
        )

        msg = EmailMessage()
        msg.set_content(content)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = to_email

        # Use SMTP_SSL for port 465, regular SMTP with STARTTLS for other ports
        if SMTP_PORT == 465:
            logger.debug("Using SMTP_SSL connection")
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
                logger.debug("SMTP_SSL connection established")
                server.login(SMTP_USER, SMTP_PASSWORD)
                logger.debug("Login successful")

                # Set debug level for verbose logging if needed
                if os.environ.get("SMTP_DEBUG", "0") == "1":
                    server.set_debuglevel(1)

                server.send_message(msg)
                logger.debug("Message sent")
        else:
            logger.debug("Using SMTP with STARTTLS")
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                logger.debug("SMTP connection established")
                server.starttls()
                logger.debug("STARTTLS successful")
                server.login(SMTP_USER, SMTP_PASSWORD)
                logger.debug("Login successful")

                # Set debug level for verbose logging if needed
                if os.environ.get("SMTP_DEBUG", "0") == "1":
                    server.set_debuglevel(1)

                server.send_message(msg)
                logger.debug("Message sent")

        return True, "Email sent successfully via SMTP"
    except ConnectionRefusedError:
        error_msg = "Connection refused. Please check if the SMTP server is reachable."
        logger.error(f"EMAIL ERROR: {error_msg}")
        return False, error_msg
    except smtplib.SMTPAuthenticationError:
        error_msg = "Authentication failed. Please check SMTP username and password."
        logger.error(f"EMAIL ERROR: {error_msg}")
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"SMTP error: {e!s}"
        logger.error(f"EMAIL ERROR: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to send email via SMTP: {e!s}"
        logger.error(f"EMAIL ERROR: {error_msg}")
        return False, error_msg


def send_password_reset_email(user_email: str, token: str) -> tuple[bool, str]:
    """
    Send a password reset link to the user

    Args:
        user_email: The user's email address
        token: The reset token

    Returns:
        tuple: (success, message)
            - success: True if the email was sent successfully, False otherwise
            - message: Success message or error details
    """
    reset_link = f"{APP_DOMAIN}/reset-password?token={token}"
    subject = "Reset Your FeedForward Password"
    content = f"""
Hello,

We received a request to reset your password for your FeedForward account. To proceed with resetting your password, please click the link below:

{reset_link}

This link will expire in 24 hours. If you did not request a password reset, you can safely ignore this email.

Best regards,
The FeedForward Team
"""

    # Log debugging information
    logger.info(f"Sending password reset email to {user_email}")

    # We always use SMTP
    return send_with_smtp(user_email, subject, content)


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
