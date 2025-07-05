"""
Simple global LoRA cache for autocomplete functionality
"""

import os
import json
from typing import List, Optional, Tuple
from .utils import find_lora_files

class LoRACache:
    """Simple cache to store discovered LoRA file paths"""
    
    def __init__(self):
        self.lora_paths: List[str] = []
        self.scan_directory: Optional[str] = None
        self.default_output_path: Optional[str] = None
        self.settings_file = os.path.join(os.path.expanduser("~"), ".lora_algebra_settings.json")
        self.load_settings()
        
    def scan_directory_for_loras(self, directory: str) -> Tuple[bool, str]:
        """Scan a directory for LoRA files and cache the results
        
        Args:
            directory: Directory path to scan
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not os.path.exists(directory):
                return False, f"Directory does not exist: {directory}"
            
            if not os.path.isdir(directory):
                return False, f"Path is not a directory: {directory}"
            
            # Use existing utility function to find LoRA files recursively
            found_files = find_lora_files(directory, recursive=True)
            
            # Clear only the old paths, not the directory
            self.lora_paths = []
            
            # Update cache with new data
            self.lora_paths = found_files
            self.scan_directory = directory
            
            # Save settings
            self.save_settings()
            
            return True, f"Found {len(found_files)} LoRA files in {directory}"
            
        except Exception as e:
            return False, f"Error scanning directory: {str(e)}"
    
    def get_matching_loras(self, query: str) -> List[str]:
        """Get LoRA paths that match the query string
        
        Args:
            query: Search string to match against
            
        Returns:
            List of matching LoRA file paths
        """
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        matches = []
        
        for lora_path in self.lora_paths:
            # Extract filename for matching
            filename = os.path.basename(lora_path).lower()
            
            # Simple contains matching
            if query_lower in filename:
                matches.append(lora_path)
        
        # Sort matches - exact filename matches first, then contains matches
        def sort_key(path):
            filename = os.path.basename(path).lower()
            if filename.startswith(query_lower):
                return (0, filename)  # Starts with query - highest priority
            else:
                return (1, filename)  # Contains query - lower priority
        
        matches.sort(key=sort_key)
        
        # Limit results to avoid UI overload
        return matches[:50]
    
    def get_cache_info(self) -> dict:
        """Get information about the current cache state"""
        return {
            "total_loras": len(self.lora_paths),
            "scan_directory": self.scan_directory,
            "has_data": len(self.lora_paths) > 0
        }
    
    def clear_cache(self):
        """Clear the cache"""
        self.lora_paths = []
        self.scan_directory = None
    
    def save_settings(self):
        """Save current settings to file"""
        try:
            settings = {
                "scan_directory": self.scan_directory,
                "default_output_path": self.default_output_path
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.scan_directory = settings.get("scan_directory")
                    self.default_output_path = settings.get("default_output_path")
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def auto_scan_on_startup(self) -> Tuple[bool, str]:
        """Automatically scan the saved directory on startup"""
        if self.scan_directory and os.path.exists(self.scan_directory):
            return self.scan_directory_for_loras(self.scan_directory)
        return False, "No saved directory to scan"
    
    def set_default_output_path(self, path: str):
        """Set and save the default output path"""
        self.default_output_path = path
        self.save_settings()
    
    def get_default_output_path(self) -> str:
        """Get the default output path or fallback"""
        return self.default_output_path or "output"

# Global cache instance
lora_cache = LoRACache()