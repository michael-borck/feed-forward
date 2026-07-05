# FeedForward - AI-Powered Educational Feedback Platform

## Project Overview

FeedForward is a web-based platform for AI-assisted formative assessment. Students submit drafts and receive multi-model AI feedback aligned with instructor rubrics. Built for Curtin University.

**Core principles**: Privacy-first (temporary content storage), iterative improvement (multi-draft), AI-powered (multi-LLM), instructor-controlled.

## Tech Stack

- **Backend**: Python 3.10+, FastHTML, Starlette, HTMX
- **Frontend**: Server-side HTML via FastHTML, Tailwind CSS
- **AI**: LiteLLM for multi-provider LLM abstraction (OpenAI, Anthropic, Google, Ollama, etc.)
- **Database**: SQLite with FastHTML's built-in ORM (dataclass-based models)
- **Auth**: Session-based, role-based (Student, Instructor, Admin)
- **Package manager**: uv

## Quick Reference Commands

> **Local dev note:** if the working copy lives on the external (exFAT) drive,
> keep the virtualenv on the internal disk — AppleDouble `._*` sidecar files
> corrupt wheel installs inside `.venv` on the external volume:
> `export UV_PROJECT_ENVIRONMENT="$HOME/.venvs/feed-forward"` before `uv sync`.

```bash
# Run the app
python app.py                      # Dev server on http://localhost:5001

# Code quality
ruff format .                      # Format code
ruff check . --fix                 # Lint with auto-fix
mypy app/                          # Type check

# Testing
pytest                             # Run tests
pytest --cov                       # With coverage

# Docker
docker-compose up                  # Standard
docker-compose -f docker-compose.dev.yml up   # Dev
docker-compose -f docker-compose.prod.yml up  # Prod

# Database
python app/init_db.py              # Initialize DB with defaults
python tools/create_demo_accounts.py  # Create demo users
```

## Project Structure

```
app/
├── __init__.py              # FastHTML app init & auth decorators
├── models/                  # Database models (dataclass-based)
│   ├── user.py              # User, Role enums
│   ├── assignment.py        # Assignment, Rubric, RubricCategory
│   ├── feedback.py          # Draft, AIModel, ModelRun, FeedbackItem
│   ├── course.py            # Course, Enrollment
│   └── config.py            # SystemConfig, AggregationMethod
├── routes/                  # FastHTML route handlers
│   ├── auth.py              # Login, signup
│   ├── admin/               # Admin panel
│   ├── instructor/          # Instructor interface
│   └── student/             # Student interface
├── services/                # Business logic
│   ├── feedback_generator.py     # Multi-model feedback generation
│   ├── rubric_generator.py       # AI rubric creation from specs
│   ├── progress_analyzer.py      # Draft comparison & metrics
│   └── prompt_templates.py       # LLM prompt building
├── assessment/              # Plugin architecture for assessment types
│   ├── base.py              # Abstract AssessmentHandler
│   ├── registry.py          # Handler discovery
│   └── handlers/            # Essay, Code, Math, Video handlers
└── utils/                   # Utilities
    ├── ai_client.py         # LiteLLM integration
    ├── feedback_orchestrator.py  # Multi-model aggregation pipeline
    ├── feedback_formatter.py     # Feedback visualization
    └── auth.py              # Password hashing
app.py                       # Main entry point
```

## Code Conventions

- **Style**: Ruff formatter, 88-char line length (Black-compatible)
- **Lint rules**: E, F, I, N, W, UP, B, C4, SIM, RUF (see pyproject.toml for ignores)
- **Naming**: snake_case functions/variables, CamelCase classes, UPPER_SNAKE_CASE constants
- **Routes**: FastHTML `@rt()` decorators, grouped by role in separate files
- **Star imports**: Allowed in routes and UI utils (FastHTML pattern) — F403/F405 suppressed
- **Type hints**: Optional but encouraged; MyPy configured leniently for FastHTML
- **Auth decorators**: `@login_required`, `@student_required`, `@instructor_required`, `@admin_required`

## Architecture Patterns

- **Plugin system**: Assessment types via `AssessmentHandler` abstract base + registry
- **Service layer**: Business logic in `app/services/`, decoupled from routes
- **Orchestration**: `FeedbackOrchestrator` coordinates multi-model feedback + aggregation
- **Privacy-by-design**: Temporary content storage, automatic deletion after feedback

## Key Documentation

- `IMPLEMENTATION_PLAN.md` — Detailed roadmap with phase status
- `docs/design/adrs/` — 10 Architecture Decision Records
- `docs/LLM_SETUP_GUIDE.md` — AI provider configuration
- `docs/design/overview.md` — Design philosophy

## Implementation Status

**Completed**: Phase 1 (Instructor Features) + Phase 2.1-2.2 (Student Experience)
- Assignment spec upload, rubric auto-generation, feedback config UI, LLM profiles
- Enhanced feedback visualization, progress tracking

**Remaining**:
- Phase 2.3: Actionable improvement recommendations
- Phase 3: Admin control panel (LLM management, usage analytics, monitoring)
- Phase 4: Polish (feedback preview, performance optimization, documentation)

## Known Issues

- Pre-commit hooks may fail (types-pkg-resources issue)
- Some type hints missing in older code
- Duplicate helper functions to consolidate
