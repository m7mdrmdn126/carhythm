# Career DNA Assessment Application

A psychological assessment platform built with FastAPI that allows students to take multi-page questionnaires and provides an admin panel for managing questions and viewing results.

## Features

- **Student Interface**: Multi-page questionnaire with essay and slider questions
- **Admin Panel**: Question and page management with authentication
- **Results Dashboard**: View and export student responses
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
uvicorn app.main:app --reload
```

3. Access the application:
- Student interface: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## Default Admin Credentials

- Username: admin
- Password: admin123

## Tech Stack

- Backend: FastAPI, SQLAlchemy, SQLite
- Frontend: Jinja2 Templates, HTML/CSS/JavaScript
- Authentication: Session-based with password hashing

## Testing

The application includes a comprehensive test suite covering unit tests, integration tests, performance tests, and security tests.

### Quick Test Setup

1. Install test dependencies:
```bash
pip install -r requirements-test.txt
```

2. Run all tests:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

4. Run specific test categories:
```bash
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m performance    # Performance tests only
pytest -m security       # Security tests only
```

### Test Structure

- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for full workflows
- `tests/performance/` - Performance and load tests
- `tests/security/` - Security vulnerability tests
- `tests/fixtures/` - Shared test fixtures and sample data

For detailed testing instructions, see [TESTING.md](TESTING.md).

## Development

### Project Structure

```
career-dna-assessment/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── models/              # Database models and schemas
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic services
│   ├── utils/               # Utility functions
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JavaScript, and images
├── tests/                   # Comprehensive test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── performance/        # Performance tests
│   ├── security/           # Security tests
│   └── fixtures/           # Test fixtures and data
├── requirements.txt         # Production dependencies
├── requirements-test.txt    # Testing dependencies
├── pytest.ini             # Test configuration
└── TESTING.md              # Detailed testing guide
```

### Code Quality

The project maintains high code quality standards:

- **Test Coverage**: Minimum 80% test coverage required
- **Security Testing**: Comprehensive security vulnerability testing
- **Performance Testing**: Load testing and performance benchmarks
- **Integration Testing**: End-to-end workflow validation

### Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Maintain test coverage: `pytest --cov=app`
6. Submit a pull request

## Deployment

### Production Checklist

1. **Security**:
   - Change default admin credentials
   - Enable HTTPS in production
   - Set secure session cookies
   - Configure proper CORS settings

2. **Performance**:
   - Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
   - Configure database connection pooling
   - Enable static file caching
   - Set up monitoring and logging

3. **Testing**:
   - Run full test suite: `pytest`
   - Verify security tests pass: `pytest -m security`
   - Run performance benchmarks: `pytest -m performance`

### Example Production Deployment

```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```