#!/bin/bash

# Career DNA Assessment - Test Runner Script
# This script provides convenient commands for running different types of tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${1}${2}${NC}\n"
}

print_header() {
    echo "=================================="
    print_color $BLUE "$1"
    echo "=================================="
}

# Check if pytest is installed
check_pytest() {
    if ! command -v pytest &> /dev/null; then
        print_color $RED "Error: pytest not found. Please install test dependencies:"
        echo "pip install -r requirements-test.txt"
        exit 1
    fi
}

# Show help
show_help() {
    echo "Career DNA Assessment - Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  all           Run all tests"
    echo "  unit          Run unit tests only"
    echo "  integration   Run integration tests only"
    echo "  performance   Run performance tests only"
    echo "  security      Run security tests only"
    echo "  coverage      Run tests with coverage report"
    echo "  fast          Run tests excluding slow performance tests"
    echo "  watch         Run tests in watch mode (auto-rerun on changes)"
    echo "  clean         Clean test artifacts and cache"
    echo "  install       Install test dependencies"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 all                    # Run complete test suite"
    echo "  $0 unit                   # Run only unit tests"
    echo "  $0 coverage               # Run tests with coverage report"
    echo "  $0 fast                   # Quick test run (skip slow tests)"
}

# Install test dependencies
install_deps() {
    print_header "Installing Test Dependencies"
    
    if [ -f "requirements.txt" ]; then
        print_color $YELLOW "Installing main dependencies..."
        pip install -r requirements.txt
    fi
    
    if [ -f "requirements-test.txt" ]; then
        print_color $YELLOW "Installing test dependencies..."
        pip install -r requirements-test.txt
    else
        print_color $RED "Error: requirements-test.txt not found"
        exit 1
    fi
    
    print_color $GREEN "Dependencies installed successfully!"
}

# Clean test artifacts
clean_tests() {
    print_header "Cleaning Test Artifacts"
    
    # Remove pytest cache
    if [ -d ".pytest_cache" ]; then
        rm -rf .pytest_cache
        print_color $YELLOW "Removed .pytest_cache/"
    fi
    
    # Remove coverage files
    if [ -f ".coverage" ]; then
        rm .coverage
        print_color $YELLOW "Removed .coverage"
    fi
    
    if [ -d "htmlcov" ]; then
        rm -rf htmlcov
        print_color $YELLOW "Removed htmlcov/"
    fi
    
    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    print_color $YELLOW "Removed __pycache__ directories"
    
    # Remove test databases
    find . -name "test_*.db" -delete 2>/dev/null || true
    print_color $YELLOW "Removed test databases"
    
    print_color $GREEN "Cleanup completed!"
}

# Run all tests
run_all_tests() {
    print_header "Running All Tests"
    check_pytest
    pytest -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ All tests passed!"
    else
        print_color $RED "❌ Some tests failed!"
        exit 1
    fi
}

# Run unit tests
run_unit_tests() {
    print_header "Running Unit Tests"
    check_pytest
    pytest tests/unit/ -v -m unit
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Unit tests passed!"
    else
        print_color $RED "❌ Unit tests failed!"
        exit 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_header "Running Integration Tests"
    check_pytest
    pytest tests/integration/ -v -m integration
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Integration tests passed!"
    else
        print_color $RED "❌ Integration tests failed!"
        exit 1
    fi
}

# Run performance tests
run_performance_tests() {
    print_header "Running Performance Tests"
    print_color $YELLOW "Note: Performance tests may take several minutes to complete"
    check_pytest
    pytest tests/performance/ -v -m performance
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Performance tests passed!"
    else
        print_color $RED "❌ Performance tests failed!"
        exit 1
    fi
}

# Run security tests
run_security_tests() {
    print_header "Running Security Tests"
    check_pytest
    pytest tests/security/ -v -m security
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Security tests passed!"
    else
        print_color $RED "❌ Security tests failed!"
        exit 1
    fi
}

# Run tests with coverage
run_coverage_tests() {
    print_header "Running Tests with Coverage Report"
    check_pytest
    pytest --cov=app --cov-report=html --cov-report=term-missing -v
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Tests passed! Coverage report generated in htmlcov/"
        if command -v open &> /dev/null; then
            print_color $BLUE "Opening coverage report in browser..."
            open htmlcov/index.html
        elif command -v xdg-open &> /dev/null; then
            print_color $BLUE "Opening coverage report in browser..."
            xdg-open htmlcov/index.html
        fi
    else
        print_color $RED "❌ Tests failed!"
        exit 1
    fi
}

# Run fast tests (excluding slow ones)
run_fast_tests() {
    print_header "Running Fast Tests (Excluding Slow Tests)"
    check_pytest
    pytest -v -m "not slow" --tb=short
    
    if [ $? -eq 0 ]; then
        print_color $GREEN "✅ Fast tests passed!"
    else
        print_color $RED "❌ Some tests failed!"
        exit 1
    fi
}

# Run tests in watch mode
run_watch_tests() {
    print_header "Running Tests in Watch Mode"
    check_pytest
    
    if ! command -v pytest-watch &> /dev/null; then
        print_color $YELLOW "Installing pytest-watch for watch mode..."
        pip install pytest-watch
    fi
    
    print_color $BLUE "Watching for file changes... Press Ctrl+C to stop"
    ptw -- --tb=short -m "not slow"
}

# Main script logic
case "${1:-help}" in
    "all")
        run_all_tests
        ;;
    "unit")
        run_unit_tests
        ;;
    "integration")
        run_integration_tests
        ;;
    "performance")
        run_performance_tests
        ;;
    "security")
        run_security_tests
        ;;
    "coverage")
        run_coverage_tests
        ;;
    "fast")
        run_fast_tests
        ;;
    "watch")
        run_watch_tests
        ;;
    "clean")
        clean_tests
        ;;
    "install")
        install_deps
        ;;
    "help"|*)
        show_help
        ;;
esac