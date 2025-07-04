#!/usr/bin/env python3
"""
LoRA Algebra GUI Launcher

Simple launcher script for the LoRA Algebra GUI
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Launch the LoRA Algebra GUI"""
    try:
        from lora_algebra.gui import launch_gui
        
        # Look for sd-scripts (should be installed locally)
        sd_scripts_path = os.path.abspath("sd-scripts")
        
        if not os.path.exists(sd_scripts_path) or not os.path.exists(os.path.join(sd_scripts_path, "networks")):
            print("⚠️  Warning: sd-scripts not found.")
            print("   Please run 'python install.py' first to set up dependencies.")
            print("   Some features may not work without sd-scripts.")
            print()
            sd_scripts_path = None
        
        print("Swiper no swiping...")
        print("   This may take a moment to start...")
        print()
        
        # Launch GUI
        launch_gui(
            sd_scripts_path=sd_scripts_path,
            share=False,
            inbrowser=True
        )
        
    except ImportError as e:
        print("❌ Error: Missing dependencies")
        print(f"   {e}")
        print()
        print("Please install requirements:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()