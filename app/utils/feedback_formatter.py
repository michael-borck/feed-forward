"""
Enhanced feedback visualization and formatting utilities
"""

from typing import Any, Optional

from fasthtml import common as fh


def get_score_color(score: float) -> str:
    """
    Get color based on score.

    Args:
        score: Score value (0-100)

    Returns:
        Color name for styling
    """
    if score >= 90:
        return "emerald"  # Excellent
    elif score >= 80:
        return "green"    # Good
    elif score >= 70:
        return "yellow"   # Satisfactory
    elif score >= 60:
        return "orange"   # Needs improvement
    else:
        return "red"      # Poor


def get_score_icon(score: float) -> str:
    """
    Get emoji icon based on score.

    Args:
        score: Score value (0-100)

    Returns:
        Emoji icon
    """
    if score >= 90:
        return "🌟"  # Star
    elif score >= 80:
        return "✅"  # Check
    elif score >= 70:
        return "👍"  # Thumbs up
    elif score >= 60:
        return "💡"  # Light bulb (needs improvement)
    else:
        return "⚠️"  # Warning


def score_bar(score: float, max_score: float = 100, height: str = "h-2") -> fh.Div:
    """
    Create a visual score bar.

    Args:
        score: Current score
        max_score: Maximum possible score
        height: Height class for the bar

    Returns:
        Div element with score bar
    """
    percentage = (score / max_score) * 100 if max_score > 0 else 0
    color = get_score_color(score)

    # Color mapping for Tailwind classes
    color_classes = {
        "emerald": "bg-emerald-500",
        "green": "bg-green-500",
        "yellow": "bg-yellow-500",
        "orange": "bg-orange-500",
        "red": "bg-red-500",
    }

    bg_color = color_classes.get(color, "bg-gray-500")

    return fh.Div(
        fh.Div(
            fh.Div(
                cls=f"{bg_color} {height} rounded-full transition-all duration-500",
                style=f"width: {percentage:.1f}%",
            ),
            cls=f"bg-gray-200 {height} rounded-full overflow-hidden",
        ),
        fh.P(
            f"{score:.0f}/{max_score:.0f}",
            cls="text-xs text-gray-600 mt-1",
        ),
    )


def rubric_category_card(
    category_name: str,
    category_description: str,
    score: float,
    feedback_text: str,
    weight: float = 0,
    show_details: bool = True
) -> fh.Div:
    """
    Create an enhanced rubric category feedback card.

    Args:
        category_name: Name of the rubric category
        category_description: Description of what's being evaluated
        score: Score for this category
        feedback_text: Detailed feedback text
        weight: Weight percentage of this category
        show_details: Whether to show detailed feedback

    Returns:
        Div element with formatted feedback card
    """
    color = get_score_color(score)
    icon = get_score_icon(score)

    # Color mapping for borders and backgrounds
    color_classes = {
        "emerald": ("border-emerald-200", "bg-emerald-50", "text-emerald-800"),
        "green": ("border-green-200", "bg-green-50", "text-green-800"),
        "yellow": ("border-yellow-200", "bg-yellow-50", "text-yellow-800"),
        "orange": ("border-orange-200", "bg-orange-50", "text-orange-800"),
        "red": ("border-red-200", "bg-red-50", "text-red-800"),
    }

    border_color, bg_color, text_color = color_classes.get(
        color, ("border-gray-200", "bg-gray-50", "text-gray-800")
    )

    return fh.Div(
        # Header with category name and score
        fh.Div(
            fh.Div(
                fh.H4(
                    fh.Span(icon, cls="mr-2"),
                    category_name,
                    fh.Span(
                        f"({weight:.0f}%)" if weight > 0 else "",
                        cls="text-sm font-normal text-gray-500 ml-2",
                    ),
                    cls="text-lg font-semibold text-gray-800",
                ),
                fh.Div(
                    fh.Span(
                        f"{score:.0f}",
                        cls=f"text-2xl font-bold {text_color}",
                    ),
                    fh.Span(
                        "/100",
                        cls="text-sm text-gray-500 ml-1",
                    ),
                    cls="text-right",
                ),
                cls="flex justify-between items-center mb-3",
            ),
            # Score bar
            score_bar(score, 100, "h-3"),
            cls="mb-4",
        ),
        # Category description
        (
            fh.P(
                category_description,
                cls="text-sm text-gray-600 italic mb-3",
            )
            if category_description and show_details
            else ""
        ),
        # Feedback text
        (
            fh.Div(
                fh.P(
                    feedback_text,
                    cls="text-gray-700 text-sm leading-relaxed",
                ),
                cls=f"p-3 {bg_color} rounded-lg border {border_color}",
            )
            if show_details
            else ""
        ),
        cls="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow",
    )


def overall_feedback_summary(
    overall_score: float,
    category_scores: dict[str, dict[str, Any]],
    strengths: Optional[list[str]] = None,
    improvements: Optional[list[str]] = None,
    draft_version: int = 1,
    max_drafts: int = 3
) -> fh.Div:
    """
    Create an overall feedback summary with visual elements.

    Args:
        overall_score: Overall assignment score
        category_scores: Dictionary of category scores and info
        strengths: List of strength points
        improvements: List of improvement suggestions
        draft_version: Current draft number
        max_drafts: Maximum allowed drafts

    Returns:
        Div element with overall feedback summary
    """
    color = get_score_color(overall_score)
    icon = get_score_icon(overall_score)

    # Performance level text
    if overall_score >= 90:
        level_text = "Excellent Work!"
    elif overall_score >= 80:
        level_text = "Good Job!"
    elif overall_score >= 70:
        level_text = "Satisfactory"
    elif overall_score >= 60:
        level_text = "Needs Improvement"
    else:
        level_text = "Requires Significant Work"

    return fh.Div(
        # Overall score display
        fh.Div(
            fh.Div(
                fh.Div(
                    fh.Span(icon, cls="text-5xl"),
                    fh.H2(
                        f"{overall_score:.0f}",
                        cls="text-6xl font-bold text-gray-800",
                    ),
                    fh.P(
                        "Overall Score",
                        cls="text-sm text-gray-600 mt-1",
                    ),
                    cls="text-center",
                ),
                fh.Div(
                    fh.H3(
                        level_text,
                        cls=f"text-2xl font-semibold {get_level_text_color(color)} mb-2",
                    ),
                    fh.P(
                        f"Draft {draft_version} of {max_drafts}",
                        cls="text-gray-600",
                    ),
                    cls="text-center",
                ),
                cls="flex flex-col md:flex-row items-center justify-center gap-8 mb-6",
            ),
            # Visual score meter
            fh.Div(
                score_bar(overall_score, 100, "h-4"),
                cls="max-w-md mx-auto mb-6",
            ),
            cls="bg-gradient-to-br from-indigo-50 to-white p-6 rounded-xl mb-6",
        ),
        # Category breakdown
        (
            fh.Div(
                fh.H4(
                    "Score Breakdown",
                    cls="text-lg font-semibold text-gray-800 mb-4",
                ),
                fh.Div(
                    *(
                        fh.Div(
                            fh.Div(
                                fh.Span(
                                    cat_name,
                                    cls="text-sm text-gray-700",
                                ),
                                fh.Span(
                                    f"{cat_info.get('score', 0):.0f}",
                                    cls="text-sm font-semibold text-gray-800",
                                ),
                                cls="flex justify-between mb-1",
                            ),
                            score_bar(cat_info.get('score', 0), 100, "h-2"),
                            cls="mb-3",
                        )
                        for cat_name, cat_info in category_scores.items()
                    ),
                    cls="space-y-2",
                ),
                cls="bg-white p-5 rounded-xl shadow-sm border border-gray-100 mb-6",
            )
            if category_scores
            else ""
        ),
        # Strengths and improvements
        fh.Div(
            # Strengths section
            (
                fh.Div(
                    fh.H4(
                        "✨ Strengths",
                        cls="text-lg font-semibold text-green-700 mb-3",
                    ),
                    fh.Ul(
                        *(
                            fh.Li(
                                strength,
                                cls="text-gray-700 mb-2",
                            )
                            for strength in (strengths or [])
                        ),
                        cls="list-disc list-inside space-y-1",
                    ),
                    cls="bg-green-50 p-4 rounded-lg border border-green-200",
                )
                if strengths
                else ""
            ),
            # Improvements section
            (
                fh.Div(
                    fh.H4(
                        "💡 Areas for Improvement",
                        cls="text-lg font-semibold text-orange-700 mb-3",
                    ),
                    fh.Ul(
                        *(
                            fh.Li(
                                improvement,
                                cls="text-gray-700 mb-2",
                            )
                            for improvement in (improvements or [])
                        ),
                        cls="list-disc list-inside space-y-1",
                    ),
                    cls="bg-orange-50 p-4 rounded-lg border border-orange-200",
                )
                if improvements
                else ""
            ),
            cls="grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
    )


def get_level_text_color(color: str) -> str:
    """Get text color class based on performance level."""
    color_map = {
        "emerald": "text-emerald-700",
        "green": "text-green-700",
        "yellow": "text-yellow-700",
        "orange": "text-orange-700",
        "red": "text-red-700",
    }
    return color_map.get(color, "text-gray-700")


def draft_progress_indicator(
    drafts_data: list[dict[str, Any]],
    current_draft: int
) -> fh.Div:
    """
    Create a visual progress indicator for draft improvements.

    Args:
        drafts_data: List of draft data with scores
        current_draft: Current draft index

    Returns:
        Div element with progress visualization
    """
    if not drafts_data or len(drafts_data) < 2:
        return fh.Div()  # No progress to show

    # Calculate improvement
    first_score = drafts_data[0].get('score', 0)
    latest_score = drafts_data[-1].get('score', 0)
    improvement = latest_score - first_score

    improvement_icon = "📈" if improvement > 0 else "📉" if improvement < 0 else "➡️"
    improvement_color = "text-green-600" if improvement > 0 else "text-red-600" if improvement < 0 else "text-gray-600"

    return fh.Div(
        fh.H4(
            "Progress Across Drafts",
            cls="text-lg font-semibold text-gray-800 mb-4",
        ),
        # Score progression chart
        fh.Div(
            fh.Div(
                *(
                    fh.Div(
                        fh.Div(
                            fh.Div(
                                cls=f"w-full bg-{get_score_color(d.get('score', 0))}-500 rounded-t",
                                style=f"height: {d.get('score', 0)}%;",
                            ),
                            cls="relative h-32 bg-gray-100 rounded flex items-end",
                        ),
                        fh.P(
                            f"D{i+1}",
                            cls="text-xs text-center mt-1 text-gray-600",
                        ),
                        fh.P(
                            f"{d.get('score', 0):.0f}",
                            cls="text-xs text-center font-semibold",
                        ),
                        cls="flex-1",
                    )
                    for i, d in enumerate(drafts_data)
                ),
                cls="flex gap-2 mb-4",
            ),
            cls="p-4 bg-gray-50 rounded-lg",
        ),
        # Improvement summary
        fh.Div(
            fh.Span(improvement_icon, cls="text-2xl mr-2"),
            fh.Span(
                f"{abs(improvement):.1f} point {'improvement' if improvement > 0 else 'decrease' if improvement < 0 else 'change'}",
                cls=f"{improvement_color} font-semibold",
            ),
            cls="text-center p-3 bg-white rounded-lg border border-gray-200",
        ),
        cls="bg-white p-5 rounded-xl shadow-sm border border-gray-100",
    )
