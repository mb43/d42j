@echo off
REM d42j First-Time Setup Script for Windows
REM Run this once to set up the backend environment

echo ========================================
echo d42j Backend Setup for Windows
echo ========================================
echo.
echo This script will:
echo 1. Create Python virtual environment
echo 2. Install Python dependencies
echo 3. Run configuration wizard
echo.
echo Please ensure you have Python 3.9+ installed
echo and added to your PATH.
echo.
pause

REM Change to backend directory
cd /d "%~dp0"

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo.
    echo Please install Python 3.9 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo ========================================
echo Step 1: Creating virtual environment...
echo ========================================
echo.

REM Remove old venv if exists
if exist "venv\" (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo.
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

echo Virtual environment created successfully.
echo.

echo ========================================
echo Step 2: Installing dependencies...
echo ========================================
echo.

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo Dependencies installed successfully.
echo.

echo ========================================
echo Step 3: Configuration
echo ========================================
echo.
echo Now you'll configure your Device42 and Jira connections.
echo Please have the following information ready:
echo.
echo - Device42 hostname (e.g., rhmd42)
echo - Device42 username and password
echo - Jira URL (e.g., https://jira.company.com)
echo - Jira username and API token
echo.
pause

python configure.py

if errorlevel 1 (
    echo.
    echo ERROR: Configuration failed!
    echo You can run this again later with: python configure.py
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now start the backend with:
echo   start-backend.bat
echo.
echo Or manually with:
echo   venv\Scripts\activate.bat
echo   python main.py
echo.
pause
