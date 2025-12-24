"""
Unit tests for BaseData

Tests the abstract base class behavior and interface.
"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd

from review_radar.data.base_client import BaseClient


# ==================== Test Fixtures ====================

class ConcreteClient(BaseClient):
    """Concrete implementation of BaseClient for testing"""
    
    def get_reviews_without_labels(self, limit: int = 100, offset: int = 0):
        """Test implementation"""
        # Simulate fetching from client
        if hasattr(self.client, 'table'):
            # Supabase-style
            response = (
                self.client.table('reviews')
                .select('*')
                .is_('labels', 'null')
                .range(offset, offset + limit - 1)
                .execute()
            )
            return pd.DataFrame(response.data)
        return pd.DataFrame()
    
    def update_reviews(self, review_id, update_data):
        """Test implementation"""
        if hasattr(self.client, 'table'):
            self.client.table('reviews').update(update_data).eq('review_id', review_id).execute()


@pytest.fixture
def concrete_client(mock_supabase_client):
    """Create concrete instance for testing"""
    return ConcreteClient(client=mock_supabase_client)


# ==================== Tests ====================

class TestBaseClient:
    """Test BaseClient abstract class"""
    
    def test_cannot_instantiate_abstract_class(self):
        """Cannot create BaseClient directly"""
        with pytest.raises(TypeError):
            BaseClient(client=Mock())
    
    def test_concrete_class_can_be_instantiated(self, mock_supabase_client):
        """Concrete implementation can be instantiated"""
        client = ConcreteClient(client=mock_supabase_client)
        assert client is not None
        assert client.client == mock_supabase_client
    
    def test_must_implement_abstract_methods(self, mock_client):
        """Concrete class must implement all abstract methods"""
        
        class IncompleteClient(BaseClient):
            pass
        
        with pytest.raises(TypeError):
            IncompleteClient(client=mock_client)
    
    def test_client_is_stored(self, concrete_client, mock_supabase_client):
        """Client is stored correctly"""
        assert concrete_client.client == mock_supabase_client
    
    def test_logger_is_optional(self, mock_supabase_client):
        """Logger is optional parameter"""
        client = ConcreteClient(client=mock_supabase_client)
        assert client.logger is None
        
        mock_logger = Mock()
        client_with_logger = ConcreteClient(client=mock_supabase_client, logger=mock_logger)
        assert client_with_logger.logger == mock_logger

class TestGetReviewsWithoutLabels:
    """Test get_reviews_without_labels method"""
    
    def test_returns_dataframe(self, concrete_client):
        """Method returns DataFrame"""
        result = concrete_client.get_reviews_without_labels()
        assert isinstance(result, pd.DataFrame)
    
    def test_default_parameters(self, concrete_client, mock_supabase_client):
        """Uses default limit and offset"""
        concrete_client.get_reviews_without_labels()
        
        mock_supabase_client.table.assert_called_once_with('reviews')
    
    def test_custom_limit(self, concrete_client, mock_supabase_client):
        """Respects custom limit parameter"""
        concrete_client.get_reviews_without_labels(limit=50)
        
        # Verify range was called with correct params
        call_args = mock_supabase_client.table().range.call_args
        assert call_args[0][0] == 0  # offset
        assert call_args[0][1] == 49  # offset + limit - 1
    
    def test_custom_offset(self, concrete_client, mock_supabase_client):
        """Respects custom offset parameter"""
        concrete_client.get_reviews_without_labels(limit=100, offset=50)
        
        call_args = mock_supabase_client.table().range.call_args
        assert call_args[0][0] == 50  # offset
        assert call_args[0][1] == 149  # offset + limit - 1
    
    def test_filters_null_labels(self, concrete_client, mock_supabase_client):
        """Filters for null labels"""
        concrete_client.get_reviews_without_labels()
        
        # Verify is_ method was called to filter null labels
        mock_supabase_client.table().is_.assert_called_once()


class TestUpdateReviews:
    """Test update_reviews method"""
    
    def test_calls_update_on_client(self, concrete_client, mock_supabase_client):
        """Calls update method on client"""
        update_data = {'labels': {'test': 'data'}}
        concrete_client.update_reviews(review_id=123, update_data=update_data)
        
        mock_supabase_client.table.assert_called_with('reviews')
        mock_supabase_client.table().update.assert_called_once_with(update_data)
    
    def test_filters_by_review_id(self, concrete_client, mock_supabase_client):
        """Filters update by review_id"""
        concrete_client.update_reviews(review_id=456, update_data={})
        
        mock_supabase_client.table().eq.assert_called_once_with('review_id', 456)
    
    def test_executes_query(self, concrete_client, mock_supabase_client):
        """Executes the update query"""
        concrete_client.update_reviews(review_id=789, update_data={})
        
        mock_supabase_client.table().execute.assert_called_once()


# ==================== Integration-like Tests ====================

class TestBaseClientWithDifferentClients:
    """Test BaseClient with different client types"""
    
    def test_works_with_supabase_client(self, mock_supabase_client):
        """Works with Supabase-style client"""
        data = ConcreteClient(client=mock_supabase_client)
        result = data.get_reviews_without_labels()
        
        assert isinstance(result, pd.DataFrame)
        mock_supabase_client.table.assert_called()
    
    def test_works_with_custom_client(self):
        """Works with any client object"""
        custom_client = Mock()
        data = ConcreteClient(client=custom_client)
        
        assert data.client == custom_client


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("limit,offset,expected_start,expected_end", [
    (10, 0, 0, 9),
    (50, 0, 0, 49),
    (100, 50, 50, 149),
    (25, 100, 100, 124),
])
def test_pagination_ranges(mock_supabase_client, limit, offset, expected_start, expected_end):
    """Test various pagination ranges"""
    data = ConcreteClient(client=mock_supabase_client)
    data.get_reviews_without_labels(limit=limit, offset=offset)
    
    call_args = mock_supabase_client.table().range.call_args
    assert call_args[0][0] == expected_start
    assert call_args[0][1] == expected_end
