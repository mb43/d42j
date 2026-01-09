@echo off
REM Quick test script to verify models load correctly

cd /d "%~dp0"

if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Run setup-windows.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Testing model imports...
echo.

python -c "print('Testing pydantic version...')"
python -c "import pydantic; print('Pydantic version:', pydantic.VERSION)"

echo.
python -c "print('Testing Asset model...')"
python -c "from models.asset import Asset, AssetType, RiskLevel; print('Asset import OK')"

echo.
python -c "print('Creating test asset...')"
python -c "from models.asset import Asset, AssetType, RiskLevel; a = Asset(id='test', name='test', hostname='test', asset_type=AssetType.PHYSICAL_SERVER); print('Asset created OK:', a.hostname)"

echo.
python -c "print('Testing RiskAssessment model...')"
python -c "from models.asset import RiskAssessment, RiskLevel; r = RiskAssessment(asset_id='1', asset_name='test', hostname='test', risk_score=50.0, risk_level=RiskLevel.MEDIUM, factors={}, recommendations=[]); print('RiskAssessment created OK')"

if errorlevel 1 (
    echo.
    echo ========================================
    echo TESTS FAILED!
    echo ========================================
    echo There is a problem with the models.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ALL TESTS PASSED!
echo ========================================
echo Models are working correctly.
echo.
pause
