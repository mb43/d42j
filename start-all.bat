@echo off
REM d42j Complete Startup Script for Windows
REM Starts BOTH backend and frontend in separate windows

echo ========================================
echo d42j Infrastructure Risk Management
echo Starting Backend and Frontend...
echo ========================================
echo.

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Start backend in new window
echo Starting Backend API in new window...
start "d42j Backend API" cmd /k "cd /d "%SCRIPT_DIR%backend" && start-backend.bat"

REM Wait a few seconds for backend to initialize
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend Dashboard in new window...
start "d42j Frontend Dashboard" cmd /k "cd /d "%SCRIPT_DIR%frontend" && start-frontend.bat"

echo.
echo ========================================
echo Both services are starting...
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Backend Docs: http://localhost:8000/docs
echo Frontend Dashboard: http://localhost:3000
echo.
echo Two new windows have been opened.
echo Close those windows to stop the services.
echo.
pause
