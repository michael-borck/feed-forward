"""
Background task handling for asynchronous operations
"""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from app.services.feedback_generator import process_draft_submission

# Configure logging
logger = logging.getLogger(__name__)

# Thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=4)

# Task tracking
active_tasks = {}


async def queue_feedback_generation(draft_id: int) -> bool:
    """
    Queue a draft for feedback generation in the background
    
    Args:
        draft_id: ID of the draft to process
        
    Returns:
        True if task was queued successfully
    """
    try:
        # Check if task is already running
        if draft_id in active_tasks:
            logger.info(f"Draft {draft_id} is already being processed")
            return False

        # Create and track the task
        task = asyncio.create_task(_process_draft_with_tracking(draft_id))
        active_tasks[draft_id] = task

        logger.info(f"Queued draft {draft_id} for feedback generation")
        return True

    except Exception as e:
        logger.error(f"Error queuing draft {draft_id}: {e!s}")
        return False


async def _process_draft_with_tracking(draft_id: int):
    """Process a draft and clean up tracking when done"""
    try:
        # Process the draft
        success = await process_draft_submission(draft_id)

        if success:
            logger.info(f"Successfully processed draft {draft_id}")
        else:
            logger.error(f"Failed to process draft {draft_id}")

    except Exception as e:
        logger.error(f"Error processing draft {draft_id}: {e!s}")

    finally:
        # Remove from active tasks
        active_tasks.pop(draft_id, None)


def get_task_status(draft_id: int) -> Optional[str]:
    """
    Get the status of a feedback generation task
    
    Args:
        draft_id: ID of the draft
        
    Returns:
        Status string or None if not found
    """
    if draft_id in active_tasks:
        task = active_tasks[draft_id]
        if task.done():
            return "completed"
        elif task.cancelled():
            return "cancelled"
        else:
            return "processing"
    return None


async def cleanup_completed_tasks():
    """Clean up completed tasks from tracking"""
    completed = []

    for draft_id, task in active_tasks.items():
        if task.done() or task.cancelled():
            completed.append(draft_id)

    for draft_id in completed:
        active_tasks.pop(draft_id, None)

    if completed:
        logger.info(f"Cleaned up {len(completed)} completed tasks")
