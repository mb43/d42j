@echo off
REM d42j Backend Startup Script for Windows
REM Double-click this file to start the backend API

echo ========================================
echo d42j Backend API - Starting...
echo ========================================
echo.

REM Change to backend directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run setup-windows.bat first.
    echo.
    pause
    exit /b 1
)

REM Check if config exists
if not exist "config.json" (
    echo Configuration file not found.
    echo Running first-time configuration...
    echo.
    call venv\Scripts\activate.bat
    python configure.py
    if errorlevel 1 (
        echo.
        echo Configuration failed!
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Start the backend
echo Starting backend API...
echo API will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py

REM If Python exits, show message
echo.
echo Backend API stopped.
pause
