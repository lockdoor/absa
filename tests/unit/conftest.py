"""
Unit Tests Configuration and Fixtures

Fixtures specific to unit tests.
"""

import pytest
from unittest.mock import Mock
import pandas as pd


# ==================== Mock Services ====================

@pytest.fixture
def mock_dataset():
    """Mock BaseDataset"""
    dataset = Mock()
    dataset.fetch_all_features.return_value = pd.DataFrame()
    return dataset


@pytest.fixture
def mock_repository():
    """Mock ReviewRepository"""
    repo = Mock()
    repo.get_unlabeled_reviews.return_value = pd.DataFrame()
    repo.get_batch_aspects.return_value = []
    repo.update_labels.return_value = True
    return repo


# @pytest.fixture
# def mock_labeling_provider():
#     """Mock LabelingProvider"""
#     from review_radar.services.labeling.providers.base_provider import LabelResult
    
#     provider = Mock()
#     provider.label_review.return_value = LabelResult(
#         labels={},
#         metadata={},
#         cost=0.0001,
#         avg_confidence=0.90
#     )
#     provider.get_model_info.return_value = {'name': 'mock-model'}
    
#     return provider
