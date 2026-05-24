# ADR 012: Signal-Based Assessment via the lens Analyser Family

## Status

Proposed

## Context

FeedForward currently scores submissions with an **LLM-as-judge** approach: the LLM
reads the whole submission and emits a 0–100 score per rubric category, which is then
aggregated across model runs (`app/services/feedback_generator.py`). This works, but:

- It is **opaque** — a student (or auditor) cannot see *why* a category scored 6/10.
- It is **non-deterministic and metered** — every run costs an API call and varies.
- It captures semantic judgment but does **not** expose concrete, improvable surface
  signals (readability, structure, citation hygiene, code complexity).

Separately, the maintainer owns the **lens analyser family** (`../lens`): independent
tools that each take a file and return structured JSON *signals*, sharing one contract
(Python `.analyse()` → pydantic; CLI; HTTP `GET /health` + `GET /manifest` +
`POST /analyse` on ports 8000–8009; `auto-analyser` routes by file extension). They
already compute, deterministically and offline:

- **document-analyser** — readability (Flesch, FK grade), structure (paragraphs,
  sentence variety, `overall_coherence_score`), `vocabulary_richness`, writing quality
  (passive voice %, hedging, transitions, academic tone), and — behind the optional
  `[nlp]` extra — sentiment/polarity (`SentimentScore.compound`, granular), NER, and
  semantic embeddings.
- **code-analyser** — cyclomatic complexity, lint violations, docstring/type/comment
  coverage.
- **cite-sight** — citation integrity score, missing/orphaned in-text citations,
  broken URLs, unresolved DOIs (TypeScript/Node; consumed over HTTP).
- **conversation-analyser** — a 0–100 critical-thinking score (for process artefacts).

The maintainer wants **signal-based assessment**: compute metrics from a submission →
map metrics to rubric elements → estimate a score → **instructor reviews the signals
and adjusts the mark**.

[ADR 011](011-assessment-type-extensibility.md) already established a plugin assessment
architecture and explicitly anticipated "reuse of existing tools as microservices"
via an `ExternalAssessmentService`. This ADR makes that concrete with the lens family
and decides how signal-derived scores relate to the existing LLM scores.

## Decision

### 1. FeedForward consumes lens; it does not build its own analysis

FeedForward will **not** implement document parsing beyond the existing text
extraction, nor any NLP/readability/complexity/citation metric calculation. Those are
the lens family's job. The nascent metric code in the assessment handlers
(`app/assessment/handlers/{essay,code,math}.py`) is to be superseded by lens signals.
When a needed signal does not exist, it is added **inside the relevant lens analyser**,
not inside FeedForward.

### 2. Analysers run as HTTP sidecar services

FeedForward calls the analysers over their HTTP contract (`POST /analyse`), with
`auto-analyser` as the single entry point for auto-routable types (documents, code,
images, …) and explicit calls to non-auto-routable members (`cite-sight`,
`conversation-analyser`) when an assignment type asks for them.

Rationale for HTTP over in-process import:
- Keeps heavy/brittle ML dependencies (torch + spaCy + sentence-transformers +
  transformers — documented as brittle when co-loaded on macOS) **out of**
  FeedForward's process and dependency tree.
- Works for the Node-based `cite-sight` (language-neutral by contract).
- Lets analysers be deployed/scaled/restarted independently.
- Matches the `ExternalAssessmentService` shape from ADR 011.

(Pure-Python `document-analyser`/`code-analyser` *may* be imported directly in
dev for convenience, but HTTP is the default and the only supported production path.)

### 3. Signals are mapped to rubric categories by a configurable scorer

A new `SignalService` extracts raw signals; a new `SignalScorer` applies
**signal rules** that transform a raw signal value into a 0–100 contribution for a
specific rubric category (e.g. *Flesch 50–60 → Clarity 70*), with a confidence.
Rules are per-assessment-type defaults, overridable per assignment. Categories with no
signal rule simply receive no signal contribution — this is expected (see Consequences).

### 4. Signals are stored as *evidence alongside* the LLM, not as a replacement

Per the maintainer's decision, signal scores join the existing aggregation rather than
replacing LLM judgment. We represent the signal engine as a **synthetic model run**:

- Seed one `ai_models` row: `name="Signal Engine (lens)"`, `provider="signal"`,
  `owner_type="system"`.
- Per draft, `SignalScorer` creates a `ModelRun` against that model, stores the raw
  analyser JSON in `ModelRun.raw_response`, and writes `CategoryScore` rows from the
  mapping.
- The existing aggregation (`_aggregate_feedback` / `_compute_aggregated_score`) groups
  `CategoryScore` by category across **all** model runs — so signal scores blend in
  with **zero changes to the aggregation code**.

Raw signals are additionally persisted in a new queryable `signals` table so they
survive the privacy content-deletion lifecycle (ADR 002 / 008) and can be shown to the
instructor and trended across drafts.

### 5. The instructor review/adjust step is wired up

The decision adds the human-in-the-loop step using fields **already present** in the
schema: `AggregatedFeedback.status` (`pending_review` → `approved` → `released`),
`edited_by_instructor`, `instructor_email`, and the `feedbacks` approval table. The
instructor sees signals + LLM feedback + the estimated score, adjusts, and releases.
This is the previously-unbuilt "feedback preview/approval" (old Phase 4.1), now driven
by signals.

### 6. The assessment-handler seam is slimmed and made live (A3)

The seam §1/§3 hang signal extraction on (`AssessmentHandler.preprocess`) is currently
**dead** — `generate_feedback_for_draft` builds its prompt straight from `draft.content`
and never calls a handler; the registry is orphaned and builds itself from the DB at
import. We settle it ("A3" in the 2026-05-23 architecture review):

- The handler becomes a **slim, DB-free declaration seam**, built from **in-process
  constants** (not a DB scan at import). The `assessment_types` table survives as
  display metadata only.
- Per type it declares: `validate_submission`, **`get_signal_sources()`** (which lens
  analysers apply), `get_prompt_template`, `format_feedback`, and a thin
  **`shape_for_prompt(text) -> str`** (code → line numbers, math → LaTeX-readable,
  essay → identity).
- The handlers' **inline metric computation is deleted** — lens computes metrics; text
  extraction already lives in `app/utils/file_handlers.py`.
- `generate_feedback_for_draft` resolves the handler from `assignment.assessment_type_id`
  (default `essay`) and uses it for signal sources, prompt, and shaping.

This amends ADR 011 (which made `preprocess` a core method and discovery DB-driven) and
makes §1/§3's "the seam already exists" true.

## Consequences

### Positive

- **Transparency & defensibility** — scores trace back to concrete, named signals.
- **Cheaper & reproducible** — deterministic signals reduce reliance on metered,
  variable LLM calls; LLM can be dialled down or made optional per assignment.
- **Instructor control** — aligns with FeedForward's "instructor-controlled" principle.
- **Privacy synergy** — signals are non-identifying numbers; keep the signals, delete
  the text (reinforces ADR 002/008).
- **No duplication** — reuses mature tooling; the integration seam
  (`AssessmentHandler.preprocess`) and the multi-source aggregation already exist.
- **Minimal schema change** — the synthetic-model-run trick reuses the whole pipeline.

### Negative / risks

- **Surface, not depth** — signals capture form (readability, structure, citations,
  complexity), not higher-order semantics (argument depth, originality). *Mitigation:*
  keep the LLM as a co-equal evidence source; leave such categories signal-free.
- **Operational complexity** — running and supervising sidecar services. *Mitigation:*
  health-checks + graceful degradation (if an analyser is down, skip its signals, log,
  proceed with LLM only).
- **lens maturity** — several analysers are alpha/beta; `document-analyser`'s **CLI**
  has a known attribute-name bug (use HTTP/library, not the CLI); `analyse/analyze`
  spelling and public-API surfaces are still being unified across the family. *Mitigation:*
  pin versions, integrate via HTTP, add smoke tests on our side.
- **Mapping calibration** — signal→score thresholds need tuning and can be gamed
  ("teaching to the metric"). *Mitigation:* instructor-overridable rules; signals are
  evidence the instructor adjusts, never the final mark.

## Implementation

Detailed phased roadmap (tracer-bullet first) lives in
[`SIGNAL_INTEGRATION_PLAN.md`](../../SIGNAL_INTEGRATION_PLAN.md). Key components:

- `app/utils/analyser_client.py` — thin HTTP client (base URLs from config/env,
  health-check, timeout, graceful degradation).
- `app/services/signal_service.py` — extract + normalize raw signals into `signals`
  rows; declares per-assessment-type signal sources via the handler.
- `app/services/signal_scorer.py` — apply `signal_rules` → `CategoryScore` under the
  synthetic `ModelRun`.
- New tables: `signals` (queryable raw signals) and `signal_rules`
  (rubric_category_id → transform + weight).
- Instructor review UI on the existing `AggregatedFeedback` approval fields.

This supersedes the metric logic in the essay/code/math handlers and refines, rather
than replaces, ADR 011's external-service vision.
