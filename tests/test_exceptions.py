"""
Unit tests for the exception hierarchy.

Tests exception inheritance, context storage, and string representations.
"""

import pytest
from form_filling.exceptions import (
    FormFillingError,
    ConfigurationError,
    ElementError,
    ValueGenerationError,
    ValidationError,
    ResourceError,
)


class TestFormFillingError:
    """Tests for the base FormFillingError class."""
    
    def test_basic_error_creation(self):
        """Test creating a basic error without context."""
        error = FormFillingError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.context == {}
    
    def test_error_with_context(self):
        """Test creating an error with contextual information."""
        context = {"field_name": "email", "element_type": "text"}
        error = FormFillingError("Failed to fill field", context=context)
        
        assert error.message == "Failed to fill field"
        assert error.context == context
        assert "field_name=email" in str(error)
        assert "element_type=text" in str(error)
    
    def test_error_repr(self):
        """Test the repr representation of the error."""
        context = {"key": "value"}
        error = FormFillingError("Test error", context=context)
        repr_str = repr(error)
        
        assert "FormFillingError" in repr_str
        assert "Test error" in repr_str
        assert "key" in repr_str
    
    def test_error_inheritance(self):
        """Test that FormFillingError inherits from Exception."""
        error = FormFillingError("Test")
        assert isinstance(error, Exception)


class TestConfigurationError:
    """Tests for ConfigurationError."""
    
    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from FormFillingError."""
        error = ConfigurationError("Invalid config")
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)
    
    def test_configuration_error_with_context(self):
        """Test ConfigurationError with configuration-specific context."""
        context = {
            "config_key": "llm.timeout",
            "config_value": -1,
            "expected_type": "positive integer",
        }
        error = ConfigurationError("Invalid timeout value", context=context)
        
        assert error.message == "Invalid timeout value"
        assert error.context["config_key"] == "llm.timeout"
        assert error.context["config_value"] == -1


class TestElementError:
    """Tests for ElementError."""
    
    def test_element_error_inheritance(self):
        """Test that ElementError inherits from FormFillingError."""
        error = ElementError("Element not found")
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)
    
    def test_element_error_with_context(self):
        """Test ElementError with element-specific context."""
        context = {
            "element_type": "select",
            "field_name": "country",
            "selector": "#country-select",
            "page_url": "https://example.com/form",
        }
        error = ElementError("Cannot interact with element", context=context)
        
        assert error.message == "Cannot interact with element"
        assert error.context["element_type"] == "select"
        assert error.context["field_name"] == "country"
        assert "country" in str(error)


class TestValueGenerationError:
    """Tests for ValueGenerationError."""
    
    def test_value_generation_error_inheritance(self):
        """Test that ValueGenerationError inherits from FormFillingError."""
        error = ValueGenerationError("Failed to generate value")
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)
    
    def test_value_generation_error_with_context(self):
        """Test ValueGenerationError with generation-specific context."""
        context = {
            "field_name": "experience",
            "element_type": "textarea",
            "generation_method": "LLM",
            "llm_provider": "ollama",
            "llm_model": "mistral",
        }
        error = ValueGenerationError("LLM timeout", context=context)
        
        assert error.message == "LLM timeout"
        assert error.context["generation_method"] == "LLM"
        assert error.context["llm_provider"] == "ollama"


class TestValidationError:
    """Tests for ValidationError."""
    
    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from FormFillingError."""
        error = ValidationError("Invalid parameter")
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)
    
    def test_validation_error_with_context(self):
        """Test ValidationError with validation-specific context."""
        context = {
            "parameter_name": "timeout",
            "parameter_value": "invalid",
            "expected_type": "int",
            "validation_rule": "must be positive integer",
        }
        error = ValidationError("Parameter validation failed", context=context)
        
        assert error.message == "Parameter validation failed"
        assert error.context["parameter_name"] == "timeout"
        assert error.context["expected_type"] == "int"


class TestResourceError:
    """Tests for ResourceError."""
    
    def test_resource_error_inheritance(self):
        """Test that ResourceError inherits from FormFillingError."""
        error = ResourceError("Resource not available")
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)
    
    def test_resource_error_with_context(self):
        """Test ResourceError with resource-specific context."""
        context = {
            "resource_type": "file",
            "resource_path": "/path/to/resume.pdf",
            "operation": "read",
            "error_code": "ENOENT",
        }
        error = ResourceError("File not found", context=context)
        
        assert error.message == "File not found"
        assert error.context["resource_type"] == "file"
        assert error.context["operation"] == "read"


class TestExceptionHierarchy:
    """Tests for the overall exception hierarchy."""
    
    def test_all_custom_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from FormFillingError."""
        exceptions = [
            ConfigurationError,
            ElementError,
            ValueGenerationError,
            ValidationError,
            ResourceError,
        ]
        
        for exc_class in exceptions:
            error = exc_class("Test message")
            assert isinstance(error, FormFillingError)
            assert isinstance(error, Exception)
    
    def test_context_preserved_across_hierarchy(self):
        """Test that context is properly stored in all exception types."""
        context = {"test_key": "test_value"}
        exceptions = [
            FormFillingError("Test", context=context),
            ConfigurationError("Test", context=context),
            ElementError("Test", context=context),
            ValueGenerationError("Test", context=context),
            ValidationError("Test", context=context),
            ResourceError("Test", context=context),
        ]
        
        for error in exceptions:
            assert error.context == context
            assert "test_key=test_value" in str(error)
