"""
Script to create sample data for test student
"""
from datetime import datetime, timedelta
import sys
import os

# Make sure app is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.assignment import Assignment, Rubric, RubricCategory, assignments, rubrics, rubric_categories
from app.utils.auth import get_password_hash

TEST_STUDENT_EMAIL = "student@student.curtin.edu.au"
TEST_INSTRUCTOR_EMAIL = "instructor@curtin.edu.au"

def create_sample_data():
    """Create sample courses and assignments for test student"""
    print("Creating sample data for test student...")
    
    # First, make sure our test users exist
    ensure_test_users_exist()
    
    # Get next available IDs
    next_course_id = get_next_id(courses())
    next_assignment_id = get_next_id(assignments()) if assignments() else 1
    next_rubric_id = get_next_id(rubrics()) if rubrics() else 1
    next_category_id = get_next_id(rubric_categories()) if rubric_categories() else 1
    next_enrollment_id = get_next_id(enrollments()) if enrollments() else 1
    
    # Create sample courses
    course_ids = []
    sample_courses = [
        {
            "id": next_course_id,
            "title": "Introduction to Computer Science",
            "code": "CS101",
            "term": "Spring 2025",
            "instructor_email": TEST_INSTRUCTOR_EMAIL,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": next_course_id + 1,
            "title": "Advanced Programming",
            "code": "CS202",
            "term": "Spring 2025",
            "instructor_email": TEST_INSTRUCTOR_EMAIL,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": next_course_id + 2,
            "title": "Technical Writing",
            "code": "ENG150",
            "term": "Spring 2025",
            "instructor_email": TEST_INSTRUCTOR_EMAIL,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Add courses if they don't already exist
    for course_data in sample_courses:
        # Check if course already exists
        exists = False
        for course in courses():
            if course.code == course_data["code"] and course.term == course_data["term"]:
                exists = True
                course_ids.append(course.id)
                print(f"Course {course.code} already exists, using existing course.")
                break
                
        if not exists:
            # Add new course
            course = Course(**course_data)
            courses.insert(course)
            course_ids.append(course.id)
            print(f"Created course: {course.title} ({course.code})")
    
    # Create enrollments for the test student
    for course_id in course_ids:
        # Check if enrollment already exists
        exists = False
        for enrollment in enrollments():
            if enrollment.course_id == course_id and enrollment.student_email == TEST_STUDENT_EMAIL:
                exists = True
                print(f"Enrollment for course {course_id} already exists.")
                break
        
        if not exists:
            # Create enrollment
            enrollment = Enrollment(
                id=next_enrollment_id,
                course_id=course_id,
                student_email=TEST_STUDENT_EMAIL
            )
            enrollments.insert(enrollment)
            next_enrollment_id += 1
            print(f"Enrolled test student in course {course_id}")
    
    # Create sample assignments for each course
    assignment_id = next_assignment_id
    for i, course_id in enumerate(course_ids):
        # Create assignments for this course
        due_dates = [
            (datetime.now() + timedelta(days=14)).isoformat(),
            (datetime.now() + timedelta(days=28)).isoformat(),
            (datetime.now() + timedelta(days=42)).isoformat()
        ]
        
        for j in range(3):  # 3 assignments per course
            # Check if assignment already exists
            exists = False
            for assignment in assignments():
                if assignment.course_id == course_id and f"Assignment {j+1}" in assignment.title:
                    exists = True
                    print(f"Assignment {j+1} for course {course_id} already exists.")
                    break
            
            if not exists:
                # Create assignment
                assignment_data = {
                    "id": assignment_id,
                    "course_id": course_id,
                    "title": f"Assignment {j+1} - Course {i+1}",
                    "description": f"This is a sample assignment for course {i+1}. Students should complete the tasks outlined and submit their work for feedback.",
                    "due_date": due_dates[j],
                    "max_drafts": 3,
                    "created_by": TEST_INSTRUCTOR_EMAIL,
                    "status": "active",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                assignment = Assignment(**assignment_data)
                assignments.insert(assignment)
                print(f"Created assignment: {assignment.title} for course {course_id}")
                
                # Create rubric for this assignment
                rubric = Rubric(
                    id=next_rubric_id,
                    assignment_id=assignment_id
                )
                rubrics.insert(rubric)
                
                # Create rubric categories
                categories = [
                    {"name": "Content", "description": "Quality and relevance of content", "weight": 40.0},
                    {"name": "Structure", "description": "Organization and flow of the work", "weight": 30.0},
                    {"name": "Language", "description": "Clarity and correctness of language", "weight": 30.0}
                ]
                
                for category in categories:
                    category_data = {
                        "id": next_category_id,
                        "rubric_id": next_rubric_id,
                        "name": category["name"],
                        "description": category["description"],
                        "weight": category["weight"]
                    }
                    rubric_categories.insert(RubricCategory(**category_data))
                    next_category_id += 1
                
                next_rubric_id += 1
                assignment_id += 1
    
    print("Sample data creation complete!")

def ensure_test_users_exist():
    """Make sure test student and instructor exist"""
    # Check for test student
    try:
        users.get(TEST_STUDENT_EMAIL)
        print("Test student already exists")
    except:
        # Create test student
        student = {
            "email": TEST_STUDENT_EMAIL,
            "name": "Test Student",
            "password": get_password_hash("Test@123"),
            "role": Role.STUDENT,
            "verified": True,
            "verification_token": "",
            "approved": True,
            "department": "Computer Science",
            "reset_token": "",
            "reset_token_expiry": ""
        }
        users.insert(User(**student))
        print("Created test student")
    
    # Check for test instructor
    try:
        users.get(TEST_INSTRUCTOR_EMAIL)
        print("Test instructor already exists")
    except:
        # Create test instructor
        instructor = {
            "email": TEST_INSTRUCTOR_EMAIL,
            "name": "Test Instructor",
            "password": get_password_hash("Instr@123"),
            "role": Role.INSTRUCTOR,
            "verified": True,
            "verification_token": "",
            "approved": True,
            "department": "Computer Science",
            "reset_token": "",
            "reset_token_expiry": ""
        }
        users.insert(User(**instructor))
        print("Created test instructor")

def get_next_id(items):
    """Get the next available ID from a collection of items"""
    if not items:
        return 1
    return max(item.id for item in items) + 1

if __name__ == "__main__":
    create_sample_data()