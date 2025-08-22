"""
Feedback-related model definitions
"""

from app.models.user import db

# Define AI models table if it doesn't exist
ai_models = db.t.ai_models
if ai_models not in db.t:
    ai_models.create(
        {
            "id": int,
            "name": str,
            "provider": str,
            "model_id": str,
            "api_config": str,  # JSON string containing API configuration
            "active": bool,
            "owner_type": str,  # 'system' or 'instructor'
            "owner_id": str,  # For instructor models, stores the instructor's email
        },
        pk="id",
    )
AIModel = ai_models.dataclass()

# Define drafts table if it doesn't exist
drafts = db.t.drafts
if drafts not in db.t:
    drafts.create(
        {
            "id": int,
            "assignment_id": int,
            "student_email": str,
            "version": int,
            "content": str,  # Temporarily stores content until feedback is generated
            "content_preserved": bool,  # Flag to indicate if content should be preserved (defaults to False)
            "submission_date": str,
            "word_count": int,  # Store word count for statistics
            "status": str,  # 'submitted', 'processing', 'feedback_ready', 'archived'
            "content_removed_date": str,  # When the content was removed
            "hidden_by_student": bool,  # For "soft delete" functionality - hide from student view
            "submission_type": str,  # 'text', 'file', 'mixed'
            "submission_metadata": str,  # JSON metadata
            "preprocessing_status": str,  # 'pending', 'processing', 'complete', 'error'
            "preprocessing_result": str,  # JSON result from preprocessing
            "external_service_id": int,  # If processed by external service
        },
        pk="id",
    )
Draft = drafts.dataclass()

# Define model runs table if it doesn't exist
model_runs = db.t.model_runs
if model_runs not in db.t:
    model_runs.create(
        {
            "id": int,
            "draft_id": int,
            "model_id": int,
            "run_number": int,
            "timestamp": str,
            "prompt": str,
            "raw_response": str,
            "status": str,  # 'pending', 'complete', 'error'
            "preprocessing_service_id": int,  # Track which service processed the submission
            "service_response_time": float,  # Time in seconds
        },
        pk="id",
    )
ModelRun = model_runs.dataclass()

# Define category scores table if it doesn't exist
category_scores = db.t.category_scores
if category_scores not in db.t:
    category_scores.create(
        {"id": int, "model_run_id": int, "category_id": int, "score": float, "confidence": float},
        pk="id",
    )
CategoryScore = category_scores.dataclass()

# Define feedback items table if it doesn't exist
feedback_items = db.t.feedback_items
if feedback_items not in db.t:
    feedback_items.create(
        {
            "id": int,
            "model_run_id": int,
            "category_id": int,
            "type": str,  # 'strength', 'improvement', 'general'
            "content": str,
            "is_strength": bool,
            "is_aggregated": bool,
        },
        pk="id",
    )
FeedbackItem = feedback_items.dataclass()

# Define feedbacks table for instructor-approved feedback
feedbacks = db.t.feedbacks
if feedbacks not in db.t:
    feedbacks.create(
        {
            "id": int,
            "draft_id": int,
            "overall_score": float,
            "general_feedback": str,
            "rubric_scores": str,  # JSON string
            "instructor_approved": bool,
            "approved_at": str,
            "approved_by": str,
            "created_at": str,
        },
        pk="id",
    )
Feedback = feedbacks.dataclass()

# Define aggregated feedback table if it doesn't exist
aggregated_feedback = db.t.aggregated_feedback
if aggregated_feedback not in db.t:
    aggregated_feedback.create(
        {
            "id": int,
            "draft_id": int,
            "category_id": int,
            "aggregated_score": float,
            "feedback_text": str,
            "edited_by_instructor": bool,
            "instructor_email": str,
            "release_date": str,
            "status": str,  # 'pending_review', 'approved', 'released'
        },
        pk="id",
    )
AggregatedFeedback = aggregated_feedback.dataclass()
