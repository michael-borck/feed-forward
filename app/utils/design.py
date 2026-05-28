"""
FeedForward design tokens — Modern Educational direction (Option B, dense).

Single source of truth for colour, spacing, radius, shadow, typography. The
helpers in ``app/utils/ui.py`` and the landing page in ``app.py`` consume these
constants; new routes should reference them rather than reaching for raw
Tailwind utilities so that drift doesn't return.

Direction summary (see ``docs/design-audit-2026-05.md`` for the audit that
produced this):

- Palette: indigo (primary) + emerald (accent), with the two-tone wordmark
  preserved as its own blue + teal — kept because Michael liked the
  wordmark and shouldn't be touched.
- Single radius (``rounded-lg``), one shadow scale.
- Typography is deliberately dense — the audit found pages overflowed even
  on desktop, so the hero, h1, and h2 sizes are one Tailwind step smaller
  than the previous values.
- Spacing scale is tight: ``2 / 3 / 4 / 6 / 8`` Tailwind units; nothing larger
  by default. ``BODY_VPAD`` of ``py-6`` replaces the ``py-16`` that was
  eating ~128px on every marketing page.

Tokens are Tailwind class fragments so they can be slotted into f-strings
without lookups:

    cls=f"bg-{COLOR['primary']} text-white {RADIUS} {SHADOW_REST}"
"""

# ---------------------------------------------------------------------------
# Colour — Tailwind palette names (not full classes), so callers can embed
# them in `bg-{...}`, `text-{...}`, `border-{...}` etc.
# ---------------------------------------------------------------------------

COLOR: dict[str, str] = {
    # Primary action / link / focus
    "primary":          "indigo-600",
    "primary_hover":    "indigo-700",
    "primary_subtle":   "indigo-50",
    # Accent — second tone (success, "ready", emerald track in two-tone use)
    "accent":           "emerald-600",
    "accent_hover":     "emerald-700",
    "accent_subtle":    "emerald-50",
    # Surfaces
    "surface":          "white",
    "surface_alt":      "slate-50",
    # Text
    "text_strong":      "slate-900",
    "text_body":        "slate-700",
    "text_muted":       "slate-500",
    # Borders
    "border":           "slate-200",
    # Semantic states
    "danger":           "red-600",
    "danger_hover":     "red-700",
    "warning":          "amber-500",
    # Wordmark — preserved as the user-liked brand mark; intentionally
    # different from primary/accent so the wordmark keeps its identity.
    "wordmark_first":        "blue-600",
    "wordmark_second":       "teal-500",
    "wordmark_first_dark":   "blue-300",   # used on the dark slate header
    "wordmark_second_dark":  "teal-400",
}

# ---------------------------------------------------------------------------
# Typography — dense scale. Each entry is a complete class string suitable
# for the relevant element (e.g. ``cls=TEXT['h1']`` on an ``H1``).
# Was: hero text-4xl md:text-6xl; h1 text-3xl md:text-4xl ... (oversized).
# Now: one Tailwind step down across the board.
# ---------------------------------------------------------------------------

TEXT: dict[str, str] = {
    # Hero — used once per landing-style page
    "hero":     "text-3xl md:text-5xl font-bold leading-tight",
    # Page titles (dashboards, list pages)
    "h1":       "text-2xl md:text-3xl font-semibold leading-tight",
    # Section heads
    "h2":       "text-xl font-semibold leading-snug",
    # Card / subsection heads
    "h3":       "text-base font-semibold leading-snug",
    # Body
    "body":     "text-base leading-normal",
    "body_sm":  "text-sm leading-normal",
    # Meta / caption
    "meta":     "text-xs text-slate-500 leading-normal",
    # Numerics — tabular feel for scores, IDs, counts (precision cue without
    # changing prose font).
    "numeric":  "font-mono tabular-nums",
}

# ---------------------------------------------------------------------------
# Spacing — Tailwind number suffixes. Use as ``f"p-{PAD['md']}"`` etc.
# Five-step scale, defaults conservative.
# ---------------------------------------------------------------------------

PAD: dict[str, str] = {
    "xs": "2",   # 0.5rem
    "sm": "3",   # 0.75rem
    "md": "4",   # 1rem   — default card padding
    "lg": "6",   # 1.5rem — roomy card / hero inner
    "xl": "8",   # 2rem   — largest standard; bigger is a smell
}

GAP: dict[str, str] = {
    "xs": "2",
    "sm": "3",
    "md": "4",
    "lg": "6",
}

# Body wrappers — what page_container / dashboard_layout use. These are
# full class strings (not just suffixes) because callers slot them into
# ``cls=`` directly.
BODY_VPAD = "py-6"           # was py-16  — single biggest density win
DASHBOARD_BODY_PAD = "p-4"   # was p-6

# ---------------------------------------------------------------------------
# Radius + shadow
# ---------------------------------------------------------------------------

RADIUS = "rounded-lg"        # single value across cards + buttons + inputs
RADIUS_PILL = "rounded-full" # pills only (status badges)

SHADOW_REST = "shadow-sm"
SHADOW_HOVER = "shadow"      # subtle lift; intentionally not shadow-lg


# ---------------------------------------------------------------------------
# Composed button classes — what ``action_button`` and the landing CTAs use.
# Three intents; everything else converges to one of these.
# ---------------------------------------------------------------------------

_BUTTON_INTENTS: dict[str, str] = {
    "primary": (
        f"bg-{COLOR['primary']} text-white "
        f"hover:bg-{COLOR['primary_hover']} {SHADOW_REST} hover:{SHADOW_HOVER}"
    ),
    "secondary": (
        f"bg-white text-{COLOR['primary']} "
        f"border border-{COLOR['primary']} hover:bg-{COLOR['primary_subtle']}"
    ),
    "ghost": (
        f"text-{COLOR['primary']} hover:bg-{COLOR['primary_subtle']}"
    ),
    "danger": (
        f"bg-{COLOR['danger']} text-white "
        f"hover:bg-{COLOR['danger_hover']} {SHADOW_REST} hover:{SHADOW_HOVER}"
    ),
}

_BUTTON_SIZES: dict[str, str] = {
    "sm": "px-3 py-1.5 text-sm",
    "md": "px-4 py-2",
    "lg": "px-5 py-2.5 text-lg",
}

_BUTTON_BASE = (
    f"inline-flex items-center justify-center font-medium {RADIUS} transition-colors"
)


def button_classes(intent: str = "primary", size: str = "md") -> str:
    """Class string for a button.

    ``intent`` is one of ``primary`` / ``secondary`` / ``ghost`` / ``danger``;
    ``size`` is ``sm`` / ``md`` / ``lg``. Unknown values fall back to the
    defaults so the page still renders rather than refusing.
    """
    return (
        f"{_BUTTON_BASE} "
        f"{_BUTTON_SIZES.get(size, _BUTTON_SIZES['md'])} "
        f"{_BUTTON_INTENTS.get(intent, _BUTTON_INTENTS['primary'])}"
    )
