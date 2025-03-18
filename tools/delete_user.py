"""
Script to delete a specific user from the FeedForward database
"""
from app.models.user import users

def delete_user(email):
    """Delete a user by email address"""
    try:
        # Check if user exists
        user = users[email]
        print(f"Found user: {user.name} ({user.email})")
        
        # Delete the user
        users.delete(email)
        print(f"Successfully deleted user: {email}")
        
    except Exception as e:
        print(f"Error deleting user: {e}")

if __name__ == "__main__":
    # Delete the specified user
    delete_user("michael.borck@curtin.edu.au")