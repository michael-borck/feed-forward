# Refactoring Example: Instructor Dashboard

This shows how to refactor the routes to avoid function name conflicts.

## Before (in instructor.py)
```python
@rt("/instructor/dashboard")
def get(session, request):  # Generic name "get"
    # dashboard code
    
@rt("/instructor/courses")  
def get(session, request):  # CONFLICT! Duplicate "get"
    # courses code
```

## After (in instructor/dashboard.py)
```python
@rt("/instructor/dashboard")
@instructor_required
def instructor_dashboard(session, request):  # Descriptive name
    """Main instructor dashboard view"""
    # dashboard code
```

## After (in instructor/courses.py)
```python
@rt("/instructor/courses")
@instructor_required
def instructor_courses_list(session, request):  # Descriptive name
    """List all instructor courses"""
    # courses code

@rt("/instructor/courses/{course_id}")
@instructor_required
def instructor_course_detail(session, request, course_id: int):
    """View specific course details"""
    # course detail code
```

## Key Benefits:
1. ✅ No more function name conflicts
2. ✅ Clear, descriptive function names
3. ✅ Better code organization
4. ✅ Easier to find specific routes
5. ✅ Type checking works properly

## Next Steps:
1. Continue splitting instructor.py into modules
2. Apply same pattern to admin.py and student.py
3. Update imports in app/routes/__init__.py
4. Test all routes still work
5. Run ruff and mypy to verify improvements