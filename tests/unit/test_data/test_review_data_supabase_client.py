"""
Tests for ReviewDataSupabaseClient

ทดสอบ Supabase implementation
"""

import pytest
from unittest.mock import Mock

from review_radar.data.review_data_supabase_client import ReviewDataSupabaseClient
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
def client_with_logger(mock_supabase_client, mock_logger):
    """Create ReviewDataSupabaseClient with logger"""
    return ReviewDataSupabaseClient(client=mock_supabase_client, logger=mock_logger)


@pytest.fixture
def client_without_logger(mock_supabase_client):
    """Create ReviewDataSupabaseClient without logger"""
    return ReviewDataSupabaseClient(client=mock_supabase_client, logger=None)


# ==================== Tests ====================

class TestReviewDataSupabaseClientInheritance:
    """Test inheritance and initialization"""
    
    def test_inherits_from_review_data(self):
        """Should inherit from ReviewData"""
        assert issubclass(ReviewDataSupabaseClient, ReviewData)
    
    def test_inherits_from_base_data(self):
        """Should inherit from BaseData (through ReviewData)"""
        assert issubclass(ReviewDataSupabaseClient, BaseData)
    
    def test_init_with_logger(self, mock_supabase_client, mock_logger):
        """Should initialize with client and logger"""
        client = ReviewDataSupabaseClient(
            client=mock_supabase_client,
            logger=mock_logger
        )
        
        assert client.client == mock_supabase_client
        assert client.logger == mock_logger
    
    def test_init_without_logger(self, mock_supabase_client):
        """Should initialize without logger"""
        client = ReviewDataSupabaseClient(client=mock_supabase_client)
        
        assert client.client == mock_supabase_client
        assert client.logger is None


class TestGetUnlabeledReviews:
    """Test get_unlabeled_reviews method"""
    
    def test_get_unlabeled_reviews_success(self, client_with_logger, mock_supabase_client):
        """Should fetch unlabeled reviews from Supabase"""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'text': 'Review 1', 'batch_id': 1, 'labels': None},
            {'id': 2, 'text': 'Review 2', 'batch_id': 1, 'labels': None},
        ]
        
        query_chain = mock_supabase_client.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        # Execute
        reviews = client_with_logger.get_unlabeled_reviews(batch_id=1, limit=10, offset=0)
        
        # Verify
        assert len(reviews) == 2
        assert reviews[0]['id'] == 1
        
        # Verify Supabase calls
        mock_supabase_client.table.assert_called_with('reviews')
        query_chain.eq.assert_called_with('batch_id', 1)
        query_chain.is_.assert_called_with('labels', 'null')
        query_chain.range.assert_called_with(0, 9)
    
    def test_get_unlabeled_reviews_empty_result(self, client_with_logger, mock_supabase_client):
        """Should return empty list when no reviews found"""
        mock_response = Mock()
        mock_response.data = []
        
        query_chain = mock_supabase_client.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        reviews = client_with_logger.get_unlabeled_reviews(batch_id=999)
        
        assert reviews == []
    
    def test_get_unlabeled_reviews_with_offset(self, client_with_logger, mock_supabase_client):
        """Should use offset for pagination"""
        mock_response = Mock()
        mock_response.data = [{'id': 3}]
        
        query_chain = mock_supabase_client.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        client_with_logger.get_unlabeled_reviews(batch_id=1, limit=5, offset=10)
        
        query_chain.range.assert_called_with(10, 14)
    
    def test_get_unlabeled_reviews_logs(self, client_with_logger, mock_logger, mock_supabase_client):
        """Should log operation"""
        mock_response = Mock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        
        client_with_logger.get_unlabeled_reviews(batch_id=1, limit=10)
        
        assert mock_logger.info.call_count >= 2  # Start and end logs
    
    def test_get_unlabeled_reviews_error(self, client_with_logger, mock_supabase_client):
        """Should raise and log error on failure"""
        mock_supabase_client.table.return_value.select.return_value.execute.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception, match="DB Error"):
            client_with_logger.get_unlabeled_reviews(batch_id=1)


class TestGetReviewsByIds:
    """Test get_reviews_by_ids method"""
    
    def test_get_reviews_by_ids_success(self, client_with_logger, mock_supabase_client):
        """Should fetch reviews by IDs"""
        mock_response = Mock()
        mock_response.data = [
            {'id': 1, 'text': 'Review 1'},
            {'id': 2, 'text': 'Review 2'},
        ]
        
        query_chain = mock_supabase_client.table.return_value.select.return_value
        query_chain.execute.return_value = mock_response
        
        reviews = client_with_logger.get_reviews_by_ids([1, 2])
        
        assert len(reviews) == 2
        query_chain.in_.assert_called_with('id', [1, 2])
    
    def test_get_reviews_by_ids_empty_list(self, client_with_logger):
        """Should return empty list for empty input"""
        reviews = client_with_logger.get_reviews_by_ids([])
        assert reviews == []
    
    def test_get_reviews_by_ids_error(self, client_with_logger, mock_supabase_client):
        """Should raise and log error on failure"""
        mock_supabase_client.table.return_value.select.return_value.execute.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception, match="DB Error"):
            client_with_logger.get_reviews_by_ids([1, 2])


class TestUpdateReviews:
    """Test update_reviews method"""
    
    def test_update_reviews_success(self, client_with_logger, mock_supabase_client):
        """Should update single review"""
        update_data = {'labels': {'sentiment': 'positive'}}
        
        client_with_logger.update_reviews(review_id=1, update_data=update_data)
        
        # Verify update chain
        mock_supabase_client.table.assert_called_with('reviews')
        update_chain = mock_supabase_client.table.return_value.update.return_value
        update_chain.eq.assert_called_with('id', 1)
    
    def test_update_reviews_logs(self, client_with_logger, mock_logger):
        """Should log operation"""
        client_with_logger.update_reviews(1, {'labels': {}})
        
        assert mock_logger.info.call_count >= 2
    
    def test_update_reviews_error(self, client_with_logger, mock_supabase_client):
        """Should raise and log error on failure"""
        mock_supabase_client.table.return_value.update.return_value.execute.side_effect = Exception("Update failed")
        
        with pytest.raises(Exception, match="Update failed"):
            client_with_logger.update_reviews(1, {'labels': {}})


class TestBulkUpdateReviews:
    """Test bulk_update_reviews method"""
    
    def test_bulk_update_reviews_success(self, client_with_logger, mock_supabase_client):
        """Should update multiple reviews"""
        updates = [
            {'id': 1, 'labels': {'sentiment': 'positive'}},
            {'id': 2, 'labels': {'sentiment': 'negative'}},
        ]
        
        count = client_with_logger.bulk_update_reviews(updates)
        
        assert count == 2
        assert mock_supabase_client.table.call_count >= 2
    
    def test_bulk_update_reviews_empty_list(self, client_with_logger):
        """Should return 0 for empty list"""
        count = client_with_logger.bulk_update_reviews([])
        assert count == 0
    
    def test_bulk_update_reviews_missing_id(self, client_with_logger, mock_logger):
        """Should skip updates without id field"""
        updates = [
            {'labels': {'sentiment': 'positive'}},  # Missing 'id'
        ]
        
        count = client_with_logger.bulk_update_reviews(updates)
        
        assert count == 0
        # Should log warning
        warning_calls = [call for call in mock_logger.warning.call_args_list 
                        if "missing 'id' field" in str(call)]
        assert len(warning_calls) > 0
    
    def test_bulk_update_reviews_partial_failure(self, client_with_logger, mock_supabase_client, mock_logger):
        """Should continue on partial failure"""
        updates = [
            {'id': 1, 'labels': {}},
            {'id': 2, 'labels': {}},
        ]
        
        # First succeeds, second fails
        call_count = [0]
        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 2:
                raise Exception("Update failed")
            return Mock()
        
        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = side_effect
        
        count = client_with_logger.bulk_update_reviews(updates)
        
        assert count == 1  # Only first succeeded
    
    def test_bulk_update_reviews_removes_id_from_data(self, client_with_logger, mock_supabase_client):
        """Should not include 'id' in update data"""
        updates = [{'id': 1, 'labels': {}, 'other_field': 'value'}]
        
        client_with_logger.bulk_update_reviews(updates)
        
        # Check that update was called without 'id'
        update_calls = mock_supabase_client.table.return_value.update.call_args_list
        update_data = update_calls[0][0][0]
        assert 'id' not in update_data
        assert 'labels' in update_data


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self, client_with_logger, mock_supabase_client):
        """Should work through complete workflow"""
        # Setup responses
        unlabeled_response = Mock()
        unlabeled_response.data = [{'id': 1}, {'id': 2}]
        
        by_ids_response = Mock()
        by_ids_response.data = [{'id': 1}, {'id': 2}]
        
        query_chain = mock_supabase_client.table.return_value.select.return_value
        query_chain.execute.return_value = unlabeled_response
        
        # 1. Get unlabeled
        reviews = client_with_logger.get_unlabeled_reviews(batch_id=1)
        assert len(reviews) == 2
        
        # 2. Update single
        client_with_logger.update_reviews(1, {'labels': {}})
        
        # 3. Bulk update
        count = client_with_logger.bulk_update_reviews([{'id': 2, 'labels': {}}])
        assert count == 1
    
    def test_without_logger(self, client_without_logger, mock_supabase_client):
        """Should work without logger"""
        mock_response = Mock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        
        # Should not raise error
        reviews = client_without_logger.get_unlabeled_reviews(batch_id=1)
        assert reviews == []
        
        client_without_logger.update_reviews(1, {})
        count = client_without_logger.bulk_update_reviews([{'id': 1}])
        assert count >= 0
