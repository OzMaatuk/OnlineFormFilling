"""
Property-based tests for configuration validation.

Feature: project-refactoring, Property 11: Configuration Validation
Validates: Requirements 6.2, 6.5

Tests that configuration validation correctly rejects invalid configurations
and accepts valid configurations with descriptive error messages.
"""

import pytest
from hypothesis import given, strategies as st, assume
from pathlib import Path

from form_filling.config import (
    LoggingConfig,
    LLMConfig,
    PerformanceConfig,
    Configuration,
)
from form_filling.exceptions import ConfigurationError
from form_filling.constants import (
    LogLevel,
    LogFormat,
    MIN_FUZZY_MATCH_THRESHOLD,
    MAX_FUZZY_MATCH_THRESHOLD,
    MIN_RETRY_ATTEMPTS,
    MAX_RETRY_ATTEMPTS,
)


# Strategies for valid configuration values
valid_log_levels = st.sampled_from([level.value for level in LogLevel])
valid_log_formats = st.sampled_from([fmt.value for fmt in LogFormat])
valid_positive_ints = st.integers(min_value=1, max_value=1_000_000_000)
valid_non_negative_ints = st.integers(min_value=0, max_value=1_000_000_000)
valid_temperatures = st.floats(
    min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False
)
valid_retry_attempts = st.integers(
    min_value=MIN_RETRY_ATTEMPTS, max_value=MAX_RETRY_ATTEMPTS
)
valid_fuzzy_thresholds = st.integers(
    min_value=MIN_FUZZY_MATCH_THRESHOLD, max_value=MAX_FUZZY_MATCH_THRESHOLD
)
valid_exponential_bases = st.floats(
    min_value=1.1, max_value=10.0, allow_nan=False, allow_infinity=False
)

# Strategies for invalid configuration values
invalid_log_levels = st.text().filter(
    lambda x: x not in [level.value for level in LogLevel]
)
invalid_log_formats = st.text().filter(
    lambda x: x not in [fmt.value for fmt in LogFormat]
)
invalid_positive_ints = st.integers(max_value=0)
invalid_negative_ints = st.integers(max_value=-1)
invalid_temperatures = st.one_of(
    st.floats(min_value=-10.0, max_value=-0.01),
    st.floats(min_value=1.01, max_value=10.0),
).filter(lambda x: not (0.0 <= x <= 1.0))
invalid_retry_attempts = st.one_of(
    st.integers(max_value=MIN_RETRY_ATTEMPTS - 1),
    st.integers(min_value=MAX_RETRY_ATTEMPTS + 1, max_value=1000),
)
invalid_fuzzy_thresholds = st.one_of(
    st.integers(max_value=MIN_FUZZY_MATCH_THRESHOLD - 1),
    st.integers(min_value=MAX_FUZZY_MATCH_THRESHOLD + 1, max_value=1000),
)
invalid_exponential_bases = st.floats(
    max_value=1.0, allow_nan=False, allow_infinity=False
)


class TestConfigurationValidation:
    """
    Property 11: Configuration Validation

    For any configuration input, the system should validate values against
    the schema and reject invalid configurations with descriptive errors.
    """

    @given(level=invalid_log_levels)
    def test_logging_config_rejects_invalid_log_level(self, level):
        """
        Property: Invalid log levels should be rejected.

        For any invalid log level, LoggingConfig validation should raise
        ConfigurationError with appropriate context.
        """
        assume(isinstance(level, str))  # Ensure it's a string
        config = LoggingConfig(level=level)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "log level" in error.message.lower() or "level" in error.message.lower()
        assert "config_key" in error.context
        assert error.context["config_key"] == "level"

    @given(format=invalid_log_formats)
    def test_logging_config_rejects_invalid_log_format(self, format):
        """
        Property: Invalid log formats should be rejected.

        For any invalid log format, LoggingConfig validation should raise
        ConfigurationError with appropriate context.
        """
        assume(isinstance(format, str))  # Ensure it's a string
        config = LoggingConfig(format=format)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "format" in error.message.lower()
        assert "config_key" in error.context
        assert error.context["config_key"] == "format"

    @given(max_file_size=invalid_positive_ints)
    def test_logging_config_rejects_non_positive_max_file_size(self, max_file_size):
        """
        Property: Non-positive max_file_size should be rejected.

        For any non-positive max_file_size value, LoggingConfig validation
        should raise ConfigurationError.
        """
        config = LoggingConfig(max_file_size=max_file_size)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "max_file_size" in error.message.lower()
        assert error.context["config_key"] == "max_file_size"

    @given(backup_count=invalid_negative_ints)
    def test_logging_config_rejects_negative_backup_count(self, backup_count):
        """
        Property: Negative backup_count should be rejected.

        For any negative backup_count value, LoggingConfig validation
        should raise ConfigurationError.
        """
        config = LoggingConfig(backup_count=backup_count)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "backup_count" in error.message.lower()
        assert error.context["config_key"] == "backup_count"

    @given(temperature=invalid_temperatures)
    def test_llm_config_rejects_invalid_temperature(self, temperature):
        """
        Property: Temperature outside [0.0, 1.0] should be rejected.

        For any temperature value outside the valid range, LLMConfig validation
        should raise ConfigurationError.
        """
        config = LLMConfig(temperature=temperature)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "temperature" in error.message.lower()
        assert error.context["config_key"] == "temperature"

    @given(timeout=invalid_positive_ints)
    def test_llm_config_rejects_non_positive_timeout(self, timeout):
        """
        Property: Non-positive timeout should be rejected.

        For any non-positive timeout value, LLMConfig validation should
        raise ConfigurationError.
        """
        config = LLMConfig(timeout=timeout)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "timeout" in error.message.lower()
        assert error.context["config_key"] == "timeout"

    @given(max_retries=invalid_retry_attempts)
    def test_llm_config_rejects_invalid_max_retries(self, max_retries):
        """
        Property: max_retries outside valid range should be rejected.

        For any max_retries value outside the valid range, LLMConfig validation
        should raise ConfigurationError.
        """
        config = LLMConfig(max_retries=max_retries)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert (
            "max_retries" in error.message.lower() or "retry" in error.message.lower()
        )
        assert error.context["config_key"] == "max_retries"

    @given(base_delay=invalid_positive_ints)
    def test_llm_config_rejects_non_positive_retry_base_delay(self, base_delay):
        """
        Property: Non-positive retry_base_delay should be rejected.

        For any non-positive retry_base_delay, LLMConfig validation should
        raise ConfigurationError.
        """
        config = LLMConfig(retry_base_delay=base_delay)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "retry_base_delay" in error.message.lower()
        assert error.context["config_key"] == "retry_base_delay"

    @given(base_delay=valid_positive_ints, max_delay=valid_positive_ints)
    def test_llm_config_rejects_max_delay_less_than_base_delay(
        self, base_delay, max_delay
    ):
        """
        Property: retry_max_delay < retry_base_delay should be rejected.

        For any configuration where max_delay is less than base_delay,
        LLMConfig validation should raise ConfigurationError.
        """
        assume(max_delay < base_delay)
        config = LLMConfig(
            retry_base_delay=float(base_delay), retry_max_delay=float(max_delay)
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "retry_max_delay" in error.message.lower()

    @given(exponential_base=invalid_exponential_bases)
    def test_llm_config_rejects_invalid_exponential_base(self, exponential_base):
        """
        Property: retry_exponential_base <= 1.0 should be rejected.

        For any exponential base <= 1.0, LLMConfig validation should
        raise ConfigurationError.
        """
        config = LLMConfig(retry_exponential_base=exponential_base)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "exponential_base" in error.message.lower()
        assert error.context["config_key"] == "retry_exponential_base"

    @given(memory_limit=invalid_positive_ints)
    def test_performance_config_rejects_non_positive_memory_limit(self, memory_limit):
        """
        Property: Non-positive memory_limit should be rejected.

        For any non-positive memory_limit, PerformanceConfig validation
        should raise ConfigurationError.
        """
        config = PerformanceConfig(memory_limit=memory_limit)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "memory_limit" in error.message.lower()
        assert error.context["config_key"] == "memory_limit"

    @given(pool_size=invalid_positive_ints)
    def test_performance_config_rejects_non_positive_connection_pool_size(
        self, pool_size
    ):
        """
        Property: Non-positive connection_pool_size should be rejected.

        For any non-positive connection_pool_size, PerformanceConfig validation
        should raise ConfigurationError.
        """
        config = PerformanceConfig(connection_pool_size=pool_size)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "connection_pool_size" in error.message.lower()
        assert error.context["config_key"] == "connection_pool_size"

    @given(threshold=invalid_fuzzy_thresholds)
    def test_configuration_rejects_invalid_fuzzy_match_threshold(self, threshold):
        """
        Property: fuzzy_match_threshold outside valid range should be rejected.

        For any fuzzy_match_threshold outside [0, 100], Configuration validation
        should raise ConfigurationError.
        """
        config = Configuration(fuzzy_match_threshold=threshold)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "fuzzy_match_threshold" in error.message.lower()
        assert error.context["config_key"] == "fuzzy_match_threshold"

    @given(timeout=invalid_positive_ints)
    def test_configuration_rejects_non_positive_element_timeout(self, timeout):
        """
        Property: Non-positive element_timeout should be rejected.

        For any non-positive element_timeout, Configuration validation
        should raise ConfigurationError.
        """
        config = Configuration(element_timeout=timeout)

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "element_timeout" in error.message.lower()
        assert error.context["config_key"] == "element_timeout"

    @given(
        level=valid_log_levels,
        format=valid_log_formats,
        max_file_size=valid_positive_ints,
        backup_count=valid_non_negative_ints,
    )
    def test_valid_logging_config_passes_validation(
        self, level, format, max_file_size, backup_count
    ):
        """
        Property: Valid LoggingConfig should pass validation.

        For any valid logging configuration values, validation should succeed
        without raising exceptions.
        """
        config = LoggingConfig(
            level=level,
            format=format,
            max_file_size=max_file_size,
            backup_count=backup_count,
        )

        # Should not raise any exception
        config.validate()

    @given(
        temperature=valid_temperatures,
        timeout=valid_positive_ints,
        max_retries=valid_retry_attempts,
        base_delay=valid_positive_ints,
        exponential_base=valid_exponential_bases,
    )
    def test_valid_llm_config_passes_validation(
        self, temperature, timeout, max_retries, base_delay, exponential_base
    ):
        """
        Property: Valid LLMConfig should pass validation.

        For any valid LLM configuration values, validation should succeed
        without raising exceptions.
        """
        max_delay = base_delay + 100  # Ensure max_delay > base_delay
        config = LLMConfig(
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            retry_base_delay=float(base_delay),
            retry_max_delay=float(max_delay),
            retry_exponential_base=exponential_base,
        )

        # Should not raise any exception
        config.validate()

    @given(
        memory_limit=valid_positive_ints,
        pool_size=valid_positive_ints,
        pool_timeout=valid_positive_ints,
        cache_ttl=valid_positive_ints,
        cache_max_size=valid_positive_ints,
    )
    def test_valid_performance_config_passes_validation(
        self, memory_limit, pool_size, pool_timeout, cache_ttl, cache_max_size
    ):
        """
        Property: Valid PerformanceConfig should pass validation.

        For any valid performance configuration values, validation should
        succeed without raising exceptions.
        """
        config = PerformanceConfig(
            memory_limit=memory_limit,
            connection_pool_size=pool_size,
            connection_pool_timeout=pool_timeout,
            cache_ttl=cache_ttl,
            cache_max_size=cache_max_size,
        )

        # Should not raise any exception
        config.validate()

    @given(threshold=valid_fuzzy_thresholds, timeout=valid_positive_ints)
    def test_valid_configuration_passes_validation(self, threshold, timeout):
        """
        Property: Valid Configuration should pass validation.

        For any valid configuration values, validation should succeed
        without raising exceptions.
        """
        config = Configuration(fuzzy_match_threshold=threshold, element_timeout=timeout)

        # Should not raise any exception
        config.validate()

    def test_configuration_rejects_both_resume_path_and_content(self):
        """
        Property: Configuration with both resume_path and resume_content should be rejected.

        When both resume_path and resume_content are specified, Configuration
        validation should raise ConfigurationError.
        """
        config = Configuration(
            resume_path=Path("/tmp/resume.pdf"), resume_content="Resume content here"
        )

        with pytest.raises(ConfigurationError) as exc_info:
            config.validate()

        error = exc_info.value
        assert "resume" in error.message.lower()
        assert "both" in error.message.lower()

    @given(
        level=valid_log_levels,
        temperature=valid_temperatures,
        threshold=valid_fuzzy_thresholds,
    )
    def test_configuration_validates_all_subconfigs(
        self, level, temperature, threshold
    ):
        """
        Property: Configuration validation should validate all sub-configurations.

        For any configuration, calling validate() should validate all nested
        configuration objects (llm, logging, performance).
        """
        # Create a configuration with valid values
        config = Configuration(
            llm=LLMConfig(temperature=temperature),
            logging=LoggingConfig(level=level),
            fuzzy_match_threshold=threshold,
        )

        # Should not raise any exception
        config.validate()

        # Now create one with an invalid sub-config
        config_invalid = Configuration(
            llm=LLMConfig(temperature=1.5),  # Invalid temperature
            fuzzy_match_threshold=threshold,
        )

        # Should raise ConfigurationError due to invalid LLM config
        with pytest.raises(ConfigurationError):
            config_invalid.validate()
