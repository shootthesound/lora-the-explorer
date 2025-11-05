#!/usr/bin/env python3
"""
Verify WAN 2.2 Installation Script

This script verifies that all components needed for WAN 2.2 LoRA operations
are correctly installed and accessible.
"""

import sys
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_musubi_tuner():
    """Check if musubi-tuner is properly installed"""
    print("🔍 Checking musubi-tuner installation...")

    errors = []
    warnings = []

    musubi_path = Path("musubi-tuner")

    # Check 1: Directory exists
    if not musubi_path.exists():
        errors.append("musubi-tuner directory not found")
        return errors, warnings
    else:
        print("   ✅ musubi-tuner directory found")

    # Check 2: merge_lora.py exists (critical for operations)
    merge_script = musubi_path / "merge_lora.py"
    if not merge_script.exists():
        errors.append(f"merge_lora.py not found at {merge_script}")
        print(f"   ❌ merge_lora.py not found (CRITICAL)")
    else:
        print(f"   ✅ merge_lora.py found at root level")

    # Check 3: Python module structure (optional but good to have)
    module_path = musubi_path / "src" / "musubi_tuner"
    if module_path.exists():
        print(f"   ✅ Python module structure found")
    else:
        warnings.append("Python module structure not found (may be older version)")
        print(f"   ⚠️  Python module structure not found")

    # Check 4: networks directory (for LoRA modules)
    networks_path = musubi_path / "networks"
    if networks_path.exists():
        print(f"   ✅ networks directory found")

        # Check for WAN-specific modules
        wan_module = networks_path / "lora_wan.py"
        if wan_module.exists():
            print(f"   ✅ lora_wan.py module found")
        else:
            warnings.append("lora_wan.py not found in networks/")
            print(f"   ⚠️  lora_wan.py not found")
    else:
        warnings.append("networks directory not found")
        print(f"   ⚠️  networks directory not found")

    return errors, warnings

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n🔍 Checking Python packages...")

    errors = []
    warnings = []

    # Critical packages
    critical_packages = {
        'torch': 'PyTorch (deep learning framework)',
        'torchvision': 'PyTorch vision utilities',
        'safetensors': 'SafeTensors file handling',
        'gradio': 'GUI framework',
    }

    # WAN 2.2 specific packages
    wan_packages = {
        'av': 'Video processing (WAN 2.2 requirement)',
        'easydict': 'WAN 2.2 configuration',
        'ftfy': 'Text preprocessing for WAN 2.2',
    }

    # Optional but recommended
    optional_packages = {
        'accelerate': 'Training acceleration',
        'transformers': 'Transformer models',
        'diffusers': 'Diffusion models',
    }

    print("\n   Critical packages:")
    for package, description in critical_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package:20s} - {description}")
        except ImportError:
            errors.append(f"Critical package '{package}' not installed ({description})")
            print(f"   ❌ {package:20s} - {description}")

    print("\n   WAN 2.2 specific packages:")
    for package, description in wan_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package:20s} - {description}")
        except ImportError:
            errors.append(f"WAN 2.2 package '{package}' not installed ({description})")
            print(f"   ❌ {package:20s} - {description}")

    print("\n   Optional packages:")
    for package, description in optional_packages.items():
        try:
            __import__(package)
            print(f"   ✅ {package:20s} - {description}")
        except ImportError:
            warnings.append(f"Optional package '{package}' not installed ({description})")
            print(f"   ⚠️  {package:20s} - {description}")

    return errors, warnings

def check_pytorch_version():
    """Check PyTorch version"""
    print("\n🔍 Checking PyTorch version...")

    errors = []
    warnings = []

    try:
        import torch
        version = torch.__version__
        print(f"   ✅ PyTorch version: {version}")

        # Check if version is adequate for WAN 2.2
        major, minor = map(int, version.split('.')[:2])
        if major < 2 or (major == 2 and minor < 9):
            warnings.append(f"PyTorch {version} may not support WAN 2.2 optimally (recommend 2.9.0+)")
            print(f"   ⚠️  Version may be outdated for WAN 2.2 (recommend 2.9.0+)")

        # Check CUDA availability
        if torch.cuda.is_available():
            cuda_version = torch.version.cuda
            print(f"   ✅ CUDA available: {cuda_version}")
            print(f"   ✅ GPU device: {torch.cuda.get_device_name(0)}")
        else:
            warnings.append("CUDA not available - will run on CPU (very slow)")
            print(f"   ⚠️  CUDA not available (CPU only - will be slow)")

    except ImportError:
        errors.append("PyTorch not installed")
        print(f"   ❌ PyTorch not installed")
    except Exception as e:
        errors.append(f"Error checking PyTorch: {e}")
        print(f"   ❌ Error: {e}")

    return errors, warnings

def check_project_structure():
    """Check if project files are in place"""
    print("\n🔍 Checking project structure...")

    errors = []
    warnings = []

    required_files = [
        "lora_algebra_gui.py",
        "lora_algebra/gui.py",
        "lora_algebra/operations.py",
        "lora_algebra/core.py",
        "requirements.txt",
    ]

    for file_path in required_files:
        if Path(file_path).exists():
            print(f"   ✅ {file_path}")
        else:
            errors.append(f"Required file missing: {file_path}")
            print(f"   ❌ {file_path}")

    return errors, warnings

def main():
    """Main verification process"""
    print_header("LoRA the Explorer - WAN 2.2 Installation Verification")

    all_errors = []
    all_warnings = []

    # Run all checks
    errors, warnings = check_musubi_tuner()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = check_python_packages()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = check_pytorch_version()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    errors, warnings = check_project_structure()
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Print summary
    print_header("Verification Summary")

    if all_errors:
        print("❌ CRITICAL ERRORS:")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
        print()

    if all_warnings:
        print("⚠️  WARNINGS:")
        for i, warning in enumerate(all_warnings, 1):
            print(f"   {i}. {warning}")
        print()

    if not all_errors and not all_warnings:
        print("✅ All checks passed! Installation looks good.")
        print("\nYou can now run the GUI:")
        print("   python lora_algebra_gui.py")
        print("   or")
        print("   ./start_gui.sh  (Unix/Mac)")
        print("   start_gui.bat   (Windows)")
        return 0
    elif not all_errors:
        print("⚠️  Installation has some warnings but should work.")
        print("\nYou can try running the GUI:")
        print("   python lora_algebra_gui.py")
        return 0
    else:
        print("❌ Installation has critical errors. Please fix them before running.")
        print("\nTo fix:")
        print("   1. Run: python install.py")
        print("   2. Check that all dependencies install correctly")
        print("   3. Run this script again: python verify_installation.py")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
