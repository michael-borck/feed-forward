# Code Quality Implementation Plan for FeedForward

## Objective
Achieve **zero errors and warnings** in linting and type checking while properly managing technical debt.

## Current State Analysis

### Issues to Address
1. **FastHTML Import Pattern**: `from fasthtml.common import *` causes ~1700+ mypy errors
2. **Linting Issues**: Multiple function redefinitions, bare excepts, unused variables
3. **Type Checking**: Missing type annotations, implicit Optional usage
4. **No Enforcement**: No pre-commit hooks or CI/CD quality gates
5. **Technical Debt**: No tracking system for suppressed warnings

## Implementation Strategy

### Phase 1: Decision & Setup (Week 1)

#### 1.1 FastHTML Import Strategy Decision

**Option A: Namespace Imports** (Recommended)
```python
from fasthtml import common as fh

def index():
    return fh.Titled(
        "Welcome",
        fh.Div(fh.H1("Hello"), fh.P("World"))
    )
```

**Pros:**
- Zero mypy errors
- Clear code origin
- Better IDE support
- No namespace pollution

**Cons:**
- More verbose
- Requires complete refactor

**Option B: Explicit Imports**
```python
from fasthtml.common import (
    FastHTML, Titled, Div, P, H1, H2,
    Form, Input, Button, Table, Tr, Td,
    # ... list all used components
)
```

**Pros:**
- Type checker friendly
- Clean syntax
- Explicit dependencies

**Cons:**
- Long import lists
- Maintenance overhead

#### 1.2 Tool Configuration

**Ruff Configuration** (`pyproject.toml`):
```toml
[tool.ruff]
line-length = 88
target-version = "py39"
select = ["ALL"]  # Enable all rules
ignore = [
    # Document each ignored rule
    "D100",  # Missing module docstring - TECH-DEBT: Add module docstrings
    "ANN101",  # Missing type annotation for self - Not needed
]
per-file-ignores = {}  # No file-specific ignores initially
```

**Mypy Configuration** (`pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.9"
strict = true  # Enable all strict options
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true
```

### Phase 2: Automated Refactoring (Week 1-2)

#### 2.1 Import Refactoring Script

Create automated script to refactor all FastHTML imports:

```python
# tools/refactor_imports.py
"""
Automated refactoring of FastHTML imports
"""

def refactor_file(file_path):
    # Parse AST
    # Identify FastHTML usage
    # Replace with namespace imports
    # Write back file
```

#### 2.2 Type Annotation Addition

Use automated tools:
```bash
# Add basic type hints
monkeytype run app.py
monkeytype apply app

# Or use pytype
pytype --generate-config pytype.cfg .
```

### Phase 3: Systematic Fixing (Week 2-3)

#### 3.1 Fix Order

1. **Imports** - Refactor all FastHTML imports
2. **Type Annotations** - Add missing type hints
3. **Function Definitions** - Fix redefinitions
4. **Error Handling** - Replace bare excepts
5. **Code Complexity** - Refactor complex functions

#### 3.2 File Priority

1. **Core Models** (`app/models/`)
2. **Services** (`app/services/`)
3. **Utilities** (`app/utils/`)
4. **Routes** (`app/routes/`)
5. **Main App** (`app.py`)

### Phase 4: Technical Debt Management (Ongoing)

#### 4.1 Suppression Format

When suppressing is necessary, use standardized format:

```python
# TECH-DEBT: [TICKET-123] @developer 2024-01-20
# Reason: Complex refactor needed for proper typing
# Plan: Refactor in Q2 when upgrading to FastHTML 2.0
result = complex_function()  # type: ignore[no-untyped-call]
```

#### 4.2 Tracking

Run regularly:
```bash
# Track all technical debt
python tools/tech_debt_tracker.py --format markdown --save TECH_DEBT.md

# Check critical items only
python tools/tech_debt_tracker.py --severity critical
```

### Phase 5: Enforcement (Week 3)

#### 5.1 Pre-commit Hooks

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        args: [--strict, --ignore-missing-imports]

  - repo: local
    hooks:
      - id: tech-debt-check
        name: Check Technical Debt
        entry: python tools/tech_debt_tracker.py --severity critical
        language: system
        pass_filenames: false
```

#### 5.2 CI/CD Pipeline

GitHub Actions (`.github/workflows/quality.yml`):
```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      
      - name: Run Ruff
        run: ruff check . --exit-non-zero-on-fix
      
      - name: Run Mypy
        run: mypy app/ --strict
      
      - name: Check Technical Debt
        run: python tools/tech_debt_tracker.py --severity high
      
      - name: Generate Report
        if: always()
        run: |
          python tools/tech_debt_tracker.py --format markdown > tech_debt.md
      
      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: tech-debt-report
          path: tech_debt.md
```

## Implementation Timeline

### Week 1: Setup & Decision
- [ ] Team decision on FastHTML import strategy
- [ ] Configure tools (ruff, mypy)
- [ ] Create refactoring scripts
- [ ] Set up technical debt tracker

### Week 2: Core Refactoring
- [ ] Refactor imports (automated)
- [ ] Fix models and services
- [ ] Add type annotations
- [ ] Document suppressed warnings

### Week 3: Routes & UI
- [ ] Refactor route files
- [ ] Fix UI components
- [ ] Address complex functions
- [ ] Clean up test files

### Week 4: Enforcement & Documentation
- [ ] Set up pre-commit hooks
- [ ] Configure CI/CD pipeline
- [ ] Document standards
- [ ] Team training

## Success Metrics

1. **Zero Errors**: No unsuppressed linting or type errors
2. **Technical Debt**: All suppressions documented with tickets
3. **CI/CD**: All commits pass quality gates
4. **Coverage**: 100% of Python files checked
5. **Maintenance**: Weekly debt review meetings

## Rollback Plan

If issues arise:
1. Keep original code in `legacy` branch
2. Can disable strict checking temporarily
3. Gradual enforcement (warnings → errors)
4. File-by-file migration possible

## Team Agreement

All developers agree to:
1. Fix issues, don't suppress without documentation
2. Add type hints to new code
3. Run quality checks before commit
4. Review technical debt weekly
5. Refactor when touching debt-marked code

## Next Steps

1. **Immediate**: Run `python tools/tech_debt_tracker.py` to baseline
2. **Day 1**: Team meeting to decide import strategy
3. **Day 2**: Start automated refactoring
4. **Week 1**: Achieve zero errors in `app/models/`
5. **Month 1**: Full codebase compliance

## Commands Reference

```bash
# Check current state
ruff check . --statistics
mypy app/ --strict --show-error-codes

# Track technical debt
python tools/tech_debt_tracker.py

# Fix automatically
ruff check . --fix
ruff format .

# Type check with details
mypy app/ --strict --show-column-numbers --pretty

# Pre-commit checks
pre-commit run --all-files

# Generate type stubs
stubgen -p app -o typings
```

## Resources

- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Mypy Error Codes](https://mypy.readthedocs.io/en/stable/error_code_list.html)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [FastHTML Best Practices](https://docs.fasthtml.dev/best-practices)