# FeedForward Development Guide

## Setup & Commands

### Initial Setup (using uv)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Development Commands
- Initialize DB: `python app/init_db.py`
- Run app: `python app.py`
- Format code: `ruff format .`
- Lint code: `ruff check . --fix`
- Type check: `mypy app/`
- Run tests: `pytest`
- Run specific test: `pytest tests/test_name.py::test_function`
- Test AI integration: `python tools/test_ai_integration.py`
- Test instructor UI: `python tools/test_instructor_feedback_ui.py`

## Code Style
- **Python**: Follow PEP 8 (4 spaces, 88 char line limit)
- **Imports**: Group standard lib, third-party, and local imports
- **Types**: Use type hints; prefer explicit over implicit
- **Error Handling**: Use specific exceptions; log errors
- **Routes**: Organize by auth roles (admin, instructor, student)
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **UI**: Use FastHTML components; maintain Tailwind classes
- **Database**: Apply SQLite best practices; validate inputs
- **Auth**: Enforce role-based security on all routes

## Repository Structure
Models → Routes → Services → Templates → Utils

## AI Integration
- **AI Client** (`app/utils/ai_client.py`): LiteLLM integration for multi-provider support
- **Feedback Orchestrator** (`app/utils/feedback_orchestrator.py`): Multi-model runs and aggregation
- **Feedback Pipeline** (`app/utils/feedback_pipeline.py`): Async processing pipeline
- **Processing Flow**: Draft submission → Background processing → Multi-model evaluation → Aggregation → Feedback ready
- **Supported Providers**: OpenAI, Anthropic, Google, Cohere, HuggingFace
- **Aggregation Methods**: Mean, Weighted Mean, Median, Trimmed Mean

## Instructor Feedback Interfaces
- **Submission Listing** (`/instructor/assignments/{id}/submissions`): View all submissions with status
- **Individual Details** (`/instructor/submissions/{draft_id}`): LLM breakdown and score comparison
- **Feedback Review** (`/instructor/submissions/{draft_id}/review`): Edit and approve AI feedback
- **Analytics Dashboard** (`/instructor/assignments/{id}/analytics`): LLM performance metrics
- **Features**: Raw AI responses, aggregated scores, bulk approval, performance insights