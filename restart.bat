@echo off
echo ============================================================
echo  BLISSFUL ABODES - Restarting Server
echo ============================================================
echo.

REM Navigate to the application directory
cd /d "%~dp0"

echo Current directory: %CD%
echo.
echo Stopping any existing Flask processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq run.py*" >nul 2>&1

echo.
echo Starting server with fixed dashboard features...
echo.
echo ============================================================

REM Start the Flask application
python run.py

REM If python doesn't work, try py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Python not found, trying 'py' command...
    py run.py
)

REM If both fail
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not start server!
    echo Please make sure Python is installed and in your PATH.
    echo.
    echo Try running manually:
    echo   python run.py
    echo.
    pause
)
