#!/usr/bin/env python3
"""
Update Launcher Scripts for LoRA the Explorer

This script regenerates the launcher scripts (start_gui.bat/start_gui.sh) 
after updates to ensure users get the latest launcher improvements.
"""

import os
import sys
import platform
from pathlib import Path

def get_python_executable():
    """Get the path to Python executable in virtual environment"""
    if platform.system() == "Windows":
        return Path("env") / "Scripts" / "python.exe"
    else:
        return Path("env") / "bin" / "python"

def create_launcher_scripts():
    """Create launcher scripts for easy access"""
    python_exe = get_python_executable()
    
    # Check if virtual environment exists
    if not python_exe.exists():
        print(f"[ERROR] Virtual environment not found at: {python_exe}")
        print("Please run install.py first to set up the environment.")
        return False
    
    if platform.system() == "Windows":
        # Windows batch file
        launcher_content = f"""@echo off
setlocal EnableDelayedExpansion
echo  Launching LoRA the Explorer GUI...
echo.

REM Check for updates if git is available (non-blocking)
git --version >nul 2>&1
if not errorlevel 1 (
    git status >nul 2>&1
    if not errorlevel 1 (
        echo [INFO] Checking for updates...
        git fetch >nul 2>&1
        if not errorlevel 1 (
            REM Check if we have an upstream branch configured
            git rev-parse --abbrev-ref @{{u}} >nul 2>&1
            if not errorlevel 1 (
                REM Count commits behind using rev-list
                for /f %%i in ('git rev-list --count HEAD..@{{u}} 2^>nul') do set BEHIND_COUNT=%%i
                if not "!BEHIND_COUNT!"=="0" if not "!BEHIND_COUNT!"=="" (
                    echo.
                    echo ===============================================
                    echo    UPDATE AVAILABLE!
                    echo ===============================================
                    echo.
                    echo A newer version of LoRA the Explorer is available.
                    echo Run update.bat to get the latest features and fixes.
                    echo.
                    echo Press any key to continue launching the GUI...
                    pause >nul
                    echo.
                ) else (
                    echo [OK] You are running the latest version
                    echo.
                )
            ) else (
                echo [INFO] No upstream branch configured, skipping update check
                echo.
            )
        )
    )
)

echo Starting GUI...
"{python_exe.absolute()}" lora_algebra_gui.py
pause
"""
        with open("start_gui.bat", "w") as f:
            f.write(launcher_content)
        
        print("[OK] Updated Windows launcher script: start_gui.bat")
        return True
        
    else:
        # Unix shell script
        launcher_content = f"""#!/bin/bash
echo " Launching LoRA the Explorer GUI..."
echo

# Check for updates if git is available (non-blocking)
if command -v git >/dev/null 2>&1; then
    if git status >/dev/null 2>&1; then
        echo "[INFO] Checking for updates..."
        if git fetch >/dev/null 2>&1; then
            # Check if we have an upstream branch configured
            if git rev-parse --abbrev-ref @{{u}} >/dev/null 2>&1; then
                # Count commits behind using rev-list
                BEHIND_COUNT=$(git rev-list --count HEAD..@{{u}} 2>/dev/null)
                if [ "$BEHIND_COUNT" -gt 0 ] 2>/dev/null; then
                    echo
                    echo "==============================================="
                    echo "    UPDATE AVAILABLE!"
                    echo "==============================================="
                    echo
                    echo "A newer version of LoRA the Explorer is available."
                    echo "Run 'git pull' to get the latest features and fixes."
                    echo
                    echo "Press any key to continue launching the GUI..."
                    read -n 1 -s
                    echo
                else
                    echo "[OK] You are running the latest version"
                    echo
                fi
            else
                echo "[INFO] No upstream branch configured, skipping update check"
                echo
            fi
        fi
    fi
fi

echo "Starting GUI..."
"{python_exe.absolute()}" lora_algebra_gui.py
"""
        with open("start_gui.sh", "w") as f:
            f.write(launcher_content)
        os.chmod("start_gui.sh", 0o755)
        
        print("[OK] Updated Unix launcher script: start_gui.sh")
        return True

def main():
    """Main function to update launcher scripts"""
    print("Updating LoRA the Explorer launcher scripts...")
    
    try:
        success = create_launcher_scripts()
        if success:
            print("[SUCCESS] Launcher scripts updated successfully!")
        else:
            print("[ERROR] Failed to update launcher scripts")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to update launcher scripts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()