#!/usr/bin/env python3
"""
Standalone database initialization script
Run this from the project root directory
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now we can import from app
from datetime import datetime

from app.models.config import (
    AggregationMethod,
    DomainWhitelist,
    FeedbackStyle,
    MarkDisplayOption,
    aggregation_methods,
    domain_whitelist,
    feedback_styles,
    mark_display_options,
)
from app.models.user import Role, User, users
from app.utils.auth import get_password_hash


def init_db():
    """Initialize the database with default data"""

    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    print("Initializing FeedForward database...")

    # Create admin user if it doesn't exist
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")

    try:
        # Check if admin exists
        users[admin_email]
        print(f"✓ Admin user {admin_email} already exists")
    except:
        # Create admin user with all new fields
        admin = User(
            email=admin_email,
            name="System Administrator",
            password=get_password_hash(admin_password),
            role=Role.ADMIN,
            verified=True,
            verification_token="",
            approved=True,
            department="Administration",
            reset_token="",
            reset_token_expiry="",
            status="active",
            last_active=datetime.now().isoformat(),
            tos_accepted=True,
            privacy_accepted=True,
            acceptance_date=datetime.now().isoformat(),
        )
        users.insert(admin)
        print(f"✓ Created admin user: {admin_email} / {admin_password}")

    # Initialize default aggregation methods if they don't exist
    default_methods = [
        {"name": "Mean", "description": "Average of all scores"},
        {"name": "Median", "description": "Middle value of all scores"},
        {"name": "Mode", "description": "Most frequent score"},
        {
            "name": "Weighted Mean",
            "description": "Weighted average based on model confidence",
        },
    ]

    for method in default_methods:
        try:
            # Check if method exists
            existing = None
            for m in aggregation_methods():
                if m.name == method["name"]:
                    existing = m
                    break
            if not existing:
                aggregation_methods.insert(
                    AggregationMethod(
                        id=len(list(aggregation_methods())) + 1,
                        name=method["name"],
                        description=method["description"],
                    )
                )
                print(f"✓ Created aggregation method: {method['name']}")
        except Exception as e:
            print(f"  Note: {method['name']} - {e!s}")

    # Initialize default feedback styles
    default_styles = [
        {"name": "Encouraging", "description": "Positive and supportive tone"},
        {"name": "Direct", "description": "Clear and straightforward feedback"},
        {
            "name": "Analytical",
            "description": "Detailed analysis with specific examples",
        },
        {
            "name": "Balanced",
            "description": "Mix of positive reinforcement and constructive criticism",
        },
    ]

    for style in default_styles:
        try:
            # Check if style exists
            existing = None
            for s in feedback_styles():
                if s.name == style["name"]:
                    existing = s
                    break
            if not existing:
                feedback_styles.insert(
                    FeedbackStyle(
                        id=len(list(feedback_styles())) + 1,
                        name=style["name"],
                        description=style["description"],
                    )
                )
                print(f"✓ Created feedback style: {style['name']}")
        except Exception as e:
            print(f"  Note: {style['name']} - {e!s}")

    # Initialize default mark display options
    default_mark_options = [
        {"name": "Percentage", "format": "{score}%"},
        {"name": "Letter Grade", "format": "Grade: {letter}"},
        {"name": "Points", "format": "{score}/100"},
        {"name": "Descriptive", "format": "{descriptor}"},
    ]

    for option in default_mark_options:
        try:
            # Check if option exists
            existing = None
            for o in mark_display_options():
                if o.name == option["name"]:
                    existing = o
                    break
            if not existing:
                mark_display_options.insert(
                    MarkDisplayOption(
                        id=len(list(mark_display_options())) + 1,
                        name=option["name"],
                        format=option["format"],
                    )
                )
                print(f"✓ Created mark display option: {option['name']}")
        except Exception as e:
            print(f"  Note: {option['name']} - {e!s}")

    # Add example whitelisted domains
    example_domains = [
        {
            "domain": "example.edu",
            "institution_name": "Example University",
            "auto_approve": True,
        },
        {
            "domain": "test.edu",
            "institution_name": "Test College",
            "auto_approve": True,
        },
    ]

    for domain in example_domains:
        try:
            # Check if domain exists
            existing = None
            for d in domain_whitelist():
                if d.domain == domain["domain"]:
                    existing = d
                    break
            if not existing:
                domain_whitelist.insert(
                    DomainWhitelist(
                        id=len(list(domain_whitelist())) + 1,
                        domain=domain["domain"],
                        institution_name=domain["institution_name"],
                        auto_approve=domain["auto_approve"],
                    )
                )
                print(f"✓ Added whitelisted domain: {domain['domain']}")
        except Exception as e:
            print(f"  Note: {domain['domain']} - {e!s}")

    print("\n✅ Database initialization complete!")
    print("\nYou can now log in with:")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")


if __name__ == "__main__":
    init_db()
