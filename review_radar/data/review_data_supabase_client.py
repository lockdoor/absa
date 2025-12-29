"""
Review Data Supabase Client

Concrete implementation ของ ReviewData สำหรับ Supabase database
"""

from typing import Optional, Any, List, Dict
from logging import Logger
from supabase import Client

from .review_data import ReviewData


class ReviewDataSupabaseClient(ReviewData):
    """
    Supabase implementation ของ ReviewData
    
    ใช้ Supabase client สำหรับ CRUD operations กับ reviews table
    """
    
    def __init__(self, client: Client, logger: Optional[Logger] = None):
        """
        Initialize ReviewDataSupabaseClient
        
        Args:
            client: Supabase client instance
            logger: Optional logger instance
        """
        super().__init__(client=client, logger=logger)
        self.client: Client
    
    def get_unlabeled_reviews(
        self,
        batch_id: int,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ที่ยังไม่มี labels จาก Supabase
        
        Args:
            batch_id: ID ของ batch ที่ต้องการ query
            limit: จำนวน records สูงสุด
            offset: เริ่มต้นจาก record ที่เท่าไร
        
        Returns:
            List of review dictionaries
        """
        self._log(
            f"Fetching unlabeled reviews for batch {batch_id}",
            level="info",
            batch_id=batch_id,
            limit=limit,
            offset=offset
        )
        
        try:
            response = (
                self.client
                .from_('reviews')
                .select('id, batch_id, review, labels!review_id(*), batch!batch_id(aspects)')
                .eq('batch_id', batch_id)
                .is_('labels', None)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            data: List[Dict[str, Any]] = response.data if response.data else []
            
            self._log(
                f"Found {len(data)} unlabeled reviews",
                level="info",
                count=len(data)
            )

            if not response.data:
                self._log(
                    response,
                    level="info"
                )
            
            return data
            
        except Exception as e:
            self._log(
                f"Error fetching unlabeled reviews: {str(e)}",
                level="error",
                error=str(e)
            )
            raise
    
    def get_reviews_by_ids(
        self,
        review_ids: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Fetch reviews ตาม IDs จาก Supabase
        
        Args:
            review_ids: List of review IDs
        
        Returns:
            List of review dictionaries
        """
        if not review_ids:
            return []
        
        self._log(
            f"Fetching {len(review_ids)} reviews by IDs",
            level="info",
            review_ids=review_ids
        )
        
        try:
            response = (
                self.client
                .table('reviews')
                .select('*')
                .in_('id', review_ids)
                .execute()
            )
            
            data = response.data if response.data else []
            
            self._log(
                f"Found {len(data)} reviews",
                level="info",
                count=len(data)
            )
            
            return data
            
        except Exception as e:
            self._log(
                f"Error fetching reviews by IDs: {str(e)}",
                level="error",
                error=str(e)
            )
            raise
    
    def update_reviews(
        self,
        review_id: int,
        update_data: Dict[str, Any]
    ) -> None:
        """
        Update review เดียวใน Supabase
        
        Args:
            review_id: Review ID ที่ต้องการ update
            update_data: Dictionary ของข้อมูลที่ต้องการ update
        """
        self._log(
            f"Updating review {review_id}",
            level="info",
            review_id=review_id,
            fields=list(update_data.keys())
        )
        
        try:
            response = (
                self.client
                .table('reviews')
                .update(update_data)
                .eq('id', review_id)
                .execute()
            )
            
            self._log(
                f"Updated review {review_id} successfully",
                level="info",
                review_id=review_id
            )
            
        except Exception as e:
            self._log(
                f"Error updating review {review_id}: {str(e)}",
                level="error",
                review_id=review_id,
                error=str(e)
            )
            raise
    
    def bulk_update_reviews(
        self,
        updates: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk update หลาย reviews พร้อมกัน
        
        Args:
            updates: List of dictionaries containing 'id' and update fields
        
        Returns:
            จำนวน reviews ที่ update สำเร็จ
        """
        if not updates:
            return 0
        
        self._log(
            f"Bulk updating {len(updates)} reviews",
            level="info",
            count=len(updates)
        )
        
        success_count = 0
        
        try:
            for update in updates:
                review_id = update.get('id')
                if not review_id:
                    self._log(
                        "Skipping update: missing 'id' field",
                        level="warning"
                    )
                    continue
                
                # Remove 'id' from update_data
                update_data = {k: v for k, v in update.items() if k != 'id'}
                
                try:
                    self.client.table('reviews').update(update_data).eq('id', review_id).execute()
                    success_count += 1
                except Exception as e:
                    self._log(
                        f"Failed to update review {review_id}: {str(e)}",
                        level="warning",
                        review_id=review_id,
                        error=str(e)
                    )
                    continue
            
            self._log(
                f"Bulk update completed: {success_count}/{len(updates)} successful",
                level="info",
                success_count=success_count,
                total=len(updates)
            )
            
            return success_count
            
        except Exception as e:
            self._log(
                f"Error during bulk update: {str(e)}",
                level="error",
                error=str(e)
            )
            raise
