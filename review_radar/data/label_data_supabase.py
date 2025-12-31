from typing import List, Dict, Any
from logging import Logger
from supabase import Client

from .label_data import LabelData


class LabelDataSupabaseClient(LabelData):
    """
    Supabase implementation ของ LabelData
    
    ใช้ Supabase client สำหรับ label data operations
    """
    
    def __init__(self, client: Any, logger: Logger):
        """
        Initialize LabelDataSupabaseClient
        
        Args:
            client: Supabase client instance
            logger: Logger instance
        """
        super().__init__(client=client, logger=logger)
        self.client: Client
    
    def insert_label(
        self,
        review_id: int,
        label: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Insert label data for a review into Supabase
        
        Args:
            review_id: review ID
            label: dictionary with label data and metadata
        
        Returns:
            Dictionary with inserted label data
        """
        self._log(
            f"{self.__class__.__name__}: Inserting label for review {review_id}",
            level="info",
            review_id=review_id
        )
        
        data = {
            "review_id": review_id,
            "label": label
        }
        
        try:
            response = (
                self.client
                .table('labels')
                .insert(data)
                .execute()
            )
            
            inserted_data = response.data
            
            self._log(
                f"Inserted label for review {review_id}",
                level="info",
                review_id=review_id
            )
            
            return inserted_data
        
        except Exception as e:
            self._log(
                f"Error inserting label for review {review_id}: {str(e)}",
                level="error",
                review_id=review_id
            )
            raise e
        
    def insert_labels_batch(
        self,
        labels: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Insert multiple label data entries in batch into Supabase
        
        Args:
            labels: List of dictionaries with label data and metadata
            [{review_id: int, label: Dict[str, Any]}, ...]
        
        Returns:
            List of dictionaries with inserted label data
        """
        self._log(
            f"{self.__class__.__name__}: Inserting batch of {len(labels)} labels",
            level="info"
        )
       
        try:
            response = (
                self.client
                .table('labels')
                .insert(labels)
                .execute()
            )
            
            inserted_data = response.data
            
            self._log(
                f"Inserted batch of {len(labels)} labels",
                level="info"
            )
            
            return inserted_data
        
        except Exception as e:
            self._log(
                f"Error inserting batch of labels: {str(e)}",
                level="error"
            )
            raise e