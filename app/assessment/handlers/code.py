"""
Code assessment type handler
"""

from typing import Any, Optional

from app.assessment.base import AssessmentHandler


class CodeAssessmentHandler(AssessmentHandler):
    """
    Handler for programming code assessments.

    This handler processes code submissions and evaluates them based on
    correctness, style, efficiency, and best practices.
    """

    def validate_submission(
        self, content: Any, metadata: dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate code submission."""
        if not content:
            return False, "Code content is required"

        # Check if it's a file path or direct code
        if metadata.get("submission_type") == "file":
            # File validation would happen elsewhere
            return True, None

        # For direct text input
        if not isinstance(content, str) or not content.strip():
            return False, "Code cannot be empty"

        # Check code length
        lines = content.strip().split("\n")
        if len(lines) > 1000:
            return False, "Code exceeds maximum length of 1000 lines"

        return True, None

    def preprocess(self, content: Any, metadata: dict[str, Any]) -> dict[str, Any]:
        """Preprocess code for AI evaluation."""
        # Detect language if not specified
        language = metadata.get("language", self._detect_language(content))

        # Add line numbers for reference
        lines = content.split("\n")
        numbered_content = "\n".join(
            f"{i + 1:4d}: {line}" for i, line in enumerate(lines)
        )

        # Extract code metrics
        metrics = self._analyze_code_metrics(content, language)

        return {
            "processed_text": numbered_content,
            "additional_context": {
                "language": language,
                "metrics": metrics,
                "line_count": len(lines),
                "has_comments": any(
                    "//" in line or "#" in line or "/*" in line for line in lines
                ),
                "has_functions": self._detect_functions(content, language),
            },
            "metadata": {
                **metadata,
                "language": language,
                "preprocessing_complete": True,
            },
        }

    def get_prompt_template(
        self, rubric: dict[str, Any], processed_content: dict[str, Any]
    ) -> str:
        """Generate code-specific prompt."""
        context = processed_content["additional_context"]

        prompt = f"""You are an expert programming instructor evaluating a code submission.

## Assignment Context
Title: {rubric.get("assignment_title", "Programming Assignment")}
Description: {rubric.get("assignment_description", "Evaluate this code submission")}
Language: {context["language"]}
Lines of Code: {context["line_count"]}

## Code Submission (with line numbers)
```{context["language"]}
{processed_content["processed_text"]}
```

## Evaluation Criteria
Please evaluate the code based on these criteria:

"""

        # Add rubric categories
        for category in rubric.get("categories", []):
            weight_percent = category["weight"] * 100
            prompt += f"### {category['name']} ({weight_percent:.0f}% of grade)\n"
            prompt += f"{category['description']}\n\n"

        prompt += """## Feedback Instructions

Provide comprehensive feedback in JSON format, focusing on:

1. Code correctness and functionality
2. Code style and readability
3. Efficiency and optimization
4. Best practices and design patterns
5. Error handling and edge cases

Include specific line numbers when referencing code.

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
            "strengths": ["strength with line reference"],
            "improvements": ["improvement with line reference"],
            "suggestions": ["suggestion 1", "suggestion 2"]
        }
    },
    "code_issues": [
        {
            "line": <line_number>,
            "issue": "description",
            "suggestion": "how to fix"
        }
    ]
}"""

        return prompt

    def format_feedback(
        self, raw_feedback: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Format code feedback for display."""
        formatted = {
            "overall": raw_feedback.get("overall", {}),
            "criteria": raw_feedback.get("criteria", {}),
            "code_issues": raw_feedback.get("code_issues", []),
            "metadata": {
                "assessment_type": "code",
                "language": metadata.get("language", "unknown"),
                "line_count": metadata.get("line_count", 0),
            },
        }

        # Sort code issues by line number
        if formatted["code_issues"]:
            formatted["code_issues"].sort(key=lambda x: x.get("line", 0))

        return formatted

    def _detect_language(self, code: str) -> str:
        """Simple language detection based on syntax."""
        # This is a simplified version - real implementation would be more robust
        if "def " in code and ":" in code:
            return "python"
        elif "function" in code or "const " in code or "=>" in code:
            return "javascript"
        elif "public class" in code or "public static void main" in code:
            return "java"
        elif "#include" in code:
            return "cpp"
        elif "<html" in code or "<div" in code:
            return "html"
        elif "{" in code and "}" in code and ";" in code:
            return "c"
        else:
            return "text"

    def _analyze_code_metrics(self, code: str, language: str) -> dict[str, Any]:
        """Analyze basic code metrics."""
        lines = code.split("\n")

        return {
            "total_lines": len(lines),
            "blank_lines": sum(1 for line in lines if not line.strip()),
            "comment_lines": sum(
                1 for line in lines if self._is_comment(line.strip(), language)
            ),
            "code_lines": sum(
                1
                for line in lines
                if line.strip() and not self._is_comment(line.strip(), language)
            ),
        }

    def _is_comment(self, line: str, language: str) -> bool:
        """Check if a line is a comment."""
        if not line:
            return False

        comment_markers = {
            "python": ["#"],
            "javascript": ["//", "/*", "*/", "*"],
            "java": ["//", "/*", "*/", "*"],
            "cpp": ["//", "/*", "*/", "*"],
            "c": ["//", "/*", "*/", "*"],
            "html": ["<!--", "-->"],
        }

        markers = comment_markers.get(language, ["//", "#"])
        return any(line.startswith(marker) for marker in markers)

    def _detect_functions(self, code: str, language: str) -> bool:
        """Detect if code contains function definitions."""
        function_patterns = {
            "python": "def ",
            "javascript": ["function ", "=>"],
            "java": ["public ", "private ", "protected "],
            "cpp": ["void ", "int ", "double ", "float "],
            "c": ["void ", "int ", "double ", "float "],
        }

        patterns = function_patterns.get(language, [])
        if isinstance(patterns, str):
            patterns = [patterns]

        return any(pattern in code for pattern in patterns)

    def get_rubric_template(self) -> dict[str, Any]:
        """Get code-specific rubric template."""
        return {
            "categories": [
                {
                    "name": "Functionality",
                    "description": "Code works correctly and meets all requirements",
                    "weight": 0.4,
                },
                {
                    "name": "Code Quality",
                    "description": "Clean, readable, well-organized code with appropriate comments",
                    "weight": 0.25,
                },
                {
                    "name": "Efficiency",
                    "description": "Efficient algorithms and resource usage",
                    "weight": 0.2,
                },
                {
                    "name": "Best Practices",
                    "description": "Follows language conventions and design patterns",
                    "weight": 0.15,
                },
            ]
        }
