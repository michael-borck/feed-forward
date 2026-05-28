"""
CSV builders for instructor exports.

Kept separate from the route module so unit tests don't drag in the FastHTML
app initialisation (which requires ``.env`` at import time). Each function
takes the rows it needs and returns a CSV string — the caller wraps it in a
Starlette ``Response`` with ``Content-Disposition``.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Iterable
from typing import Any

SUBMISSION_FIELDS = ["student_email", "version", "status", "submission_date", "score"]


def build_submissions_csv(rows: Iterable[tuple[Any, float | None]]) -> str:
    """CSV body for the per-assignment "Export Data" download.

    ``rows`` is an iterable of ``(draft, overall_score_or_None)`` pairs. The
    score is the aggregated 0-100 across rubric categories; ``None`` renders as
    an empty cell so spreadsheets can distinguish "no feedback yet" from "zero".
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(SUBMISSION_FIELDS)
    for draft, score in rows:
        writer.writerow(
            [
                getattr(draft, "student_email", ""),
                getattr(draft, "version", ""),
                getattr(draft, "status", ""),
                getattr(draft, "submission_date", ""),
                f"{score:.1f}" if score is not None else "",
            ]
        )
    return buf.getvalue()
