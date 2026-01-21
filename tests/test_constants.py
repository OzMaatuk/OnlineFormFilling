"""
Unit tests for the constants module.
Tests that all constants are properly defined and accessible.
"""

from form_filling.constants import (
    # Enums
    LogLevel,
    LogFormat,
    ElementType,
    # Logging constants
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_MAX_FILE_SIZE,
    DEFAULT_LOG_BACKUP_COUNT,
    # LLM constants
    DEFAULT_LLM_PROVIDER,
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_LLM_MAX_RETRIES,
    DEFAULT_LLM_RETRY_BASE_DELAY,
    DEFAULT_LLM_RETRY_MAX_DELAY,
    DEFAULT_LLM_RETRY_EXPONENTIAL_BASE,
    # Form filling constants
    DEFAULT_FUZZY_MATCH_THRESHOLD,
    DEFAULT_ELEMENT_TIMEOUT,
    DEFAULT_PAGE_LOAD_TIMEOUT,
    MAX_FIELD_NAME_LENGTH,
    MAX_RESUME_SIZE,
    # Field detection
    FIELD_DETECTION_ATTRIBUTES,
    # Cache constants
    DEFAULT_CACHE_TTL,
    DEFAULT_CACHE_MAX_SIZE,
    # Performance constants
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_CONNECTION_POOL_SIZE,
    DEFAULT_CONNECTION_POOL_TIMEOUT,
    # Validation constants
    MIN_FUZZY_MATCH_THRESHOLD,
    MAX_FUZZY_MATCH_THRESHOLD,
    MIN_RETRY_ATTEMPTS,
    MAX_RETRY_ATTEMPTS,
)


class TestEnums:
    """Test enum definitions."""

    def test_log_level_enum_values(self):
        """Test LogLevel enum has correct values."""
        assert LogLevel.DEBUG == "DEBUG"
        assert LogLevel.INFO == "INFO"
        assert LogLevel.WARNING == "WARNING"
        assert LogLevel.ERROR == "ERROR"
        assert LogLevel.CRITICAL == "CRITICAL"

    def test_log_level_enum_members(self):
        """Test LogLevel enum has all expected members."""
        expected_members = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        actual_members = {member.name for member in LogLevel}
        assert actual_members == expected_members

    def test_log_format_enum_values(self):
        """Test LogFormat enum has correct values."""
        assert LogFormat.STRUCTURED == "structured"
        assert LogFormat.JSON == "json"
        assert LogFormat.PLAIN == "plain"

    def test_log_format_enum_members(self):
        """Test LogFormat enum has all expected members."""
        expected_members = {"STRUCTURED", "JSON", "PLAIN"}
        actual_members = {member.name for member in LogFormat}
        assert actual_members == expected_members

    def test_element_type_enum_values(self):
        """Test ElementType enum has correct values."""
        assert ElementType.TEXT == "text"
        assert ElementType.EMAIL == "email"
        assert ElementType.TEL == "tel"
        assert ElementType.URL == "url"
        assert ElementType.SEARCH == "search"
        assert ElementType.PASSWORD == "password"
        assert ElementType.TEXTAREA == "textarea"
        assert ElementType.SELECT == "select"
        assert ElementType.SELECT_ONE == "select-one"
        assert ElementType.RADIO == "radio"
        assert ElementType.RADIOGROUP == "radiogroup"
        assert ElementType.CHECKBOX == "checkbox"
        assert ElementType.CHECKBOX_CONTAINER == "checkbox-container"
        assert ElementType.FIELDSET == "fieldset"
        assert ElementType.CLICKABLE == "clickable"
        assert ElementType.FILE == "file"

    def test_element_type_enum_members(self):
        """Test ElementType enum has all expected members."""
        expected_members = {
            "TEXT",
            "EMAIL",
            "TEL",
            "URL",
            "SEARCH",
            "PASSWORD",
            "TEXTAREA",
            "SELECT",
            "SELECT_ONE",
            "RADIO",
            "RADIOGROUP",
            "CHECKBOX",
            "CHECKBOX_CONTAINER",
            "FIELDSET",
            "CLICKABLE",
            "FILE",
        }
        actual_members = {member.name for member in ElementType}
        assert actual_members == expected_members


class TestLoggingConstants:
    """Test logging-related constants."""

    def test_default_log_level(self):
        """Test default log level is INFO."""
        assert DEFAULT_LOG_LEVEL == LogLevel.INFO

    def test_default_log_format(self):
        """Test default log format is STRUCTURED."""
        assert DEFAULT_LOG_FORMAT == LogFormat.STRUCTURED

    def test_default_log_max_file_size(self):
        """Test default log max file size is 10MB."""
        assert DEFAULT_LOG_MAX_FILE_SIZE == 10_000_000

    def test_default_log_backup_count(self):
        """Test default log backup count is 5."""
        assert DEFAULT_LOG_BACKUP_COUNT == 5


class TestLLMConstants:
    """Test LLM-related constants."""

    def test_default_llm_provider(self):
        """Test default LLM provider is ollama."""
        assert DEFAULT_LLM_PROVIDER == "ollama"

    def test_default_llm_model(self):
        """Test default LLM model is mistral."""
        assert DEFAULT_LLM_MODEL == "mistral"

    def test_default_llm_temperature(self):
        """Test default LLM temperature is 0.0."""
        assert DEFAULT_LLM_TEMPERATURE == 0.0

    def test_default_llm_timeout(self):
        """Test default LLM timeout is 30 seconds."""
        assert DEFAULT_LLM_TIMEOUT == 30

    def test_default_llm_max_retries(self):
        """Test default LLM max retries is 3."""
        assert DEFAULT_LLM_MAX_RETRIES == 3

    def test_default_llm_retry_base_delay(self):
        """Test default LLM retry base delay is 1.0 seconds."""
        assert DEFAULT_LLM_RETRY_BASE_DELAY == 1.0

    def test_default_llm_retry_max_delay(self):
        """Test default LLM retry max delay is 60.0 seconds."""
        assert DEFAULT_LLM_RETRY_MAX_DELAY == 60.0

    def test_default_llm_retry_exponential_base(self):
        """Test default LLM retry exponential base is 2.0."""
        assert DEFAULT_LLM_RETRY_EXPONENTIAL_BASE == 2.0


class TestFormFillingConstants:
    """Test form filling-related constants."""

    def test_default_fuzzy_match_threshold(self):
        """Test default fuzzy match threshold is 80."""
        assert DEFAULT_FUZZY_MATCH_THRESHOLD == 80

    def test_default_element_timeout(self):
        """Test default element timeout is 5000ms."""
        assert DEFAULT_ELEMENT_TIMEOUT == 5000

    def test_default_page_load_timeout(self):
        """Test default page load timeout is 30000ms."""
        assert DEFAULT_PAGE_LOAD_TIMEOUT == 30000

    def test_max_field_name_length(self):
        """Test max field name length is 100 characters."""
        assert MAX_FIELD_NAME_LENGTH == 100

    def test_max_resume_size(self):
        """Test max resume size is 10MB."""
        assert MAX_RESUME_SIZE == 10_000_000


class TestFieldDetectionConstants:
    """Test field detection-related constants."""

    def test_field_detection_attributes(self):
        """Test field detection attributes tuple."""
        expected = ("name", "id", "aria-label", "data-testid", "placeholder")
        assert FIELD_DETECTION_ATTRIBUTES == expected

    def test_field_detection_attributes_is_tuple(self):
        """Test field detection attributes is a tuple."""
        assert isinstance(FIELD_DETECTION_ATTRIBUTES, tuple)


class TestCacheConstants:
    """Test cache-related constants."""

    def test_default_cache_ttl(self):
        """Test default cache TTL is 3600 seconds."""
        assert DEFAULT_CACHE_TTL == 3600

    def test_default_cache_max_size(self):
        """Test default cache max size is 1000 entries."""
        assert DEFAULT_CACHE_MAX_SIZE == 1000


class TestPerformanceConstants:
    """Test performance-related constants."""

    def test_default_memory_limit(self):
        """Test default memory limit is 500MB."""
        assert DEFAULT_MEMORY_LIMIT == 500_000_000

    def test_default_connection_pool_size(self):
        """Test default connection pool size is 10."""
        assert DEFAULT_CONNECTION_POOL_SIZE == 10

    def test_default_connection_pool_timeout(self):
        """Test default connection pool timeout is 30 seconds."""
        assert DEFAULT_CONNECTION_POOL_TIMEOUT == 30


class TestValidationConstants:
    """Test validation-related constants."""

    def test_min_fuzzy_match_threshold(self):
        """Test min fuzzy match threshold is 0."""
        assert MIN_FUZZY_MATCH_THRESHOLD == 0

    def test_max_fuzzy_match_threshold(self):
        """Test max fuzzy match threshold is 100."""
        assert MAX_FUZZY_MATCH_THRESHOLD == 100

    def test_min_retry_attempts(self):
        """Test min retry attempts is 0."""
        assert MIN_RETRY_ATTEMPTS == 0

    def test_max_retry_attempts(self):
        """Test max retry attempts is 10."""
        assert MAX_RETRY_ATTEMPTS == 10

    def test_fuzzy_match_threshold_range(self):
        """Test fuzzy match threshold range is valid."""
        assert MIN_FUZZY_MATCH_THRESHOLD < MAX_FUZZY_MATCH_THRESHOLD
        assert MIN_FUZZY_MATCH_THRESHOLD >= 0
        assert MAX_FUZZY_MATCH_THRESHOLD <= 100

    def test_retry_attempts_range(self):
        """Test retry attempts range is valid."""
        assert MIN_RETRY_ATTEMPTS < MAX_RETRY_ATTEMPTS
        assert MIN_RETRY_ATTEMPTS >= 0


class TestConstantsAccessibility:
    """Test that all constants are properly accessible."""

    def test_all_constants_are_importable(self):
        """Test that all constants can be imported without errors."""
        # This test passes if the imports at the top of the file succeed
        assert True

    def test_constants_are_not_none(self):
        """Test that no constant is None."""
        constants = [
            DEFAULT_LOG_LEVEL,
            DEFAULT_LOG_FORMAT,
            DEFAULT_LOG_MAX_FILE_SIZE,
            DEFAULT_LOG_BACKUP_COUNT,
            DEFAULT_LLM_PROVIDER,
            DEFAULT_LLM_MODEL,
            DEFAULT_LLM_TEMPERATURE,
            DEFAULT_LLM_TIMEOUT,
            DEFAULT_LLM_MAX_RETRIES,
            DEFAULT_LLM_RETRY_BASE_DELAY,
            DEFAULT_LLM_RETRY_MAX_DELAY,
            DEFAULT_LLM_RETRY_EXPONENTIAL_BASE,
            DEFAULT_FUZZY_MATCH_THRESHOLD,
            DEFAULT_ELEMENT_TIMEOUT,
            DEFAULT_PAGE_LOAD_TIMEOUT,
            MAX_FIELD_NAME_LENGTH,
            MAX_RESUME_SIZE,
            FIELD_DETECTION_ATTRIBUTES,
            DEFAULT_CACHE_TTL,
            DEFAULT_CACHE_MAX_SIZE,
            DEFAULT_MEMORY_LIMIT,
            DEFAULT_CONNECTION_POOL_SIZE,
            DEFAULT_CONNECTION_POOL_TIMEOUT,
            MIN_FUZZY_MATCH_THRESHOLD,
            MAX_FUZZY_MATCH_THRESHOLD,
            MIN_RETRY_ATTEMPTS,
            MAX_RETRY_ATTEMPTS,
        ]
        for constant in constants:
            assert constant is not None
