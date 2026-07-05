"""
Background task handling for asynchronous operations.

Consolidated from the original services/background_tasks.py and
utils/feedback_pipeline.py. Supports both asyncio task creation (when
running inside an event loop) and thread-based fallback for non-async
callers.
"""

import asyncio
import logging
import threading
from typing import Optional

from app.services.feedback_generator import process_draft_submission

# Configure logging
logger = logging.getLogger(__name__)

# Task tracking — maps draft_id to asyncio.Task or threading.Thread
active_tasks: dict[int, asyncio.Task | threading.Thread] = {}


async def queue_feedback_generation(draft_id: int) -> bool:
    """
    Queue a draft for feedback generation in the background.

    Must be called from within a running event loop. The task is tracked
    by draft_id so duplicate submissions are prevented.

    Args:
        draft_id: ID of the draft to process

    Returns:
        True if task was queued successfully
    """
    try:
        # Prevent duplicate processing
        if draft_id in active_tasks:
            existing = active_tasks[draft_id]
            if isinstance(existing, asyncio.Task) and not existing.done():
                logger.info(f"Draft {draft_id} is already being processed")
                return False
            if isinstance(existing, threading.Thread) and existing.is_alive():
                logger.info(f"Draft {draft_id} is already being processed (thread)")
                return False
            # Stale entry — remove it
            active_tasks.pop(draft_id, None)

        # Create and track the task
        task = asyncio.create_task(_process_draft_with_tracking(draft_id))
        active_tasks[draft_id] = task

        logger.info(f"Queued draft {draft_id} for feedback generation")
        return True

    except Exception as e:
        logger.error(f"Error queuing draft {draft_id}: {e!s}")
        return False


def queue_feedback_generation_sync(draft_id: int) -> bool:
    """
    Queue feedback generation from a non-async context using a background
    thread. Useful when calling outside of an event loop.

    Args:
        draft_id: ID of the draft to process

    Returns:
        True if task was queued successfully
    """
    try:
        if draft_id in active_tasks:
            existing = active_tasks[draft_id]
            if isinstance(existing, asyncio.Task) and not existing.done():
                logger.info(f"Draft {draft_id} is already being processed")
                return False
            if isinstance(existing, threading.Thread) and existing.is_alive():
                logger.info(f"Draft {draft_id} is already being processed (thread)")
                return False
            active_tasks.pop(draft_id, None)

        thread = threading.Thread(
            target=_process_draft_in_thread,
            args=(draft_id,),
            daemon=True,
        )
        active_tasks[draft_id] = thread
        thread.start()

        logger.info(f"Started background thread for draft {draft_id}")
        return True

    except Exception as e:
        logger.error(f"Error starting thread for draft {draft_id}: {e!s}")
        return False


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------


async def _process_draft_with_tracking(draft_id: int):
    """Process a draft via asyncio and clean up tracking when done."""
    try:
        success = await process_draft_submission(draft_id)

        if success:
            logger.info(f"Successfully processed draft {draft_id}")
        else:
            logger.error(f"Failed to process draft {draft_id}")

    except Exception as e:
        logger.error(f"Error processing draft {draft_id}: {e!s}")

    finally:
        active_tasks.pop(draft_id, None)


def _process_draft_in_thread(draft_id: int):
    """Wrapper that creates a new event loop in a thread for async processing."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_process_draft_with_tracking(draft_id))
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Background thread failed for draft {draft_id}: {e!s}")
    finally:
        active_tasks.pop(draft_id, None)


def get_task_status(draft_id: int) -> Optional[str]:
    """
    Get the status of a feedback generation task.

    Args:
        draft_id: ID of the draft

    Returns:
        Status string or None if not tracked
    """
    if draft_id not in active_tasks:
        return None

    entry = active_tasks[draft_id]

    if isinstance(entry, asyncio.Task):
        if entry.done():
            return "completed"
        if entry.cancelled():
            return "cancelled"
        return "processing"

    if isinstance(entry, threading.Thread):
        if entry.is_alive():
            return "processing"
        return "completed"

    return None


def retry_failed_processing(draft_id: int, background: bool = True) -> bool:
    """
    Retry processing for a failed draft.

    Args:
        draft_id: ID of the draft to retry
        background: If True, run in a background thread; otherwise block.

    Returns:
        True if retry was initiated
    """
    from app.models.feedback import drafts

    try:
        draft = drafts[draft_id]
        draft.status = "submitted"
        drafts.update(draft)

        if background:
            return queue_feedback_generation_sync(draft_id)
        else:
            loop = asyncio.new_event_loop()
            try:
                loop.run_until_complete(process_draft_submission(draft_id))
            finally:
                loop.close()
            return True

    except Exception as e:
        logger.error(f"Failed to retry processing for draft {draft_id}: {e!s}")
        return False


async def cleanup_completed_tasks():
    """Clean up completed tasks from tracking."""
    completed = []

    for draft_id, entry in active_tasks.items():
        if (
            isinstance(entry, asyncio.Task) and (entry.done() or entry.cancelled())
        ) or (isinstance(entry, threading.Thread) and not entry.is_alive()):
            completed.append(draft_id)

    for draft_id in completed:
        active_tasks.pop(draft_id, None)

    if completed:
        logger.info(f"Cleaned up {len(completed)} completed tasks")
