"""
Repository Tests Configuration and Fixtures

Fixtures specific to repository layer tests.
"""

import pytest
from unittest.mock import Mock
import pandas as pd


# ==================== Mock Client Fixtures ====================

@pytest.fixture
def mock_database_client():
    """Mock database client for repository tests"""
    client = Mock()
    
    # Mock common methods
    client.get_reviews_without_labels.return_value = pd.DataFrame()
    client.update_reviews.return_value = None
    
    return client


@pytest.fixture
def mock_logger():
    """Mock logger instance"""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    
    return logger
