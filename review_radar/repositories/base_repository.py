"""
Base Repository

Abstract base class for all repositories.
Repositories add domain-specific logic on top of database clients.
"""

from abc import ABC
from typing import Optional, Any
from logging import Logger
from ..data.base_client import BaseClient


class BaseRepository(ABC):
    """
    Base class for all repositories
    
    Repositories provide domain-specific data access methods
    and encapsulate business rules related to data operations.
    They use BaseClient for actual database access.
    """
    
    def __init__(
        self,
        client: BaseClient,  # BaseClient instance
        logger: Optional[Logger] = None
    ):
        """
        Initialize base repository
        
        Args:
            client: BaseClient instance for database access
            logger: Optional logger instance for logging
        """
        self.client = client
        self.logger = logger
    
    def _log(self, message: str, level: str = "info", **kwargs):
        """
        Log message if logger is available
        
        Args:
            message: Log message
            level: Log level ('debug', 'info', 'warning', 'error')
            **kwargs: Additional context to log
        """
        if self.logger:
            log_func = getattr(self.logger, level, self.logger.info)
            log_func(message, extra=kwargs)
    
    def _validate_not_none(self, value: Any, param_name: str):
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
    
    def _validate_positive(self, value: int, param_name: str):
        """
        Validate that value is positive
        
        Args:
            value: Value to validate
            param_name: Parameter name for error message
            
        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"{param_name} must be positive, got {value}")
