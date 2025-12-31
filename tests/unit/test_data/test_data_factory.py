"""
Tests for DataFactory

ทดสอบ Factory pattern + Singleton management
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os

from review_radar.data.data_factory import DataFactory
from review_radar.data.base_data import BaseData
from review_radar.data.review_data import ReviewData
from review_radar.data.review_data_supabase_client import ReviewDataSupabaseClient


# ==================== Fixtures ====================

@pytest.fixture(autouse=True)
def reset_factory():
    """Reset factory before each test"""
    DataFactory.reset()
    yield
    DataFactory.reset()


@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = Mock()
    logger.info = Mock()
    return logger


@pytest.fixture
def mock_supabase_env():
    """Mock Supabase environment variables"""
    with patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'SUPABASE_KEY': 'test_key'
    }):
        yield


# ==================== Tests ====================

class TestDataFactoryValidation:
    """Test input validation"""
    
    def test_invalid_data_type(self):
        """Should raise ValueError for invalid data_type"""
        with pytest.raises(ValueError, match="Invalid data_type"):
            DataFactory.create(data_type='invalid')
    
    def test_invalid_client_type(self):
        """Should raise ValueError for invalid client_type"""
        with pytest.raises(ValueError, match="Invalid client_type"):
            DataFactory.create(data_type='review', client_type='invalid')
    
    def test_valid_data_types(self, mock_supabase_env):
        """Should accept valid data_types"""
        with patch('supabase.create_client'):
            # Test review (should work)
            review = DataFactory.create(data_type='review')
            assert review is not None
            assert isinstance(review, ReviewData)
            
            # Reset before testing next type
            DataFactory.reset()
            
            # Test batch (may not be implemented yet)
            
            batch = DataFactory.create(data_type='batch')
            assert batch is not None
            DataFactory.reset()

    
    def test_valid_client_types(self, mock_supabase_env):
        """Should accept valid client_types"""
        with patch('supabase.create_client'):
            # supabase is implemented
            instance = DataFactory.create(client_type='supabase')
            assert instance is not None
            
            DataFactory.reset()
            
            # postgres not yet implemented
            with pytest.raises(NotImplementedError):
                DataFactory.create(client_type='postgres')


class TestDataFactorySupabaseCreation:
    """Test Supabase client creation"""
    
    @patch('supabase.create_client')
    def test_create_review_supabase_client(self, mock_create_client, mock_supabase_env, mock_logger):
        """Should create ReviewDataSupabaseClient"""
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        client = DataFactory.create(
            data_type='review',
            client_type='supabase',
            logger=mock_logger
        )
        
        assert isinstance(client, ReviewDataSupabaseClient)
        assert isinstance(client, ReviewData)
        assert isinstance(client, BaseData)
        assert client.logger == mock_logger
        
        mock_create_client.assert_called_once_with(
            'https://test.supabase.co',
            'test_key'
        )
    
    def test_create_supabase_missing_env_url(self):
        """Should raise ValueError when SUPABASE_URL missing"""
        with patch.dict(os.environ, {'SUPABASE_KEY': 'test_key'}, clear=True):
            with pytest.raises(ValueError, match="Supabase credentials not found"):
                DataFactory.create(data_type='review', client_type='supabase')
    
    def test_create_supabase_missing_env_key(self):
        """Should raise ValueError when SUPABASE_KEY missing"""
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://test.supabase.co'}, clear=True):
            with pytest.raises(ValueError, match="Supabase credentials not found"):
                DataFactory.create(data_type='review', client_type='supabase')
    
    @patch('supabase.create_client')
    def test_create_without_logger(self, mock_create_client, mock_supabase_env):
        """Should create client without logger"""
        mock_create_client.return_value = Mock()
        
        client = DataFactory.create(data_type='review', client_type='supabase')
        
        assert client.logger is None


class TestDataFactorySingleton:
    """Test singleton pattern"""
    
    @patch('supabase.create_client')
    def test_singleton_same_parameters(self, mock_create_client, mock_supabase_env):
        """Should return same instance for same parameters"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        client2 = DataFactory.create(data_type='review', client_type='supabase')
        
        assert client1 is client2
        # create_client should be called only once
        assert mock_create_client.call_count == 1
    
    @patch('supabase.create_client')
    def test_singleton_different_data_type(self, mock_create_client, mock_supabase_env):
        """Should create different instances for different data_type"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        
        # batch not implemented yet, so can't test
        # But we can verify review is stored
        instances = DataFactory.list_instances()
        assert ('review', 'supabase') in instances
    
    @patch('supabase.create_client')
    def test_singleton_logger_ignored(self, mock_create_client, mock_supabase_env):
        """Should return same instance even with different logger"""
        mock_create_client.return_value = Mock()
        
        logger1 = Mock()
        logger2 = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase', logger=logger1)
        client2 = DataFactory.create(data_type='review', client_type='supabase', logger=logger2)
        
        # Same instance (singleton ignores logger parameter after first creation)
        assert client1 is client2
        # First logger is used
        assert client1.logger == logger1


class TestDataFactoryReset:
    """Test reset functionality"""
    
    @patch('supabase.create_client')
    def test_reset_all(self, mock_create_client, mock_supabase_env):
        """Should reset all instances"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        
        DataFactory.reset()
        
        # Should create new instance
        client2 = DataFactory.create(data_type='review', client_type='supabase')
        assert client1 is not client2
        assert mock_create_client.call_count == 2
    
    @patch('supabase.create_client')
    def test_reset_specific_data_type(self, mock_create_client, mock_supabase_env):
        """Should reset only specific data_type"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        
        # Reset only review
        DataFactory.reset(data_type='review')
        
        # Should create new instance
        client2 = DataFactory.create(data_type='review', client_type='supabase')
        assert client1 is not client2
    
    @patch('supabase.create_client')
    def test_reset_specific_client_type(self, mock_create_client, mock_supabase_env):
        """Should reset only specific client_type"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        
        # Reset only supabase
        DataFactory.reset(client_type='supabase')
        
        # Should create new instance
        client2 = DataFactory.create(data_type='review', client_type='supabase')
        assert client1 is not client2
    
    @patch('supabase.create_client')
    def test_reset_specific_combination(self, mock_create_client, mock_supabase_env):
        """Should reset specific combination only"""
        mock_create_client.return_value = Mock()
        
        client1 = DataFactory.create(data_type='review', client_type='supabase')
        
        # Reset specific combination
        DataFactory.reset(data_type='review', client_type='supabase')
        
        # Should create new instance
        client2 = DataFactory.create(data_type='review', client_type='supabase')
        assert client1 is not client2


class TestDataFactoryGetInstance:
    """Test get_instance method"""
    
    def test_get_instance_not_created(self):
        """Should return None if instance not created"""
        instance = DataFactory.get_instance('review', 'supabase')
        assert instance is None
    
    @patch('supabase.create_client')
    def test_get_instance_exists(self, mock_create_client, mock_supabase_env):
        """Should return existing instance"""
        mock_create_client.return_value = Mock()
        
        created = DataFactory.create(data_type='review', client_type='supabase')
        fetched = DataFactory.get_instance('review', 'supabase')
        
        assert fetched is created


class TestDataFactoryListInstances:
    """Test list_instances method"""
    
    def test_list_instances_empty(self):
        """Should return empty dict when no instances"""
        instances = DataFactory.list_instances()
        assert instances == {}
    
    @patch('supabase.create_client')
    def test_list_instances_with_data(self, mock_create_client, mock_supabase_env):
        """Should list all created instances"""
        mock_create_client.return_value = Mock()
        
        client = DataFactory.create(data_type='review', client_type='supabase')
        instances = DataFactory.list_instances()
        
        assert len(instances) == 1
        assert ('review', 'supabase') in instances
        assert instances[('review', 'supabase')] is client
    
    @patch('supabase.create_client')
    def test_list_instances_returns_copy(self, mock_create_client, mock_supabase_env):
        """Should return copy, not original dict"""
        mock_create_client.return_value = Mock()
        
        DataFactory.create(data_type='review', client_type='supabase')
        instances1 = DataFactory.list_instances()
        instances2 = DataFactory.list_instances()
        
        # Should be equal but not same object
        assert instances1 == instances2
        assert instances1 is not instances2


class TestDataFactoryIntegration:
    """Integration tests"""
    
    @patch('supabase.create_client')
    def test_full_workflow(self, mock_create_client, mock_supabase_env, mock_logger):
        """Should work through complete workflow"""
        mock_supabase = Mock()
        mock_create_client.return_value = mock_supabase
        
        # 1. Create client
        client1 = DataFactory.create('review', 'supabase', mock_logger)
        assert isinstance(client1, ReviewDataSupabaseClient)
        
        # 2. Get same instance
        client2 = DataFactory.create('review', 'supabase')
        assert client1 is client2
        
        # 3. Check instance exists
        fetched = DataFactory.get_instance('review', 'supabase')
        assert fetched is client1
        
        # 4. List instances
        instances = DataFactory.list_instances()
        assert len(instances) == 1
        
        # 5. Reset
        DataFactory.reset()
        
        # 6. Create new instance
        client3 = DataFactory.create('review', 'supabase')
        assert client3 is not client1
        
        # Should have called create_client twice
        assert mock_create_client.call_count == 2


class TestDataFactoryNotImplemented:
    """Test not-yet-implemented features"""
    
    def test_postgres_not_implemented(self):
        """Should raise NotImplementedError for postgres"""
        with pytest.raises(NotImplementedError, match="PostgreSQL clients"):
            DataFactory.create(data_type='review', client_type='postgres')
