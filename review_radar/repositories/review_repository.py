"""
Review Repository

Repository สำหรับ review operations
ใช้ DataFactory เพื่อสร้าง ReviewData instance และเพิ่ม business logic
"""

from typing import Optional, List, Dict, Any
from logging import Logger
from datetime import datetime

from .base_repository import BaseRepository
from review_radar.data import DataFactory
from review_radar.data.review_data import ReviewData


class ReviewRepository(BaseRepository):
    """
    Repository for reviews table
    
    Provides data access methods for:
    - Fetching unlabeled reviews
    - Updating review labels
    - Bulk operations
    
    Uses DataFactory to get ReviewData instance
    """
    
    def __init__(
        self,
        data_type: str = 'review',
        client_type: str = 'supabase',
        logger: Optional[Logger] = None
    ):
        """
        Initialize ReviewRepository
        
        Args:
            data_type: Data type for factory ('review')
            client_type: Client type for factory ('supabase' or 'postgres')
            logger: Optional logger instance
        """
        super().__init__(logger=logger)
        
        # Use DataFactory to create ReviewData instance
        self._review_data: ReviewData = DataFactory.create(
            data_type=data_type,
            client_type=client_type,
            logger=logger
        )
        
    
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ที่ยังไม่มี labels
        
        Args:
            batch_id: ID ของ batch ที่ต้องการ
            limit: จำนวน records สูงสุด (default: 100)
        
        Returns:
            List of review dictionaries
        
        Raises:
            ValueError: If validation fails
        
        Example:
            reviews = repo.get_unlabeled_reviews(batch_id=1, limit=50)
        """
        # Validation
        self._validate_not_none(batch_id, "batch_id")
        self._validate_positive(batch_id, "batch_id")
        self._validate_positive(limit, "limit")
        
        # Log operation
        self._log(
            f"Fetching unlabeled reviews for batch {batch_id}",
            level="info",
            batch_id=batch_id,
            limit=limit,
            offset=offset
        )
        
        # Call data layer
        reviews = self._review_data.get_unlabeled_reviews(
            batch_id=batch_id,
            limit=limit,
            offset=offset
        )
        
        # Log result
        self._log(
            f"Found {len(reviews)} unlabeled reviews",
            level="info",
            count=len(reviews)
        )
        
        return reviews
    
    def get_reviews_by_ids(
        self,
        review_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ตาม IDs
        
        Args:
            review_ids: List of review IDs
        
        Returns:
            List of review dictionaries
        
        Example:
            reviews = repo.get_reviews_by_ids([1, 2, 3])
        """
        if not review_ids:
            return []
        
        self._log(
            f"Fetching {len(review_ids)} reviews by IDs",
            level="info",
            count=len(review_ids)
        )
        
        return self._review_data.get_reviews_by_ids(review_ids)
    
    def update_labels(
        self,
        review_id: int,
        labels: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update labels สำหรับ review เดียว
        
        Args:
            review_id: Review ID ที่ต้องการ update
            labels: Dictionary ของ labels
            metadata: Optional metadata (e.g., confidence, model_version)
        
        Returns:
            True if successful, False otherwise
        
        Example:
            success = repo.update_labels(
                review_id=1,
                labels={'sentiment': 'positive', 'aspects': ['quality']},
                metadata={'confidence': 0.95}
            )
        """
        # Validation
        self._validate_not_none(review_id, "review_id")
        self._validate_positive(review_id, "review_id")
        self._validate_not_none(labels, "labels")
        
        # Prepare update data
        update_data = {
            'labels': labels,
            'labeled_at': datetime.utcnow().isoformat()
        }
        
        # Add metadata if provided
        if metadata:
            update_data['metadata'] = metadata
        
        # Log operation
        self._log(
            f"Updating labels for review {review_id}",
            level="info",
            review_id=review_id,
            labels=labels
        )
        
        try:
            # Call data layer
            self._review_data.update_reviews(
                review_id=review_id,
                update_data=update_data
            )
            
            # Log success
            self._log(
                f"Successfully updated review {review_id}",
                level="info",
                review_id=review_id
            )
            
            return True
            
        except Exception as e:
            # Log failure
            self._log(
                f"Failed to update review {review_id}: {str(e)}",
                level="warning",
                review_id=review_id,
                error=str(e)
            )
            return False
    
    def bulk_update_labels(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk update labels สำหรับหลาย reviews
        
        Args:
            updates: List of update dictionaries
                Each dict should contain:
                - review_id: int
                - labels: Dict[str, Any]
                - metadata: Optional[Dict[str, Any]]
        
        Returns:
            จำนวน reviews ที่ update สำเร็จ
        
        Example:
            updates = [
                {
                    'review_id': 1,
                    'labels': {'sentiment': 'positive'},
                    'metadata': {'confidence': 0.95}
                },
                {
                    'review_id': 2,
                    'labels': {'sentiment': 'negative'},
                    'metadata': {'confidence': 0.88}
                }
            ]
            success_count = repo.bulk_update_labels(updates)
        """
        if not updates:
            return 0
        
        self._log(
            f"Bulk updating {len(updates)} reviews",
            level="info",
            count=len(updates)
        )
        
        # Prepare bulk updates
        bulk_updates = []
        for update in updates:
            review_id = update.get('review_id')
            labels = update.get('labels')
            metadata = update.get('metadata')
            
            if not review_id or not labels:
                self._log(
                    "Skipping update: missing review_id or labels",
                    level="warning"
                )
                continue
            
            update_data = {
                'id': review_id,
                'labels': labels,
                'labeled_at': datetime.utcnow().isoformat()
            }
            
            if metadata:
                update_data['metadata'] = metadata
            
            bulk_updates.append(update_data)
        
        # Call data layer
        success_count = self._review_data.bulk_update_reviews(bulk_updates)
        
        # Log result
        self._log(
            f"Bulk update completed: {success_count}/{len(updates)} successful",
            level="info",
            success_count=success_count,
            total=len(updates)
        )
        
        return success_count
