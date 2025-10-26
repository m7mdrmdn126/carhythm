@echo off
REM Database Population Script for Career DNA Assessment
REM This script populates the database with realistic fake data

echo Career DNA Assessment - Database Population
echo ==========================================

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo Error: Virtual environment not found.
    echo Please make sure you're in the correct directory and the virtual environment is set up.
    pause
    exit /b 1
)

REM Check if Faker is installed
".venv\Scripts\python.exe" -c "import faker" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required package: faker
    ".venv\Scripts\python.exe" -m pip install faker
    if %errorlevel% neq 0 (
        echo Error: Failed to install faker package
        pause
        exit /b 1
    )
)

REM Run the population script in auto mode
echo.
echo Running database population script in automatic mode...
echo This will clear existing data and create 25 sample responses.
echo.
".venv\Scripts\python.exe" populate_db.py --auto --responses=25

if %errorlevel% equ 0 (
    echo.
    echo [92mDatabase population completed successfully![0m
) else (
    echo.
    echo [91mError occurred during database population[0m
)

echo.
echo Press any key to exit...
pause >nul