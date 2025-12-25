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
    
    # Mock table chain
    table_mock = Mock()
    client.table.return_value = table_mock
    
    # Mock query chain
    query_mock = Mock()
    table_mock.select.return_value = query_mock
    query_mock.eq.return_value = query_mock
    query_mock.is_.return_value = query_mock
    query_mock.in_.return_value = query_mock
    query_mock.range.return_value = query_mock
    
    # Mock update chain
    update_mock = Mock()
    table_mock.update.return_value = update_mock
    update_mock.eq.return_value = update_mock
    
    # Mock execute response
    execute_response = Mock()
    execute_response.data = []
    query_mock.execute.return_value = execute_response
    update_mock.execute.return_value = execute_response
    
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
