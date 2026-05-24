# Signal Integration Plan — FeedForward × lens

Concrete roadmap for [ADR 012](docs/adr/012-signal-based-assessment-via-lens.md):
make FeedForward consume the **lens analyser family** for deterministic *signals*,
map those signals to rubric categories, and let the instructor review/adjust before
release. Signals are **evidence alongside** the LLM, not a replacement.

> Decisions already locked (see ADR 012): consume lens (don't build our own
> analysis); call analysers over **HTTP** with `auto-analyser` as the router; store
> signal scores as a **synthetic model run** so they flow through the existing
> aggregation untouched; reuse the existing instructor-approval fields.

---

## Architecture at a glance

```
Student submission
   │  (existing) extract_file_content → text
   ▼
FeedbackGenerator.generate_feedback_for_draft(draft_id)
   ├── LLM runs ─────────────► CategoryScore rows  (existing)
   └── SignalService.extract(draft)                          ← NEW
          │  HTTP POST /analyse → auto-analyser → document/code/… analyser
          │  (explicit: cite-sight, conversation-analyser)
          ▼
       signals table  (raw, queryable, survives content deletion)
          ▼
       SignalScorer.score(draft)                              ← NEW
          │  apply signal_rules (signal → 0–100 + confidence)
          ▼
       synthetic ModelRun  ──► CategoryScore rows
   ▼
_aggregate_feedback  (UNCHANGED — blends LLM + signal CategoryScores per category)
   ▼
AggregatedFeedback (status: pending_review)
   ▼
Instructor review UI: signals + LLM + estimate → adjust → approved → released   ← NEW
   ▼
Student sees released feedback   (existing visualization)
```

**The seam was NOT already there** (2026-05-23 architecture review): the handler
`preprocess()` is dead code and the generator hardcodes "run LLM" as the only evidence
producer. The locked design below introduces the seam properly.

## Architecture decisions (2026-05-23 review)

Settled in a grilling session on the architecture review (recorded in ADR 012 §6):

1. **Handler = slim declaration seam (A3).** `AssessmentHandler` rebuilt from in-process
   constants (no DB at import); declares `validate_submission`, `get_signal_sources()`,
   `get_prompt_template`, `format_feedback`, and a thin `shape_for_prompt(text)` (code →
   line numbers, math → LaTeX-readable, essay → identity). Inline metric computation
   deleted (lens computes metrics; extraction stays in `file_handlers.py`). The
   `assessment_types` table becomes display metadata. The generator resolves the handler
   from `assignment.assessment_type_id` (default `essay`).

2. **Evidence-source seam (B + C are one seam).** `EvidenceSource.produce(draft,
   assignment, settings)` with two adapters: `LLMEvidenceSource`, `SignalEvidenceSource`.
   The generator holds an **injected** `sources` list (default `[LLM]`; signal added when
   enabled), gathers them, aggregates the union. Persistence is **thin**: each source
   writes its own `ModelRun` + `CategoryScore`s (as `_run_single_model` does today) but
   takes an injected `model_provider` (litellm) / `signal_client` (lens HTTP). Pure-result
   value objects are a later deepening.

3. **Aggregation refinements (not a zero-change).** The signal run must join the
   `successful_runs` set that `_aggregate_feedback` iterates (feedback_generator.py:541),
   and that method must write `status="pending_review"` (line 615), not `"approved"`, to
   enable the §5 instructor review.

4. **Testing.** No data-access port is injected: tests point `db` at a throwaway file via
   the `DATABASE_PATH` env var in `conftest.py` (db is built from it at import,
   user.py:13). Only the network ports (`model_provider`, `signal_client`) are faked.
   Order: introduce the seam, then tests (the thin refactor is mechanical; mock-feedback
   path is the interim smoke check).

5. **Row-lookup slice (D).** A small `app/utils/db_query.py` (`by_id`, `where`, `first`,
   `next_id`) that retires the racy `_get_next_id`; used for the new `signals` /
   `signal_rules` reads and the generator's own scans we're already editing. The ~100
   route scans are left for later.

**Revised ordering:** settle the handler seam (A3) + stand up the evidence-source seam +
the `db_query` slice **before** S2 scoring. S0/S1 (sidecar + read-only signals) can run in
parallel — they don't depend on the generator refactor.

### Verified 2026-05-24 (lens runs)

`document-analyser` 0.3.1 runs from its own `.venv`:
`/Users/michael/Projects/lens/document-analyser/.venv/bin/document-analyser serve --port 8000`.

- ✅ `/health`, `/manifest`, and **`/text`** (POST `{"text": ...}`) work. `/text` returns
  the full essay signal set — readability (`flesch_score`, FK grade), writing quality
  (passive %, sentence variety, academic tone, transitions, hedging), word analysis
  (`vocabulary_richness`, n-grams), and NER — in ~0.5s.
- ✅ **Integration uses `/text` with already-extracted text**, NOT the file-upload
  `/analyse`. `/analyse` 500s in 0.3.1 (references `flesch_reading_ease` / `gunning_fog` /
  `smog_index` / `automated_readability_index` — none exist on `DocumentAnalysis`; it has
  `flesch_score` + `flesch_kincaid_grade`). `/text` sidesteps this and fits FeedForward,
  which already extracts text in `file_handlers.py`.
- ⚠ The **`/semantic/*` tier (sentiment, embeddings) crashes the server on macOS**
  (SIGBUS, `loky` semaphore leak — the documented torch/sentence-transformers
  brittleness). **Sentiment/coherence signals are deferred** until that lens-side
  instability is fixed; S1 uses `/text` signals only.

Two optional lens-side fixes (separate repo, Michael owns it): one-spot `/analyse`
attribute fix; investigate the macOS semantic-tier crash. Neither blocks S1.

---

## What lens gives us (signals → candidate rubric dimensions)

| Signal source | Example signals | Maps naturally to |
|---|---|---|
| document-analyser (core) | flesch_score, flesch_kincaid_grade, paragraph_count, avg_words_per_sentence, sentence_variety, vocabulary_richness | Clarity, Structure/Organisation, Vocabulary |
| document-analyser `[nlp]` | sentiment compound, granular sentiment, NER, `overall_coherence_score`, sentence-dislocation | Coherence, Tone, Topic focus — ⚠ semantic/sentiment tier **crashes on macOS** (deferred); NER works via `/text` |
| document-analyser (WritingQuality) | passive_voice_percentage, transition_words, hedging_language, academic_tone | Academic writing, Style |
| cite-sight | integrity_score, missing_in_text, orphaned_in_text, broken_urls, unresolved_dois | Referencing / Academic integrity |
| code-analyser | cyclomatic complexity, lint violations, docstring/type coverage | Code quality, Documentation, Style |
| conversation-analyser | critical-thinking score, engagement band, pushback ratio | Process / Critical thinking |

> Note: not every rubric category has a signal. Categories like "depth of argument"
> stay LLM-only. That is by design.

---

## Data model changes (additive, backward-compatible)

1. **Seed model** — one `ai_models` row: `Signal Engine (lens)`, `provider="signal"`,
   `owner_type="system"`. (No schema change; uses existing table.)

2. **`signals`** (new) — queryable raw signals; survives content deletion.
   ```
   id, draft_id, source (e.g. "document-analyser"),
   name (e.g. "flesch_score"), value (float), raw (str/JSON, nullable),
   created_at
   ```

3. **`signal_rules`** (new) — signal → category transform.
   ```
   id, rubric_category_id, signal_source, signal_name,
   transform (JSON: {type: "band"|"linear", params: {...}}),
   weight (float), enabled (bool)
   ```
   Transforms: `band` = piecewise thresholds → score; `linear` = clamp+scale.
   Seeded with per-assessment-type defaults; instructor-overridable per assignment.

(`ModelRun.raw_response` already stores the full analyser JSON for the signal run; no
change needed there.)

---

## New code

| Module | Responsibility |
|---|---|
| `app/utils/analyser_client.py` | HTTP client: base URLs from config/env, `health()`, `analyse(file/text, source)`, timeout + graceful degradation (analyser down → return empty, log, continue) |
| `app/services/signal_service.py` | Orchestrate extraction per assessment type → write `signals` rows. Handler declares its sources via new `AssessmentHandler.get_signal_sources()` |
| `app/services/signal_scorer.py` | Load `signal_rules`, apply transforms → `CategoryScore` under the synthetic `ModelRun` |
| (edit) `app/services/feedback_generator.py` | Kick off `SignalService` + `SignalScorer` alongside LLM runs |
| (new UI) instructor review route | Render signals + LLM + estimate; edit + approve via existing `AggregatedFeedback` status fields |

---

## Phases (each independently shippable; tracer-bullet first)

### S0 — Infra spike *(small)*
- Stand up `document-analyser serve` on `:8000` with the `[nlp]` extra; confirm
  `auto-analyser` routes a `.pdf`/`.docx` to it.
- Add `analyser_client.py` with a health-check; smoke-test from a throwaway script.
- **Exit:** a script posts a sample essay and prints back signals JSON.

### S1 — Tracer bullet: essay + document-analyser, read-only
- For an essay draft, call document-analyser, persist to `signals`.
- Show the raw signals on the **instructor** submission-review page (no scoring yet).
- **Exit:** instructor can see real readability/structure/sentiment signals for a real
  submission, end to end. Validates the whole round-trip with one analyser, one type.
- **✅ Landed 2026-05-24:** `app/models/signals.py`, `app/utils/analyser_client.py`
  (POST `/text`, graceful degradation), `app/services/signal_service.py` (extract +
  flatten + persist, idempotent), background extraction fired at submission
  (`student/submissions.py`), and a read-only panel at
  `/instructor/submissions/{id}/signals` linked from the submissions list. Round-trip
  smoke verified (14 signals; graceful when analyser down). Caveats: signals render on a
  dedicated route, not the detail view (which has pre-existing stale `ModelRun` field
  refs); the panel was compile-checked but not yet rendered in a live browser (the app
  needs a `.env` to import — `app/utils/email.py` reads it at import time); sentiment
  deferred (macOS semantic crash).

### S2 — Mapping + estimated score
- Add `signal_rules` + essay defaults; implement `signal_scorer.py` + synthetic
  `ModelRun`; emit `CategoryScore` rows.
- Show estimated per-category signal scores next to LLM scores; confirm aggregation
  blends them.
- **Exit:** a draft shows LLM score, signal score, and blended aggregate per category.
- **✅ Landed 2026-05-24:** `signal_rules` model + `signal_scorer` (band/linear
  transforms, weighted per-category score + confidence); auto-match signals→categories
  by name (`suggest_rules_for_category`); read-only estimates on the instructor panel;
  synthetic Signal Engine run (`signal_evidence.produce_signal_run`, sentinel
  `model_id=-1`) blended into live aggregation in both paths (best-effort; auto-release
  kept). 32 tests green. **Deferred:** A3 handler / EvidenceSource / `db_query` deepening
  (task 13); `pending_review` + instructor approval UI (S3); confirm/override rules UI;
  sentiment signals (await the lens semantic-tier fix release).

### S3 — Instructor review/adjust (old Phase 4.1)
- Wire `AggregatedFeedback.status` (pending_review → approved → released) and
  `edited_by_instructor` into a review UI.
- Instructor adjusts the mark with signals visible, then releases to the student.
- **Exit:** nothing reaches the student until an instructor approves.
- **✅ Landed 2026-05-24:** feedback now generated as `pending_review`;
  `app/services/feedback_review.py` (release filter + `apply_review`); rebuilt
  per-category instructor review UI (`/review` GET + `/review/save` POST) showing
  signals + estimate, editable score/feedback, Approve&release / Save-draft;
  student view gated to released feedback with an "awaiting review" state, and
  `render_enhanced_feedback` rewritten for the real per-category schema. Also fixed
  the root cause that broke **all** async POST handlers (the auth decorators were
  sync wrappers — now async-aware in `app/__init__.py`), which also repairs student
  submit. Verified end-to-end in the running app (pending → approve → released).
  Note: same-path GET+POST doesn't dispatch by method in FastHTML here, so POST
  handlers need a distinct path (or to be named `post`).

### S4 — Generalise across types
- code → `code-analyser` (`:8004`); citations → `cite-sight` (HTTP); route everything
  through `auto-analyser`; per-type rule defaults.
- **Exit:** code and essay assignments both produce signals via the same pipeline.

### S5 — Hardening
- **Tests first for all new code** (the repo currently has no active suite — start the
  suite here).
- Fallback behaviour when an analyser is offline; pin lens versions.
- Privacy lifecycle: confirm `signals` are retained while draft `content` is deleted.
- Remove the hardcoded auth bypass in `app/routes/auth.py`.
- Instructor docs for editing `signal_rules`.

---

## Open questions for calibration (defer past S1)
- Default signal→score bands per assessment type (needs a few real submissions to tune).
- How to weight the signal run vs LLM runs in aggregation (start: equal; expose later).
- Whether to surface signal *contributions* to students or only the blended score.

## Risks / watch-items (from ADR 012)
- lens maturity: use HTTP/library, **not** document-analyser's CLI (known bug); pin versions.
- ML deps stay in the sidecar, never in FeedForward's process.
- Missing signals → add them in the relevant **lens** analyser, not in FeedForward.
