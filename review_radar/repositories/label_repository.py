from typing import Optional, List, Dict, Any
from logging import Logger

from .base_repository import BaseRepository
from review_radar.data import DataFactory
from review_radar.data.label_data import LabelData


class LabelRepository(BaseRepository):
    """
    Repository สำหรับ label operations
    
    ใช้ DataFactory เพื่อสร้าง LabelData instance และเพิ่ม business logic
    """
    
    def __init__(
        self,
        data_type: str = 'label',
        client_type: str = 'supabase',
        logger: Optional[Logger] = None
    ):
        """
        Initialize LabelRepository
        
        Args:
            data_type: Data type for factory ('label')
            client_type: Client type for factory ('supabase' or 'postgres')
            logger: Optional logger instance
        """
        super().__init__(logger=logger)
        
        # Use DataFactory to create LabelData instance
        self._label_data: LabelData = DataFactory.create(
            data_type=data_type,
            client_type=client_type,
            logger=logger
        )

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
        """
        if self._logger:
            self._log(
                f"{self.__class__.__name__}: Inserting label for review {review_id}",
                level="info",
                review_id=review_id
            )
        return self._label_data.insert_label(
            review_id=review_id,
            label=label
        )
    
    def insert_labels_batch(
        self,
        labels: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Insert multiple label data entries in batch
        
        Args:
            labels: List of dictionaries with label data and metadata
            [{review_id: int, label: Dict[str, Any]}, ...]
        
        Returns:
            List of dictionaries with inserted label data
        """
        if self._logger:
            self._log(
                f"{self.__class__.__name__}: Inserting batch of {len(labels)} labels",
                level="info",
                batch_size=len(labels)
            )
        return self._label_data.insert_labels_batch(
            labels=labels
        )
