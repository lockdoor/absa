"""Helper utilities"""

import json
import random
import numpy as np
import torch
from pathlib import Path
from typing import Any, Dict, Union
import torch.nn as nn


def set_seed(seed: int = 42) -> None:
    """
    Set random seed for reproducibility
    
    Args:
        seed: Random seed value
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        file_path: Path to save file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load dictionary from JSON file
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        Loaded dictionary
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_parameters(model: nn.Module) -> Dict[str, int]:
    """
    Count model parameters
    
    Args:
        model: PyTorch model
    
    Returns:
        Dictionary with parameter counts
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    non_trainable_params = total_params - trainable_params
    
    return {
        'total': total_params,
        'trainable': trainable_params,
        'non_trainable': non_trainable_params
    }


def format_time(seconds: float) -> str:
    """
    Format seconds into readable time string
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_device(prefer_gpu: bool = True) -> str:
    """
    Get available device
    
    Args:
        prefer_gpu: Whether to prefer GPU if available
    
    Returns:
        Device string ('cuda' or 'cpu')
    """
    if prefer_gpu and torch.cuda.is_available():
        return "cuda"
    return "cpu"


def print_model_summary(model: nn.Module) -> None:
    """
    Print model summary
    
    Args:
        model: PyTorch model
    """
    print("\n" + "=" * 60)
    print("Model Summary")
    print("=" * 60)
    
    param_counts = count_parameters(model)
    
    print(f"Total parameters: {param_counts['total']:,}")
    print(f"Trainable parameters: {param_counts['trainable']:,}")
    print(f"Non-trainable parameters: {param_counts['non_trainable']:,}")
    
    print("=" * 60 + "\n")
