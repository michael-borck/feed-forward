"""
Essay assessment type handler
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from app.assessment.base import AssessmentHandler


class EssayAssessmentHandler(AssessmentHandler):
    """
    Handler for traditional text-based essay assessments.
    
    This handler processes plain text essays and generates feedback
    based on content, structure, and writing quality.
    """
    
    def validate_submission(self, content: Any, metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate essay submission."""
        # Check if content is provided
        if not content or not isinstance(content, str):
            return False, "Essay content is required"
        
        # Remove whitespace and check length
        cleaned_content = content.strip()
        if not cleaned_content:
            return False, "Essay cannot be empty"
        
        # Check word count
        word_count = len(cleaned_content.split())
        config = json.loads(self.config.get("configuration", "{}"))
        min_words = config.get("min_words", 100)
        max_words = config.get("max_words", 5000)
        
        if word_count < min_words:
            return False, f"Essay must be at least {min_words} words (current: {word_count})"
        
        if word_count > max_words:
            return False, f"Essay must not exceed {max_words} words (current: {word_count})"
        
        return True, None
    
    def preprocess(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess essay for AI evaluation."""
        # Clean and normalize text
        cleaned_content = content.strip()
        
        # Calculate statistics
        word_count = len(cleaned_content.split())
        paragraph_count = len([p for p in cleaned_content.split('\n\n') if p.strip()])
        sentence_count = cleaned_content.count('.') + cleaned_content.count('!') + cleaned_content.count('?')
        
        # Extract structure information
        has_introduction = self._detect_introduction(cleaned_content)
        has_conclusion = self._detect_conclusion(cleaned_content)
        
        return {
            "processed_text": cleaned_content,
            "additional_context": {
                "word_count": word_count,
                "paragraph_count": paragraph_count,
                "sentence_count": sentence_count,
                "avg_words_per_sentence": word_count / max(sentence_count, 1),
                "structural_elements": {
                    "has_introduction": has_introduction,
                    "has_conclusion": has_conclusion
                }
            },
            "metadata": {
                **metadata,
                "word_count": word_count,
                "preprocessing_complete": True
            }
        }
    
    def get_prompt_template(self, rubric: Dict[str, Any], processed_content: Dict[str, Any]) -> str:
        """Generate essay-specific prompt."""
        context = processed_content["additional_context"]
        
        prompt = f"""You are an expert educational assessment assistant evaluating an essay submission.

## Assignment Context
Title: {rubric.get('assignment_title', 'Essay Assignment')}
Description: {rubric.get('assignment_description', 'Evaluate this essay submission')}
Word Count: {context['word_count']} words
Structure: {context['paragraph_count']} paragraphs, {context['sentence_count']} sentences

## Evaluation Criteria
Please evaluate the essay based on these criteria:

"""
        
        # Add rubric categories
        for category in rubric.get('categories', []):
            weight_percent = category['weight'] * 100
            prompt += f"### {category['name']} ({weight_percent:.0f}% of grade)\n"
            prompt += f"{category['description']}\n\n"
        
        prompt += f"""## Student Essay

{processed_content['processed_text']}

## Feedback Instructions

Please provide comprehensive feedback in JSON format:

1. For each criterion:
   - Identify 2-3 specific strengths with quotes from the essay
   - Identify 2-3 areas for improvement with specific examples
   - Provide actionable suggestions for enhancement
   - Score out of 100

2. Overall assessment:
   - Synthesize the main strengths across all criteria
   - Identify the 2-3 most important areas for improvement
   - Provide specific next steps for the student
   - Calculate an overall score based on the weighted criteria

Focus on:
- Writing clarity and coherence
- Argument development and evidence
- Essay structure and organization
- Grammar and style (but don't over-emphasize minor errors)
- Critical thinking and analysis

Maintain an encouraging tone while providing honest, constructive feedback.

Return your response in this exact JSON format:
{{
    "overall": {{
        "score": <0-100>,
        "strengths": ["strength 1", "strength 2", "strength 3"],
        "improvements": ["improvement 1", "improvement 2", "improvement 3"],
        "suggestions": ["specific suggestion 1", "specific suggestion 2"]
    }},
    "criteria": {{
        "<category_name>": {{
            "score": <0-100>,
            "strengths": ["strength 1", "strength 2"],
            "improvements": ["improvement 1", "improvement 2"],
            "suggestions": ["suggestion 1", "suggestion 2"]
        }}
    }}
}}"""
        
        return prompt
    
    def format_feedback(self, raw_feedback: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format essay feedback for display."""
        # Ensure feedback has required structure
        formatted = {
            "overall": raw_feedback.get("overall", {}),
            "criteria": raw_feedback.get("criteria", {}),
            "metadata": {
                "assessment_type": "essay",
                "word_count": metadata.get("word_count", 0),
                "processing_complete": True
            }
        }
        
        # Add essay-specific formatting hints
        if "suggestions" in formatted["overall"]:
            # Add emphasis to key terms in suggestions
            formatted["overall"]["formatted_suggestions"] = [
                self._highlight_key_terms(suggestion) 
                for suggestion in formatted["overall"]["suggestions"]
            ]
        
        return formatted
    
    def _detect_introduction(self, text: str) -> bool:
        """Detect if essay has an introduction."""
        # Simple heuristic: check first paragraph for thesis indicators
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            return False
        
        first_para = paragraphs[0].lower()
        intro_indicators = ['this essay', 'this paper', 'i will', 'we will', 
                           'argues that', 'explores', 'examines', 'discusses']
        
        return any(indicator in first_para for indicator in intro_indicators)
    
    def _detect_conclusion(self, text: str) -> bool:
        """Detect if essay has a conclusion."""
        # Simple heuristic: check last paragraph for conclusion indicators
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        if not paragraphs:
            return False
        
        last_para = paragraphs[-1].lower()
        conclusion_indicators = ['in conclusion', 'to conclude', 'in summary', 
                                'to summarize', 'therefore', 'thus', 'finally']
        
        return any(indicator in last_para for indicator in conclusion_indicators)
    
    def _highlight_key_terms(self, text: str) -> str:
        """Highlight key terms in feedback text."""
        # This is a placeholder - in real implementation, this could add
        # HTML tags or markdown formatting
        key_terms = ['thesis', 'evidence', 'structure', 'argument', 'clarity',
                     'coherence', 'transition', 'conclusion', 'introduction']
        
        highlighted = text
        for term in key_terms:
            # In a real implementation, you might add <strong> tags or **markdown**
            highlighted = highlighted.replace(term, f"**{term}**")
            highlighted = highlighted.replace(term.capitalize(), f"**{term.capitalize()}**")
        
        return highlighted
    
    def get_rubric_template(self) -> Dict[str, Any]:
        """Get essay-specific rubric template."""
        return {
            "categories": [
                {
                    "name": "Thesis and Argument",
                    "description": "Clear thesis statement and well-developed argument with supporting evidence",
                    "weight": 0.3
                },
                {
                    "name": "Organization and Structure",
                    "description": "Logical flow, clear paragraphs, effective introduction and conclusion",
                    "weight": 0.25
                },
                {
                    "name": "Evidence and Analysis",
                    "description": "Use of relevant evidence, critical analysis, and original thinking",
                    "weight": 0.25
                },
                {
                    "name": "Writing Style and Clarity",
                    "description": "Clear expression, appropriate tone, grammar, and vocabulary",
                    "weight": 0.2
                }
            ]
        }