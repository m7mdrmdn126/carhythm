# CaRhythm Archive

This directory contains files that are not actively used in the main application but are kept for reference and historical purposes.

## Directory Structure

### 📄 `/docs` - Documentation Files
All markdown documentation files from the development process:
- Implementation summaries and progress reports
- Setup guides (Email, Gmail, Admin)
- Database migration documentation
- Testing checklists
- Deployment guides

### 🔧 `/scripts` - Population & Migration Scripts
Scripts used during development for database setup:
- `populate_*.py` - Various database population scripts
- `migrate_story_mode.py` - Story mode migration script
- `populate_db.bat` - Windows batch script for DB population

### 🗂️ `/old_services` - Deprecated Service Files
Previous versions of service modules:
- `scoring_service_OLD.py` - Old v1.0 scoring implementation
- `pdf_service_v1_0_OLD.py` - Old v1.0 PDF generation

### 🧪 `/tests` - Old Test Scripts
Previous testing scripts (superseded by `test_complete_flow.py`):
- `test_email_delivery.py` - Email testing script
- `test_v1_1_integration.sh` - Integration test shell script
- `run_tests.bat` / `run_tests.sh` - Test runners

### 📊 `/pdfs` - Generated & Reference PDFs
- Test output PDFs from various test runs
- CaRhythm Q Inventory.pdf (reference document)
- Sample generated reports

### 💾 `/backups` - Backups & Misc Files
- Database backups from migration phases
- `final_qustions.txt` - Question drafts
- `PROJECT_STRUCTURE.txt` - Old project structure reference

## Current Active Files (Not in Archive)

**Core Application:**
- `run.py` - Main application entry point
- `app/` - Main application package
- `frontend/` - React frontend application
- `tests/` - Current test suite

**Active Configuration:**
- `.env` / `.env.example` - Environment configuration
- `requirements.txt` / `requirements-test.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `.gitignore` - Git ignore rules

**Current Services (app/services/):**
- `scoring_service_v1_1.py` - Current scoring implementation
- `pdf_service.py` - Current PDF generation (v1.1)
- `email_service.py` - Email delivery service
- Other active services

**Current Test:**
- `test_complete_flow.py` - Comprehensive test suite for engineer profiles

## Notes

- All archived files were moved on December 3, 2025
- These files may be useful for reference but are not required for the application to run
- Database backups should be kept until production is stable
