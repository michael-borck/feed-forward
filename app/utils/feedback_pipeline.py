"""
Feedback Pipeline - Async processing for draft submissions
Integrates with feedback orchestrator for background AI processing
"""

import asyncio
import logging
import threading
from datetime import datetime, timedelta

from app.models.feedback import drafts
from app.utils.feedback_orchestrator import feedback_orchestrator
from app.utils.privacy import remove_student_content_after_delay

logger = logging.getLogger(__name__)


class FeedbackPipeline:
    """Manages async feedback processing pipeline"""

    def __init__(self):
        self.processing_tasks = {}  # Track running tasks

    def process_draft_submission(self, draft_id: int, background: bool = True):
        """
        Trigger feedback processing for a new draft submission

        Args:
            draft_id: ID of the draft to process
            background: Whether to run in background thread (default True)
        """
        if background:
            # Start background processing
            thread = threading.Thread(
                target=self._process_draft_async_wrapper, args=(draft_id,), daemon=True
            )
            thread.start()
            logger.info(f"Started background feedback processing for draft {draft_id}")
        else:
            # Process synchronously (for testing)
            asyncio.run(self._process_draft_async(draft_id))

    def _process_draft_async_wrapper(self, draft_id: int):
        """Wrapper to run async processing in thread"""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Run the async processing
            result = loop.run_until_complete(self._process_draft_async(draft_id))

            # Clean up
            loop.close()

        except Exception as e:
            logger.error(f"Background processing failed for draft {draft_id}: {e!s}")

    async def _process_draft_async(self, draft_id: int):
        """Main async processing function"""
        try:
            logger.info(f"Starting feedback processing for draft {draft_id}")

            # Process feedback through orchestrator
            result = await feedback_orchestrator.process_draft_feedback(draft_id)

            if result.success:
                logger.info(
                    f"Feedback processing completed successfully for draft {draft_id}"
                )
                logger.info(
                    f"Models run: {result.successful_runs}/{result.total_models_run}"
                )

                # Schedule content removal for privacy (after 7 days default)
                self._schedule_content_removal(draft_id)

            else:
                logger.error(
                    f"Feedback processing failed for draft {draft_id}: {result.error_message}"
                )

                # Update draft status to indicate error
                try:
                    drafts.update(draft_id, {"status": "error"})
                except Exception as e:
                    logger.error(f"Failed to update draft status: {e!s}")

            return result

        except Exception as e:
            logger.error(f"Async processing error for draft {draft_id}: {e!s}")

            # Update draft status to indicate error
            try:
                drafts.update(draft_id, {"status": "error"})
            except:
                pass

            raise

    def _schedule_content_removal(self, draft_id: int, delay_days: int = 7):
        """Schedule content removal for privacy protection"""
        try:
            # For now, just log the scheduling
            # In production, this could use a task queue like Celery
            removal_date = datetime.now() + timedelta(days=delay_days)
            logger.info(
                f"Content removal scheduled for draft {draft_id} on {removal_date}"
            )

            # Immediately call the privacy function with delay
            remove_student_content_after_delay(draft_id, delay_days)

        except Exception as e:
            logger.error(
                f"Failed to schedule content removal for draft {draft_id}: {e!s}"
            )

    def get_processing_status(self, draft_id: int) -> dict:
        """Get current processing status for a draft"""
        return feedback_orchestrator.get_draft_feedback_status(draft_id)

    def retry_failed_processing(self, draft_id: int):
        """Retry processing for a failed draft"""
        try:
            # Reset draft status
            drafts.update(draft_id, {"status": "submitted"})

            # Restart processing
            self.process_draft_submission(draft_id)

            logger.info(f"Retrying feedback processing for draft {draft_id}")

        except Exception as e:
            logger.error(f"Failed to retry processing for draft {draft_id}: {e!s}")


# Global pipeline instance
feedback_pipeline = FeedbackPipeline()


# Convenience function for easy import
def process_draft_submission(draft_id: int, background: bool = True):
    """Process a draft submission through the AI feedback pipeline"""
    return feedback_pipeline.process_draft_submission(draft_id, background)


def get_processing_status(draft_id: int) -> dict:
    """Get processing status for a draft"""
    return feedback_pipeline.get_processing_status(draft_id)


def retry_processing(draft_id: int):
    """Retry processing for a failed draft"""
    return feedback_pipeline.retry_failed_processing(draft_id)
