from .base_client import BaseClient
import pandas as pd
from typing import Optional, Any
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from .client_factory import ClientFactory


load_dotenv()


def create_supabase_client_from_env() -> Client:
    """
    Create Supabase client from environment variables
    
    Returns:
        Supabase Client instance
    
    Raises:
        ValueError: If SUPABASE_URL or SUPABASE_KEY not set
    """
    supabase_url: str | None = os.getenv("SUPABASE_URL", None)
    supabase_key: str | None = os.getenv("SUPABASE_KEY", None)
    
    if not supabase_url or not supabase_key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
    
    return create_client(supabase_url, supabase_key)


@ClientFactory.register('supabase')
class SupabaseClient(BaseClient):
    """Client for Supabase database interactions"""

    def __init__(self, client: Client, logger: Optional[Any] = None):
        """
        Initialize SupabaseClient
        
        Args:
            client: Supabase client instance
            logger: Optional logger instance
        """
        super().__init__(client=client, logger=logger)
        self.client: Client = client

    def get_reviews_without_labels(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> pd.DataFrame:
        """Fetch reviews without labels from Supabase

        Args:
            limit (int): Number of records to fetch
            offset (int): Offset for pagination

        Returns:
            pd.DataFrame: DataFrame of reviews without labels
        """
        response = (
            self.client
            .table('reviews')
            .select('*')
            .is_('label', None)
            .range(offset, offset + limit - 1)
            .execute()
        )
        data = response.data
        return pd.DataFrame(data)
    
    def update_reviews(
        self,
        review_id: int,
        update_data: dict
    ) -> None:
        """Update review record in Supabase

        Args:
            review_id (int): ID of the review to update
            update_data (dict): Data to update
        """
        (
            self.client
            .table('reviews')
            .update(update_data)
            .eq('review_id', review_id)
            .execute()
        )
