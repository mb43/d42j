@echo off
REM d42j Frontend Startup Script for Windows
REM Double-click this file to start the frontend dashboard

echo ========================================
echo d42j Frontend Dashboard - Starting...
echo ========================================
echo.

REM Change to frontend directory
cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Node modules not found. Installing dependencies...
    echo This may take a few minutes...
    echo.
    call npm install
    if errorlevel 1 (
        echo.
        echo Installation failed!
        pause
        exit /b 1
    )
)

REM Start the frontend
echo Starting development server...
echo Dashboard will open at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

call npm start

REM If npm exits, show message
echo.
echo Frontend dashboard stopped.
pause
