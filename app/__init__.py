"""
FeedForward Application Package
"""

import os
import secrets
from functools import wraps
from fasthtml.common import *
from starlette.responses import Response, RedirectResponse
from starlette.exceptions import HTTPException

# Create FastHTML app instance
custom_styles = Style("""
.mw-960 { max-width: 960px; }
.mw-480 { max-width: 480px; }
.mx-auto { margin-left: auto; margin-right: auto; }
""")

# Include Tailwind CSS for styling
tailwind_cdn = Script(src="https://cdn.tailwindcss.com")

app, rt = fast_app(live=True, debug=True, hdrs=(custom_styles, tailwind_cdn))

# --- Basic Authentication Decorator ---
def basic_auth(f):
    @wraps(f)
    def wrapper(session, *args, **kwargs):
        if "auth" not in session:
            return RedirectResponse('/login', status_code=303)
        
        try:
            from app.models.user import users
            user = users[session['auth']]
            # Add role check based on domain
            if not user.verified:
                del session['auth']
                return RedirectResponse('/login', status_code=303)
        except Exception:
            del session['auth']
            return RedirectResponse('/login', status_code=303)
            
        return f(session, *args, **kwargs)
    return wrapper

# --- Domain-specific role Authorization Decorator ---
def role_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(session, *args, **kwargs):
            try:
                from app.models.user import users, Role
                user = users[session['auth']]
                if user.role != role:
                    return Response(f"You need {role} role to access this page", status_code=403)
            except:
                return RedirectResponse('/login', status_code=303)
                
            return f(session, *args, **kwargs)
        return wrapper
    return decorator

# --- Instructor Authorization Decorator ---
def instructor_required(f):
    from app.models.user import Role
    return role_required(Role.INSTRUCTOR)(f)

# --- Student Authorization Decorator ---
def student_required(f):
    from app.models.user import Role
    return role_required(Role.STUDENT)(f)

# --- Admin Authorization Decorator ---
def admin_required(f):
    from app.models.user import Role
    return role_required(Role.ADMIN)(f)

__version__ = "0.1.0"