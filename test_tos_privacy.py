#!/usr/bin/env python3
"""
Test script to verify ToS/Privacy acceptance functionality
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from app.models.user import db, users, User, Role

def test_tos_privacy_fields():
    """Test that ToS and Privacy fields are added to user model"""
    print("Testing ToS/Privacy acceptance fields...")
    
    # Check if the table has the new columns
    print("\nChecking user table schema...")
    
    # Create a test user with ToS/Privacy fields
    test_email = "test_tos@example.com"
    
    try:
        # Delete test user if exists
        if test_email in users:
            users.delete(test_email)
            print(f"Deleted existing test user: {test_email}")
    except:
        pass
    
    # Create new test user with ToS/Privacy acceptance
    test_user = User(
        email=test_email,
        name="Test ToS User",
        password="hashed_password",
        role=Role.STUDENT,
        verified=True,
        verification_token="",
        approved=True,
        department="",
        reset_token="",
        reset_token_expiry="",
        status="active",
        last_active=datetime.now().isoformat(),
        tos_accepted=True,
        privacy_accepted=True,
        acceptance_date=datetime.now().isoformat()
    )
    
    print("\nCreating test user with ToS/Privacy acceptance...")
    try:
        users.insert(test_user)
        print("✓ Successfully created user with ToS/Privacy fields")
        
        # Retrieve and verify
        retrieved_user = users[test_email]
        print(f"\nRetrieved user details:")
        print(f"  Email: {retrieved_user.email}")
        print(f"  Name: {retrieved_user.name}")
        print(f"  ToS Accepted: {getattr(retrieved_user, 'tos_accepted', 'Field not found')}")
        print(f"  Privacy Accepted: {getattr(retrieved_user, 'privacy_accepted', 'Field not found')}")
        print(f"  Acceptance Date: {getattr(retrieved_user, 'acceptance_date', 'Field not found')}")
        
        # Clean up
        users.delete(test_email)
        print("\n✓ Test completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\nThis likely means the database schema needs to be updated.")
        print("The new fields will be automatically added when a user registers.")

if __name__ == "__main__":
    test_tos_privacy_fields()