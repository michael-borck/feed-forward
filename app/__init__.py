"""
FeedForward Application Package
"""

import inspect
import os
import secrets
from functools import wraps

from fasthtml import common as fh
from starlette.exceptions import HTTPException
from starlette.responses import HTMLResponse, RedirectResponse, Response

# Create FastHTML app instance
custom_styles = fh.Style("""
.mw-960 { max-width: 960px; }
.mw-480 { max-width: 480px; }
.mx-auto { margin-left: auto; margin-right: auto; }
""")

# Typography: Inter as the app-wide sans, Fraunces as the display serif
# (Editorial direction, 2026-07 — see app/utils/design.py). Loaded before
# Tailwind so the config below can reference them.
inter_font = fh.Link(
    rel="stylesheet",
    href=(
        "https://fonts.googleapis.com/css2"
        "?family=Inter:wght@400;500;600;700"
        "&family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700"
        "&display=swap"
    ),
)

# Include Tailwind CSS for styling
tailwind_cdn = fh.Script(src="https://cdn.tailwindcss.com")
tailwind_config = fh.Script("""
tailwind.config = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Fraunces', 'Georgia', 'ui-serif', 'serif'],
      },
    },
  },
}
""")

# Inline SVG favicon (two-tone arrow glyph in the Editorial palette — navy
# ink + brand teal); also stops browsers 404-ing /favicon.ico on every page.
favicon = fh.Link(
    rel="icon",
    type="image/svg+xml",
    href=(
        "data:image/svg+xml,"
        "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
        "%3Crect width='32' height='32' rx='4' fill='%231a2e44'/%3E"
        "%3Cpath d='M8 22 L16 10 L20 16 L24 10' stroke='%230d9488' "
        "stroke-width='3' fill='none' stroke-linecap='round' "
        "stroke-linejoin='round'/%3E%3C/svg%3E"
    ),
)

app, rt = fh.fast_app(
    live=True,
    debug=True,
    hdrs=(custom_styles, inter_font, tailwind_cdn, tailwind_config, favicon),
    # Pin Pico (FastHTML's base stylesheet) to its light theme: the Editorial
    # design is paper-light everywhere, and without this any element that
    # lacks explicit Tailwind colours (bare inputs, page gutters) flips to
    # Pico's dark palette for dark-mode users.
    htmlkw={"data-theme": "light"},
)

# We'll use explicit route handlers for error pages instead of exception handlers
# This ensures proper HTML rendering


async def _maybe_await(result):
    """Await a handler's result only if it's a coroutine — lets these (sync)
    decorators wrap both sync and async route handlers correctly."""
    return await result if inspect.isawaitable(result) else result


# --- Basic Authentication Decorator ---
def basic_auth(f):
    @wraps(f)
    async def wrapper(session, *args, **kwargs):
        if "auth" not in session:
            return fh.RedirectResponse("/login", status_code=303)

        try:
            from app.models.user import users

            user = users[session["auth"]]
            # Add role check based on domain
            if not user.verified:
                del session["auth"]
                return fh.RedirectResponse("/login", status_code=303)
        except Exception:
            del session["auth"]
            return fh.RedirectResponse("/login", status_code=303)

        return await _maybe_await(f(session, *args, **kwargs))

    return wrapper


# --- General Login Required Decorator ---
def login_required(f):
    """Decorator to require authentication without specific role"""

    @wraps(f)
    async def wrapper(session, *args, **kwargs):
        try:
            from app.models.user import users

            # Just check if user exists in session
            users[session["auth"]]
        except Exception:
            return fh.RedirectResponse("/login", status_code=303)

        return await _maybe_await(f(session, *args, **kwargs))

    return wrapper


# --- Domain-specific role Authorization Decorator ---
def role_required(role):
    def decorator(f):
        @wraps(f)
        async def wrapper(session, *args, **kwargs):
            try:
                from app.models.user import Role, users

                user = users[session["auth"]]
                if user.role != role:
                    # Redirect to access-denied page with role information
                    error_message = (
                        f"You need {role.name.lower()} role to access this page."
                    )
                    # We'll create a dedicated error route for 403 errors
                    return fh.RedirectResponse(
                        f"/error/403?message={error_message}", status_code=303
                    )
            except Exception:
                return fh.RedirectResponse("/login", status_code=303)

            return await _maybe_await(f(session, *args, **kwargs))

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
