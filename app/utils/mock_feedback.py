"""
Mock Feedback Generator for FeedForward
Provides simulated feedback when no LLM providers are available
"""

import json
import random
from datetime import datetime

from app.models.assignment import Assignment, RubricCategory


class MockFeedbackGenerator:
    """Generate mock feedback for testing and demonstration purposes"""

    def __init__(self):
        self.feedback_templates = {
            "strengths": [
                "Clear and well-organized structure",
                "Good understanding of the key concepts",
                "Effective use of examples to support arguments",
                "Strong introduction that sets up the topic well",
                "Logical flow of ideas throughout",
                "Good attention to detail",
                "Demonstrates critical thinking",
                "Well-researched and supported arguments",
                "Clear thesis statement",
                "Appropriate academic tone",
            ],
            "improvements": [
                "Could benefit from more specific examples",
                "Consider expanding on the main arguments",
                "The conclusion could be strengthened",
                "Some paragraphs could use better transitions",
                "Consider addressing counterarguments",
                "More citations would strengthen the arguments",
                "Some sections could be more concise",
                "Consider reorganizing for better flow",
                "The analysis could go deeper",
                "Proofread for minor grammatical issues",
            ],
            "general": [
                "This is a solid draft that shows good understanding of the material. With some refinement in the areas mentioned above, this could be an excellent submission.",
                "You've made good progress on this assignment. The foundation is strong, and with attention to the suggested improvements, you can enhance the overall quality.",
                "This submission demonstrates engagement with the topic. Consider the feedback provided to take your work to the next level.",
                "Good effort on this draft. You're on the right track, and implementing the suggested changes will help clarify and strengthen your arguments.",
                "This is a promising start. Focus on the areas for improvement to develop a more comprehensive and polished final version.",
            ],
        }

    def generate_mock_feedback(
        self,
        assignment: Assignment,
        rubric_categories: list[RubricCategory],
        student_submission: str,
        draft_version: int = 1,
    ) -> dict:
        """Generate mock feedback based on rubric categories"""

        # Calculate a base score with some randomness
        base_score = random.randint(65, 85)

        # Adjust based on draft version (later drafts get slightly higher scores)
        base_score += min(draft_version * 2, 10)

        # Generate category scores
        category_feedback = []
        total_weight = sum(cat.weight for cat in rubric_categories)

        for category in rubric_categories:
            # Generate score for this category (with some variance)
            category_score = base_score + random.randint(-10, 10)
            category_score = max(0, min(100, category_score))  # Clamp to 0-100

            # Select random strengths and improvements
            num_strengths = random.randint(1, 3)
            num_improvements = random.randint(1, 3)

            strengths = random.sample(
                self.feedback_templates["strengths"],
                min(num_strengths, len(self.feedback_templates["strengths"])),
            )
            improvements = random.sample(
                self.feedback_templates["improvements"],
                min(num_improvements, len(self.feedback_templates["improvements"])),
            )

            category_feedback.append(
                {
                    "criterion_name": category.name,
                    "strengths": strengths,
                    "improvements": improvements,
                    "examples": [
                        f"In your discussion of {category.name.lower()}, you demonstrated good understanding."
                    ],
                    "score": category_score,
                }
            )

        # Calculate weighted overall score
        if total_weight > 0:
            overall_score = sum(
                cf["score"] * cat.weight / total_weight
                for cf, cat in zip(category_feedback, rubric_categories)
            )
        else:
            overall_score = base_score

        # Select overall feedback
        overall_strengths = random.sample(
            self.feedback_templates["strengths"],
            min(2, len(self.feedback_templates["strengths"])),
        )
        overall_improvements = random.sample(
            self.feedback_templates["improvements"],
            min(2, len(self.feedback_templates["improvements"])),
        )

        # Add version-specific feedback for later drafts
        if draft_version > 1:
            overall_strengths.insert(
                0, f"Good improvements from draft {draft_version - 1}"
            )

        general_feedback_text = random.choice(self.feedback_templates["general"])

        # Add a note about this being mock feedback
        mock_notice = (
            "\n\n[Note: This is simulated feedback generated for demonstration purposes. "
            "To enable real AI feedback, please configure API keys using: python tools/setup_api_keys.py]"
        )

        return {
            "criteria_feedback": category_feedback,
            "overall_feedback": {
                "strengths": overall_strengths,
                "improvements": overall_improvements,
                "suggestions": [
                    f"For your next draft, focus on {random.choice(['strengthening your arguments', 'adding more evidence', 'improving transitions', 'clarifying your thesis'])}",
                    "Consider reviewing the rubric criteria to ensure all points are addressed",
                ],
                "score": round(overall_score, 1),
                "summary": general_feedback_text + mock_notice,
            },
        }

    def format_as_json_response(self, feedback: dict) -> str:
        """Format the feedback as a JSON string matching expected format"""
        return json.dumps(feedback, indent=2)

    def generate_mock_model_run(
        self,
        assignment: Assignment,
        rubric_categories: list[RubricCategory],
        student_submission: str,
        draft_version: int = 1,
        provider: str = "Mock",
        model_id: str = "mock-1.0",
    ) -> dict:
        """Generate a complete mock model run response"""

        feedback = self.generate_mock_feedback(
            assignment, rubric_categories, student_submission, draft_version
        )

        return {
            "provider": provider,
            "model_id": model_id,
            "timestamp": datetime.now().isoformat(),
            "status": "complete",
            "response": self.format_as_json_response(feedback),
            "feedback": feedback,
            "mock": True,  # Flag to indicate this is mock feedback
        }


# Global instance
mock_feedback_generator = MockFeedbackGenerator()
