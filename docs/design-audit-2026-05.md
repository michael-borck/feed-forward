# FeedForward UI design audit — 2026-05-29

A grounded look at the styling layer as it stands today, with three directional
options for a refresh. The audit is deliberately concrete: every "current state"
observation below is backed by a number from the codebase, not a vibe.

**Audience for the platform:** instructors and students at Curtin University.
Instructors design rubrics and review feedback; students submit drafts and
receive iterative feedback. The UI carries emotionally-loaded content (grades,
critique), and the platform handles their academic work — it needs to feel
both trustworthy and approachable.

**Constraints to honour:** server-rendered FastHTML + Tailwind via CDN (no JS
build step, no PostCSS, no custom Tailwind config). Whatever we choose has to
be expressible with Tailwind utility classes a server template emits.

---

## What the brand actually is (in code, today)

There is no design system file, but there is a brand fingerprint, repeated in
`app/utils/ui.py` in `page_header` / `page_footer` / `dashboard_header`:

- The wordmark is two-tone: **"Feed" in blue + "Forward" in teal**, using
  `text-blue-300` + `text-teal-400` on dark backgrounds and `text-blue-600` +
  `text-teal-500` on light. This is the bit you've said you like.
- The marketing header behind it is a **dark slate gradient**:
  `bg-gradient-to-r from-slate-700 to-slate-800`.
- The dashboards drop the gradient and use a white-on-gray-100 surface
  layout (chrome on `bg-gray-50`, body on `bg-gray-100`, cards on `bg-white`).

That's the brand. The problem is that almost nothing else in the codebase
references it — the two-tone identity is locked to the wordmark and the rest
of the app drifts.

---

## Current state — 10 concrete observations

Numbers from `grep` across `app/**.py`:

1. **43 distinct "primary button" class strings.** Every place an instructor
   or student clicks a primary action, someone wrote a fresh `bg-{color}-600
   text-white px-{n} py-{m} rounded-{r} hover:bg-{color}-700 ...` rather than
   using `action_button`. Same conceptual element, 43 implementations.

2. **8+ colour hues in active use** — indigo, emerald, teal, blue, purple,
   pink, orange, yellow, green, plus full gray scales. The brand is two-tone;
   the code is everything-tone. The accent colour for a given concept (success?
   primary action? destructive?) isn't anchored — a "view" link is sometimes
   indigo, sometimes emerald, sometimes teal.

3. **Brand mismatch inside the app itself.** The wordmark uses `blue` +
   `teal`; the dashboards predominantly use `indigo` (a different blue, sits
   purple-side of true blue) and `emerald` (a different green than teal).
   Three "blue-greens" are in active rotation: blue, indigo, teal — and three
   "greens": emerald, teal, green. The brand says one thing; the dashboards
   say another.

4. **4 corner radii in active use:** `rounded-md` (101×), `rounded-lg` (245×),
   `rounded-xl` (131×), `rounded-full` (24×). No discernible hierarchy —
   buttons can be md, lg, or xl in different files. The same component (a
   card) is `rounded-lg` in one place and `rounded-xl` next door.

5. **7+ padding values with no system.** `p-3`, `p-4`, `p-5`, `p-6`, `p-8`,
   plus a sprawl of mixed `px-{n} py-{m}` combinations. `p-4` (132×) and
   `p-6` (55×) dominate but inconsistently — the same card type uses both
   in different routes.

6. **5 shadow levels active** (`shadow-sm`, `shadow`, `shadow-md`,
   `shadow-lg`, `shadow-xl`). `shadow-md` dominates (148×) but a card can be
   any of the five depending on the file. Shadows aren't doing semantic
   work — they're decorative.

7. **Heading hierarchy is unclear.** H1 elements use `text-2xl` (41×),
   `text-3xl` (11×), and `text-4xl` (4×) interchangeably. There's no rule
   like "page H1 = 3xl, section H2 = 2xl, card H3 = xl." The same page title
   sized differently page-to-page.

8. **Typography is system defaults only.** Body inherits `font-sans` (system
   sans-serif); headings inherit the same family. Nothing is intentionally
   chosen. Numbers and code share the same font as prose, which makes the
   scoring sections (lots of `87.5/100` text) feel less precise than they
   should.

9. **Gradients used as ornament.** The page header has a slate gradient; some
   cards have indigo gradients; the landing page mixes both. Without a
   gradient policy they read as accidental flourish, not design choice.

10. **Footer copyright is hardcoded** (`"2025"` in `page_footer`) with a
    `# In a real app, you'd use datetime.now().year` comment. Symptom of
    "this layer never got the same care as the services layer." Easy fix,
    but worth naming as part of the pattern.

**Deletion test for `action_button` (the helper that's supposed to centralise
primary buttons):** if I deleted it, would complexity reappear in many call
sites? Yes — 43 of them. So the helper has every right to exist. But callers
mostly aren't using it, which is the actionable bit.

---

## Three directional options

Each option is a complete design vocabulary. Pick one; the next slice writes
`app/utils/design.py` with these tokens and refactors `ui.py` to consume
them. Then we refresh pages incrementally against the chosen direction.

### Option A — "Academic restrained"

Feels like a university printed handbook brought online: serious, dense,
quiet.

| Token | Value |
|---|---|
| Surface | Warm off-white `#fafaf6`, body `#f5f4ee` |
| Primary | Deep navy `#1e3a5f` (replaces both blue and indigo) |
| Accent | Brand teal `#0d9488` (preserves the "Forward" half of the wordmark) |
| Neutrals | Slate scale, headings `#0f172a`, body `#334155`, muted `#64748b` |
| Type — heading | Serif: system `Georgia` / `Source Serif` |
| Type — body | Sans: system stack |
| Type — numeric | Tabular sans, slight tracking-tight |
| Scale | H1 `text-3xl`, H2 `text-2xl`, H3 `text-xl`; body `text-base`; meta `text-sm` |
| Radius | One value: `rounded` (4px) |
| Shadow | None — use 1px slate-200 borders instead |
| Spacing | 4-step scale: `2`, `4`, `6`, `10` |

**Wordmark mapping:** "Feed" stays a darker navy (`#1e3a5f`), "Forward" stays
the brand teal — the two-tone identity continues but now matches the rest of
the app instead of fighting it.

**Strengths:** institutional credibility; dense by default (good for
rubric/category-heavy pages); the serif headings give student feedback a more
considered tone.

**Risks:** can feel stuffy or dated if executed conservatively; the lack of
shadows means depth comes from borders and surface contrast, which is
unforgiving when poorly tuned.

---

### Option B — "Modern educational" (recommended)

Feels like modern edtech (Notion-shaped, Linear-shaped): friendly, calm,
generous whitespace, but information-dense where it counts.

| Token | Value |
|---|---|
| Surface | Body `#f8fafc` (slate-50), cards `#ffffff` |
| Primary | Indigo `#4f46e5` (already dominant; we unify around it) |
| Accent | Emerald `#10b981` (replaces teal + green; carries the "Forward" wordmark half) |
| Neutrals | Slate scale, headings `slate-900`, body `slate-700`, muted `slate-500` |
| Type — heading | Sans (system) — `font-semibold` |
| Type — body | Sans (system), leading-relaxed |
| Type — numeric | `font-mono` for scores + IDs (precision cue without changing prose) |
| Scale | H1 `text-3xl`, H2 `text-2xl`, H3 `text-lg`; body `text-base`; meta `text-sm` |
| Radius | One value: `rounded-lg` (8px) for cards + buttons; pills stay `rounded-full` |
| Shadow | One scale: `shadow-sm` (cards), `shadow-md` (hover/elevation) |
| Spacing | 5-step scale: `2`, `4`, `6`, `8`, `12` |

**Wordmark mapping:** "Feed" becomes indigo, "Forward" becomes emerald. The
brand DNA is preserved but unified with the rest of the app's actual usage
(indigo + emerald are already the most common dashboard hues — we just stop
fighting them with blue/teal). The two-tone wordmark becomes the visible
expression of a colour system that runs through every page.

**Strengths:** smallest gap from current code (most pages already lean indigo
+ emerald); modern feel matches student expectations; preserves what you like
about the two-tone identity rather than replacing it.

**Risks:** can feel generic if executed without enough character — the
restraint is its design, not a default; need to invest in a couple of
distinctive touches (e.g., the numeric-mono trick) so it doesn't blur into
every other edtech tool.

---

### Option C — "Minimal scientific"

Feels like a research tool (Stripe-shaped, Linear-cold): precise, tight,
restrained colour use.

| Token | Value |
|---|---|
| Surface | Pure white `#ffffff` on `#fafafa`; no card distinction |
| Primary | One ink: `slate-900` |
| Accent | One accent only, used sparingly: brand indigo `#4f46e5` |
| Neutrals | Cool grays only; no warm tones |
| Type — heading | Sans (Inter if available, system fallback), `font-medium` not bold |
| Type — body | Sans, `text-sm` default |
| Type — numeric | Mono throughout for any number |
| Scale | H1 `text-2xl`, H2 `text-lg`, H3 `text-base`; body `text-sm`; meta `text-xs` |
| Radius | `rounded-sm` (2px) everywhere |
| Shadow | None — 1px borders only |
| Spacing | Tight: `1`, `2`, `4`, `6` |

**Wordmark mapping:** the two-tone wordmark becomes the ONLY place colour
appears in the chrome. Everywhere else is monochrome. The brand becomes a
deliberate splash rather than a system.

**Strengths:** information-dense (good for the rubric-heavy instructor pages);
feels precise and unfrivolous; biggest visual departure from the current state.

**Risks:** can feel cold or unwelcoming on the student side, where feedback
delivery already carries emotional weight; the lack of warmth and shadow
makes typography mistakes very visible — needs careful execution.

---

## Comparison at a glance

| | A: Academic | B: Modern Ed | C: Minimal Sci |
|---|---|---|---|
| Mood | Institutional, serious | Friendly, calm | Precise, tool-like |
| Brand colours used | Navy + teal (everywhere) | Indigo + emerald (everywhere) | Indigo only (sparingly) |
| Heading typeface | Serif | Sans | Sans (Inter) |
| Body density | High | Medium | High |
| Radius | 4px (single) | 8px (single) | 2px (single) |
| Shadows | None | Soft, one scale | None |
| Gap from today | Large | Smallest | Largest |
| Student warmth | Medium | High | Low |
| Instructor density | High | Medium | High |

---

## Recommendation

**Option B — Modern educational.** Three reasons:

1. It preserves the two-tone wordmark you said you like, and extends it into a
   colour system the whole app uses — the brand becomes consistent instead of
   isolated.
2. It has the smallest gap from the current code. Most dashboards already use
   indigo + emerald — option B unifies what's already happening rather than
   imposing a new vocabulary.
3. The audience tilt matters. Students receiving feedback are emotionally
   exposed; warmth and calm pay off there. Instructors want density, but
   `font-mono` numerics + medium spacing handles that without going cold.

A + C are both defensible — A if you want the platform to read as more
institutionally serious than modern; C if you want it to read as a
research/data tool first and an educational platform second.

---

## What the next slice does (once you pick)

1. **`app/utils/design.py`** — token constants:
   ```python
   COLOR = {"primary": "indigo-600", "primary_hover": "indigo-700", ...}
   RADIUS = "rounded-lg"
   PAD = {"sm": "p-3", "md": "p-6", "lg": "p-8"}
   SHADOW = {"rest": "shadow-sm", "hover": "shadow-md"}
   TEXT = {"h1": "text-3xl font-semibold text-slate-900", ...}
   ```
2. **Refactor `app/utils/ui.py`** — the 16 helpers consume the tokens. Same
   call sites, new look.
3. **Refresh one pattern page end-to-end** — the instructor dashboard, since
   it's the most-visited and shows off cards + tables + actions. It becomes
   the visual template for the rest of the app to inherit.
4. **Audit the 43 button drift sites** — most should convert to
   `action_button` with one of three intents (primary / secondary /
   destructive). What doesn't convert tells us where the helper has gaps.

Out of scope for this audit (would be later slices): refreshing every route
page; the marketing/landing page; the auth pages.

Pick a direction and the next slice executes.
