#!/usr/bin/env python3
"""
LoRA the Explorer Installation Script

Creates a Python virtual environment and installs dependencies, similar to FluxGym.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description, check=True):
    """Run a command with nice output"""
    print(f" {description}...")
    try:
        if isinstance(command, str):
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command, check=check, capture_output=True, text=True)
        
        if result.stdout:
            print(f"    {result.stdout.strip()}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"    Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        if check:
            raise
        return e

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info

    # UPDATED: Require Python 3.10+ for PyTorch 2.7.1+, Gradio 5.49.1, and musubi-tuner
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        print("\n   Why Python 3.10+?")
        print("   • PyTorch 2.7.1+ requires Python 3.10+")
        print("   • Gradio 5.49.1 requires Python 3.10+")
        print("   • musubi-tuner (WAN 2.2 support) requires Python 3.10-3.12")
        print("\n   Note: Python 3.14 is not yet supported due to Pydantic compatibility issues")
        print("   Recommended: Python 3.10, 3.11, or 3.12")
        sys.exit(1)

    # Warn about Python 3.13+ (may have issues)
    if version.major == 3 and version.minor >= 13:
        print(f"⚠️  Python {version.major}.{version.minor}.{version.micro} detected")
        print("   Warning: Python 3.13+ may have compatibility issues with Gradio/Pydantic")
        print("   Python 3.12 is recommended for best compatibility")
        print("   Continuing anyway...")
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")

    return True

def create_virtual_environment():
    """Create Python virtual environment"""
    env_path = Path("env")
    
    if env_path.exists():
        print(" Virtual environment already exists")
        return env_path
    
    print(" Creating Python virtual environment...")
    
    # Create virtual environment
    result = run_command([sys.executable, "-m", "venv", "env"], "Creating virtual environment")
    
    if result.returncode == 0:
        print("    Virtual environment created successfully")
        return env_path
    else:
        print("    Failed to create virtual environment")
        sys.exit(1)

def get_python_executable():
    """Get the path to Python executable in virtual environment"""
    if platform.system() == "Windows":
        return Path("env") / "Scripts" / "python.exe"
    else:
        return Path("env") / "bin" / "python"

def get_pip_executable():
    """Get the path to pip executable in virtual environment"""
    if platform.system() == "Windows":
        return Path("env") / "Scripts" / "pip.exe"
    else:
        return Path("env") / "bin" / "pip"

def ask_gpu_type():
    """Ask user which GPU they have"""
    print("\n🎮 GPU Configuration")
    print("=" * 70)
    print()
    print("Which GPU/hardware do you have?")
    print()
    print("1. RTX 5090/5080 (Blackwell - requires CUDA 12.8)")
    print("2. RTX 4090/4080 or other modern NVIDIA GPU (CUDA 12.4)")
    print("3. CPU only (no GPU / AMD / Intel)")
    print()

    while True:
        choice = input("Enter your choice (1-3): ").strip()

        if choice == "1":
            print("\n✅ Selected: RTX 5090/5080 (Blackwell)")
            print("   📦 Will install PyTorch with CUDA 12.8 support")
            print("   💡 Requirements: NVIDIA Driver 570.86+, CUDA Toolkit 12.8")
            return "cu128", "RTX 5090/5080"
        elif choice == "2":
            print("\n✅ Selected: Modern NVIDIA GPU")
            print("   📦 Will install PyTorch with CUDA 12.4 support")
            return "cu124", "NVIDIA GPU"
        elif choice == "3":
            print("\n✅ Selected: CPU only")
            print("   📦 Will install CPU-optimized PyTorch")
            return "cpu", "CPU"
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
            print()

def install_dependencies():
    """Install required dependencies"""
    pip_exe = get_pip_executable()
    python_exe = get_python_executable()

    if not pip_exe.exists():
        print("❌ pip not found in virtual environment")
        sys.exit(1)

    print("\n📦 Installing dependencies...")

    # Upgrade pip first using python -m pip (more reliable on Windows)
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip", check=False)

    # Install wheel for better package building
    run_command([str(pip_exe), "install", "wheel"], "Installing wheel")

    # Ask user about their GPU
    cuda_version, gpu_name = ask_gpu_type()

    # Install PyTorch first with correct CUDA support
    print(f"\n🔥 Installing PyTorch for {gpu_name}...")

    if cuda_version == "cu128":
        # RTX 5090/5080 - Blackwell architecture requires CUDA 12.8
        pytorch_cmd = [
            str(pip_exe), "install",
            "torch==2.8.0+cu128",
            "torchvision==0.23.0+cu128",
            "--index-url", "https://download.pytorch.org/whl/cu128"
        ]
        print("   Installing PyTorch 2.8.0 with CUDA 12.8 (Blackwell support)")
    elif cuda_version == "cu124":
        # RTX 4090 and other modern GPUs - use musubi-tuner compatible version
        pytorch_cmd = [
            str(pip_exe), "install",
            "torch==2.7.1+cu124",
            "torchvision==0.22.1+cu124",
            "--index-url", "https://download.pytorch.org/whl/cu124"
        ]
        print("   Installing PyTorch 2.7.1 with CUDA 12.4 (musubi-tuner compatible)")
    else:
        # CPU only
        pytorch_cmd = [
            str(pip_exe), "install",
            "torch==2.8.0",
            "torchvision==0.23.0",
            "--index-url", "https://download.pytorch.org/whl/cpu"
        ]
        print("   Installing PyTorch 2.8.0 (CPU only)")

    pytorch_result = run_command(pytorch_cmd, "Installing PyTorch", check=False)

    if pytorch_result.returncode != 0:
        print("\n⚠️  PyTorch installation failed. Trying fallback method...")
        # Fallback: try without index-url (will install latest stable)
        fallback_cmd = [str(pip_exe), "install", "torch>=2.7.1", "torchvision>=0.22.1"]
        run_command(fallback_cmd, "Installing PyTorch (fallback)")

    # Install requirements (this will skip torch/torchvision as they're already installed)
    if Path("requirements.txt").exists():
        print("\n📋 Installing remaining dependencies from requirements.txt...")
        run_command([str(pip_exe), "install", "-r", "requirements.txt"], "Installing requirements", check=False)
    else:
        # Fallback to manual installation of core dependencies
        print("\n⚠️  requirements.txt not found, using fallback dependencies...")
        dependencies = [
            "accelerate==1.6.0",              # Match musubi-tuner for compatibility
            "transformers==4.54.1",           # UPDATED: From 4.44.0 to match musubi-tuner
            "diffusers[torch]==0.32.1",       # UPDATED: From 0.25.0 for WAN 2.2 support
            "safetensors>=0.4.5",             # UPDATED: From 0.4.4
            "sentencepiece>=0.2.1",           # UPDATED: From 0.2.0
            "gradio>=5.49.1",                 # UPDATED: From >=4.0.0 to match requirements.txt
            "einops==0.7.0",                  # Match musubi-tuner exactly for compatibility
            "huggingface-hub>=0.34.3",        # UPDATED: From 0.24.5 for API compatibility
            "rich>=14.2.0",                   # UPDATED: From 13.7.0
            "numpy>=1.24.0",
            "pyyaml>=6.0.0",
            "pillow>=11.3.0",                 # UPDATED: From >=10.0.0 to match musubi-tuner
            "tqdm>=4.66.0",
            "opencv-python>=4.10.0",          # ADDED: Version specification
            "toml==0.10.2",                   # ADDED: Required for compatibility
            "imagesize==1.4.1",               # ADDED: Required dependency
            "av>=14.0.0",                     # WAN 2.2 video processing
            "easydict>=1.13",                 # WAN 2.2 configuration
            "ftfy>=6.3.0",                    # WAN 2.2 text preprocessing
            "voluptuous>=0.15.0",             # Config validation
        ]

        for dep in dependencies:
            run_command([str(pip_exe), "install", dep], f"Installing {dep}", check=False)

    # Verify PyTorch installation and GPU support
    print("\n🔍 Verifying PyTorch installation...")
    verify_cmd = [
        str(python_exe), "-c",
        "import torch; print(f'PyTorch: {torch.__version__}'); "
        "print(f'CUDA available: {torch.cuda.is_available()}'); "
        "print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU only\"}'); "
        "print(f'Compute capability: {torch.cuda.get_device_capability(0) if torch.cuda.is_available() else \"N/A\"}')"
    ]
    verify_result = run_command(verify_cmd, "Checking PyTorch", check=False)

    if verify_result.returncode == 0:
        print("\n✅ PyTorch installation verified!")
        # Check for RTX 5090 specific verification
        if cuda_version == "cu128":
            print("\n🎮 RTX 5090 Support:")
            print("   ✅ PyTorch installed with CUDA 12.8")
            print("   ✅ Blackwell architecture (sm_120) supported")
            print("   💡 Make sure you have:")
            print("      • NVIDIA Driver 570.86 or newer")
            print("      • CUDA Toolkit 12.8 installed")
    else:
        print("\n⚠️  Could not verify PyTorch installation")
        print("   The installation may still work, but GPU acceleration might not be available")

    # Install current package in development mode
    run_command([str(pip_exe), "install", "-e", "."], "Installing LoRA the Explorer in development mode")

def create_launcher_scripts():
    """Create launcher scripts for easy access"""
    python_exe = get_python_executable()
    
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
        
        print(" Created Windows launcher script:")
        print("    start_gui.bat - Launch GUI")
        
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
        
        print(" Created Unix launcher script:")
        print("    start_gui.sh - Launch GUI")

def download_sd_scripts():
    """Download and set up musubi-tuner"""
    sd_scripts_path = Path("musubi-tuner")

    # Check if musubi-tuner is already installed
    # Look for either the root merge_lora.py or the module structure
    if sd_scripts_path.exists():
        has_merge_script = (sd_scripts_path / "merge_lora.py").exists()
        has_module = (sd_scripts_path / "src" / "musubi_tuner").exists()
        if has_merge_script or has_module:
            print(" musubi-tuner already installed")
            return sd_scripts_path

    print(" Downloading musubi-tuner...")

    # Clone musubi-tuner repository (WAN 2.2 support)
    clone_result = run_command([
        "git", "clone",
        "https://github.com/kohya-ss/musubi-tuner.git",
        "musubi-tuner"
    ], "Cloning musubi-tuner (WAN 2.2 support)", check=False)
    
    if clone_result.returncode != 0:
        print(" Failed to clone musubi-tuner. Trying alternative method...")

        # Alternative: download as zip
        try:
            import urllib.request
            import zipfile

            print(" Downloading musubi-tuner as ZIP...")
            url = "https://github.com/kohya-ss/musubi-tuner/archive/refs/heads/main.zip"
            zip_path = "musubi-tuner-main.zip"

            urllib.request.urlretrieve(url, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")

            # Rename extracted folder
            if Path("musubi-tuner-main").exists():
                Path("musubi-tuner-main").rename("musubi-tuner")

            # Clean up
            Path(zip_path).unlink()
            print(" musubi-tuner downloaded successfully")

        except Exception as e:
            print(f" Failed to download musubi-tuner: {e}")
            print("   Please manually download from: https://github.com/kohya-ss/musubi-tuner")
            print("   Extract to: ./musubi-tuner/")
            return None
    
    # Install musubi-tuner requirements and package
    if sd_scripts_path.exists():
        print(" Installing musubi-tuner dependencies...")
        pip_exe = get_pip_executable()
        python_exe = get_python_executable()

        # Install musubi-tuner requirements
        sd_requirements = sd_scripts_path / "requirements.txt"
        if sd_requirements.exists():
            run_command([
                str(pip_exe), "install", "-r", str(sd_requirements)
            ], "Installing musubi-tuner requirements", check=False)
        else:
            print("   Warning: musubi-tuner requirements.txt not found")

        # Install musubi-tuner as editable package
        print(" Installing musubi-tuner library...")
        install_result = run_command([
            str(pip_exe), "install", "-e", str(sd_scripts_path)
        ], "Installing musubi-tuner library", check=False)

        # Verify installation by checking if library module can be imported
        print(" Verifying musubi-tuner installation...")
        verify_result = run_command([
            str(python_exe), "-c", f"import sys; sys.path.insert(0, '{sd_scripts_path}'); import library.utils; print(' musubi-tuner library verified')"
        ], "Verifying library module", check=False)

        if verify_result.returncode == 0:
            print(" musubi-tuner setup complete")
        else:
            print("  musubi-tuner installed but library verification failed")
            print("   This may cause issues with LoRA operations")
        
        return sd_scripts_path
    
    return None

def main():
    """Main installation process"""
    print("LoRA the Explorer Installation")
    print("=" * 50)
    print()
    
    # Check Python version
    check_python_version()
    print()
    
    # Create virtual environment
    env_path = create_virtual_environment()
    print()
    
    # Install dependencies
    install_dependencies()
    print()
    
    # Create launcher scripts
    create_launcher_scripts()
    print()
    
    # Download and set up musubi-tuner
    sd_scripts_path = download_sd_scripts()
    print()

    # Success message
    print(" Installation Complete!")
    print("=" * 50)
    print()
    print(" Quick Start:")

    if platform.system() == "Windows":
        print("    GUI: Double-click start_gui.bat")
    else:
        print("    GUI: ./start_gui.sh")

    print()
    print(" Manual command:")
    python_exe = get_python_executable()
    print(f"    GUI: {python_exe} lora_algebra_gui.py")
    print()
    print("🔗 Project: https://github.com/shootthesound/lora-the-explorer")

    if sd_scripts_path:
        print(f" musubi-tuner: {sd_scripts_path.absolute()}")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n Installation failed: {e}")
        sys.exit(1)