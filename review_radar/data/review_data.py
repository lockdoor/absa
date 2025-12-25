"""
Review Data Layer

Abstract class สำหรับ review operations
กำหนด contract สำหรับการเข้าถึงข้อมูล reviews
"""

from abc import abstractmethod
from typing import Dict, List, Any

from .base_data import BaseData


class ReviewData(BaseData):
    """
    Abstract class สำหรับ review data operations
    
    กำหนด interface สำหรับ:
    - Query reviews (unlabeled, by IDs)
    - Update reviews (single, bulk)
    
    Implementations:
    - ReviewDataSupabaseClient: Supabase implementation
    - ReviewDataPostgresClient: PostgreSQL implementation
    """
    
    @abstractmethod
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ที่ยังไม่มี labels
        
        Args:
            batch_id: ID ของ batch ที่ต้องการ query
            limit: จำนวน records สูงสุดที่ต้องการ (default: 100)
            offset: เริ่มต้นจาก record ที่เท่าไร (default: 0)
        
        Returns:
            List of review dictionaries
            
        Example:
            [
                {
                    'id': 1,
                    'text': 'Great product',
                    'batch_id': 123,
                    'labels': None
                },
                ...
            ]
        """
        pass
    
    @abstractmethod
    def get_reviews_by_ids(
        self,
        review_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ตาม IDs ที่ระบุ
        
        Args:
            review_ids: List of review IDs
        
        Returns:
            List of review dictionaries
            
        Example:
            reviews = client.get_reviews_by_ids([1, 2, 3])
        """
        pass
    
    @abstractmethod
    def update_reviews(
        self,
        review_id: int,
        update_data: Dict[str, Any]
    ) -> None:
        """
        Update review เดียว
        
        Args:
            review_id: Review ID ที่ต้องการ update
            update_data: Dictionary ของข้อมูลที่ต้องการ update
        
        Example:
            client.update_reviews(
                review_id=1,
                update_data={'labels': {...}, 'labeled_at': '2024-01-01'}
            )
        """
        pass
    
    @abstractmethod
    def bulk_update_reviews(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk update หลาย reviews พร้อมกัน
        
        Args:
            updates: List of dictionaries containing review_id and update_data
        
        Returns:
            จำนวน reviews ที่ update สำเร็จ
            
        Example:
            count = client.bulk_update_reviews([
                {'id': 1, 'labels': {...}},
                {'id': 2, 'labels': {...}},
            ])
        """
        pass
