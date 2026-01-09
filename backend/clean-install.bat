@echo off
REM Complete clean reinstall for d42j backend
REM Use this when you get persistent errors

echo ========================================
echo d42j Backend - Complete Clean Reinstall
echo ========================================
echo.
echo This will:
echo 1. Delete virtual environment
echo 2. Clear Python cache files
echo 3. Create fresh virtual environment
echo 4. Install dependencies from requirements.txt
echo.
echo Press Ctrl+C to cancel, or
pause

cd /d "%~dp0"

echo.
echo ========================================
echo Step 1: Cleaning up old files...
echo ========================================

REM Remove virtual environment
if exist "venv\" (
    echo Removing virtual environment...
    rmdir /s /q venv
)

REM Remove Python cache
echo Removing Python cache files...
for /d /r %%i in (__pycache__) do @if exist "%%i" rmdir /s /q "%%i"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

REM Clear pip cache
echo Clearing pip cache...
pip cache purge 2>nul

echo.
echo ========================================
echo Step 2: Creating fresh virtual environment...
echo ========================================

python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 3: Activating environment...
echo ========================================

call venv\Scripts\activate.bat

echo.
echo ========================================
echo Step 4: Upgrading pip...
echo ========================================

python -m pip install --upgrade pip --no-cache-dir

echo.
echo ========================================
echo Step 5: Installing dependencies from requirements.txt...
echo ========================================

pip install --no-cache-dir -r requirements.txt

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Installation failed!
    echo ========================================
    echo.
    echo Try these solutions:
    echo 1. Run: ..\fix-zscaler.bat (if using ZScaler)
    echo 2. Disable antivirus temporarily
    echo 3. Run Command Prompt as Administrator
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 6: Verifying installation...
echo ========================================

python -c "import fastapi; print('fastapi version:', fastapi.__version__)"
python -c "import uvicorn; print('uvicorn OK')"
python -c "import pydantic; print('pydantic version:', pydantic.VERSION)"

if errorlevel 1 (
    echo.
    echo ERROR: Basic imports failed!
    pause
    exit /b 1
)

echo.
echo Testing models...
python -c "from models.asset import Asset, AssetType; print('models import OK')"

if errorlevel 1 (
    echo.
    echo ERROR: Model import failed!
    echo.
    echo This might be a code issue. Check the error above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installed versions:
pip list | findstr "fastapi pydantic uvicorn"
echo.
echo Now run configuration:
echo   python configure.py
echo.
echo Then start the server:
echo   python main.py
echo.
pause
exit /b 0
