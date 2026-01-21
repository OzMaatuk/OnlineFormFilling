"""
Centralized constants for the form filling system.
All magic numbers and configuration defaults are defined here.
"""

from enum import Enum
from typing import Final


# Logging Constants
class LogLevel(str, Enum):
    """Enumeration of logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Enumeration of log output formats."""

    STRUCTURED = "structured"
    JSON = "json"
    PLAIN = "plain"


DEFAULT_LOG_LEVEL: Final[str] = LogLevel.INFO
DEFAULT_LOG_FORMAT: Final[str] = LogFormat.STRUCTURED
DEFAULT_LOG_MAX_FILE_SIZE: Final[int] = 10_000_000  # 10MB
DEFAULT_LOG_BACKUP_COUNT: Final[int] = 5


# LLM Constants
DEFAULT_LLM_PROVIDER: Final[str] = "ollama"
DEFAULT_LLM_MODEL: Final[str] = "mistral"
DEFAULT_LLM_TEMPERATURE: Final[float] = 0.0
DEFAULT_LLM_TIMEOUT: Final[int] = 30  # seconds
DEFAULT_LLM_MAX_RETRIES: Final[int] = 3
DEFAULT_LLM_RETRY_BASE_DELAY: Final[float] = 1.0  # seconds
DEFAULT_LLM_RETRY_MAX_DELAY: Final[float] = 60.0  # seconds
DEFAULT_LLM_RETRY_EXPONENTIAL_BASE: Final[float] = 2.0


# Form Filling Constants
DEFAULT_FUZZY_MATCH_THRESHOLD: Final[int] = 80  # percentage
DEFAULT_ELEMENT_TIMEOUT: Final[int] = 5000  # milliseconds
DEFAULT_PAGE_LOAD_TIMEOUT: Final[int] = 30000  # milliseconds
MAX_FIELD_NAME_LENGTH: Final[int] = 100  # characters
MAX_RESUME_SIZE: Final[int] = 10_000_000  # 10MB


# Element Type Constants
class ElementType(str, Enum):
    """Enumeration of supported form element types."""

    TEXT = "text"
    EMAIL = "email"
    TEL = "tel"
    URL = "url"
    SEARCH = "search"
    PASSWORD = "password"
    TEXTAREA = "textarea"
    SELECT = "select"
    SELECT_ONE = "select-one"
    RADIO = "radio"
    RADIOGROUP = "radiogroup"
    CHECKBOX = "checkbox"
    CHECKBOX_CONTAINER = "checkbox-container"
    FIELDSET = "fieldset"
    CLICKABLE = "clickable"
    FILE = "file"


# Attribute Names for Field Detection
FIELD_DETECTION_ATTRIBUTES: Final[tuple] = (
    "name",
    "id",
    "aria-label",
    "data-testid",
    "placeholder",
)


# Cache Constants
DEFAULT_CACHE_TTL: Final[int] = 3600  # seconds (1 hour)
DEFAULT_CACHE_MAX_SIZE: Final[int] = 1000  # entries


# Performance Constants
DEFAULT_MEMORY_LIMIT: Final[int] = 500_000_000  # 500MB
DEFAULT_CONNECTION_POOL_SIZE: Final[int] = 10
DEFAULT_CONNECTION_POOL_TIMEOUT: Final[int] = 30  # seconds


# Validation Constants
MIN_FUZZY_MATCH_THRESHOLD: Final[int] = 0
MAX_FUZZY_MATCH_THRESHOLD: Final[int] = 100
MIN_RETRY_ATTEMPTS: Final[int] = 0
MAX_RETRY_ATTEMPTS: Final[int] = 10
