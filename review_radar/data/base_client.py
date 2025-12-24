from abc import ABC, abstractmethod
from typing import Any, Optional, Dict
from pandas import DataFrame

class BaseClient(ABC):
    """
    Base class for data handling CRUD operations
    """

    def __init__(self, client: Any, logger: Optional[Any] = None):
        self.client = client
        self.logger = logger

    @abstractmethod
    def get_reviews_without_labels(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> DataFrame:
        """
        Fetch reviews without labels
        
        Args:
            limit: Number of reviews to fetch
            offset: Offset for pagination
        
        Returns:
            DataFrame with reviews without labels
        """
        pass

    @abstractmethod
    def update_reviews(
        self,
        review_id: Any,
        update_data: Dict[str, Any]
    ) -> None:
        """
        Update a review in the database
        
        Args:
            review_id: ID of the review to update
            update_data: Dictionary with fields to update
        
        Returns:
            None
        """
        pass
