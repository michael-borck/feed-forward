"""
System configuration and settings model definitions
"""
from fasthtml.common import database
from app.models.user import db

# Define system configuration table if it doesn't exist
system_config = db.t.system_config
if system_config not in db.t:
    system_config.create(dict(
        key=str,
        value=str,
        description=str
    ), pk='key')
SystemConfig = system_config.dataclass()

# Define aggregation methods table if it doesn't exist
aggregation_methods = db.t.aggregation_methods
if aggregation_methods not in db.t:
    aggregation_methods.create(dict(
        id=int,
        name=str,
        description=str,
        is_active=bool
    ), pk='id')
AggregationMethod = aggregation_methods.dataclass()

# Define feedback styles table if it doesn't exist
feedback_styles = db.t.feedback_styles
if feedback_styles not in db.t:
    feedback_styles.create(dict(
        id=int,
        name=str,
        description=str,
        is_active=bool
    ), pk='id')
FeedbackStyle = feedback_styles.dataclass()

# Define mark display options table if it doesn't exist
mark_display_options = db.t.mark_display_options
if mark_display_options not in db.t:
    mark_display_options.create(dict(
        id=int,
        display_type=str,  # 'numeric', 'hidden', 'icon'
        name=str,
        description=str,
        icon_type=str,
        is_active=bool
    ), pk='id')
MarkDisplayOption = mark_display_options.dataclass()

# Define assignment settings table if it doesn't exist
assignment_settings = db.t.assignment_settings
if assignment_settings not in db.t:
    assignment_settings.create(dict(
        id=int,
        assignment_id=int,
        ai_model_id=int,
        num_runs=int,
        aggregation_method_id=int,
        feedback_style_id=int,
        require_review=bool,
        mark_display_option_id=int
    ), pk='id')
AssignmentSettings = assignment_settings.dataclass()