"""
Video assessment type handler
"""

import json
from typing import Any, Optional

from app.assessment.base import AssessmentHandler
from app.models.assessment import AssessmentService, assessment_services


class VideoAssessmentHandler(AssessmentHandler):
    """
    Handler for video-based assessments.

    This handler integrates with external video processing services
    to extract transcripts and analyze video presentations.
    """

    def validate_submission(
        self, content: Any, metadata: dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate video submission."""
        # For video, content should be a file path
        if metadata.get("submission_type") != "file":
            return False, "Video submissions must be uploaded as files"

        if not content or not isinstance(content, str):
            return False, "Video file path is required"

        # Check file extension
        allowed_extensions = self.get_allowed_extensions()
        file_ext = content.lower().split(".")[-1] if "." in content else ""

        if f".{file_ext}" not in allowed_extensions:
            return (
                False,
                f"File type .{file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}",
            )

        # Check if external service is configured
        if not self._get_video_service():
            return (
                False,
                "Video assessment service is not configured. Please contact your administrator.",
            )

        return True, None

    def preprocess(self, content: Any, metadata: dict[str, Any]) -> dict[str, Any]:
        """Preprocess video using external service."""
        # Get the video processing service
        service = self._get_video_service()

        if not service:
            return {
                "processed_text": "Error: Video processing service not available",
                "additional_context": {"error": True},
                "metadata": {**metadata, "preprocessing_complete": False},
            }

        # Simulate calling external service
        # In real implementation, this would make an API call to your Electron app service
        video_analysis = self._call_video_service(content, service, metadata)

        return {
            "processed_text": video_analysis.get("transcript", ""),
            "additional_context": {
                "duration_seconds": video_analysis.get("duration", 0),
                "key_frames": video_analysis.get("key_frames", []),
                "audio_quality": video_analysis.get("audio_quality", "unknown"),
                "video_quality": video_analysis.get("video_quality", "unknown"),
                "speaker_confidence": video_analysis.get("speaker_confidence", 0),
                "topics_detected": video_analysis.get("topics", []),
            },
            "metadata": {
                **metadata,
                "service_used": service.service_name,
                "preprocessing_complete": True,
            },
        }

    def get_prompt_template(
        self, rubric: dict[str, Any], processed_content: dict[str, Any]
    ) -> str:
        """Generate video-specific prompt."""
        context = processed_content["additional_context"]

        # Handle error case
        if context.get("error"):
            return "Error: Unable to process video submission"

        duration_min = context["duration_seconds"] / 60

        prompt = f"""You are an expert evaluating a video presentation submission.

## Assignment Context
Title: {rubric.get("assignment_title", "Video Presentation Assignment")}
Description: {rubric.get("assignment_description", "Evaluate this video presentation")}
Video Duration: {duration_min:.1f} minutes
Audio Quality: {context["audio_quality"]}
Speaker Confidence: {context["speaker_confidence"]}%

## Video Transcript

{processed_content["processed_text"]}

## Additional Context
Topics Detected: {", ".join(context["topics_detected"])}

## Evaluation Criteria
Please evaluate the video presentation based on these criteria:

"""

        # Add rubric categories
        for category in rubric.get("categories", []):
            weight_percent = category["weight"] * 100
            prompt += f"### {category['name']} ({weight_percent:.0f}% of grade)\n"
            prompt += f"{category['description']}\n\n"

        prompt += """## Feedback Instructions

Provide comprehensive feedback on the video presentation, considering:

1. Content quality and accuracy
2. Presentation skills and delivery
3. Visual aids and production quality
4. Organization and time management
5. Engagement and communication effectiveness

Note: Base your evaluation primarily on the transcript and provided metrics.

Return your response in this exact JSON format:
{
    "overall": {
        "score": <0-100>,
        "strengths": ["presentation strength 1", "presentation strength 2"],
        "improvements": ["improvement area 1", "improvement area 2"],
        "suggestions": ["specific suggestion 1", "specific suggestion 2"]
    },
    "criteria": {
        "<category_name>": {
            "score": <0-100>,
            "strengths": ["specific strength"],
            "improvements": ["area for improvement"],
            "suggestions": ["suggestion 1", "suggestion 2"]
        }
    },
    "presentation_feedback": {
        "delivery": "feedback on speaking and presentation style",
        "content_organization": "feedback on how content was structured",
        "visual_elements": "feedback on any visual aids mentioned",
        "timing": "feedback on pacing and time management"
    }
}"""

        return prompt

    def format_feedback(
        self, raw_feedback: dict[str, Any], metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Format video feedback for display."""
        formatted = {
            "overall": raw_feedback.get("overall", {}),
            "criteria": raw_feedback.get("criteria", {}),
            "presentation_feedback": raw_feedback.get("presentation_feedback", {}),
            "metadata": {
                "assessment_type": "video",
                "duration_seconds": metadata.get("duration_seconds", 0),
                "service_used": metadata.get("service_used", "unknown"),
            },
        }

        # Add video-specific display hints
        formatted["show_video_preview"] = True
        formatted["show_timeline_feedback"] = bool(metadata.get("timestamps"))

        return formatted

    def _get_video_service(self) -> Optional[AssessmentService]:
        """Get configured video processing service."""
        try:
            # Look for active video processing service
            services = assessment_services()
            for service in services:
                if service.is_active:
                    service_types = json.loads(service.assessment_types)
                    if "video" in service_types:
                        return service
        except Exception as e:
            print(f"Error getting video service: {e}")

        return None

    def _call_video_service(
        self, video_path: str, service: AssessmentService, metadata: dict[str, Any]
    ) -> dict[str, Any]:
        """Call external video processing service."""
        # This is a mock implementation
        # In reality, this would make an HTTP request to your Electron app service

        # Example of what the real implementation might look like:
        # import requests
        # response = requests.post(
        #     f"{service.service_url}/analyze",
        #     json={"video_path": video_path, "metadata": metadata},
        #     headers={"Authorization": f"Bearer {service.api_key}"},
        #     timeout=service.timeout_seconds
        # )
        # return response.json()

        # Mock response for development
        return {
            "transcript": """Hello, today I'll be presenting on the topic of sustainable energy.

            First, let me discuss solar power. Solar energy is one of the most promising
            renewable energy sources. It's clean, abundant, and becoming more affordable.

            Next, I'll cover wind energy. Wind turbines can generate significant amounts
            of electricity, especially in coastal and mountainous regions.

            Finally, let's look at the future. Combining multiple renewable sources
            will be key to achieving energy independence.

            Thank you for watching my presentation.""",
            "duration": 180,  # 3 minutes
            "audio_quality": "good",
            "video_quality": "HD",
            "speaker_confidence": 85,
            "topics": [
                "renewable energy",
                "solar power",
                "wind energy",
                "sustainability",
            ],
            "key_frames": [
                {"timestamp": 10, "description": "Title slide"},
                {"timestamp": 30, "description": "Solar panel diagram"},
                {"timestamp": 90, "description": "Wind turbine illustration"},
                {"timestamp": 150, "description": "Future projections chart"},
            ],
        }

    def get_rubric_template(self) -> dict[str, Any]:
        """Get video-specific rubric template."""
        return {
            "categories": [
                {
                    "name": "Content Quality",
                    "description": "Accuracy, depth, and relevance of presented information",
                    "weight": 0.35,
                },
                {
                    "name": "Presentation Skills",
                    "description": "Speaking clarity, engagement, and professional delivery",
                    "weight": 0.3,
                },
                {
                    "name": "Visual Production",
                    "description": "Quality of visual aids, video/audio quality, and editing",
                    "weight": 0.2,
                },
                {
                    "name": "Organization",
                    "description": "Logical flow, time management, and structure",
                    "weight": 0.15,
                },
            ]
        }
