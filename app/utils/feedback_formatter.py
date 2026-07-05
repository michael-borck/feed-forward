"""
Feedback visualization and formatting utilities — Editorial direction.

Every public renderer takes a ``display`` mode that controls how performance
is expressed to students (FeedForward does not show numeric scores by
default — see docs/design/direction-editorial-2026-07.md):

- ``"icon"``   (default) — the dartboard: ``bullseye_progress`` glyphs whose
  dart sits closer to the centre as work improves, plus qualitative level
  words. No digits.
- ``"hidden"`` — qualitative level words and the written feedback only.
- ``"numeric"`` — scores shown as serif numerals (instructor opt-in via the
  assignment's mark display option).

Scores still arrive as floats in all modes — they drive glyph closeness and
level words; the mode only controls whether digits are rendered.
"""

from typing import Any, Optional

from fasthtml import common as fh

from app.utils.design import COLOR, RADIUS, TEXT
from app.utils.ui import bullseye_progress

DISPLAY_NUMERIC = "numeric"
DISPLAY_HIDDEN = "hidden"
DISPLAY_ICON = "icon"
DEFAULT_DISPLAY = DISPLAY_ICON

_INK = "#1a2e44"


def get_score_color(score: float) -> str:
    """Editorial semantic colour family for a score: teal / amber / red."""
    if score >= 80:
        return "teal"
    elif score >= 60:
        return "amber"
    else:
        return "red"


def get_level_text(score: float) -> str:
    """Qualitative level word — the student-facing vocabulary for a score."""
    if score >= 90:
        return "On the bullseye"
    elif score >= 80:
        return "Closing in"
    elif score >= 70:
        return "On the board"
    elif score >= 60:
        return "Finding the range"
    else:
        return "Take another aim"


def _level_badge(score: float) -> fh.Span:
    color = get_score_color(score)
    return fh.Span(
        get_level_text(score),
        cls=(
            f"{TEXT['label']} text-{color}-700 border border-{color}-200 "
            f"bg-{color}-50 px-3 py-1 rounded-full whitespace-nowrap"
        ),
    )


def score_bar(
    score: float,
    max_score: float = 100,
    height: str = "h-1",
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """
    Hairline score meter (editorial: an ink line on a slate track).

    The numeric caption renders only in ``numeric`` mode.
    """
    percentage = (score / max_score) * 100 if max_score > 0 else 0

    return fh.Div(
        fh.Div(
            fh.Div(
                cls=f"{height} rounded-full transition-all duration-500",
                style=f"width: {percentage:.1f}%; background: {_INK}",
            ),
            cls=f"bg-slate-200 {height} rounded-full overflow-hidden",
        ),
        (
            fh.P(
                f"{score:.0f}/{max_score:.0f}",
                cls=f"text-xs text-{COLOR['text_muted']} {TEXT['numeric']} mt-1",
            )
            if display == DISPLAY_NUMERIC
            else ""
        ),
    )


def _performance_cell(score: float, display: str, glyph_size: int = 32):
    """Right-hand performance indicator for a card header, per display mode."""
    if display == DISPLAY_NUMERIC:
        return fh.Div(
            fh.Span(
                f"{score:.0f}",
                cls=f"font-serif text-2xl font-semibold text-{COLOR['text_strong']}",
            ),
            fh.Span("/100", cls=f"text-sm text-{COLOR['text_muted']} ml-1"),
            cls="text-right shrink-0",
        )
    if display == DISPLAY_ICON:
        return fh.Div(
            bullseye_progress(score / 100, size=glyph_size),
            _level_badge(score),
            cls="flex items-center gap-3 shrink-0",
        )
    return fh.Div(_level_badge(score), cls="shrink-0")


def rubric_category_card(
    category_name: str,
    category_description: str,
    score: float,
    feedback_text: str,
    weight: float = 0,
    show_details: bool = True,
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """
    Rubric category feedback card: serif category head, performance cell per
    display mode, feedback text as a left-ruled quote block.
    """
    color = get_score_color(score)

    return fh.Div(
        fh.Div(
            fh.Div(
                fh.H4(
                    category_name,
                    fh.Span(
                        f" ({weight:.0f}%)" if weight > 0 else "",
                        cls=f"text-sm font-normal text-{COLOR['text_muted']} ml-1",
                    ),
                    cls=f"{TEXT['h3']} text-{COLOR['text_strong']}",
                ),
                (
                    fh.P(
                        category_description,
                        cls=f"text-sm text-{COLOR['text_muted']} italic mt-0.5",
                    )
                    if category_description and show_details
                    else ""
                ),
                cls="flex-1 pr-4",
            ),
            _performance_cell(score, display),
            cls="flex justify-between items-start mb-3",
        ),
        (score_bar(score, 100, "h-1", display) if display == DISPLAY_NUMERIC else ""),
        (
            fh.Div(
                fh.P(
                    feedback_text,
                    cls=f"text-{COLOR['text_body']} text-sm leading-relaxed",
                ),
                cls=f"mt-3 pl-4 border-l-2 border-{color}-600",
            )
            if show_details and feedback_text
            else ""
        ),
        cls=(f"bg-{COLOR['surface']} p-5 {RADIUS} border border-{COLOR['border']}"),
    )


def overall_feedback_summary(
    overall_score: float,
    category_scores: dict[str, dict[str, Any]],
    strengths: Optional[list[str]] = None,
    improvements: Optional[list[str]] = None,
    draft_version: int = 1,
    max_drafts: int = 3,
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """Overall feedback summary: hero (per display mode), category breakdown,
    strengths / to-improve columns in the editorial voice."""

    if display == DISPLAY_NUMERIC:
        hero_figure = fh.Div(
            fh.Span(
                f"{overall_score:.0f}",
                cls=f"font-serif text-6xl font-semibold text-{COLOR['text_strong']}",
            ),
            fh.Span("/100", cls=f"text-xl text-{COLOR['text_muted']} ml-1"),
            cls="text-center",
        )
    elif display == DISPLAY_ICON:
        hero_figure = fh.Div(
            bullseye_progress(overall_score / 100, size=88),
            cls="flex justify-center",
        )
    else:
        hero_figure = ""

    hero = fh.Div(
        hero_figure,
        fh.H2(
            get_level_text(overall_score),
            cls=f"{TEXT['h2']} text-{COLOR['text_strong']} mt-4 text-center",
        ),
        fh.P(
            f"Draft {draft_version} of {max_drafts}",
            cls=f"{TEXT['label']} text-{COLOR['text_muted']} mt-1 text-center",
        ),
        (
            fh.Div(
                score_bar(overall_score, 100, "h-1", display),
                cls="max-w-md mx-auto mt-4",
            )
            if display == DISPLAY_NUMERIC
            else ""
        ),
        cls=f"py-6 border-b border-{COLOR['border']} mb-6",
    )

    breakdown = ""
    if category_scores:
        rows = []
        for cat_name, cat_info in category_scores.items():
            cat_score = cat_info.get("score", 0)
            if display == DISPLAY_ICON:
                right = fh.Div(
                    bullseye_progress(cat_score / 100, size=24),
                    cls="shrink-0",
                )
            elif display == DISPLAY_NUMERIC:
                right = fh.Span(
                    f"{cat_score:.0f}",
                    cls=f"text-sm {TEXT['numeric']} text-{COLOR['text_strong']}",
                )
            else:
                right = fh.Span(
                    get_level_text(cat_score),
                    cls=f"text-xs text-{COLOR['text_muted']}",
                )
            rows.append(
                fh.Div(
                    fh.Span(cat_name, cls=f"text-sm text-{COLOR['text_body']} flex-1"),
                    (
                        fh.Div(
                            score_bar(cat_score, 100, "h-1", display="hidden"),
                            cls="w-32 mx-4",
                        )
                        if display != DISPLAY_HIDDEN
                        else ""
                    ),
                    right,
                    cls=(
                        "flex items-center justify-between py-2.5 "
                        f"border-t border-{COLOR['border']}"
                    ),
                )
            )
        breakdown = fh.Div(
            fh.H4(
                "By rubric category",
                cls=f"{TEXT['label']} text-{COLOR['text_muted']} pb-2",
            ),
            *rows,
            cls="mb-6",
        )

    def _quote_column(label: str, items: list[str], color: str):
        if not items:
            return ""
        return fh.Div(
            fh.H4(label, cls=f"{TEXT['label']} text-{color}-700 mb-2"),
            fh.Ul(
                *(
                    fh.Li(item, cls=f"text-sm text-{COLOR['text_body']} mb-2")
                    for item in items
                ),
                cls="list-disc list-inside space-y-1",
            ),
            cls=f"pl-4 border-l-2 border-{color}-600",
        )

    return fh.Div(
        hero,
        breakdown,
        fh.Div(
            _quote_column("Strengths", strengths or [], "teal"),
            _quote_column("To improve", improvements or [], "amber"),
            cls="grid grid-cols-1 md:grid-cols-2 gap-6",
        ),
    )


def draft_progress_indicator(
    drafts_data: list[dict[str, Any]],
    current_draft: int,
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """
    Progress across drafts. Icon mode renders the signature dartboard row —
    one board per draft, the dart landing closer to the bullseye as scores
    rise. Numeric mode renders ink bars with values.
    """
    if not drafts_data or len(drafts_data) < 2:
        return fh.Div()  # No progress to show

    first_score = drafts_data[0].get("score", 0)
    latest_score = drafts_data[-1].get("score", 0)
    improvement = latest_score - first_score

    if improvement > 0:
        trend_color = "text-teal-700"
        trend_text = (
            f"{improvement:.1f} point improvement since Draft 1"
            if display == DISPLAY_NUMERIC
            else "Your aim is improving — the dart is closing on the bullseye."
        )
    elif improvement < 0:
        trend_color = "text-amber-700"
        trend_text = (
            f"{abs(improvement):.1f} point decrease since Draft 1"
            if display == DISPLAY_NUMERIC
            else "This draft landed further out than your first — worth revisiting the feedback."
        )
    else:
        trend_color = f"text-{COLOR['text_muted']}"
        trend_text = (
            "No score change since Draft 1"
            if display == DISPLAY_NUMERIC
            else "Holding steady — aim for the next ring."
        )

    if display == DISPLAY_NUMERIC:
        chart = fh.Div(
            fh.Div(
                *(
                    fh.Div(
                        fh.Div(
                            fh.Div(
                                cls="w-full rounded-t",
                                style=(
                                    f"height: {d.get('score', 0)}%; background: {_INK}"
                                ),
                            ),
                            cls="relative h-32 bg-slate-100 rounded flex items-end",
                        ),
                        fh.P(
                            f"D{i + 1}",
                            cls=f"{TEXT['label']} text-center mt-1 text-{COLOR['text_muted']}",
                        ),
                        fh.P(
                            f"{d.get('score', 0):.0f}",
                            cls=f"text-xs text-center {TEXT['numeric']} font-semibold",
                        ),
                        cls="flex-1",
                    )
                    for i, d in enumerate(drafts_data)
                ),
                cls="flex gap-2",
            ),
            cls=f"p-4 bg-{COLOR['surface_alt']} {RADIUS}",
        )
    else:
        boards = []
        for i, d in enumerate(drafts_data):
            if i > 0:
                boards.append(
                    fh.Span("→", cls=f"text-{COLOR['text_muted']} text-lg px-1")
                )
            boards.append(
                fh.Div(
                    bullseye_progress(d.get("score", 0) / 100, size=48),
                    fh.P(
                        f"Draft {i + 1}",
                        cls=f"{TEXT['label']} text-{COLOR['text_muted']} text-center mt-1",
                    ),
                )
            )
        chart = fh.Div(
            fh.Div(*boards, cls="flex items-center justify-center gap-3 flex-wrap"),
            cls=f"p-5 bg-{COLOR['surface_alt']} {RADIUS}",
        )

    return fh.Div(
        fh.H4(
            "Progress across drafts",
            cls=f"{TEXT['h3']} text-{COLOR['text_strong']} mb-4",
        ),
        chart,
        fh.P(trend_text, cls=f"text-sm {trend_color} font-medium text-center mt-3"),
        cls=f"bg-{COLOR['surface']} p-5 {RADIUS} border border-{COLOR['border']}",
    )


def draft_comparison_card(
    comparison_data: dict[str, Any],
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """Comparison between two drafts, in the editorial voice."""
    if "error" in comparison_data:
        return fh.Div(
            fh.P(comparison_data["error"], cls=f"text-{COLOR['danger']}"),
            cls=f"p-4 bg-red-50 {RADIUS} border-l-2 border-{COLOR['danger']}",
        )

    draft1 = comparison_data["draft1"]
    draft2 = comparison_data["draft2"]
    changes = comparison_data["changes"]
    score_change = changes["score_change"]

    def _draft_figure(draft, emphasize=False):
        if display == DISPLAY_NUMERIC:
            tone = COLOR["text_strong"] if emphasize else COLOR["text_muted"]
            figure = fh.P(
                f"{draft['score']:.0f}",
                cls=f"font-serif text-3xl font-semibold text-{tone}",
            )
        elif display == DISPLAY_ICON:
            figure = bullseye_progress(draft["score"] / 100, size=56)
        else:
            figure = fh.P(
                get_level_text(draft["score"]),
                cls=f"text-sm font-medium text-{COLOR['text_body']}",
            )
        return fh.Div(
            fh.P(
                f"Draft {draft['version']}",
                cls=f"{TEXT['label']} text-{COLOR['text_muted']} mb-2",
            ),
            figure,
            cls="text-center flex flex-col items-center",
        )

    if score_change > 0:
        change_color = "text-teal-700"
        change_text = (
            f"{score_change:.1f} point improvement ({changes['score_change_percent']:.1f}%)"
            if display == DISPLAY_NUMERIC
            else "Closer to the bullseye"
        )
    elif score_change < 0:
        change_color = "text-amber-700"
        change_text = (
            f"{abs(score_change):.1f} point decrease ({changes['score_change_percent']:.1f}%)"
            if display == DISPLAY_NUMERIC
            else "Further from the bullseye"
        )
    else:
        change_color = f"text-{COLOR['text_muted']}"
        change_text = "No change" if display == DISPLAY_NUMERIC else "Holding position"

    def _change_block(label: str, items: list[str], color: str, empty_text: str):
        return fh.Div(
            fh.H4(label, cls=f"{TEXT['label']} text-{color}-700 mb-2"),
            (
                fh.Ul(
                    *(
                        fh.Li(item, cls=f"text-sm text-{COLOR['text_body']}")
                        for item in items
                    ),
                    cls="list-disc list-inside space-y-1",
                )
                if items
                else fh.P(empty_text, cls=f"text-sm text-{COLOR['text_muted']} italic")
            ),
            cls=f"pl-4 border-l-2 border-{color}-600",
        )

    return fh.Div(
        fh.H3(
            f"Draft {draft1['version']} → Draft {draft2['version']}",
            cls=f"{TEXT['h3']} text-{COLOR['text_strong']} mb-4",
        ),
        fh.Div(
            _draft_figure(draft1),
            fh.Span("→", cls=f"text-2xl text-{COLOR['text_muted']} px-4"),
            _draft_figure(draft2, emphasize=True),
            cls="flex justify-center items-center mb-2",
        ),
        fh.P(change_text, cls=f"text-center {change_color} font-medium mb-6"),
        fh.Div(
            (
                _change_block(
                    "Improved",
                    changes["improvement_areas"],
                    "teal",
                    "No significant improvements",
                )
                if changes["improvement_areas"] or score_change > 0
                else ""
            ),
            (
                _change_block(
                    "Worth revisiting",
                    changes["regression_areas"],
                    "amber",
                    "No regressions noted",
                )
                if changes["regression_areas"]
                else ""
            ),
            (
                _change_block(
                    "Maintained strengths",
                    changes["maintained_strengths"],
                    "slate",
                    "Building new strengths",
                )
                if changes["maintained_strengths"]
                else ""
            ),
            cls="space-y-4",
        ),
        (
            fh.P(
                f"Word count: {draft1['word_count']} → {draft2['word_count']} "
                f"({'+' if changes['word_count_change'] > 0 else ''}{changes['word_count_change']} words)",
                cls=f"text-sm text-{COLOR['text_muted']} text-center mt-4 {TEXT['numeric']}",
            )
            if draft1.get("word_count") or draft2.get("word_count")
            else ""
        ),
        cls=f"bg-{COLOR['surface']} p-6 {RADIUS} border border-{COLOR['border']}",
    )


def improvement_metrics_card(
    metrics: dict[str, Any],
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """
    Overall progress overview. Numeric mode shows the metric tiles;
    icon/hidden modes show the first→latest dartboard pair and a trend
    statement (draft counts are not scores, so they always render).
    """
    total_imp = metrics.get("total_improvement", 0)

    submitted_line = fh.P(
        f"Submitted {metrics['drafts_submitted']} draft{'s' if metrics['drafts_submitted'] != 1 else ''}, "
        f"{metrics['drafts_with_feedback']} with feedback",
        cls=f"text-sm text-{COLOR['text_muted']} text-center mt-4",
    )

    if display != DISPLAY_NUMERIC:
        if total_imp > 0:
            trend = ("Improving", "text-teal-700")
        elif total_imp < 0:
            trend = ("Needs another aim", "text-amber-700")
        else:
            trend = ("Holding steady", f"text-{COLOR['text_muted']}")

        figures = (
            fh.Div(
                fh.Div(
                    bullseye_progress(metrics["initial_score"] / 100, size=56),
                    fh.P(
                        "First draft",
                        cls=f"{TEXT['label']} text-{COLOR['text_muted']} text-center mt-1",
                    ),
                ),
                fh.Span("→", cls=f"text-2xl text-{COLOR['text_muted']} px-4"),
                fh.Div(
                    bullseye_progress(metrics["current_score"] / 100, size=56),
                    fh.P(
                        "Latest draft",
                        cls=f"{TEXT['label']} text-{COLOR['text_muted']} text-center mt-1",
                    ),
                ),
                cls="flex items-center justify-center",
            )
            if display == DISPLAY_ICON
            else ""
        )

        return fh.Div(
            fh.H3(
                "Progress overview",
                cls=f"{TEXT['h3']} text-{COLOR['text_strong']} mb-4",
            ),
            figures,
            fh.P(
                f"Overall trend: {trend[0]}",
                cls=f"text-center font-medium {trend[1]} mt-3",
            ),
            submitted_line,
            cls=f"bg-{COLOR['surface']} p-6 {RADIUS} border border-{COLOR['border']}",
        )

    imp_color = (
        "text-teal-700"
        if total_imp > 0
        else "text-red-700"
        if total_imp < 0
        else f"text-{COLOR['text_muted']}"
    )

    def _tile(label: str, value: str, value_color: str):
        return fh.Div(
            fh.P(label, cls=f"{TEXT['label']} text-{COLOR['text_muted']} mb-1"),
            fh.P(
                value,
                cls=f"font-serif text-2xl font-semibold {value_color} {TEXT['numeric']}",
            ),
            cls=(
                f"bg-{COLOR['surface_alt']} p-3 {RADIUS} text-center "
                f"border border-{COLOR['border']}"
            ),
        )

    return fh.Div(
        fh.H3(
            "Progress overview", cls=f"{TEXT['h3']} text-{COLOR['text_strong']} mb-4"
        ),
        fh.Div(
            _tile(
                "Total progress",
                f"{'+' if total_imp > 0 else ''}{total_imp:.1f}",
                imp_color,
            ),
            _tile(
                "Avg per draft",
                f"{'+' if metrics['average_improvement_per_draft'] > 0 else ''}"
                f"{metrics['average_improvement_per_draft']:.1f}",
                f"text-{COLOR['text_strong']}",
            ),
            _tile(
                "Best jump",
                f"+{metrics['best_improvement']:.1f}",
                "text-teal-700",
            ),
            _tile(
                "Consistency",
                f"{metrics['consistency_score']:.0f}%",
                f"text-{COLOR['text_strong']}",
            ),
            cls="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4",
        ),
        fh.Div(
            fh.Div(
                fh.Span(
                    f"{metrics['initial_score']:.0f}",
                    cls=f"text-xs text-{COLOR['text_muted']} {TEXT['numeric']}",
                ),
                fh.Span(
                    f"{metrics['current_score']:.0f}",
                    cls=f"text-xs text-{COLOR['text_muted']} {TEXT['numeric']}",
                ),
                cls="flex justify-between mb-1",
            ),
            score_bar(metrics["current_score"], 100, "h-1", display="hidden"),
        ),
        submitted_line,
        cls=f"bg-{COLOR['surface']} p-6 {RADIUS} border border-{COLOR['border']}",
    )


def next_steps_recommendations(
    recommendations: list[dict[str, Any]],
    max_drafts_remaining: int,
    display: str = DEFAULT_DISPLAY,
) -> fh.Div:
    """Prioritized focus areas for the next draft."""
    if not recommendations:
        return fh.Div()

    priority_colors = {
        "high": "red",
        "medium": "amber",
        "low": "teal",
    }

    cards = []
    for rec in recommendations:
        color = priority_colors.get(rec["priority"], "slate")
        cards.append(
            fh.Div(
                fh.Div(
                    fh.Div(
                        fh.H4(
                            rec["category"],
                            cls=f"font-serif font-semibold text-{COLOR['text_strong']}",
                        ),
                        fh.P(
                            rec["description"],
                            cls=f"text-sm text-{COLOR['text_muted']} mt-1",
                        ),
                        cls="flex-1",
                    ),
                    fh.Span(
                        rec["priority"],
                        cls=(
                            f"{TEXT['label']} text-{color}-700 border "
                            f"border-{color}-200 bg-{color}-50 px-3 py-1 "
                            "rounded-full ml-4 whitespace-nowrap"
                        ),
                    ),
                    cls="flex justify-between items-start mb-2",
                ),
                (
                    fh.Div(
                        fh.Div(
                            fh.P(
                                f"Current: {rec['current_score']:.0f}/100",
                                cls=f"text-sm text-{COLOR['text_muted']} {TEXT['numeric']}",
                            ),
                            fh.P(
                                f"Potential: +{rec['potential_impact']:.1f}",
                                cls=f"text-sm text-teal-700 font-medium {TEXT['numeric']}",
                            ),
                            cls="flex justify-between",
                        ),
                        score_bar(rec["current_score"], 100, "h-1", display="hidden"),
                        cls="mt-2",
                    )
                    if display == DISPLAY_NUMERIC
                    else ""
                ),
                fh.P(
                    rec["action"],
                    cls=f"text-sm mt-2 text-{COLOR['text_body']}",
                ),
                (
                    fh.P(
                        fh.Span("From your feedback: ", cls="font-medium"),
                        rec["example"],
                        cls=f"text-sm text-{COLOR['text_body']} mt-2 italic",
                    )
                    if rec.get("example")
                    else ""
                ),
                (
                    fh.Div(
                        fh.Span(
                            "Resources: ",
                            cls=f"text-sm font-medium text-{COLOR['text_body']}",
                        ),
                        *(
                            fh.A(
                                res["title"],
                                href=res["url"],
                                target="_blank",
                                rel="noopener",
                                cls=(
                                    f"text-sm text-{COLOR['accent']} "
                                    "hover:underline mr-3"
                                ),
                            )
                            for res in rec["resources"]
                        ),
                        cls="mt-2",
                    )
                    if rec.get("resources")
                    else ""
                ),
                cls=f"p-4 {RADIUS} border-l-2 border-{color}-600 bg-{COLOR['surface_alt']}",
            )
        )

    return fh.Div(
        fh.H3(
            "Focus areas for your next draft",
            cls=f"{TEXT['h3']} text-{COLOR['text_strong']} mb-2",
        ),
        (
            fh.P(
                f"You have {max_drafts_remaining} draft{'s' if max_drafts_remaining != 1 else ''} remaining",
                cls=f"text-sm text-{COLOR['text_muted']} mb-4",
            )
            if max_drafts_remaining > 0
            else fh.P(
                "This is your final draft — make it count.",
                cls="text-sm text-amber-700 font-medium mb-4",
            )
        ),
        fh.Div(*cards, cls="space-y-3"),
        cls=f"bg-{COLOR['surface']} p-6 {RADIUS} border border-{COLOR['border']}",
    )
