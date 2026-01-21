"""
Property-based tests for exception error handling consistency.

Feature: project-refactoring, Property 3: Error Handling Consistency
Validates: Requirements 3.5, 4.2, 4.4

Tests that error handling is consistent across all exception types,
with proper context storage and appropriate error information.
"""

import pytest
from hypothesis import given, strategies as st
from form_filling.exceptions import (
    FormFillingError,
    ConfigurationError,
    ElementError,
    ValueGenerationError,
    ValidationError,
    ResourceError,
)


# Strategy for generating exception classes
exception_classes = st.sampled_from(
    [
        FormFillingError,
        ConfigurationError,
        ElementError,
        ValueGenerationError,
        ValidationError,
        ResourceError,
    ]
)

# Strategy for generating error messages
error_messages = st.text(min_size=1, max_size=200)

# Strategy for generating context dictionaries
context_keys = st.text(
    alphabet=st.characters(
        whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters="_"
    ),
    min_size=1,
    max_size=50,
)

context_values = st.one_of(
    st.text(max_size=100),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.none(),
)

context_dicts = st.dictionaries(
    keys=context_keys, values=context_values, min_size=0, max_size=10
)


class TestErrorHandlingConsistency:
    """
    Property 3: Error Handling Consistency

    For any error condition, the system should raise appropriate error types
    with contextual information and log them at correct severity levels.
    """

    @given(exception_class=exception_classes, message=error_messages)
    def test_all_exceptions_accept_message(self, exception_class, message):
        """
        Property: All exception types should accept a message parameter.

        For any exception class and any message string, creating an exception
        should succeed and store the message correctly.
        """
        error = exception_class(message)
        assert error.message == message
        assert str(error) == message

    @given(
        exception_class=exception_classes, message=error_messages, context=context_dicts
    )
    def test_all_exceptions_accept_context(self, exception_class, message, context):
        """
        Property: All exception types should accept and store context.

        For any exception class, message, and context dictionary, creating
        an exception should store the context correctly.
        """
        error = exception_class(message, context=context)
        assert error.context == context
        assert error.message == message

    @given(
        exception_class=exception_classes, message=error_messages, context=context_dicts
    )
    def test_context_preserved_in_string_representation(
        self, exception_class, message, context
    ):
        """
        Property: Context information should be included in string representation.

        For any exception with context, the string representation should include
        context information when context is non-empty.
        """
        error = exception_class(message, context=context)
        error_str = str(error)

        # Message should always be in the string representation
        assert message in error_str

        # If context is non-empty, it should be reflected in the string
        if context:
            assert "Context:" in error_str or any(
                str(k) in error_str for k in context.keys()
            )

    @given(exception_class=exception_classes, message=error_messages)
    def test_exceptions_without_context_have_empty_dict(self, exception_class, message):
        """
        Property: Exceptions created without context should have empty context dict.

        For any exception created without a context parameter, the context
        attribute should be an empty dictionary, not None.
        """
        error = exception_class(message)
        assert error.context == {}
        assert isinstance(error.context, dict)

    @given(
        exception_class=exception_classes, message=error_messages, context=context_dicts
    )
    def test_all_exceptions_inherit_from_base(self, exception_class, message, context):
        """
        Property: All custom exceptions should inherit from FormFillingError.

        For any exception class in the hierarchy, instances should be
        instances of both FormFillingError and Exception.
        """
        error = exception_class(message, context=context)
        assert isinstance(error, FormFillingError)
        assert isinstance(error, Exception)

    @given(
        exception_class=exception_classes, message=error_messages, context=context_dicts
    )
    def test_exception_repr_is_valid(self, exception_class, message, context):
        """
        Property: Exception repr should be valid and informative.

        For any exception, the repr should contain the class name and
        be a valid Python representation.
        """
        error = exception_class(message, context=context)
        repr_str = repr(error)

        # Should contain the class name
        assert exception_class.__name__ in repr_str

        # Should be a non-empty string
        assert len(repr_str) > 0

    @given(
        exception_class=exception_classes, message=error_messages, context=context_dicts
    )
    def test_context_immutability_after_creation(
        self, exception_class, message, context
    ):
        """
        Property: Context dictionary should be independent after creation.

        For any exception, modifying the original context dict after exception
        creation should not affect the exception's stored context.
        """
        original_context = context.copy()
        error = exception_class(message, context=context)

        # Modify the original context
        context["new_key"] = "new_value"

        # Exception's context should remain unchanged
        assert error.context == original_context
        assert "new_key" not in error.context

    @given(exception_class=exception_classes, message=error_messages)
    def test_exception_can_be_raised_and_caught(self, exception_class, message):
        """
        Property: All exceptions should be raisable and catchable.

        For any exception class and message, the exception should be
        raisable and catchable as both its specific type and base types.
        """
        with pytest.raises(exception_class) as exc_info:
            raise exception_class(message)

        assert exc_info.value.message == message

        # Should also be catchable as FormFillingError
        with pytest.raises(FormFillingError):
            raise exception_class(message)

        # Should also be catchable as Exception
        with pytest.raises(Exception):
            raise exception_class(message)

    @given(message=error_messages, context=context_dicts)
    def test_specific_exception_types_for_specific_errors(self, message, context):
        """
        Property: Different exception types should be distinguishable.

        For any message and context, different exception types should
        create distinct exception instances that can be differentiated.
        """
        config_error = ConfigurationError(message, context=context)
        element_error = ElementError(message, context=context)
        value_error = ValueGenerationError(message, context=context)
        validation_error = ValidationError(message, context=context)
        resource_error = ResourceError(message, context=context)

        # All should have the same message and context
        errors = [
            config_error,
            element_error,
            value_error,
            validation_error,
            resource_error,
        ]
        for error in errors:
            assert error.message == message
            assert error.context == context

        # But they should be different types
        assert type(config_error) is not type(element_error)
        assert type(element_error) is not type(value_error)
        assert type(value_error) is not type(validation_error)
        assert type(validation_error) is not type(resource_error)

        # And should be catchable by their specific types
        assert isinstance(config_error, ConfigurationError)
        assert isinstance(element_error, ElementError)
        assert isinstance(value_error, ValueGenerationError)
        assert isinstance(validation_error, ValidationError)
        assert isinstance(resource_error, ResourceError)
