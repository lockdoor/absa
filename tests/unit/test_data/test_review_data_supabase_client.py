"""
Tests for ReviewDataSupabaseClient

ทดสอบ Supabase implementation ของ ReviewData
"""

import pytest
from unittest.mock import Mock

from review_radar.data.supabase.review_data_supabase_client import ReviewDataSupabaseClient
from review_radar.data.review_data import ReviewData
from review_radar.data.base_data import BaseData


# ==================== Fixtures ====================

@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
def mock_supabase_with_from():
    """Create mock Supabase client with from_() method"""
    client = Mock()
    
    # Mock from_() chain (used in actual implementation)
    from_mock = Mock()
    client.from_ = Mock(return_value=from_mock)
    
    # Mock query chain
    query_mock = Mock()
    from_mock.select.return_value = query_mock
    query_mock.select.return_value = query_mock
    query_mock.eq.return_value = query_mock
    query_mock.is_.return_value = query_mock
    query_mock.range.return_value = query_mock
    query_mock.in_.return_value = query_mock
    
    # Mock execute response
    execute_response = Mock()
    execute_response.data = []
    query_mock.execute.return_value = execute_response
    
    # Mock table() chain (used by get_reviews_by_ids and update methods)
    table_mock = Mock()
    client.table = Mock(return_value=table_mock)
    table_mock.select.return_value = query_mock
    
    # Mock update chain
    update_mock = Mock()
    table_mock.update.return_value = update_mock
    update_mock.eq.return_value = update_mock
    update_mock.execute.return_value = execute_response
    
    return client


@pytest.fixture
def client_with_logger(mock_supabase_with_from, mock_logger):
    """Create ReviewDataSupabaseClient with logger"""
    return ReviewDataSupabaseClient(client=mock_supabase_with_from, logger=mock_logger)


@pytest.fixture
def client_without_logger(mock_supabase_with_from):
    """Create ReviewDataSupabaseClient without logger"""
    return ReviewDataSupabaseClient(client=mock_supabase_with_from, logger=None)


# ==================== Tests ====================

class TestReviewDataSupabaseClientInit:
    """Test __init__ method"""
    
    def test_inherits_from_review_data(self):
        """Should inherit from ReviewData"""
        assert issubclass(ReviewDataSupabaseClient, ReviewData)
    
    def test_inherits_from_base_data(self):
        """Should inherit from BaseData through ReviewData"""
        assert issubclass(ReviewDataSupabaseClient, BaseData)
    
    def test_init_with_client_and_logger(self, mock_supabase_with_from, mock_logger):
        """Should initialize with client and logger"""
        client = ReviewDataSupabaseClient(
            client=mock_supabase_with_from,
            logger=mock_logger
        )
        
        assert client.client == mock_supabase_with_from
        assert client.logger == mock_logger
    
    def test_init_with_client_only(self, mock_supabase_with_from):
        """Should initialize with client only (logger is None)"""
        client = ReviewDataSupabaseClient(client=mock_supabase_with_from)
        
        assert client.client == mock_supabase_with_from
        assert client.logger is None
    
    def test_init_stores_client_as_correct_type(self, mock_supabase_with_from):
        """Should store client with correct type annotation"""
        client = ReviewDataSupabaseClient(client=mock_supabase_with_from)
        
        # Verify client is stored and accessible
        assert hasattr(client, 'client')
        assert client.client is not None


class TestGetUnlabeledReviews:
    """Test get_unlabeled_reviews method"""
    
    def test_get_unlabeled_reviews_success(self, client_with_logger, mock_supabase_with_from):
        """Should fetch unlabeled reviews successfully"""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [
            {
                'id': 1,
                'batch_id': 1,
                'review': 'สินค้าดีมาก คุณภาพดี',
                'labels': []
            },
            {
                'id': 2,
                'batch_id': 1,
                'review': 'ราคาแพงไป',
                'labels': []
            }
        ]
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Execute
        result = client_with_logger.get_unlabeled_reviews(batch_id=1, limit=10, offset=0)
        
        # Verify result
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[0]['review'] == 'สินค้าดีมาก คุณภาพดี'
        assert result[1]['id'] == 2
        assert result[0]['labels'] == None or result[0]['labels'] == [] and len(result[1]['labels']) == 0   
        # Verify Supabase calls
        # query_chain.select.assert_called_once()
        query_chain.eq.assert_called_once_with('batch_id', 1)
        query_chain.is_.assert_called_once_with('labels', None)
        query_chain.range.assert_called_once_with(0, 9)
        query_chain.execute.assert_called_once()
    
    def test_get_unlabeled_reviews_with_default_params(self, client_with_logger, mock_supabase_with_from):
        """Should use default limit=100 and offset=0"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Execute without limit and offset
        result = client_with_logger.get_unlabeled_reviews(batch_id=1)
        
        # Verify default range is used
        query_chain.range.assert_called_once_with(0, 99)  # 0 to 100-1
    
    def test_get_unlabeled_reviews_with_custom_limit(self, client_with_logger, mock_supabase_with_from):
        """Should use custom limit"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Execute with custom limit
        result = client_with_logger.get_unlabeled_reviews(batch_id=1, limit=5, offset=0)
        
        # Verify range calculation
        query_chain.range.assert_called_once_with(0, 4)  # 0 to 5-1
    
    def test_get_unlabeled_reviews_with_offset(self, client_with_logger, mock_supabase_with_from):
        """Should handle pagination with offset"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Execute with offset
        result = client_with_logger.get_unlabeled_reviews(batch_id=1, limit=10, offset=20)
        
        # Verify range calculation with offset
        query_chain.range.assert_called_once_with(20, 29)  # 20 to 20+10-1
    
    def test_get_unlabeled_reviews_empty_result(self, client_with_logger, mock_supabase_with_from):
        """Should return empty list when no reviews found"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        result = client_with_logger.get_unlabeled_reviews(batch_id=999)
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_unlabeled_reviews_none_data(self, client_with_logger, mock_supabase_with_from):
        """Should handle None response.data gracefully"""
        mock_response = Mock()
        mock_response.data = None
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        result = client_with_logger.get_unlabeled_reviews(batch_id=1)
        
        assert result == []
    
    def test_get_unlabeled_reviews_logs_operation(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log the operation"""
        mock_response = Mock()
        mock_response.data = [{'id': 1}]
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        client_with_logger.get_unlabeled_reviews(batch_id=1, limit=10, offset=0)
        
        # Verify logging was called
        assert mock_logger.info.call_count >= 2  # Start and end logs
        
        # Check log messages contain relevant info
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Fetching' in str(call) and 'batch' in str(call).lower() for call in log_calls)
        assert any('Found' in str(call) for call in log_calls)
    
    def test_get_unlabeled_reviews_logs_empty_result(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log when response.data is empty"""
        mock_response = Mock()
        mock_response.data = None
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        client_with_logger.get_unlabeled_reviews(batch_id=1)
        
        # Should log the response when data is None
        assert mock_logger.info.call_count >= 3
    
    def test_get_unlabeled_reviews_raises_on_error(self, client_with_logger, mock_supabase_with_from):
        """Should raise exception when query fails"""
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            client_with_logger.get_unlabeled_reviews(batch_id=1)
    
    def test_get_unlabeled_reviews_logs_error(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log error when query fails"""
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.side_effect = Exception("Database error")
        
        try:
            client_with_logger.get_unlabeled_reviews(batch_id=1)
        except Exception:
            pass
        
        # Verify error was logged
        assert mock_logger.error.call_count >= 1
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any('Error' in str(call) and 'fetching' in str(call).lower() for call in error_calls)
    
    def test_get_unlabeled_reviews_without_logger(self, client_without_logger, mock_supabase_with_from):
        """Should work without logger"""
        mock_response = Mock()
        mock_response.data = [{'id': 1}]
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Should not raise error even without logger
        result = client_without_logger.get_unlabeled_reviews(batch_id=1)
        
        assert len(result) == 1
    
    def test_get_unlabeled_reviews_different_batch_ids(self, client_with_logger, mock_supabase_with_from):
        """Should correctly filter by different batch_ids"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_with_from.from_.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Test with batch_id=5
        client_with_logger.get_unlabeled_reviews(batch_id=5)
        query_chain.eq.assert_called_with('batch_id', 5)
        
        # Reset mock
        query_chain.eq.reset_mock()
        
        # Test with batch_id=10
        client_with_logger.get_unlabeled_reviews(batch_id=10)
        query_chain.eq.assert_called_with('batch_id', 10)


class TestGetReviewsByIds:
    """Test get_reviews_by_ids method"""
    
    def test_get_reviews_by_ids_success(self, client_with_logger, mock_supabase_with_from):
        """Should fetch reviews by IDs successfully"""
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'review': 'Review 1', 'batch_id': 1},
            {'id': 2, 'review': 'Review 2', 'batch_id': 1}
        ]
        
        table_mock = mock_supabase_with_from.table.return_value
        query_chain = table_mock.select.return_value
        query_chain.execute.return_value = mock_response
        
        result = client_with_logger.get_reviews_by_ids([1, 2])
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        assert result[1]['id'] == 2
        
        # Verify Supabase calls
        mock_supabase_with_from.table.assert_called_once_with('reviews')
        table_mock.select.assert_called_once_with('*')
        query_chain.in_.assert_called_once_with('id', [1, 2])
        query_chain.execute.assert_called_once()
    
    def test_get_reviews_by_ids_empty_list(self, client_with_logger):
        """Should return empty list when input is empty"""
        result = client_with_logger.get_reviews_by_ids([])
        
        assert result == []
        assert isinstance(result, list)
    
    def test_get_reviews_by_ids_single_id(self, client_with_logger, mock_supabase_with_from):
        """Should handle single ID"""
        mock_response = Mock()
        mock_response.data = [{'id': 5, 'review': 'Single review'}]
        
        query_chain = mock_supabase_with_from.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        result = client_with_logger.get_reviews_by_ids([5])
        
        assert len(result) == 1
        assert result[0]['id'] == 5
        query_chain.in_.assert_called_once_with('id', [5])
    
    def test_get_reviews_by_ids_none_data(self, client_with_logger, mock_supabase_with_from):
        """Should handle None response.data"""
        mock_response = Mock()
        mock_response.data = None
        
        query_chain = mock_supabase_with_from.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        result = client_with_logger.get_reviews_by_ids([1, 2])
        
        assert result == []
    
    def test_get_reviews_by_ids_logs_operation(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log the operation"""
        mock_response = Mock()
        mock_response.data = [{'id': 1}]
        
        query_chain = mock_supabase_with_from.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        client_with_logger.get_reviews_by_ids([1, 2, 3])
        
        assert mock_logger.info.call_count >= 2
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Fetching' in str(call) and '3' in str(call) for call in log_calls)
        assert any('Found' in str(call) for call in log_calls)
    
    def test_get_reviews_by_ids_raises_on_error(self, client_with_logger, mock_supabase_with_from):
        """Should raise exception on query failure"""
        query_chain = mock_supabase_with_from.table.return_value.select.return_value
        query_chain.execute.side_effect = Exception("Query failed")
        
        with pytest.raises(Exception, match="Query failed"):
            client_with_logger.get_reviews_by_ids([1, 2])
    
    def test_get_reviews_by_ids_logs_error(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log error on failure"""
        query_chain = mock_supabase_with_from.table.return_value.select.return_value
        query_chain.execute.side_effect = Exception("Database error")
        
        try:
            client_with_logger.get_reviews_by_ids([1, 2])
        except Exception:
            pass
        
        assert mock_logger.error.call_count >= 1
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any('Error' in str(call) and 'fetching' in str(call).lower() for call in error_calls)


class TestUpdateReviews:
    """Test update_reviews method"""
    
    def test_update_reviews_success(self, client_with_logger, mock_supabase_with_from):
        """Should update review successfully"""
        update_data = {
            'sentiment': 0.8,
            'sentiment_confidence': 0.9,
            'aspect_sentiments': {'quality': 0.9}
        }
        
        client_with_logger.update_reviews(review_id=1, update_data=update_data)
        
        # Verify Supabase calls
        mock_supabase_with_from.table.assert_called_once_with('reviews')
        update_chain = mock_supabase_with_from.table.return_value.update.return_value
        mock_supabase_with_from.table.return_value.update.assert_called_once_with(update_data)
        update_chain.eq.assert_called_once_with('id', 1)
        update_chain.execute.assert_called_once()
    
    def test_update_reviews_with_different_review_id(self, client_with_logger, mock_supabase_with_from):
        """Should update different review IDs correctly"""
        update_data = {'sentiment': 0.5}
        
        # Update review 5
        client_with_logger.update_reviews(review_id=5, update_data=update_data)
        update_chain = mock_supabase_with_from.table.return_value.update.return_value
        update_chain.eq.assert_called_with('id', 5)
        
        # Reset and update review 10
        update_chain.eq.reset_mock()
        client_with_logger.update_reviews(review_id=10, update_data=update_data)
        update_chain.eq.assert_called_with('id', 10)
    
    def test_update_reviews_empty_update_data(self, client_with_logger, mock_supabase_with_from):
        """Should handle empty update data"""
        client_with_logger.update_reviews(review_id=1, update_data={})
        
        # Should still make the call
        mock_supabase_with_from.table.assert_called_once_with('reviews')
        mock_supabase_with_from.table.return_value.update.assert_called_once_with({})
    
    def test_update_reviews_logs_operation(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log the operation"""
        update_data = {'sentiment': 0.8, 'confidence': 0.9}
        
        client_with_logger.update_reviews(review_id=1, update_data=update_data)
        
        assert mock_logger.info.call_count >= 2
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Updating' in str(call) and 'review' in str(call).lower() for call in log_calls)
        assert any('Updated' in str(call) and 'successfully' in str(call).lower() for call in log_calls)
    
    def test_update_reviews_raises_on_error(self, client_with_logger, mock_supabase_with_from):
        """Should raise exception on update failure"""
        update_chain = mock_supabase_with_from.table.return_value.update.return_value
        update_chain.execute.side_effect = Exception("Update failed")
        
        with pytest.raises(Exception, match="Update failed"):
            client_with_logger.update_reviews(review_id=1, update_data={'sentiment': 0.8})
    
    def test_update_reviews_logs_error(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log error on failure"""
        update_chain = mock_supabase_with_from.table.return_value.update.return_value
        update_chain.execute.side_effect = Exception("Database error")
        
        try:
            client_with_logger.update_reviews(review_id=1, update_data={'sentiment': 0.8})
        except Exception:
            pass
        
        assert mock_logger.error.call_count >= 1
        error_calls = [str(call) for call in mock_logger.error.call_args_list]
        assert any('Error' in str(call) and 'updating' in str(call).lower() for call in error_calls)


class TestBulkUpdateReviews:
    """Test bulk_update_reviews method"""
    
    def test_bulk_update_reviews_success(self, client_with_logger, mock_supabase_with_from):
        """Should update multiple reviews successfully"""
        updates = [
            {'id': 1, 'sentiment': 0.8, 'confidence': 0.9},
            {'id': 2, 'sentiment': -0.5, 'confidence': 0.85}
        ]
        
        result = client_with_logger.bulk_update_reviews(updates)
        
        assert result == 2
        assert mock_supabase_with_from.table.call_count == 2
    
    def test_bulk_update_reviews_empty_list(self, client_with_logger):
        """Should return 0 for empty list"""
        result = client_with_logger.bulk_update_reviews([])
        
        assert result == 0
    
    def test_bulk_update_reviews_removes_id_from_data(self, client_with_logger, mock_supabase_with_from):
        """Should remove 'id' field from update data"""
        updates = [
            {'id': 1, 'sentiment': 0.8, 'other_field': 'value'}
        ]
        
        client_with_logger.bulk_update_reviews(updates)
        
        # Verify update was called without 'id'
        update_calls = mock_supabase_with_from.table.return_value.update.call_args_list
        update_data = update_calls[0][0][0]
        
        assert 'id' not in update_data
        assert 'sentiment' in update_data
        assert 'other_field' in update_data
    
    def test_bulk_update_reviews_missing_id(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should skip updates missing 'id' field"""
        updates = [
            {'sentiment': 0.8},  # Missing 'id'
            {'id': 2, 'sentiment': 0.5}
        ]
        
        result = client_with_logger.bulk_update_reviews(updates)
        
        assert result == 1  # Only second update succeeded
        assert mock_supabase_with_from.table.call_count == 1
        
        # Should log warning
        assert mock_logger.warning.call_count >= 1
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any("missing 'id'" in str(call).lower() for call in warning_calls)
    
    def test_bulk_update_reviews_partial_failure(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should continue on partial failure"""
        updates = [
            {'id': 1, 'sentiment': 0.8},
            {'id': 2, 'sentiment': 0.5},
            {'id': 3, 'sentiment': -0.3}
        ]
        
        # Second update fails
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Update failed")
            return Mock()
        
        update_chain = mock_supabase_with_from.table.return_value.update.return_value.eq.return_value
        update_chain.execute.side_effect = side_effect
        
        result = client_with_logger.bulk_update_reviews(updates)
        
        assert result == 2  # First and third succeeded
        assert mock_logger.warning.call_count >= 1  # Failed update logged
    
    def test_bulk_update_reviews_all_fail(self, client_with_logger, mock_supabase_with_from):
        """Should return 0 when all updates fail"""
        updates = [
            {'id': 1, 'sentiment': 0.8},
            {'id': 2, 'sentiment': 0.5}
        ]
        
        update_chain = mock_supabase_with_from.table.return_value.update.return_value.eq.return_value
        update_chain.execute.side_effect = Exception("All updates fail")
        
        result = client_with_logger.bulk_update_reviews(updates)
        
        assert result == 0
    
    def test_bulk_update_reviews_logs_operation(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log bulk update operation"""
        updates = [
            {'id': 1, 'sentiment': 0.8},
            {'id': 2, 'sentiment': 0.5}
        ]
        
        client_with_logger.bulk_update_reviews(updates)
        
        assert mock_logger.info.call_count >= 2
        log_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Bulk updating' in str(call) for call in log_calls)
        assert any('completed' in str(call).lower() for call in log_calls)
    
    def test_bulk_update_reviews_logs_individual_failures(self, client_with_logger, mock_logger, mock_supabase_with_from):
        """Should log individual update failures"""
        updates = [
            {'id': 1, 'sentiment': 0.8},
            {'id': 2, 'sentiment': 0.5}
        ]
        
        update_chain = mock_supabase_with_from.table.return_value.update.return_value.eq.return_value
        update_chain.execute.side_effect = [Mock(), Exception("Second update failed")]
        
        client_with_logger.bulk_update_reviews(updates)
        
        # Should log warning for failed update
        assert mock_logger.warning.call_count >= 1
        warning_calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any('Failed to update' in str(call) for call in warning_calls)
    
    def test_bulk_update_reviews_uses_correct_eq_field(self, client_with_logger, mock_supabase_with_from):
        """Should use 'id' field in eq() call"""
        updates = [{'id': 5, 'sentiment': 0.8}]
        
        client_with_logger.bulk_update_reviews(updates)
        
        update_chain = mock_supabase_with_from.table.return_value.update.return_value
        update_chain.eq.assert_called_once_with('id', 5)
    
    def test_bulk_update_reviews_without_logger(self, client_without_logger, mock_supabase_with_from):
        """Should work without logger"""
        updates = [
            {'id': 1, 'sentiment': 0.8},
            {'id': 2, 'sentiment': 0.5}
        ]
        
        result = client_without_logger.bulk_update_reviews(updates)
        
        assert result == 2
