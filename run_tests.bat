@echo off
REM Career DNA Assessment - Test Runner Script for Windows
REM This script provides convenient commands for running different types of tests

setlocal enabledelayedexpansion

REM Jump to main logic
goto main

REM Function to print colored output (simplified for Windows)
:print_header
echo.
echo ==================================
echo %~1
echo ==================================
echo.
goto :eof

:print_success
echo [92m%~1[0m
goto :eof

:print_error
echo [91m%~1[0m
goto :eof

:print_warning
echo [93m%~1[0m
goto :eof

:print_info
echo [94m%~1[0m
goto :eof

REM Check if pytest is installed
:check_pytest
"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Error: pytest not found. Please install test dependencies:"
    echo Use: .\run_tests.bat install
    exit /b 1
)
goto :eof

REM Show help
:show_help
echo Career DNA Assessment - Test Runner for Windows
echo.
echo Usage: %0 [COMMAND]
echo.
echo Commands:
echo   all           Run all tests
echo   unit          Run unit tests only
echo   integration   Run integration tests only
echo   performance   Run performance tests only
echo   security      Run security tests only
echo   coverage      Run tests with coverage report
echo   fast          Run tests excluding slow performance tests
echo   clean         Clean test artifacts and cache
echo   install       Install test dependencies
echo   help          Show this help message
echo.
echo Examples:
echo   %0 all                    # Run complete test suite
echo   %0 unit                   # Run only unit tests
echo   %0 coverage               # Run tests with coverage report
echo   %0 fast                   # Quick test run ^(skip slow tests^)
goto :eof

REM Install test dependencies
:install_deps
call :print_header "Installing Test Dependencies"

if exist "requirements.txt" (
    call :print_warning "Installing main dependencies..."
    "C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        call :print_error "Failed to install main dependencies"
        exit /b 1
    )
)

if exist "requirements-test.txt" (
    call :print_warning "Installing test dependencies..."
    "C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pip install -r requirements-test.txt
    if errorlevel 1 (
        call :print_error "Failed to install test dependencies"
        exit /b 1
    )
) else (
    call :print_error "Error: requirements-test.txt not found"
    exit /b 1
)

call :print_success "Dependencies installed successfully!"
goto :eof

REM Clean test artifacts
:clean_tests
call :print_header "Cleaning Test Artifacts"

if exist ".pytest_cache" (
    rmdir /s /q ".pytest_cache"
    call :print_warning "Removed .pytest_cache/"
)

if exist ".coverage" (
    del ".coverage"
    call :print_warning "Removed .coverage"
)

if exist "htmlcov" (
    rmdir /s /q "htmlcov"
    call :print_warning "Removed htmlcov/"
)

REM Remove __pycache__ directories
for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
call :print_warning "Removed __pycache__ directories"

REM Remove test databases
for %%f in (test_*.db) do if exist "%%f" del "%%f" 2>nul
call :print_warning "Removed test databases"

call :print_success "Cleanup completed!"
goto :eof

REM Run all tests
:run_all_tests
call :print_header "Running All Tests"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest -v --tb=short
if errorlevel 1 (
    call :print_error "❌ Some tests failed!"
    exit /b 1
) else (
    call :print_success "✅ All tests passed!"
)
goto :eof

REM Run unit tests
:run_unit_tests
call :print_header "Running Unit Tests"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest tests/unit/ -v -m unit
if errorlevel 1 (
    call :print_error "❌ Unit tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Unit tests passed!"
)
goto :eof

REM Run integration tests
:run_integration_tests
call :print_header "Running Integration Tests"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest tests/integration/ -v -m integration
if errorlevel 1 (
    call :print_error "❌ Integration tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Integration tests passed!"
)
goto :eof

REM Run performance tests
:run_performance_tests
call :print_header "Running Performance Tests"
call :print_warning "Note: Performance tests may take several minutes to complete"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest tests/performance/ -v -m performance
if errorlevel 1 (
    call :print_error "❌ Performance tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Performance tests passed!"
)
goto :eof

REM Run security tests
:run_security_tests
call :print_header "Running Security Tests"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest tests/security/ -v -m security
if errorlevel 1 (
    call :print_error "❌ Security tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Security tests passed!"
)
goto :eof

REM Run tests with coverage
:run_coverage_tests
call :print_header "Running Tests with Coverage Report"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest --cov=app --cov-report=html --cov-report=term-missing -v
if errorlevel 1 (
    call :print_error "❌ Tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Tests passed! Coverage report generated in htmlcov/"
    if exist "htmlcov/index.html" (
        call :print_info "Opening coverage report in browser..."
        start htmlcov/index.html
    )
)
goto :eof

REM Run fast tests (excluding slow ones)
:run_fast_tests
call :print_header "Running Fast Tests (Excluding Slow Tests)"
call :check_pytest
if errorlevel 1 exit /b 1

"C:\Users\pc\Desktop\Project sigma\.venv\Scripts\python.exe" -m pytest -v -m "not slow" --tb=short
if errorlevel 1 (
    call :print_error "❌ Some tests failed!"
    exit /b 1
) else (
    call :print_success "✅ Fast tests passed!"
)
goto :eof

REM Main script entry point
:main
if "%1"=="" goto show_help
if "%1"=="help" goto show_help
if "%1"=="all" goto run_all_tests
if "%1"=="unit" goto run_unit_tests
if "%1"=="integration" goto run_integration_tests
if "%1"=="performance" goto run_performance_tests
if "%1"=="security" goto run_security_tests
if "%1"=="coverage" goto run_coverage_tests
if "%1"=="fast" goto run_fast_tests
if "%1"=="clean" goto clean_tests
if "%1"=="install" goto install_deps

REM If we get here, unknown command
echo Unknown command: %1
echo.
goto show_help