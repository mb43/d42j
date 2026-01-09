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
echo 4. Install dependencies from scratch
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
echo Step 5: Installing dependencies...
echo ========================================

REM Install one by one to see which fails
echo Installing fastapi...
pip install --no-cache-dir fastapi==0.103.0
if errorlevel 1 goto install_failed

echo Installing uvicorn...
pip install --no-cache-dir uvicorn==0.23.0
if errorlevel 1 goto install_failed

echo Installing requests...
pip install --no-cache-dir requests==2.31.0
if errorlevel 1 goto install_failed

echo Installing pydantic...
pip install --no-cache-dir pydantic==1.10.13
if errorlevel 1 goto install_failed

echo Installing python-dotenv...
pip install --no-cache-dir python-dotenv==1.0.0
if errorlevel 1 goto install_failed

echo Installing cryptography...
pip install --no-cache-dir cryptography==41.0.7
if errorlevel 1 (
    echo WARNING: cryptography failed, trying binary-only...
    pip install --no-cache-dir --only-binary cryptography cryptography==41.0.7
    if errorlevel 1 goto install_failed
)

echo Installing jira...
pip install --no-cache-dir jira==3.5.2
if errorlevel 1 goto install_failed

echo Installing python-dateutil...
pip install --no-cache-dir python-dateutil==2.8.2
if errorlevel 1 goto install_failed

echo Installing cachetools...
pip install --no-cache-dir cachetools==5.3.2
if errorlevel 1 goto install_failed

echo Installing pyyaml...
pip install --no-cache-dir pyyaml==6.0.1
if errorlevel 1 goto install_failed

echo.
echo ========================================
echo Step 6: Verifying installation...
echo ========================================

python -c "import fastapi; print('fastapi OK')"
python -c "import uvicorn; print('uvicorn OK')"
python -c "import pydantic; print('pydantic version:', pydantic.VERSION)"
python -c "from models.asset import Asset; print('models OK')"

if errorlevel 1 (
    echo.
    echo ERROR: Verification failed!
    echo There may be an issue with the code files.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now run configuration:
echo   python configure.py
echo.
echo Then start the server:
echo   python main.py
echo.
pause
exit /b 0

:install_failed
echo.
echo ========================================
echo ERROR: Installation failed!
echo ========================================
echo.
echo The package installation failed.
echo.
echo Try these solutions:
echo 1. Run: fix-zscaler.bat (if using ZScaler)
echo 2. Disable antivirus temporarily
echo 3. Run Command Prompt as Administrator
echo.
pause
exit /b 1
