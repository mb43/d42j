@echo off
REM Fix for ZScaler SSL certificate issues on Windows
REM Run this if you get "unable to get issuer cert" errors

echo ========================================
echo ZScaler SSL Certificate Fix
echo ========================================
echo.
echo This script will configure npm and pip to work with ZScaler.
echo.
echo Choose your fix level:
echo   1. Quick fix (disable SSL verification - RECOMMENDED for internal use)
echo   2. Manual certificate setup (more secure)
echo   3. Exit
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" goto quickfix
if "%choice%"=="2" goto certfix
if "%choice%"=="3" goto end

:quickfix
echo.
echo ========================================
echo Applying Quick Fix...
echo ========================================
echo.

REM Fix npm SSL
echo Configuring npm to bypass SSL verification...
call npm config set strict-ssl false
if errorlevel 1 (
    echo WARNING: npm config failed. Is Node.js installed?
) else (
    echo npm configured successfully.
)

REM Fix pip SSL
echo.
echo Configuring pip to bypass SSL verification...
echo [global] > %APPDATA%\pip\pip.ini
echo trusted-host = pypi.org >> %APPDATA%\pip\pip.ini
echo                pypi.python.org >> %APPDATA%\pip\pip.ini
echo                files.pythonhosted.org >> %APPDATA%\pip\pip.ini
echo pip configured successfully.

echo.
echo ========================================
echo Quick Fix Applied!
echo ========================================
echo.
echo npm and pip will now work with ZScaler.
echo You can now run:
echo   - npm install
echo   - pip install -r requirements.txt
echo.
pause
goto end

:certfix
echo.
echo ========================================
echo Manual Certificate Setup
echo ========================================
echo.
echo To use ZScaler's certificate:
echo.
echo 1. Export ZScaler certificate from browser:
echo    - Open Chrome/Edge
echo    - Go to any HTTPS site
echo    - Click padlock - Certificate - Details - Copy to File
echo    - Save as zscaler.crt to your Desktop
echo.
echo 2. Run these commands:
echo    npm config set cafile "C:\Users\%USERNAME%\Desktop\zscaler.crt"
echo    pip config set global.cert "C:\Users\%USERNAME%\Desktop\zscaler.crt"
echo.
echo This is more secure than disabling SSL verification.
echo.
pause
goto end

:end
