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
- ✅ **`/semantic/sentiment` macOS crash FIXED** (lens-side, 2026-05-24: mmap'd
  safetensors weights cloned onto the heap in `GranularSentimentAnalyzer.__init__`;
  see document-analyser `INTEGRATION-NOTES.md`). Re-verified live 2026-06-12:
  sentiment request returns sentence/paragraph/document-level results and the
  server stays up; FeedForward end-to-end extraction stores 18 signals including
  `sentiment_{positive,negative,neutral,compound}`, and the "Tone" auto-match
  consumes them.

One optional lens-side fix remains (separate repo, Michael owns it): the one-spot
`/analyse` attribute fix. It doesn't block anything — integration uses `/text`.

---

## What lens gives us (signals → candidate rubric dimensions)

| Signal source | Example signals | Maps naturally to |
|---|---|---|
| document-analyser (core) | flesch_score, flesch_kincaid_grade, paragraph_count, avg_words_per_sentence, sentence_variety, vocabulary_richness | Clarity, Structure/Organisation, Vocabulary |
| document-analyser `[nlp]` | sentiment compound, granular sentiment, NER, `overall_coherence_score`, sentence-dislocation | Coherence, Tone, Topic focus — sentiment live via `/semantic/sentiment` (macOS crash fixed 2026-05-24); NER works via `/text` |
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
  kept). 32 tests green. **Deferred:** task 13 architectural deepening since
  landed in three phases (D `db_query` helper: `app/utils/db_query.py` +
  ~14 call sites refactored; B `EvidenceSource` seam: `app/services/evidence.py`
  with `LLMEvidenceSource` + `SignalEvidenceSource`, orchestration iterates
  sources uniformly with explicit "≥1 LLM run" policy; A3 slim handler:
  `AssessmentHandler` collapsed from 4-abstract-method ABC + 1059-LOC
  unused concretes to a declaration dataclass with a single `evidence_sources`
  factory, 4 handlers reduced to slim instances, generator delegates source
  construction to the handler);
  `pending_review` + instructor approval UI (S3, since landed);
  confirm/override rules UI (since landed: `signal_rules_service` +
  `/instructor/assignments/{id}/signal-rules`); sentiment signals (since landed —
  document-analyser 0.5.1 sentiment fix + FeedForward extraction & "Tone" auto-match).

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
- **✅ code half landed 2026-06-12:** `analyser_client.analyse_code` (multipart to
  `:8004`, `CODE_ANALYSER_URL` override); `signal_service` routes by assessment type
  (`registry.type_code_for_assignment`, used by the generator too — it previously
  hardcoded `DEFAULT_HANDLER`); code response flattened to 18 signals (incl.
  `syntax_valid`/`has_main_guard` as 0/1); filename for language detection from
  `submission_files.original_filename`, content-sniffed fallback for text-only
  submissions; auto-match suggestions are now **per assessment type** (a code
  "Style" category maps to lint warnings, not passive voice) and
  `signal_rules_service` persists the right `signal_source`; code extensions +
  `.md` now extract as plain text in `file_handlers` (previously rejected, so code
  uploads couldn't submit at all). 146 tests green (19 new in
  `tests/test_code_signals.py`); verified live end-to-end against code-analyser
  0.6.0. **Remaining for S4:** cite-sight, auto-analyser routing.
- **✅ cite-sight half landed 2026-06-12:** `analyser_client.analyse_citations`
  (multipart to `:3001` `/analyse`, `CITE_SIGHT_URL`/`CITE_SIGHT_TIMEOUT`
  overrides; `CITE_SIGHT_VERIFY=false` disables the Crossref/OpenAlex + URL
  network tier, local cross-referencing always on). `signal_service` refactored
  to **multiple sources per assessment type** (essay → document-analyser +
  cite-sight), each idempotent and independently degrading — a re-run backfills
  a source that was down without duplicating the others. Citation flattening
  guards verification-dependent signals (a `format_only` run emits no
  verified-counts, so "verification off" can't read as "all citations bogus").
  Referencing/citation categories auto-match to `citation_integrity_pct`,
  orphaned-reference and format-issue bands (suggestion tuples can now carry a
  per-signal source). Verified live: fabricated reference → not_found, uncited
  bibliography entry → orphan, Referencing estimate 48.3/100. 11 new tests.
- **⊘ auto-analyser routing — deliberately NOT adopted (decided 2026-06-13).**
  The plan originally said "route everything through `auto-analyser`". On
  review that adds cost without benefit *for FeedForward's architecture*:
  - auto-analyser's value is **format auto-detection** — routing an unknown
    file to the right analyser. FeedForward always knows the assessment type
    (the instructor declares it per assignment), so `signal_service._sources_for_type`
    already routes precisely, by type, with no detection needed.
    `type_code_for_assignment` is more accurate than content-sniffing (an essay
    that quotes code wouldn't be misrouted).
  - auto-analyser only does **routing**. FeedForward still needs its own
    per-analyser flatteners (`_flatten_text/code/citation_response`) and
    per-type category mappings — that's the real work, and auto-analyser
    can't collapse it. So adopting it removes a two-line dict lookup and adds
    a fourth always-on sidecar (`:8010`) to keep healthy.
  - It also can't express "essay → **two** sources (document + cite-sight)";
    that fan-out lives correctly in `_sources_for_type`.

  Revisit only if FeedForward grows a genuine "mixed/unknown submission" type
  (e.g. a zip of arbitrary files), where bundle-/auto-analyser would earn their
  keep. Until then, S4 is **complete**: code and essay assignments both produce
  signals via the same pipeline (the S4 exit criterion), routed explicitly.

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
  **Tooling landed 2026-06-13:** `/instructor/assignments/{id}/signal-calibration`
  (`signal_calibration.calibration_for_assignment`) compares signal estimates
  against instructor-released scores per category and surfaces systematic bias —
  the evidence loop for retuning rules as real submissions accumulate.
- How to weight the signal run vs LLM runs in aggregation (start: equal; expose later).
- Whether to surface signal *contributions* to students or only the blended score.

## Risks / watch-items (from ADR 012)
- lens maturity: use HTTP/library, **not** document-analyser's CLI (known bug); pin versions.
- ML deps stay in the sidecar, never in FeedForward's process.
- Missing signals → add them in the relevant **lens** analyser, not in FeedForward.
