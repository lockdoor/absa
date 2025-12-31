from typing import List, Dict, Any
from logging import Logger
from supabase import Client

from ..batch_data import BatchData


class BatchDataSupabaseClient(BatchData):
    """
    Supabase implementation ของ BatchData
    
    ใช้ Supabase client สำหรับ batch data operations
    """
    
    def __init__(self, client: Any, logger: Logger):
        """
        Initialize BatchDataSupabaseClient
        
        Args:
            client: Supabase client instance
            logger: Logger instance
        """
        super().__init__(client=client, logger=logger)
        self.client: Client
    
    def get_batch_aspects(
        self,
        batch_id: int
    ) -> List[str]:
        """
        Fetch batch aspects จาก Supabase
        
        Args:
            batch_id: batch ID
        
        Returns:
            list with batch aspects
        """
        self._log(
            f"{self.__class__.__name__}: Fetching aspects for batch {batch_id}",
            level="info",
            batch_id=batch_id
        )
        
        try:
            response = (
                self.client
                .from_('batch')
                .select('aspects')
                .eq('id', batch_id)
                .single()
                .execute()
            )
            
            data = response.data
            aspects: List[str] = data.get('aspects', [])
            
            self._log(
                f"Fetched {len(aspects)} aspects for batch {batch_id}",
                level="info",
                batch_id=batch_id,
                aspects=aspects
            )
            
            return aspects
        
        except Exception as e:
            self._log(
                f"Exception during fetching batch aspects: {str(e)}",
                level="error",
                batch_id=batch_id
            )
            return []
