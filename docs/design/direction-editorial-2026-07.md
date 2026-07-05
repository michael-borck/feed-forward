# Design direction: Editorial ("academic press") — decided 2026-07-05

## The question and how it was answered

The 2026-05 refresh (Option B "Modern Educational", indigo + emerald) never
achieved full adoption — three palettes kept competing (design.py tokens,
app.py `BRAND_COLORS`, and hardcoded blue/teal across `ui.py` and the
dashboards). A hard refresh was prototyped as four radically different
variants rendered live on `/landing?variant=`, each with an "inside the app"
specimen strip built from identical mock data:

- **Editorial** — academic press: paper, serif display, navy + teal, hairlines
- **Precision** — research instrument: monochrome + one accent, mono numerics
- **Studio** — bold product: dark hero, indigo→emerald gradient, glass panels
- **Warm** — friendly coach: cream, rounded, pastel chips, coaching copy

**Michael chose Editorial.** The prototype (`app/prototype_ui.py` + hooks in
`app.py`) has been deleted; this document and `app/utils/design.py` are the
durable record.

## The vocabulary

| Token | Value |
|---|---|
| Surface | Paper `#faf8f2` (page), warm near-white `#fdfcf8` (cards) |
| Ink / primary | Navy `#1a2e44` |
| Accent | Brand teal `teal-600` (`#0d9488`) — the "Forward" wordmark half |
| Text | Ink for headings, `slate-700` body, `slate-500` muted |
| Display type | Fraunces (serif), loaded in `app/__init__.py`; `font-serif` |
| Body type | Inter (unchanged) |
| Labels | Small-caps: `text-xs uppercase tracking-[0.2em]` (`TEXT['label']`) |
| Radius | One value: `rounded` (4px); pills only for status badges |
| Depth | Hairline `slate-300` borders and a 2px ink rule (`RULE_HEAVY`); **no shadows** |
| Buttons | Rectangular, uppercase letterspaced; navy primary, outlined secondary |
| Wordmark | Serif two-tone: "Feed" navy + "Forward" teal |

## Scores are off by default — the dart and the board

FeedForward does **not** show numeric scores to students by default: score
display is a configuration option, default off (still work in progress).
Student-facing progress uses the **bullseye glyph** instead — a dartboard
whose dart lands closer to the centre as drafts improve. Implemented as
`app/utils/ui.py::bullseye_progress(closeness)`; how feedback maps to
`closeness` is still being designed, so treat it as a qualitative cue.

Design consequence: feedback views must not be built around a big numeric
hero. The score-centric layouts in `app/utils/feedback_formatter.py` predate
this decision.

## Applied in this slice

- `app/utils/design.py` — rewritten to the vocabulary above (same token keys)
- `app/__init__.py` — Fraunces loaded, `font-serif` configured, favicon renavied
- `app/utils/ui.py` — all shared chrome + components restyled; `brand_wordmark`
  and `bullseye_progress` added
- `app.py` — Editorial landing (asymmetric hero + ruled contents list);
  legacy `BRAND_COLORS`/`TYPOGRAPHY`/`BUTTON_STYLES` re-pointed at the tokens

## Follow-ups

1. `app/utils/feedback_formatter.py` — full refresh: score-centric emerald/
   green/yellow layouts → editorial + bullseye, honouring scores-off default
2. Auth pages (`app/routes/auth.py`) — indigo forms → tokens
3. The ~43 hand-rolled button class strings across routes → `button_classes`
4. Legal/error prose pages in `app.py` — gradients and raw grays → tokens
5. Delete dead theme systems: `app_themed.py`, `app/utils/theme.py`,
   `app/utils/color_scheme.py`, `app/utils/theme_example.py`
