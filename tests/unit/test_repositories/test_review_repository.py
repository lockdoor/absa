"""
Unit tests for ReviewRepository

Tests the repository layer for review operations using DataFactory
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from review_radar.repositories.review_repository import ReviewRepository
from review_radar.repositories.base_repository import BaseRepository


# ==================== Test Fixtures ====================

@pytest.fixture
def mock_logger():
    """Mock logger instance"""
    return Mock()


@pytest.fixture
def mock_review_data():
    """Mock ReviewData instance"""
    mock_data = Mock()
    mock_data.get_unlabeled_reviews.return_value = []
    mock_data.get_reviews_by_ids.return_value = []
    mock_data.update_reviews.return_value = None
    mock_data.bulk_update_reviews.return_value = 0
    return mock_data


@pytest.fixture
def review_repository(mock_review_data, mock_logger):
    """Create ReviewRepository instance for testing"""
    with patch('review_radar.repositories.review_repository.DataFactory') as mock_factory:
        mock_factory.create.return_value = mock_review_data
        repo = ReviewRepository(logger=mock_logger)
        return repo


@pytest.fixture
def sample_reviews():
    """Sample review data"""
    return [
        {
            'id': 1,
            'batch_id': 1,
            'text': 'Great product!',
            'source': 'web',
            'created_at': '2025-01-01'
        },
        {
            'id': 2,
            'batch_id': 1,
            'text': 'Not satisfied',
            'source': 'mobile',
            'created_at': '2025-01-02'
        }
    ]


# ==================== Tests ====================

class TestReviewRepositoryInit:
    """Test ReviewRepository initialization"""
    
    def test_inherits_from_base_repository(self):
        """ReviewRepository inherits from BaseRepository"""
        with patch('review_radar.repositories.review_repository.DataFactory'):
            repo = ReviewRepository()
            
            assert isinstance(repo, BaseRepository)
            assert hasattr(repo, 'logger')
            assert hasattr(repo, '_log')
            assert hasattr(repo, '_validate_not_none')
            assert hasattr(repo, '_validate_positive')
    
    def test_uses_data_factory(self):
        """Uses DataFactory to create ReviewData instance"""
        with patch('review_radar.repositories.review_repository.DataFactory') as mock_factory:
            mock_review_data = Mock()
            mock_factory.create.return_value = mock_review_data
            
            repo = ReviewRepository(data_type='review', client_type='supabase')
            
            # Verify DataFactory was called
            mock_factory.create.assert_called_once_with(
                data_type='review',
                client_type='supabase',
                logger=None
            )
            
            # Verify review_data was stored
            assert repo._review_data == mock_review_data
    
    def test_logger_is_optional(self):
        """Logger is optional"""
        with patch('review_radar.repositories.review_repository.DataFactory'):
            repo = ReviewRepository()
            assert repo.logger is None
    
    def test_passes_logger_to_factory(self, mock_logger):
        """Passes logger to DataFactory"""
        with patch('review_radar.repositories.review_repository.DataFactory') as mock_factory:
            repo = ReviewRepository(logger=mock_logger)
            
            mock_factory.create.assert_called_once()
            call_kwargs = mock_factory.create.call_args[1]
            assert call_kwargs['logger'] == mock_logger


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
    
    def test_calls_review_data_get_unlabeled_reviews(self, review_repository, mock_review_data, sample_reviews):
        """Calls _review_data.get_unlabeled_reviews with correct parameters"""
        mock_review_data.get_unlabeled_reviews.return_value = sample_reviews
        
        result = review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # Verify review_data was called with correct params
        mock_review_data.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=100,
            offset=0
        )
        
        # Verify result
        assert result == sample_reviews
    
    def test_returns_list_of_dicts(self, review_repository, mock_review_data, sample_reviews):
        """Returns list of dictionaries"""
        mock_review_data.get_unlabeled_reviews.return_value = sample_reviews
        
        result = review_repository.get_unlabeled_reviews(batch_id=1, limit=50)
        
        assert isinstance(result, list)
        assert all(isinstance(item, dict) for item in result)
    
    def test_uses_default_limit(self, review_repository, mock_review_data):
        """Uses default limit of 100"""
        review_repository.get_unlabeled_reviews(batch_id=1)
        
        mock_review_data.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=100,
            offset=0
        )
    
    def test_respects_custom_limit(self, review_repository, mock_review_data):
        """Respects custom limit"""
        review_repository.get_unlabeled_reviews(batch_id=1, limit=50)
        
        mock_review_data.get_unlabeled_reviews.assert_called_once_with(
            batch_id=1,
            limit=50,
            offset=0
        )
    
    def test_logs_fetch_operation(self, review_repository, mock_logger):
        """Logs fetch operation"""
        review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # Check for fetch log
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Fetching unlabeled reviews' in str(call) for call in calls)
    
    def test_logs_result_count(self, review_repository, mock_review_data, mock_logger, sample_reviews):
        """Logs result count"""
        mock_review_data.get_unlabeled_reviews.return_value = sample_reviews
        
        review_repository.get_unlabeled_reviews(batch_id=1, limit=100)
        
        # Check for result count log
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Found' in str(call) and 'reviews' in str(call) for call in calls)


class TestGetReviewsByIds:
    """Test get_reviews_by_ids method"""
    
    def test_returns_empty_list_for_empty_ids(self, review_repository):
        """Returns empty list for empty IDs"""
        result = review_repository.get_reviews_by_ids([])
        assert result == []
    
    def test_calls_review_data_get_reviews_by_ids(self, review_repository, mock_review_data, sample_reviews):
        """Calls _review_data.get_reviews_by_ids"""
        mock_review_data.get_reviews_by_ids.return_value = sample_reviews
        
        result = review_repository.get_reviews_by_ids([1, 2, 3])
        
        mock_review_data.get_reviews_by_ids.assert_called_once_with([1, 2, 3])
        assert result == sample_reviews
    
    def test_logs_operation(self, review_repository, mock_logger):
        """Logs operation"""
        review_repository.get_reviews_by_ids([1, 2, 3])
        
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Fetching' in str(call) and 'reviews by IDs' in str(call) for call in calls)


class TestUpdateLabels:
    """Test update_labels method"""
    
    def test_validates_review_id_not_none(self, review_repository):
        """Raises ValueError if review_id is None"""
        with pytest.raises(ValueError, match="review_id cannot be None"):
            review_repository.update_labels(review_id=None, labels={'sentiment': 'positive'})
    
    def test_validates_review_id_positive(self, review_repository):
        """Raises ValueError if review_id is not positive"""
        with pytest.raises(ValueError, match="review_id must be positive"):
            review_repository.update_labels(review_id=0, labels={'sentiment': 'positive'})
        
        with pytest.raises(ValueError, match="review_id must be positive"):
            review_repository.update_labels(review_id=-1, labels={'sentiment': 'positive'})
    
    def test_validates_labels_not_none(self, review_repository):
        """Raises ValueError if labels is None"""
        with pytest.raises(ValueError, match="labels cannot be None"):
            review_repository.update_labels(review_id=1, labels=None)
    
    def test_calls_review_data_update_reviews(self, review_repository, mock_review_data):
        """Calls _review_data.update_reviews"""
        labels = {'sentiment': 'positive', 'aspects': ['quality']}
        
        review_repository.update_labels(review_id=1, labels=labels)
        
        # Verify update was called
        mock_review_data.update_reviews.assert_called_once()
        
        # Verify arguments
        call_args = mock_review_data.update_reviews.call_args
        assert call_args[1]['review_id'] == 1
        
        update_data = call_args[1]['update_data']
        assert update_data['labels'] == labels
        assert 'labeled_at' in update_data
    
    def test_prepares_update_data_with_timestamp(self, review_repository, mock_review_data):
        """Prepares update data with timestamp"""
        labels = {'sentiment': 'positive'}
        
        review_repository.update_labels(review_id=1, labels=labels)
        
        call_args = mock_review_data.update_reviews.call_args
        update_data = call_args[1]['update_data']
        
        assert 'labeled_at' in update_data
        assert isinstance(update_data['labeled_at'], str)
    
    def test_includes_metadata_when_provided(self, review_repository, mock_review_data):
        """Includes metadata when provided"""
        labels = {'sentiment': 'positive'}
        metadata = {'confidence': 0.95, 'model_version': 'v1.0'}
        
        review_repository.update_labels(review_id=1, labels=labels, metadata=metadata)
        
        call_args = mock_review_data.update_reviews.call_args
        update_data = call_args[1]['update_data']
        
        assert update_data['metadata'] == metadata
    
    def test_returns_true_on_success(self, review_repository, mock_review_data):
        """Returns True on successful update"""
        result = review_repository.update_labels(review_id=1, labels={'sentiment': 'positive'})
        assert result is True
    
    def test_returns_false_on_failure(self, review_repository, mock_review_data):
        """Returns False on failure"""
        mock_review_data.update_reviews.side_effect = Exception("Database error")
        
        result = review_repository.update_labels(review_id=1, labels={'sentiment': 'positive'})
        assert result is False
    
    def test_logs_update_operation(self, review_repository, mock_logger):
        """Logs update operation"""
        review_repository.update_labels(review_id=1, labels={'sentiment': 'positive'})
        
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Updating labels' in str(call) for call in calls)
    
    def test_logs_success(self, review_repository, mock_logger):
        """Logs success"""
        review_repository.update_labels(review_id=1, labels={'sentiment': 'positive'})
        
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Successfully updated' in str(call) for call in calls)
    
    def test_logs_failure_as_warning(self, review_repository, mock_review_data, mock_logger):
        """Logs failure as warning"""
        mock_review_data.update_reviews.side_effect = Exception("Database error")
        
        review_repository.update_labels(review_id=1, labels={'sentiment': 'positive'})
        
        mock_logger.warning.assert_called()
        calls = [str(call) for call in mock_logger.warning.call_args_list]
        assert any('Failed to update' in str(call) for call in calls)


class TestBulkUpdateLabels:
    """Test bulk_update_labels method"""
    
    def test_returns_zero_for_empty_updates(self, review_repository):
        """Returns 0 for empty updates"""
        result = review_repository.bulk_update_labels([])
        assert result == 0
    
    def test_prepares_bulk_updates(self, review_repository, mock_review_data):
        """Prepares bulk updates correctly"""
        updates = [
            {
                'review_id': 1,
                'labels': {'sentiment': 'positive'},
                'metadata': {'confidence': 0.95}
            },
            {
                'review_id': 2,
                'labels': {'sentiment': 'negative'},
                'metadata': {'confidence': 0.88}
            }
        ]
        
        review_repository.bulk_update_labels(updates)
        
        # Verify bulk_update_reviews was called
        mock_review_data.bulk_update_reviews.assert_called_once()
        
        # Verify prepared updates
        call_args = mock_review_data.bulk_update_reviews.call_args[0][0]
        assert len(call_args) == 2
        
        # Check first update
        assert call_args[0]['id'] == 1
        assert call_args[0]['labels'] == {'sentiment': 'positive'}
        assert call_args[0]['metadata'] == {'confidence': 0.95}
        assert 'labeled_at' in call_args[0]
    
    def test_skips_updates_without_review_id(self, review_repository, mock_review_data, mock_logger):
        """Skips updates without review_id"""
        updates = [
            {'labels': {'sentiment': 'positive'}},  # Missing review_id
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        # Only 1 update should be sent
        call_args = mock_review_data.bulk_update_reviews.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]['id'] == 2
        
        # Should log warning
        mock_logger.warning.assert_called()
    
    def test_skips_updates_without_labels(self, review_repository, mock_review_data, mock_logger):
        """Skips updates without labels"""
        updates = [
            {'review_id': 1},  # Missing labels
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        # Only 1 update should be sent
        call_args = mock_review_data.bulk_update_reviews.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]['id'] == 2
    
    def test_returns_success_count(self, review_repository, mock_review_data):
        """Returns success count from data layer"""
        mock_review_data.bulk_update_reviews.return_value = 5
        
        updates = [
            {'review_id': i, 'labels': {'sentiment': 'positive'}}
            for i in range(1, 6)
        ]
        
        result = review_repository.bulk_update_labels(updates)
        assert result == 5
    
    def test_logs_bulk_operation(self, review_repository, mock_logger):
        """Logs bulk operation"""
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Bulk updating' in str(call) for call in calls)
    
    def test_logs_result(self, review_repository, mock_review_data, mock_logger):
        """Logs result"""
        mock_review_data.bulk_update_reviews.return_value = 2
        
        updates = [
            {'review_id': 1, 'labels': {'sentiment': 'positive'}},
            {'review_id': 2, 'labels': {'sentiment': 'negative'}}
        ]
        
        review_repository.bulk_update_labels(updates)
        
        calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Bulk update completed' in str(call) for call in calls)


class TestReviewRepositoryWorkflow:
    """Test complete workflows"""
    
    def test_fetch_and_update_workflow(self, review_repository, mock_review_data, sample_reviews):
        """Test complete fetch and update workflow"""
        # Setup
        mock_review_data.get_unlabeled_reviews.return_value = sample_reviews
        
        # 1. Fetch unlabeled reviews
        reviews = review_repository.get_unlabeled_reviews(batch_id=1, limit=10)
        assert len(reviews) == 2
        
        # 2. Update labels
        for review in reviews:
            result = review_repository.update_labels(
                review_id=review['id'],
                labels={'sentiment': 'positive'},
                metadata={'confidence': 0.9}
            )
            assert result is True
        
        # Verify updates were called
        assert mock_review_data.update_reviews.call_count == 2
    
    def test_bulk_update_workflow(self, review_repository, mock_review_data, sample_reviews):
        """Test bulk update workflow"""
        # Setup
        mock_review_data.get_reviews_by_ids.return_value = sample_reviews
        mock_review_data.bulk_update_reviews.return_value = 2
        
        # 1. Fetch reviews by IDs
        reviews = review_repository.get_reviews_by_ids([1, 2])
        assert len(reviews) == 2
        
        # 2. Prepare bulk updates
        updates = [
            {
                'review_id': review['id'],
                'labels': {'sentiment': 'positive'},
                'metadata': {'confidence': 0.9}
            }
            for review in reviews
        ]
        
        # 3. Bulk update
        success_count = review_repository.bulk_update_labels(updates)
        assert success_count == 2


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("batch_id,limit,should_raise", [
    (None, 100, True),
    (0, 100, True),
    (-1, 100, True),
    (1, 0, True),
    (1, -10, True),
    (1, 100, False),
    (42, 50, False),
])
def test_get_unlabeled_reviews_validation(review_repository, batch_id, limit, should_raise):
    """Parametrized validation tests for get_unlabeled_reviews"""
    if should_raise:
        with pytest.raises(ValueError):
            review_repository.get_unlabeled_reviews(batch_id=batch_id, limit=limit)
    else:
        # Should not raise
        review_repository.get_unlabeled_reviews(batch_id=batch_id, limit=limit)


@pytest.mark.parametrize("review_id,labels,should_raise", [
    (None, {'sentiment': 'positive'}, True),
    (0, {'sentiment': 'positive'}, True),
    (-1, {'sentiment': 'positive'}, True),
    (1, None, True),
    (1, {'sentiment': 'positive'}, False),
    (123, {'sentiment': 'negative', 'aspects': ['price']}, False),
])
def test_update_labels_validation(review_repository, review_id, labels, should_raise):
    """Parametrized validation tests for update_labels"""
    if should_raise:
        with pytest.raises(ValueError):
            review_repository.update_labels(review_id=review_id, labels=labels)
    else:
        # Should not raise
        result = review_repository.update_labels(review_id=review_id, labels=labels)
        assert result is True
