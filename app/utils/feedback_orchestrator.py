"""
Feedback Orchestration Service for FeedForward
Handles multi-model runs, aggregation, and feedback processing pipeline
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.models.assignment import (
    Assignment,
    RubricCategory,
    assignments,
    rubric_categories,
)
from app.models.config import system_config
from app.models.feedback import (
    AIModel,
    aggregated_feedback,
    ai_models,
    category_scores,
    drafts,
    feedback_items,
    model_runs,
)
from app.utils.ai_client import ModelResult, ai_client


@dataclass
class AggregatedScore:
    """Aggregated score for a rubric category"""

    category_id: int
    category_name: str
    final_score: float
    individual_scores: List[float]
    confidence: float
    method_used: str


@dataclass
class ProcessingResult:
    """Result of feedback processing pipeline"""

    draft_id: int
    success: bool
    aggregated_scores: List[AggregatedScore]
    total_models_run: int
    successful_runs: int
    error_message: Optional[str] = None


class FeedbackOrchestrator:
    """Orchestrates the complete feedback generation and aggregation process"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_assignment_models(self, assignment: Assignment) -> List[AIModel]:
        """Get AI models configured for an assignment"""
        try:
            # Get models from assignment configuration
            assignment_config = assignment.ai_config or {}

            # Get system default models if no assignment-specific models
            if not assignment_config.get("model_ids"):
                system_configs = system_config()
                default_model_ids = []

                for config in system_configs:
                    if config.key == "default_ai_models":
                        default_model_ids = config.value.split(",")
                        break

                model_ids = [
                    int(mid.strip())
                    for mid in default_model_ids
                    if mid.strip().isdigit()
                ]
            else:
                model_ids = assignment_config["model_ids"]

            if not model_ids:
                # Fallback: get all active system models
                all_models = ai_models()
                return [
                    model
                    for model in all_models
                    if model.active and model.owner_type == "system"
                ]

            # Get specific models by ID
            all_models = ai_models()
            selected_models = [
                model for model in all_models if model.id in model_ids and model.active
            ]

            return selected_models

        except Exception as e:
            self.logger.error(f"Error getting assignment models: {e!s}")
            return []

    def get_rubric_categories(self, assignment_id: int) -> List[RubricCategory]:
        """Get rubric categories for an assignment"""
        try:
            categories = rubric_categories()
            return [cat for cat in categories if cat.assignment_id == assignment_id]
        except Exception as e:
            self.logger.error(f"Error getting rubric categories: {e!s}")
            return []

    async def process_draft_feedback(self, draft_id: int) -> ProcessingResult:
        """Main pipeline: process a draft through all configured AI models"""
        try:
            # Get draft and related data
            draft = drafts[draft_id]
            assignment = assignments[draft.assignment_id]
            models = self.get_assignment_models(assignment)
            categories = self.get_rubric_categories(assignment.id)

            if not models:
                return ProcessingResult(
                    draft_id=draft_id,
                    success=False,
                    aggregated_scores=[],
                    total_models_run=0,
                    successful_runs=0,
                    error_message="No AI models configured for this assignment",
                )

            if not draft.content:
                return ProcessingResult(
                    draft_id=draft_id,
                    success=False,
                    aggregated_scores=[],
                    total_models_run=0,
                    successful_runs=0,
                    error_message="No content found in draft submission",
                )

            # Update draft status
            drafts.update(draft_id, {"status": "processing"})

            self.logger.info(f"Processing draft {draft_id} with {len(models)} models")

            # Run all models concurrently
            tasks = []
            for i, model in enumerate(models):
                task = ai_client.run_single_model(
                    ai_model=model,
                    assignment=assignment,
                    rubric_categories=categories,
                    student_submission=draft.content,
                    draft_id=draft_id,
                    run_number=i + 1,
                )
                tasks.append(task)

            # Execute all model runs
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_results = []
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Model run exception: {result!s}")
                elif isinstance(result, ModelResult) and result.success:
                    successful_results.append(result)

            total_runs = len(models)
            successful_runs = len(successful_results)

            if successful_runs == 0:
                drafts.update(draft_id, {"status": "error"})
                return ProcessingResult(
                    draft_id=draft_id,
                    success=False,
                    aggregated_scores=[],
                    total_models_run=total_runs,
                    successful_runs=0,
                    error_message="All AI model runs failed",
                )

            # Aggregate feedback from successful runs
            aggregated_scores = self.aggregate_feedback(
                successful_results, categories, assignment
            )

            # Store aggregated feedback
            self.store_aggregated_feedback(draft_id, aggregated_scores, categories)

            # Update draft status
            drafts.update(draft_id, {"status": "feedback_ready"})

            self.logger.info(
                f"Successfully processed draft {draft_id}: {successful_runs}/{total_runs} models succeeded"
            )

            return ProcessingResult(
                draft_id=draft_id,
                success=True,
                aggregated_scores=aggregated_scores,
                total_models_run=total_runs,
                successful_runs=successful_runs,
            )

        except Exception as e:
            error_msg = f"Pipeline error: {e!s}"
            self.logger.error(error_msg)

            try:
                drafts.update(draft_id, {"status": "error"})
            except:
                pass

            return ProcessingResult(
                draft_id=draft_id,
                success=False,
                aggregated_scores=[],
                total_models_run=0,
                successful_runs=0,
                error_message=error_msg,
            )

    def aggregate_feedback(
        self,
        results: List[ModelResult],
        categories: List[RubricCategory],
        assignment: Assignment,
    ) -> List[AggregatedScore]:
        """Aggregate scores from multiple AI models"""

        # Get aggregation method from assignment config
        assignment_config = assignment.ai_config or {}
        aggregation_method = assignment_config.get(
            "aggregation_method", "weighted_mean"
        )

        aggregated_scores = []

        # Create category mapping
        category_map = {cat.id: cat for cat in categories}

        # Get all category scores from model runs
        all_run_ids = [result.model_run_id for result in results]
        all_scores = category_scores()

        # Group scores by category
        category_score_groups = {}
        for score in all_scores:
            if score.model_run_id in all_run_ids:
                if score.category_id not in category_score_groups:
                    category_score_groups[score.category_id] = []
                category_score_groups[score.category_id].append(score)

        # Aggregate each category
        for category_id, scores in category_score_groups.items():
            if category_id not in category_map:
                continue

            category = category_map[category_id]
            score_values = [s.score for s in scores]
            confidences = [s.confidence for s in scores]

            # Calculate aggregated score based on method
            if aggregation_method == "mean":
                final_score = statistics.mean(score_values)
            elif aggregation_method == "weighted_mean":
                # Weight by confidence
                total_weight = sum(confidences)
                if total_weight > 0:
                    final_score = (
                        sum(s * c for s, c in zip(score_values, confidences))
                        / total_weight
                    )
                else:
                    final_score = statistics.mean(score_values)
            elif aggregation_method == "median":
                final_score = statistics.median(score_values)
            elif aggregation_method == "trimmed_mean":
                # Remove outliers (10% from each end) then take mean
                sorted_scores = sorted(score_values)
                trim_count = max(1, len(sorted_scores) // 10)
                if len(sorted_scores) > 2 * trim_count:
                    trimmed_scores = sorted_scores[trim_count:-trim_count]
                else:
                    trimmed_scores = sorted_scores
                final_score = statistics.mean(trimmed_scores)
            else:
                final_score = statistics.mean(score_values)

            # Calculate overall confidence
            avg_confidence = statistics.mean(confidences)

            aggregated_scores.append(
                AggregatedScore(
                    category_id=category_id,
                    category_name=category.name,
                    final_score=round(final_score, 2),
                    individual_scores=score_values,
                    confidence=round(avg_confidence, 3),
                    method_used=aggregation_method,
                )
            )

        return aggregated_scores

    def store_aggregated_feedback(
        self,
        draft_id: int,
        aggregated_scores: List[AggregatedScore],
        categories: List[RubricCategory],
    ):
        """Store aggregated feedback in database"""

        # Get all feedback items from the model runs for this draft
        all_runs = model_runs()
        draft_run_ids = [
            run.id
            for run in all_runs
            if run.draft_id == draft_id and run.status == "complete"
        ]

        all_feedback_items = feedback_items()

        # Aggregate feedback text by type
        strengths = []
        improvements = []
        general_feedback = []

        for item in all_feedback_items:
            if item.model_run_id in draft_run_ids:
                if item.type == "strength":
                    strengths.append(item.content)
                elif item.type == "improvement":
                    improvements.append(item.content)
                elif item.type == "general":
                    general_feedback.append(item.content)

        # Store aggregated feedback for each category
        for agg_score in aggregated_scores:
            # Combine relevant feedback
            category_feedback = []

            # Add category-specific feedback (if any)
            category_strengths = [s for s in strengths if len(s) > 0][
                :3
            ]  # Limit to top 3
            category_improvements = [i for i in improvements if len(i) > 0][
                :3
            ]  # Limit to top 3

            feedback_text = ""
            if category_strengths:
                feedback_text += (
                    "**Strengths:**\n"
                    + "\n".join(f"• {s}" for s in category_strengths)
                    + "\n\n"
                )
            if category_improvements:
                feedback_text += "**Areas for Improvement:**\n" + "\n".join(
                    f"• {i}" for i in category_improvements
                )

            aggregated_feedback.insert(
                {
                    "draft_id": draft_id,
                    "category_id": agg_score.category_id,
                    "aggregated_score": agg_score.final_score,
                    "feedback_text": feedback_text.strip(),
                    "edited_by_instructor": False,
                    "instructor_email": "",
                    "release_date": "",
                    "status": "pending_review",
                }
            )

    def get_draft_feedback_status(self, draft_id: int) -> Dict:
        """Get current feedback processing status for a draft"""
        try:
            draft = drafts[draft_id]

            # Get model runs for this draft
            all_runs = model_runs()
            draft_runs = [run for run in all_runs if run.draft_id == draft_id]

            # Get aggregated feedback
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
                "feedback_status": draft_agg_feedback[0].status
                if draft_agg_feedback
                else "no_feedback",
            }

        except Exception as e:
            self.logger.error(f"Error getting feedback status: {e!s}")
            return {
                "draft_status": "unknown",
                "total_runs": 0,
                "completed_runs": 0,
                "failed_runs": 0,
                "has_aggregated_feedback": False,
                "feedback_status": "error",
            }


# Global orchestrator instance
feedback_orchestrator = FeedbackOrchestrator()
