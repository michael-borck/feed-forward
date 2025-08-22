"""
Student routes - refactored into modules

All student routes have been organized into logical modules:
- dashboard: Main student dashboard
- courses: Course views and course-specific assignment lists
- assignments: Individual assignment views and general assignment lists
- submissions: Draft submission forms, submission history, and management
- join: Course enrollment via invitation tokens

This file imports all routes from the modules to maintain compatibility.
"""

# Import all routes from student modules
from app.routes.student.assignments import *
from app.routes.student.courses import *
from app.routes.student.dashboard import *
from app.routes.student.join import *
from app.routes.student.submissions import *
