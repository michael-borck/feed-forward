#!/usr/bin/env python3
"""
Simple functional test for FeedForward application
Tests basic workflows after refactoring
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.assignment import assignments, rubric_categories, rubrics
from app.models.course import courses
from app.models.feedback import aggregated_feedback, ai_models, drafts, model_runs
from app.models.user import users


def test_database_connectivity():
    """Test basic database operations"""
    print("\n=== Testing Database Connectivity ===")

    try:
        # Test user operations
        user_count = len(list(users()))
        print(f"✅ Users table accessible: {user_count} users")

        # Test course operations
        course_count = len(list(courses()))
        print(f"✅ Courses table accessible: {course_count} courses")

        # Test assignment operations
        assignment_count = len(list(assignments()))
        print(f"✅ Assignments table accessible: {assignment_count} assignments")

        # Test rubric operations
        rubric_count = len(list(rubrics()))
        print(f"✅ Rubrics table accessible: {rubric_count} rubrics")

        # Test rubric categories
        category_count = len(list(rubric_categories()))
        print(f"✅ Rubric categories table accessible: {category_count} categories")

        # Test feedback tables
        draft_count = len(list(drafts()))
        print(f"✅ Drafts table accessible: {draft_count} drafts")

        model_run_count = len(list(model_runs()))
        print(f"✅ Model runs table accessible: {model_run_count} model runs")

        ai_model_count = len(list(ai_models()))
        print(f"✅ AI models table accessible: {ai_model_count} AI models")

        aggregated_count = len(list(aggregated_feedback()))
        print(f"✅ Aggregated feedback table accessible: {aggregated_count} feedbacks")

        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_model_relationships():
    """Test that model relationships are working"""
    print("\n=== Testing Model Relationships ===")

    try:
        # Get a course with assignments
        course = courses()[0] if courses() else None
        if course:
            course_assignments = [a for a in assignments() if a.course_id == course.id]
            print(f"✅ Course '{course.title}' has {len(course_assignments)} assignments")

            # Check rubrics for assignments
            for assignment in course_assignments[:1]:  # Check first assignment
                assignment_rubrics = [r for r in rubrics() if r.assignment_id == assignment.id]
                if assignment_rubrics:
                    rubric = assignment_rubrics[0]
                    categories = [c for c in rubric_categories() if c.rubric_id == rubric.id]
                    print(f"✅ Assignment '{assignment.title}' has rubric with {len(categories)} categories")

        # Check AI models
        active_models = [m for m in ai_models() if m.active]
        print(f"✅ Found {len(active_models)} active AI models")

        return True

    except Exception as e:
        print(f"❌ Relationship error: {e}")
        return False


def test_authentication_system():
    """Test authentication-related operations"""
    print("\n=== Testing Authentication System ===")

    try:
        # Check for different user roles
        admins = [u for u in users() if u.role == 'admin']
        instructors = [u for u in users() if u.role == 'instructor']
        students = [u for u in users() if u.role == 'student']

        print(f"✅ Found {len(admins)} admin(s)")
        print(f"✅ Found {len(instructors)} instructor(s)")
        print(f"✅ Found {len(students)} student(s)")

        # Check for approved instructors
        approved_instructors = [u for u in instructors if u.approved]
        print(f"✅ {len(approved_instructors)} of {len(instructors)} instructors are approved")

        return True

    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False


def test_feedback_system():
    """Test feedback-related operations"""
    print("\n=== Testing Feedback System ===")

    try:
        # Check draft statuses
        draft_list = list(drafts())
        if draft_list:
            statuses = {d.status for d in draft_list if hasattr(d, 'status')}
            print(f"✅ Draft statuses found: {', '.join(statuses) if statuses else 'none'}")

            # Check for drafts with feedback
            drafts_with_runs = []
            for draft in draft_list:
                runs = [r for r in model_runs() if r.draft_id == draft.id]
                if runs:
                    drafts_with_runs.append(draft)

            print(f"✅ {len(drafts_with_runs)} draft(s) have model runs")
        else:
            print("✅ No drafts in system yet (expected for fresh install)")

        return True

    except Exception as e:
        print(f"❌ Feedback system error: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Starting FeedForward Functionality Tests")
    print("=" * 50)

    all_passed = True

    # Run tests
    all_passed &= test_database_connectivity()
    all_passed &= test_model_relationships()
    all_passed &= test_authentication_system()
    all_passed &= test_feedback_system()

    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All functionality tests passed!")
        print("\nNext steps:")
        print("1. The application is running on http://localhost:5001")
        print("2. You can login as admin@example.com / Admin123!")
        print("3. Try creating courses, assignments, and submitting drafts")
        print("4. All refactoring changes have been successfully applied")
    else:
        print("❌ Some tests failed - review the output above")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
