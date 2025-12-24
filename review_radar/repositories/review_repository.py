"""
Review Repository

Data access layer for reviews table.
Handles CRUD operations and queries related to reviews.
"""

from typing import Dict, List, Any
from datetime import datetime

from .base_repository import BaseRepository


class ReviewRepository(BaseRepository):
    """
    Repository for reviews table
    
    Provides data access methods for:
    - Fetching unlabeled reviews
    - Updating review labels
    """
    
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews that don't have labels yet
        
        Args:
            batch_id: Batch ID to filter by
            limit: Maximum number of reviews to fetch
        
        Returns:
            List of review dictionaries
        
        Raises:
            ValueError: If batch_id is None or limit is not positive
        """
        self._validate_not_none(batch_id, "batch_id")
        self._validate_positive(batch_id, "batch_id")
        self._validate_positive(limit, "limit")
        
        self._log(
            f"Fetching unlabeled reviews for batch {batch_id}, limit={limit}",
            batch_id=batch_id,
            limit=limit
        )
        
        reviews = self.client.get_unlabeled_reviews(
            batch_id=batch_id,
            limit=limit
        )
        
        self._log(f"Found {len(reviews)} unlabeled reviews", count=len(reviews))
        return reviews
    
    def update_labels(
        self,
        review_id: int,
        labels: Dict[str, Any],
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Update labels for a single review
        
        Args:
            review_id: Review ID to update
            labels: Labels dictionary to save
            metadata: Additional metadata (optional)
        
        Returns:
            True if successful
        
        Raises:
            ValueError: If review_id is None or not positive
        """
        self._validate_not_none(review_id, "review_id")
        self._validate_positive(review_id, "review_id")
        self._validate_not_none(labels, "labels")
        
        self._log(
            f"Updating labels for review {review_id}",
            review_id=review_id
        )
        
        # Prepare update data
        update_data = {
            "review_id": review_id,
            "labels": labels,
            "updated_at": datetime.now().isoformat()
        }
        
        if metadata:
            update_data["metadata"] = metadata
        
        # Use client to update
        updated_count = self.client.update_reviews([update_data])
        success = updated_count > 0
        
        if success:
            self._log(f"Successfully updated labels for review {review_id}")
        else:
            self._log(
                f"Failed to update labels for review {review_id}",
                level="warning"
            )
        
        return success
    
    def bulk_update_labels(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        Update labels for multiple reviews in batch
        
        Args:
            updates: List of dicts with 'review_id', 'labels', 'metadata'
        
        Returns:
            Number of successfully updated reviews
        
        Raises:
            ValueError: If updates is None or empty
        """
        self._validate_not_none(updates, "updates")
        
        if not updates:
            raise ValueError("updates list cannot be empty")
        
        self._log(f"Bulk updating {len(updates)} reviews", count=len(updates))
        
        # Prepare updates with timestamp
        prepared_updates = []
        for update in updates:
            update_data = {
                "review_id": update["review_id"],
                "labels": update["labels"],
                "updated_at": datetime.now().isoformat()
            }
            if "metadata" in update:
                update_data["metadata"] = update["metadata"]
            
            prepared_updates.append(update_data)
        
        # Use client to bulk update
        updated_count = self.client.update_reviews(prepared_updates)
        
        self._log(
            f"Successfully updated {updated_count}/{len(updates)} reviews",
            updated=updated_count,
            total=len(updates)
        )
        
        return updated_count
