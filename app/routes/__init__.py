"""
Route modules for the FeedForward application
"""

def register_routes():
    """Register all application routes"""
    from app.routes import auth, student, instructor, admin