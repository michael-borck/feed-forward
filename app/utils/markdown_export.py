"""
Markdown builders for instructor downloads.

Kept separate from the route module so unit tests don't drag in the FastHTML
app initialisation (which still depends on ``.env`` at import time). Each
function takes the rows it needs and returns the full Markdown string — the
caller wraps it in a Starlette ``Response`` with ``Content-Disposition``.
"""

from __future__ import annotations

from typing import Any


def build_feedback_markdown(
    draft: Any,
    assignment: Any,
    course_title: str,
    aggregated_rows: list[Any],
    category_name_by_id: dict[int, str],
) -> str:
    """Render one draft's aggregated feedback as a self-contained Markdown doc.

    ``aggregated_rows`` is the list of ``AggregatedFeedback`` rows for the
    draft (one per rubric category). ``category_name_by_id`` maps
    ``rubric_category_id -> human name``; missing ids fall back to
    ``"Category N"`` so the export always produces something readable.

    Overall score is the unweighted average of category scores. Status:
    "Released (release_date)" if any row is ``approved``; otherwise
    "Pending review". A footer per category notes the instructor when
    ``edited_by_instructor`` is set.
    """
    lines: list[str] = []
    lines.append(f"# Feedback - {assignment.title}")
    lines.append("")
    lines.append(f"- **Course:** {course_title}")
    lines.append(f"- **Student:** {draft.student_email}")
    lines.append(f"- **Draft:** version {draft.version}")
    lines.append(f"- **Submitted:** {draft.submission_date}")

    if aggregated_rows:
        scores = [af.aggregated_score for af in aggregated_rows]
        overall = sum(scores) / len(scores)
        lines.append(f"- **Overall:** {overall:.1f}/100")
        if any(af.status == "approved" for af in aggregated_rows):
            release = next(
                (af.release_date for af in aggregated_rows if af.release_date), ""
            )
            suffix = f" ({release})" if release else ""
            lines.append(f"- **Status:** Released{suffix}")
        else:
            lines.append("- **Status:** Pending review")

    lines.append("")
    lines.append("## Category feedback")
    lines.append("")

    if not aggregated_rows:
        lines.append("_No aggregated feedback yet._")
        lines.append("")
        return "\n".join(lines)

    for af in aggregated_rows:
        name = category_name_by_id.get(af.category_id, f"Category {af.category_id}")
        lines.append(f"### {name} - {af.aggregated_score:.1f}/100")
        lines.append("")
        text = (getattr(af, "feedback_text", "") or "").strip()
        lines.append(text if text else "_(no feedback text)_")
        lines.append("")
        if getattr(af, "edited_by_instructor", False):
            who = getattr(af, "instructor_email", "") or "instructor"
            lines.append(f"_Reviewed by {who}._")
            lines.append("")

    return "\n".join(lines)
