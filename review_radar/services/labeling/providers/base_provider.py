"""
Base LLM Provider for Auto-Labeling

Abstract base class for LLM providers (OpenAI, Gemini, etc.)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LabelResult:
    """Result from LLM labeling operation"""
    labels: Dict[str, Any]  # Extracted labels (sentiment, aspects, etc.)
    metadata: Dict[str, Any]  # Provider metadata (model, timestamp, etc.)

    def to_dict(self) -> Dict[str, Any]:
        """Convert LabelResult to dictionary"""
        return {
            'labels': self.labels,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """Convert LabelResult to JSON string"""
        import json
        return json.dumps(self.to_dict())


class BaseLabelingProvider(ABC):
    """
    Abstract base class for LLM labeling providers
    
    Subclasses must implement:
    - label_review(): Send review to LLM and get labels
    - get_model_info(): Return model information
    """
    
    def __init__(self, logger=None):
        """
        Initialize provider
        
        Args:
            logger: Optional logger instance
        """
        self.model_id = "base-provider"
        self.logger = logger
        self.total_requests = 0
        self.total_token_usage = 0
    
    @abstractmethod
    def ark_llm(self, text: str, aspects: List[str]) -> List[float | None]:
        """
        Send review to LLM and get labels
        
        Args:
            text: Review text
            aspects: List of aspects to extract
        
        Returns:
            List of scores: [aspect1_score, aspect2_score, ..., overall_confidence]
            - Each aspect score: -1.0 (negative) to 1.0 (positive), or None (not found)
            - Last value: overall confidence 0.0 to 1.0
        """
        pass
  
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get model information
        
        Returns:
            Dict with model name, version, etc.
        """
        pass

    @abstractmethod
    def parser_label(self, llm_response: str) -> Any:
        """
        Parse LLM response to extract scores
        
        Args:
            llm_response: Raw response string from LLM
        
        Returns:
            Parsed scores list
        """
        pass

    @abstractmethod
    def process_label(self, text: str) -> LabelResult:
        """
        Process labeling for a single review
        
        Args:
            text: Review text
        
        Returns:
            LabelResult with extracted labels
        
        Raises:
            ValueError: If LLM response validation fails
        """
        pass
    
    def _log(self, message: str, level: str = "info", **kwargs):
        """Helper method for logging"""
        if self.logger:
            log_method = getattr(self.logger, level, self.logger.info)
            log_method(message, extra=kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            'total_requests': self.total_requests,
            'total_token_usage': self.total_token_usage,
            'avg_token_usage_per_request': self.total_token_usage / self.total_requests if self.total_requests > 0 else 0.0
        }
    
    def reset_stats(self):
        """Reset statistics counters"""
        self.total_requests = 0
        self.total_token_usage = 0
