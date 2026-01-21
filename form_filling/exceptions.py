"""
Enhanced exception hierarchy for the form filling system.

This module provides a comprehensive set of custom exceptions with contextual
information to improve error handling and debugging capabilities.
"""

from typing import Optional, Dict, Any


class FormFillingError(Exception):
    """
    Base exception for all form filling operations.

    This exception includes support for contextual information to aid in
    debugging and error recovery.

    Attributes:
        message: The error message describing what went wrong
        context: Additional contextual information about the error
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Initialize the FormFillingError.

        Args:
            message: The error message
            context: Optional dictionary containing contextual information
                    such as element details, field names, operation IDs, etc.
        """
        super().__init__(message)
        self.message = message
        self.context = context.copy() if context else {}

    def __str__(self) -> str:
        """Return a string representation including context if available."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Context: {context_str})"
        return self.message

    def __repr__(self) -> str:
        """Return a detailed representation of the exception."""
        return f"{self.__class__.__name__}(message={self.message!r}, context={self.context!r})"


class ConfigurationError(FormFillingError):
    """
    Raised when configuration is invalid or missing.

    This exception is raised during configuration validation or when
    required configuration values are missing or invalid.

    Context keys:
        - config_key: The configuration key that caused the error
        - config_value: The invalid configuration value
        - expected_type: The expected type for the configuration value
        - validation_error: Specific validation error message
    """

    pass


class ElementError(FormFillingError):
    """
    Raised when element operations fail.

    This exception covers issues related to locating, identifying, or
    interacting with form elements.

    Context keys:
        - element_type: The type of element (text, select, radio, etc.)
        - field_name: The name or identifier of the field
        - selector: The selector used to locate the element
        - page_url: The URL of the page containing the element
        - element_state: The state of the element when the error occurred
    """

    pass


class ValueGenerationError(FormFillingError):
    """
    Raised when value generation fails.

    This exception is raised when the system cannot generate an appropriate
    value for a form field, including LLM failures and content generation issues.

    Context keys:
        - field_name: The field for which value generation failed
        - element_type: The type of element requiring a value
        - generation_method: The method used for value generation (LLM, resume, etc.)
        - llm_provider: The LLM provider if applicable
        - llm_model: The LLM model if applicable
        - error_details: Detailed error information from the generation process
    """

    pass


class ValidationError(FormFillingError):
    """
    Raised when input validation fails.

    This exception is raised when method parameters or input values fail
    validation checks.

    Context keys:
        - parameter_name: The name of the parameter that failed validation
        - parameter_value: The invalid parameter value
        - expected_type: The expected type for the parameter
        - validation_rule: The validation rule that was violated
        - allowed_values: List of allowed values if applicable
    """

    pass


class ResourceError(FormFillingError):
    """
    Raised when resource operations fail.

    This exception covers issues related to file I/O, network operations,
    memory management, and other resource-related failures.

    Context keys:
        - resource_type: The type of resource (file, network, memory, etc.)
        - resource_path: The path or identifier of the resource
        - operation: The operation that failed (read, write, connect, etc.)
        - error_code: System error code if applicable
        - available_memory: Available memory if memory-related
    """

    pass
