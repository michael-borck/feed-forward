"""
Instructor routes - refactored into modules

All instructor routes have been organized into logical modules:
- dashboard: Main instructor dashboard
- models: AI model management
- courses: Course creation and management
- assignments: Assignment creation and rubric management
- submissions: Submission review and feedback approval
- students: Student enrollment and invitation management
- analytics: Performance analytics and reporting

This file imports all routes from the modules to maintain compatibility.
"""

# Import all routes from instructor modules
from app.routes.instructor.analytics import *
from app.routes.instructor.assignments import *
from app.routes.instructor.courses import *
from app.routes.instructor.dashboard import *
from app.routes.instructor.models import *
from app.routes.instructor.students import *
from app.routes.instructor.submissions import *
