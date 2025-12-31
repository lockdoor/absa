from abc import abstractmethod
from typing import List

from .base_data import BaseData


class BatchData(BaseData):
    """
    Abstract class สำหรับ batch data operations
    
    กำหนด interface สำหรับ:
    - Query batch details
    - Update batch status
    
    Implementations:
    - BatchDataSupabaseClient: Supabase implementation
    - BatchDataPostgresClient: PostgreSQL implementation
    """
    
    @abstractmethod
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
        pass
