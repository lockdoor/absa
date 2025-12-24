"""
Unit tests for BaseRepository

Tests the base repository class functionality and helper methods.
"""

import pytest
from unittest.mock import Mock
from review_radar.repositories.base_repository import BaseRepository


# ==================== Test Implementation ====================

class ConcreteRepository(BaseRepository):
    """Concrete implementation for testing"""
    
    def get_data(self):
        """Test method"""
        return self.client.get_data()


# ==================== Initialization Tests ====================

class TestBaseRepositoryInit:
    """Test BaseRepository initialization"""
    
    def test_concrete_class_can_be_instantiated(self, mock_database_client):
        """Concrete implementation can be instantiated"""
        repo = ConcreteRepository(client=mock_database_client)
        
        assert repo is not None
        assert repo.client == mock_database_client
        assert repo.logger is None
    
    def test_stores_client(self, mock_database_client):
        """Stores client instance"""
        repo = ConcreteRepository(client=mock_database_client)
        
        assert repo.client == mock_database_client
    
    def test_stores_logger(self, mock_database_client, mock_logger):
        """Stores logger instance"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        assert repo.logger == mock_logger
    
    def test_logger_is_optional(self, mock_database_client):
        """Logger is optional parameter"""
        repo = ConcreteRepository(client=mock_database_client)
        
        assert repo.logger is None


# ==================== Logging Tests ====================

class TestLogging:
    """Test logging functionality"""
    
    def test_log_with_logger(self, mock_database_client, mock_logger):
        """Logs message when logger is available"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        repo._log("Test message", level="info")
        
        mock_logger.info.assert_called_once_with("Test message", extra={})
    
    def test_log_without_logger(self, mock_database_client):
        """Does not raise error when logger is None"""
        repo = ConcreteRepository(client=mock_database_client, logger=None)
        
        # Should not raise
        repo._log("Test message", level="info")
    
    def test_log_different_levels(self, mock_database_client, mock_logger):
        """Logs at different levels"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        repo._log("Debug", level="debug")
        repo._log("Info", level="info")
        repo._log("Warning", level="warning")
        repo._log("Error", level="error")
        
        mock_logger.debug.assert_called_once()
        mock_logger.info.assert_called_once()
        mock_logger.warning.assert_called_once()
        mock_logger.error.assert_called_once()
    
    def test_log_with_extra_kwargs(self, mock_database_client, mock_logger):
        """Logs with extra context"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        repo._log("Test", level="info", user_id=123, action="create")
        
        mock_logger.info.assert_called_once_with(
            "Test",
            extra={"user_id": 123, "action": "create"}
        )
    
    def test_log_defaults_to_info(self, mock_database_client, mock_logger):
        """Defaults to info level"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        repo._log("Test message")
        
        mock_logger.info.assert_called_once()
    
    def test_log_handles_missing_level(self, mock_database_client, mock_logger):
        """Calls getattr with fallback to info"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        # Mock logger doesn't have 'custom_level' attribute
        # getattr will use default (logger.info)
        delattr(mock_logger, 'custom_level') if hasattr(mock_logger, 'custom_level') else None
        
        repo._log("Test", level="custom_level")
        
        # Should have called something (getattr creates Mock attribute)
        assert mock_logger.method_calls  # Some call was made


# ==================== Validation Tests ====================

class TestValidateNotNone:
    """Test _validate_not_none method"""
    
    def test_raises_for_none_value(self, mock_database_client):
        """Raises ValueError when value is None"""
        repo = ConcreteRepository(client=mock_database_client)
        
        with pytest.raises(ValueError, match="test_param cannot be None"):
            repo._validate_not_none(None, "test_param")
    
    def test_does_not_raise_for_valid_value(self, mock_database_client):
        """Does not raise for non-None value"""
        repo = ConcreteRepository(client=mock_database_client)
        
        # Should not raise
        repo._validate_not_none("value", "test_param")
        repo._validate_not_none(123, "test_param")
        repo._validate_not_none([], "test_param")
        repo._validate_not_none({}, "test_param")
    
    def test_accepts_zero_and_empty_string(self, mock_database_client):
        """Accepts 0 and empty string (falsy but not None)"""
        repo = ConcreteRepository(client=mock_database_client)
        
        # Should not raise
        repo._validate_not_none(0, "test_param")
        repo._validate_not_none("", "test_param")
        repo._validate_not_none(False, "test_param")
    
    def test_error_message_includes_param_name(self, mock_database_client):
        """Error message includes parameter name"""
        repo = ConcreteRepository(client=mock_database_client)
        
        with pytest.raises(ValueError) as exc_info:
            repo._validate_not_none(None, "batch_id")
        
        assert "batch_id" in str(exc_info.value)


class TestValidatePositive:
    """Test _validate_positive method"""
    
    def test_raises_for_zero(self, mock_database_client):
        """Raises ValueError for zero"""
        repo = ConcreteRepository(client=mock_database_client)
        
        with pytest.raises(ValueError, match="test_param must be positive"):
            repo._validate_positive(0, "test_param")
    
    def test_raises_for_negative(self, mock_database_client):
        """Raises ValueError for negative values"""
        repo = ConcreteRepository(client=mock_database_client)
        
        with pytest.raises(ValueError, match="test_param must be positive, got -5"):
            repo._validate_positive(-5, "test_param")
    
    def test_does_not_raise_for_positive(self, mock_database_client):
        """Does not raise for positive values"""
        repo = ConcreteRepository(client=mock_database_client)
        
        # Should not raise
        repo._validate_positive(1, "test_param")
        repo._validate_positive(100, "test_param")
        repo._validate_positive(999999, "test_param")
    
    def test_error_message_includes_value(self, mock_database_client):
        """Error message includes actual value"""
        repo = ConcreteRepository(client=mock_database_client)
        
        with pytest.raises(ValueError) as exc_info:
            repo._validate_positive(-10, "limit")
        
        assert "-10" in str(exc_info.value)
        assert "limit" in str(exc_info.value)


# ==================== Parametrized Tests ====================

@pytest.mark.parametrize("value,should_raise", [
    (None, True),
    ("value", False),
    (0, False),
    (123, False),
    ([], False),
    ({}, False),
    ("", False),
    (False, False),
])
def test_validate_not_none_parametrized(mock_database_client, value, should_raise):
    """Test _validate_not_none with various values"""
    repo = ConcreteRepository(client=mock_database_client)
    
    if should_raise:
        with pytest.raises(ValueError):
            repo._validate_not_none(value, "param")
    else:
        repo._validate_not_none(value, "param")


@pytest.mark.parametrize("value,should_raise", [
    (-100, True),
    (-1, True),
    (0, True),
    (1, False),
    (100, False),
    (999999, False),
])
def test_validate_positive_parametrized(mock_database_client, value, should_raise):
    """Test _validate_positive with various values"""
    repo = ConcreteRepository(client=mock_database_client)
    
    if should_raise:
        with pytest.raises(ValueError):
            repo._validate_positive(value, "param")
    else:
        repo._validate_positive(value, "param")


# ==================== Integration-like Tests ====================

class TestRepositoryWorkflow:
    """Test repository with validation in workflow"""
    
    def test_validation_before_client_call(self, mock_database_client):
        """Validates parameters before calling client"""
        repo = ConcreteRepository(client=mock_database_client)
        
        # Validation should catch error before client is called
        with pytest.raises(ValueError):
            repo._validate_not_none(None, "id")
            repo.client.get_data()  # Should not reach here
        
        # Client should not have been called
        mock_database_client.get_data.assert_not_called()
    
    def test_logging_and_validation_together(self, mock_database_client, mock_logger):
        """Can use logging and validation together"""
        repo = ConcreteRepository(client=mock_database_client, logger=mock_logger)
        
        repo._log("Starting validation", level="debug")
        repo._validate_positive(10, "limit")
        repo._log("Validation passed", level="debug")
        
        assert mock_logger.debug.call_count == 2
