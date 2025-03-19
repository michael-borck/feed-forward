"""
Admin routes - user management, system configuration, etc.
"""
from fasthtml.common import *
from starlette.responses import RedirectResponse

from app.models.user import User, Role, users
from app.models.course import Course, Enrollment, courses, enrollments
from app.models.feedback import AIModel
from app.models.config import SystemConfig, AggregationMethod, FeedbackStyle, MarkDisplayOption, DomainWhitelist, domain_whitelist

from app import app, rt, admin_required

# --- Admin Dashboard ---
@rt('/admin/dashboard')
@admin_required
def get(session):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button
    
    # Sidebar content
    sidebar_content = Div(
        # User welcome card
        Div(
            H3("Welcome, " + user.name, cls="text-xl font-semibold text-indigo-900 mb-2"),
            P("Admin Account", cls="text-gray-600 mb-4"),
            Div(
                # System stats summary
                Div(
                    Div(
                        "3", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Total Users", cls="text-gray-600"),
                    cls="flex items-center space-x-2 mb-2"
                ),
                # Pending approvals summary
                Div(
                    Div(
                        "0", 
                        cls="text-indigo-700 font-bold"
                    ),
                    P("Pending Approvals", cls="text-gray-600"),
                    cls="flex items-center space-x-2"
                ),
                cls="space-y-2"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Quick actions section
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Approve Instructors", color="indigo", href="/admin/instructors/approve", icon="✓"),
                action_button("Manage Instructors", color="teal", href="/admin/instructors", icon="👨‍🏫"),
                action_button("Manage Users", color="teal", href="/admin/users", icon="👥"),
                action_button("Domain Whitelist", color="amber", href="/admin/domains", icon="🔑"),
                action_button("System Settings", color="indigo", href="/admin/settings", icon="⚙️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content
    main_content = Div(
        # System stats
        Div(
            Div(
                # Users card
                card(
                    Div(
                        H3("3", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("Total Users", cls="text-gray-600"),
                        P("Last updated today", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # Courses card
                card(
                    Div(
                        H3("0", cls="text-4xl font-bold text-teal-700 mb-2"),
                        P("Active Courses", cls="text-gray-600"),
                        P("Across all instructors", cls="text-xs text-gray-500 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                # System health card
                card(
                    Div(
                        H3("100%", cls="text-4xl font-bold text-indigo-700 mb-2"),
                        P("System Health", cls="text-gray-600"),
                        P("All services operational", cls="text-xs text-green-600 mt-2"),
                        cls="text-center p-4"
                    ),
                    padding=0
                ),
                cls="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
            )
        ),
        
        # User Management
        Div(
            H2("User Management", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3("Instructor Approval", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("No pending instructor approvals.", cls="text-gray-500 italic"),
                    Div(
                        action_button("View All", color="indigo", href="/admin/instructors/approve", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ),
                Div(
                    H3("Recent Users", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("3 users registered in the system.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Manage Users", color="teal", href="/admin/users", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                cls="mb-8"
            )
        ),
        
        # System Configuration
        Div(
            H2("System Configuration", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                Div(
                    H3("AI Models", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("Configure the AI models used for feedback generation.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Configure Models", color="indigo", href="/admin/ai-models", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-4"
                ),
                Div(
                    H3("Feedback Settings", cls="text-lg font-semibold text-indigo-800 mb-4"),
                    P("Adjust global feedback settings and templates.", cls="text-gray-600 mb-2"),
                    Div(
                        action_button("Adjust Settings", color="teal", href="/admin/feedback-settings", size="small"),
                        cls="mt-4"
                    ),
                    cls="bg-white p-6 rounded-xl shadow-md border border-gray-100"
                ),
                cls="mb-8"
            )
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Admin Dashboard | FeedForward",
        dashboard_layout(
            "Admin Dashboard", 
            sidebar_content, 
            main_content, 
            user_role=Role.ADMIN
        )
    )

# --- Approve Instructors Route ---
@rt('/admin/instructors/approve')
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session['auth']]
    from app.utils.ui import dashboard_layout, card, action_button, data_table
    
    # Get all instructors that need approval
    pending_instructors = []
    for instructor in users():
        if instructor.role == Role.INSTRUCTOR and not instructor.approved:
            pending_instructors.append(instructor)
    
    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/admin/dashboard", icon="←"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Admin actions
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Manage Users", color="teal", href="/admin/users", icon="👥"),
                action_button("System Settings", color="indigo", href="/admin/settings", icon="⚙️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - Instructor approval list
    main_content = Div(
        H1("Approve Instructors", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P("Review and approve instructor account requests.", cls="text-gray-600 mb-8"),
        
        # Instructor approval table
        Div(
            Div(
                H2("Pending Approval", cls="text-2xl font-bold text-indigo-900 mb-4"),
                
                # Check if there are pending instructors
                (Div(
                    Table(
                        Thead(
                            Tr(
                                Th("Name", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Email", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Department", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                                Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                            ),
                            cls="bg-indigo-50"
                        ),
                        Tbody(
                            *(Tr(
                                Td(instructor.name, cls="py-4 px-6"),
                                Td(instructor.email, cls="py-4 px-6"),
                                Td(instructor.department or "Not specified", cls="py-4 px-6"),
                                Td(
                                    Div(
                                        Button("Approve", 
                                               cls="bg-teal-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-teal-700 transition-colors shadow-sm",
                                               hx_post=f"/admin/instructors/approve/{instructor.email}",
                                               hx_swap="outerHTML"),
                                        Button("Reject", 
                                               cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                               hx_post=f"/admin/instructors/reject/{instructor.email}",
                                               hx_swap="outerHTML"),
                                        cls="flex"
                                    ),
                                    cls="py-4 px-6"
                                )
                            ) for instructor in pending_instructors)
                        ),
                        cls="w-full"
                    ),
                    cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
                )) if pending_instructors else 
                Div(
                    P("No pending instructor approvals at this time.", 
                      cls="text-gray-500 italic text-center py-8"),
                    cls="bg-white rounded-lg shadow-md border border-gray-100 w-full"
                ),
                Div(cls="mb-8")
            )
        ),
        
        # Back button
        Div(
            action_button("Back to Dashboard", color="gray", href="/admin/dashboard", icon="←"),
            cls="mt-4"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Approve Instructors | FeedForward",
        dashboard_layout(
            "Approve Instructors", 
            sidebar_content, 
            main_content, 
            user_role=Role.ADMIN
        )
    )

# --- Approve Instructor API ---
@rt('/admin/instructors/approve/{email}')
@admin_required
def post(session, email: str):
    try:
        # Get the instructor
        instructor = users[email]
        
        # Update approval status
        instructor.approved = True
        users.update(instructor)
        
        # Return success message with auto-refresh
        return Div(
            P("Approved successfully", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
            cls="py-2 px-4"
        )
    except:
        # Return error message
        return Div(
            P("Error approving instructor", cls="text-red-500"),
            cls="py-2 px-4"
        )

# --- Reject Instructor API ---
@rt('/admin/instructors/reject/{email}')
@admin_required
def post(session, email: str):
    try:
        # Get the instructor and delete
        users.delete(email)
        
        # Return success message with auto-refresh
        return Div(
            P("Rejected and removed", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);"),
            cls="py-2 px-4"
        )
    except:
        # Return error message
        return Div(
            P("Error rejecting instructor", cls="text-red-500"),
            cls="py-2 px-4"
        )

# --- Instructor Management ---
@rt('/admin/instructors')
@admin_required
def get(session):
    # Get current user
    user = users[session['auth']]
    
    # Import UI components
    from app.utils.ui import dashboard_layout, card, action_button
    
    # Get all instructors who aren't deleted
    instructor_list = []
    for u in users():
        if u.role == Role.INSTRUCTOR and (not hasattr(u, 'status') or u.status \!= "deleted"):
            instructor_list.append(u)
    
    # Create instructor management content
    management_content = Div(
        Div(
            H2("Manage Instructors", cls="text-2xl font-bold text-indigo-900 mb-6"),
            Div(
                H3(f"{len(instructor_list)} Instructors", cls="text-xl font-bold text-indigo-800 mb-4"),
                Div(
                    P("• Manage instructor accounts", cls="text-gray-600 mb-1"),
                    P("• Approve new instructor registrations", cls="text-gray-600 mb-1"),
                    P("• Remove instructors from the system", cls="text-gray-600"),
                    cls="text-sm mb-4"
                ),
                cls="bg-indigo-50 p-4 rounded-lg mb-6"
            ),
            
            # Instructor table
            Div(
                Table(
                    Thead(
                        Tr(
                            Th("Name", cls="px-4 py-3 text-left text-sm font-semibold text-gray-700"),
                            Th("Email", cls="px-4 py-3 text-left text-sm font-semibold text-gray-700"),
                            Th("Status", cls="px-4 py-3 text-left text-sm font-semibold text-gray-700"),
                            Th("Department", cls="px-4 py-3 text-left text-sm font-semibold text-gray-700"),
                            Th("Actions", cls="px-4 py-3 text-left text-sm font-semibold text-gray-700"),
                            cls="bg-gray-100"
                        )
                    ),
                    Tbody(
                        *(Tr(
                            Td(instructor.name, cls="px-4 py-3 text-sm text-gray-800"),
                            Td(instructor.email, cls="px-4 py-3 text-sm text-gray-800"),
                            Td(
                                (Span("✅ Approved", 
                                    cls="px-3 py-1 rounded-full text-xs bg-green-100 text-green-800") 
                                if instructor.approved else
                                Span("⏳ Pending Approval", 
                                    cls="px-3 py-1 rounded-full text-xs bg-amber-100 text-amber-800")),
                                cls="px-4 py-3"
                            ),
                            Td(instructor.department or "Not specified", cls="px-4 py-3 text-sm text-gray-800"),
                            Td(
                                Div(
                                    (Button("Approve",
                                        cls="text-xs px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 mr-2",
                                        hx_post=f"/admin/instructors/approve/{instructor.email}",
                                        hx_target="#message") 
                                    if not instructor.approved else
                                    Span("", cls="")),
                                    Button("Remove",
                                        cls="text-xs px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700",
                                        hx_post=f"/admin/instructors/remove/{instructor.email}",
                                        hx_confirm=f"Are you sure you want to remove {instructor.email}? This will delete their account and cannot be undone.",
                                        hx_target="#message")
                                ),
                                cls="px-4 py-3"
                            ),
                            cls="border-b border-gray-200 hover:bg-gray-50"
                        ) for instructor in instructor_list)
                    ),
                    cls="min-w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow border border-gray-200"
            ),
            
            # Message area for feedback
            Div(id="message", cls="mt-6"),
            
            cls=""
        ),
        cls="p-6"
    )
    
    # Create sidebar content
    sidebar_content = Div(
        Div(
            H3("Admin Actions", cls="text-xl font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/admin/dashboard", icon="←"),
                action_button("Approve Instructors", color="indigo", href="/admin/instructors/approve", icon="✓"),
                action_button("Domain Whitelist", color="amber", href="/admin/domains", icon="🔑"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        Div(
            H3("Instructor Stats", cls="text-xl font-semibold text-indigo-900 mb-4"),
            P(f"Total: {len(instructor_list)}", cls="text-gray-600 mb-2"),
            P(f"Approved: {sum(1 for i in instructor_list if i.approved)}", cls="text-green-600 mb-2"),
            P(f"Pending: {sum(1 for i in instructor_list if not i.approved)}", cls="text-amber-600 mb-2"),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Return the complete page
    return Titled(
        "Manage Instructors | FeedForward",
        dashboard_layout(
            "Manage Instructors", 
            sidebar_content, 
            management_content, 
            user_role=Role.ADMIN
        )
    )

# --- Remove Instructor ---
@rt('/admin/instructors/remove/{email}')
@admin_required
def post(session, email: str):
    # Get current user
    admin_user = users[session['auth']]
    
    # Don't allow removing self
    if email == admin_user.email:
        return Div(
            P("You cannot remove your own account.", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )
    
    try:
        # Get the instructor
        instructor = users[email]
        
        # Check if this is actually an instructor
        if instructor.role \!= Role.INSTRUCTOR:
            return Div(
                P("This user is not an instructor.", cls="text-red-600"),
                cls="bg-red-50 p-4 rounded-lg"
            )
        
        # Import datetime for timestamp updates
        from datetime import datetime
        
        # Remove all enrollments for courses taught by this instructor
        for c in courses():
            if c.instructor_email == email:
                # Soft delete all enrollments for this course
                for e in enrollments():
                    if e.course_id == c.id:
                        try:
                            # No status field in enrollments yet, so we'll still need to hard delete
                            enrollments.delete(e.id)
                        except:
                            pass
                
                # Soft delete the course
                try:
                    c.status = "deleted"
                    c.updated_at = datetime.now().isoformat()
                    courses.update(c)
                except:
                    pass
        
        # Soft delete the instructor account
        instructor.status = "deleted"
        instructor.last_active = datetime.now().isoformat()
        users.update(instructor)
        
        return Div(
            P(f"Instructor {email} has been removed from the system.", cls="text-green-600"),
            Script("setTimeout(function() { window.location.reload(); }, 1500);"),
            cls="bg-green-50 p-4 rounded-lg"
        )
    except Exception as e:
        return Div(
            P(f"Error removing instructor: {str(e)}", cls="text-red-600"),
            cls="bg-red-50 p-4 rounded-lg"
        )

# --- Domain Whitelist Management ---
@rt('/admin/domains')
@admin_required
def get(session):
    # Get current user and UI components
    user = users[session['auth']]
    from app.utils.ui import dashboard_layout, card, action_button
    
    # Get all domains from the whitelist
    all_domains = list(domain_whitelist.select())
    
    # Sidebar content
    sidebar_content = Div(
        # Quick navigation
        Div(
            H3("Admin Navigation", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Dashboard", color="gray", href="/admin/dashboard", icon="←"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        ),
        
        # Admin actions
        Div(
            H3("Admin Actions", cls="font-semibold text-indigo-900 mb-4"),
            Div(
                action_button("Approve Instructors", color="indigo", href="/admin/instructors/approve", icon="✓"),
                action_button("Manage Users", color="teal", href="/admin/users", icon="👥"),
                action_button("System Settings", color="indigo", href="/admin/settings", icon="⚙️"),
                cls="space-y-3"
            ),
            cls="mb-6 p-4 bg-white rounded-xl shadow-md border border-gray-100"
        )
    )
    
    # Main content - Domain whitelist management
    main_content = Div(
        H1("Domain Whitelist Management", cls="text-3xl font-bold text-indigo-900 mb-6"),
        P("Configure which domains are allowed for instructor registration and whether they're auto-approved.", cls="text-gray-600 mb-8"),
        
        # Add new domain form
        Div(
            H2("Add New Domain", cls="text-2xl font-bold text-indigo-900 mb-4"),
            Form(
                Div(
                    Div(
                        Label("Domain", for_="domain", cls="block text-indigo-900 font-medium mb-1"),
                        P("e.g. 'curtin.edu.au' (without 'http://' or '@')", cls="text-sm text-gray-500 mb-1"),
                        Input(id="domain", type="text", placeholder="Domain name", required=True,
                              cls="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"),
                        cls="mb-4 w-full"
                    ),
                    Div(
                        Div(
                            Input(type="checkbox", id="auto_approve", 
                                  cls="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"),
                            Label("Auto-approve instructors from this domain", for_="auto_approve", 
                                  cls="ml-2 block text-indigo-900 font-medium"),
                            cls="flex items-center" 
                        ),
                        cls="mb-6"
                    ),
                    Div(
                        Button("Add Domain", type="submit", 
                              cls="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors shadow-sm"),
                        cls="mb-4"
                    ),
                    Span(id="domain_result", cls="block text-center"),
                    cls="flex flex-wrap"
                ),
                hx_post="/admin/domains/add",
                hx_target="#domain_result",
                hx_swap="innerHTML",
                cls="bg-white p-6 rounded-xl shadow-md border border-gray-100 mb-8"
            )
        ),
        
        # Domain list
        Div(
            H2("Current Domains", cls="text-2xl font-bold text-indigo-900 mb-4"),
            
            # Check if there are domains
            (Div(
                Table(
                    Thead(
                        Tr(
                            Th("Domain", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Auto-approve", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100"),
                            Th("Actions", cls="text-left py-4 px-6 font-semibold text-indigo-900 border-b-2 border-indigo-100")
                        ),
                        cls="bg-indigo-50"
                    ),
                    Tbody(
                        *(Tr(
                            Td(domain['domain'], cls="py-4 px-6"),
                            Td(
                                Span("✅ Yes" if domain['auto_approve_instructor'] else "❌ No", 
                                     cls="px-3 py-1 rounded-full text-sm " + 
                                     ("bg-green-100 text-green-800" if domain['auto_approve_instructor'] else 
                                      "bg-red-100 text-red-800")),
                                cls="py-4 px-6"
                            ),
                            Td(
                                Div(
                                    Button("Toggle Auto-approve", 
                                           cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                                           hx_post=f"/admin/domains/toggle/{domain['id']}",
                                           hx_target="closest tr",
                                           hx_swap="outerHTML"),
                                    Button("Delete", 
                                           cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                                           hx_post=f"/admin/domains/delete/{domain['id']}",
                                           hx_target="closest tr",
                                           hx_swap="outerHTML"),
                                    cls="flex"
                                ),
                                cls="py-4 px-6"
                            )
                        ) for domain in all_domains)
                    ),
                    cls="w-full"
                ),
                cls="overflow-x-auto bg-white rounded-lg shadow-md border border-gray-100"
            )) if all_domains else 
            Div(
                P("No domains in the whitelist. Add some domains to allow instructor registration.", 
                  cls="text-gray-500 italic text-center py-8"),
                cls="bg-white rounded-lg shadow-md border border-gray-100 w-full"
            ),
            cls="mb-8"
        ),
        
        # Back button
        Div(
            action_button("Back to Dashboard", color="gray", href="/admin/dashboard", icon="←"),
            cls="mt-4"
        )
    )
    
    # Use the dashboard layout with our components
    return Titled(
        "Domain Whitelist | FeedForward",
        dashboard_layout(
            "Domain Whitelist", 
            sidebar_content, 
            main_content, 
            user_role=Role.ADMIN
        )
    )

# --- Add Domain to Whitelist ---
@rt('/admin/domains/add')
@admin_required
def post(session, domain: str, auto_approve: bool = False):
    # Basic validation
    if not domain:
        return Div(P("Domain name is required", cls="text-red-500"))
    
    # Clean up domain
    domain = domain.strip().lower()
    
    # Remove any protocol or @ symbol
    domain = domain.replace("http://", "").replace("https://", "").replace("@", "")
    
    # Check if domain already exists
    for existing in domain_whitelist.select():
        if existing['domain'] == domain:
            return Div(P(f"Domain '{domain}' already exists in the whitelist", cls="text-amber-500"))
    
    try:
        # Get next available ID
        next_id = 1
        existing_ids = [d['id'] for d in domain_whitelist.select()]
        if existing_ids:
            next_id = max(existing_ids) + 1
        
        # Create timestamp
        from datetime import datetime
        now = datetime.now().isoformat()
        
        # Create new domain entry
        new_domain = DomainWhitelist(
            id=next_id,
            domain=domain,
            auto_approve_instructor=auto_approve,
            created_at=now,
            updated_at=now
        )
        
        # Add to database
        domain_whitelist.insert(new_domain)
        
        # Return success message with page reload
        return Div(
            P(f"Added domain '{domain}' to the whitelist", cls="text-green-500"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);")
        )
    except Exception as e:
        # Return error message
        return Div(P(f"Error adding domain: {str(e)}", cls="text-red-500"))

# --- Toggle Auto-approve for Domain ---
@rt('/admin/domains/toggle/{id}')
@admin_required
def post(session, id: int):
    try:
        # Find the domain
        domain_record = None
        for d in domain_whitelist.select():
            if d['id'] == id:
                domain_record = d
                break
        
        if not domain_record:
            return "Domain not found"
        
        # Toggle auto-approve
        domain_record['auto_approve_instructor'] = not domain_record['auto_approve_instructor']
        
        # Update timestamp
        from datetime import datetime
        domain_record['updated_at'] = datetime.now().isoformat()
        
        # Save changes
        domain_whitelist.update(domain_record)
        
        # Return updated row
        return Tr(
            Td(domain_record['domain'], cls="py-4 px-6"),
            Td(
                Span("✅ Yes" if domain_record['auto_approve_instructor'] else "❌ No", 
                     cls="px-3 py-1 rounded-full text-sm " + 
                     ("bg-green-100 text-green-800" if domain_record['auto_approve_instructor'] else 
                      "bg-red-100 text-red-800")),
                cls="py-4 px-6"
            ),
            Td(
                Div(
                    Button("Toggle Auto-approve", 
                           cls="bg-amber-600 text-white px-4 py-2 rounded-lg mr-2 hover:bg-amber-700 transition-colors shadow-sm",
                           hx_post=f"/admin/domains/toggle/{id}",
                           hx_target="closest tr",
                           hx_swap="outerHTML"),
                    Button("Delete", 
                           cls="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors shadow-sm",
                           hx_post=f"/admin/domains/delete/{id}",
                           hx_target="closest tr",
                           hx_swap="outerHTML"),
                    cls="flex"
                ),
                cls="py-4 px-6"
            )
        )
    except Exception as e:
        return f"Error updating domain: {str(e)}"

# --- Delete Domain from Whitelist ---
@rt('/admin/domains/delete/{id}')
@admin_required
def post(session, id: int):
    try:
        # Find the domain
        domain_found = False
        for d in domain_whitelist.select():
            if d['id'] == id:
                domain_found = True
                break
        
        if not domain_found:
            return "Domain not found"
        
        # Delete the domain
        domain_whitelist.delete(id)
        
        # Return deleted confirmation
        return Div(
            P("Domain deleted", cls="text-green-500 p-4"),
            Script("setTimeout(function() { window.location.reload(); }, 1000);")
        )
    except Exception as e:
        return f"Error deleting domain: {str(e)}"
