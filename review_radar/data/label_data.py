from abc import abstractmethod
from typing import Dict, Any, Optional

from .base_data import BaseData


class LabelData(BaseData):
    """
    Abstract class สำหรับ label data operations
    
    กำหนด interface สำหรับ:
    - Fetch label data by batch ID
    - Update label data status
    
    Implementations:
    - LabelDataSupabaseClient: Supabase implementation
    - LabelDataPostgresClient: PostgreSQL implementation
    """
    
    @abstractmethod
    def insert_label(
        self,
        review_id: int,
        label: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert label data for a review
        
        Args:
            review_id: review ID
            label: dictionary with label data and metadata
        
        Returns:
            Dictionary with inserted label data
        """
        pass

    @abstractmethod
    def insert_labels_batch(
        self,
        labels: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Insert multiple label data entries in batch
        
        Args:
            labels: List of dictionaries with label data and metadata
            [{review_id: int, label: Dict[str, Any]}, ...]
        
        Returns:
            List of dictionaries with inserted label data
        """
        pass
