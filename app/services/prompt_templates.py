"""
Prompt template system for generating AI prompts based on rubrics
"""

import json
from dataclasses import dataclass
from typing import Optional

from app.models.assignment import Assignment, RubricCategory, rubric_categories, rubrics
from app.models.config import FeedbackStyle, feedback_styles


@dataclass
class PromptContext:
    """Context data for generating prompts"""

    assignment: Assignment
    rubric_categories: list[RubricCategory]
    student_submission: str
    draft_version: int
    max_drafts: int
    feedback_style: Optional[FeedbackStyle] = None
    feedback_level: str = "both"  # 'overall', 'criterion', 'both'
    word_count: Optional[int] = None
    feedback_tone: Optional[str] = None  # From assignment config
    feedback_detail: Optional[str] = None  # From assignment config
    focus_areas: Optional[list] = None  # From assignment config
    custom_prompt: Optional[str] = None  # From assignment config


class PromptTemplate:
    """Base class for prompt templates"""

    def __init__(self, context: Optional[PromptContext] = None):
        self.context = context
        self.system_prompt = self._get_system_prompt(context)

    def _get_system_prompt(self, context: Optional[PromptContext] = None) -> str:
        """Get the system prompt for the AI model"""
        base_prompt = """You are an expert educational assessment assistant helping to provide constructive feedback on student assignments.
Your role is to:
1. Evaluate student work against specific rubric criteria
2. Provide actionable, specific feedback for improvement
3. Focus on helping students learn and grow
4. Adapt your tone and style based on instructor preferences

"""

        # Add tone-specific instructions
        if context and context.feedback_tone:
            tone_guides = {
                "encouraging": "Maintain a warm, supportive, and encouraging tone. Emphasize strengths and frame improvements positively.",
                "neutral": "Maintain a balanced, objective tone. Present feedback matter-of-factly without excessive praise or criticism.",
                "direct": "Be clear and direct with feedback. Focus on what needs improvement with straightforward language.",
                "critical": "Provide rigorous, demanding feedback. Hold work to high standards and be explicit about shortcomings."
            }
            base_prompt += f"Tone Guideline: {tone_guides.get(context.feedback_tone, tone_guides['encouraging'])}\n\n"

        # Add detail level instructions
        if context and context.feedback_detail:
            detail_guides = {
                "brief": "Provide concise feedback with key points only. Keep explanations short and to the point.",
                "standard": "Provide balanced feedback with moderate detail. Include examples and explanations where helpful.",
                "comprehensive": "Provide thorough, detailed feedback. Include extensive examples, explanations, and specific suggestions."
            }
            base_prompt += f"Detail Level: {detail_guides.get(context.feedback_detail, detail_guides['standard'])}\n\n"

        base_prompt += """Important guidelines:
- Be specific with examples from the student's work
- Balance positive feedback with areas for improvement
- Suggest concrete next steps
- Use clear, accessible language"""

        return base_prompt

    def generate_prompt(self, context: PromptContext) -> str:
        """Generate a complete prompt based on the context"""
        prompt_parts = []

        # Add assignment context
        prompt_parts.append(self._format_assignment_context(context))

        # Add rubric criteria
        prompt_parts.append(self._format_rubric_criteria(context))

        # Add student submission
        prompt_parts.append(self._format_student_submission(context))

        # Add feedback instructions
        prompt_parts.append(self._format_feedback_instructions(context))

        return "\n\n".join(prompt_parts)

    def _format_assignment_context(self, context: PromptContext) -> str:
        """Format the assignment context section"""
        return f"""## Assignment Context

Title: {context.assignment.title}
Description: {context.assignment.description}
Draft: {context.draft_version} of {context.max_drafts}
Word Count: {context.word_count or "Not specified"}"""

    def _format_rubric_criteria(self, context: PromptContext) -> str:
        """Format the rubric criteria section"""
        criteria_text = "## Evaluation Criteria\n\n"
        criteria_text += (
            "Please evaluate the submission based on these weighted criteria:\n\n"
        )

        total_weight = sum(cat.weight for cat in context.rubric_categories)

        for category in sorted(
            context.rubric_categories, key=lambda c: c.weight, reverse=True
        ):
            weight_percent = (
                (category.weight / total_weight) * 100 if total_weight > 0 else 0
            )
            criteria_text += f"### {category.name} ({weight_percent:.0f}% of grade)\n"
            criteria_text += f"{category.description}\n\n"

        return criteria_text

    def _format_student_submission(self, context: PromptContext) -> str:
        """Format the student submission section"""
        return f"""## Student Submission

{context.student_submission}"""

    def _format_feedback_instructions(self, context: PromptContext) -> str:
        """Format the feedback instructions based on settings"""
        instructions = "## Feedback Instructions\n\n"

        # Add style-specific instructions
        if context.feedback_style:
            instructions += f"Feedback Style: {context.feedback_style.name} - {context.feedback_style.description}\n\n"

        # Add focus areas if specified
        if context.focus_areas:
            focus_area_names = {
                "grammar": "Grammar and Mechanics",
                "content": "Content and Ideas",
                "structure": "Organization and Structure",
                "evidence": "Evidence and Support",
                "citations": "Citations and References",
                "critical_thinking": "Critical Thinking",
                "creativity": "Creativity and Originality"
            }

            instructions += "### Priority Focus Areas\n"
            instructions += "Pay special attention to the following aspects:\n"
            for area in context.focus_areas:
                area_name = focus_area_names.get(area, area)
                instructions += f"- {area_name}\n"
            instructions += "\n"

        # Add custom prompt if provided
        if context.custom_prompt:
            instructions += "### Additional Instructions from Instructor\n"
            instructions += f"{context.custom_prompt}\n\n"

        # Add level-specific instructions
        if context.feedback_level == "overall":
            instructions += self._get_overall_feedback_instructions()
        elif context.feedback_level == "criterion":
            instructions += self._get_criterion_feedback_instructions(context)
        else:  # both
            instructions += self._get_combined_feedback_instructions(context)

        # Add JSON format requirements
        instructions += "\n\n" + self._get_json_format_instructions(context)

        return instructions

    def _get_overall_feedback_instructions(self) -> str:
        """Get instructions for overall feedback only"""
        return """Please provide an overall assessment of the submission including:
1. General impression and main strengths
2. Key areas for improvement
3. Specific suggestions for the next draft
4. An overall score out of 100"""

    def _get_criterion_feedback_instructions(self, context: PromptContext) -> str:
        """Get instructions for criterion-specific feedback"""
        return """Please evaluate each criterion separately:
1. For each criterion, identify specific strengths and weaknesses
2. Provide concrete examples from the submission
3. Suggest improvements for each criterion
4. Score each criterion out of 100"""

    def _get_combined_feedback_instructions(self, context: PromptContext) -> str:
        """Get instructions for both overall and criterion feedback"""
        return """Please provide comprehensive feedback:

1. First, evaluate each criterion individually:
   - Identify specific strengths and weaknesses
   - Provide concrete examples from the submission
   - Score each criterion out of 100

2. Then, provide an overall assessment:
   - General impression and synthesis
   - How the criteria work together
   - Priority areas for improvement
   - Overall score out of 100"""

    def _get_json_format_instructions(self, context: PromptContext) -> str:
        """Get JSON format instructions for structured output"""
        example: dict[str, object]
        if context.feedback_level == "overall":
            example = {
                "overall_feedback": {
                    "strengths": ["List of main strengths"],
                    "improvements": ["List of areas for improvement"],
                    "suggestions": ["Specific suggestions for next draft"],
                    "score": 85,
                    "summary": "Brief overall summary",
                }
            }
        elif context.feedback_level == "criterion":
            example = {
                "criteria_feedback": [
                    {
                        "criterion_name": "Criterion Name",
                        "strengths": ["Specific strengths for this criterion"],
                        "improvements": ["Areas to improve for this criterion"],
                        "examples": ["Specific examples from the text"],
                        "score": 80,
                    }
                ]
            }
        else:  # both
            example = {
                "criteria_feedback": [
                    {
                        "criterion_name": "Criterion Name",
                        "strengths": ["Specific strengths"],
                        "improvements": ["Areas to improve"],
                        "examples": ["Examples from text"],
                        "score": 80,
                    }
                ],
                "overall_feedback": {
                    "strengths": ["Main strengths across all criteria"],
                    "improvements": ["Priority improvements"],
                    "suggestions": ["Next steps"],
                    "score": 85,
                    "summary": "Overall assessment",
                },
            }

        return f"""Please format your response as JSON following this structure:

```json
{json.dumps(example, indent=2)}
```

Ensure all scores are between 0 and 100, and all text fields contain specific, actionable feedback."""


class IterativePromptTemplate(PromptTemplate):
    """Specialized template for iterative feedback on multiple drafts"""

    def _format_assignment_context(self, context: PromptContext) -> str:
        """Add draft-specific context for iterative feedback"""
        base_context = super()._format_assignment_context(context)

        if context.draft_version > 1:
            base_context += f"\n\nNote: This is draft {context.draft_version} of {context.max_drafts}. "
            base_context += "Please acknowledge improvements from previous drafts while still providing constructive feedback for continued improvement."

        return base_context

    def _get_combined_feedback_instructions(self, context: PromptContext) -> str:
        """Add iterative-specific instructions"""
        base_instructions = super()._get_combined_feedback_instructions(context)

        if context.draft_version > 1:
            base_instructions += "\n\n3. For revision drafts, also comment on:"
            base_instructions += "\n   - Progress made since the previous draft"
            base_instructions += "\n   - Whether previous feedback was addressed"
            base_instructions += "\n   - Remaining areas for improvement"

        return base_instructions


def create_prompt_template(template_type: str = "standard", context: Optional[PromptContext] = None) -> PromptTemplate:
    """Factory function to create appropriate prompt template"""
    if template_type == "iterative":
        return IterativePromptTemplate(context)
    return PromptTemplate(context)


def generate_feedback_prompt(
    assignment: Assignment,
    student_submission: str,
    draft_version: int,
    feedback_style_id: Optional[int] = None,
    feedback_level: str = "both",
) -> str:
    """
    Generate a complete feedback prompt for an assignment submission

    Args:
        assignment: The assignment object
        student_submission: The student's submitted text
        draft_version: Which draft number this is
        feedback_style_id: Optional feedback style to use
        feedback_level: Type of feedback ('overall', 'criterion', 'both')

    Returns:
        Complete prompt string ready for AI model
    """
    # Get rubric categories for the assignment
    assignment_rubric = None
    for rubric in rubrics():
        if rubric.assignment_id == assignment.id:
            assignment_rubric = rubric
            break

    if not assignment_rubric:
        raise ValueError(f"No rubric found for assignment {assignment.id}")

    # Get rubric categories
    categories = []
    for category in rubric_categories():
        if category.rubric_id == assignment_rubric.id:
            categories.append(category)

    if not categories:
        raise ValueError(
            f"No rubric categories found for rubric {assignment_rubric.id}"
        )

    # Get feedback style if specified
    style = None
    if feedback_style_id:
        for fs in feedback_styles():
            if fs.id == feedback_style_id:
                style = fs
                break

    # Calculate word count
    word_count = len(student_submission.split()) if student_submission else 0

    # Parse assignment feedback configuration
    focus_areas = None
    if hasattr(assignment, 'feedback_focus') and assignment.feedback_focus:
        try:
            focus_areas = json.loads(assignment.feedback_focus)
        except (json.JSONDecodeError, TypeError, ValueError):
            focus_areas = None

    # Create context with all configuration
    context = PromptContext(
        assignment=assignment,
        rubric_categories=categories,
        student_submission=student_submission,
        draft_version=draft_version,
        max_drafts=assignment.max_drafts,
        feedback_style=style,
        feedback_level=feedback_level,
        word_count=word_count,
        feedback_tone=getattr(assignment, 'feedback_tone', 'encouraging'),
        feedback_detail=getattr(assignment, 'feedback_detail', 'standard'),
        focus_areas=focus_areas,
        custom_prompt=getattr(assignment, 'custom_prompt', None),
    )

    # Create appropriate template with context
    template = create_prompt_template(
        "iterative" if assignment.max_drafts > 1 else "standard",
        context
    )

    # Generate and return prompt
    return template.generate_prompt(context)
