# FeedForward Code Quality Action Plan

## Current State (As of Now)
- **501 Linting Errors** (137 auto-fixable)
- **1789 Type Checking Errors** (mostly from FastHTML star imports)
- **0 Technical Debt Markers** (good starting point)

## Decision Required: FastHTML Import Strategy

### Option A: Namespace Import (Recommended)
```python
from fasthtml import common as fh

# Usage
return fh.Titled("Page", fh.Div(fh.H1("Hello")))
```

**Impact:**
- Requires refactoring all route files
- Eliminates ~1700 type errors
- Tool available: `python tools/refactor_fasthtml_imports.py`

### Option B: Keep Star Imports with Suppressions
```python
from fasthtml.common import *  # type: ignore[import]
# TECH-DEBT: FastHTML requires star imports for HTML components
```

**Impact:**
- Minimal code changes
- Must suppress mypy for all route files
- Goes against zero-error goal

## Execution Plan

### Step 1: Backup & Branch (30 min)
```bash
# Create feature branch
git checkout -b feature/code-quality-enforcement

# Create backup
cp -r . ../feedforward-backup-$(date +%Y%m%d)
```

### Step 2: Auto-fix What We Can (1 hour)
```bash
# Fix auto-fixable linting issues
ruff check . --fix --unsafe-fixes

# Format code
ruff format .

# Commit auto-fixes
git add -A
git commit -m "chore: auto-fix linting issues"
```

### Step 3: Refactor FastHTML Imports (2-3 hours)
```bash
# Dry run first
python tools/refactor_fasthtml_imports.py --dry-run

# If looks good, run for real
python tools/refactor_fasthtml_imports.py

# Test application still works
python app.py
# Navigate through UI to verify

# Commit
git add -A
git commit -m "refactor: convert FastHTML star imports to namespace imports"
```

### Step 4: Fix Remaining Linting Issues (3-4 hours)

Priority order:
1. **Bare excepts (40)** - Add specific exception types
2. **Unused variables (18)** - Remove or use them
3. **Redefined functions (10)** - Rename functions
4. **Implicit Optional (22)** - Add Optional type hints

For each category:
```python
# Before
except:  # E722
    pass

# After - Option 1: Specific exception
except FileNotFoundError:
    pass

# After - Option 2: Document why broad
except Exception as e:  # TECH-DEBT: Need to identify specific exceptions
    logger.error(f"Unexpected error: {e}")
```

### Step 5: Add Type Hints (4-5 hours)

Focus areas:
1. All function signatures in `app/models/`
2. All public APIs in `app/utils/`
3. Route handlers return types

```python
# Before
def get_user(email):
    return users[email]

# After
def get_user(email: str) -> Optional[User]:
    return users.get(email)
```

### Step 6: Document Technical Debt (1 hour)

For any suppressions needed:
```python
# TECH-DEBT: [FEEDFORWARD-XXX] Complex refactor needed
# Owner: @developer
# Date: 2024-01-20
# Plan: Refactor when upgrading to FastHTML 2.0
result = legacy_function()  # type: ignore[no-untyped-call]
```

### Step 7: Set Up Enforcement (1 hour)

1. **Update pyproject.toml**:
```toml
[tool.ruff]
# No ignores except documented
ignore = []

[tool.mypy]
strict = true
```

2. **Create pre-commit config**:
```bash
pip install pre-commit
pre-commit install
```

3. **Add CI/CD checks** (see `.github/workflows/quality.yml`)

### Step 8: Test Everything (2 hours)
```bash
# Run all quality checks
ruff check .
mypy app/ --strict
python tools/tech_debt_tracker.py

# Run application tests
pytest

# Manual testing
python app.py
```

## Time Estimate

| Phase | Time | Cumulative |
|-------|------|------------|
| Backup & Setup | 30 min | 30 min |
| Auto-fixes | 1 hr | 1.5 hrs |
| FastHTML Refactor | 3 hrs | 4.5 hrs |
| Manual Linting Fixes | 4 hrs | 8.5 hrs |
| Type Hints | 5 hrs | 13.5 hrs |
| Documentation | 1 hr | 14.5 hrs |
| Enforcement Setup | 1 hr | 15.5 hrs |
| Testing | 2 hrs | 17.5 hrs |
| **Total** | **~18 hours** | **2-3 days** |

## Success Criteria

✅ Zero linting errors (`ruff check .` passes)
✅ Zero type errors (`mypy app/ --strict` passes)
✅ All suppressions documented with TECH-DEBT markers
✅ Pre-commit hooks installed and passing
✅ CI/CD pipeline configured
✅ Application still functions correctly
✅ All tests pass

## Rollback Plan

If issues arise:
```bash
# Rollback to backup branch
git checkout main
git branch -D feature/code-quality-enforcement

# Or revert specific commits
git revert HEAD~n
```

## Commands Cheat Sheet

```bash
# Current state
ruff check . --statistics
mypy app/ --show-error-codes

# Fix what we can
ruff check . --fix --unsafe-fixes
ruff format .

# Refactor imports
python tools/refactor_fasthtml_imports.py --dry-run
python tools/refactor_fasthtml_imports.py

# Track debt
python tools/tech_debt_tracker.py

# Test
pytest
python app.py

# Commit with conventional commits
git add -A
git commit -m "chore: enforce code quality standards"
```

## Next Actions

1. **TODAY**: Team meeting to approve FastHTML import strategy
2. **TOMORROW**: Begin execution starting with Step 1
3. **THIS WEEK**: Complete through Step 5
4. **NEXT WEEK**: Finish Steps 6-8 and merge

## Questions to Resolve

1. [ ] Namespace imports (fh.Div) or star imports with suppressions?
2. [ ] Strict mypy or gradual typing?
3. [ ] Fix all at once or file by file?
4. [ ] Who owns which sections?
5. [ ] Timeline acceptable?

---

**Ready to proceed?** Run `python tools/refactor_fasthtml_imports.py --dry-run` to see the impact.