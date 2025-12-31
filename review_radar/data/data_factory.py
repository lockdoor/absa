"""
Data Factory

Factory pattern with singleton management สำหรับ data layer
สร้างและจัดการ data client instances (ReviewData, BatchData, AspectData)
"""

import os
from typing import Optional, Dict, Tuple, Literal
from logging import Logger

from .base_data import BaseData


DataType = Literal['review', 'batch', 'label']
ClientType = Literal['supabase', 'postgres']


class DataFactory:
    """
    Factory class สำหรับสร้างและจัดการ data layer clients
    
    Features:
    - Singleton pattern: แต่ละ (data_type, client_type) combination มี instance เดียว
    - Lazy initialization: สร้าง instance เมื่อต้องการใช้งานจริง
    - Resource management: ไม่สร้าง connection ซ้ำซ้อน
    
    Usage:
        # สร้าง ReviewData client
        review_client = DataFactory.create(data_type='review', client_type='supabase')
        
        # สร้าง BatchData client
        batch_client = DataFactory.create(data_type='batch', client_type='supabase')
        
        # Reset (สำหรับ testing)
        DataFactory.reset()
    """
    
    _instances: Dict[Tuple[str, str], BaseData] = {}
    
    @classmethod
    def create(
        cls,
        data_type: DataType = 'review',
        client_type: ClientType = 'supabase',
        logger: Optional[Logger] = None
    ) -> BaseData:
        """
        สร้างหรือ return existing instance ของ data client
        
        Args:
            data_type: ประเภทของ data ('review', 'batch')
            client_type: ประเภทของ database client ('supabase', 'postgres')
            logger: Optional logger instance
        
        Returns:
            BaseData instance (ReviewData, BatchData, หรือ AspectData)
        
        Raises:
            ValueError: ถ้า data_type หรือ client_type ไม่ถูกต้อง
            ValueError: ถ้า environment variables ไม่ครบ (สำหรับ supabase)
        
        Example:
            review_client = DataFactory.create('review', 'supabase', my_logger)
        """
        # Validate inputs
        if data_type not in ('review', 'batch', 'label'):
            raise ValueError(
                f"Invalid data_type: {data_type}. "
                f"Must be 'review', 'batch', or 'label'"
            )
        
        if client_type not in ('supabase', 'postgres'):
            raise ValueError(
                f"Invalid client_type: {client_type}. "
                f"Must be 'supabase' or 'postgres'"
            )
        
        # Check if instance already exists
        key = (data_type, client_type)
        
        if key not in cls._instances:
            cls._instances[key] = cls._create_instance(
                data_type=data_type,
                client_type=client_type,
                logger=logger
            )
        
        return cls._instances[key]
    
    @classmethod
    def _create_instance(
        cls,
        data_type: str,
        client_type: str,
        logger: Optional[Logger]
    ) -> BaseData:
        """
        สร้าง instance ใหม่ตาม data_type และ client_type
        
        Args:
            data_type: 'review' or 'batch'
            client_type: 'supabase' or 'postgres'
            logger: Optional logger
        
        Returns:
            BaseData instance
        """
        if client_type == 'supabase':
            return cls._create_supabase_instance(data_type, logger)
        elif client_type == 'postgres':
            return cls._create_postgres_instance(data_type, logger)
        else:
            raise ValueError(f"Unsupported client_type: {client_type}")
    
    @classmethod
    def _create_supabase_instance(
        cls,
        data_type: str,
        logger: Optional[Logger]
    ) -> BaseData:
        """
        สร้าง Supabase instance
        
        Args:
            data_type: 'review', 'batch', or 'label'
            logger: Optional logger
        
        Returns:
            Supabase implementation instance
        """
        # Import here to avoid circular dependency
        from supabase import create_client
        
        # Get credentials from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase credentials not found. "
                "Set SUPABASE_URL and SUPABASE_KEY environment variables."
            )
        
        # Create supabase client
        supabase_client = create_client(supabase_url, supabase_key)

        # Create appropriate data instance
        if data_type == 'review':
            from .review_data_supabase_client import ReviewDataSupabaseClient
            return ReviewDataSupabaseClient(client=supabase_client, logger=logger)
        
        elif data_type == 'batch':
            from .batch_data_supabase import BatchDataSupabaseClient
            return BatchDataSupabaseClient(client=supabase_client, logger=logger)
        
        elif data_type == 'label':
            from .label_data_supabase import LabelDataSupabaseClient
            return LabelDataSupabaseClient(client=supabase_client, logger=logger)
        
        else:
            raise ValueError(f"Unknown data_type: {data_type}")
    
    @classmethod
    def _create_postgres_instance(
        cls,
        data_type: str,
        logger: Optional[Logger]
    ) -> BaseData:
        """
        สร้าง PostgreSQL instance
        
        Args:
            data_type: 'review', 'batch', or 'aspect'
            logger: Optional logger
        
        Returns:
            PostgreSQL implementation instance
        """
        # TODO: Implement PostgreSQL clients
        raise NotImplementedError(
            "PostgreSQL clients not yet implemented. "
            "Use client_type='supabase' for now."
        )
    
    @classmethod
    def reset(cls, data_type: Optional[str] = None, client_type: Optional[str] = None):
        """
        Reset singleton instances (สำหรับ testing)
        
        Args:
            data_type: ถ้าระบุ จะ reset เฉพาะ data_type นี้
            client_type: ถ้าระบุ จะ reset เฉพาะ client_type นี้
        
        Example:
            # Reset ทั้งหมด
            DataFactory.reset()
            
            # Reset เฉพาะ review clients
            DataFactory.reset(data_type='review')
            
            # Reset เฉพาะ supabase clients
            DataFactory.reset(client_type='supabase')
            
            # Reset specific combination
            DataFactory.reset(data_type='review', client_type='supabase')
        """
        if data_type is None and client_type is None:
            # Reset all
            cls._instances.clear()
        else:
            # Reset matching keys
            keys_to_remove = [
                key for key in cls._instances.keys()
                if (data_type is None or key[0] == data_type)
                and (client_type is None or key[1] == client_type)
            ]
            for key in keys_to_remove:
                del cls._instances[key]
    
    @classmethod
    def get_instance(
        cls,
        data_type: DataType,
        client_type: ClientType
    ) -> Optional[BaseData]:
        """
        Get existing instance without creating new one
        
        Args:
            data_type: 'review', 'batch', or 'aspect'
            client_type: 'supabase' or 'postgres'
        
        Returns:
            Existing instance or None if not created yet
        
        Example:
            instance = DataFactory.get_instance('review', 'supabase')
            if instance is None:
                instance = DataFactory.create('review', 'supabase')
        """
        key = (data_type, client_type)
        return cls._instances.get(key)
    
    @classmethod
    def list_instances(cls) -> Dict[Tuple[str, str], BaseData]:
        """
        List all created instances
        
        Returns:
            Dictionary of (data_type, client_type) -> instance
        
        Example:
            instances = DataFactory.list_instances()
            print(f"Active instances: {len(instances)}")
        """
        return cls._instances.copy()
