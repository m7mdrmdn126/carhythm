# Carhythm Project Structure

This document describes the organized directory structure of the Carhythm project.

## Root Directory

The root directory contains only essential project files:

```
/
├── app/                    # Main application code
├── tests/                  # All testing infrastructure
├── archive/                # Historical files, backups, and documentation
├── scripts/                # Utility scripts
├── frontend/               # Frontend application
├── career_dna.db           # SQLite database (active)
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── run_tests.sh           # Test runner wrapper (→ tests/run_all_tests.py)
├── pytest.ini             # Symlink to tests/config/pytest.ini
└── .env                   # Environment configuration
```

## Directory Details

### `/app` - Application Code
Main FastAPI application with MVC structure:
- **models/** - Database models (SQLAlchemy)
- **routers/** - API endpoints and route handlers
- **schemas/** - Pydantic schemas for validation
- **services/** - Business logic layer
- **static/** - Static files (CSS, JS, images)
- **templates/** - Jinja2 HTML templates
- **utils/** - Helper functions and utilities

### `/tests` - Testing Infrastructure
Comprehensive test suite organized by test type:

```
tests/
├── config/
│   ├── pytest.ini              # Pytest configuration
│   └── requirements-test.txt   # Test dependencies
├── fixtures/                   # Test fixtures and data
├── unit/                       # Unit tests (111 tests)
├── integration/                # Integration tests (255 tests)
├── security/                   # Security tests
├── performance/                # Performance/benchmark tests
├── test_logs/                  # Test execution logs
├── conftest.py                 # Pytest configuration
├── run_all_tests.py           # Main test orchestrator
└── README.md                   # Testing documentation
```

**Running Tests:**
```bash
# From root directory
./run_tests.sh

# Or directly
python3 tests/run_all_tests.py

# Or with pytest
pytest
```

**Test Statistics:**
- Total Tests: 455
- Passing: 340 (74.7%)
- Unit Tests: 111/116 passing
- Integration Tests: Multiple endpoint coverage

### `/archive` - Historical Files
Organized archive of old files, documentation, and backups:

```
archive/
├── backups/                # Database backups
│   └── career_dna.db.backup_*
├── deployment/             # Deployment scripts
│   ├── database_update.sql
│   └── deploy.sh
├── docs/                   # Historical documentation
│   ├── ADMIN_GUIDE.md
│   ├── DEPLOYMENT.md
│   ├── EMAIL_DELIVERY_SETUP.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── TEST_FIXES_TODO.md
├── old_tests/              # Old test scripts and PDFs
│   ├── test_*.py          # Legacy test files
│   └── test_*.pdf         # Test output PDFs
├── old_services/           # Deprecated service files
├── pdfs/                   # Sample PDF outputs
├── scripts/                # Old utility scripts
└── README.md              # Archive documentation
```

### `/scripts` - Utility Scripts
Active utility scripts for maintenance tasks:
- `add_arabic_translations.py` - Add Arabic translations to database
- `add_translation_columns.py` - Database schema updates
- `update_server_database.sh` - Server database sync script

### `/frontend` - Frontend Application
Vue.js/Vite frontend application (separate from main FastAPI app).

## File Organization Guidelines

### Files belong in root if they are:
- ✅ Core application entry points (`run.py`)
- ✅ Project dependencies (`requirements.txt`)
- ✅ Active database (`career_dna.db`)
- ✅ Environment configuration (`.env`)
- ✅ Version control config (`.gitignore`)

### Files belong in `/tests` if they are:
- ✅ Test files (`test_*.py`)
- ✅ Test configuration (`pytest.ini`, `conftest.py`)
- ✅ Test fixtures and data
- ✅ Test dependencies (`requirements-test.txt`)
- ✅ Test logs and reports

### Files belong in `/archive` if they are:
- ✅ Database backups (`.db.backup_*`)
- ✅ Old documentation (`.md` guides)
- ✅ Deployment scripts not in active use
- ✅ Legacy test files
- ✅ Historical PDF outputs
- ✅ Deprecated code

### Files belong in `/scripts` if they are:
- ✅ Active utility scripts
- ✅ Database maintenance tools
- ✅ Translation management

## Recent Organization Changes (2025-01-04)

### Files Moved to `/tests`:
- `pytest.ini` → `tests/config/pytest.ini` (+ symlink in root)
- `requirements-test.txt` → `tests/config/`
- `run_all_tests.py` → `tests/`
- `test_logs/` → `tests/test_logs/`

### Files Moved to `/archive`:
- `career_dna.db.backup_*` → `archive/backups/`
- `database_update.sql` → `archive/deployment/`
- `deploy.sh` → `archive/deployment/`
- `TEST_FIXES_TODO.md` → `archive/docs/`
- Old test scripts → `archive/old_tests/`
- Test PDF outputs → `archive/old_tests/`

### New Files Created:
- `run_tests.sh` - Convenience wrapper for test execution
- `PROJECT_STRUCTURE.md` - This file

## Maintenance

### Adding New Files
- **Tests:** Add to appropriate subdirectory in `/tests`
- **Documentation:** Add to `/archive/docs` if historical, root if current
- **Scripts:** Add to `/scripts` if active utility
- **Backups:** Add to `/archive/backups`

### Cleaning Up
Periodically review and move to `/archive`:
- Old database backups (keep latest 3-5)
- Deprecated documentation
- Test logs older than 30 days
- Obsolete scripts

## Links
- [Testing Documentation](tests/README.md)
- [Archive Contents](archive/README.md)
- [Frontend README](frontend/README.md)
