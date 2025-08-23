#!/usr/bin/env python
"""
Script to test email sending using only the .env file settings.
This script loads settings directly from the .env file, ignoring any environment variables.
"""

import logging
import os
import pathlib
import sys

from app.utils.email import generate_verification_token, send_verification_email

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def send_test_email(recipient_email=None):
    """Send a test email using settings from .env file only"""

    # Load .env directly
    env_path = pathlib.Path(__file__).parent / ".env"
    env_vars = {}

    print(f"Loading settings from {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # Remove comments and quotes
                if "#" in value:
                    value = value.split("#", 1)[0].strip()
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                env_vars[key] = value

                # Don't print password
                if key == "SMTP_PASSWORD":
                    print(f"{key} = ********")
                else:
                    print(f"{key} = {value}")

    # Set variables in environment
    for key, value in env_vars.items():
        os.environ[key] = value

    # Generate token and send email
    token = generate_verification_token("test@example.com")

    # Use provided email or default
    if not recipient_email:
        recipient_email = "michael@borck.me"

    print(f"\nSending verification email to {recipient_email}...")
    success, message = send_verification_email(recipient_email, token)

    if success:
        print(f"SUCCESS: Email sent successfully to {recipient_email}")
        print(f"Message: {message}")
    else:
        print(f"ERROR: Failed to send email to {recipient_email}")
        print(f"Error: {message}")


if __name__ == "__main__":
    recipient = sys.argv[1] if len(sys.argv) > 1 else None
    send_test_email(recipient)
