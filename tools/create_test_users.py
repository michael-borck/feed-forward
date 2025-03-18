"""
Script to create test users for FeedForward
"""
from app.models.user import User, Role, users
from app.utils.auth import get_password_hash

def create_test_users():
    """Create test users for development purposes"""
    # Create test student
    student = {
        "email": "student@student.curtin.edu.au",
        "name": "Test Student",
        "password": get_password_hash("Test@123"),  # Strong password
        "role": Role.STUDENT,
        "verified": True,  # Pre-verified for testing
        "verification_token": "",
        "approved": True,  # Pre-approved for testing
        "department": "Computer Science",
        "reset_token": "",
        "reset_token_expiry": ""
    }
    
    # Create admin user
    admin = {
        "email": "admin@curtin.edu.au",
        "name": "Admin User",
        "password": get_password_hash("Admin@123"),  # Strong password
        "role": Role.ADMIN,
        "verified": True,  # Pre-verified for testing
        "verification_token": "",
        "approved": True,  # Pre-approved for testing
        "department": "Computer Science",
        "reset_token": "",
        "reset_token_expiry": ""
    }
    
    # Create instructor if needed
    instructor = {
        "email": "instructor@curtin.edu.au",
        "name": "Test Instructor",
        "password": get_password_hash("Instr@123"),  # Strong password
        "role": Role.INSTRUCTOR,
        "verified": True,  # Pre-verified for testing
        "verification_token": "",
        "approved": True,  # Pre-approved for testing
        "department": "Computer Science",
        "reset_token": "",
        "reset_token_expiry": ""
    }
    
    # Add users to database
    try:
        # First check if users already exist
        users.get('student@student.curtin.edu.au')
        print("Student already exists, skipping...")
    except:
        users.insert(User(**student))
        print("Created test student: student@student.curtin.edu.au / Test@123")
    
    try:
        users.get('admin@curtin.edu.au')
        # Update user to admin role if exists
        user = users['admin@curtin.edu.au']
        if user.role != Role.ADMIN:
            user.role = Role.ADMIN
            users.update(user)
            print("Updated user to admin role")
        else:
            print("Admin already exists, skipping...")
    except:
        users.insert(User(**admin))
        print("Created admin user: admin@curtin.edu.au / Admin@123")
    
    try:
        users.get('instructor@curtin.edu.au')
        print("Instructor already exists, skipping...")
    except:
        users.insert(User(**instructor))
        print("Created test instructor: instructor@curtin.edu.au / Instr@123")
    
    print("\nAll test users created successfully!")
    print("You can now log in with these credentials:")
    print("  - Student: student@student.curtin.edu.au / Test@123")
    print("  - Admin: admin@curtin.edu.au / Admin@123")
    print("  - Instructor: instructor@curtin.edu.au / Instr@123")

if __name__ == "__main__":
    create_test_users()