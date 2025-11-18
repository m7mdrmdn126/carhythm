# CaRhythm - Career DNA Assessment System

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Database Schema](#database-schema)
5. [Core Features](#core-features)
6. [Module Details](#module-details)
7. [Setup and Installation](#setup-and-installation)
8. [Running the Application](#running-the-application)
9. [API Documentation](#api-documentation)
10. [Testing](#testing)

---

## Overview

CaRhythm is a comprehensive web-based career assessment platform that evaluates students across three psychological dimensions:

1. **RIASEC Career Interest** - Holland Code assessment measuring career preferences
2. **Big Five Personality** - Trait assessment measuring personality dimensions
3. **Work Rhythm Traits** - Work-related characteristics assessment

The system provides:
- Interactive multi-page assessments with various question types
- Advanced scoring algorithms with weighted calculations
- Professional PDF reports with visualizations
- Admin panel for complete assessment management
- Question pool system for reusable content
- CSV import/export capabilities

---

## System Architecture

### Application Structure
```
carhythm/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── database.py         # Database configuration
│   │   ├── admin.py            # Admin user model
│   │   ├── page.py             # Assessment page model
│   │   ├── question.py         # Question model with types
│   │   ├── question_pool.py    # Question pool & categories
│   │   ├── response.py         # Student responses & answers
│   │   └── assessment_score.py # Calculated scores
│   ├── routers/                # FastAPI route handlers
│   │   ├── admin.py            # Admin authentication
│   │   ├── admin_panel.py      # Admin CRUD operations
│   │   ├── examination.py      # Student exam interface
│   │   └── question_pool.py    # Question pool management
│   ├── services/               # Business logic layer
│   │   ├── auth.py             # Authentication service
│   │   ├── question_service.py # Question CRUD operations
│   │   ├── response_service.py # Response handling
│   │   ├── scoring_service.py  # Assessment scoring algorithms
│   │   ├── pdf_service.py      # PDF report generation
│   │   ├── csv_import_service.py # CSV import/export
│   │   └── question_pool_service.py # Question pool operations
│   ├── schemas/                # Pydantic validation models
│   ├── utils/                  # Helper functions
│   │   ├── helpers.py          # Utility functions
│   │   └── security.py         # Password hashing
│   ├── static/                 # Static assets
│   │   ├── css/                # Stylesheets
│   │   ├── js/                 # JavaScript files
│   │   ├── img/                # Images
│   │   └── uploads/            # User uploaded files
│   └── templates/              # Jinja2 HTML templates
│       ├── base/               # Base templates
│       ├── admin/              # Admin interface
│       ├── student/            # Student interface
│       └── csv_templates/      # CSV templates
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   ├── performance/            # Performance tests
│   └── security/               # Security tests
├── run.py                      # Application launcher
├── populate_db.py              # Database population script
├── populate_question_pool.py   # Question pool seeding
└── requirements.txt            # Python dependencies
```

### Design Pattern: MVC Architecture
- **Models**: SQLAlchemy ORM models in `app/models/`
- **Views**: Jinja2 templates in `app/templates/`
- **Controllers**: FastAPI routers in `app/routers/`
- **Services**: Business logic layer for separation of concerns

---

## Technology Stack

### Backend
- **FastAPI** 0.104.1 - Modern async web framework
- **Uvicorn** 0.24.0 - ASGI server
- **SQLAlchemy** 2.0.23 - ORM and database toolkit
- **Python-Jose** 3.3.0 - JWT token handling
- **Passlib** 1.7.4 - Password hashing with bcrypt

### Frontend
- **Jinja2** 3.1.2 - Template engine
- **HTML/CSS/JavaScript** - Responsive UI
- **Custom CSS** - No external CSS frameworks

### Data Processing
- **ReportLab** 4.0.7 - PDF generation
- **Matplotlib** 3.8.2 - Chart visualization
- **Python-Multipart** 0.0.6 - File uploads

### Database
- **SQLite** - Default database (via aiosqlite 0.19.0)
- Supports PostgreSQL/MySQL via DATABASE_URL configuration

---

## Database Schema

### Core Tables

#### 1. `admins`
```sql
- id: INTEGER PRIMARY KEY
- username: VARCHAR(50) UNIQUE
- password_hash: VARCHAR(128)
- created_at: TIMESTAMP
```

#### 2. `pages`
```sql
- id: INTEGER PRIMARY KEY
- title: VARCHAR(200)
- description: TEXT
- order_index: INTEGER
- is_active: BOOLEAN
- created_at: TIMESTAMP
```

#### 3. `questions`
```sql
- id: INTEGER PRIMARY KEY
- page_id: INTEGER FOREIGN KEY
- question_text: TEXT
- question_type: ENUM (essay, slider, mcq, ordering)
- image_path: VARCHAR(255)
- order_index: INTEGER
- is_required: BOOLEAN
- essay_char_limit: INTEGER
- slider_min_label: VARCHAR(100)
- slider_max_label: VARCHAR(100)
- mcq_options: TEXT (JSON)
- mcq_correct_answer: TEXT (JSON)
- allow_multiple_selection: BOOLEAN
- ordering_options: TEXT (JSON)
- randomize_order: BOOLEAN
- created_at: TIMESTAMP
```

#### 4. `student_responses`
```sql
- id: INTEGER PRIMARY KEY
- session_id: VARCHAR(36) UNIQUE (UUID)
- email: VARCHAR(255)
- full_name: VARCHAR(200)
- age_group: VARCHAR(50)
- country: VARCHAR(100)
- origin_country: VARCHAR(100)
- completed_at: TIMESTAMP
- created_at: TIMESTAMP
```

#### 5. `question_answers`
```sql
- id: INTEGER PRIMARY KEY
- response_id: INTEGER FOREIGN KEY
- question_id: INTEGER FOREIGN KEY
- answer_text: TEXT
- answer_value: FLOAT
- answer_json: TEXT (JSON)
```

#### 6. `assessment_scores`
```sql
- id: INTEGER PRIMARY KEY
- response_id: INTEGER FOREIGN KEY UNIQUE
- riasec_r_score: FLOAT
- riasec_i_score: FLOAT
- riasec_a_score: FLOAT
- riasec_s_score: FLOAT
- riasec_e_score: FLOAT
- riasec_c_score: FLOAT
- riasec_profile: VARCHAR(20)
- riasec_complete: BOOLEAN
- bigfive_openness: FLOAT
- bigfive_conscientiousness: FLOAT
- bigfive_extraversion: FLOAT
- bigfive_agreeableness: FLOAT
- bigfive_neuroticism: FLOAT
- bigfive_complete: BOOLEAN
- workrhythm_motivation: FLOAT
- workrhythm_grit: FLOAT
- workrhythm_self_efficacy: FLOAT
- workrhythm_resilience: FLOAT
- workrhythm_learning: FLOAT
- workrhythm_empathy: FLOAT
- workrhythm_procrastination: FLOAT
- workrhythm_complete: BOOLEAN
- calculated_at: TIMESTAMP
- last_updated: TIMESTAMP
- notes: TEXT
```

### Question Pool Tables

#### 7. `categories`
```sql
- id: INTEGER PRIMARY KEY
- name: VARCHAR(100) UNIQUE
- description: TEXT
- color: VARCHAR(7)
- created_at: TIMESTAMP
- is_active: BOOLEAN
```

#### 8. `question_pool`
```sql
- id: INTEGER PRIMARY KEY
- title: VARCHAR(200)
- question_text: TEXT
- question_type: VARCHAR(20)
- category_id: INTEGER FOREIGN KEY
- [All question type fields from questions table]
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
- created_by: VARCHAR(100)
- usage_count: INTEGER
```

#### 9. `question_page_assignments`
```sql
- id: INTEGER PRIMARY KEY
- question_pool_id: INTEGER FOREIGN KEY
- page_id: INTEGER FOREIGN KEY
- order_index: INTEGER
- assigned_at: TIMESTAMP
- assigned_by: VARCHAR(100)
```

#### 10. `import_logs`
```sql
- id: INTEGER PRIMARY KEY
- filename: VARCHAR(255)
- import_type: VARCHAR(50)
- total_rows: INTEGER
- successful_imports: INTEGER
- failed_imports: INTEGER
- errors: TEXT (JSON)
- imported_by: VARCHAR(100)
- imported_at: TIMESTAMP
```

---

## Core Features

### 1. Multi-Type Question System

#### Question Types:

**Essay Questions**
- Free-text responses with character limits
- Rich text input support
- Configurable character constraints

**Slider Questions**
- 0-100 value range
- Customizable min/max labels
- Used for Likert-scale items

**Multiple Choice Questions (MCQ)**
- Single or multiple selection
- Configurable options (2+)
- Correct answer tracking
- Support for forced-choice pairs

**Ordering Questions**
- Drag-and-drop item ranking
- Configurable randomization
- Used for preference ranking

### 2. Assessment Workflow

**Student Journey:**
1. Landing page (welcome)
2. Personal information collection
3. Multi-page assessment (paginated)
4. Progress tracking with next/previous navigation
5. Answer persistence (session-based)
6. Completion confirmation
7. Results page with scores

**Features:**
- Session management with UUID
- Auto-save functionality
- Page navigation with validation
- Mobile-responsive interface
- Progress indicators

### 3. Scoring System

#### RIASEC Career Interest Scoring
**Formula**: `Final = 0.5 × Likert + 0.3 × Forced Choice + 0.2 × Ranking`

**Components:**
- **Likert Items** (18 questions, 3 per type): Mean × 50
- **Forced Choice** (6 pairs): (Count chosen / Total) × 100
- **Ranking** (3 sets): Position-weighted scoring

**Output:**
- R, I, A, S, E, C scores (0-100)
- Top 3 profile code (e.g., "R-I-A")

#### Big Five Personality Scoring
**Formula**: `Score = Mean × 50` (per trait)

**Traits:**
- Openness
- Conscientiousness
- Extraversion
- Agreeableness
- Neuroticism

**Features:**
- Reverse-keyed item support
- 0-100 scale per trait

#### Work Rhythm Traits Scoring
**Formula**: `Score = Mean × 50` (with reverse keying)

**Traits:**
- Motivation
- Grit
- Self-Efficacy
- Resilience
- Learning Agility
- Empathy
- Procrastination (reverse-keyed)

### 4. PDF Report Generation

**Features:**
- Professional layout with branding
- Student information summary
- Radar chart visualizations
- Score tables with interpretations
- Color-coded results
- Downloadable format

**Report Sections:**
1. Header with student info
2. RIASEC profile with chart
3. Big Five personality with chart
4. Work Rhythm traits with chart
5. Score interpretation guides

### 5. Admin Panel

#### Page Management
- Create/edit/delete pages
- Reorder pages
- Activate/deactivate pages
- Add descriptions

#### Question Management
- Create questions of all types
- Edit existing questions
- Delete questions
- Reorder within pages
- Upload images
- Bulk operations

#### Response Management
- View all student responses
- Search and filter
- Export to CSV
- View individual submissions
- Calculate scores on-demand
- Generate PDF reports
- Delete responses

### 6. Question Pool System

**Features:**
- Central question repository
- Category organization
- Question reusability
- Usage tracking
- Assignment to multiple pages

**Categories:**
- Personal Background
- Skills Evaluation
- Career Interests
- Career Goals
- Work Preferences

**Operations:**
- Create/edit/delete questions
- Organize by category
- Assign to pages
- Track usage statistics
- Bulk CSV import

### 7. CSV Import/Export

**Import Capabilities:**
- Essay questions
- Slider questions
- MCQ questions
- Ordering questions

**CSV Templates Provided:**
- Standardized formats
- Validation rules
- Error reporting
- Import logs

**Export Features:**
- Student responses
- Question data
- Score reports
- Usage statistics

---

## Module Details

### Authentication Module (`app/services/auth.py`)
- Password hashing with bcrypt
- Session management
- Admin login/logout
- Cookie-based authentication
- Protected route decorators

### Question Service (`app/services/question_service.py`)
**Functions:**
- `get_pages()` - Retrieve all pages
- `get_page_by_id()` - Get single page
- `create_page()` - Create new page
- `update_page()` - Update page details
- `delete_page()` - Delete page and questions
- `get_questions_by_page()` - Get page questions
- `create_question()` - Create new question
- `update_question()` - Update question
- `delete_question()` - Delete question

### Response Service (`app/services/response_service.py`)
**Functions:**
- `create_student_response()` - Initialize response
- `get_student_response_by_session()` - Retrieve by session
- `update_student_info()` - Update demographics
- `create_or_update_answer()` - Save answers
- `get_answers_by_response()` - Retrieve all answers
- `mark_response_complete()` - Mark as completed
- `get_all_responses()` - List all responses
- `delete_response()` - Delete response

### Scoring Service (`app/services/scoring_service.py`)
**Functions:**
- `calculate_riasec_scores()` - RIASEC calculation
- `calculate_bigfive_scores()` - Big Five calculation
- `calculate_workrhythm_scores()` - Work traits calculation
- `calculate_all_scores()` - Complete assessment scoring
- `save_assessment_scores()` - Persist scores to DB
- `get_assessment_scores()` - Retrieve saved scores

### PDF Service (`app/services/pdf_service.py`)
**Functions:**
- `generate_pdf_report()` - Create complete report
- `create_radar_chart()` - Generate visualization
- `get_score_interpretation()` - Score text descriptions

### Question Pool Service (`app/services/question_pool_service.py`)
**Functions:**
- `get_categories()` - List categories
- `create_category()` - Create category
- `get_question_pool()` - List pool questions
- `create_question_pool()` - Add to pool
- `assign_question_to_page()` - Link question to page
- `get_page_assignments()` - View assignments
- `increment_usage_count()` - Track usage

### CSV Import Service (`app/services/csv_import_service.py`)
**Functions:**
- `validate_and_import_csv()` - Process CSV imports
- `export_questions_to_csv()` - Export questions
- `get_import_logs()` - View import history
- `download_template()` - Get CSV templates

---

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation Steps

1. **Clone the repository**
```bash
cd /path/to/carhythm
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# OR
.venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create `.env` file in root directory:
```env
DATABASE_URL=sqlite:///./career_dna.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here
```

5. **Initialize database**
```bash
python populate_db.py
```

6. **Populate question pool (optional)**
```bash
python populate_question_pool.py
```

---

## Running the Application

### Development Mode
```bash
python run.py
```

Or directly with uvicorn:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points
- **Student Interface**: http://localhost:8000/student/welcome
- **Admin Panel**: http://localhost:8000/admin/login
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

### Default Admin Credentials
- Username: `admin` (or from .env)
- Password: `admin123` (or from .env)

---

## API Documentation

### Student Endpoints

#### GET `/student/welcome`
Welcome page for students

#### GET `/student/exam`
Start assessment (creates session)

#### GET `/student/exam/page/{page_number}`
Get specific assessment page

#### POST `/student/exam/submit-answers`
Submit answers for current page
**Form Data:**
- `session_id`: Session UUID
- Question answers (varies by type)

#### POST `/student/exam/complete`
Complete assessment
**Form Data:**
- `session_id`: Session UUID
- `email`: Student email
- `full_name`: Full name
- `age_group`: Age category
- `country`: Current country
- `origin_country`: Origin country

#### GET `/student/results/{session_id}`
View results page

### Admin Endpoints

#### POST `/admin/login`
Admin authentication
**Form Data:**
- `username`: Admin username
- `password`: Admin password

#### GET `/admin/logout`
Admin logout

#### GET `/admin/dashboard`
Admin dashboard (requires auth)

#### GET `/admin/pages`
Page management interface

#### POST `/admin/pages`
Create new page

#### POST `/admin/pages/{page_id}/edit`
Update page

#### POST `/admin/pages/{page_id}/delete`
Delete page

#### GET `/admin/questions`
Question management interface
**Query Params:**
- `page_id`: Filter by page

#### POST `/admin/questions`
Create question

#### POST `/admin/questions/{question_id}/edit`
Update question

#### POST `/admin/questions/{question_id}/delete`
Delete question

#### GET `/admin/responses`
View all responses
**Query Params:**
- `search`: Search term
- `sort`: Sort field

#### GET `/admin/responses/{response_id}`
View single response

#### POST `/admin/responses/{response_id}/calculate-scores`
Calculate assessment scores

#### GET `/admin/responses/{response_id}/download-pdf`
Generate and download PDF report

#### GET `/admin/responses/{response_id}/export-csv`
Export response as CSV

#### POST `/admin/responses/{response_id}/delete`
Delete response

### Question Pool Endpoints

#### GET `/admin/question-pool`
Question pool interface

#### GET `/admin/question-pool/categories`
List categories

#### POST `/admin/question-pool/categories`
Create category

#### GET `/admin/question-pool/questions`
List pool questions

#### POST `/admin/question-pool/questions`
Create pool question

#### POST `/admin/question-pool/questions/{question_id}/assign`
Assign question to page

#### POST `/admin/question-pool/import-csv`
Import questions from CSV
**Form Data:**
- `file`: CSV file
- `question_type`: Question type

#### GET `/admin/question-pool/export-csv`
Export pool questions

#### GET `/admin/question-pool/templates/{question_type}`
Download CSV template

---

## Testing

### Test Structure
```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── performance/       # Performance and load tests
└── security/          # Security tests
```

### Running Tests

**All tests:**
```bash
pytest
```

**Specific test file:**
```bash
pytest tests/unit/test_scoring.py
```

**With coverage:**
```bash
pytest --cov=app --cov-report=html
```

**Test scripts:**
```bash
./run_tests.sh        # Linux/Mac
run_tests.bat         # Windows
```

### Test Files
- `requirements-test.txt` - Testing dependencies
- `pytest.ini` - Pytest configuration
- `conftest.py` - Test fixtures and configuration

---

## Database Population Scripts

### `populate_db.py`
Seeds the database with:
- Sample pages (10 pages)
- Sample questions (various types)
- Sample student responses (50)
- Sample answers
- Admin user

**Usage:**
```bash
python populate_db.py
```

### `populate_question_pool.py`
Seeds question pool with:
- Categories (5)
- Sample questions in pool (20+)
- Various question types

**Usage:**
```bash
python populate_question_pool.py
```

### `populate_carhythm_assessment.py`
Seeds complete CaRhythm assessment with actual inventory questions following the published assessment structure.

**Usage:**
```bash
python populate_carhythm_assessment.py
```

---

## Security Features

1. **Password Security**
   - Bcrypt hashing
   - Salted passwords
   - No plaintext storage

2. **Session Management**
   - UUID-based sessions
   - HTTP-only cookies
   - Session validation

3. **Input Validation**
   - Pydantic schemas
   - Type checking
   - SQL injection prevention (ORM)

4. **File Upload Security**
   - File type validation
   - Size limits
   - Secure file naming
   - Directory restrictions

5. **Authentication**
   - Cookie-based auth
   - Protected routes
   - Admin-only endpoints

---

## Configuration

### Environment Variables
```env
DATABASE_URL=sqlite:///./career_dna.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure_password
SECRET_KEY=your-secret-key
MAX_FILE_SIZE=5242880  # 5MB
UPLOAD_DIR=app/static/uploads
```

### Database Migration
To change database (e.g., PostgreSQL):
```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

---

## Troubleshooting

### Common Issues

**Database locked error:**
- Close other database connections
- Use WAL mode for SQLite

**Import errors:**
- Verify virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

**Port already in use:**
- Change port in `run.py` or use: `uvicorn app.main:app --port 8001`

**Static files not loading:**
- Check `app/static/` directory exists
- Verify file permissions

**Admin can't login:**
- Reset password using populate_db.py
- Check .env configuration

---

## Maintenance

### Backup Database
```bash
cp career_dna.db career_dna_backup_$(date +%Y%m%d).db
```

### Clear Test Data
```bash
python populate_db.py  # Re-runs with fresh data
```

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## License

Copyright © 2025 CaRhythm Assessment System

---

## Support

For issues, questions, or contributions, please contact the development team.
