"""
AI Client Service for FeedForward
Handles interaction with multiple AI providers via LiteLLM
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import litellm
from litellm import completion

from app.models.assignment import Assignment, RubricCategory
from app.models.feedback import AIModel
from app.utils.crypto import decrypt_sensitive_data

# Configure LiteLLM logging
litellm.set_verbose = False
logging.getLogger("litellm").setLevel(logging.WARNING)


@dataclass
class FeedbackResponse:
    """Structured response from AI model evaluation"""

    overall_score: float
    category_scores: Dict[str, float]
    strengths: List[str]
    improvements: List[str]
    general_feedback: str
    confidence: float = 0.8


@dataclass
class ModelResult:
    """Result from a single model run"""

    model_run_id: int
    success: bool
    feedback: Optional[FeedbackResponse] = None
    error: Optional[str] = None


class AIClientError(Exception):
    """Custom exception for AI client errors"""

    pass


class AIClient:
    """Main AI client for generating feedback using multiple providers"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _get_model_config(self, ai_model: AIModel) -> Dict[str, Any]:
        """Extract and decrypt model configuration"""
        try:
            config = json.loads(ai_model.api_config)

            # Decrypt API key if present
            if "api_key_encrypted" in config:
                config["api_key"] = decrypt_sensitive_data(config["api_key_encrypted"])
                del config["api_key_encrypted"]

            return config
        except (json.JSONDecodeError, Exception) as e:
            raise AIClientError(f"Failed to parse model config: {e!s}")

    def _build_litellm_model_name(
        self, ai_model: AIModel, config: Dict[str, Any]
    ) -> str:
        """Build LiteLLM model name from provider and model_id"""
        provider_mapping = {
            "openai": lambda model_id: f"openai/{model_id}",
            "anthropic": lambda model_id: f"anthropic/{model_id}",
            "google": lambda model_id: f"google/{model_id}",
            "cohere": lambda model_id: f"cohere/{model_id}",
            "huggingface": lambda model_id: f"huggingface/{model_id}",
        }

        provider = ai_model.provider.lower()
        if provider not in provider_mapping:
            raise AIClientError(f"Unsupported provider: {provider}")

        return provider_mapping[provider](ai_model.model_id)

    def _create_rubric_prompt(
        self,
        assignment: Assignment,
        rubric_categories: List[RubricCategory],
        student_submission: str,
    ) -> str:
        """Create a structured prompt for AI evaluation based on rubric"""

        # Build rubric description
        rubric_details = []
        for category in rubric_categories:
            rubric_details.append(f"""
**{category.name}** (Weight: {category.weight}%)
Description: {category.description}
Criteria: {category.criteria}""")

        rubric_text = "\n".join(rubric_details)

        prompt = f"""You are an expert academic evaluator providing constructive feedback on student work. 

**Assignment:** {assignment.title}
**Description:** {assignment.description}

**Rubric Categories:**
{rubric_text}

**Student Submission:**
{student_submission}

**Instructions:**
1. Evaluate the submission against each rubric category
2. Provide scores from 0-100 for each category
3. Identify specific strengths (what the student did well)
4. Identify specific areas for improvement (be constructive, not just critical)
5. Provide overall feedback that encourages improvement

**Required Response Format (JSON):**
{{
    "overall_score": <float 0-100>,
    "category_scores": {{
        "{rubric_categories[0].name if rubric_categories else "Overall"}": <float 0-100>,
        ...
    }},
    "strengths": [
        "<specific strength 1>",
        "<specific strength 2>",
        ...
    ],
    "improvements": [
        "<specific improvement suggestion 1>",
        "<specific improvement suggestion 2>",
        ...
    ],
    "general_feedback": "<overall constructive feedback paragraph>",
    "confidence": <float 0-1 indicating confidence in evaluation>
}}

Respond ONLY with valid JSON. Be specific, constructive, and encouraging in your feedback."""

        return prompt

    def _parse_ai_response(self, response_text: str) -> FeedbackResponse:
        """Parse and validate AI response into structured feedback"""
        try:
            # Clean response text (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            data = json.loads(cleaned_text)

            # Validate required fields
            required_fields = [
                "overall_score",
                "category_scores",
                "strengths",
                "improvements",
                "general_feedback",
            ]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            # Validate score ranges
            if not 0 <= data["overall_score"] <= 100:
                raise ValueError("Overall score must be between 0-100")

            for category, score in data["category_scores"].items():
                if not 0 <= score <= 100:
                    raise ValueError(
                        f"Category score for {category} must be between 0-100"
                    )

            return FeedbackResponse(
                overall_score=float(data["overall_score"]),
                category_scores=data["category_scores"],
                strengths=data["strengths"][:10],  # Limit to 10 items
                improvements=data["improvements"][:10],  # Limit to 10 items
                general_feedback=data["general_feedback"][:2000],  # Limit length
                confidence=float(data.get("confidence", 0.8)),
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            raise AIClientError(f"Failed to parse AI response: {e!s}")

    async def run_single_model(
        self,
        ai_model: AIModel,
        assignment: Assignment,
        rubric_categories: List[RubricCategory],
        student_submission: str,
        draft_id: int,
        run_number: int,
    ) -> ModelResult:
        """Run a single AI model and return structured result"""

        # Create model run record
        from app.models.feedback import model_runs

        prompt = self._create_rubric_prompt(
            assignment, rubric_categories, student_submission
        )

        model_run_data = {
            "draft_id": draft_id,
            "model_id": ai_model.id,
            "run_number": run_number,
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "raw_response": "",
            "status": "pending",
        }

        model_run_id = model_runs.insert(model_run_data)

        try:
            # Get model configuration
            config = self._get_model_config(ai_model)
            litellm_model = self._build_litellm_model_name(ai_model, config)

            # Prepare LiteLLM call parameters
            call_params = {
                "model": litellm_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": config.get("temperature", 0.7),
                "max_tokens": config.get("max_tokens", 2000),
            }

            # Add API key if available
            if "api_key" in config:
                call_params["api_key"] = config["api_key"]

            # Make API call
            self.logger.info(f"Making AI call to {litellm_model} for draft {draft_id}")
            response = completion(**call_params)

            raw_response = response.choices[0].message.content

            # Update model run with response
            model_runs.update(
                model_run_id, {"raw_response": raw_response, "status": "complete"}
            )

            # Parse response into structured feedback
            feedback = self._parse_ai_response(raw_response)

            # Store category scores and feedback items
            self._store_feedback_data(model_run_id, feedback, rubric_categories)

            return ModelResult(
                model_run_id=model_run_id, success=True, feedback=feedback
            )

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"AI model run failed: {error_msg}")

            # Update model run with error
            model_runs.update(
                model_run_id, {"status": "error", "raw_response": f"Error: {error_msg}"}
            )

            return ModelResult(
                model_run_id=model_run_id, success=False, error=error_msg
            )

    def _store_feedback_data(
        self,
        model_run_id: int,
        feedback: FeedbackResponse,
        rubric_categories: List[RubricCategory],
    ):
        """Store parsed feedback data in database"""
        from app.models.feedback import category_scores, feedback_items

        # Create category mapping
        category_map = {cat.name: cat.id for cat in rubric_categories}

        # Store category scores
        for category_name, score in feedback.category_scores.items():
            if category_name in category_map:
                category_scores.insert(
                    {
                        "model_run_id": model_run_id,
                        "category_id": category_map[category_name],
                        "score": score,
                        "confidence": feedback.confidence,
                    }
                )

        # Store feedback items
        # Strengths
        for strength in feedback.strengths:
            feedback_items.insert(
                {
                    "model_run_id": model_run_id,
                    "category_id": None,  # General strength
                    "type": "strength",
                    "content": strength,
                    "is_strength": True,
                    "is_aggregated": False,
                }
            )

        # Improvements
        for improvement in feedback.improvements:
            feedback_items.insert(
                {
                    "model_run_id": model_run_id,
                    "category_id": None,  # General improvement
                    "type": "improvement",
                    "content": improvement,
                    "is_strength": False,
                    "is_aggregated": False,
                }
            )

        # General feedback
        if feedback.general_feedback:
            feedback_items.insert(
                {
                    "model_run_id": model_run_id,
                    "category_id": None,
                    "type": "general",
                    "content": feedback.general_feedback,
                    "is_strength": False,
                    "is_aggregated": False,
                }
            )


# Global client instance
ai_client = AIClient()
