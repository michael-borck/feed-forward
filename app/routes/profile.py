"""
User profile management routes
Handles profile viewing and editing for all user types
"""

from datetime import datetime

from fasthtml import common as fh

from app import rt, login_required
from app.models.user import users
from app.models.config import ai_models
from app.models.instructor_preferences import instructor_model_prefs, InstructorModelPref
from app.utils.ui import action_button, card, dashboard_layout
from app.utils.auth import get_password_hash, verify_password


@rt("/profile")
@login_required
def profile_view(session):
    """View user profile"""
    # Get current user
    user = users[session["auth"]]
    
    # Sidebar content
    sidebar_content = fh.Div(
        # Navigation
        fh.Div(
            fh.H3("Navigation", cls="font-semibold text-slate-800 mb-4"),
            fh.Div(
                action_button(
                    "Dashboard", 
                    color="gray", 
                    href=f"/{user.role}/dashboard", 
                    icon="←"
                ),
                cls="space-y-3",
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
        # Quick Actions based on role
        fh.Div(
            fh.H3("Quick Actions", cls="font-semibold text-slate-800 mb-4"),
            fh.Div(
                (
                    action_button(
                        "Manage AI Models",
                        color="teal",
                        href="/instructor/models",
                        icon="🤖",
                    )
                    if user.role == "instructor"
                    else fh.Div()
                ),
                (
                    action_button(
                        "View Courses",
                        color="blue",
                        href=f"/{user.role}/courses",
                        icon="📚",
                    )
                    if user.role in ["instructor", "student"]
                    else fh.Div()
                ),
                action_button(
                    "Change Password",
                    color="amber",
                    href="/profile/change-password",
                    icon="🔒",
                ),
                cls="space-y-3",
            ),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        ),
    )
    
    # Main content
    main_content = fh.Div(
        fh.H1("My Profile", cls="text-3xl font-bold text-slate-800 mb-6"),
        
        # Profile Information Card
        fh.Div(
            card(
                fh.H2("Personal Information", cls="text-xl font-bold text-slate-700 mb-4"),
            fh.Div(
                # Name
                fh.Div(
                    fh.Label("Name", cls="text-sm font-medium text-gray-500"),
                    fh.P(user.name, cls="text-lg text-slate-800 mt-1"),
                    cls="mb-4",
                ),
                # Email
                fh.Div(
                    fh.Label("Email", cls="text-sm font-medium text-gray-500"),
                    fh.P(user.email, cls="text-lg text-slate-800 mt-1"),
                    cls="mb-4",
                ),
                # Role
                fh.Div(
                    fh.Label("Role", cls="text-sm font-medium text-gray-500"),
                    fh.P(
                        user.role.title(),
                        cls="text-lg text-slate-800 mt-1 capitalize",
                    ),
                    cls="mb-4",
                ),
                # Department (if instructor)
                (
                    fh.Div(
                        fh.Label("Department", cls="text-sm font-medium text-gray-500"),
                        fh.P(
                            user.department if user.department else "Not specified",
                            cls="text-lg text-slate-800 mt-1",
                        ),
                        cls="mb-4",
                    )
                    if user.role == "instructor" and hasattr(user, "department")
                    else fh.Div()
                ),
                # Account Status
                fh.Div(
                    fh.Label("Account Status", cls="text-sm font-medium text-gray-500"),
                    fh.Div(
                        fh.Span(
                            "✓ Verified" if user.verified else "⚠ Unverified",
                            cls=f"px-3 py-1 rounded-full text-sm font-medium {
                                'bg-green-100 text-green-700' if user.verified 
                                else 'bg-amber-100 text-amber-700'
                            }",
                        ),
                        (
                            fh.Span(
                                "✓ Approved" if user.approved else "⏳ Pending Approval",
                                cls=f"px-3 py-1 rounded-full text-sm font-medium ml-2 {
                                    'bg-green-100 text-green-700' if user.approved 
                                    else 'bg-gray-100 text-gray-700'
                                }",
                            )
                            if user.role == "instructor"
                            else fh.Span()
                        ),
                        cls="mt-1",
                    ),
                    cls="mb-4",
                ),
                # Edit button
                fh.Div(
                    action_button(
                        "Edit Profile",
                        color="blue",
                        href="/profile/edit",
                        icon="✏️",
                        size="regular",
                    ),
                    cls="mt-6",
                ),
                ),
            ),
            cls="mb-6",
        ),
        
        # Role-specific information
        (
            card(
                fh.Div(
                    fh.H2("Instructor Settings", cls="text-xl font-bold text-slate-700 mb-4"),
                    fh.P(
                        "Manage your teaching preferences and AI model configurations.",
                        cls="text-gray-600 mb-4",
                    ),
                    fh.Div(
                        fh.P("Department: ", fh.Strong(user.department or "Not set"), cls="text-gray-700 mb-2"),
                        fh.P("Default feedback style: ", fh.Strong("Balanced"), cls="text-gray-700 mb-2"),
                        fh.P("AI models enabled: ", fh.Strong("Check AI Models page"), cls="text-gray-700"),
                        cls="space-y-2",
                    ),
                )
            )
            if user.role == "instructor"
            else fh.Div()
        ),
        
        # Student-specific information
        (
            card(
                fh.H2("Student Settings", cls="text-xl font-bold text-slate-700 mb-4"),
                fh.P(
                    "View your enrolled courses and submissions.",
                    cls="text-gray-600 mb-4",
                ),
                fh.Div(
                    action_button(
                        "My Courses",
                        color="blue",
                        href="/student/courses",
                        icon="📚",
                        size="regular",
                    ),
                    fh.P(
                        "View enrolled courses and assignments",
                        cls="text-sm text-gray-500 mt-2",
                    ),
                    cls="mb-4",
                ),
                fh.Div(
                    action_button(
                        "My Submissions",
                        color="green",
                        href="/student/dashboard",
                        icon="📝",
                        size="regular",
                    ),
                    fh.P(
                        "Track your assignment submissions and feedback",
                        cls="text-sm text-gray-500 mt-2",
                    ),
                ),
            )
            if user.role == "student"
            else fh.Div()
        ),
        
        # Security Settings
        fh.Div(
            card(
                fh.Div(
                    fh.H2("Security", cls="text-xl font-bold text-slate-700 mb-4"),
                    fh.P(
                        "Manage your account security settings.",
                        cls="text-gray-600 mb-4",
                    ),
                    fh.Div(
                        action_button(
                            "Change Password",
                            color="amber",
                            href="/profile/change-password",
                            icon="🔒",
                            size="regular",
                        ),
                        fh.P(
                            "Update your account password",
                            cls="text-sm text-gray-500 mt-2",
                        ),
                    ),
                )
            ),
            cls="mt-6",
        ),
    )
    
    return dashboard_layout(
        "My Profile",
        sidebar_content,
        main_content,
        user_role=user.role,
        current_path="/profile",
    )


@rt("/profile/edit")
@login_required
def profile_edit(session):
    """Edit user profile form"""
    user = users[session["auth"]]
    
    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Edit Profile", cls="font-semibold text-slate-800 mb-4"),
            fh.P("Update your personal information.", cls="text-gray-600 mb-4"),
            action_button("Cancel", color="gray", href="/profile", icon="×"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )
    
    # Main content - Edit form
    main_content = fh.Div(
        fh.H1("Edit Profile", cls="text-3xl font-bold text-slate-800 mb-6"),
        fh.Form(
            card(
                fh.H2("Personal Information", cls="text-xl font-bold text-slate-700 mb-4"),
                # Name field
                fh.Div(
                    fh.Label(
                        "Name",
                        for_="name",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    fh.Input(
                        type="text",
                        id="name",
                        name="name",
                        value=user.name,
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        required=True,
                    ),
                    cls="mb-4",
                ),
                # Email field (read-only)
                fh.Div(
                    fh.Label(
                        "Email",
                        for_="email",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    fh.Input(
                        type="email",
                        id="email",
                        name="email",
                        value=user.email,
                        cls="w-full px-3 py-2 border border-gray-200 rounded-md bg-gray-50 text-gray-600 cursor-not-allowed",
                        readonly=True,
                    ),
                    fh.P(
                        "Email cannot be changed",
                        cls="text-sm text-gray-500 mt-1",
                    ),
                    cls="mb-4",
                ),
                # Department field (for instructors)
                (
                    fh.Div(
                        fh.Label(
                            "Department",
                            for_="department",
                            cls="block text-sm font-medium text-gray-700 mb-2",
                        ),
                        fh.Input(
                            type="text",
                            id="department",
                            name="department",
                            value=user.department if hasattr(user, "department") and user.department else "",
                            placeholder="e.g., Computer Science",
                            cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        ),
                        cls="mb-6",
                    )
                    if user.role == "instructor"
                    else fh.Div()
                ),
                # Submit buttons
                fh.Div(
                    fh.Button(
                        "Save Changes",
                        type="submit",
                        cls="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 transition-colors mr-4",
                    ),
                    fh.A(
                        "Cancel",
                        href="/profile",
                        cls="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300 transition-colors inline-block",
                    ),
                    cls="flex items-center",
                ),
            ),
            method="post",
            action="/profile/update",
        ),
    )
    
    return dashboard_layout(
        "Edit Profile",
        sidebar_content,
        main_content,
        user_role=user.role,
        current_path="/profile",
    )


@rt("/profile/update")
@login_required
def profile_update(session, name: str, department: str = None):
    """Handle profile update"""
    user = users[session["auth"]]
    
    # Update user information
    update_data = {"name": name}
    if user.role == "instructor" and department is not None:
        update_data["department"] = department
    
    # Update the user record
    users.update(user.email, update_data)
    
    # Redirect back to profile with success message
    return fh.RedirectResponse("/profile", status_code=303)


@rt("/profile/change-password")
@login_required
def change_password_form(session):
    """Change password form"""
    user = users[session["auth"]]
    
    # Sidebar content
    sidebar_content = fh.Div(
        fh.Div(
            fh.H3("Change Password", cls="font-semibold text-slate-800 mb-4"),
            fh.P("Update your account password.", cls="text-gray-600 mb-4"),
            action_button("Cancel", color="gray", href="/profile", icon="×"),
            cls="p-4 bg-white rounded-xl shadow-md border border-gray-100",
        )
    )
    
    # Main content - Password change form
    main_content = fh.Div(
        fh.H1("Change Password", cls="text-3xl font-bold text-slate-800 mb-6"),
        fh.Form(
            card(
                fh.Div(
                    fh.H2("Update Password", cls="text-xl font-bold text-slate-700 mb-4"),
                    # Current password
                    fh.Div(
                    fh.Label(
                        "Current Password",
                        for_="current_password",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    fh.Input(
                        type="password",
                        id="current_password",
                        name="current_password",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        required=True,
                    ),
                    cls="mb-4",
                ),
                # New password
                fh.Div(
                    fh.Label(
                        "New Password",
                        for_="new_password",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    fh.Input(
                        type="password",
                        id="new_password",
                        name="new_password",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        required=True,
                        minlength="8",
                    ),
                    fh.P(
                        "Minimum 8 characters",
                        cls="text-sm text-gray-500 mt-1",
                    ),
                    cls="mb-4",
                ),
                # Confirm new password
                fh.Div(
                    fh.Label(
                        "Confirm New Password",
                        for_="confirm_password",
                        cls="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    fh.Input(
                        type="password",
                        id="confirm_password",
                        name="confirm_password",
                        cls="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                        required=True,
                        minlength="8",
                    ),
                    cls="mb-6",
                ),
                # Submit buttons
                fh.Div(
                    fh.Button(
                        "Update Password",
                        type="submit",
                        cls="bg-amber-600 text-white px-6 py-2 rounded-md hover:bg-amber-700 transition-colors mr-4",
                    ),
                    fh.A(
                        "Cancel",
                        href="/profile",
                        cls="bg-gray-200 text-gray-700 px-6 py-2 rounded-md hover:bg-gray-300 transition-colors inline-block",
                    ),
                    cls="flex items-center",
                ),
                )
            ),
            method="post",
            action="/profile/update-password",
            hx_boost="true",
            hx_target="#password-result",
        ),
        fh.Div(id="password-result"),
    )
    
    return dashboard_layout(
        "Change Password",
        sidebar_content,
        main_content,
        user_role=user.role,
        current_path="/profile",
    )


@rt("/profile/update-password")
@login_required
def update_password(session, current_password: str, new_password: str, confirm_password: str):
    """Handle password update"""
    user = users[session["auth"]]
    
    # Validate current password
    if not verify_password(current_password, user.password):
        return fh.Div(
            fh.P(
                "Current password is incorrect",
                cls="text-red-600 bg-red-50 p-4 rounded-lg mb-4",
            ),
            id="password-result",
        )
    
    # Validate new passwords match
    if new_password != confirm_password:
        return fh.Div(
            fh.P(
                "New passwords do not match",
                cls="text-red-600 bg-red-50 p-4 rounded-lg mb-4",
            ),
            id="password-result",
        )
    
    # Update password
    hashed_password = get_password_hash(new_password)
    users.update(user.email, {"password": hashed_password})
    
    # Return success message and redirect
    return fh.Div(
        fh.P(
            "Password updated successfully!",
            cls="text-green-600 bg-green-50 p-4 rounded-lg mb-4",
        ),
        fh.Script("setTimeout(() => window.location.href = '/profile', 1500)"),
        id="password-result",
    )


