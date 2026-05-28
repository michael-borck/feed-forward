"""
Filter assignments by the student-course-view tab selection.

Tabs (``?filter=...``):
- ``all``        — every assignment (unchanged input).
- ``active``     — ``status == "active"``.
- ``completed``  — ``status == "closed"`` (matches the existing sidebar summary).

Anything else (missing param, typo, etc.) falls through to ``all`` — the UI
should still render rather than refuse on a bad query string.
"""

from typing import Any


def filter_assignments_by_status(
    assignments_list: list[Any], filter_name: str
) -> list[Any]:
    """Return assignments matching the tab's filter. ``filter_name`` is lowercase."""
    if filter_name == "active":
        return [a for a in assignments_list if a.status == "active"]
    if filter_name == "completed":
        return [a for a in assignments_list if a.status == "closed"]
    return list(assignments_list)
