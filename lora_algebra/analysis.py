"""
LoRA analysis and compatibility prediction
"""

import os
from typing import List, Dict, Any, Tuple
from .core import LoRAProcessor

def extract_metadata(lora_path: str) -> Dict[str, Any]:
    """Extract metadata from a LoRA file
    
    Args:
        lora_path: Path to LoRA file
        
    Returns:
        Dictionary containing metadata
    """
    processor = LoRAProcessor()
    return processor.extract_metadata(lora_path) or {}

def predict_compatibility(lora_a_path: str, lora_b_path: str) -> Dict[str, Any]:
    """Predict compatibility between two LoRAs
    
    Args:
        lora_a_path: Path to first LoRA
        lora_b_path: Path to second LoRA
        
    Returns:
        Dictionary containing compatibility analysis
    """
    processor = LoRAProcessor()
    
    metadata_a = processor.extract_metadata(lora_a_path)
    metadata_b = processor.extract_metadata(lora_b_path)
    
    if not metadata_a or not metadata_b:
        return {
            "compatible": False,
            "confidence": 0.0,
            "issues": ["Could not extract metadata from one or both LoRAs"],
            "recommendations": ["Check that both files are valid LoRA .safetensors files"]
        }
    
    issues = []
    recommendations = []
    compatibility_score = 1.0
    
    # Check rank compatibility
    rank_a = metadata_a.get('network_dim', 32)
    rank_b = metadata_b.get('network_dim', 32)
    
    if abs(rank_a - rank_b) > 64:
        issues.append(f"Large rank difference: {rank_a} vs {rank_b}")
        recommendations.append("Consider using concat mode when merging")
        compatibility_score -= 0.2
    
    # Check alpha compatibility
    alpha_a = metadata_a.get('network_alpha', 32.0)
    alpha_b = metadata_b.get('network_alpha', 32.0)
    
    alpha_ratio = max(alpha_a, alpha_b) / min(alpha_a, alpha_b) if min(alpha_a, alpha_b) > 0 else 1.0
    
    if alpha_ratio > 2.0:
        issues.append(f"Very different alpha values: {alpha_a} vs {alpha_b}")
        recommendations.append("May need strength adjustment when combining")
        compatibility_score -= 0.1
    
    # Check base model compatibility
    base_a = metadata_a.get('base_model', '').lower()
    base_b = metadata_b.get('base_model', '').lower()
    
    if base_a and base_b and base_a != base_b:
        if 'flux' in base_a and 'flux' in base_b:
            # Both are Flux models, probably compatible
            pass
        elif 'sd' in base_a and 'sd' in base_b:
            # Both are SD models, check version compatibility
            if '1.5' in base_a and 'xl' in base_b or 'xl' in base_a and '1.5' in base_b:
                issues.append(f"Different SD versions: {base_a} vs {base_b}")
                recommendations.append("These LoRAs may not be compatible - consider training on same base model")
                compatibility_score -= 0.5
        else:
            issues.append(f"Different model families: {base_a} vs {base_b}")
            recommendations.append("Cross-model LoRAs may not work well together")
            compatibility_score -= 0.3
    
    # Rank efficiency analysis
    efficiency_a = alpha_a / rank_a if rank_a > 0 else 1.0
    efficiency_b = alpha_b / rank_b if rank_b > 0 else 1.0
    
    if abs(efficiency_a - efficiency_b) > 1.0:
        issues.append("Different training efficiencies detected")
        recommendations.append("Consider adjusting relative strengths when combining")
        compatibility_score -= 0.1
    
    # Overall assessment
    if compatibility_score > 0.8:
        status = "Highly Compatible"
        confidence = compatibility_score
    elif compatibility_score > 0.6:
        status = "Compatible with Adjustments"
        confidence = compatibility_score
    elif compatibility_score > 0.4:
        status = "Limited Compatibility"
        confidence = compatibility_score
        recommendations.append("Consider using LoRA difference to resolve conflicts")
    else:
        status = "Incompatible"
        confidence = compatibility_score
        recommendations.append("Strong recommendation to use LoRA difference for conflict resolution")
    
    if not issues:
        issues.append("No major compatibility issues detected")
    
    if not recommendations:
        recommendations.append("LoRAs should work well together with standard strengths")
    
    return {
        "compatible": compatibility_score > 0.4,
        "status": status,
        "confidence": round(confidence, 2),
        "compatibility_score": round(compatibility_score, 2),
        "issues": issues,
        "recommendations": recommendations,
        "metadata_a": metadata_a,
        "metadata_b": metadata_b,
        "suggested_strengths": {
            "lora_a": min(1.0, 1.0 * compatibility_score + 0.2),
            "lora_b": min(1.0, 1.0 * compatibility_score + 0.2)
        }
    }

def analyze_multiple_loras(lora_paths: List[str]) -> Dict[str, Any]:
    """Analyze compatibility between multiple LoRAs
    
    Args:
        lora_paths: List of paths to LoRA files
        
    Returns:
        Dictionary containing multi-LoRA analysis
    """
    if len(lora_paths) < 2:
        return {"error": "Need at least 2 LoRAs for compatibility analysis"}
    
    # Extract metadata for all LoRAs
    processor = LoRAProcessor()
    lora_metadata = []
    
    for path in lora_paths:
        metadata = processor.extract_metadata(path)
        if metadata:
            metadata['path'] = path
            lora_metadata.append(metadata)
    
    if len(lora_metadata) < 2:
        return {"error": "Could not extract metadata from enough LoRAs"}
    
    # Build compatibility matrix
    compatibility_matrix = {}
    overall_issues = []
    
    for i, lora_a in enumerate(lora_metadata):
        for j, lora_b in enumerate(lora_metadata):
            if i < j:  # Only check each pair once
                key = f"{os.path.basename(lora_a['path'])} × {os.path.basename(lora_b['path'])}"
                compat = predict_compatibility(lora_a['path'], lora_b['path'])
                compatibility_matrix[key] = compat
                
                if not compat['compatible']:
                    overall_issues.extend(compat['issues'])
    
    # Calculate overall compatibility
    scores = [result['compatibility_score'] for result in compatibility_matrix.values()]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    # Recommendations for multi-LoRA usage
    recommendations = []
    
    if avg_score > 0.7:
        recommendations.append("All LoRAs show good compatibility - can be used together")
    elif avg_score > 0.5:
        recommendations.append("Some LoRAs may conflict - consider adjusting strengths")
        recommendations.append("Use LoRA difference to resolve specific conflicts")
    else:
        recommendations.append("Multiple compatibility issues detected")
        recommendations.append("Strong recommendation to use LoRA difference workflow")
        recommendations.append("Consider processing LoRAs in pairs before combining all")
    
    return {
        "lora_count": len(lora_metadata),
        "overall_compatibility": avg_score > 0.5,
        "average_score": round(avg_score, 2),
        "compatibility_matrix": compatibility_matrix,
        "overall_issues": list(set(overall_issues)),  # Remove duplicates
        "recommendations": recommendations,
        "metadata": lora_metadata
    }