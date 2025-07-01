"""
Privacy-related utility functions for the FeedForward application

These functions help manage data lifecycle and privacy concerns related to
student submissions and other sensitive data.
"""

from datetime import datetime


def calculate_word_count(text):
    """Calculate the word count of a text submission"""
    if not text:
        return 0
    return len(text.split())


def cleanup_draft_content(draft):
    """
    Remove content from a draft, preserving only metadata and statistics

    Args:
        draft: The Draft object to clean up

    Returns:
        Updated draft with content removed
    """
    from app.models.feedback import drafts

    # Store word count before removing content
    word_count = calculate_word_count(draft.content)

    # Clear content unless specifically marked for preservation
    if not getattr(draft, "content_preserved", False):
        draft.content = "[Content removed for privacy]"
        draft.content_removed_date = datetime.now().isoformat()
        draft.word_count = word_count

        # Update the draft in the database
        drafts.update(draft)

    return draft


def cleanup_drafts_after_feedback():
    """
    Scheduled job to clean up draft content after feedback has been generated
    This should be called periodically to ensure privacy
    """
    from app.models.feedback import drafts

    cleaned_count = 0
    for draft in drafts():
        # Only clean up drafts with feedback that haven't been cleaned yet
        if (
            draft.status == "feedback_ready"
            and draft.content != "[Content removed for privacy]"
            and not getattr(draft, "content_preserved", False)
        ):
            cleanup_draft_content(draft)
            cleaned_count += 1

    return cleaned_count


def remove_student_content_after_delay(draft_id, delay_days=7):
    """
    Schedule content removal for privacy protection
    In a production system, this would use a task queue like Celery
    For demo purposes, this is a placeholder function
    """
    import logging
    from datetime import timedelta

    logger = logging.getLogger(__name__)
    removal_date = datetime.now() + timedelta(days=delay_days)
    logger.info(f"Content removal scheduled for draft {draft_id} on {removal_date}")

    # In production, this would:
    # 1. Add a task to a queue (Celery, RQ, etc.)
    # 2. Execute the cleanup after the specified delay
    # 3. Update the draft record accordingly

    # For demo purposes, we'll just log the scheduling
    return True
