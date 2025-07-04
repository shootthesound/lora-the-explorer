"""
Core LoRA manipulation functionality
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from safetensors import safe_open

class LoRAProcessor:
    """Main class for LoRA manipulation operations"""
    
    def __init__(self, sd_scripts_path: Optional[str] = None):
        """Initialize LoRA processor
        
        Args:
            sd_scripts_path: Path to sd-scripts directory. If None, looks in parent directory.
        """
        self.sd_scripts_path = self._find_sd_scripts(sd_scripts_path)
        
    def _find_sd_scripts(self, custom_path: Optional[str] = None) -> str:
        """Find sd-scripts directory"""
        if custom_path and os.path.exists(custom_path):
            return custom_path
            
        # Look in common locations
        possible_paths = [
            "sd-scripts",
            "../sd-scripts", 
            "../../sd-scripts",
            os.path.join(os.path.dirname(__file__), "..", "..", "sd-scripts")
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path) and os.path.exists(os.path.join(abs_path, "networks")):
                return abs_path
                
        raise FileNotFoundError("sd-scripts directory not found. Please specify the path manually.")
    
    def extract_metadata(self, lora_path: str) -> Optional[Dict[str, Any]]:
        """Extract metadata from LoRA file
        
        Args:
            lora_path: Path to LoRA .safetensors file
            
        Returns:
            Dictionary containing LoRA metadata or None if extraction fails
        """
        try:
            if not os.path.exists(lora_path):
                return None
                
            metadata = {}
            
            with safe_open(lora_path, framework="pt", device="cpu") as f:
                file_metadata = f.metadata()
                
                # Extract network dimension (rank)
                network_dim = None
                network_alpha = None
                
                # Try to get from metadata first
                if file_metadata:
                    network_dim = file_metadata.get('ss_network_dim')
                    network_alpha = file_metadata.get('ss_network_alpha')
                    
                    # Get other useful metadata
                    metadata['learning_rate'] = file_metadata.get('ss_learning_rate', '1e-4')
                    metadata['base_model'] = file_metadata.get('ss_base_model_version', '')
                    metadata['training_comment'] = file_metadata.get('ss_training_comment', '')
                
                # If not in metadata, inspect tensor shapes
                if network_dim is None:
                    for key in f.keys():
                        if 'lora_down.weight' in key:
                            tensor = f.get_tensor(key)
                            if len(tensor.shape) == 2:  # Linear layer
                                network_dim = tensor.shape[0]
                                break
                            elif len(tensor.shape) == 4:  # Conv layer  
                                network_dim = tensor.shape[0]
                                break
                
                # If still not found, try alpha tensors
                if network_alpha is None:
                    for key in f.keys():
                        if key.endswith('.alpha'):
                            alpha_tensor = f.get_tensor(key)
                            network_alpha = float(alpha_tensor.item())
                            break
            
            # Convert to proper types
            if network_dim:
                try:
                    network_dim = int(network_dim)
                except:
                    network_dim = 32  # fallback
            else:
                network_dim = 32  # fallback
                
            if network_alpha:
                try:
                    network_alpha = float(network_alpha)
                except:
                    network_alpha = 32.0  # fallback
            else:
                network_alpha = 32.0  # fallback
            
            metadata['network_dim'] = network_dim
            metadata['network_alpha'] = network_alpha
            
            return metadata
            
        except Exception as e:
            print(f"Error extracting LoRA metadata from {lora_path}: {e}")
            return None
    
    def _run_sd_script(self, script_name: str, args: list) -> Tuple[bool, str]:
        """Run an sd-scripts command
        
        Args:
            script_name: Name of the script (e.g., 'flux_merge_lora.py')
            args: List of arguments to pass to the script
            
        Returns:
            Tuple of (success: bool, output: str)
        """
        script_path = os.path.join(self.sd_scripts_path, "networks", script_name)
        
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_path}"
        
        command = [sys.executable, script_path] + args
        
        print(f"DEBUG: Running command: {' '.join(command)}")
        print(f"DEBUG: Working directory: {self.sd_scripts_path}")
        print(f"DEBUG: Script exists: {os.path.exists(script_path)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self.sd_scripts_path
            )
            
            success = result.returncode == 0
            
            if success:
                output = result.stdout
            else:
                # Combine both stdout and stderr for better error reporting
                output = f"Return code: {result.returncode}\n"
                if result.stdout:
                    output += f"STDOUT:\n{result.stdout}\n"
                if result.stderr:
                    output += f"STDERR:\n{result.stderr}\n"
                if not result.stdout and not result.stderr:
                    output += "No output from command"
            
            return success, output
            
        except Exception as e:
            return False, f"Exception running command: {str(e)}\nCommand: {' '.join(command)}"
    
    def _resolve_path(self, path: str) -> str:
        """Convert relative path to absolute with quotes"""
        abs_path = os.path.abspath(path)
        return f'"{abs_path}"'
    
    def _resolve_path_without_quotes(self, path: str) -> str:
        """Convert relative path to absolute without quotes"""
        return os.path.abspath(path)