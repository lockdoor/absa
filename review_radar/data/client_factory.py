"""Factory for creating dataset instances"""

from typing import Any, Dict, Optional
from .base_client import BaseClient


class ClientFactory:
    """Factory for creating appropriate dataset instances based on client type"""
    
    # Registry of dataset classes
    _registry: Dict[str, type] = {}
    
    @classmethod
    def register(cls, client_type: str):
        """Decorator to register dataset classes"""
        def decorator(dataset_class: type):
            cls._registry[client_type] = dataset_class
            return dataset_class
        return decorator
    
    @classmethod
    def create(
        cls,
        client: Any,
        client_type: Optional[str] = None,
        **kwargs
    ) -> BaseClient:
        """
        Create dataset instance based on client type
        
        Args:
            client: Database client instance
            client_type: Type of client ('supabase', 'postgres', 'mongodb', etc.)
                        If None, will try to auto-detect
            **kwargs: Additional arguments for dataset initialization
        
        Returns:
            BaseDataset instance
        
        Examples:
            # Explicit type
            dataset = DatasetFactory.create(client, client_type='supabase')
            
            # Auto-detect
            dataset = DatasetFactory.create(client)
        """
        # Auto-detect client type if not provided
        if client_type is None:
            client_type = cls._detect_client_type(client)
        
        # Get dataset class from registry
        dataset_class = cls._registry.get(client_type)
        
        if dataset_class is None:
            raise ValueError(
                f"Unknown client type: {client_type}. "
                f"Registered types: {list(cls._registry.keys())}"
            )
        
        # Create and return dataset instance
        return dataset_class(client=client, **kwargs)
    
    @classmethod
    def _detect_client_type(cls, client: Any) -> str:
        """Auto-detect client type from client instance"""
        client_class_name = client.__class__.__name__.lower()
        
        # Detection rules
        if 'supabase' in client_class_name:
            return 'supabase'
        elif 'postgres' in client_class_name or 'psycopg' in client_class_name:
            return 'postgres'
        elif 'mongo' in client_class_name or 'pymongo' in client_class_name:
            return 'mongodb'
        elif 'mysql' in client_class_name:
            return 'mysql'
        
        # Default fallback
        raise ValueError(
            f"Cannot auto-detect client type for {client.__class__.__name__}. "
            f"Please specify client_type explicitly."
        )
    
    @classmethod
    def list_supported_types(cls) -> list:
        """List all registered client types"""
        return list(cls._registry.keys())


# Convenience function
def create_dataset(
    client: Any,
    client_type: Optional[str] = None,
    **kwargs
) -> BaseClient:
    """
    Convenience function to create dataset
    
    Args:
        client: Database client instance
        client_type: Type of client (optional, will auto-detect)
        **kwargs: Additional arguments
    
    Returns:
        BaseDataset instance
    
    Examples:
        from review_radar.data import create_dataset
        
        dataset = create_dataset(supabase_client)
        dataset = create_dataset(postgres_client, client_type='postgres')
    """
    return ClientFactory.create(client, client_type, **kwargs)
