@echo off
echo ======================================
echo CardioPredict Application Launcher
echo ======================================
echo.
echo Starting application...
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed or not in your PATH.
    echo Please install Python 3.7 or higher and try again.
    pause
    exit /b 1
)

:: Launch the application using the launcher script
python run_app.py

:: If the application exits, wait before closing
echo.
echo Application has closed. Press any key to exit...
pause > nul