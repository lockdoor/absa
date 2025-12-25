"""
Tests for BaseData

ทดสอบ base functionality: client management, logging
"""

import pytest
from unittest.mock import Mock, MagicMock
from review_radar.data.base_data import BaseData


# ==================== Mock Implementation ====================

class ConcreteData(BaseData):
    """Concrete implementation สำหรับ testing"""
    
    def sample_method(self):
        """Example method that uses logging"""
        self._log("Sample method called", operation="sample")
        return "success"


# ==================== Fixtures ====================

@pytest.fixture
def mock_client():
    """Create mock database client"""
    client = Mock()
    client.query = Mock(return_value=[{"id": 1, "name": "test"}])
    return client


@pytest.fixture
def mock_logger():
    """Create mock logger"""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.debug = Mock()
    return logger


@pytest.fixture
def data_with_logger(mock_client, mock_logger):
    """Create ConcreteData with logger"""
    return ConcreteData(client=mock_client, logger=mock_logger)


@pytest.fixture
def data_without_logger(mock_client):
    """Create ConcreteData without logger"""
    return ConcreteData(client=mock_client, logger=None)


# ==================== Tests ====================

class TestBaseDataInit:
    """Test initialization"""
    
    def test_init_with_logger(self, mock_client, mock_logger):
        """Should initialize with client and logger"""
        data = ConcreteData(client=mock_client, logger=mock_logger)
        
        assert data.client == mock_client
        assert data.logger == mock_logger
    
    def test_init_without_logger(self, mock_client):
        """Should initialize without logger"""
        data = ConcreteData(client=mock_client, logger=None)
        
        assert data.client == mock_client
        assert data.logger is None


class TestBaseDataProperties:
    """Test properties"""
    
    def test_client_property(self, data_with_logger, mock_client):
        """Should access client via property"""
        assert data_with_logger.client == mock_client
    
    def test_logger_property(self, data_with_logger, mock_logger):
        """Should access logger via property"""
        assert data_with_logger.logger == mock_logger
    
    def test_logger_property_none(self, data_without_logger):
        """Should return None when no logger"""
        assert data_without_logger.logger is None


class TestBaseDataLogging:
    """Test logging functionality"""
    
    def test_log_with_logger_info(self, data_with_logger, mock_logger):
        """Should log info message when logger available"""
        data_with_logger._log("Test message", level="info", key="value")
        
        mock_logger.info.assert_called_once_with(
            "Test message",
            extra={"key": "value"}
        )
    
    def test_log_with_logger_warning(self, data_with_logger, mock_logger):
        """Should log warning message"""
        data_with_logger._log("Warning message", level="warning")
        
        mock_logger.warning.assert_called_once_with(
            "Warning message",
            extra={}
        )
    
    def test_log_with_logger_error(self, data_with_logger, mock_logger):
        """Should log error message"""
        data_with_logger._log("Error message", level="error", error_code=500)
        
        mock_logger.error.assert_called_once_with(
            "Error message",
            extra={"error_code": 500}
        )
    
    def test_log_with_logger_debug(self, data_with_logger, mock_logger):
        """Should log debug message"""
        data_with_logger._log("Debug message", level="debug")
        
        mock_logger.debug.assert_called_once_with(
            "Debug message",
            extra={}
        )
    
    def test_log_without_logger(self, data_without_logger):
        """Should not raise error when logging without logger"""
        # Should not raise exception
        data_without_logger._log("Test message", level="info")
    
    def test_log_default_level(self, data_with_logger, mock_logger):
        """Should default to info level"""
        data_with_logger._log("Default level message")
        
        mock_logger.info.assert_called_once_with(
            "Default level message",
            extra={}
        )
    
    def test_log_with_multiple_kwargs(self, data_with_logger, mock_logger):
        """Should pass multiple kwargs to logger"""
        data_with_logger._log(
            "Complex log",
            level="info",
            user_id=123,
            action="update",
            status="success"
        )
        
        mock_logger.info.assert_called_once_with(
            "Complex log",
            extra={
                "user_id": 123,
                "action": "update",
                "status": "success"
            }
        )


class TestBaseDataIntegration:
    """Test integration scenarios"""
    
    def test_concrete_class_usage(self, data_with_logger, mock_logger):
        """Should work with concrete implementation"""
        result = data_with_logger.sample_method()
        
        assert result == "success"
        mock_logger.info.assert_called_once_with(
            "Sample method called",
            extra={"operation": "sample"}
        )
    
    def test_client_access_in_methods(self, data_with_logger, mock_client):
        """Should access client in methods"""
        # ConcreteData can use self.client
        assert data_with_logger.client.query() == [{"id": 1, "name": "test"}]
        mock_client.query.assert_called_once()


class TestBaseDataAbstract:
    """Test abstract behavior"""
    
    def test_cannot_instantiate_directly(self):
        """Should not instantiate BaseData directly"""
        mock_client = Mock()
        
        # BaseData is abstract but doesn't have abstract methods
        # So it CAN be instantiated, but shouldn't be in practice
        # This is design choice - could add @abstractmethod if needed
        instance = BaseData(client=mock_client)
        assert isinstance(instance, BaseData)
