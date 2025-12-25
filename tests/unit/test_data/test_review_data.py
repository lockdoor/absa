"""
Tests for ReviewData

ทดสอบ abstract interface และ contract
"""

import pytest
from unittest.mock import Mock
from abc import ABC

from review_radar.data.review_data import ReviewData
from review_radar.data.base_data import BaseData


# ==================== Mock Implementations ====================

class ConcreteReviewData(ReviewData):
    """Concrete implementation สำหรับ testing"""
    
    def __init__(self, client, logger=None):
        super().__init__(client, logger)
        self.mock_reviews = [
            {'id': 1, 'text': 'Review 1', 'batch_id': 1, 'labels': None},
            {'id': 2, 'text': 'Review 2', 'batch_id': 1, 'labels': None},
            {'id': 3, 'text': 'Review 3', 'batch_id': 2, 'labels': {'sentiment': 'positive'}},
        ]
    
    def get_unlabeled_reviews(self, batch_id: int, limit: int = 100, offset: int = 0):
        """Return unlabeled reviews for batch"""
        self._log(f"Fetching unlabeled reviews", batch_id=batch_id, limit=limit)
        
        unlabeled = [r for r in self.mock_reviews if r['batch_id'] == batch_id and r['labels'] is None]
        return unlabeled[offset:offset+limit]
    
    def get_reviews_by_ids(self, review_ids):
        """Return reviews by IDs"""
        self._log(f"Fetching reviews by IDs", review_ids=review_ids)
        return [r for r in self.mock_reviews if r['id'] in review_ids]
    
    def update_reviews(self, review_id: int, update_data):
        """Update single review"""
        self._log(f"Updating review {review_id}", update_data=update_data)
        for review in self.mock_reviews:
            if review['id'] == review_id:
                review.update(update_data)
    
    def bulk_update_reviews(self, updates):
        """Bulk update reviews"""
        self._log(f"Bulk updating {len(updates)} reviews")
        count = 0
        for update in updates:
            review_id = update.get('id')
            for review in self.mock_reviews:
                if review['id'] == review_id:
                    review.update({k: v for k, v in update.items() if k != 'id'})
                    count += 1
        return count


# ==================== Fixtures ====================

@pytest.fixture
def mock_client():
    """Create mock database client"""
    return Mock()


@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    return logger


@pytest.fixture
def review_data(mock_client, mock_logger):
    """Create ConcreteReviewData instance"""
    return ConcreteReviewData(client=mock_client, logger=mock_logger)


@pytest.fixture
def review_data_no_logger(mock_client):
    """Create ConcreteReviewData without logger"""
    return ConcreteReviewData(client=mock_client, logger=None)


# ==================== Tests ====================

class TestReviewDataInheritance:
    """Test inheritance structure"""
    
    def test_inherits_from_base_data(self):
        """Should inherit from BaseData"""
        assert issubclass(ReviewData, BaseData)
    
    def test_is_abstract(self):
        """Should be abstract class"""
        assert issubclass(ReviewData, ABC)
    
    def test_cannot_instantiate_directly(self, mock_client):
        """Should not instantiate ReviewData directly"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            ReviewData(client=mock_client)
    
    def test_concrete_implementation_valid(self, review_data, mock_client):
        """Should instantiate concrete implementation"""
        assert isinstance(review_data, ReviewData)
        assert isinstance(review_data, BaseData)
        assert review_data.client == mock_client


class TestReviewDataGetUnlabeledReviews:
    """Test get_unlabeled_reviews method"""
    
    def test_get_unlabeled_reviews(self, review_data):
        """Should return unlabeled reviews for batch"""
        reviews = review_data.get_unlabeled_reviews(batch_id=1, limit=10)
        
        assert len(reviews) == 2
        assert all(r['labels'] is None for r in reviews)
        assert all(r['batch_id'] == 1 for r in reviews)
    
    def test_get_unlabeled_reviews_with_limit(self, review_data):
        """Should respect limit parameter"""
        reviews = review_data.get_unlabeled_reviews(batch_id=1, limit=1)
        assert len(reviews) == 1
    
    def test_get_unlabeled_reviews_with_offset(self, review_data):
        """Should respect offset parameter"""
        reviews = review_data.get_unlabeled_reviews(batch_id=1, limit=10, offset=1)
        assert len(reviews) == 1
        assert reviews[0]['id'] == 2
    
    def test_get_unlabeled_reviews_empty_batch(self, review_data):
        """Should return empty list for batch with no unlabeled reviews"""
        reviews = review_data.get_unlabeled_reviews(batch_id=2)
        assert reviews == []
    
    def test_get_unlabeled_reviews_logs(self, review_data, mock_logger):
        """Should log operation"""
        review_data.get_unlabeled_reviews(batch_id=1, limit=10)
        
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args
        assert "Fetching unlabeled reviews" in call_args[0][0]


class TestReviewDataGetReviewsByIds:
    """Test get_reviews_by_ids method"""
    
    def test_get_reviews_by_ids(self, review_data):
        """Should return reviews with specified IDs"""
        reviews = review_data.get_reviews_by_ids([1, 3])
        
        assert len(reviews) == 2
        assert reviews[0]['id'] == 1
        assert reviews[1]['id'] == 3
    
    def test_get_reviews_by_ids_single(self, review_data):
        """Should work with single ID"""
        reviews = review_data.get_reviews_by_ids([2])
        assert len(reviews) == 1
        assert reviews[0]['id'] == 2
    
    def test_get_reviews_by_ids_empty_list(self, review_data):
        """Should return empty list for empty IDs"""
        reviews = review_data.get_reviews_by_ids([])
        assert reviews == []
    
    def test_get_reviews_by_ids_nonexistent(self, review_data):
        """Should return empty list for non-existent IDs"""
        reviews = review_data.get_reviews_by_ids([999])
        assert reviews == []
    
    def test_get_reviews_by_ids_logs(self, review_data, mock_logger):
        """Should log operation"""
        review_data.get_reviews_by_ids([1, 2])
        
        mock_logger.info.assert_called()


class TestReviewDataUpdateReviews:
    """Test update_reviews method"""
    
    def test_update_reviews(self, review_data):
        """Should update single review"""
        review_data.update_reviews(
            review_id=1,
            update_data={'labels': {'sentiment': 'positive'}}
        )
        
        # Verify update
        reviews = review_data.get_reviews_by_ids([1])
        assert reviews[0]['labels'] == {'sentiment': 'positive'}
    
    def test_update_reviews_multiple_fields(self, review_data):
        """Should update multiple fields"""
        review_data.update_reviews(
            review_id=1,
            update_data={
                'labels': {'sentiment': 'positive'},
                'labeled_at': '2024-01-01'
            }
        )
        
        reviews = review_data.get_reviews_by_ids([1])
        assert reviews[0]['labels'] == {'sentiment': 'positive'}
        assert reviews[0]['labeled_at'] == '2024-01-01'
    
    def test_update_reviews_logs(self, review_data, mock_logger):
        """Should log operation"""
        review_data.update_reviews(1, {'labels': {}})
        
        mock_logger.info.assert_called()


class TestReviewDataBulkUpdateReviews:
    """Test bulk_update_reviews method"""
    
    def test_bulk_update_reviews(self, review_data):
        """Should update multiple reviews"""
        updates = [
            {'id': 1, 'labels': {'sentiment': 'positive'}},
            {'id': 2, 'labels': {'sentiment': 'negative'}},
        ]
        
        count = review_data.bulk_update_reviews(updates)
        
        assert count == 2
        
        # Verify updates
        reviews = review_data.get_reviews_by_ids([1, 2])
        assert reviews[0]['labels'] == {'sentiment': 'positive'}
        assert reviews[1]['labels'] == {'sentiment': 'negative'}
    
    def test_bulk_update_reviews_empty_list(self, review_data):
        """Should handle empty list"""
        count = review_data.bulk_update_reviews([])
        assert count == 0
    
    def test_bulk_update_reviews_partial_success(self, review_data):
        """Should return count of successful updates"""
        updates = [
            {'id': 1, 'labels': {'sentiment': 'positive'}},
            {'id': 999, 'labels': {'sentiment': 'negative'}},  # non-existent
        ]
        
        count = review_data.bulk_update_reviews(updates)
        assert count == 1
    
    def test_bulk_update_reviews_logs(self, review_data, mock_logger):
        """Should log operation"""
        review_data.bulk_update_reviews([{'id': 1, 'labels': {}}])
        
        mock_logger.info.assert_called()


class TestReviewDataIntegration:
    """Test integration scenarios"""
    
    def test_full_workflow(self, review_data):
        """Should work through complete workflow"""
        # 1. Get unlabeled reviews
        reviews = review_data.get_unlabeled_reviews(batch_id=1)
        assert len(reviews) == 2
        
        # 2. Update first review
        review_data.update_reviews(
            reviews[0]['id'],
            {'labels': {'sentiment': 'positive'}}
        )
        
        # 3. Bulk update remaining
        count = review_data.bulk_update_reviews([
            {'id': reviews[1]['id'], 'labels': {'sentiment': 'negative'}}
        ])
        assert count == 1
        
        # 4. Verify all labeled
        unlabeled = review_data.get_unlabeled_reviews(batch_id=1)
        assert len(unlabeled) == 0
    
    def test_without_logger(self, review_data_no_logger):
        """Should work without logger"""
        # Should not raise error
        reviews = review_data_no_logger.get_unlabeled_reviews(batch_id=1)
        assert len(reviews) == 2
        
        review_data_no_logger.update_reviews(1, {'labels': {}})
        count = review_data_no_logger.bulk_update_reviews([{'id': 2, 'labels': {}}])
        assert count == 1
