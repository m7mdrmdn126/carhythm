# Career DNA Assessment - Testing Guide

## Overview

This document provides comprehensive testing instructions for the Career DNA Assessment application. The test suite includes unit tests, integration tests, performance tests, and security tests to ensure the application is robust, secure, and performs well under various conditions.

## Test Structure

```
tests/
├── conftest.py                 # Main pytest configuration and fixtures
├── pytest.ini                 # Pytest configuration settings
├── requirements-test.txt       # Testing dependencies
├── fixtures/
│   ├── __init__.py
│   ├── conftest.py            # Shared fixtures
│   ├── sample_data.py         # Test data fixtures
│   └── test_utils.py          # Testing utilities and helpers
├── unit/
│   ├── __init__.py
│   ├── test_utils.py          # Unit tests for utility functions
│   ├── test_models.py         # Unit tests for database models
│   └── test_services.py       # Unit tests for business logic services
├── integration/
│   ├── __init__.py
│   ├── test_admin_endpoints.py    # Integration tests for admin functionality
│   └── test_student_endpoints.py # Integration tests for student examination flow
├── performance/
│   ├── __init__.py
│   └── test_performance.py    # Performance and load tests
└── security/
    ├── __init__.py
    └── test_security.py       # Security and vulnerability tests
```

## Setup and Installation

### 1. Install Testing Dependencies

```bash
# Install main application dependencies first
pip install -r requirements.txt

# Install testing dependencies
pip install -r requirements-test.txt
```

### 2. Environment Setup

The tests use a temporary SQLite database that is created and destroyed for each test session. No additional database setup is required.

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m performance    # Performance tests only
pytest -m security       # Security tests only

# Run tests in specific directories
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/
pytest tests security/
```

### Advanced Test Options

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run tests in parallel (faster execution)
pytest -n auto

# Run only failed tests from last run
pytest --lf

# Run tests and stop on first failure
pytest -x

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::TestPage::test_create_page

# Run tests with specific markers
pytest -m "not slow"     # Skip slow tests
pytest -m "database"     # Only database-related tests
pytest -m "auth"         # Only authentication tests
```

## Test Categories

### Unit Tests (`tests/unit/`)

Test individual components in isolation:

- **test_utils.py**: Tests utility functions like password hashing, validation
- **test_models.py**: Tests database models and relationships
- **test_services.py**: Tests business logic services

```bash
# Run unit tests
pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)

Test component interactions and full workflows:

- **test_admin_endpoints.py**: Tests admin authentication, CRUD operations, file uploads
- **test_student_endpoints.py**: Tests complete examination flow, answer submission, student info collection

```bash
# Run integration tests
pytest tests/integration/ -v
```

### Performance Tests (`tests/performance/`)

Test application performance under various conditions:

- Load time tests for critical pages
- Concurrent request handling
- Memory usage monitoring
- Database query performance benchmarks

```bash
# Run performance tests (these may take longer)
pytest tests/performance/ -v -m slow
```

### Security Tests (`tests/security/`)

Test security vulnerabilities and protections:

- SQL injection protection
- XSS (Cross-Site Scripting) protection
- Authentication and authorization
- Input validation
- File upload security
- Session management security

```bash
# Run security tests
pytest tests/security/ -v -m security
```

## Test Configuration

### pytest.ini

The `pytest.ini` file contains test configuration:

- Test discovery patterns
- Coverage settings (minimum 80% coverage required)
- Markers for test categorization
- Output formatting options

### Coverage Requirements

- Minimum coverage: 80%
- Coverage reports generated in `htmlcov/` directory
- Coverage excludes test files and migration scripts

### Test Markers

Tests are marked with categories for selective execution:

- `unit`: Individual component tests
- `integration`: Component interaction tests
- `slow`: Long-running tests (performance, load tests)
- `database`: Tests requiring database operations
- `auth`: Authentication/authorization tests
- `admin`: Admin functionality tests
- `student`: Student/examination functionality tests
- `api`: API endpoint tests
- `security`: Security vulnerability tests

## Test Data and Fixtures

### Fixtures (tests/fixtures/)

Reusable test components:

- **Database fixtures**: Temporary test database setup/teardown
- **Authentication fixtures**: Pre-authenticated admin clients
- **Data fixtures**: Sample pages, questions, student responses
- **Mock fixtures**: Mock file uploads and external dependencies

### Sample Data

The test suite includes comprehensive sample data:

- Sample pages with different configurations
- Essay and slider questions with various settings
- Student responses with realistic data
- File upload scenarios

## Continuous Integration

The test suite is designed to run in CI/CD environments:

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Performance Benchmarks

Expected performance thresholds:

- Homepage load time: < 1.0 seconds
- Admin dashboard load time: < 2.0 seconds
- Examination page load time: < 1.5 seconds
- Answer submission time: < 0.5 seconds
- Results page with 20 responses: < 3.0 seconds

## Security Test Coverage

Security tests cover:

- **Input Validation**: SQL injection, XSS, path traversal
- **Authentication**: Brute force protection, session management
- **Authorization**: Access control, privilege escalation
- **Data Protection**: Data isolation, secure storage
- **File Upload**: Malicious file detection, type validation
- **Rate Limiting**: Protection against DoS attacks

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're in the project root directory
   cd career-dna-assessment
   # Install dependencies
   pip install -r requirements.txt -r requirements-test.txt
   ```

2. **Database Errors**
   ```bash
   # Clear any existing test databases
   rm -f test_*.db
   # Ensure proper permissions
   chmod 755 tests/
   ```

3. **Coverage Issues**
   ```bash
   # Run tests with coverage debugging
   pytest --cov=app --cov-report=term-missing -v
   ```

4. **Slow Tests**
   ```bash
   # Skip performance tests for faster development
   pytest -m "not slow"
   ```

### Debug Mode

Run tests with debugging information:

```bash
# Enable debug logging
pytest -v -s --log-cli-level=DEBUG

# Run single test with debugging
pytest -v -s tests/unit/test_models.py::TestPage::test_create_page --log-cli-level=DEBUG
```

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_*.py` for files, `test_*` for functions
2. **Use appropriate markers**: Mark tests with relevant categories
3. **Write docstrings**: Document what each test verifies
4. **Use fixtures**: Reuse existing fixtures when possible
5. **Assert meaningfully**: Include descriptive assertion messages
6. **Test edge cases**: Cover both happy path and error conditions

### Test Writing Guidelines

```python
def test_example_function():
    """Test that example_function returns expected result"""
    # Arrange
    input_data = "test input"
    expected_result = "expected output"
    
    # Act
    result = example_function(input_data)
    
    # Assert
    assert result == expected_result, f"Expected {expected_result}, got {result}"
```

## Reporting Issues

When reporting test failures:

1. Include the full test command used
2. Provide the complete error output
3. Mention your Python version and OS
4. Include relevant environment information
5. Describe steps to reproduce the issue

---

This testing guide ensures comprehensive coverage of the Career DNA Assessment application, providing confidence in its reliability, security, and performance.