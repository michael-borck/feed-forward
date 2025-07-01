"""
Admin routes - refactored into modules

All admin routes have been organized into logical modules:
- dashboard: Main admin dashboard
- instructors: Instructor approval and management
- domains: Domain whitelist management
- models: AI model configuration and management

This file imports all routes from the modules to maintain compatibility.

Note: The AI models module contains simplified placeholder implementations
for some routes due to the complexity of the original code. The core
functionality (list, basic CRUD) is implemented, but advanced features
like comprehensive model testing and detailed configuration may need
additional implementation.
"""

# Import all routes from admin modules
from app.routes.admin.dashboard import *
from app.routes.admin.domains import *
from app.routes.admin.instructors import *
from app.routes.admin.models import *
