"""
Configuration management system for the form filling library.

This module provides dataclasses for configuration management and a builder
pattern for fluent configuration setup. It supports multiple configuration
sources and includes validation.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union
from pathlib import Path
import os
import json

from form_filling.constants import (
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
    DEFAULT_MEMORY_LIMIT,
    DEFAULT_CONNECTION_POOL_SIZE,
    DEFAULT_CONNECTION_POOL_TIMEOUT,
    DEFAULT_CACHE_TTL,
    DEFAULT_CACHE_MAX_SIZE,
    DEFAULT_FUZZY_MATCH_THRESHOLD,
    DEFAULT_ELEMENT_TIMEOUT,
    MIN_FUZZY_MATCH_THRESHOLD,
    MAX_FUZZY_MATCH_THRESHOLD,
    MIN_RETRY_ATTEMPTS,
    MAX_RETRY_ATTEMPTS,
    LogLevel,
    LogFormat,
)
from form_filling.exceptions import ConfigurationError


@dataclass
class LoggingConfig:
    """
    Configuration for the logging system.

    Attributes:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log output format (structured, json, plain)
        output_file: Optional path to log file
        max_file_size: Maximum log file size in bytes before rotation
        backup_count: Number of backup log files to keep
    """

    level: str = DEFAULT_LOG_LEVEL
    format: str = DEFAULT_LOG_FORMAT
    output_file: Optional[Path] = None
    max_file_size: int = DEFAULT_LOG_MAX_FILE_SIZE
    backup_count: int = DEFAULT_LOG_BACKUP_COUNT

    def validate(self) -> None:
        """
        Validate logging configuration values.

        Raises:
            ConfigurationError: If configuration values are invalid
        """
        # Validate log level
        valid_levels = [level.value for level in LogLevel]
        if self.level not in valid_levels:
            raise ConfigurationError(
                f"Invalid log level: {self.level}",
                context={
                    "config_key": "level",
                    "config_value": self.level,
                    "allowed_values": valid_levels,
                },
            )

        # Validate log format
        valid_formats = [fmt.value for fmt in LogFormat]
        if self.format not in valid_formats:
            raise ConfigurationError(
                f"Invalid log format: {self.format}",
                context={
                    "config_key": "format",
                    "config_value": self.format,
                    "allowed_values": valid_formats,
                },
            )

        # Validate max_file_size
        if self.max_file_size <= 0:
            raise ConfigurationError(
                f"max_file_size must be positive, got {self.max_file_size}",
                context={
                    "config_key": "max_file_size",
                    "config_value": self.max_file_size,
                },
            )

        # Validate backup_count
        if self.backup_count < 0:
            raise ConfigurationError(
                f"backup_count must be non-negative, got {self.backup_count}",
                context={
                    "config_key": "backup_count",
                    "config_value": self.backup_count,
                },
            )


@dataclass
class LLMConfig:
    """
    Configuration for LLM (Large Language Model) integration.

    Attributes:
        provider: LLM provider name (e.g., "ollama", "openai")
        model: Model name to use
        temperature: Sampling temperature (0.0 to 1.0)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_base_delay: Base delay between retries in seconds
        retry_max_delay: Maximum delay between retries in seconds
        retry_exponential_base: Exponential backoff base multiplier
    """

    provider: str = DEFAULT_LLM_PROVIDER
    model: str = DEFAULT_LLM_MODEL
    temperature: float = DEFAULT_LLM_TEMPERATURE
    timeout: int = DEFAULT_LLM_TIMEOUT
    max_retries: int = DEFAULT_LLM_MAX_RETRIES
    retry_base_delay: float = DEFAULT_LLM_RETRY_BASE_DELAY
    retry_max_delay: float = DEFAULT_LLM_RETRY_MAX_DELAY
    retry_exponential_base: float = DEFAULT_LLM_RETRY_EXPONENTIAL_BASE

    def validate(self) -> None:
        """
        Validate LLM configuration values.

        Raises:
            ConfigurationError: If configuration values are invalid
        """
        # Validate provider
        if not self.provider or not isinstance(self.provider, str):
            raise ConfigurationError(
                f"Invalid LLM provider: {self.provider}",
                context={
                    "config_key": "provider",
                    "config_value": self.provider,
                    "expected_type": "str",
                },
            )

        # Validate model
        if not self.model or not isinstance(self.model, str):
            raise ConfigurationError(
                f"Invalid LLM model: {self.model}",
                context={
                    "config_key": "model",
                    "config_value": self.model,
                    "expected_type": "str",
                },
            )

        # Validate temperature
        if not (0.0 <= self.temperature <= 1.0):
            raise ConfigurationError(
                f"temperature must be between 0.0 and 1.0, got {self.temperature}",
                context={"config_key": "temperature", "config_value": self.temperature},
            )

        # Validate timeout
        if self.timeout <= 0:
            raise ConfigurationError(
                f"timeout must be positive, got {self.timeout}",
                context={"config_key": "timeout", "config_value": self.timeout},
            )

        # Validate max_retries
        if not (MIN_RETRY_ATTEMPTS <= self.max_retries <= MAX_RETRY_ATTEMPTS):
            raise ConfigurationError(
                f"max_retries must be between {MIN_RETRY_ATTEMPTS} and {MAX_RETRY_ATTEMPTS}, got {self.max_retries}",
                context={"config_key": "max_retries", "config_value": self.max_retries},
            )

        # Validate retry delays
        if self.retry_base_delay <= 0:
            raise ConfigurationError(
                f"retry_base_delay must be positive, got {self.retry_base_delay}",
                context={
                    "config_key": "retry_base_delay",
                    "config_value": self.retry_base_delay,
                },
            )

        if self.retry_max_delay <= 0:
            raise ConfigurationError(
                f"retry_max_delay must be positive, got {self.retry_max_delay}",
                context={
                    "config_key": "retry_max_delay",
                    "config_value": self.retry_max_delay,
                },
            )

        if self.retry_max_delay < self.retry_base_delay:
            raise ConfigurationError(
                "retry_max_delay must be >= retry_base_delay",
                context={
                    "config_key": "retry_max_delay",
                    "config_value": self.retry_max_delay,
                    "retry_base_delay": self.retry_base_delay,
                },
            )

        if self.retry_exponential_base <= 1.0:
            raise ConfigurationError(
                f"retry_exponential_base must be > 1.0, got {self.retry_exponential_base}",
                context={
                    "config_key": "retry_exponential_base",
                    "config_value": self.retry_exponential_base,
                },
            )


@dataclass
class PerformanceConfig:
    """
    Configuration for performance and resource management.

    Attributes:
        memory_limit: Maximum memory usage in bytes
        connection_pool_size: Size of connection pool for LLM API calls
        connection_pool_timeout: Timeout for acquiring connection from pool
        cache_ttl: Time-to-live for cached data in seconds
        cache_max_size: Maximum number of entries in cache
    """

    memory_limit: int = DEFAULT_MEMORY_LIMIT
    connection_pool_size: int = DEFAULT_CONNECTION_POOL_SIZE
    connection_pool_timeout: int = DEFAULT_CONNECTION_POOL_TIMEOUT
    cache_ttl: int = DEFAULT_CACHE_TTL
    cache_max_size: int = DEFAULT_CACHE_MAX_SIZE

    def validate(self) -> None:
        """
        Validate performance configuration values.

        Raises:
            ConfigurationError: If configuration values are invalid
        """
        # Validate memory_limit
        if self.memory_limit <= 0:
            raise ConfigurationError(
                f"memory_limit must be positive, got {self.memory_limit}",
                context={
                    "config_key": "memory_limit",
                    "config_value": self.memory_limit,
                },
            )

        # Validate connection_pool_size
        if self.connection_pool_size <= 0:
            raise ConfigurationError(
                f"connection_pool_size must be positive, got {self.connection_pool_size}",
                context={
                    "config_key": "connection_pool_size",
                    "config_value": self.connection_pool_size,
                },
            )

        # Validate connection_pool_timeout
        if self.connection_pool_timeout <= 0:
            raise ConfigurationError(
                f"connection_pool_timeout must be positive, got {self.connection_pool_timeout}",
                context={
                    "config_key": "connection_pool_timeout",
                    "config_value": self.connection_pool_timeout,
                },
            )

        # Validate cache_ttl
        if self.cache_ttl <= 0:
            raise ConfigurationError(
                f"cache_ttl must be positive, got {self.cache_ttl}",
                context={"config_key": "cache_ttl", "config_value": self.cache_ttl},
            )

        # Validate cache_max_size
        if self.cache_max_size <= 0:
            raise ConfigurationError(
                f"cache_max_size must be positive, got {self.cache_max_size}",
                context={
                    "config_key": "cache_max_size",
                    "config_value": self.cache_max_size,
                },
            )


@dataclass
class Configuration:
    """
    Main configuration container for the form filling system.

    This class aggregates all configuration sections and provides
    validation for the entire configuration.

    Attributes:
        llm: LLM configuration
        logging: Logging configuration
        performance: Performance configuration
        resume_path: Optional path to resume file
        resume_content: Optional resume content as string
        fuzzy_match_threshold: Threshold for fuzzy matching (0-100)
        element_timeout: Timeout for element operations in milliseconds
        custom_handlers: Dictionary of custom element handlers
    """

    llm: LLMConfig = field(default_factory=LLMConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    resume_path: Optional[Path] = None
    resume_content: Optional[str] = None
    fuzzy_match_threshold: int = DEFAULT_FUZZY_MATCH_THRESHOLD
    element_timeout: int = DEFAULT_ELEMENT_TIMEOUT
    custom_handlers: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """
        Validate the entire configuration.

        This method validates all configuration sections and cross-section
        constraints.

        Raises:
            ConfigurationError: If any configuration value is invalid
        """
        # Validate sub-configurations
        self.llm.validate()
        self.logging.validate()
        self.performance.validate()

        # Validate fuzzy_match_threshold
        if not (
            MIN_FUZZY_MATCH_THRESHOLD
            <= self.fuzzy_match_threshold
            <= MAX_FUZZY_MATCH_THRESHOLD
        ):
            raise ConfigurationError(
                f"fuzzy_match_threshold must be between {MIN_FUZZY_MATCH_THRESHOLD} and {MAX_FUZZY_MATCH_THRESHOLD}, got {self.fuzzy_match_threshold}",
                context={
                    "config_key": "fuzzy_match_threshold",
                    "config_value": self.fuzzy_match_threshold,
                },
            )

        # Validate element_timeout
        if self.element_timeout <= 0:
            raise ConfigurationError(
                f"element_timeout must be positive, got {self.element_timeout}",
                context={
                    "config_key": "element_timeout",
                    "config_value": self.element_timeout,
                },
            )

        # Validate resume configuration
        if self.resume_path is not None and self.resume_content is not None:
            raise ConfigurationError(
                "Cannot specify both resume_path and resume_content",
                context={
                    "config_key": "resume",
                    "resume_path": str(self.resume_path),
                    "resume_content_length": len(self.resume_content),
                },
            )


class ConfigurationBuilder:
    """
    Builder class for fluent configuration setup.

    This class provides a fluent interface for constructing Configuration
    objects with validation and support for multiple configuration sources.

    Example:
        config = (ConfigurationBuilder()
                 .with_llm_provider("openai")
                 .with_llm_model("gpt-4")
                 .with_log_level("DEBUG")
                 .build())
    """

    def __init__(self):
        """Initialize the configuration builder with default values."""
        self._llm_config = LLMConfig()
        self._logging_config = LoggingConfig()
        self._performance_config = PerformanceConfig()
        self._resume_path: Optional[Path] = None
        self._resume_content: Optional[str] = None
        self._fuzzy_match_threshold: int = DEFAULT_FUZZY_MATCH_THRESHOLD
        self._element_timeout: int = DEFAULT_ELEMENT_TIMEOUT
        self._custom_handlers: Dict[str, Any] = {}

    # LLM configuration methods
    def with_llm_provider(self, provider: str) -> "ConfigurationBuilder":
        """Set the LLM provider."""
        self._llm_config.provider = provider
        return self

    def with_llm_model(self, model: str) -> "ConfigurationBuilder":
        """Set the LLM model."""
        self._llm_config.model = model
        return self

    def with_llm_temperature(self, temperature: float) -> "ConfigurationBuilder":
        """Set the LLM temperature."""
        self._llm_config.temperature = temperature
        return self

    def with_llm_timeout(self, timeout: int) -> "ConfigurationBuilder":
        """Set the LLM timeout."""
        self._llm_config.timeout = timeout
        return self

    def with_llm_max_retries(self, max_retries: int) -> "ConfigurationBuilder":
        """Set the maximum number of LLM retries."""
        self._llm_config.max_retries = max_retries
        return self

    def with_llm(self, llm: Any) -> "ConfigurationBuilder":
        """
        Set LLM configuration from an LLM object.

        This method provides backward compatibility with the original API.
        """
        if llm is not None:
            # Extract configuration from LLM object if possible
            if hasattr(llm, "model"):
                self._llm_config.model = llm.model
            if hasattr(llm, "provider"):
                self._llm_config.provider = llm.provider
        return self

    # Logging configuration methods
    def with_log_level(self, level: str) -> "ConfigurationBuilder":
        """Set the log level."""
        self._logging_config.level = level
        return self

    def with_log_format(self, format: str) -> "ConfigurationBuilder":
        """Set the log format."""
        self._logging_config.format = format
        return self

    def with_log_file(self, output_file: Union[str, Path]) -> "ConfigurationBuilder":
        """Set the log output file."""
        self._logging_config.output_file = Path(output_file) if output_file else None
        return self

    def with_log_max_file_size(self, max_file_size: int) -> "ConfigurationBuilder":
        """Set the maximum log file size."""
        self._logging_config.max_file_size = max_file_size
        return self

    def with_log_backup_count(self, backup_count: int) -> "ConfigurationBuilder":
        """Set the number of log backup files."""
        self._logging_config.backup_count = backup_count
        return self

    # Performance configuration methods
    def with_memory_limit(self, memory_limit: int) -> "ConfigurationBuilder":
        """Set the memory limit."""
        self._performance_config.memory_limit = memory_limit
        return self

    def with_connection_pool_size(self, pool_size: int) -> "ConfigurationBuilder":
        """Set the connection pool size."""
        self._performance_config.connection_pool_size = pool_size
        return self

    def with_cache_ttl(self, cache_ttl: int) -> "ConfigurationBuilder":
        """Set the cache TTL."""
        self._performance_config.cache_ttl = cache_ttl
        return self

    # Resume configuration methods
    def with_resume_path(self, resume_path: Union[str, Path]) -> "ConfigurationBuilder":
        """Set the resume file path."""
        self._resume_path = Path(resume_path) if resume_path else None
        return self

    def with_resume_content(self, resume_content: str) -> "ConfigurationBuilder":
        """Set the resume content directly."""
        self._resume_content = resume_content
        return self

    def with_resume(self, resume: Any) -> "ConfigurationBuilder":
        """
        Set resume configuration from a resume object or path.

        This method provides backward compatibility with the original API.
        """
        if resume is not None:
            if isinstance(resume, (str, Path)):
                self._resume_path = Path(resume)
            else:
                # Assume it's resume content
                self._resume_content = str(resume)
        return self

    # Other configuration methods
    def with_fuzzy_match_threshold(self, threshold: int) -> "ConfigurationBuilder":
        """Set the fuzzy match threshold."""
        self._fuzzy_match_threshold = threshold
        return self

    def with_element_timeout(self, timeout: int) -> "ConfigurationBuilder":
        """Set the element timeout."""
        self._element_timeout = timeout
        return self

    def with_custom_handler(
        self, element_type: str, handler: Any
    ) -> "ConfigurationBuilder":
        """Add a custom element handler."""
        self._custom_handlers[element_type] = handler
        return self

    # Configuration loading methods
    def from_dict(self, config_dict: Dict[str, Any]) -> "ConfigurationBuilder":
        """
        Load configuration from a dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Self for method chaining
        """
        # Load LLM configuration
        if "llm" in config_dict:
            llm_config = config_dict["llm"]
            if "provider" in llm_config:
                self.with_llm_provider(llm_config["provider"])
            if "model" in llm_config:
                self.with_llm_model(llm_config["model"])
            if "temperature" in llm_config:
                self.with_llm_temperature(llm_config["temperature"])
            if "timeout" in llm_config:
                self.with_llm_timeout(llm_config["timeout"])
            if "max_retries" in llm_config:
                self.with_llm_max_retries(llm_config["max_retries"])

        # Load logging configuration
        if "logging" in config_dict:
            logging_config = config_dict["logging"]
            if "level" in logging_config:
                self.with_log_level(logging_config["level"])
            if "format" in logging_config:
                self.with_log_format(logging_config["format"])
            if "output_file" in logging_config:
                self.with_log_file(logging_config["output_file"])
            if "max_file_size" in logging_config:
                self.with_log_max_file_size(logging_config["max_file_size"])
            if "backup_count" in logging_config:
                self.with_log_backup_count(logging_config["backup_count"])

        # Load performance configuration
        if "performance" in config_dict:
            perf_config = config_dict["performance"]
            if "memory_limit" in perf_config:
                self.with_memory_limit(perf_config["memory_limit"])
            if "connection_pool_size" in perf_config:
                self.with_connection_pool_size(perf_config["connection_pool_size"])
            if "cache_ttl" in perf_config:
                self.with_cache_ttl(perf_config["cache_ttl"])

        # Load other configuration
        if "resume_path" in config_dict:
            self.with_resume_path(config_dict["resume_path"])
        if "resume_content" in config_dict:
            self.with_resume_content(config_dict["resume_content"])
        if "fuzzy_match_threshold" in config_dict:
            self.with_fuzzy_match_threshold(config_dict["fuzzy_match_threshold"])
        if "element_timeout" in config_dict:
            self.with_element_timeout(config_dict["element_timeout"])

        return self

    def from_file(self, file_path: Union[str, Path]) -> "ConfigurationBuilder":
        """
        Load configuration from a JSON file.

        Args:
            file_path: Path to the configuration file

        Returns:
            Self for method chaining

        Raises:
            ConfigurationError: If file cannot be read or parsed
        """
        try:
            path = Path(file_path)
            with open(path, "r") as f:
                config_dict = json.load(f)
            return self.from_dict(config_dict)
        except FileNotFoundError:
            raise ConfigurationError(
                f"Configuration file not found: {file_path}",
                context={"file_path": str(file_path)},
            )
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {file_path}",
                context={"file_path": str(file_path), "error": str(e)},
            )
        except Exception as e:
            raise ConfigurationError(
                f"Error reading configuration file: {file_path}",
                context={"file_path": str(file_path), "error": str(e)},
            )

    def from_env(self, prefix: str = "FORM_FILLING_") -> "ConfigurationBuilder":
        """
        Load configuration from environment variables.

        Environment variables should be prefixed (default: FORM_FILLING_)
        and use uppercase with underscores, e.g.:
        - FORM_FILLING_LLM_PROVIDER
        - FORM_FILLING_LOG_LEVEL

        Args:
            prefix: Prefix for environment variables

        Returns:
            Self for method chaining
        """
        # LLM configuration
        if f"{prefix}LLM_PROVIDER" in os.environ:
            self.with_llm_provider(os.environ[f"{prefix}LLM_PROVIDER"])
        if f"{prefix}LLM_MODEL" in os.environ:
            self.with_llm_model(os.environ[f"{prefix}LLM_MODEL"])
        if f"{prefix}LLM_TEMPERATURE" in os.environ:
            self.with_llm_temperature(float(os.environ[f"{prefix}LLM_TEMPERATURE"]))
        if f"{prefix}LLM_TIMEOUT" in os.environ:
            self.with_llm_timeout(int(os.environ[f"{prefix}LLM_TIMEOUT"]))
        if f"{prefix}LLM_MAX_RETRIES" in os.environ:
            self.with_llm_max_retries(int(os.environ[f"{prefix}LLM_MAX_RETRIES"]))

        # Logging configuration
        if f"{prefix}LOG_LEVEL" in os.environ:
            self.with_log_level(os.environ[f"{prefix}LOG_LEVEL"])
        if f"{prefix}LOG_FORMAT" in os.environ:
            self.with_log_format(os.environ[f"{prefix}LOG_FORMAT"])
        if f"{prefix}LOG_FILE" in os.environ:
            self.with_log_file(os.environ[f"{prefix}LOG_FILE"])

        # Performance configuration
        if f"{prefix}MEMORY_LIMIT" in os.environ:
            self.with_memory_limit(int(os.environ[f"{prefix}MEMORY_LIMIT"]))
        if f"{prefix}CONNECTION_POOL_SIZE" in os.environ:
            self.with_connection_pool_size(
                int(os.environ[f"{prefix}CONNECTION_POOL_SIZE"])
            )

        # Other configuration
        if f"{prefix}RESUME_PATH" in os.environ:
            self.with_resume_path(os.environ[f"{prefix}RESUME_PATH"])
        if f"{prefix}FUZZY_MATCH_THRESHOLD" in os.environ:
            self.with_fuzzy_match_threshold(
                int(os.environ[f"{prefix}FUZZY_MATCH_THRESHOLD"])
            )
        if f"{prefix}ELEMENT_TIMEOUT" in os.environ:
            self.with_element_timeout(int(os.environ[f"{prefix}ELEMENT_TIMEOUT"]))

        return self

    def build(self) -> Configuration:
        """
        Build and validate the configuration.

        Returns:
            A validated Configuration object

        Raises:
            ConfigurationError: If configuration is invalid
        """
        config = Configuration(
            llm=self._llm_config,
            logging=self._logging_config,
            performance=self._performance_config,
            resume_path=self._resume_path,
            resume_content=self._resume_content,
            fuzzy_match_threshold=self._fuzzy_match_threshold,
            element_timeout=self._element_timeout,
            custom_handlers=self._custom_handlers.copy(),
        )

        # Validate the configuration
        config.validate()

        return config
