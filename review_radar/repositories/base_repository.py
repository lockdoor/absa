"""
Base Repository

Abstract base class สำหรับทุก repository classes
ให้ common functionality สำหรับ validation และ logging
"""

from abc import ABC
from typing import Any, Optional
from logging import Logger


class BaseRepository(ABC):
    """
    Abstract base class สำหรับ repositories
    
    Provides common functionality:
    - Validation helpers
    - Logging helpers
    """
    
    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize BaseRepository
        
        Args:
            logger: Optional logger instance
        """
        self._logger = logger
    
    @property
    def logger(self) -> Optional[Logger]:
        """Get logger (read-only)"""
        return self._logger
    
    def _log(self, message: str, level: str = "info", **kwargs) -> None:
        """
        Helper method for logging
        
        Args:
            message: Log message
            level: Log level (debug, info, warning, error)
            **kwargs: Additional context for structured logging
        """
        if self._logger:
            log_method = getattr(self._logger, level, self._logger.info)
            log_method(message, extra=kwargs)
    
    def _validate_not_none(self, value: Any, param_name: str) -> None:
        """
        Validate that value is not None
        
        Args:
            value: Value to validate
            param_name: Parameter name for error message
        
        Raises:
            ValueError: If value is None
        """
        if value is None:
            raise ValueError(f"{param_name} cannot be None")
    
    def _validate_positive(self, value: int, param_name: str) -> None:
        """
        Validate that value is positive
        
        Args:
            value: Value to validate
            param_name: Parameter name for error message
        
        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"{param_name} must be positive")
