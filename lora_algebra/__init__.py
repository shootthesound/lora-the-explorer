"""
LoRA Algebra: Advanced LoRA Manipulation Toolkit

Revolutionary LoRA manipulation toolkit enabling mathematical operations 
on Low-Rank Adaptation models for unprecedented compatibility and control.
"""

__version__ = "1.0.0"
__author__ = "LoRA Algebra Team"
__license__ = "MIT"

from .core import LoRAProcessor
from .operations import subtract_loras, merge_loras, analyze_lora
from .analysis import extract_metadata, predict_compatibility

__all__ = [
    "LoRAProcessor",
    "subtract_loras",
    "merge_loras", 
    "analyze_lora",
    "extract_metadata",
    "predict_compatibility"
]