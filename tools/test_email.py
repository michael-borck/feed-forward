"""
Script to test email sending with SMTP configuration

Usage:
    python test_email.py                       # Sends verification email to default personal email
    python test_email.py your-email@example.com # Sends verification email to specified address
    python test_email.py --type reset          # Sends password reset email to default personal email
    python test_email.py --type invitation     # Sends invitation email to default personal email
    python test_email.py --profile work        # Sends verification email to default work email

    # Full example:
    python test_email.py --type invitation --profile work
"""

import argparse
import logging

from app.utils.email import (
    generate_invitation_token,
    generate_password_reset_token,
    generate_verification_token,
    send_password_reset_email,
    send_student_invitation_email,
    send_verification_email,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Always use DEBUG level for testing
logging.getLogger().setLevel(logging.DEBUG)

# No overrides - using settings from .env file

# Print SMTP settings being used
from app.utils.email import SMTP_FROM, SMTP_PORT, SMTP_SERVER, SMTP_USER

print("\nSMTP Settings:")
print(f"Server: {SMTP_SERVER}")
print(f"Port: {SMTP_PORT}")
print(f"User: {SMTP_USER}")
print(f"From: {SMTP_FROM}\n")


def test_email_sending(
    test_email=None, email_type="verification", email_profile="personal"
):
    """
    Tests sending an email using SMTP based on .env settings

    Args:
        test_email: The email address to send to
        email_type: The type of email to send (verification, reset, invitation)
        email_profile: Which default email to use if test_email is None ("personal" or "work")
    """
    # Default email profiles
    default_emails = {
        "personal": "michael@borck.me",
        "work": "michael.borck@curtin.edu.au",
    }

    # Use default email if none provided
    if not test_email:
        if email_profile in default_emails:
            test_email = default_emails[email_profile]
        else:
            test_email = default_emails["personal"]
            print(
                f"Warning: Profile '{email_profile}' not found, using 'personal' instead."
            )

    print(f"Sending {email_type} email to {test_email}...")

    # Send appropriate type of test email
    if email_type == "verification":
        token = generate_verification_token(test_email)
        success, message = send_verification_email(test_email, token)
    elif email_type == "reset":
        token = generate_password_reset_token()
        success, message = send_password_reset_email(test_email, token)
    elif email_type == "invitation":
        token = generate_invitation_token()
        success, message = send_student_invitation_email(
            test_email, "Professor Test", "Introduction to Computer Science", token
        )

    # Print results
    if success:
        print(f"SUCCESS: Test {email_type} email sent successfully to {test_email}.")
        print(f"Message: {message}")
    else:
        print(f"ERROR: Failed to send test {email_type} email.")
        print(f"Error message: {message}")


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test email sending functionality")
    parser.add_argument("email", nargs="?", help="Email address to send test email to")
    parser.add_argument(
        "--type",
        choices=["verification", "reset", "invitation"],
        default="verification",
        help="Type of email to send",
    )
    parser.add_argument(
        "--profile",
        choices=["personal", "work"],
        default="personal",
        help="Email profile to use if no email provided",
    )
    args = parser.parse_args()

    # Run the test
    test_email_sending(args.email, args.type, args.profile)
