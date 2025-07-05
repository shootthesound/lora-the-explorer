@echo off
title LoRA the Explorer - Update

echo.
echo ===============================================
echo    LoRA the Explorer - Update
echo ===============================================
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Check if git is available
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] GIT NOT FOUND
    echo.
    echo Git is required to update LoRA the Explorer.
    echo.
    echo NEXT STEPS:
    echo 1. Download Git from: https://git-scm.com/download/win
    echo 2. Install Git with default settings
    echo 3. Restart your computer after installation
    echo 4. Run this updater again
    echo.
    pause
    exit /b 1
)

echo [OK] Git found
git --version
echo.

REM Check if we're in a git repository
git status >nul 2>&1
if errorlevel 1 (
    echo [ERROR] NOT A GIT REPOSITORY
    echo.
    echo This directory is not a git repository.
    echo Cannot perform update.
    echo.
    pause
    exit /b 1
)

echo [OK] Git repository detected
echo.

echo Checking for updates...
echo.

REM Fetch latest changes
git fetch
if errorlevel 1 (
    echo [ERROR] Failed to fetch updates from remote repository
    echo.
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

REM Check if there are updates available
git status -uno | findstr "Your branch is behind" >nul
if errorlevel 1 (
    echo [INFO] Already up to date!
    echo No updates available.
    echo.
) else (
    echo [INFO] Updates available. Pulling changes...
    echo.
    
    REM Pull the latest changes
    git pull
    if errorlevel 1 (
        echo [ERROR] Failed to pull updates
        echo.
        echo There may be local changes conflicting with the update.
        echo Please resolve any conflicts manually or contact support.
        echo.
    ) else (
        echo [SUCCESS] Update completed successfully!
        echo.
        echo Latest changes have been applied to your LoRA the Explorer installation.
        echo.
    )
)

echo Press any key to close this window...
pause >nul