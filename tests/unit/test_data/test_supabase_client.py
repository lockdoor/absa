"""
Unit tests for SupabaseClient

Tests the Supabase client implementation with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import os

from review_radar.data.supabase_client import SupabaseClient


# ==================== Test Fixtures ====================

@pytest.fixture
def mock_supabase_env(monkeypatch):
    """Mock environment variables for Supabase"""
    monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key-123")


@pytest.fixture
def mock_create_client():
    """Mock the create_client function"""
    with patch('review_radar.data.supabase_client.create_client') as mock:
        mock_client = Mock()
        
        # Mock response
        mock_response = Mock()
        mock_response.data = []
        
        # Mock query chain
        mock_query = Mock()
        mock_query.table.return_value = mock_query
        mock_query.select.return_value = mock_query
        mock_query.is_.return_value = mock_query
        mock_query.eq.return_value = mock_query
        mock_query.update.return_value = mock_query
        mock_query.range.return_value = mock_query
        mock_query.execute.return_value = mock_response
        
        mock_client.table.return_value = mock_query
        mock.return_value = mock_client
        
        yield mock


@pytest.fixture
def supabase_client(mock_supabase_env, mock_create_client):
    """Create SupabaseClient instance with mocked dependencies"""
    return SupabaseClient()


# ==================== Initialization Tests ====================

class TestSupabaseClientInit:
    """Test SupabaseClient initialization"""
    
    def test_requires_environment_variables(self):
        """Cannot initialize without environment variables"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Supabase URL and Key must be set"):
                SupabaseClient()
    
    def test_requires_url(self, monkeypatch):
        """Cannot initialize without SUPABASE_URL"""
        monkeypatch.delenv("SUPABASE_URL", raising=False)
        monkeypatch.setenv("SUPABASE_KEY", "test-key")
        
        with pytest.raises(ValueError):
            SupabaseClient()
    
    def test_requires_key(self, monkeypatch):
        """Cannot initialize without SUPABASE_KEY"""
        monkeypatch.setenv("SUPABASE_URL", "https://test.supabase.co")
        monkeypatch.delenv("SUPABASE_KEY", raising=False)
        
        with pytest.raises(ValueError):
            SupabaseClient()
    
    def test_creates_client_with_correct_credentials(self, mock_supabase_env, mock_create_client):
        """Creates Supabase client with correct credentials"""
        client = SupabaseClient()
        
        mock_create_client.assert_called_once_with(
            "https://test.supabase.co",
            "test-key-123"
        )
    
    def test_stores_client(self, supabase_client):
        """Stores client instance"""
        assert supabase_client.client is not None


# ==================== Get Reviews Without Labels Tests ====================

class TestGetReviewsWithoutLabels:
    """Test get_reviews_without_labels method"""
    
    def test_returns_dataframe(self, supabase_client):
        """Returns pandas DataFrame"""
        result = supabase_client.get_reviews_without_labels()
        
        assert isinstance(result, pd.DataFrame)
    
    def test_queries_reviews_table(self, supabase_client):
        """Queries the reviews table"""
        supabase_client.get_reviews_without_labels()
        
        supabase_client.client.table.assert_called_with('reviews')
    
    def test_selects_all_columns(self, supabase_client):
        """Selects all columns with *"""
        supabase_client.get_reviews_without_labels()
        
        # Verify select('*') was called
        supabase_client.client.table().select.assert_called_with('*')
    
    def test_filters_null_labels(self, supabase_client):
        """Filters for null labels"""
        supabase_client.get_reviews_without_labels()
        
        # Verify is_('label', None) was called
        supabase_client.client.table().is_.assert_called_with('label', None)
    
    def test_default_limit_and_offset(self, supabase_client):
        """Uses default limit=100 and offset=0"""
        supabase_client.get_reviews_without_labels()
        
        # Should call range(0, 99)
        supabase_client.client.table().range.assert_called_with(0, 99)
    
    def test_custom_limit(self, supabase_client):
        """Respects custom limit"""
        supabase_client.get_reviews_without_labels(limit=50, offset=0)
        
        # Should call range(0, 49)
        supabase_client.client.table().range.assert_called_with(0, 49)
    
    def test_custom_offset(self, supabase_client):
        """Respects custom offset"""
        supabase_client.get_reviews_without_labels(limit=100, offset=50)
        
        # Should call range(50, 149)
        supabase_client.client.table().range.assert_called_with(50, 149)
    
    def test_executes_query(self, supabase_client):
        """Executes the query"""
        supabase_client.get_reviews_without_labels()
        
        supabase_client.client.table().execute.assert_called_once()
    
    def test_returns_data_from_response(self, supabase_client, mock_create_client):
        """Returns data from response"""
        # Setup mock data
        mock_data = [
            {'review_id': 1, 'review': 'Test review', 'label': None}
        ]
        mock_create_client.return_value.table().execute.return_value.data = mock_data
        
        result = supabase_client.get_reviews_without_labels()
        
        assert len(result) == 1
        assert result.iloc[0]['review_id'] == 1


# ==================== Update Reviews Tests ====================

class TestUpdateReviews:
    """Test update_reviews method"""
    
    def test_queries_reviews_table(self, supabase_client):
        """Queries the reviews table"""
        supabase_client.update_reviews(123, {'label': 'test'})
        
        supabase_client.client.table.assert_called_with('reviews')
    
    def test_calls_update_with_data(self, supabase_client):
        """Calls update with provided data"""
        update_data = {'label': {'test': 'data'}}
        supabase_client.update_reviews(123, update_data)
        
        supabase_client.client.table().update.assert_called_with(update_data)
    
    def test_filters_by_review_id(self, supabase_client):
        """Filters by review_id"""
        supabase_client.update_reviews(456, {})
        
        supabase_client.client.table().eq.assert_called_with('review_id', 456)
    
    def test_executes_update(self, supabase_client):
        """Executes the update query"""
        supabase_client.update_reviews(789, {})
        
        supabase_client.client.table().execute.assert_called_once()
    
    def test_returns_none(self, supabase_client):
        """Returns None"""
        result = supabase_client.update_reviews(1, {})
        
        assert result is None


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("limit,offset,expected_start,expected_end", [
    (10, 0, 0, 9),
    (50, 0, 0, 49),
    (100, 50, 50, 149),
    (25, 100, 100, 124),
    (1, 0, 0, 0),
    (200, 0, 0, 199),
])
def test_pagination_calculations(supabase_client, limit, offset, expected_start, expected_end):
    """Test various pagination scenarios"""
    supabase_client.get_reviews_without_labels(limit=limit, offset=offset)
    
    supabase_client.client.table().range.assert_called_with(expected_start, expected_end)


# ==================== Error Handling Tests ====================

class TestErrorHandling:
    """Test error handling"""
    
    def test_handles_empty_response(self, supabase_client, mock_create_client):
        """Handles empty response gracefully"""
        mock_create_client.return_value.table().execute.return_value.data = []
        
        result = supabase_client.get_reviews_without_labels()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_handles_api_error_on_fetch(self, supabase_client):
        """Handles API errors during fetch"""
        supabase_client.client.table().execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            supabase_client.get_reviews_without_labels()
    
    def test_handles_api_error_on_update(self, supabase_client):
        """Handles API errors during update"""
        supabase_client.client.table().execute.side_effect = Exception("Update failed")
        
        with pytest.raises(Exception, match="Update failed"):
            supabase_client.update_reviews(1, {})
