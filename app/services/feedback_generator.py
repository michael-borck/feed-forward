"""
Feedback generation service for processing student submissions.

Consolidated from the original services/feedback_generator.py and
utils/feedback_orchestrator.py + utils/ai_client.py pipelines.
"""

import asyncio
import json
import logging
import os
import re
import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

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
from app.models.instructor_preferences import instructor_model_prefs
from app.services.prompt_templates import generate_feedback_prompt
from app.utils.crypto import decrypt_sensitive_data
from app.utils.privacy import cleanup_draft_content

# Configure logging
logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.drop_params = True  # Drop unsupported params instead of raising errors
litellm.set_verbose = False
logging.getLogger("litellm").setLevel(logging.WARNING)

# Environment variable map for provider API keys
_ENV_VAR_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "cohere": "COHERE_API_KEY",
    "huggingface": "HUGGINGFACE_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "custom": "CUSTOM_LLM_API_KEY",
}

# API key env vars to check for mock fallback detection
_API_KEY_VARS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "GROQ_API_KEY",
    "OLLAMA_API_BASE",
]


@dataclass
class FeedbackGenerationResult:
    """Result of feedback generation for a single run"""

    model_run_id: int
    success: bool
    feedback_data: Optional[dict] = None
    error_message: Optional[str] = None


class FeedbackGenerator:
    """Service for generating AI feedback on student submissions"""

    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    async def generate_feedback_for_draft(self, draft_id: int) -> bool:
        """
        Generate feedback for a student draft submission.

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
            active_models = self._get_instructor_active_models(assignment.created_by)

            if not active_models:
                # Check for mock fallback
                if not self._check_for_api_keys():
                    logger.warning(
                        f"No AI models or API keys configured for draft {draft_id}. "
                        "Using mock feedback."
                    )
                    return await self._process_with_mock_feedback(
                        draft, assignment, settings
                    )

                logger.error(
                    f"No active AI models for instructor {assignment.created_by}"
                )
                draft.status = "error"
                drafts.update(draft)
                return False

            # Create model configurations from active models
            model_configs = []
            for model in active_models:
                num_runs = getattr(settings, "num_runs", 1)
                model_configs.append({"model": model, "num_runs": num_runs})

            # Build all run coroutines and execute concurrently
            tasks = []
            for model_config in model_configs:
                model = model_config["model"]
                for run_num in range(model_config["num_runs"]):
                    tasks.append(
                        self._run_single_model(
                            draft, assignment, settings, model, run_num + 1
                        )
                    )

            all_runs = await asyncio.gather(*tasks, return_exceptions=True)

            # Separate successes from failures
            successful_runs = []
            for result in all_runs:
                if isinstance(result, Exception):
                    logger.error(f"Model run exception: {result!s}")
                elif isinstance(result, FeedbackGenerationResult) and result.success:
                    successful_runs.append(result)

            if not successful_runs:
                logger.error(f"No successful model runs for draft {draft_id}")
                draft.status = "error"
                drafts.update(draft)
                return False

            # Blend in signal-based evidence as a synthetic run (ADR 012, S2)
            signal_run_id = await self._produce_signal_evidence(draft.id)
            if signal_run_id is not None:
                successful_runs.append(
                    FeedbackGenerationResult(model_run_id=signal_run_id, success=True)
                )

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
            except Exception:
                pass
            return False

    async def _run_single_model(
        self,
        draft: Draft,
        assignment: Assignment,
        settings: AssignmentSettings,
        model: AIModel,
        run_number: int,
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
            status="pending",
        )
        model_runs.insert(model_run)

        try:
            # Generate prompt
            prompt = generate_feedback_prompt(
                assignment=assignment,
                student_submission=draft.content,
                draft_version=draft.version,
                feedback_style_id=settings.feedback_style_id,
                feedback_level=settings.feedback_level,
            )

            # Update prompt in model run
            model_run.prompt = prompt
            model_runs.update(model_run)

            # Prepare API configuration
            api_config = self._get_model_config(model)

            # Call the AI model
            response = await self._call_ai_model(
                model=model, prompt=prompt, api_config=api_config
            )

            # Parse the response
            feedback_data = self._parse_ai_response(response)

            # Store raw response
            model_run.raw_response = response
            model_run.status = "complete"
            model_runs.update(model_run)

            # Store structured feedback
            await self._store_model_feedback(
                model_run.id, draft.assignment_id, feedback_data
            )

            return FeedbackGenerationResult(
                model_run_id=model_run.id, success=True, feedback_data=feedback_data
            )

        except Exception as e:
            logger.error(f"Error in model run {model_run.id}: {e!s}")
            model_run.status = "error"
            model_run.raw_response = str(e)
            model_runs.update(model_run)

            return FeedbackGenerationResult(
                model_run_id=model_run.id, success=False, error_message=str(e)
            )

    def _get_model_config(self, model: AIModel) -> dict[str, Any]:
        """Extract model configuration, decrypting API keys and resolving env vars."""
        try:
            config: dict[str, Any] = (
                json.loads(model.api_config) if model.api_config else {}
            )
        except (json.JSONDecodeError, TypeError):
            config = {}

        # Decrypt API key if stored encrypted
        if "api_key_encrypted" in config:
            try:
                config["api_key"] = decrypt_sensitive_data(config["api_key_encrypted"])
                del config["api_key_encrypted"]
            except Exception as e:
                logger.warning(f"Failed to decrypt API key for {model.provider}: {e!s}")

        # Fall back to environment variable if no key in config
        if "api_key" not in config:
            provider = model.provider.lower()
            env_var = _ENV_VAR_MAP.get(provider)
            if env_var:
                api_key = os.environ.get(env_var)
                if api_key:
                    config["api_key"] = api_key

        return config

    def _build_litellm_model_name(self, model: AIModel) -> str:
        """Build the LiteLLM model string from provider and model_id."""
        provider = model.provider.lower()
        if provider == "custom":
            return str(model.model_id)
        return f"{provider}/{model.model_id}"

    def _resolve_base_url(
        self, model: AIModel, api_config: dict[str, Any]
    ) -> Optional[str]:
        """Resolve the base URL for provider-specific routing."""
        if "api_base" in api_config:
            return api_config["api_base"]

        provider = model.provider.lower()
        if provider == "ollama":
            return os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
        if provider == "openrouter":
            return "https://openrouter.ai/api/v1"
        if provider == "custom":
            return os.environ.get("CUSTOM_LLM_BASE_URL")
        return None

    async def _call_ai_model(
        self, model: AIModel, prompt: str, api_config: dict
    ) -> str:
        """Call the AI model using LiteLLM with retries."""

        model_string = self._build_litellm_model_name(model)

        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert educational assessment assistant. "
                    "Provide feedback in valid JSON format only."
                ),
            },
            {"role": "user", "content": prompt},
        ]

        # Build call parameters
        call_params: dict[str, Any] = {
            "model": model_string,
            "messages": messages,
            "temperature": api_config.get("temperature", 0.7),
            "max_tokens": api_config.get("max_tokens", 2000),
        }

        # Add API key if available
        if "api_key" in api_config:
            call_params["api_key"] = api_config["api_key"]

        # Add base URL for provider-specific routing
        base_url = self._resolve_base_url(model, api_config)
        if base_url:
            call_params["api_base"] = base_url

        # Request JSON mode for providers that support it
        if model.provider.lower() == "openai":
            call_params["response_format"] = {"type": "json_object"}

        # Make the API call with retries
        for attempt in range(self.max_retries):
            try:
                response = await litellm.acompletion(**call_params)

                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("Empty response from AI model")
                return str(content)

            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                raise e

        raise RuntimeError("Failed to get AI response after all retries")

    def _parse_ai_response(self, response: str) -> dict[Any, Any]:
        """Parse the AI response into structured feedback"""
        try:
            # Strip markdown code fences if present
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            result: dict[Any, Any] = json.loads(cleaned)
            return result
        except json.JSONDecodeError:
            # Try to extract JSON from the response with regex
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                try:
                    result2: dict[Any, Any] = json.loads(json_match.group())
                    return result2
                except Exception:
                    pass

            # If we can't parse it, create a simple structure
            return {
                "overall_feedback": {
                    "summary": response,
                    "score": 70,
                    "strengths": ["Unable to parse structured feedback"],
                    "improvements": ["Response format was not as expected"],
                    "suggestions": ["Please try again"],
                }
            }

    async def _store_model_feedback(
        self, model_run_id: int, assignment_id: int, feedback_data: dict[Any, Any]
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
                        confidence=0.8,
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
                            is_aggregated=False,
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
                            is_aggregated=False,
                        )
                        feedback_items.insert(item)

        # Store overall feedback if present
        if "overall_feedback" in feedback_data:
            overall = feedback_data["overall_feedback"]

            summary_item = FeedbackItem(
                id=self._get_next_id(feedback_items),
                model_run_id=model_run_id,
                category_id=None,
                type="general",
                content=overall.get("summary", ""),
                is_strength=False,
                is_aggregated=False,
            )
            feedback_items.insert(summary_item)

    async def _produce_signal_evidence(self, draft_id: int) -> Optional[int]:
        """
        Ensure signals are extracted, then record them as a synthetic ModelRun
        whose CategoryScores blend into aggregation (ADR 012 §4, phase S2).

        Best-effort: any failure (analyser down, no rubric, etc.) is logged and
        skipped so signal evidence never blocks LLM feedback.
        """
        try:
            from app.services import signal_evidence, signal_service

            loop = asyncio.get_event_loop()
            # Idempotent — extracts if the background pass hasn't finished yet.
            await loop.run_in_executor(
                None, signal_service.extract_signals_for_draft, draft_id
            )
            return await loop.run_in_executor(
                None, signal_evidence.produce_signal_run, draft_id
            )
        except Exception as e:
            logger.warning("Signal evidence failed for draft %s: %s", draft_id, e)
            return None

    async def _aggregate_feedback(
        self,
        draft: Draft,
        assignment: Assignment,
        settings: AssignmentSettings,
        successful_runs: list[FeedbackGenerationResult],
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
            logger.warning(
                f"Aggregation method {settings.aggregation_method_id} not found, "
                "using average"
            )
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
            score_confidences = []

            for run in successful_runs:
                for score in category_scores():
                    if (
                        score.model_run_id == run.model_run_id
                        and score.category_id == category.id
                    ):
                        all_scores.append(score.score)
                        score_confidences.append(
                            score.confidence if hasattr(score, "confidence") else 0.8
                        )

                for item in feedback_items():
                    if (
                        item.model_run_id == run.model_run_id
                        and item.category_id == category.id
                    ):
                        all_feedback_items.append(item)

            # Calculate aggregated score based on method
            if all_scores:
                aggregated_score = self._compute_aggregated_score(
                    aggregation_method_name, all_scores, score_confidences
                )
            else:
                aggregated_score = 0

            # Combine feedback text
            strengths = [
                item.content for item in all_feedback_items if item.is_strength
            ]
            improvements = [
                item.content for item in all_feedback_items if not item.is_strength
            ]

            # Deduplicate and combine feedback, keeping track of frequency
            strength_counts: dict[str, int] = {}
            for s in strengths:
                strength_counts[s] = strength_counts.get(s, 0) + 1

            improvement_counts: dict[str, int] = {}
            for i in improvements:
                improvement_counts[i] = improvement_counts.get(i, 0) + 1

            # Sort by frequency (most common first)
            sorted_strengths = sorted(
                strength_counts.items(), key=lambda x: x[1], reverse=True
            )
            sorted_improvements = sorted(
                improvement_counts.items(), key=lambda x: x[1], reverse=True
            )

            # Create aggregated feedback text
            feedback_text = ""
            if sorted_strengths:
                feedback_text += "Strengths:\n" + "\n".join(
                    f"• {s[0]}" for s in sorted_strengths
                )
            if sorted_improvements:
                if feedback_text:
                    feedback_text += "\n\n"
                feedback_text += "Areas for Improvement:\n" + "\n".join(
                    f"• {i[0]}" for i in sorted_improvements
                )

            # Store aggregated feedback
            agg_feedback = AggregatedFeedback(
                id=self._get_next_id(aggregated_feedback),
                draft_id=draft.id,
                category_id=category.id,
                aggregated_score=aggregated_score,
                feedback_text=feedback_text,
                edited_by_instructor=False,
                instructor_email="",
                release_date="",
                status="pending_review",
            )
            aggregated_feedback.insert(agg_feedback)

    def _compute_aggregated_score(
        self,
        method_name: str,
        scores: list[float],
        confidences: list[float],
    ) -> float:
        """Compute an aggregated score using the specified method."""
        if method_name == "Average":
            return statistics.mean(scores)

        if method_name == "Weighted Average":
            if confidences and sum(confidences) > 0:
                weighted_sum = sum(
                    s * c for s, c in zip(scores, confidences)
                )
                return weighted_sum / sum(confidences)
            return statistics.mean(scores)

        if method_name == "Maximum":
            return max(scores)

        if method_name == "Median":
            return statistics.median(scores)

        if method_name == "Trimmed Mean":
            sorted_scores = sorted(scores)
            trim_count = max(1, len(sorted_scores) // 10)
            if len(sorted_scores) > 2 * trim_count:
                trimmed = sorted_scores[trim_count:-trim_count]
            else:
                trimmed = sorted_scores
            return statistics.mean(trimmed)

        # Default to average
        return statistics.mean(scores)

    # ------------------------------------------------------------------
    # Mock feedback fallback
    # ------------------------------------------------------------------

    def _check_for_api_keys(self) -> bool:
        """Check if any API keys are configured in environment."""
        return any(os.environ.get(var) for var in _API_KEY_VARS)

    async def _process_with_mock_feedback(
        self,
        draft: Draft,
        assignment: Assignment,
        settings: AssignmentSettings,
    ) -> bool:
        """Generate mock feedback when no real API keys are available."""
        from app.utils.mock_feedback import mock_feedback_generator

        try:
            # Get rubric categories
            assignment_rubric = None
            for rubric in rubrics():
                if rubric.assignment_id == assignment.id:
                    assignment_rubric = rubric
                    break

            categories = []
            if assignment_rubric:
                for cat in rubric_categories():
                    if cat.rubric_id == assignment_rubric.id:
                        categories.append(cat)

            mock_response = mock_feedback_generator.generate_mock_model_run(
                assignment=assignment,
                rubric_categories=categories,
                student_submission=draft.content,
                draft_version=draft.version,
                provider="Mock",
                model_id="mock-feedback-1.0",
            )

            # Create a mock model run record
            model_run = ModelRun(
                id=self._get_next_id(model_runs),
                draft_id=draft.id,
                model_id=0,
                run_number=1,
                timestamp=mock_response["timestamp"],
                prompt="Mock feedback generation",
                raw_response=mock_response["response"],
                status="complete",
            )
            model_runs.insert(model_run)

            # Store structured feedback
            feedback_data = mock_response["feedback"]
            await self._store_model_feedback(
                model_run.id, assignment.id, feedback_data
            )

            # Aggregate (mock run + optional signal evidence) (ADR 012, S2)
            mock_result = FeedbackGenerationResult(
                model_run_id=model_run.id, success=True, feedback_data=feedback_data
            )
            runs = [mock_result]
            signal_run_id = await self._produce_signal_evidence(draft.id)
            if signal_run_id is not None:
                runs.append(
                    FeedbackGenerationResult(model_run_id=signal_run_id, success=True)
                )
            await self._aggregate_feedback(draft, assignment, settings, runs)

            draft.status = "feedback_ready"
            drafts.update(draft)

            if not draft.content_preserved:
                cleanup_draft_content(draft)

            logger.info(
                f"Mock feedback generated successfully for draft {draft.id}"
            )
            return True

        except Exception as e:
            logger.error(f"Mock feedback generation failed: {e!s}")
            try:
                draft.status = "error"
                drafts.update(draft)
            except Exception:
                pass
            return False

    # ------------------------------------------------------------------
    # Status query
    # ------------------------------------------------------------------

    def get_feedback_status(self, draft_id: int) -> dict:
        """Get current feedback processing status for a draft."""
        try:
            draft = drafts[draft_id]

            all_runs = model_runs()
            draft_runs = [run for run in all_runs if run.draft_id == draft_id]

            all_agg_feedback = aggregated_feedback()
            draft_agg_feedback = [
                af for af in all_agg_feedback if af.draft_id == draft_id
            ]

            return {
                "draft_status": draft.status,
                "total_runs": len(draft_runs),
                "completed_runs": len(
                    [r for r in draft_runs if r.status == "complete"]
                ),
                "failed_runs": len([r for r in draft_runs if r.status == "error"]),
                "has_aggregated_feedback": len(draft_agg_feedback) > 0,
                "feedback_status": (
                    draft_agg_feedback[0].status
                    if draft_agg_feedback
                    else "no_feedback"
                ),
            }

        except Exception as e:
            logger.error(f"Error getting feedback status: {e!s}")
            return {
                "draft_status": "unknown",
                "total_runs": 0,
                "completed_runs": 0,
                "failed_runs": 0,
                "has_aggregated_feedback": False,
                "feedback_status": "error",
            }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_instructor_active_models(self, instructor_email: str) -> list[AIModel]:
        """Get active AI models for an instructor based on their preferences"""
        active_model_ids = set()

        for pref in instructor_model_prefs():
            if pref.instructor_email == instructor_email and pref.is_active:
                active_model_ids.add(pref.model_id)

        if not active_model_ids:
            for model in ai_models():
                if model.is_active and model.created_by == "system":
                    active_model_ids.add(model.id)

        active_models = []
        for model in ai_models():
            if model.id in active_model_ids and model.is_active:
                active_models.append(model)

        return active_models

    def _get_assignment_settings(
        self, assignment_id: int
    ) -> Optional[AssignmentSettings]:
        """Get settings for an assignment"""
        for settings in assignment_settings():
            if settings.assignment_id == assignment_id:
                return settings
        return None

    def _get_model_configurations(self, settings_id: int) -> list[AssignmentModelRun]:
        """Get model configurations for assignment settings"""
        configs = []
        for config in assignment_model_runs():
            if config.assignment_setting_id == settings_id:
                configs.append(config)
        return configs

    def _get_next_id(self, table: Any) -> int:
        """Get the next available ID for a table"""
        try:
            all_records = list(table())
            if all_records:
                max_id: int = max(r.id for r in all_records) + 1
                return max_id
            return 1
        except Exception:
            return 1


# Singleton instance
feedback_generator = FeedbackGenerator()


async def process_draft_submission(draft_id: int) -> bool:
    """
    Process a draft submission for feedback generation.

    This is the main entry point for the feedback generation pipeline.
    It should be called after a student submits a draft.

    Args:
        draft_id: ID of the draft to process

    Returns:
        True if successful, False otherwise
    """
    return await feedback_generator.generate_feedback_for_draft(draft_id)


def get_feedback_status(draft_id: int) -> dict:
    """Get current feedback processing status for a draft."""
    return feedback_generator.get_feedback_status(draft_id)
