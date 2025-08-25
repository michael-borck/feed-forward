"""
Route modules for the FeedForward application
"""


def register_routes():
    """Register all application routes"""
    from app.routes import admin, auth, docs, instructor, legal, student
