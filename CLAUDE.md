# FeedForward Development Guide

## Commands
- Install: `pip install -r requirements.txt`
- Initialize DB: `python app/init_db.py`
- Run app: `python app.py`
- Run test: `pytest tests/test_name.py`
- Run single test: `pytest tests/test_name.py::test_function`
- Type check: `mypy app/`

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