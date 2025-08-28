"""
AI Client Service for FeedForward
Handles interaction with multiple AI providers via LiteLLM
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

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
    category_scores: dict[str, float]
    strengths: list[str]
    improvements: list[str]
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

    def _get_model_config(self, ai_model: AIModel) -> dict[str, Any]:
        """Extract and decrypt model configuration"""
        try:
            config: dict[str, Any] = json.loads(ai_model.api_config)

            # Decrypt API key if present
            if "api_key_encrypted" in config:
                config["api_key"] = decrypt_sensitive_data(config["api_key_encrypted"])
                del config["api_key_encrypted"]

            # Check for API keys in environment variables if not in config
            if "api_key" not in config:
                provider = ai_model.provider.lower()
                env_var_map = {
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

                if provider in env_var_map:
                    env_var = env_var_map[provider]
                    api_key = os.environ.get(env_var)
                    if api_key:
                        config["api_key"] = api_key
                        self.logger.info(
                            f"Using API key from environment variable {env_var}"
                        )
                    else:
                        self.logger.warning(
                            f"No API key found for {ai_model.provider}. "
                            f"Please set {env_var} in your .env file or run: python tools/setup_api_keys.py"
                        )

            return config
        except (json.JSONDecodeError, Exception) as e:
            raise AIClientError(f"Failed to parse model config: {e!s}") from e

    def _build_litellm_model_name(
        self, ai_model: AIModel, config: dict[str, Any]
    ) -> str:
        """Build LiteLLM model name from provider and model_id"""
        provider_mapping = {
            "openai": lambda model_id: f"openai/{model_id}",
            "anthropic": lambda model_id: f"anthropic/{model_id}",
            "google": lambda model_id: f"google/{model_id}",
            "gemini": lambda model_id: f"gemini/{model_id}",
            "groq": lambda model_id: f"groq/{model_id}",
            "cohere": lambda model_id: f"cohere/{model_id}",
            "huggingface": lambda model_id: f"huggingface/{model_id}",
            "ollama": lambda model_id: f"ollama/{model_id}",
            "openrouter": lambda model_id: f"openrouter/{model_id}",
            "custom": lambda model_id: model_id,  # For custom, use model_id directly
        }

        provider = ai_model.provider.lower()
        if provider not in provider_mapping:
            # Default to OpenAI-compatible format
            self.logger.warning(f"Unknown provider {provider}, treating as OpenAI-compatible")
            return ai_model.model_id

        return provider_mapping[provider](ai_model.model_id)

    def _create_rubric_prompt(
        self,
        assignment: Assignment,
        rubric_categories: list[RubricCategory],
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
            raise AIClientError(f"Failed to parse AI response: {e!s}") from e

    async def run_single_model(
        self,
        ai_model: AIModel,
        assignment: Assignment,
        rubric_categories: list[RubricCategory],
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

            # Add custom base URL for Ollama or custom providers
            if "api_base" in config:
                call_params["api_base"] = config["api_base"]
            elif ai_model.provider.lower() == "ollama":
                # Use environment variable or default to localhost
                ollama_base = os.environ.get("OLLAMA_API_BASE", "http://localhost:11434")
                call_params["api_base"] = ollama_base
            elif ai_model.provider.lower() == "openrouter":
                call_params["api_base"] = "https://openrouter.ai/api/v1"
            elif ai_model.provider.lower() == "custom":
                # Custom providers must specify api_base in config
                custom_base = config.get("api_base") or os.environ.get("CUSTOM_LLM_BASE_URL")
                if custom_base:
                    call_params["api_base"] = custom_base

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

            # Provide more helpful error messages based on the error type
            if "api_key" in error_msg.lower() or "unauthorized" in error_msg.lower():
                helpful_msg = (
                    f"API key error for {ai_model.provider}. "
                    f"Please configure your API keys by running: python tools/setup_api_keys.py"
                )
                self.logger.error(helpful_msg)
                error_msg = helpful_msg
            elif "rate limit" in error_msg.lower():
                helpful_msg = f"Rate limit exceeded for {ai_model.provider}. Please wait and try again."
                self.logger.error(helpful_msg)
                error_msg = helpful_msg
            elif "connection" in error_msg.lower() or "refused" in error_msg.lower():
                if ai_model.provider.lower() == "ollama":
                    helpful_msg = (
                        "Cannot connect to Ollama. Please ensure Ollama is running locally. "
                        "Install from https://ollama.ai and run: ollama serve"
                    )
                else:
                    helpful_msg = f"Connection error for {ai_model.provider}. Please check your internet connection."
                self.logger.error(helpful_msg)
                error_msg = helpful_msg
            else:
                self.logger.error(
                    f"AI model run failed for {ai_model.provider}: {error_msg}"
                )

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
        rubric_categories: list[RubricCategory],
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
