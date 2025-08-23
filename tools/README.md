# FeedForward Tools

This directory contains utility scripts for managing and maintaining the FeedForward system.

## 🛠️ Active Tools

### Production Utilities
- **`cleanup_drafts.py`** - Remove old draft submissions and temporary files
- **`delete_user.py`** - Safely remove user accounts and associated data
- **`check_llm_health.py`** - Check health and connectivity of AI model providers

### Setup & Configuration
- **`init_db_standalone.py`** - Initialize database schema (standalone mode)
- **`setup_api_keys.py`** - Configure AI provider API keys securely
- **`seed_domain_whitelist.py`** - Configure allowed email domains for registration

### Development & Maintenance
- **`tech_debt_tracker.py`** - Track and manage technical debt items

## 📁 Archive Directory

The `archive/` directory contains scripts that were used during development but are not typically needed for regular operations:

### One-time Migration Scripts
- Database migration scripts (`migrate_*.py`)
- Code refactoring utilities (`fix_*.py`, `refactor_*.py`)

### Development & Testing Tools
- Demo data creation (`create_demo_accounts.py`, `create_sample_data.py`)
- Testing utilities (`test_*.py`)
- License generation (`generate_licenses.py`)

### Usage Notes
- Archived scripts are kept for historical reference
- They may require updates to work with current codebase
- Use with caution as they may modify production data

## 🚀 Quick Commands

```bash
# Clean up old drafts (run periodically)
python tools/cleanup_drafts.py

# Check AI provider connectivity
python tools/check_llm_health.py

# Initialize database (if needed)
python tools/init_db_standalone.py
```

## 📝 Adding New Tools

When adding new utility scripts:
1. Include comprehensive docstrings
2. Add error handling and logging
3. Test thoroughly before committing
4. Update this README with description and usage
5. Consider if the script should be archived after one-time use