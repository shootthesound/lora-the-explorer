"""
Utility functions for LoRA operations
"""

import os
import re
from typing import List, Tuple, Optional
from pathlib import Path

def find_lora_files(directory: str, recursive: bool = True) -> List[str]:
    """Find all LoRA files in a directory
    
    Args:
        directory: Directory to search
        recursive: Whether to search subdirectories
        
    Returns:
        List of LoRA file paths
    """
    lora_files = []
    search_pattern = "**/*.safetensors" if recursive else "*.safetensors"
    
    try:
        directory_path = Path(directory)
        if directory_path.exists():
            for file_path in directory_path.glob(search_pattern):
                if file_path.is_file():
                    lora_files.append(str(file_path))
    except Exception as e:
        print(f"Error searching directory {directory}: {e}")
    
    return sorted(lora_files)

def validate_lora_path(path: str) -> Tuple[bool, str]:
    """Validate that a path points to a valid LoRA file
    
    Args:
        path: Path to validate
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not path:
        return False, "Path is empty"
    
    if not os.path.exists(path):
        return False, f"File does not exist: {path}"
    
    if not path.lower().endswith('.safetensors'):
        return False, "File must be a .safetensors file"
    
    if not os.path.isfile(path):
        return False, "Path is not a file"
    
    # Check file size (LoRAs should be at least 1KB, typically much larger)
    try:
        size = os.path.getsize(path)
        if size < 1024:  # Less than 1KB
            return False, "File is too small to be a valid LoRA"
    except Exception as e:
        return False, f"Could not check file size: {e}"
    
    return True, "Valid LoRA file"

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe use across different operating systems
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    
    # Truncate if too long (255 chars is common limit)
    if len(filename) > 200:  # Leave room for extension
        filename = filename[:200]
    
    return filename

def generate_output_path(base_dir: str, name: str, operation: str = "processed") -> str:
    """Generate a safe output path for processed LoRAs
    
    Args:
        base_dir: Base directory for output
        name: Base name for the file
        operation: Type of operation (for naming)
        
    Returns:
        Full output path
    """
    # Sanitize the name
    safe_name = sanitize_filename(name)
    
    # Add operation suffix
    if operation != "processed":
        safe_name = f"{safe_name}_{operation}"
    
    # Ensure .safetensors extension
    if not safe_name.lower().endswith('.safetensors'):
        safe_name += '.safetensors'
    
    # Create full path
    output_path = os.path.join(base_dir, safe_name)
    
    # Handle name conflicts by adding numbers
    counter = 1
    original_path = output_path
    while os.path.exists(output_path):
        base, ext = os.path.splitext(original_path)
        output_path = f"{base}_{counter}{ext}"
        counter += 1
    
    return output_path

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def get_recent_loras(directory: str, limit: int = 10) -> List[Tuple[str, str, float]]:
    """Get recently modified LoRA files
    
    Args:
        directory: Directory to search
        limit: Maximum number of files to return
        
    Returns:
        List of tuples (path, name, modification_time)
    """
    lora_files = find_lora_files(directory, recursive=True)
    
    # Get modification times and sort
    file_info = []
    for file_path in lora_files:
        try:
            mod_time = os.path.getmtime(file_path)
            name = os.path.basename(file_path)
            file_info.append((file_path, name, mod_time))
        except Exception:
            continue  # Skip files we can't access
    
    # Sort by modification time (newest first) and limit
    file_info.sort(key=lambda x: x[2], reverse=True)
    return file_info[:limit]

def estimate_processing_time(lora_paths: List[str], operation: str = "subtract") -> float:
    """Estimate processing time for LoRA operations
    
    Args:
        lora_paths: List of LoRA file paths
        operation: Type of operation
        
    Returns:
        Estimated time in seconds
    """
    if not lora_paths:
        return 0.0
    
    # Base processing time per operation
    base_times = {
        "subtract": 3.0,
        "merge": 2.5,
        "analyze": 1.0
    }
    
    base_time = base_times.get(operation, 2.0)
    
    # Adjust based on file sizes
    total_size = 0
    for path in lora_paths:
        if os.path.exists(path):
            total_size += os.path.getsize(path)
    
    # Add time based on file size (rough estimate)
    size_factor = (total_size / (1024 * 1024)) * 0.1  # 0.1 seconds per MB
    
    return base_time + size_factor

def create_backup(file_path: str, backup_dir: Optional[str] = None) -> str:
    """Create a backup of a file
    
    Args:
        file_path: Path to file to backup
        backup_dir: Directory for backup (default: same directory)
        
    Returns:
        Path to backup file
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Determine backup directory
    if backup_dir is None:
        backup_dir = os.path.dirname(file_path)
    else:
        os.makedirs(backup_dir, exist_ok=True)
    
    # Generate backup filename
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    
    import time
    timestamp = int(time.time())
    backup_name = f"{name}_backup_{timestamp}{ext}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # Copy file
    import shutil
    shutil.copy2(file_path, backup_path)
    
    return backup_path