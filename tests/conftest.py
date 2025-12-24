"""
Pytest Configuration and Fixtures

Global fixtures shared across all tests.
Contains database client mocks used throughout the test suite.
"""

import pytest
from unittest.mock import Mock


# ==================== Database Client Mocks ====================

@pytest.fixture
def mock_client():
    """Mock generic database client"""
    client = Mock()
    return client


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with table() method chain"""
    client = Mock()
    
    # Mock the response object with data attribute
    mock_response = Mock()
    mock_response.data = []
    
    # Mock table().select().is_().range().execute() chain
    mock_query = Mock()
    mock_query.select.return_value = mock_query
    mock_query.is_.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.update.return_value = mock_query
    mock_query.range.return_value = mock_query
    mock_query.execute.return_value = mock_response
    
    client.table.return_value = mock_query
    
    return client


@pytest.fixture
def mock_postgres_client():
    """Mock PostgreSQL client with cursor()"""
    client = Mock()
    
    mock_cursor = Mock()
    mock_cursor.fetchall.return_value = []
    mock_cursor.description = []
    
    client.cursor.return_value = mock_cursor
    client.commit = Mock()
    
    return client
