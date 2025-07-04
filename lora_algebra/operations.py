"""
LoRA mathematical operations (subtract, merge, etc.)
"""

import os
import sys
import subprocess
from typing import Optional, Tuple, List
from safetensors import safe_open
from safetensors.torch import save_file
import torch


class LoRAProcessor:
    """Helper class for LoRA operations using sd-scripts"""
    
    def __init__(self, sd_scripts_path: Optional[str] = None):
        self.sd_scripts_path = sd_scripts_path or resolve_path_without_quotes("../sd-scripts")
    
    def _run_sd_script(self, script_name: str, args: List[str]) -> Tuple[bool, str]:
        """Run an sd-scripts script with given arguments"""
        script_path = os.path.join(self.sd_scripts_path, "networks", script_name)
        
        if not os.path.exists(script_path):
            return False, f"Script not found: {script_path}"
        
        command = [sys.executable, script_path] + args
        
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Set up environment with sd-scripts in Python path
            env = os.environ.copy()
            if 'PYTHONPATH' in env:
                env['PYTHONPATH'] = f"{self.sd_scripts_path}{os.pathsep}{env['PYTHONPATH']}"
            else:
                env['PYTHONPATH'] = self.sd_scripts_path
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=project_root,
                env=env
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                error_msg = result.stderr or result.stdout
                if "ModuleNotFoundError: No module named 'library'" in error_msg:
                    error_msg += f"\n\nTroubleshooting: sd-scripts library not found. Try:\n"
                    error_msg += f"1. Ensure sd-scripts is properly installed\n"
                    error_msg += f"2. Check that sd-scripts path is correct: {self.sd_scripts_path}\n"
                    error_msg += f"3. Reinstall by running the installer again"
                return False, error_msg
                
        except Exception as e:
            return False, f"Error running script: {str(e)}"
    
    def extract_metadata(self, lora_path: str) -> dict:
        """Extract metadata from LoRA file"""
        try:
            with safe_open(lora_path, framework="pt", device="cpu") as f:
                metadata = {}
                if f.metadata():
                    metadata.update(f.metadata())
                return metadata
        except Exception as e:
            return {"error": f"Could not read metadata: {str(e)}"}

def resolve_path_without_quotes(p):
    """Copy of custom.py's path resolution"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    norm_path = os.path.normpath(os.path.join(current_dir, p))
    return norm_path

def subtract_loras(
    lora_a_path: str, 
    lora_b_path: str, 
    output_path: str,
    strength_a: float = 1.0,
    strength_b: float = 1.0,
    use_concat: bool = True,
    sd_scripts_path: Optional[str] = None
) -> Tuple[bool, str]:
    """Extract difference between two LoRAs (A - B) using negative weights - copied from custom.py"""
    
    # Validate inputs
    if not lora_a_path or not lora_b_path:
        return False, "Error: Please provide paths for both LoRAs"
    
    if not os.path.exists(lora_a_path):
        return False, f"Error: LoRA A file not found: {lora_a_path}"
    
    if not os.path.exists(lora_b_path):
        return False, f"Error: LoRA B file not found: {lora_b_path}"
    
    if not output_path:
        return False, "Error: Please provide an output path"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build command for LoRA difference extraction using negative weight - EXACT copy from custom.py
    script_path = resolve_path_without_quotes("../sd-scripts/networks/flux_merge_lora.py")
    
    # Use positive weight for A and negative weight for B to get A - B
    command = [
        sys.executable,
        script_path,
        "--save_to", output_path,
        "--models", lora_a_path, lora_b_path,
        "--ratios", str(strength_a), str(-strength_b),  # Negative for subtraction
        "--save_precision", "fp16"
    ]
    
    # Add concat flag if selected
    if use_concat:
        command.append("--concat")
    
    try:
        # Run the difference extraction command - but use project root as working directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Set up environment with sd-scripts in Python path
        sd_scripts_dir = sd_scripts_path or resolve_path_without_quotes("../sd-scripts")
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{sd_scripts_dir}{os.pathsep}{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = sd_scripts_dir
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=project_root,
            env=env
        )
        
        if result.returncode == 0:
            return True, f"Success! Difference LoRA saved to: {output_path}\n\nThis LoRA represents: A (strength {strength_a}) - B (strength {strength_b})\n\nOutput:\n{result.stdout}"
        else:
            error_msg = result.stderr or result.stdout
            if "ModuleNotFoundError: No module named 'library'" in error_msg:
                error_msg += f"\n\nTroubleshooting: sd-scripts library not found. Try:\n"
                error_msg += f"1. Ensure sd-scripts is properly installed\n"
                error_msg += f"2. Check that sd-scripts path is correct: {sd_scripts_dir}\n"
                error_msg += f"3. Reinstall by running the installer again"
            return False, f"Error during difference extraction:\n{error_msg}"
            
    except Exception as e:
        return False, f"Error running difference extraction: {str(e)}"

def merge_loras(
    lora_a_path: str,
    lora_b_path: str, 
    output_path: str,
    strength_a: float = 1.0,
    strength_b: float = 1.0,
    use_concat: bool = True,
    sd_scripts_path: Optional[str] = None
) -> Tuple[bool, str]:
    """Merge two LoRAs with positive weights (A + B)
    
    Args:
        lora_a_path: Path to LoRA A
        lora_b_path: Path to LoRA B
        output_path: Path for output LoRA
        strength_a: Strength multiplier for LoRA A
        strength_b: Strength multiplier for LoRA B
        use_concat: Whether to use concat mode for different ranks
        sd_scripts_path: Custom path to sd-scripts directory
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    processor = LoRAProcessor(sd_scripts_path)
    
    # Validate inputs
    if not os.path.exists(lora_a_path):
        return False, f"LoRA A file not found: {lora_a_path}"
    
    if not os.path.exists(lora_b_path):
        return False, f"LoRA B file not found: {lora_b_path}"
    
    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Build merge command
    args = [
        "--save_to", output_path,
        "--models", lora_a_path, lora_b_path,
        "--ratios", str(strength_a), str(strength_b),
        "--save_precision", "fp16"
    ]
    
    # Add concat flag if selected
    if use_concat:
        args.append("--concat")
    
    # Run the merge
    success, output = processor._run_sd_script("flux_merge_lora.py", args)
    
    if success and os.path.exists(output_path):
        return True, f"Success! Merged LoRA saved to: {output_path}\\n\\nCombined: A (strength {strength_a}) + B (strength {strength_b})"
    else:
        return False, f"Error during merge: {output}"

def analyze_lora(lora_path: str, sd_scripts_path: Optional[str] = None) -> dict:
    """Analyze a LoRA file and return detailed information
    
    Args:
        lora_path: Path to LoRA file
        sd_scripts_path: Custom path to sd-scripts directory
        
    Returns:
        Dictionary containing analysis results
    """
    processor = LoRAProcessor(sd_scripts_path)
    
    if not os.path.exists(lora_path):
        return {"error": f"File not found: {lora_path}"}
    
    # Extract metadata
    metadata = processor.extract_metadata(lora_path)
    
    if not metadata:
        return {"error": "Could not extract metadata from LoRA file"}
    
    # File size analysis
    file_size = os.path.getsize(lora_path)
    file_size_mb = file_size / (1024 * 1024)
    
    # Rank analysis
    rank = metadata.get('network_dim', 32)
    alpha = metadata.get('network_alpha', 32.0)
    
    # Calculate approximate parameter count
    # This is a rough estimate for Flux LoRAs
    approx_params = rank * rank * 50  # Rough estimate
    
    analysis = {
        "file_path": lora_path,
        "file_size_mb": round(file_size_mb, 2),
        "rank": rank,
        "alpha": alpha,
        "learning_rate": metadata.get('learning_rate', 'Unknown'),
        "base_model": metadata.get('base_model', 'Unknown'),
        "training_comment": metadata.get('training_comment', ''),
        "estimated_parameters": approx_params,
        "rank_efficiency": f"{alpha/rank:.2f}" if rank > 0 else "N/A",
        "metadata": metadata
    }
    
    return analysis

def target_lora_layers(
    lora_path: str,
    output_path: str,
    mute_layers: List[int],
    sd_scripts_path: Optional[str] = None
) -> Tuple[bool, str]:
    """Mute specific FLUX layers in a LoRA by setting their weights to zero
    
    Args:
        lora_path: Path to input LoRA file
        output_path: Path for output LoRA file
        mute_layers: List of layer numbers to mute (e.g., [7, 20])
        sd_scripts_path: Not used but kept for consistency
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate input
        if not os.path.exists(lora_path):
            return False, f"LoRA file not found: {lora_path}"
        
        if not mute_layers:
            return False, "No layers selected to mute"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"🔍 Loading LoRA from: {lora_path}")
        print(f"🎯 Targeting layers: {mute_layers}")
        
        # Load the LoRA file and analyze structure
        tensors = {}
        metadata = {}
        total_tensors = 0
        muted_tensors = 0
        layer_analysis = {}
        
        with safe_open(lora_path, framework="pt", device="cpu") as f:
            # Copy metadata
            if f.metadata():
                metadata.update(f.metadata())
            
            # First pass: analyze tensor structure
            all_keys = list(f.keys())
            total_tensors = len(all_keys)
            print(f"📊 Total tensors in LoRA: {total_tensors}")
            
            # Debug: Print ALL tensor names to understand the naming pattern
            print(f"🔍 DEBUG: ALL {total_tensors} tensor names:")
            for i, key in enumerate(all_keys):
                print(f"   {i+1:4d}. {key}")
            
            # Also analyze unique patterns
            unique_prefixes = set()
            for key in all_keys:
                parts = key.split('.')
                if len(parts) >= 2:
                    unique_prefixes.add('.'.join(parts[:2]))
            
            print(f"🔍 DEBUG: Unique tensor prefixes found:")
            for prefix in sorted(unique_prefixes):
                count = len([k for k in all_keys if k.startswith(prefix)])
                print(f"   {prefix}: {count} tensors")
            
            # Analyze layer distribution with FLUX-specific patterns
            for key in all_keys:
                for layer_num in range(50):  # Check layers 0-49
                    # FLUX LoRA naming patterns
                    patterns = [
                        f"_layers_{layer_num}_",  # lora_te1_text_model_encoder_layers_7_
                        f"_blocks_{layer_num}_",  # lora_unet_double_blocks_7_, lora_unet_single_blocks_7_
                        f"single_blocks_{layer_num}_",  # lora_unet_single_blocks_7_
                        f"double_blocks_{layer_num}_",  # lora_unet_double_blocks_7_
                        # Legacy patterns for compatibility
                        f"single_transformer_blocks.{layer_num}.",
                        f"transformer.single_transformer_blocks.{layer_num}.",
                        f"transformer_blocks.{layer_num}.",
                        f"blocks.{layer_num}.",
                        f"layer.{layer_num}.",
                        f"layers.{layer_num}."
                    ]
                    
                    found_match = False
                    for pattern in patterns:
                        if pattern in key:
                            if layer_num not in layer_analysis:
                                layer_analysis[layer_num] = []
                            layer_analysis[layer_num].append(key)
                            found_match = True
                            break
                    
                    if found_match:
                        break
            
            print(f"📈 Layer distribution found:")
            for layer_num in sorted(layer_analysis.keys()):
                tensor_count = len(layer_analysis[layer_num])
                is_target = layer_num in mute_layers
                status = "🎯 TARGET" if is_target else "✅ keep"
                print(f"   Layer {layer_num}: {tensor_count} tensors {status}")
            
            # Second pass: process each tensor
            for key in all_keys:
                tensor = f.get_tensor(key)
                
                # Check if this tensor belongs to a layer we want to mute
                should_mute = False
                matched_layer = None
                
                for layer_num in mute_layers:
                    # Use FLUX LoRA naming patterns (same as analysis)
                    layer_patterns = [
                        f"_layers_{layer_num}_",  # lora_te1_text_model_encoder_layers_7_
                        f"_blocks_{layer_num}_",  # lora_unet_double_blocks_7_, lora_unet_single_blocks_7_
                        f"single_blocks_{layer_num}_",  # lora_unet_single_blocks_7_
                        f"double_blocks_{layer_num}_",  # lora_unet_double_blocks_7_
                        # Legacy patterns for compatibility
                        f"single_transformer_blocks.{layer_num}.",
                        f"transformer.single_transformer_blocks.{layer_num}.",
                        f"transformer_blocks.{layer_num}.",
                        f"blocks.{layer_num}.",
                        f"layer.{layer_num}.",
                        f"layers.{layer_num}."
                    ]
                    
                    if any(pattern in key for pattern in layer_patterns):
                        should_mute = True
                        matched_layer = layer_num
                        muted_tensors += 1
                        print(f"🔇 Muting L{layer_num}: {key}")
                        break
                
                if should_mute:
                    # Set tensor to zeros (mute the layer)
                    tensors[key] = torch.zeros_like(tensor)
                else:
                    # Keep original tensor
                    tensors[key] = tensor.clone()
        
        print(f"✅ Processing complete: {muted_tensors}/{total_tensors} tensors muted")
        
        # Add targeting info to metadata
        metadata["lora_algebra_targeted_layers"] = ",".join(map(str, mute_layers))
        metadata["lora_algebra_operation"] = "layer_targeting"
        
        # Save the modified LoRA
        print(f"💾 Saving modified LoRA to: {output_path}")
        save_file(tensors, output_path, metadata=metadata)
        
        # Create detailed report
        layer_report = ""
        for layer_num in sorted(layer_analysis.keys()):
            tensor_count = len(layer_analysis[layer_num])
            is_muted = layer_num in mute_layers
            status = "🔇 MUTED" if is_muted else "✅ preserved"
            layer_report += f"Layer {layer_num}: {tensor_count} tensors - {status}\n"
        
        report = f"""✅ Layer targeting completed successfully!

📊 ANALYSIS REPORT:
Total tensors processed: {total_tensors}
Tensors muted: {muted_tensors}
Layers targeted: {mute_layers}

📈 LAYER BREAKDOWN:
{layer_report}
💾 Output saved to: {output_path}

🎯 OPERATION SUMMARY:
The selected facial layers have been zeroed out while preserving all other characteristics. This LoRA should now work without the original facial features while maintaining style, poses, and costume elements."""
        
        return True, report
        
    except Exception as e:
        return False, f"Error during layer targeting: {str(e)}"

def selective_layer_merge(
    lora_a_path: str,
    lora_b_path: str, 
    output_path: str,
    layers_from_a: List[int],
    layers_from_b: List[int],
    strength_a: float = 1.0,
    strength_b: float = 1.0,
    sd_scripts_path: Optional[str] = None
) -> Tuple[bool, str]:
    """Selectively merge specific layers from two LoRAs with strength control
    
    Args:
        lora_a_path: Path to LoRA A
        lora_b_path: Path to LoRA B
        output_path: Path for output LoRA
        layers_from_a: List of layer numbers to take from LoRA A
        layers_from_b: List of layer numbers to take from LoRA B
        strength_a: Strength multiplier for all layers from LoRA A (default 1.0)
        strength_b: Strength multiplier for all layers from LoRA B (default 1.0)
        sd_scripts_path: Not used but kept for consistency
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Validate inputs
        if not os.path.exists(lora_a_path):
            return False, f"LoRA A file not found: {lora_a_path}"
        
        if not os.path.exists(lora_b_path):
            return False, f"LoRA B file not found: {lora_b_path}"
        
        if not layers_from_a and not layers_from_b:
            return False, "No layers selected for merging"
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        print(f"🔀 Loading LoRAs for selective merge")
        print(f"📁 LoRA A: {lora_a_path} (strength: {strength_a})")
        print(f"📁 LoRA B: {lora_b_path} (strength: {strength_b})")
        print(f"🔵 Layers from A: {layers_from_a}")
        print(f"🔴 Layers from B: {layers_from_b}")
        
        # Load both LoRAs
        merged_tensors = {}
        merged_metadata = {}
        
        # Statistics
        tensors_from_a = 0
        tensors_from_b = 0
        total_tensors = 0
        
        # First, load LoRA A and copy selected layers
        with safe_open(lora_a_path, framework="pt", device="cpu") as f_a:
            # Copy metadata from A as base
            if f_a.metadata():
                merged_metadata.update(f_a.metadata())
            
            all_keys_a = list(f_a.keys())
            print(f"📊 LoRA A has {len(all_keys_a)} tensors")
            
            for key in all_keys_a:
                tensor = f_a.get_tensor(key)
                total_tensors += 1
                
                # Check if this tensor belongs to a layer we want from A
                should_include = False
                for layer_num in layers_from_a:
                    # Use same layer patterns as targeting
                    layer_patterns = [
                        f"_layers_{layer_num}_",  # lora_te1_text_model_encoder_layers_7_
                        f"_blocks_{layer_num}_",  # lora_unet_double_blocks_7_, lora_unet_single_blocks_7_
                        f"single_blocks_{layer_num}_",  # lora_unet_single_blocks_7_
                        f"double_blocks_{layer_num}_",  # lora_unet_double_blocks_7_
                    ]
                    
                    if any(pattern in key for pattern in layer_patterns):
                        should_include = True
                        tensors_from_a += 1
                        print(f"🔵 From A L{layer_num}: {key}")
                        break
                
                if should_include:
                    # Apply strength multiplier for LoRA A
                    modified_tensor = tensor.clone() * strength_a
                    merged_tensors[key] = modified_tensor
        
        # Then, load LoRA B and copy selected layers
        with safe_open(lora_b_path, framework="pt", device="cpu") as f_b:
            all_keys_b = list(f_b.keys())
            print(f"📊 LoRA B has {len(all_keys_b)} tensors")
            
            for key in all_keys_b:
                tensor = f_b.get_tensor(key)
                
                # Check if this tensor belongs to a layer we want from B
                should_include = False
                for layer_num in layers_from_b:
                    # Use same layer patterns as targeting
                    layer_patterns = [
                        f"_layers_{layer_num}_",  # lora_te1_text_model_encoder_layers_7_
                        f"_blocks_{layer_num}_",  # lora_unet_double_blocks_7_, lora_unet_single_blocks_7_
                        f"single_blocks_{layer_num}_",  # lora_unet_single_blocks_7_
                        f"double_blocks_{layer_num}_",  # lora_unet_double_blocks_7_
                    ]
                    
                    if any(pattern in key for pattern in layer_patterns):
                        should_include = True
                        tensors_from_b += 1
                        print(f"🔴 From B L{layer_num}: {key}")
                        break
                
                if should_include:
                    # Check for conflicts (same tensor name from both LoRAs)
                    if key in merged_tensors:
                        print(f"⚠️ Conflict detected: {key} exists in both LoRAs, using version from B")
                    # Apply strength multiplier for LoRA B
                    modified_tensor = tensor.clone() * strength_b
                    merged_tensors[key] = modified_tensor
        
        print(f"✅ Merge statistics:")
        print(f"   Tensors from A: {tensors_from_a}")
        print(f"   Tensors from B: {tensors_from_b}")
        print(f"   Total merged: {len(merged_tensors)}")
        
        if len(merged_tensors) == 0:
            return False, "No tensors were selected for merging. Check layer selection."
        
        # Add merge info to metadata
        merged_metadata["lora_algebra_merge_type"] = "selective_layer_merge"
        merged_metadata["lora_algebra_source_a"] = os.path.basename(lora_a_path)
        merged_metadata["lora_algebra_source_b"] = os.path.basename(lora_b_path)
        merged_metadata["lora_algebra_layers_from_a"] = ",".join(map(str, layers_from_a))
        merged_metadata["lora_algebra_layers_from_b"] = ",".join(map(str, layers_from_b))
        merged_metadata["lora_algebra_strength_a"] = str(strength_a)
        merged_metadata["lora_algebra_strength_b"] = str(strength_b)
        
        # Save the merged LoRA
        print(f"💾 Saving merged LoRA to: {output_path}")
        save_file(merged_tensors, output_path, metadata=merged_metadata)
        
        # Create detailed report
        report = f"""✅ Selective layer merge completed successfully!

📊 MERGE STATISTICS:
Source A: {os.path.basename(lora_a_path)} @ {strength_a}x strength
Source B: {os.path.basename(lora_b_path)} @ {strength_b}x strength
Tensors from A: {tensors_from_a}
Tensors from B: {tensors_from_b}
Total merged tensors: {len(merged_tensors)}

🔵 Layers from A: {layers_from_a}
🔴 Layers from B: {layers_from_b}
⚡ Strength multipliers: A={strength_a}x, B={strength_b}x

💾 Output saved to: {output_path}

🎯 HYBRID LoRA CREATED:
This LoRA combines the best aspects of both source LoRAs with surgical precision and custom strength control. Each layer was carefully selected and scaled to create the perfect hybrid for your specific use case."""
        
        return True, report
        
    except Exception as e:
        return False, f"Error during selective layer merge: {str(e)}"

def deep_layer_analysis(
    lora_path: str,
    user_goal: str = "Keep maximum flexibility (works with any style)",
    sd_scripts_path: Optional[str] = None
) -> Tuple[bool, dict]:
    """Perform deep analysis of LoRA layer patterns and generate recommendations
    
    Args:
        lora_path: Path to LoRA file
        user_goal: User's intended use case for tailored recommendations
        sd_scripts_path: Not used but kept for consistency
        
    Returns:
        Tuple of (success: bool, analysis_dict: dict)
    """
    try:
        import numpy as np
        
        if not os.path.exists(lora_path):
            return False, {"error": f"LoRA file not found: {lora_path}"}
        
        print(f"🧠 Starting deep layer analysis: {lora_path}")
        print(f"🎯 User goal: {user_goal}")
        
        # Initialize analysis structures
        layer_stats = {}
        te_layers = {}      # Text Encoder layers 0-11
        double_layers = {}  # Double Block layers 0-19
        single_layers = {}  # Single Block layers 0-37
        
        all_tensors = []
        total_tensors = 0
        
        # Load and analyze all tensors
        with safe_open(lora_path, framework="pt", device="cpu") as f:
            all_keys = list(f.keys())
            total_tensors = len(all_keys)
            
            print(f"📊 Analyzing {total_tensors} tensors...")
            
            for key in all_keys:
                tensor = f.get_tensor(key)
                all_tensors.append(tensor)
                
                # Calculate tensor statistics
                tensor_stats = {
                    'mean_abs': float(torch.mean(torch.abs(tensor)).item()),
                    'std': float(torch.std(tensor).item()),
                    'max_abs': float(torch.max(torch.abs(tensor)).item()),
                    'frobenius_norm': float(torch.norm(tensor, 'fro').item()),
                    'sparsity': float((tensor == 0).sum().item() / tensor.numel()),
                    'tensor_size': tensor.numel(),
                    'shape': list(tensor.shape)
                }
                
                # Classify by layer type and number
                layer_num = None
                layer_type = None
                
                # Text Encoder layers
                if 'te1_text_model_encoder_layers_' in key:
                    import re
                    match = re.search(r'layers_(\d+)_', key)
                    if match:
                        layer_num = int(match.group(1))
                        layer_type = 'te'
                        if layer_num not in te_layers:
                            te_layers[layer_num] = {'tensors': [], 'stats': []}
                        te_layers[layer_num]['tensors'].append(key)
                        te_layers[layer_num]['stats'].append(tensor_stats)
                
                # UNet Double Block layers
                elif 'unet_double_blocks_' in key:
                    import re
                    match = re.search(r'blocks_(\d+)_', key)
                    if match:
                        layer_num = int(match.group(1))
                        layer_type = 'double'
                        if layer_num not in double_layers:
                            double_layers[layer_num] = {'tensors': [], 'stats': []}
                        double_layers[layer_num]['tensors'].append(key)
                        double_layers[layer_num]['stats'].append(tensor_stats)
                
                # UNet Single Block layers
                elif 'unet_single_blocks_' in key:
                    import re
                    match = re.search(r'blocks_(\d+)_', key)
                    if match:
                        layer_num = int(match.group(1))
                        layer_type = 'single'
                        if layer_num not in single_layers:
                            single_layers[layer_num] = {'tensors': [], 'stats': []}
                        single_layers[layer_num]['tensors'].append(key)
                        single_layers[layer_num]['stats'].append(tensor_stats)
        
        # Aggregate layer statistics
        def aggregate_layer_stats(layer_dict):
            aggregated = {}
            for layer_num, data in layer_dict.items():
                stats_list = data['stats']
                if stats_list:
                    aggregated[layer_num] = {
                        'tensor_count': len(stats_list),
                        'total_magnitude': sum(s['frobenius_norm'] for s in stats_list),
                        'avg_magnitude': sum(s['frobenius_norm'] for s in stats_list) / len(stats_list),
                        'max_magnitude': max(s['frobenius_norm'] for s in stats_list),
                        'total_parameters': sum(s['tensor_size'] for s in stats_list),
                        'avg_sparsity': sum(s['sparsity'] for s in stats_list) / len(stats_list)
                    }
            return aggregated
        
        te_aggregated = aggregate_layer_stats(te_layers)
        double_aggregated = aggregate_layer_stats(double_layers)
        single_aggregated = aggregate_layer_stats(single_layers)
        
        # Detect patterns and anomalies
        known_facial_layers = [7, 12, 16, 20]
        
        # Find layers with unusually high magnitude (potential overtraining)
        suspicious_layers = []
        
        # Check for facial data in non-facial layers
        if single_aggregated:
            # Calculate baseline from known facial layers
            facial_magnitudes = [single_aggregated.get(layer, {}).get('avg_magnitude', 0) 
                               for layer in known_facial_layers if layer in single_aggregated]
            
            if facial_magnitudes:
                facial_baseline = np.mean(facial_magnitudes)
                facial_std = np.std(facial_magnitudes) if len(facial_magnitudes) > 1 else facial_baseline * 0.3
                
                # Check all layers for suspicious activity
                for layer_num, stats in single_aggregated.items():
                    if layer_num not in known_facial_layers:
                        if stats['avg_magnitude'] > facial_baseline * 0.7:  # 70% of facial layer magnitude
                            confidence = min(100, (stats['avg_magnitude'] / facial_baseline) * 100)
                            suspicious_layers.append({
                                'layer': layer_num,
                                'type': 'single',
                                'magnitude': stats['avg_magnitude'],
                                'confidence': confidence,
                                'reason': 'High magnitude suggesting facial data'
                            })
        
        # Generate analysis report
        analysis = {
            'file_info': {
                'path': lora_path,
                'filename': os.path.basename(lora_path),
                'file_size_mb': round(os.path.getsize(lora_path) / (1024 * 1024), 2),
                'total_tensors': total_tensors
            },
            'layer_distribution': {
                'text_encoder': len(te_aggregated),
                'double_blocks': len(double_aggregated), 
                'single_blocks': len(single_aggregated)
            },
            'layer_stats': {
                'text_encoder': te_aggregated,
                'double_blocks': double_aggregated,
                'single_blocks': single_aggregated
            },
            'pattern_analysis': {
                'known_facial_layers': known_facial_layers,
                'suspicious_layers': suspicious_layers,
                'overtraining_detected': len(suspicious_layers) > 0
            },
            'user_goal': user_goal,
            'analysis_timestamp': str(torch.rand(1).item())  # Simple timestamp
        }
        
        print(f"✅ Analysis complete: {len(suspicious_layers)} suspicious layers detected")
        
        return True, analysis
        
    except Exception as e:
        print(f"❌ Error during deep analysis: {str(e)}")
        return False, {"error": f"Analysis failed: {str(e)}"}

def generate_recommendations(analysis_result: dict) -> str:
    """Generate contextual recommendations based on analysis and user goals"""
    
    if "error" in analysis_result:
        return f"**❌ Analysis Error**\n\n{analysis_result['error']}"
    
    user_goal = analysis_result.get('user_goal', 'Keep maximum flexibility (works with any style)')
    suspicious_layers = analysis_result.get('pattern_analysis', {}).get('suspicious_layers', [])
    overtraining = analysis_result.get('pattern_analysis', {}).get('overtraining_detected', False)
    
    recommendations = []
    
    # Header based on analysis
    if overtraining:
        recommendations.append("## ⚠️ **Overtraining Detected**\n")
        recommendations.append(f"Found facial data in {len(suspicious_layers)} non-standard layers.\n")
    else:
        recommendations.append("## ✅ **Clean LoRA Structure**\n")
        recommendations.append("No obvious overtraining patterns detected.\n")
    
    # Goal-specific recommendations
    recommendations.append(f"### 🎯 **Recommendations for: {user_goal}**\n")
    
    if user_goal == "Keep maximum flexibility (works with any style)":
        if overtraining:
            recommendations.append("**For Maximum Flexibility:**")
            recommendations.append("- Use **🎨 Style Layers** preset to remove facial data from non-facial layers")
            recommendations.append("- This will prevent interference when combining with style LoRAs")
            recommendations.append(f"- Specifically target layers: {', '.join(str(l['layer']) for l in suspicious_layers)}")
            recommendations.append("- **Why:** Facial data in style layers causes conflicts with artistic LoRAs\n")
        else:
            recommendations.append("**Your LoRA looks clean!**")
            recommendations.append("- No changes needed for maximum flexibility")
            recommendations.append("- Should work well with most style LoRAs")
            recommendations.append("- Consider light targeting (7,12,16,20) only if you experience conflicts\n")
    
    elif user_goal == "Preserve strong character identity":
        if overtraining:
            recommendations.append("**For Strong Character Preservation:**")
            recommendations.append("- Use **👤🔥 Facial Priority** preset to keep ALL facial data")
            recommendations.append("- Include standard layers (7,12,16,20) PLUS detected layers")
            recommendations.append(f"- Keep layers: 7,12,16,20,{','.join(str(l['layer']) for l in suspicious_layers)}")
            recommendations.append("- **Trade-off:** Strong identity but may conflict with style LoRAs")
            recommendations.append("- **Why:** Preserves all facial information for maximum character fidelity\n")
        else:
            recommendations.append("**For Character Preservation:**")
            recommendations.append("- Use standard **👤🎨 Face A + Style B** when merging")
            recommendations.append("- Your LoRA has clean facial separation")
            recommendations.append("- Should preserve identity well without modifications\n")
    
    elif user_goal == "Fix overtraining issues":
        if overtraining:
            recommendations.append("**Overtraining Fix Strategy:**")
            recommendations.append("- Use **🔥 Aggressive** preset in Layer Targeting")
            recommendations.append("- Target ALL detected problematic layers")
            recommendations.append(f"- Mute layers: {', '.join(str(l['layer']) for l in suspicious_layers)}")
            for layer_info in suspicious_layers:
                recommendations.append(f"  - Layer {layer_info['layer']}: {layer_info['reason']} ({layer_info['confidence']:.0f}% confidence)")
            recommendations.append("- **Result:** Cleaner LoRA with proper layer separation\n")
        else:
            recommendations.append("**No Overtraining Detected:**")
            recommendations.append("- Your LoRA appears well-trained")
            recommendations.append("- No fixing needed")
            recommendations.append("- Layer separation looks appropriate\n")
    
    elif user_goal == "Understand layer distribution":
        layer_stats = analysis_result.get('layer_stats', {})
        recommendations.append("**Layer Distribution Analysis:**")
        
        if layer_stats.get('text_encoder'):
            recommendations.append(f"- **Text Encoder:** {len(layer_stats['text_encoder'])} active layers")
        if layer_stats.get('double_blocks'):
            recommendations.append(f"- **Double Blocks:** {len(layer_stats['double_blocks'])} active layers")
        if layer_stats.get('single_blocks'):
            recommendations.append(f"- **Single Blocks:** {len(layer_stats['single_blocks'])} active layers")
        
        if suspicious_layers:
            recommendations.append("\n**Unusual Activity:**")
            for layer_info in suspicious_layers:
                recommendations.append(f"- Layer {layer_info['layer']}: {layer_info['reason']}")
        
        recommendations.append("\n**Layer Function Reference:**")
        recommendations.append("- Layers 7,12,16,20: Standard facial features")
        recommendations.append("- Layers 0-6: Early structure/composition")
        recommendations.append("- Layers 21-37: Fine details/textures")
    
    # Add specific action items
    recommendations.append("\n### 🔧 **Recommended Actions:**\n")
    
    if overtraining and user_goal != "Preserve strong character identity":
        recommendations.append("1. **Immediate:** Use Layer Targeting to clean detected layers")
        recommendations.append("2. **Test:** Check if targeted LoRA works better with style combinations")
        recommendations.append("3. **Compare:** A/B test original vs cleaned version")
    else:
        recommendations.append("1. **Current LoRA:** Appears suitable for your goal")
        recommendations.append("2. **Optional:** Light targeting if you experience conflicts")
        recommendations.append("3. **Monitor:** Watch for style conflicts in actual use")
    
    return "\n".join(recommendations)

def create_layer_heatmap(analysis_result: dict):
    """Create a visual heatmap of layer magnitudes"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        if "error" in analysis_result:
            return None
        
        layer_stats = analysis_result.get('layer_stats', {})
        
        # Prepare data for heatmap
        single_blocks = layer_stats.get('single_blocks', {})
        double_blocks = layer_stats.get('double_blocks', {})
        te_blocks = layer_stats.get('text_encoder', {})
        
        # Create magnitude arrays
        single_mags = [single_blocks.get(i, {}).get('avg_magnitude', 0) for i in range(38)]
        double_mags = [double_blocks.get(i, {}).get('avg_magnitude', 0) for i in range(20)]
        te_mags = [te_blocks.get(i, {}).get('avg_magnitude', 0) for i in range(12)]
        
        # Create the plot
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 8))
        
        # Single blocks heatmap
        ax1.bar(range(38), single_mags, color=['red' if i in [7,12,16,20] else 'lightblue' for i in range(38)])
        ax1.set_title('Single Block Layers (0-37)')
        ax1.set_ylabel('Magnitude')
        ax1.set_xticks(range(0, 38, 5))
        
        # Double blocks heatmap  
        ax2.bar(range(20), double_mags, color=['red' if i in [7,12,16] else 'lightgreen' for i in range(20)])
        ax2.set_title('Double Block Layers (0-19)')
        ax2.set_ylabel('Magnitude')
        ax2.set_xticks(range(0, 20, 2))
        
        # Text encoder heatmap
        ax3.bar(range(12), te_mags, color=['red' if i == 7 else 'lightyellow' for i in range(12)])
        ax3.set_title('Text Encoder Layers (0-11)')
        ax3.set_ylabel('Magnitude')
        ax3.set_xlabel('Layer Number')
        ax3.set_xticks(range(12))
        
        plt.tight_layout()
        plt.suptitle(f"Layer Magnitude Analysis - {analysis_result['file_info']['filename']}", y=0.98)
        
        return fig
        
    except Exception as e:
        print(f"Error creating heatmap: {e}")
        return None