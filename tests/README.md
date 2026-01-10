# CaRhythm Test Suite Documentation

## Overview

Comprehensive testing suite for the CaRhythm Career DNA Assessment System covering unit tests, integration tests, security tests, and performance tests.

## Test Structure

```
tests/
├── conftest.py                          # Shared fixtures and test configuration
├── unit/                                # Unit tests for individual components
│   ├── test_models.py                   # Database model tests
│   ├── test_services_complete.py        # Service layer tests
│   └── test_utils_comprehensive.py      # Utility function tests
├── integration/                         # Integration tests
│   ├── test_routers_comprehensive.py    # API endpoint tests
│   ├── test_workflows_complete.py       # End-to-end workflow tests
│   ├── test_admin_comprehensive.py      # Admin panel integration tests
│   ├── test_student_comprehensive.py    # Student exam integration tests
│   └── test_question_pool_comprehensive.py  # Question pool tests
├── security/                            # Security and authentication tests
│   └── test_security_comprehensive.py   # Auth, permissions, validation tests
└── performance/                         # Performance and load tests
    └── test_performance_comprehensive.py # Speed, concurrency, scalability tests
```

## Test Coverage

### Unit Tests (tests/unit/)

#### Models (`test_models.py`)
- ✅ Admin model creation and validation
- ✅ Page model with relationships
- ✅ Question model (all types: essay, slider, MCQ, ordering)
- ✅ StudentResponse model with session tracking
- ✅ QuestionAnswer model with polymorphic answers
- ✅ Category and QuestionPool models
- ✅ QuestionPageAssignment relationships
- ✅ ImportLog tracking
- ✅ Cascade delete behaviors
- ✅ Unique constraints and validations

#### Services (`test_services_complete.py`)
- ✅ **Authentication Service**: admin creation, login, password verification
- ✅ **Question Service**: CRUD operations for pages and questions
- ✅ **Response Service**: session management, answer submission
- ✅ **Scoring Service**: RIASEC, Big Five, behavioral calculations
- ✅ **PDF Service**: report generation, chart creation, archetype data
- ✅ **Email Service**: results emails, admin notifications
- ✅ **Question Pool Service**: category management, pool CRUD
- ✅ **CSV Import Service**: validation, import, export operations

#### Utilities (`test_utils_comprehensive.py`)
- ✅ Password hashing and verification
- ✅ JWT token creation and validation
- ✅ Session ID generation
- ✅ Date/time formatting
- ✅ Image validation
- ✅ File upload handling

### Integration Tests (tests/integration/)

#### API Routers (`test_routers_comprehensive.py`)
- ✅ **Admin Authentication**: login, logout, session management
- ✅ **Page Management**: list, create, update, delete, reorder
- ✅ **Question Management**: all question types CRUD
- ✅ **Response Management**: view, filter, export, delete
- ✅ **Category Management**: CRUD operations
- ✅ **Question Pool**: dashboard, filters, assignments
- ✅ **CSV Operations**: import/export, templates
- ✅ **Analytics**: dashboard, charts, statistics
- ✅ **API v2**: REST endpoints for React frontend
- ✅ **Feedback**: submission and viewing
- ✅ **Settings**: admin configuration

#### Workflows (`test_workflows_complete.py`)
- ✅ **Complete Student Journey**: welcome → exam → answers → results
- ✅ **Complete Admin Workflow**: login → create pages → create questions → view responses
- ✅ **Question Pool Workflow**: create → assign to page → track usage
- ✅ **CSV Round-trip**: import CSV → modify → export CSV
- ✅ **Scoring & PDF**: calculate scores → save → generate PDF
- ✅ **API v2 Workflow**: session → questions → submit → complete
- ✅ **Feedback Workflow**: student submit → admin view
- ✅ **Multiple Students**: concurrent sessions with unique IDs
- ✅ **Error Handling**: invalid sessions, missing fields, duplicates

### Security Tests (tests/security/)

- ✅ Password hashing strength
- ✅ Authentication bypass prevention
- ✅ Authorization checks
- ✅ SQL injection prevention
- ✅ XSS prevention
- ✅ CSRF protection
- ✅ Session management security
- ✅ Input validation
- ✅ File upload security

### Performance Tests (tests/performance/)

- ✅ **Database Performance**: bulk queries, large datasets, joins
- ✅ **API Performance**: response times for all major endpoints
- ✅ **Scoring Performance**: calculation speed for all algorithms
- ✅ **PDF Generation**: report creation performance
- ✅ **Concurrent Operations**: multiple sessions, parallel submissions
- ✅ **Memory Usage**: large dataset handling
- ✅ **Caching Efficiency**: repeated queries, eager loading
- ✅ **Scalability**: pagination, filtered queries

## Running Tests

### Run All Tests
```bash
# Full test suite with coverage
python run_all_tests.py

# Or using pytest directly
pytest tests/ -v --cov=app --cov-report=html
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Security tests only
pytest tests/security/ -v

# Performance tests only
pytest tests/performance/ -v

# Specific test file
pytest tests/unit/test_models.py -v

# Specific test class
pytest tests/unit/test_models.py::TestPageModel -v

# Specific test function
pytest tests/unit/test_models.py::TestPageModel::test_page_creation -v
```

### Run with Coverage

```bash
# HTML coverage report
pytest tests/ --cov=app --cov-report=html

# Terminal coverage report
pytest tests/ --cov=app --cov-report=term

# Coverage for specific module
pytest tests/unit/ --cov=app.services --cov-report=term
```

### Run with Different Output Formats

```bash
# Verbose output
pytest tests/ -v

# Quiet output
pytest tests/ -q

# Stop on first failure
pytest tests/ -x

# Show print statements
pytest tests/ -s

# Run last failed tests
pytest tests/ --lf

# Show slowest tests
pytest tests/ --durations=10
```

## Test Fixtures

Key fixtures available in `conftest.py`:

### Database Fixtures
- `test_db` - Temporary test database (session scope)
- `db_session` - Database session for each test

### Model Fixtures
- `test_admin` - Admin user
- `test_page` - Test page
- `test_essay_question` - Essay question
- `test_slider_question` - Slider question
- `test_mcq_question` - Multiple choice question
- `test_ordering_question` - Ordering question
- `test_student_response` - Student response with session
- `test_category` - Question category
- `test_question_pool` - Question in pool
- `test_question_pool_mcq` - MCQ in pool
- `test_question_pool_slider` - Slider in pool
- `test_question_pool_ordering` - Ordering in pool

### Client Fixtures
- `client` - Test client for API calls
- `authenticated_admin_client` - Client with admin session

### Data Fixtures
- `sample_questions_data` - Sample question JSON
- `sample_student_data` - Sample student info
- `multiple_pages` - 3 test pages
- `multiple_categories` - 3 test categories

## Writing New Tests

### Test Structure
```python
class TestYourFeature:
    """Test description"""
    
    def test_specific_behavior(self, fixture1, fixture2):
        """Test a specific behavior"""
        # Arrange
        data = {"key": "value"}
        
        # Act
        result = function_to_test(data)
        
        # Assert
        assert result is not None
        assert result.key == "value"
```

### Using Fixtures
```python
def test_with_database(self, db_session, test_page):
    """Test using database fixtures"""
    from app.models import Question
    
    question = Question(
        page_id=test_page.id,
        question_text="Test",
        question_type="essay"
    )
    db_session.add(question)
    db_session.commit()
    
    assert question.id is not None
```

### Testing API Endpoints
```python
def test_endpoint(self, authenticated_admin_client):
    """Test an API endpoint"""
    response = authenticated_admin_client.get("/admin/dashboard")
    assert response.status_code == 200
    
    response = authenticated_admin_client.post("/admin/pages", data={
        "title": "New Page",
        "description": "Test"
    })
    assert response.status_code == 302
```

## Coverage Reports

After running tests with coverage:
1. Open `htmlcov/index.html` in a browser
2. Review coverage percentages for each module
3. Click on files to see line-by-line coverage
4. Focus on improving coverage for critical modules

Target Coverage:
- Models: 95%+
- Services: 90%+
- Routers: 85%+
- Utils: 95%+

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ --cov=app --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Test Data Cleanup

All tests use temporary databases and clean up after themselves:
- Session-scoped database created at start
- Each test gets its own session
- Database deleted after test suite completes
- No pollution between tests

## Debugging Tests

### View detailed output
```bash
pytest tests/unit/test_models.py::TestPageModel::test_page_creation -vv -s
```

### Debug with breakpoint
```python
def test_something(self):
    import pdb; pdb.set_trace()
    # Test code here
```

### Show local variables on failure
```bash
pytest tests/ --showlocals
```

## Common Issues

### Import Errors
- Ensure you're in the project root
- Activate virtual environment
- Install test dependencies: `pip install -r requirements-test.txt`

### Database Locked
- Close any SQLite browser tools
- Kill any hanging Python processes
- Delete test database files manually if needed

### Fixture Not Found
- Check `conftest.py` for fixture definition
- Ensure fixture name is spelled correctly
- Check fixture scope matches usage

## Test Maintenance

- Update tests when adding new features
- Keep test data realistic but minimal
- Use factories for complex object creation
- Mock external services (email, etc.)
- Keep tests independent and isolated
- Aim for fast test execution

## Performance Benchmarks

Expected test execution times:
- Unit tests: < 10 seconds
- Integration tests: < 30 seconds
- Security tests: < 15 seconds
- Performance tests: < 45 seconds
- Full suite: < 2 minutes

## Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add docstrings to test classes and functions
3. Group related tests in classes
4. Use appropriate fixtures
5. Ensure tests are independent
6. Add coverage for edge cases
7. Update this README if needed

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Coverage.py](https://coverage.readthedocs.io/)
