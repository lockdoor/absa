"""
Base Data Layer

Abstract base class สำหรับ data layer ทั้งหมด
ให้ shared functionality: logging, client management
"""

from abc import ABC
from typing import Optional, Any
from logging import Logger


class BaseData(ABC):
    """
    Base class สำหรับทุก data layer classes
    
    Provides:
    - Client management (supabase, postgres, etc.)
    - Logger functionality
    - Common helper methods
    
    Subclasses:
    - ReviewData: Abstract class สำหรับ review operations
    - BatchData: Abstract class สำหรับ batch operations
    - AspectData: Abstract class สำหรับ aspect operations
    """
    
    def __init__(
        self,
        client: Any,  # SupabaseClient | PostgresClient | Any database client
        logger: Optional[Logger] = None
    ):
        """
        Initialize base data layer
        
        Args:
            client: Database client instance (supabase, postgres, etc.)
            logger: Optional logger for logging operations
        """
        self._client = client
        self._logger = logger
    
    @property
    def client(self) -> Any:
        """Get database client"""
        return self._client
    
    @property
    def logger(self) -> Optional[Logger]:
        """Get logger instance"""
        return self._logger
    
    def _log(
        self, 
        message: str, 
        level: str = "info", 
        **kwargs: Any
    ) -> None:
        """
        Log message if logger is available
        
        Args:
            message: Log message
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
            **kwargs: Additional context to include in log
        
        Example:
            self._log("Fetching reviews", batch_id=123, limit=100)
        """
        if self._logger is None:
            return
        
        log_func = getattr(self._logger, level, self._logger.info)
        log_func(message, extra=kwargs)
