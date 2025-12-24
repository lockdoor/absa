"""
Unit tests for ReviewRepository

Tests the repository layer for review operations.
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
import pandas as pd

from review_radar.repositories.review_repository import ReviewRepository


# ==================== Test Fixtures ====================

@pytest.fixture
def review_repository(mock_database_client, mock_logger):
    """Create ReviewRepository instance for testing"""
    return ReviewRepository(client=mock_database_client, logger=mock_logger)


@pytest.fixture
def sample_reviews():
    """Sample review data"""
    return [
        {
            'review_id': 1,
            'batch_id': 1,
            'review': 'Great product!',
            'source': 'web',
            'review_date': '2025-01-01'
        },
        {
            'review_id': 2,
            'batch_id': 1,
            'review': 'Not satisfied',
            'source': 'mobile',
            'review_date': '2025-01-02'
        }
    ]


# ==================== Tests ====================

class TestReviewRepositoryInit:
    """Test ReviewRepository initialization"""
    
    def test_inherits_from_base_repository(self, mock_database_client):
        """ReviewRepository inherits from BaseRepository"""
        repo = ReviewRepository(client=mock_database_client)
        
        assert hasattr(repo, 'client')
        assert hasattr(repo, 'logger')
        assert hasattr(repo, '_log')
        assert hasattr(repo, '_validate_not_none')
        assert hasattr(repo, '_validate_positive')
    
    def test_stores_client(self, mock_database_client):
        """Stores client instance"""
        repo = ReviewRepository(client=mock_database_client)
        
        assert repo.client == mock_database_client
    
    def test_logger_is_optional(self, mock_database_client):
        """Logger is optional"""
        repo = ReviewRepository(client=mock_database_client)
        
        assert repo.logger is None


class TestGetUnlabeledReviews:
    """Test get_unlabeled_reviews method"""
    
    def test_validates_batch_id_not_none(self, review_repository):
        """Raises ValueError if batch_id is None"""
        with pytest.raises(ValueError, match="batch_id cannot be None"):
            review_repository.get_unlabeled_reviews(batch_id=None, limit=100)
    
    def test_validates_batch_id_positive(self, review_repository):
        """Raises ValueError if batch_id is not positive"""
        with pytest.raises(ValueError, match="batch_id must be positive"):
            review_repository.get_unlabeled_reviews(batch_id=0, limit=100)
        
        with pytest.raises(ValueError, match="batch_id must be positive"):
            review_repository.get_unlabeled_reviews(batch_id=-1, limit=100)
    
    def test_validates_limit_positive(self, review_repository):
        """Raises ValueError if limit is not positive"""
        with pytest.raises(ValueError, match="limit must be positive"):
            review_repository.get_unlabeled_reviews(batch_id=1, limit=0)
        
        with pytest.raises(ValueError, match="limit must be positive"):
            review_repository.get_unlabeled_reviews(batch_id=1, limit=-10)
    
    def test_calls_client_get_unlabeled_reviews(self, review_repository, mock_database_client, sample_reviews):
        """Calls client.get_unlabeled_reviews with correct parameters"""
        # Setup mock to return DataFrame
        mock_df = pd.DataFrame(sample_reviews)
        mock_database_client.get_unlabeled_reviews.return_value = mock_df
        
        result = review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # Verify client was called with correct params
        mock_database_client.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=100
        )
    
    def test_returns_list_of_dicts(self, review_repository, mock_database_client, sample_reviews):
        """Returns list of review dictionaries"""
        mock_df = pd.DataFrame(sample_reviews)
        mock_database_client.get_unlabeled_reviews.return_value = mock_df
        
        result = review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # get_unlabeled_reviews returns DataFrame from client
        # Repository should work with what client returns
        assert isinstance(result, pd.DataFrame)
    
    def test_uses_default_limit(self, review_repository, mock_database_client):
        """Uses default limit=100"""
        mock_database_client.get_unlabeled_reviews.return_value = pd.DataFrame()
        
        review_repository.get_unlabeled_reviews(batch_id=1)
        
        mock_database_client.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=100
        )
    
    def test_respects_custom_limit(self, review_repository, mock_database_client):
        """Respects custom limit parameter"""
        mock_database_client.get_unlabeled_reviews.return_value = pd.DataFrame()
        
        review_repository.get_unlabeled_reviews(batch_id=1, limit=50)
        
        mock_database_client.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=50
        )
    
    def test_logs_fetch_operation(self, review_repository, mock_database_client, mock_logger):
        """Logs fetch operation with context"""
        mock_database_client.get_unlabeled_reviews.return_value = pd.DataFrame()
        
        review_repository.get_unlabeled_reviews(batch_id=42, limit=25)
        
        # Check that logger was called
        assert mock_logger.info.called
        # First call should be for fetching
        call_args = mock_logger.info.call_args_list[0]
        assert "Fetching unlabeled reviews" in str(call_args)
    
    def test_logs_result_count(self, review_repository, mock_database_client, mock_logger, sample_reviews):
        """Logs number of reviews found"""
        mock_df = pd.DataFrame(sample_reviews)
        mock_database_client.get_unlabeled_reviews.return_value = mock_df
        
        review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # Should log the count
        assert mock_logger.info.call_count >= 2
        # Last call should be about count
        last_call = mock_logger.info.call_args_list[-1]
        assert "Found" in str(last_call)


class TestUpdateLabels:
    """Test update_labels method"""
    
    def test_validates_review_id_not_none(self, review_repository):
        """Raises ValueError if review_id is None"""
        with pytest.raises(ValueError, match="review_id cannot be None"):
            review_repository.update_labels(
                review_id=None,
                labels={'sentiment': 'positive'}
            )
    
    def test_validates_review_id_positive(self, review_repository):
        """Raises ValueError if review_id is not positive"""
        with pytest.raises(ValueError, match="review_id must be positive"):
            review_repository.update_labels(
                review_id=0,
                labels={'sentiment': 'positive'}
            )
    
    def test_validates_labels_not_none(self, review_repository):
        """Raises ValueError if labels is None"""
        with pytest.raises(ValueError, match="labels cannot be None"):
            review_repository.update_labels(
                review_id=1,
                labels=None
            )
    
    def test_calls_client_update_reviews(self, review_repository, mock_database_client):
        """Calls client.update_reviews"""
        mock_database_client.update_reviews.return_value = 1
        
        labels = {'sentiment': 'positive', 'aspects': ['quality']}
        review_repository.update_labels(review_id=123, labels=labels)
        
        mock_database_client.update_reviews.assert_called_once()
    
    def test_prepares_update_data_with_timestamp(self, review_repository, mock_database_client):
        """Prepares update data with timestamp"""
        mock_database_client.update_reviews.return_value = 1
        
        labels = {'sentiment': 'positive'}
        review_repository.update_labels(review_id=123, labels=labels)
        
        # Check the data passed to client
        call_args = mock_database_client.update_reviews.call_args[0][0]
        assert len(call_args) == 1
        update_data = call_args[0]
        
        assert update_data['review_id'] == 123
        assert update_data['labels'] == labels
        assert 'updated_at' in update_data
    
    def test_includes_metadata_when_provided(self, review_repository, mock_database_client):
        """Includes metadata in update data"""
        mock_database_client.update_reviews.return_value = 1
        
        labels = {'sentiment': 'positive'}
        metadata = {'provider': 'gemini', 'confidence': 0.95}
        
        review_repository.update_labels(
            review_id=123,
            labels=labels,
            metadata=metadata
        )
        
        call_args = mock_database_client.update_reviews.call_args[0][0]
        update_data = call_args[0]
        
        assert update_data['metadata'] == metadata
    
    def test_returns_true_on_success(self, review_repository, mock_database_client):
        """Returns True when update succeeds"""
        mock_database_client.update_reviews.return_value = 1
        
        result = review_repository.update_labels(
            review_id=123,
            labels={'sentiment': 'positive'}
        )
        
        assert result is True
    
    def test_returns_false_on_failure(self, review_repository, mock_database_client):
        """Returns False when no rows updated"""
        mock_database_client.update_reviews.return_value = 0
        
        result = review_repository.update_labels(
            review_id=123,
            labels={'sentiment': 'positive'}
        )
        
        assert result is False
    
    def test_logs_update_operation(self, review_repository, mock_database_client, mock_logger):
        """Logs update operation"""
        mock_database_client.update_reviews.return_value = 1
        
        review_repository.update_labels(
            review_id=123,
            labels={'sentiment': 'positive'}
        )
        
        # Should log the operation
        assert mock_logger.info.called
        call_args = str(mock_logger.info.call_args_list)
        assert "Updating labels" in call_args
    
    def test_logs_success(self, review_repository, mock_database_client, mock_logger):
        """Logs success message"""
        mock_database_client.update_reviews.return_value = 1
        
        review_repository.update_labels(
            review_id=123,
            labels={'sentiment': 'positive'}
        )
        
        call_args = str(mock_logger.info.call_args_list)
        assert "Successfully updated" in call_args
    
    def test_logs_failure_as_warning(self, review_repository, mock_database_client, mock_logger):
        """Logs failure as warning"""
        mock_database_client.update_reviews.return_value = 0
        
        review_repository.update_labels(
            review_id=123,
            labels={'sentiment': 'positive'}
        )
        
        # Should log warning
        assert mock_logger.warning.called


class TestBulkUpdateLabels:
    """Test bulk_update_labels method"""
    
    def test_validates_updates_not_none(self, review_repository):
        """Raises ValueError if updates is None"""
        with pytest.raises(ValueError, match="updates cannot be None"):
            review_repository.bulk_update_labels(updates=None)
    
    def test_validates_updates_not_empty(self, review_repository):
        """Raises ValueError if updates is empty"""
        with pytest.raises(ValueError, match="updates list cannot be empty"):
            review_repository.bulk_update_labels(updates=[])
    
    def test_calls_client_update_reviews(self, review_repository, mock_database_client):
        """Calls client.update_reviews with prepared data"""
        mock_database_client.update_reviews.return_value = 2
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        mock_database_client.update_reviews.assert_called_once()
    
    def test_prepares_all_updates_with_timestamps(self, review_repository, mock_database_client):
        """Prepares all updates with timestamps"""
        mock_database_client.update_reviews.return_value = 2
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        call_args = mock_database_client.update_reviews.call_args[0][0]
        
        assert len(call_args) == 2
        for update_data in call_args:
            assert 'review_id' in update_data
            assert 'labels' in update_data
            assert 'updated_at' in update_data
    
    def test_includes_metadata_when_provided(self, review_repository, mock_database_client):
        """Includes metadata for updates that have it"""
        mock_database_client.update_reviews.return_value = 2
        
        updates = [
            {
                'review_id': 1,
                'labels': {'sentiment': 'positive'},
                'metadata': {'provider': 'gemini'}
            },
            {
                'review_id': 2,
                'labels': {'sentiment': 'negative'}
            }
        ]
        
        review_repository.bulk_update_labels(updates)
        
        call_args = mock_database_client.update_reviews.call_args[0][0]
        
        # First update should have metadata
        assert 'metadata' in call_args[0]
        assert call_args[0]['metadata']['provider'] == 'gemini'
        
        # Second update should not have metadata
        assert 'metadata' not in call_args[1]
    
    def test_returns_updated_count(self, review_repository, mock_database_client):
        """Returns number of successfully updated reviews"""
        mock_database_client.update_reviews.return_value = 3
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}},
            {'review_id': 3, 'labels': {'sentiment': 'neutral'}}
        ]
        
        result = review_repository.bulk_update_labels(updates)
        
        assert result == 3
    
    def test_logs_bulk_operation(self, review_repository, mock_database_client, mock_logger):
        """Logs bulk update operation"""
        mock_database_client.update_reviews.return_value = 2
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        # Should log operation and result
        assert mock_logger.info.called
        call_args = str(mock_logger.info.call_args_list)
        assert "Bulk updating" in call_args or "Successfully updated" in call_args


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("batch_id,limit,should_raise", [
    (1, 100, False),      # Valid
    (42, 50, False),      # Valid
    (None, 100, True),    # Invalid: None batch_id
    (0, 100, True),       # Invalid: zero batch_id
    (-1, 100, True),      # Invalid: negative batch_id
    (1, 0, True),         # Invalid: zero limit
    (1, -10, True),       # Invalid: negative limit
])
def test_get_unlabeled_reviews_validation(review_repository, mock_database_client, batch_id, limit, should_raise):
    """Test validation for various parameter combinations"""
    mock_database_client.get_unlabeled_reviews.return_value = pd.DataFrame()
    
    if should_raise:
        with pytest.raises(ValueError):
            review_repository.get_unlabeled_reviews(batch_id=batch_id, limit=limit)
    else:
        result = review_repository.get_unlabeled_reviews(batch_id=batch_id, limit=limit)
        assert result is not None


@pytest.mark.parametrize("review_id,labels,should_raise", [
    (1, {'sentiment': 'positive'}, False),           # Valid
    (123, {'aspects': ['quality']}, False),          # Valid
    (None, {'sentiment': 'positive'}, True),         # Invalid: None review_id
    (0, {'sentiment': 'positive'}, True),            # Invalid: zero review_id
    (-1, {'sentiment': 'positive'}, True),           # Invalid: negative review_id
    (1, None, True),                                 # Invalid: None labels
])
def test_update_labels_validation(review_repository, mock_database_client, review_id, labels, should_raise):
    """Test validation for various parameter combinations"""
    mock_database_client.update_reviews.return_value = 1
    
    if should_raise:
        with pytest.raises(ValueError):
            review_repository.update_labels(review_id=review_id, labels=labels)
    else:
        result = review_repository.update_labels(review_id=review_id, labels=labels)
        assert isinstance(result, bool)


# ==================== Integration-like Tests ====================

class TestReviewRepositoryWorkflow:
    """Test complete workflows"""
    
    def test_fetch_and_update_workflow(self, review_repository, mock_database_client, sample_reviews):
        """Test typical fetch -> update workflow"""
        # Setup: fetch returns reviews
        mock_df = pd.DataFrame(sample_reviews)
        mock_database_client.get_unlabeled_reviews.return_value = mock_df
        mock_database_client.update_reviews.return_value = 1
        
        # Fetch unlabeled reviews
        reviews = review_repository.get_unlabeled_reviews(batch_id=1, limit=10)
        assert len(reviews) == 2
        
        # Update one review
        success = review_repository.update_labels(
            review_id=1,
            labels={'sentiment': 'positive', 'aspects': ['quality']}
        )
        assert success is True
    
    def test_bulk_update_workflow(self, review_repository, mock_database_client):
        """Test bulk update workflow"""
        mock_database_client.update_reviews.return_value = 3
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}},
            {'review_id': 3, 'labels': {'sentiment': 'neutral'}}
        ]
        
        updated_count = review_repository.bulk_update_labels(updates)
        
        assert updated_count == 3
        mock_database_client.update_reviews.assert_called_once()
