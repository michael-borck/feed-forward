# Route Refactoring Guide for FeedForward

## Current Issues

The route files have grown large and contain multiple functions with the same names (`get`, `post`), which causes:
- MyPy errors about function redefinition
- Difficult navigation and maintenance
- Potential bugs from accidental overwrites

### File Sizes:
- `instructor.py`: 5,501 lines (too large!)
- `admin.py`: 1,963 lines
- `student.py`: 1,907 lines
- `auth.py`: 694 lines (reasonable)

## Recommended Refactoring Strategy

### 1. **Split Large Route Files by Feature**

#### instructor.py → Split into:
```
app/routes/instructor/
├── __init__.py
├── dashboard.py      # Dashboard and overview routes
├── courses.py        # Course management routes
├── assignments.py    # Assignment creation/editing
├── submissions.py    # Student submission review
├── feedback.py       # Feedback review and approval
├── analytics.py      # Analytics and reporting
└── models.py         # AI model configuration
```

#### admin.py → Split into:
```
app/routes/admin/
├── __init__.py
├── dashboard.py      # Admin dashboard
├── users.py          # User management
├── instructors.py    # Instructor approval/management
├── students.py       # Student enrollment
├── system.py         # System configuration
└── models.py         # AI model management
```

#### student.py → Split into:
```
app/routes/student/
├── __init__.py
├── dashboard.py      # Student dashboard
├── courses.py        # Course enrollment/viewing
├── assignments.py    # Assignment viewing
├── submissions.py    # Draft submission/management
└── feedback.py       # Viewing feedback
```

### 2. **Naming Convention for Route Functions**

Instead of generic `get` and `post`, use descriptive names:

```python
# Bad (current)
@rt("/instructor/dashboard")
def get(session, request):
    ...

@rt("/instructor/courses")
def get(session, request):  # Redefinition!
    ...

# Good (proposed)
@rt("/instructor/dashboard")
def instructor_dashboard(session, request):
    ...

@rt("/instructor/courses")
def instructor_courses_list(session, request):
    ...
```

### 3. **Implementation Steps**

1. **Create new directory structure**:
   ```bash
   mkdir -p app/routes/{instructor,admin,student}
   ```

2. **Move routes gradually**:
   - Start with the largest file (instructor.py)
   - Move related routes together
   - Update imports in app.py

3. **Update app.py imports**:
   ```python
   # Old
   from app.routes import admin, instructor, student, auth
   
   # New
   from app.routes import auth
   from app.routes.admin import dashboard as admin_dashboard
   from app.routes.admin import users as admin_users
   # ... etc
   ```

### 4. **Example Refactoring**

**Before** (in instructor.py):
```python
@rt("/instructor/dashboard")
def get(session, request):
    # Dashboard code
    
@rt("/instructor/courses")
def get(session, request):  # Duplicate name!
    # Courses code
```

**After** (in instructor/dashboard.py):
```python
from fasthtml.common import *

@rt("/instructor/dashboard")
def instructor_dashboard(session, request):
    # Dashboard code
```

**After** (in instructor/courses.py):
```python
from fasthtml.common import *

@rt("/instructor/courses")
def instructor_courses_list(session, request):
    # Courses code
```

### 5. **Benefits**

- ✅ No more function name conflicts
- ✅ Easier to find specific routes
- ✅ Better code organization
- ✅ Cleaner imports
- ✅ Easier testing
- ✅ Better type checking

### 6. **Migration Priority**

1. **High Priority**: instructor.py (5,500 lines)
2. **Medium Priority**: admin.py, student.py (~2,000 lines each)
3. **Low Priority**: auth.py (already reasonable size)

### 7. **Naming Guidelines**

Use this pattern for route functions:
```
{role}_{resource}_{action}

Examples:
- instructor_dashboard_view
- instructor_courses_list
- instructor_course_create
- instructor_assignment_edit
- admin_users_list
- admin_user_approve
- student_assignment_view
- student_draft_submit
```

This refactoring will significantly improve code maintainability and eliminate the duplicate function name issues.