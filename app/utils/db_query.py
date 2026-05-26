"""
Thin lookup helpers over fastlite ``Table`` objects.

The codebase grew the pattern ``[r for r in table() if r.attr == value]`` —
each one a full-table Python scan, hiding a simple intent behind a
comprehension. This module gives those patterns names and a uniform surface:

- ``by_id(table, pk)`` — indexed primary-key lookup via fastlite ``table[pk]``;
  returns ``None`` when the row doesn't exist.
- ``where(table, **filters)`` — every row matching every keyword filter by
  equality; order preserved.
- ``first(table, **filters)`` — first such row, or ``None``.
- ``count(table, **filters)`` — how many rows match.

Behaviour for non-PK filters is unchanged from the inlined comprehensions: a
Python-side scan over ``table()``. That's deliberate — the win here is the
seam, not performance. Once the seam is in place, switching ``where`` to a
fastlite-native SQL ``where=`` is a one-file change.
"""

from typing import Any, Optional

from apswutils.db import NotFoundError


def by_id(table: Any, pk: Any) -> Optional[Any]:
    """Indexed primary-key lookup. Returns the row dataclass, or ``None``."""
    try:
        return table[pk]
    except NotFoundError:
        return None


def _matches(row: Any, filters: dict[str, Any]) -> bool:
    return all(getattr(row, k, None) == v for k, v in filters.items())


def where(table: Any, **filters: Any) -> list[Any]:
    """Every row matching every keyword filter by equality (order preserved)."""
    return [r for r in table() if _matches(r, filters)]


def first(table: Any, **filters: Any) -> Optional[Any]:
    """First row matching every keyword filter by equality, or ``None``."""
    return next((r for r in table() if _matches(r, filters)), None)


def count(table: Any, **filters: Any) -> int:
    """Count of rows matching every keyword filter by equality."""
    return sum(1 for r in table() if _matches(r, filters))
