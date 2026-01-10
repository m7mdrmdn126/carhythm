#!/usr/bin/env python3
"""
Comprehensive Test Runner with Logging
Runs all test suites and saves output to log file
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Create logs directory (relative to project root, not tests directory)
project_root = Path(__file__).parent.parent
LOGS_DIR = project_root / "tests" / "test_logs"
LOGS_DIR.mkdir(exist_ok=True)

# Create log file with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOGS_DIR / f"test_run_{timestamp}.log"

# Global log file handle
log_handle = None

def log_and_print(message):
    """Print to console and write to log file"""
    print(message)
    if log_handle:
        log_handle.write(message + "\n")
        log_handle.flush()

def print_header(text):
    """Print a formatted header"""
    log_and_print("\n" + "=" * 80)
    log_and_print(f"  {text}")
    log_and_print("=" * 80 + "\n")

def run_command(description, command):
    """Run a command and capture output"""
    log_and_print(f"\n{'='*80}")
    log_and_print(f"Running: {description}")
    log_and_print(f"Command: {' '.join(command)}")
    log_and_print(f"{'='*80}\n")
    
    # Set PYTHONPATH to current directory
    env = os.environ.copy()
    env['PYTHONPATH'] = os.getcwd()
    
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        env=env
    )
    
    log_and_print(result.stdout)
    if result.stderr:
        log_and_print("STDERR:")
        log_and_print(result.stderr)
    
    return result.returncode

def main():
    """Run all test suites"""
    global log_handle
    
    # Get project root (parent directory of tests/)
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    
    # Use pytest from virtual environment
    pytest_cmd = project_root / ".venv" / "bin" / "pytest"
    if not pytest_cmd.exists():
        pytest_cmd = "pytest"  # Fallback to system pytest
    else:
        pytest_cmd = str(pytest_cmd)
    
    log_and_print(f"\nProject root: {project_root}")
    log_and_print(f"Pytest command: {pytest_cmd}")
    log_and_print(f"Log file: {LOG_FILE}\n")
    
    # Open log file
    with open(LOG_FILE, 'w', encoding='utf-8') as log_handle:
        print_header("COMPREHENSIVE TEST SUITE EXECUTION")
        
        log_and_print(f"Starting test execution at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        log_and_print(f"Working directory: {os.getcwd()}")
        log_and_print(f"Python version: {sys.version}")
        
        # Test suites to run
        test_suites = [
            ("Unit Tests - Models", [pytest_cmd, "tests/unit/test_models.py", "-v", "--tb=short"]),
            ("Unit Tests - Services", [pytest_cmd, "tests/unit/test_services_complete.py", "-v", "--tb=short"]),
            ("Unit Tests - Utils", [pytest_cmd, "tests/unit/test_utils_comprehensive.py", "-v", "--tb=short"]),
            ("Integration Tests - Routers", [pytest_cmd, "tests/integration/test_routers_comprehensive.py", "-v", "--tb=short"]),
            ("Integration Tests - Workflows", [pytest_cmd, "tests/integration/test_workflows_complete.py", "-v", "--tb=short"]),
            ("Security Tests", [pytest_cmd, "tests/security/", "-v", "--tb=short"]),
            ("Performance Tests", [pytest_cmd, "tests/performance/test_performance_comprehensive.py", "-v", "--tb=short"]),
            ("All Tests with Coverage", [pytest_cmd, "tests/", "-v", "--cov=app", "--cov-report=html", "--cov-report=term"])
        ]
        
        results = {}
        
        for description, command in test_suites:
            returncode = run_command(description, command)
            results[description] = "PASSED" if returncode == 0 else "FAILED"
        
        # Print summary
        print_header("TEST EXECUTION SUMMARY")
        
        log_and_print(f"\nCompleted at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for suite, status in results.items():
            status_symbol = "✓" if status == "PASSED" else "✗"
            log_and_print(f"{status_symbol} {suite}: {status}")
        
        # Count results
        passed = sum(1 for s in results.values() if s == "PASSED")
        failed = sum(1 for s in results.values() if s == "FAILED")
        
        log_and_print(f"\nTotal: {passed} passed, {failed} failed out of {len(results)} suites")
        log_and_print(f"\nDetailed logs saved to: {LOG_FILE}")
        
        # Check coverage report
        coverage_report = os.path.join(project_root, "htmlcov", "index.html")
        if os.path.exists(coverage_report):
            log_and_print(f"Coverage report: {coverage_report}")
        
        print_header("END OF TEST EXECUTION")
        
        # Exit with error if any test suite failed
        if failed > 0:
            sys.exit(1)

if __name__ == "__main__":
    main()
