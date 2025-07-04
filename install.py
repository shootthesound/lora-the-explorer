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
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(" Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    
    print(f" Python {version.major}.{version.minor}.{version.micro} - Compatible")
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

def install_dependencies():
    """Install required dependencies"""
    pip_exe = get_pip_executable()
    python_exe = get_python_executable()
    
    if not pip_exe.exists():
        print(" pip not found in virtual environment")
        sys.exit(1)
    
    print(" Installing dependencies...")
    
    # Upgrade pip first using python -m pip (more reliable on Windows)
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], "Upgrading pip", check=False)
    
    # Install wheel for better package building
    run_command([str(pip_exe), "install", "wheel"], "Installing wheel")
    
    # Install requirements
    if Path("requirements.txt").exists():
        run_command([str(pip_exe), "install", "-r", "requirements.txt"], "Installing requirements")
    else:
        # Fallback to manual installation of core dependencies
        dependencies = [
            "torch==2.7.1",
            "torchvision==0.22.1", 
            "accelerate==0.33.0",
            "transformers==4.44.0",
            "diffusers[torch]==0.25.0",
            "safetensors==0.4.4",
            "sentencepiece==0.2.0",
            "gradio>=4.0.0",
            "einops==0.7.0",
            "huggingface-hub==0.24.5",
            "rich==13.7.0",
            "numpy>=1.24.0",
            "pyyaml>=6.0.0",
            "pillow>=10.0.0",
            "tqdm>=4.66.0"
        ]
        
        for dep in dependencies:
            run_command([str(pip_exe), "install", dep], f"Installing {dep}")
    
    # Install current package in development mode
    run_command([str(pip_exe), "install", "-e", "."], "Installing LoRA the Explorer in development mode")

def create_launcher_scripts():
    """Create launcher scripts for easy access"""
    python_exe = get_python_executable()
    
    if platform.system() == "Windows":
        # Windows batch file
        launcher_content = f"""@echo off
echo  Launching LoRA the Explorer GUI...
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
"{python_exe.absolute()}" lora_algebra_gui.py
"""
        with open("start_gui.sh", "w") as f:
            f.write(launcher_content)
        os.chmod("start_gui.sh", 0o755)
        
        print(" Created Unix launcher script:")
        print("    start_gui.sh - Launch GUI")

def download_sd_scripts():
    """Download and set up sd-scripts"""
    sd_scripts_path = Path("sd-scripts")
    
    if sd_scripts_path.exists() and (sd_scripts_path / "networks").exists():
        print(" sd-scripts already installed")
        return sd_scripts_path
    
    print(" Downloading sd-scripts...")
    
    # Clone sd-scripts repository (sd3 branch with Flux support)
    clone_result = run_command([
        "git", "clone", 
        "-b", "sd3",
        "https://github.com/kohya-ss/sd-scripts.git", 
        "sd-scripts"
    ], "Cloning sd-scripts sd3 branch (Flux support)", check=False)
    
    if clone_result.returncode == 0:
        # Pin to specific commit for version stability
        print(" Pinning sd-scripts to tested commit...")
        
        # Change to sd-scripts directory to run git checkout
        original_dir = os.getcwd()
        try:
            os.chdir("sd-scripts")
            run_command([
                "git", "checkout", "3e6935a07edcb944407840ef74fcaf6fcad352f7"
            ], "Pinning to stable commit", check=False)
        finally:
            os.chdir(original_dir)
    
    if clone_result.returncode != 0:
        print(" Failed to clone sd-scripts. Trying alternative method...")
        
        # Alternative: download as zip
        try:
            import urllib.request
            import zipfile
            
            print(" Downloading sd-scripts sd3 branch as ZIP...")
            url = "https://github.com/kohya-ss/sd-scripts/archive/refs/heads/sd3.zip"
            zip_path = "sd-scripts-sd3.zip"
            
            urllib.request.urlretrieve(url, zip_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
            
            # Rename extracted folder
            if Path("sd-scripts-sd3").exists():
                Path("sd-scripts-sd3").rename("sd-scripts")
            
            # Clean up
            Path(zip_path).unlink()
            print(" sd-scripts downloaded successfully")
            
        except Exception as e:
            print(f" Failed to download sd-scripts: {e}")
            print("   Please manually download from: https://github.com/kohya-ss/sd-scripts")
            print("   Extract to: ./sd-scripts/")
            return None
    
    # Install sd-scripts requirements and package
    if sd_scripts_path.exists():
        print(" Installing sd-scripts dependencies...")
        pip_exe = get_pip_executable()
        python_exe = get_python_executable()
        
        # Install sd-scripts requirements
        sd_requirements = sd_scripts_path / "requirements.txt"
        if sd_requirements.exists():
            run_command([
                str(pip_exe), "install", "-r", str(sd_requirements)
            ], "Installing sd-scripts requirements", check=False)
        else:
            print("   Warning: sd-scripts requirements.txt not found")
        
        # Install sd-scripts as editable package
        print(" Installing sd-scripts library...")
        install_result = run_command([
            str(pip_exe), "install", "-e", str(sd_scripts_path)
        ], "Installing sd-scripts library", check=False)
        
        # Verify installation by checking if library module can be imported
        print(" Verifying sd-scripts installation...")
        verify_result = run_command([
            str(python_exe), "-c", f"import sys; sys.path.insert(0, '{sd_scripts_path}'); import library.utils; print(' sd-scripts library verified')"
        ], "Verifying library module", check=False)
        
        if verify_result.returncode == 0:
            # Apply fix for FLUX LoRA metadata by copying corrected file
            print("🔧 Applying FLUX metadata fix...")
            try:
                import shutil
                fixed_file = Path("fixed_files") / "flux_merge_lora.py"
                target_file = sd_scripts_path / "networks" / "flux_merge_lora.py"
                
                if fixed_file.exists() and target_file.exists():
                    shutil.copy2(str(fixed_file), str(target_file))
                    print(" FLUX metadata fix applied (networks.lora_flux)")
                elif not fixed_file.exists():
                    print("  Fixed file not found in fixed_files directory")
                elif not target_file.exists():
                    print("  Target file not found in sd-scripts")
            except Exception as e:
                print(f"️  Could not apply FLUX metadata fix: {e}")
                print("   LoRAs may have incorrect network module metadata")
            
            print(" sd-scripts setup complete")
        else:
            print("  sd-scripts installed but library verification failed")
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
    
    # Download and set up sd-scripts
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
        print(f" sd-scripts: {sd_scripts_path.absolute()}")
    
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