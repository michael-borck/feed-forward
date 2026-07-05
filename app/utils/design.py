"""
FeedForward design tokens — Editorial direction (chosen 2026-07-05).

Single source of truth for colour, spacing, radius, shadow, typography. The
helpers in ``app/utils/ui.py`` and the landing page in ``app.py`` consume these
constants; new routes should reference them rather than reaching for raw
Tailwind utilities so that drift doesn't return.

Direction summary (picked from four prototyped variants on ``/landing``; see
``docs/design/direction-editorial-2026-07.md``):

- "Academic press": warm paper surfaces, deep navy ink, the brand teal as the
  single accent. Serif display type (Fraunces, loaded in ``app/__init__.py``)
  for headings and the wordmark; Inter stays for body text.
- Depth comes from hairline rules and borders, never shadows.
- Labels are small-caps (uppercase + letterspacing) — see ``TEXT['label']``.
- One radius (``rounded``, 4px); pills only for status badges.
- Numeric scores are NOT shown to students by default (config option, default
  off). Progress is expressed with the bullseye glyph
  (``app/utils/ui.py::bullseye_progress``) rather than numbers.

Tokens are Tailwind class fragments so they can be slotted into f-strings
without lookups (arbitrary-value fragments like ``[#1a2e44]`` work because
Tailwind is the Play CDN):

    cls=f"bg-{COLOR['primary']} text-white {RADIUS}"
"""

# ---------------------------------------------------------------------------
# Colour — Tailwind palette names or arbitrary-value fragments (not full
# classes), so callers can embed them in `bg-{...}`, `text-{...}`,
# `border-{...}` etc.
# ---------------------------------------------------------------------------

COLOR: dict[str, str] = {
    # Primary ink / action — deep navy
    "primary": "[#1a2e44]",
    "primary_hover": "[#0f1e30]",
    "primary_subtle": "[#edeae1]",
    # Accent — the brand teal (the "Forward" half of the wordmark)
    "accent": "teal-600",
    "accent_hover": "teal-700",
    "accent_subtle": "teal-50",
    # Surfaces — warm paper, with a near-white warm card surface
    "surface": "[#fdfcf8]",
    "surface_alt": "[#faf8f2]",
    # Text
    "text_strong": "[#1a2e44]",
    "text_body": "slate-700",
    "text_muted": "slate-500",
    # Borders — hairlines do the work shadows used to do
    "border": "slate-300",
    # Semantic states
    "danger": "red-700",
    "danger_hover": "red-800",
    "warning": "amber-700",
    # Wordmark — "Feed" in ink navy, "Forward" in brand teal
    "wordmark_first": "[#1a2e44]",
    "wordmark_second": "teal-600",
    "wordmark_first_dark": "[#f5f2e9]",  # for any remaining dark surface
    "wordmark_second_dark": "teal-300",
}

# ---------------------------------------------------------------------------
# Typography — serif display over sans body. Each entry is a complete class
# string suitable for the relevant element (e.g. ``cls=TEXT['h1']``).
# ``font-serif`` resolves to Fraunces via the Tailwind config in
# ``app/__init__.py``.
# ---------------------------------------------------------------------------

TEXT: dict[str, str] = {
    # Hero — used once per landing-style page
    "hero": "font-serif text-4xl md:text-6xl font-semibold leading-[1.05]",
    # Page titles (dashboards, list pages)
    "h1": "font-serif text-2xl md:text-3xl font-semibold leading-tight",
    # Section heads
    "h2": "font-serif text-xl md:text-2xl font-semibold leading-snug",
    # Card / subsection heads
    "h3": "font-serif text-lg font-semibold leading-snug",
    # Body — stays sans (Inter)
    "body": "text-base leading-relaxed",
    "body_sm": "text-sm leading-relaxed",
    # Meta / caption
    "meta": "text-xs text-slate-500 leading-normal",
    # Small-caps label — eyebrows, table headers, statuses. The signature
    # editorial device; pair with a muted or accent text colour.
    "label": "text-xs uppercase tracking-[0.2em]",
    # Numerics — tabular figures for the rare places numbers still align
    # (instructor tables). Student-facing progress uses bullseye_progress.
    "numeric": "tabular-nums",
}

# ---------------------------------------------------------------------------
# Spacing — Tailwind number suffixes. Use as ``f"p-{PAD['md']}"`` etc.
# ---------------------------------------------------------------------------

PAD: dict[str, str] = {
    "xs": "2",  # 0.5rem
    "sm": "3",  # 0.75rem
    "md": "4",  # 1rem   — default card padding
    "lg": "6",  # 1.5rem — roomy card / hero inner
    "xl": "8",  # 2rem   — largest standard; bigger is a smell
}

GAP: dict[str, str] = {
    "xs": "2",
    "sm": "3",
    "md": "4",
    "lg": "6",
}

# Body wrappers — what page_container / dashboard_layout use.
BODY_VPAD = "py-6"
DASHBOARD_BODY_PAD = "p-4"

# ---------------------------------------------------------------------------
# Radius + shadow — editorial: one small radius, no shadows anywhere.
# ---------------------------------------------------------------------------

RADIUS = "rounded"  # 4px, single value across cards + buttons + inputs
RADIUS_PILL = "rounded-full"  # pills only (status badges)

SHADOW_REST = "shadow-none"
SHADOW_HOVER = "shadow-none"

# Hairline rules — the editorial depth cues. HAIRLINE for internal division,
# RULE_HEAVY for the chrome (header/footer/table-head) signature 2px ink rule.
HAIRLINE = f"border-{COLOR['border']}"
RULE_HEAVY = f"border-b-2 border-{COLOR['primary']}"


# ---------------------------------------------------------------------------
# Composed button classes — what ``action_button`` and the landing CTAs use.
# Editorial buttons are rectangular small-caps; three intents.
# ---------------------------------------------------------------------------

_BUTTON_INTENTS: dict[str, str] = {
    "primary": (
        f"bg-{COLOR['primary']} text-[#faf8f2] hover:bg-{COLOR['primary_hover']}"
    ),
    "secondary": (
        f"bg-transparent text-{COLOR['primary']} "
        f"border border-{COLOR['primary']} "
        f"hover:bg-{COLOR['primary']} hover:text-[#faf8f2]"
    ),
    "ghost": (f"text-{COLOR['primary']} hover:bg-{COLOR['primary_subtle']}"),
    "danger": (f"bg-{COLOR['danger']} text-white hover:bg-{COLOR['danger_hover']}"),
}

_BUTTON_SIZES: dict[str, str] = {
    "sm": "px-3 py-1.5 text-[11px]",
    "md": "px-5 py-2.5 text-xs",
    "lg": "px-7 py-3 text-sm",
}

_BUTTON_BASE = (
    "inline-flex items-center justify-center font-medium uppercase "
    f"tracking-[0.15em] {RADIUS} transition-colors"
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
