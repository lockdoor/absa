from .base_client import BaseClient
import pandas as pd
from dotenv import load_dotenv
import os
from supabase import create_client, Client


load_dotenv()


class SupabaseClient(BaseClient):
    """Client for Supabase database interactions"""

    def __init__(self):
        supabase_url: str | None = os.getenv("SUPABASE_URL", None)
        supabase_key: str | None = os.getenv("SUPABASE_KEY", None)
        
        if not supabase_url or not supabase_key:
            raise ValueError("Supabase URL and Key must be set in environment variables.")
        
        client: Client = create_client(supabase_url, supabase_key)
        super().__init__(client=client)
        self.client: Client

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