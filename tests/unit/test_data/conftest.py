"""
Data Module Test Fixtures

Fixtures specific to review_radar.data module tests.
Uses helper functions from tests.fixtures.sample_data for DRY principle.
"""

import pytest
import sys
from pathlib import Path

# Add tests directory to path to import fixtures
tests_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(tests_dir))

from fixtures.sample_data import (
    get_sample_reviews,
    get_sample_batch,
    SAMPLE_ASPECTS,
    SAMPLE_LABEL_RESULT
)


# ==================== Data Fixtures ====================

@pytest.fixture
def sample_reviews_df():
    """Sample reviews DataFrame without labels"""
    return get_sample_reviews(count=3, with_labels=False)


@pytest.fixture
def sample_labeled_reviews_df():
    """Sample reviews DataFrame with labels"""
    return get_sample_reviews(count=2, with_labels=True)


@pytest.fixture
def sample_batch():
    """Sample batch data"""
    return get_sample_batch(batch_id=100)


@pytest.fixture
def sample_aspects():
    """Sample aspects list"""
    return SAMPLE_ASPECTS


@pytest.fixture
def sample_label_result():
    """Sample label result from LLM"""
    return SAMPLE_LABEL_RESULT
