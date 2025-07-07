@echo off
title LoRA the Explorer - Installation

echo.
echo ===============================================
echo    LoRA the Explorer - Installation
echo ===============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] PYTHON NOT FOUND
    echo.
    echo LoRA the Explorer requires Python 3.8 or higher to run.
    echo.
    echo NEXT STEPS:
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, CHECK "Add Python to PATH"
    echo 3. Restart your computer after installation
    echo 4. Run this installer again
    echo.
    echo IMPORTANT: You MUST check "Add Python to PATH" during installation
    echo or this installer will not work.
    echo.
    pause
    exit /b 1
)

echo [OK] Python found
python --version
echo.

echo Starting installation...
echo This will create a virtual environment and install all dependencies
echo.

REM Run the installer
python install.py

echo.
if errorlevel 1 (
    echo [ERROR] Installation failed!
    echo.
    echo Please check the error messages above and try again.
    echo If problems persist, please report the issue.
    echo.
) else (
    echo [SUCCESS] Installation completed successfully!
    echo.
    echo You can now launch LoRA the Explorer by:
    echo   - Double-clicking start_gui.bat
    echo   - Or running: python lora_algebra_gui.py
    echo.
)

echo Press any key to close this window...
pause >nul