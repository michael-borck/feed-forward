#!/usr/bin/env python3
"""
Create demo accounts for FeedForward demonstration
"""

import os
import sys
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.assignment import assignments, rubric_categories, rubrics
from app.models.course import courses, enrollments
from app.models.user import Role, users
from app.utils.auth import get_password_hash


def create_demo_accounts():
    """Create demo accounts for testing"""

    # Demo account data with simple passwords
    demo_accounts = [
        {
            "email": "instructor@demo.com",
            "name": "Dr. Jane Smith",
            "password": "instructor123",
            "role": Role.INSTRUCTOR,
            "verified": True,
            "verification_token": "",
            "approved": True,
            "department": "Computer Science",
            "reset_token": "",
            "reset_token_expiry": "",
            "status": "active",
            "last_active": datetime.now().isoformat(),
        },
        {
            "email": "student1@demo.com",
            "name": "Alice Johnson",
            "password": "student123",
            "role": Role.STUDENT,
            "verified": True,
            "verification_token": "",
            "approved": True,
            "department": "",
            "reset_token": "",
            "reset_token_expiry": "",
            "status": "active",
            "last_active": datetime.now().isoformat(),
        },
        {
            "email": "student2@demo.com",
            "name": "Bob Wilson",
            "password": "student123",
            "role": Role.STUDENT,
            "verified": True,
            "verification_token": "",
            "approved": True,
            "department": "",
            "reset_token": "",
            "reset_token_expiry": "",
            "status": "active",
            "last_active": datetime.now().isoformat(),
        },
    ]

    print("Creating demo accounts...")

    # Create or update accounts
    for account in demo_accounts:
        try:
            # Check if user exists
            existing_user = None
            all_users = users()
            for user in all_users:
                if user.email == account["email"]:
                    existing_user = user
                    break

            if existing_user:
                print(f"✅ User {account['email']} already exists")
            else:
                # Hash the password
                account["password"] = get_password_hash(account["password"])
                users.insert(account)
                print(f"✅ Created {account['role']} account: {account['email']}")

        except Exception as e:
            print(f"❌ Error creating {account['email']}: {e!s}")

    return True


def create_demo_course():
    """Create a demo course with assignment"""
    print("\nCreating demo course...")

    # Create demo course
    demo_course = {
        "code": "CS101",
        "title": "Introduction to Programming",
        "term": "Fall 2024",
        "department": "Computer Science",
        "instructor_email": "instructor@demo.com",
        "status": "active",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    try:
        # Check if course exists
        all_courses = courses()
        existing_course = next(
            (c for c in all_courses if c.code == demo_course["code"]), None
        )

        if existing_course:
            course_id = existing_course.id
            print(f"✅ Course {demo_course['code']} already exists")
        else:
            course_result = courses.insert(demo_course)
            course_id = (
                course_result.id if hasattr(course_result, "id") else course_result
            )
            print(f"✅ Created course: {demo_course['title']}")

        # Enroll students
        student_emails = ["student1@demo.com", "student2@demo.com"]
        for student_email in student_emails:
            try:
                # Check if enrollment exists
                all_enrollments = enrollments()
                existing_enrollment = next(
                    (
                        e
                        for e in all_enrollments
                        if e.course_id == course_id and e.student_email == student_email
                    ),
                    None,
                )

                if not existing_enrollment:
                    enrollments.insert(
                        {"course_id": int(course_id), "student_email": student_email}
                    )
                    print(f"✅ Enrolled {student_email} in {demo_course['code']}")
                else:
                    print(
                        f"✅ {student_email} already enrolled in {demo_course['code']}"
                    )

            except Exception as e:
                print(f"❌ Error enrolling {student_email}: {e!s}")

        # Create demo assignment
        demo_assignment = {
            "course_id": int(course_id),
            "title": "Essay Assignment - Programming Concepts",
            "description": "Write a 500-word essay explaining object-oriented programming concepts.",
            "due_date": datetime.now().isoformat(),
            "max_drafts": 3,
            "created_by": "instructor@demo.com",
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        try:
            # Check if assignment exists
            all_assignments = assignments()
            existing_assignment = next(
                (
                    a
                    for a in all_assignments
                    if a.title == demo_assignment["title"] and a.course_id == course_id
                ),
                None,
            )

            if existing_assignment:
                assignment_id = existing_assignment.id
                print(f"✅ Assignment already exists: {demo_assignment['title']}")
            else:
                assignment_result = assignments.insert(demo_assignment)
                assignment_id = (
                    assignment_result.id
                    if hasattr(assignment_result, "id")
                    else assignment_result
                )
                print(f"✅ Created assignment: {demo_assignment['title']}")

            # Create rubric
            demo_rubric = {"assignment_id": int(assignment_id)}

            try:
                all_rubrics = rubrics()
                existing_rubric = next(
                    (r for r in all_rubrics if r.assignment_id == assignment_id), None
                )

                if existing_rubric:
                    rubric_id = existing_rubric.id
                    print(f"✅ Rubric already exists for assignment {assignment_id}")
                else:
                    rubric_result = rubrics.insert(demo_rubric)
                    rubric_id = (
                        rubric_result.id
                        if hasattr(rubric_result, "id")
                        else rubric_result
                    )
                    print("✅ Created rubric for assignment")

                # Create rubric categories
                demo_categories = [
                    {
                        "rubric_id": int(rubric_id),
                        "name": "Content Understanding",
                        "description": "Demonstrates understanding of programming concepts",
                        "weight": 40.0,
                    },
                    {
                        "rubric_id": int(rubric_id),
                        "name": "Writing Quality",
                        "description": "Clear, well-structured writing",
                        "weight": 35.0,
                    },
                    {
                        "rubric_id": int(rubric_id),
                        "name": "Examples & Evidence",
                        "description": "Uses appropriate examples to support arguments",
                        "weight": 25.0,
                    },
                ]

                for category in demo_categories:
                    try:
                        all_cats = rubric_categories()
                        existing_cat = next(
                            (
                                c
                                for c in all_cats
                                if c.name == category["name"]
                                and c.rubric_id == rubric_id
                            ),
                            None,
                        )

                        if not existing_cat:
                            rubric_categories.insert(category)
                            print(f"✅ Created rubric category: {category['name']}")
                        else:
                            print(f"✅ Category already exists: {category['name']}")

                    except Exception as e:
                        print(
                            f"❌ Error creating category {category['name']}: {e!s}"
                        )

            except Exception as e:
                print(f"❌ Error creating rubric: {e!s}")

        except Exception as e:
            print(f"❌ Error creating assignment: {e!s}")

    except Exception as e:
        print(f"❌ Error creating course: {e!s}")

    return True


def main():
    """Create all demo data"""
    print("🚀 Creating FeedForward Demo Accounts")

    try:
        # Create user accounts
        create_demo_accounts()

        # Create course structure
        create_demo_course()

        print("\n✅ Demo setup complete!")
        print("\n📋 Demo Account Credentials:")
        print("=" * 50)
        print("ADMIN:")
        print("  Email: admin@example.com")
        print("  Password: Admin123!")
        print("\nINSTRUCTOR:")
        print("  Email: instructor@demo.com")
        print("  Password: instructor123")
        print("\nSTUDENTS:")
        print("  Email: student1@demo.com")
        print("  Password: student123")
        print("  Name: Alice Johnson")
        print("")
        print("  Email: student2@demo.com")
        print("  Password: student123")
        print("  Name: Bob Wilson")
        print("\n🎯 Ready for demo at: http://localhost:5001")

    except Exception as e:
        print(f"❌ Demo setup failed: {e!s}")
        return False

    return True


if __name__ == "__main__":
    main()
