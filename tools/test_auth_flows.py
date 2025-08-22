#!/usr/bin/env python3
"""
Test script for authentication flows in FeedForward

This script tests backend functionality for authentication flows.
UI/UX testing must be done manually.
"""

import os
import random
import string
import sys
from datetime import datetime

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.config import domain_whitelist
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.user import Role, User, users
from app.utils.auth import (
    get_password_hash,
    is_institutional_email,
)
from app.utils.email import APP_DOMAIN, generate_verification_token


def generate_random_email(domain="example.com"):
    """Generate a random email address for testing"""
    username = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{username}@{domain}"


def generate_random_name():
    """Generate a random name for testing"""
    first_names = [
        "Alex",
        "Jordan",
        "Taylor",
        "Casey",
        "Morgan",
        "Jamie",
        "Riley",
        "Avery",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def test_domain_whitelist():
    """Test domain whitelist functionality"""
    print("\n--- Testing Domain Whitelist ---")

    # Get all domains
    all_domains = list(domain_whitelist())
    print(f"Found {len(all_domains)} domains in whitelist")

    # Test if curtin.edu.au is whitelisted for auto-approval
    test_email = "test@curtin.edu.au"
    is_valid, role, auto_approve = is_institutional_email(test_email)

    if is_valid and role == "instructor" and auto_approve:
        print(f"✅ {test_email} correctly identified as auto-approved instructor")
    else:
        print(
            f"❌ {test_email} not correctly processed: valid={is_valid}, role={role}, auto={auto_approve}"
        )

    # Test if notre-dame.edu.au is whitelisted but not auto-approved
    test_email = "test@notre-dame.edu.au"
    is_valid, role, auto_approve = is_institutional_email(test_email)

    if is_valid and role == "instructor" and not auto_approve:
        print(f"✅ {test_email} correctly identified as non-auto-approved instructor")
    else:
        print(
            f"❌ {test_email} not correctly processed: valid={is_valid}, role={role}, auto={auto_approve}"
        )

    # Test an unknown domain
    test_email = "test@unknown-university.edu"
    is_valid, role, auto_approve = is_institutional_email(test_email)

    if is_valid and role == "instructor" and not auto_approve:
        print(
            f"✅ {test_email} correctly identified as regular instructor requiring approval"
        )
    else:
        print(
            f"❌ {test_email} not correctly processed: valid={is_valid}, role={role}, auto={auto_approve}"
        )


def test_instructor_registration():
    """Test instructor registration flow"""
    print("\n--- Testing Instructor Registration ---")

    # Create test instructors with different domains
    test_cases = [
        # Auto-approved domain
        {
            "email": generate_random_email("curtin.edu.au"),
            "name": generate_random_name(),
            "expected_auto_approve": True,
        },
        # Non-auto-approved domain
        {
            "email": generate_random_email("notre-dame.edu.au"),
            "name": generate_random_name(),
            "expected_auto_approve": False,
        },
        # Unknown domain
        {
            "email": generate_random_email("unknown-university.edu"),
            "name": generate_random_name(),
            "expected_auto_approve": False,
        },
    ]

    for case in test_cases:
        # Check if user exists first
        try:
            users[case["email"]]
            print(f"⚠️ User {case['email']} already exists, skipping")
            continue
        except:
            pass

        # Create verification token
        token = generate_verification_token(case["email"])

        # Get approval status from domain
        _, _, auto_approve = is_institutional_email(case["email"])

        # Create new user
        new_user = User(
            email=case["email"],
            name=case["name"],
            password=get_password_hash("Test123!"),
            role=Role.INSTRUCTOR,
            verified=False,
            verification_token=token,
            approved=auto_approve,
            department="Test Department",
            reset_token="",
            reset_token_expiry="",
        )

        # Insert user
        users.insert(new_user)

        # Check if user was created correctly
        try:
            user = users[case["email"]]

            # Check approval status
            if user.approved == case["expected_auto_approve"]:
                print(
                    f"✅ {case['email']} created with correct auto-approval={user.approved}"
                )
            else:
                print(
                    f"❌ {case['email']} has incorrect approval status: {user.approved}"
                )

            # Show verification link
            verification_link = f"{APP_DOMAIN}/verify?token={token}"
            print(f"  📧 Verification link: {verification_link}")

        except Exception as e:
            print(f"❌ Error retrieving user {case['email']}: {e!s}")


def test_student_invitation():
    """Test student invitation flow"""
    print("\n--- Testing Student Invitation ---")

    # First create a test instructor if we don't have one
    instructor_email = "test_instructor@curtin.edu.au"
    try:
        instructor = users[instructor_email]
    except:
        # Create test instructor
        token = generate_verification_token(instructor_email)
        instructor = User(
            email=instructor_email,
            name="Test Instructor",
            password=get_password_hash("Test123!"),
            role=Role.INSTRUCTOR,
            verified=True,
            verification_token="",
            approved=True,
            department="Test Department",
            reset_token="",
            reset_token_expiry="",
        )
        users.insert(instructor)
        print(f"✅ Created test instructor: {instructor_email}")

    # Create a test course if we don't have one
    test_course = None
    for course in courses():
        if (
            hasattr(course, "instructor_email")
            and course.instructor_email == instructor_email
        ):
            test_course = course
            break

    if not test_course:
        # Get next course ID
        next_course_id = 1
        try:
            course_ids = [c.id for c in courses()]
            if course_ids:
                next_course_id = max(course_ids) + 1
        except:
            pass

        # Create test course
        test_course = Course(
            id=next_course_id,
            title="Test Course",
            code="TEST101",
            term="2023-1",
            department="Test Department",
            instructor_email=instructor_email,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            status="active",
        )
        courses.insert(test_course)
        print(f"✅ Created test course: {test_course.title} (ID: {test_course.id})")

    # Create test students with different scenarios
    student_emails = [
        generate_random_email("student.example.com"),
        generate_random_email("test.edu"),
    ]

    # Get next enrollment ID
    next_enrollment_id = 1
    try:
        enrollment_ids = [e.id for e in enrollments()]
        if enrollment_ids:
            next_enrollment_id = max(enrollment_ids) + 1
    except:
        pass

    datetime.now().isoformat()

    for email in student_emails:
        # Check if student already exists
        try:
            users[email]
            print(f"⚠️ Student {email} already exists, skipping")
            continue
        except:
            pass

        # Generate token
        token = generate_verification_token(email)

        # Create student record
        new_student = User(
            email=email,
            name="",  # Will be filled when they register
            password="",  # Will be set when they register
            role=Role.STUDENT,
            verified=False,
            verification_token=token,
            approved=True,  # Students are auto-approved
            department="",
            reset_token="",
            reset_token_expiry="",
        )
        users.insert(new_student)

        # Create enrollment
        new_enrollment = Enrollment(
            id=next_enrollment_id, course_id=test_course.id, student_email=email
        )
        enrollments.insert(new_enrollment)
        next_enrollment_id += 1

        # Show invitation link
        invitation_link = f"{APP_DOMAIN}/student/join?token={token}"
        print(f"✅ Created student invitation for {email}")
        print(f"  📧 Invitation link: {invitation_link}")


def main():
    """Run all tests"""
    print("FeedForward Authentication Flow Test")
    print("==============================")
    print(f"APP_DOMAIN: {APP_DOMAIN}")
    print("Running tests...")

    test_domain_whitelist()
    test_instructor_registration()
    test_student_invitation()

    print("\nTests completed!")
    print("\nManual Testing Instructions:")
    print("1. Start the server: python app.py")
    print("2. Open a browser to http://localhost:5000")
    print("3. Follow the verification/invitation links above")
    print("4. Login as admin to approve instructors: admin@example.com / Admin123!")


if __name__ == "__main__":
    main()
