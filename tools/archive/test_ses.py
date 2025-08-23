#!/usr/bin/env python
"""
Script to test Amazon SES email sending by ensuring environment variables
don't override the .env settings

Usage:
    ./test_ses.py                            # Test with default settings (will likely fail until verified)
    ./test_ses.py --verified-email your@email.com  # Test with a pre-verified email in SES

You must verify both sender and recipient emails in the AWS SES console
while in sandbox mode.
"""

import argparse
import os
import subprocess
import sys

# Parse arguments
parser = argparse.ArgumentParser(description="Test Amazon SES email sending")
parser.add_argument(
    "--verified-email",
    help="A pre-verified email address in AWS SES to use as both sender and recipient",
)
parser.add_argument(
    "--type",
    choices=["verification", "reset", "invitation"],
    default="verification",
    help="Type of email to send",
)
parser.add_argument(
    "--domain",
    default="https://feedforward.serveur.au:5001",
    help="The base domain to use in email links",
)
args, remaining_args = parser.parse_known_args()

# Unset any environment variables that might override our .env file
env_vars_to_unset = [
    "SMTP_SERVER",
    "SMTP_PORT",
    "SMTP_USER",
    "SMTP_PASSWORD",
    "SMTP_FROM",
    "APP_DOMAIN",
]

# Create a clean environment
clean_env = os.environ.copy()
for var in env_vars_to_unset:
    if var in clean_env:
        print(f"Unsetting environment variable: {var}")
        del clean_env[var]

# Set important environment variables
if args.verified_email:
    print(f"Using verified email for testing: {args.verified_email}")
    clean_env["SMTP_FROM"] = args.verified_email
    email_arg = args.verified_email
else:
    email_arg = None

# Force the correct APP_DOMAIN for email links
print(f"Using domain for links: {args.domain}")
clean_env["APP_DOMAIN"] = args.domain

# Build the command to run test_email.py
cmd = [sys.executable, "test_email.py"]
if email_arg:
    cmd.append(email_arg)
if args.type:
    cmd.extend(["--type", args.type])
cmd.extend(remaining_args)

print(f"Running command: {' '.join(cmd)}")

# Run the test_email.py script with the clean environment
subprocess.run(cmd, env=clean_env)
