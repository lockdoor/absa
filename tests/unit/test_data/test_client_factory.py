"""
Unit tests for ClientFactory

Tests the factory pattern for creating client instances.
"""

import pytest
from unittest.mock import Mock, patch
from review_radar.data.client_factory import ClientFactory, create_dataset
from review_radar.data.base_client import BaseClient


# ==================== Test Fixtures ====================

class MockSupabaseClient(BaseClient):
    """Mock Supabase client for testing"""
    
    def get_reviews_without_labels(self, limit=100, offset=0):
        return Mock()
    
    def update_reviews(self, review_id, update_data):
        pass


class MockPostgresClient(BaseClient):
    """Mock Postgres client for testing"""
    
    def get_reviews_without_labels(self, limit=100, offset=0):
        return Mock()
    
    def update_reviews(self, review_id, update_data):
        pass


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset factory registry before each test"""
    original_registry = ClientFactory._registry.copy()
    ClientFactory._registry = {}
    yield
    ClientFactory._registry = original_registry


@pytest.fixture
def mock_supabase_instance():
    """Mock Supabase client instance"""
    client = Mock()
    client.__class__.__name__ = 'SupabaseClient'
    return client


@pytest.fixture
def mock_postgres_instance():
    """Mock Postgres client instance"""
    client = Mock()
    client.__class__.__name__ = 'PostgresConnection'
    return client


@pytest.fixture
def mock_mongodb_instance():
    """Mock MongoDB client instance"""
    client = Mock()
    client.__class__.__name__ = 'MongoClient'
    return client


@pytest.fixture
def register_test_clients():
    """Register test client classes"""
    ClientFactory.register('supabase')(MockSupabaseClient)
    ClientFactory.register('postgres')(MockPostgresClient)


# ==================== Registration Tests ====================

class TestClientFactoryRegistration:
    """Test factory registration mechanism"""
    
    def test_register_decorator(self):
        """Can register client class with decorator"""
        
        @ClientFactory.register('test_type')
        class TestClient(BaseClient):
            def get_reviews_without_labels(self, limit=100, offset=0):
                return Mock()
            def update_reviews(self, review_id, update_data):
                pass
        
        assert 'test_type' in ClientFactory._registry
        assert ClientFactory._registry['test_type'] == TestClient
    
    def test_register_multiple_types(self):
        """Can register multiple client types"""
        
        @ClientFactory.register('type1')
        class Client1(BaseClient):
            def get_reviews_without_labels(self, limit=100, offset=0):
                return Mock()
            def update_reviews(self, review_id, update_data):
                pass
        
        @ClientFactory.register('type2')
        class Client2(BaseClient):
            def get_reviews_without_labels(self, limit=100, offset=0):
                return Mock()
            def update_reviews(self, review_id, update_data):
                pass
        
        assert len(ClientFactory._registry) == 2
        assert 'type1' in ClientFactory._registry
        assert 'type2' in ClientFactory._registry
    
    def test_list_supported_types(self, register_test_clients):
        """Can list all registered types"""
        types = ClientFactory.list_supported_types()
        
        assert isinstance(types, list)
        assert 'supabase' in types
        assert 'postgres' in types


# ==================== Creation Tests ====================

class TestClientFactoryCreate:
    """Test client creation"""
    
    def test_create_with_explicit_type(self, mock_supabase_instance, register_test_clients):
        """Creates client with explicit type"""
        client = ClientFactory.create(mock_supabase_instance, client_type='supabase')
        
        assert isinstance(client, MockSupabaseClient)
        assert client.client == mock_supabase_instance
    
    def test_create_passes_kwargs(self, mock_supabase_instance, register_test_clients):
        """Passes additional kwargs to client"""
        mock_logger = Mock()
        client = ClientFactory.create(
            mock_supabase_instance,
            client_type='supabase',
            logger=mock_logger
        )
        
        assert client.logger == mock_logger
    
    def test_create_raises_for_unknown_type(self, mock_supabase_instance):
        """Raises ValueError for unknown client type"""
        with pytest.raises(ValueError, match="Unknown client type: unknown_type"):
            ClientFactory.create(mock_supabase_instance, client_type='unknown_type')
    
    def test_error_message_shows_registered_types(self, register_test_clients, mock_supabase_instance):
        """Error message shows available types"""
        with pytest.raises(ValueError, match="Registered types:.*supabase.*postgres"):
            ClientFactory.create(mock_supabase_instance, client_type='invalid')


# ==================== Auto-detection Tests ====================

class TestClientTypeDetection:
    """Test automatic client type detection"""
    
    def test_detects_supabase_client(self, mock_supabase_instance):
        """Detects Supabase client"""
        client_type = ClientFactory._detect_client_type(mock_supabase_instance)
        
        assert client_type == 'supabase'
    
    def test_detects_postgres_client(self, mock_postgres_instance):
        """Detects Postgres client"""
        client_type = ClientFactory._detect_client_type(mock_postgres_instance)
        
        assert client_type == 'postgres'
    
    def test_detects_mongodb_client(self, mock_mongodb_instance):
        """Detects MongoDB client"""
        client_type = ClientFactory._detect_client_type(mock_mongodb_instance)
        
        assert client_type == 'mongodb'
    
    def test_detects_psycopg_client(self):
        """Detects psycopg client"""
        client = Mock()
        client.__class__.__name__ = 'psycopg2.connection'
        
        client_type = ClientFactory._detect_client_type(client)
        
        assert client_type == 'postgres'
    
    def test_detects_pymongo_client(self):
        """Detects pymongo client"""
        client = Mock()
        client.__class__.__name__ = 'pymongo.MongoClient'
        
        client_type = ClientFactory._detect_client_type(client)
        
        assert client_type == 'mongodb'
    
    def test_detects_mysql_client(self):
        """Detects MySQL client"""
        client = Mock()
        client.__class__.__name__ = 'MySQLConnection'
        
        client_type = ClientFactory._detect_client_type(client)
        
        assert client_type == 'mysql'
    
    def test_detection_is_case_insensitive(self):
        """Detection is case insensitive"""
        client = Mock()
        client.__class__.__name__ = 'SUPABASECLIENT'
        
        client_type = ClientFactory._detect_client_type(client)
        
        assert client_type == 'supabase'
    
    def test_raises_for_unknown_client(self):
        """Raises ValueError for unknown client"""
        client = Mock()
        client.__class__.__name__ = 'UnknownClient'
        
        with pytest.raises(ValueError, match="Cannot auto-detect client type"):
            ClientFactory._detect_client_type(client)
    
    def test_error_shows_client_name(self):
        """Error message shows client class name"""
        client = Mock()
        client.__class__.__name__ = 'CustomClient'
        
        with pytest.raises(ValueError, match="CustomClient"):
            ClientFactory._detect_client_type(client)


# ==================== Auto-create Tests ====================

class TestAutoCreate:
    """Test auto-detection during creation"""
    
    def test_create_without_type_autodetects(self, mock_supabase_instance, register_test_clients):
        """Creates client with auto-detection"""
        client = ClientFactory.create(mock_supabase_instance)
        
        assert isinstance(client, MockSupabaseClient)
    
    def test_autodetect_postgres(self, mock_postgres_instance, register_test_clients):
        """Auto-detects and creates Postgres client"""
        client = ClientFactory.create(mock_postgres_instance)
        
        assert isinstance(client, MockPostgresClient)
    
    def test_explicit_type_overrides_detection(self, mock_supabase_instance, register_test_clients):
        """Explicit type overrides auto-detection"""
        # Even though it's a Supabase instance, force it to be postgres
        client = ClientFactory.create(mock_supabase_instance, client_type='postgres')
        
        assert isinstance(client, MockPostgresClient)


# ==================== Convenience Function Tests ====================

class TestCreateDatasetFunction:
    """Test convenience function"""
    
    def test_create_dataset_function(self, mock_supabase_instance, register_test_clients):
        """create_dataset function works"""
        client = create_dataset(mock_supabase_instance, client_type='supabase')
        
        assert isinstance(client, MockSupabaseClient)
    
    def test_create_dataset_with_autodetect(self, mock_supabase_instance, register_test_clients):
        """create_dataset with auto-detection"""
        client = create_dataset(mock_supabase_instance)
        
        assert isinstance(client, MockSupabaseClient)
    
    def test_create_dataset_passes_kwargs(self, mock_supabase_instance, register_test_clients):
        """create_dataset passes kwargs"""
        mock_logger = Mock()
        client = create_dataset(
            mock_supabase_instance,
            client_type='supabase',
            logger=mock_logger
        )
        
        assert client.logger == mock_logger


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("class_name,expected_type", [
    ('SupabaseClient', 'supabase'),
    ('supabase_client', 'supabase'),
    ('PostgresConnection', 'postgres'),
    ('psycopg2.connection', 'postgres'),
    ('MongoClient', 'mongodb'),
    ('pymongo.MongoClient', 'mongodb'),
    ('MySQLConnection', 'mysql'),
])
def test_detection_patterns(class_name, expected_type):
    """Test various detection patterns"""
    client = Mock()
    client.__class__.__name__ = class_name
    
    detected = ClientFactory._detect_client_type(client)
    
    assert detected == expected_type
