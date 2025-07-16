"""
Mathematics assessment type handler
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple

from app.assessment.base import AssessmentHandler


class MathAssessmentHandler(AssessmentHandler):
    """
    Handler for mathematical assessments.
    
    This handler processes mathematical proofs, calculations, and LaTeX content.
    """
    
    def validate_submission(self, content: Any, metadata: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate math submission."""
        if not content:
            return False, "Mathematical content is required"
        
        if not isinstance(content, str) or not content.strip():
            return False, "Submission cannot be empty"
        
        # Check for basic mathematical content
        math_indicators = [r'\$', r'\\', '=', '+', '-', '*', '/', '^', 
                          'proof', 'theorem', 'equation', 'solve']
        
        has_math = any(indicator in content.lower() for indicator in math_indicators)
        if not has_math:
            return False, "Submission does not appear to contain mathematical content"
        
        return True, None
    
    def preprocess(self, content: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess mathematical content for AI evaluation."""
        # Extract LaTeX expressions
        latex_expressions = self._extract_latex(content)
        
        # Convert LaTeX to readable format for LLM
        readable_content = self._make_latex_readable(content)
        
        # Extract mathematical structure
        structure = self._analyze_math_structure(content)
        
        return {
            "processed_text": readable_content,
            "additional_context": {
                "has_latex": bool(latex_expressions),
                "latex_count": len(latex_expressions),
                "math_type": structure["type"],
                "has_proof": structure["has_proof"],
                "has_equations": structure["has_equations"],
                "has_calculations": structure["has_calculations"]
            },
            "metadata": {
                **metadata,
                "original_latex": latex_expressions,
                "preprocessing_complete": True
            }
        }
    
    def get_prompt_template(self, rubric: Dict[str, Any], processed_content: Dict[str, Any]) -> str:
        """Generate math-specific prompt."""
        context = processed_content["additional_context"]
        
        prompt = f"""You are an expert mathematics instructor evaluating a mathematical submission.

## Assignment Context
Title: {rubric.get('assignment_title', 'Mathematics Assignment')}
Description: {rubric.get('assignment_description', 'Evaluate this mathematical submission')}
Content Type: {context['math_type']}
Contains LaTeX: {context['has_latex']}

## Mathematical Submission

{processed_content['processed_text']}

## Evaluation Criteria
Please evaluate the mathematical work based on these criteria:

"""
        
        # Add rubric categories
        for category in rubric.get('categories', []):
            weight_percent = category['weight'] * 100
            prompt += f"### {category['name']} ({weight_percent:.0f}% of grade)\n"
            prompt += f"{category['description']}\n\n"
        
        prompt += """## Feedback Instructions

Provide comprehensive feedback focusing on:

1. Mathematical correctness and rigor
2. Clarity of explanation and notation
3. Logical flow and proof structure
4. Problem-solving approach
5. Mathematical communication

When referencing mathematical expressions, use LaTeX notation.

Return your response in this exact JSON format:
{
    "overall": {
        "score": <0-100>,
        "strengths": ["strength 1", "strength 2"],
        "improvements": ["improvement 1", "improvement 2"],
        "suggestions": ["specific suggestion 1", "specific suggestion 2"]
    },
    "criteria": {
        "<category_name>": {
            "score": <0-100>,
            "strengths": ["mathematical strength"],
            "improvements": ["area for improvement"],
            "suggestions": ["suggestion 1", "suggestion 2"]
        }
    },
    "mathematical_errors": [
        {
            "location": "description of where",
            "error": "description of error",
            "correction": "correct approach"
        }
    ]
}"""
        
        return prompt
    
    def format_feedback(self, raw_feedback: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format math feedback for display."""
        formatted = {
            "overall": raw_feedback.get("overall", {}),
            "criteria": raw_feedback.get("criteria", {}),
            "mathematical_errors": raw_feedback.get("mathematical_errors", []),
            "metadata": {
                "assessment_type": "math",
                "has_latex": metadata.get("has_latex", False)
            }
        }
        
        # Mark LaTeX expressions for rendering
        formatted["requires_latex_rendering"] = True
        
        return formatted
    
    def _extract_latex(self, content: str) -> List[str]:
        """Extract LaTeX expressions from content."""
        # Match $...$ and $$...$$ patterns
        inline_pattern = r'\$([^\$]+)\$'
        display_pattern = r'\$\$([^\$]+)\$\$'
        
        inline_matches = re.findall(inline_pattern, content)
        display_matches = re.findall(display_pattern, content)
        
        return inline_matches + display_matches
    
    def _make_latex_readable(self, content: str) -> str:
        """Convert LaTeX to more readable format for LLM."""
        # This is a simplified version - real implementation would handle more cases
        readable = content
        
        # Common LaTeX replacements
        replacements = {
            r'\frac{': 'fraction: (',
            r'\sqrt{': 'square root of (',
            r'\sum': 'sum',
            r'\int': 'integral',
            r'\infty': 'infinity',
            r'\alpha': 'alpha',
            r'\beta': 'beta',
            r'\gamma': 'gamma',
            r'\theta': 'theta',
            r'\pi': 'pi',
            r'\leq': '≤',
            r'\geq': '≥',
            r'\neq': '≠',
            r'\approx': '≈'
        }
        
        for latex, readable_text in replacements.items():
            readable = readable.replace(latex, readable_text)
        
        return readable
    
    def _analyze_math_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of mathematical content."""
        lower_content = content.lower()
        
        # Detect type of mathematical content
        if 'proof' in lower_content or 'theorem' in lower_content:
            math_type = 'proof'
        elif 'solve' in lower_content or 'calculate' in lower_content:
            math_type = 'calculation'
        elif 'derive' in lower_content:
            math_type = 'derivation'
        else:
            math_type = 'general'
        
        return {
            "type": math_type,
            "has_proof": 'proof' in lower_content,
            "has_equations": '=' in content,
            "has_calculations": any(op in content for op in ['+', '-', '*', '/', '^'])
        }
    
    def get_rubric_template(self) -> Dict[str, Any]:
        """Get math-specific rubric template."""
        return {
            "categories": [
                {
                    "name": "Mathematical Correctness",
                    "description": "Accuracy of calculations, proofs, and mathematical reasoning",
                    "weight": 0.4
                },
                {
                    "name": "Problem Solving Approach",
                    "description": "Logical method and strategy used to solve problems",
                    "weight": 0.25
                },
                {
                    "name": "Mathematical Communication",
                    "description": "Clear notation, proper formatting, and explanation of steps",
                    "weight": 0.2
                },
                {
                    "name": "Completeness",
                    "description": "All parts of the problem addressed with sufficient detail",
                    "weight": 0.15
                }
            ]
        }