"""
Feedback generation service for processing student submissions
"""
import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import litellm

from app.models.assignment import Assignment, assignments, rubric_categories, rubrics
from app.models.config import (
    AIModel,
    AssignmentModelRun,
    AssignmentSettings,
    aggregation_methods,
    ai_models,
    assignment_model_runs,
    assignment_settings,
)
from app.models.feedback import (
    AggregatedFeedback,
    CategoryScore,
    Draft,
    FeedbackItem,
    ModelRun,
    aggregated_feedback,
    category_scores,
    drafts,
    feedback_items,
    model_runs,
)
from app.services.prompt_templates import generate_feedback_prompt
from app.utils.privacy import cleanup_draft_content

# Configure logging
logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.drop_params = True  # Drop unsupported params instead of raising errors


@dataclass
class FeedbackGenerationResult:
    """Result of feedback generation for a single run"""
    model_run_id: int
    success: bool
    feedback_data: Optional[Dict] = None
    error_message: Optional[str] = None


class FeedbackGenerator:
    """Service for generating AI feedback on student submissions"""

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def generate_feedback_for_draft(self, draft_id: int) -> bool:
        """
        Generate feedback for a student draft submission
        
        Args:
            draft_id: ID of the draft to process
            
        Returns:
            True if feedback generation was successful, False otherwise
        """
        try:
            # Get the draft
            draft = drafts[draft_id]
            if not draft:
                logger.error(f"Draft {draft_id} not found")
                return False

            # Update draft status to processing
            draft.status = "processing"
            drafts.update(draft)

            # Get assignment and settings
            assignment = assignments[draft.assignment_id]
            settings = self._get_assignment_settings(assignment.id)

            if not settings:
                logger.error(f"No settings found for assignment {assignment.id}")
                draft.status = "error"
                drafts.update(draft)
                return False

            # Get configured AI models for this assignment
            model_configs = self._get_model_configurations(settings.id)

            if not model_configs:
                logger.error(f"No AI models configured for assignment {assignment.id}")
                draft.status = "error"
                drafts.update(draft)
                return False

            # Generate feedback using each configured model
            all_runs = []
            for model_config in model_configs:
                model = ai_models[model_config.ai_model_id]

                # Run the model multiple times as configured
                for run_num in range(model_config.num_runs):
                    result = await self._run_single_model(
                        draft, assignment, settings, model, run_num + 1
                    )
                    all_runs.append(result)

            # Check if we have successful runs
            successful_runs = [r for r in all_runs if r.success]

            if not successful_runs:
                logger.error(f"No successful model runs for draft {draft_id}")
                draft.status = "error"
                drafts.update(draft)
                return False

            # Aggregate feedback from successful runs
            await self._aggregate_feedback(draft, assignment, settings, successful_runs)

            # Update draft status
            draft.status = "feedback_ready"
            drafts.update(draft)

            # Clean up draft content for privacy
            if not draft.content_preserved:
                cleanup_draft_content(draft)

            logger.info(f"Successfully generated feedback for draft {draft_id}")
            return True

        except Exception as e:
            logger.error(f"Error generating feedback for draft {draft_id}: {e!s}")
            try:
                draft = drafts[draft_id]
                draft.status = "error"
                drafts.update(draft)
            except:
                pass
            return False

    async def _run_single_model(
        self,
        draft: Draft,
        assignment: Assignment,
        settings: AssignmentSettings,
        model: AIModel,
        run_number: int
    ) -> FeedbackGenerationResult:
        """Run a single AI model to generate feedback"""

        # Create model run record
        model_run = ModelRun(
            id=self._get_next_id(model_runs),
            draft_id=draft.id,
            model_id=model.id,
            run_number=run_number,
            timestamp=datetime.now().isoformat(),
            prompt="",  # Will be set below
            raw_response="",
            status="pending"
        )
        model_runs.insert(model_run)

        try:
            # Generate prompt
            prompt = generate_feedback_prompt(
                assignment=assignment,
                student_submission=draft.content,
                draft_version=draft.version,
                feedback_style_id=settings.feedback_style_id,
                feedback_level=settings.feedback_level
            )

            # Update prompt in model run
            model_run.prompt = prompt
            model_runs.update(model_run)

            # Prepare API configuration
            api_config = json.loads(model.api_config) if model.api_config else {}

            # Call the AI model
            response = await self._call_ai_model(
                model=model,
                prompt=prompt,
                api_config=api_config
            )

            # Parse the response
            feedback_data = self._parse_ai_response(response)

            # Store raw response
            model_run.raw_response = response
            model_run.status = "complete"
            model_runs.update(model_run)

            # Store structured feedback
            await self._store_model_feedback(model_run.id, draft.assignment_id, feedback_data)

            return FeedbackGenerationResult(
                model_run_id=model_run.id,
                success=True,
                feedback_data=feedback_data
            )

        except Exception as e:
            logger.error(f"Error in model run {model_run.id}: {e!s}")
            model_run.status = "error"
            model_run.raw_response = str(e)
            model_runs.update(model_run)

            return FeedbackGenerationResult(
                model_run_id=model_run.id,
                success=False,
                error_message=str(e)
            )

    async def _call_ai_model(
        self,
        model: AIModel,
        prompt: str,
        api_config: Dict
    ) -> str:
        """Call the AI model using LiteLLM"""

        # Prepare the model string for LiteLLM
        if model.provider.lower() == "openai":
            model_string = model.model_id
        elif model.provider.lower() == "anthropic":
            model_string = f"claude-{model.model_id}"
        elif model.provider.lower() == "ollama":
            model_string = f"ollama/{model.model_id}"
        else:
            model_string = f"{model.provider.lower()}/{model.model_id}"

        # Set up API key if provided
        api_key = api_config.get("api_key")
        if api_key:
            if model.provider.lower() == "openai":
                litellm.openai_key = api_key
            elif model.provider.lower() == "anthropic":
                litellm.anthropic_key = api_key

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are an expert educational assessment assistant. Provide feedback in valid JSON format only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        # Make the API call with retries
        for attempt in range(self.max_retries):
            try:
                response = await litellm.acompletion(
                    model=model_string,
                    messages=messages,
                    temperature=api_config.get("temperature", 0.7),
                    max_tokens=api_config.get("max_tokens", 2000),
                    response_format={"type": "json_object"} if model.provider.lower() == "openai" else None
                )

                return response.choices[0].message.content

            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise e

    def _parse_ai_response(self, response: str) -> Dict:
        """Parse the AI response into structured feedback"""
        try:
            # Try to parse as JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # If not valid JSON, try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass

            # If we can't parse it, create a simple structure
            return {
                "overall_feedback": {
                    "summary": response,
                    "score": 70,  # Default score
                    "strengths": ["Unable to parse structured feedback"],
                    "improvements": ["Response format was not as expected"],
                    "suggestions": ["Please try again"]
                }
            }

    async def _store_model_feedback(
        self,
        model_run_id: int,
        assignment_id: int,
        feedback_data: Dict
    ):
        """Store the parsed feedback data in the database"""

        # Get rubric categories for scoring
        assignment_rubric = None
        for rubric in rubrics():
            if rubric.assignment_id == assignment_id:
                assignment_rubric = rubric
                break

        rubric_cats = {}
        if assignment_rubric:
            for cat in rubric_categories():
                if cat.rubric_id == assignment_rubric.id:
                    rubric_cats[cat.name] = cat.id

        # Store criterion-level feedback if present
        if "criteria_feedback" in feedback_data:
            for criterion in feedback_data["criteria_feedback"]:
                criterion_name = criterion.get("criterion_name", "")
                category_id = rubric_cats.get(criterion_name)

                if category_id:
                    # Store score
                    score = CategoryScore(
                        id=self._get_next_id(category_scores),
                        model_run_id=model_run_id,
                        category_id=category_id,
                        score=float(criterion.get("score", 0)),
                        confidence=0.8  # Default confidence
                    )
                    category_scores.insert(score)

                    # Store feedback items
                    for strength in criterion.get("strengths", []):
                        item = FeedbackItem(
                            id=self._get_next_id(feedback_items),
                            model_run_id=model_run_id,
                            category_id=category_id,
                            type="strength",
                            content=strength,
                            is_strength=True,
                            is_aggregated=False
                        )
                        feedback_items.insert(item)

                    for improvement in criterion.get("improvements", []):
                        item = FeedbackItem(
                            id=self._get_next_id(feedback_items),
                            model_run_id=model_run_id,
                            category_id=category_id,
                            type="improvement",
                            content=improvement,
                            is_strength=False,
                            is_aggregated=False
                        )
                        feedback_items.insert(item)

        # Store overall feedback if present
        if "overall_feedback" in feedback_data:
            overall = feedback_data["overall_feedback"]

            # Create a general feedback item for overall feedback
            summary_item = FeedbackItem(
                id=self._get_next_id(feedback_items),
                model_run_id=model_run_id,
                category_id=None,  # No specific category
                type="general",
                content=overall.get("summary", ""),
                is_strength=False,
                is_aggregated=False
            )
            feedback_items.insert(summary_item)

    async def _aggregate_feedback(
        self,
        draft: Draft,
        assignment: Assignment,
        settings: AssignmentSettings,
        successful_runs: List[FeedbackGenerationResult]
    ):
        """Aggregate feedback from multiple model runs"""

        # Get rubric categories
        assignment_rubric = None
        for rubric in rubrics():
            if rubric.assignment_id == assignment.id:
                assignment_rubric = rubric
                break

        if not assignment_rubric:
            return

        # Get aggregation method
        aggregation_method = None
        for method in aggregation_methods():
            if method.id == settings.aggregation_method_id:
                aggregation_method = method
                break

        if not aggregation_method:
            logger.warning(f"Aggregation method {settings.aggregation_method_id} not found, using average")
            aggregation_method_name = "Average"
        else:
            aggregation_method_name = aggregation_method.name

        # Aggregate by category
        for category in rubric_categories():
            if category.rubric_id != assignment_rubric.id:
                continue

            # Collect scores for this category across all runs
            all_scores = []
            all_feedback_items = []
            score_confidences = []  # For weighted average

            for run in successful_runs:
                # Get scores for this category from this run
                for score in category_scores():
                    if score.model_run_id == run.model_run_id and score.category_id == category.id:
                        all_scores.append(score.score)
                        score_confidences.append(score.confidence if hasattr(score, 'confidence') else 0.8)

                # Get feedback items for this category
                for item in feedback_items():
                    if item.model_run_id == run.model_run_id and item.category_id == category.id:
                        all_feedback_items.append(item)

            # Calculate aggregated score based on method
            if all_scores:
                if aggregation_method_name == "Average":
                    # Simple average
                    aggregated_score = sum(all_scores) / len(all_scores)
                elif aggregation_method_name == "Weighted Average":
                    # Weighted average based on confidence
                    if score_confidences and sum(score_confidences) > 0:
                        weighted_sum = sum(score * conf for score, conf in zip(all_scores, score_confidences))
                        weight_total = sum(score_confidences)
                        aggregated_score = weighted_sum / weight_total
                    else:
                        # Fallback to simple average if no confidence values
                        aggregated_score = sum(all_scores) / len(all_scores)
                elif aggregation_method_name == "Maximum":
                    # Take the highest score
                    aggregated_score = max(all_scores)
                elif aggregation_method_name == "Median":
                    # Take the median score
                    sorted_scores = sorted(all_scores)
                    n = len(sorted_scores)
                    if n % 2 == 0:
                        aggregated_score = (sorted_scores[n//2 - 1] + sorted_scores[n//2]) / 2
                    else:
                        aggregated_score = sorted_scores[n//2]
                else:
                    # Default to average
                    aggregated_score = sum(all_scores) / len(all_scores)
            else:
                aggregated_score = 0

            # Combine feedback text
            strengths = [item.content for item in all_feedback_items if item.is_strength]
            improvements = [item.content for item in all_feedback_items if not item.is_strength]

            # Deduplicate and combine feedback, keeping track of frequency
            strength_counts = {}
            for s in strengths:
                strength_counts[s] = strength_counts.get(s, 0) + 1

            improvement_counts = {}
            for i in improvements:
                improvement_counts[i] = improvement_counts.get(i, 0) + 1

            # Sort by frequency (most common first)
            sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
            sorted_improvements = sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)

            # Create aggregated feedback text
            feedback_text = ""
            if sorted_strengths:
                feedback_text += "Strengths:\n" + "\n".join(f"• {s[0]}" for s in sorted_strengths)
            if sorted_improvements:
                if feedback_text:
                    feedback_text += "\n\n"
                feedback_text += "Areas for Improvement:\n" + "\n".join(f"• {i[0]}" for i in sorted_improvements)

            # Store aggregated feedback
            agg_feedback = AggregatedFeedback(
                id=self._get_next_id(aggregated_feedback),
                draft_id=draft.id,
                category_id=category.id,
                aggregated_score=aggregated_score,
                feedback_text=feedback_text,
                edited_by_instructor=False,
                instructor_email="",
                release_date=datetime.now().isoformat(),
                status="approved"  # Auto-approve for now
            )
            aggregated_feedback.insert(agg_feedback)

    def _get_assignment_settings(self, assignment_id: int) -> Optional[AssignmentSettings]:
        """Get settings for an assignment"""
        for settings in assignment_settings():
            if settings.assignment_id == assignment_id:
                return settings
        return None

    def _get_model_configurations(self, settings_id: int) -> List[AssignmentModelRun]:
        """Get model configurations for assignment settings"""
        configs = []
        for config in assignment_model_runs():
            if config.assignment_setting_id == settings_id:
                configs.append(config)
        return configs

    def _get_next_id(self, table) -> int:
        """Get the next available ID for a table"""
        try:
            all_records = list(table())
            if all_records:
                return max(r.id for r in all_records) + 1
            return 1
        except:
            return 1


# Singleton instance
feedback_generator = FeedbackGenerator()


async def process_draft_submission(draft_id: int) -> bool:
    """
    Process a draft submission for feedback generation
    
    This is the main entry point for the feedback generation pipeline.
    It should be called after a student submits a draft.
    
    Args:
        draft_id: ID of the draft to process
        
    Returns:
        True if successful, False otherwise
    """
    return await feedback_generator.generate_feedback_for_draft(draft_id)
