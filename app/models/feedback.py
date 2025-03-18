"""
Feedback-related model definitions
"""
from fasthtml.common import database
from app.models.user import db

# Define AI models table if it doesn't exist
ai_models = db.t.ai_models
if ai_models not in db.t:
    ai_models.create(dict(
        id=int,
        name=str,
        provider=str,
        model_id=str,
        api_config=str,  # JSON string containing API configuration
        active=bool,
        owner_type=str,  # 'system' or 'instructor'
        owner_id=str     # For instructor models, stores the instructor's email
    ), pk='id')
AIModel = ai_models.dataclass()

# Define drafts table if it doesn't exist
drafts = db.t.drafts
if drafts not in db.t:
    drafts.create(dict(
        id=int,
        assignment_id=int,
        student_email=str,
        version=int,
        content=str,
        submission_date=str,
        status=str  # 'submitted', 'processing', 'feedback_ready'
    ), pk='id')
Draft = drafts.dataclass()

# Define model runs table if it doesn't exist
model_runs = db.t.model_runs
if model_runs not in db.t:
    model_runs.create(dict(
        id=int,
        draft_id=int,
        model_id=int,
        run_number=int,
        timestamp=str,
        prompt=str,
        raw_response=str,
        status=str  # 'pending', 'complete', 'error'
    ), pk='id')
ModelRun = model_runs.dataclass()

# Define category scores table if it doesn't exist
category_scores = db.t.category_scores
if category_scores not in db.t:
    category_scores.create(dict(
        id=int,
        model_run_id=int,
        category_id=int,
        score=float,
        confidence=float
    ), pk='id')
CategoryScore = category_scores.dataclass()

# Define feedback items table if it doesn't exist
feedback_items = db.t.feedback_items
if feedback_items not in db.t:
    feedback_items.create(dict(
        id=int,
        model_run_id=int,
        category_id=int,
        type=str,  # 'strength', 'improvement', 'general'
        content=str,
        is_strength=bool,
        is_aggregated=bool
    ), pk='id')
FeedbackItem = feedback_items.dataclass()

# Define aggregated feedback table if it doesn't exist
aggregated_feedback = db.t.aggregated_feedback
if aggregated_feedback not in db.t:
    aggregated_feedback.create(dict(
        id=int,
        draft_id=int,
        category_id=int,
        aggregated_score=float,
        feedback_text=str,
        edited_by_instructor=bool,
        instructor_email=str,
        release_date=str,
        status=str  # 'pending_review', 'approved', 'released'
    ), pk='id')
AggregatedFeedback = aggregated_feedback.dataclass()