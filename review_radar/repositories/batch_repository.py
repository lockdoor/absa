from typing import Optional, List, Dict, Any
from logging import Logger

from .base_repository import BaseRepository
from review_radar.data import DataFactory
from review_radar.data.batch_data import BatchData

class BatchRepository(BaseRepository):
    """
    Repository สำหรับ batch operations
    
    ใช้ DataFactory เพื่อสร้าง BatchData instance และเพิ่ม business logic
    """
    
    def __init__(
        self,
        data_type: str = 'batch',
        client_type: str = 'supabase',
        logger: Optional[Logger] = None
    ):
        """
        Initialize BatchRepository
        
        Args:
            data_type: Data type for factory ('batch')
            client_type: Client type for factory ('supabase' or 'postgres')
            logger: Optional logger instance
        """
        super().__init__(logger=logger)
        
        # Use DataFactory to create BatchData instance
        self._batch_data: BatchData = DataFactory.create(
            data_type=data_type,
            client_type=client_type,
            logger=logger
        )

    def get_batch_aspects(
        self,
        batch_id: int
    ) -> List[str]:
        """
        Fetch batch aspects
        
        Args:
            batch_id: batch ID
        
        Returns:
            list with batch aspects
        """
        if self._logger:
            self._log(
                f"{self.__class__.__name__}: Fetching aspects for batch {batch_id}",
                level="info",
                batch_id=batch_id
            )
        return self._batch_data.get_batch_aspects(batch_id=batch_id)
