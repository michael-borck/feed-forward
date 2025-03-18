#!/usr/bin/env python
"""
Script to test email sending with your personal SMTP server,
but with the correct domain in the verification links.

Usage:
    ./test_smtp.py                         # Uses default settings
    ./test_smtp.py --domain https://example.com  # Override the domain
    ./test_smtp.py --type reset            # Send a password reset email
    ./test_smtp.py --profile work          # Send to your work email
"""
import os
import subprocess
import sys
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description="Test email sending with correct domain")
parser.add_argument("--domain", default="https://feedforward.serveur.au:5001",
                    help="The domain to use in email links")
parser.add_argument("--type", choices=["verification", "reset", "invitation"], 
                    default="verification", help="Type of email to send")
parser.add_argument("--profile", choices=["personal", "work"], 
                    default="personal", help="Email profile to use if no email provided")
args, remaining_args = parser.parse_known_args()

# Create environment with correct settings
env = os.environ.copy()

# Override just the APP_DOMAIN
print(f"Using domain for links: {args.domain}")
env["APP_DOMAIN"] = args.domain

# Use personal SMTP server settings 
env["SMTP_SERVER"] = "mail.borck.me"  
env["SMTP_PORT"] = "465"
env["SMTP_USER"] = "michael@borck.me"
# Note: You need to set SMTP_PASSWORD environment variable before running this script
# Prompt the user if password is not set
if not os.environ.get("SMTP_PASSWORD"):
    import getpass
    print("SMTP password is not set in environment. Please enter it now:")
    env["SMTP_PASSWORD"] = getpass.getpass("SMTP Password: ")
env["SMTP_FROM"] = "noreply@feedforward.au"

# Build the command to run test_email.py
cmd = [sys.executable, "test_email.py"]
if args.profile:
    cmd.extend(["--profile", args.profile])
if args.type:
    cmd.extend(["--type", args.type])
cmd.extend(remaining_args)

print(f"Running command: {' '.join(cmd)}")

# Run the test_email.py script with our environment
subprocess.run(cmd, env=env)