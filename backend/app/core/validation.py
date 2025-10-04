"""
Configuration validation utilities.

Validates environment variables and configuration on startup.
"""
import logging
import re
from typing import List, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)


def validate_database_url(url: str) -> Tuple[bool, List[str]]:
    """
    Validate database URL format.

    Args:
        url: Database URL to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check if URL is present
    if not url:
        errors.append("DATABASE_URL is empty")
        return False, errors

    # Check basic format
    if not url.startswith("postgresql"):
        errors.append("DATABASE_URL must start with 'postgresql' or 'postgresql+asyncpg'")
        return False, errors

    # Validate URL structure
    # Format: postgresql[+driver]://user:password@host:port/database
    pattern = r"^postgresql(\+\w+)?://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)$"
    if not re.match(pattern, url):
        errors.append(
            "DATABASE_URL format is invalid. Expected: "
            "postgresql[+driver]://user:password@host:port/database"
        )
        return False, errors

    # Check driver for async operations
    if "+asyncpg" in url:
        logger.info("Using asyncpg driver for async database operations")
    elif "+" in url:
        errors.append(
            f"Unknown database driver in URL. For async operations, use +asyncpg"
        )
        return False, errors
    else:
        logger.warning(
            "No driver specified in DATABASE_URL. "
            "For async operations, use postgresql+asyncpg://"
        )

    return True, errors


def validate_redis_url(url: str) -> Tuple[bool, List[str]]:
    """
    Validate Redis URL format.

    Args:
        url: Redis URL to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Check if URL is present
    if not url:
        errors.append("REDIS_URL is empty")
        return False, errors

    # Check basic format
    if not url.startswith(("redis://", "rediss://")):
        errors.append("REDIS_URL must start with 'redis://' or 'rediss://' for TLS")
        return False, errors

    # Validate URL structure
    # Format: redis[s]://[user:password@]host:port[/db]
    pattern = r"^rediss?://(([^:]+):([^@]+)@)?([^:]+):(\d+)(/\d+)?$"
    if not re.match(pattern, url):
        errors.append(
            "REDIS_URL format is invalid. Expected: "
            "redis://[user:password@]host:port[/db] or "
            "rediss://[user:password@]host:port[/db] for TLS"
        )
        return False, errors

    return True, errors


def validate_secret_key(key: str) -> Tuple[bool, List[str]]:
    """
    Validate secret key strength.

    Args:
        key: Secret key to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not key:
        errors.append("SECRET_KEY is empty")
        return False, errors

    if len(key) < 32:
        errors.append(
            f"SECRET_KEY is too short ({len(key)} characters). "
            "It should be at least 32 characters for security."
        )
        return False, errors

    # Check for weak patterns
    if key.lower() == "your-secret-key-here" or key == "changeme":
        errors.append("SECRET_KEY appears to be a placeholder. Use a strong random string.")
        return False, errors

    return True, errors


def validate_cors_origins(origins: str) -> Tuple[bool, List[str]]:
    """
    Validate CORS origins format.

    Args:
        origins: Comma-separated CORS origins

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    warnings = []

    if not origins:
        warnings.append("CORS_ORIGINS is empty. No origins will be allowed.")
        return True, warnings

    # Parse origins
    origin_list = [o.strip() for o in origins.split(",") if o.strip()]

    if not origin_list:
        warnings.append("CORS_ORIGINS contains no valid origins after parsing.")
        return True, warnings

    # Validate each origin
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    for origin in origin_list:
        if origin == "*":
            warnings.append(
                "CORS_ORIGINS contains '*' (allow all). "
                "This is insecure for production."
            )
            continue

        if not re.match(url_pattern, origin):
            errors.append(f"Invalid CORS origin format: '{origin}'")

    if errors:
        return False, errors

    return True, warnings


def validate_fred_api_key(key: str) -> Tuple[bool, List[str]]:
    """
    Validate FRED API key format.

    Args:
        key: FRED API key to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not key:
        errors.append("FRED_API_KEY is empty")
        return False, errors

    # FRED API keys are typically 32 character alphanumeric strings
    if len(key) != 32:
        errors.append(
            f"FRED_API_KEY has unexpected length ({len(key)} characters). "
            "Expected 32 characters."
        )

    if not re.match(r"^[a-f0-9]{32}$", key):
        errors.append(
            "FRED_API_KEY format appears invalid. "
            "Expected 32 hexadecimal characters."
        )

    return len(errors) == 0, errors


def validate_all_config() -> bool:
    """
    Validate all configuration settings.

    Returns:
        bool: True if all validations pass, False otherwise

    Raises:
        ValueError: If critical configuration is invalid
    """
    logger.info("Validating application configuration...")

    all_valid = True
    all_errors = []
    all_warnings = []

    # Validate DATABASE_URL
    valid, errors = validate_database_url(settings.DATABASE_URL)
    if not valid:
        all_valid = False
        all_errors.extend([f"DATABASE_URL: {e}" for e in errors])
    elif errors:  # Warnings
        all_warnings.extend([f"DATABASE_URL: {e}" for e in errors])

    # Validate REDIS_URL
    valid, errors = validate_redis_url(settings.REDIS_URL)
    if not valid:
        all_valid = False
        all_errors.extend([f"REDIS_URL: {e}" for e in errors])
    elif errors:  # Warnings
        all_warnings.extend([f"REDIS_URL: {e}" for e in errors])

    # Validate SECRET_KEY
    valid, errors = validate_secret_key(settings.SECRET_KEY)
    if not valid:
        all_valid = False
        all_errors.extend([f"SECRET_KEY: {e}" for e in errors])

    # Validate CORS_ORIGINS
    valid, messages = validate_cors_origins(settings.CORS_ORIGINS)
    if not valid:
        all_valid = False
        all_errors.extend([f"CORS_ORIGINS: {e}" for e in messages])
    elif messages:  # Warnings
        all_warnings.extend([f"CORS_ORIGINS: {w}" for w in messages])

    # Validate FRED_API_KEY
    valid, errors = validate_fred_api_key(settings.FRED_API_KEY)
    if not valid:
        # FRED API key validation is a warning, not an error
        all_warnings.extend([f"FRED_API_KEY: {e}" for e in errors])

    # Validate environment-specific settings
    if settings.ENVIRONMENT == "production":
        if settings.DEBUG:
            all_errors.append(
                "ENVIRONMENT: DEBUG is enabled in production. "
                "This is a security risk and must be disabled."
            )
            all_valid = False

        # Strict CORS validation for production
        if "localhost" in settings.CORS_ORIGINS or "127.0.0.1" in settings.CORS_ORIGINS:
            all_errors.append(
                "CORS_ORIGINS: Contains localhost/127.0.0.1 in production environment. "
                "This is a security risk and must be removed."
            )
            all_valid = False

    # Log results
    if all_errors:
        logger.error("Configuration validation failed with errors:")
        for error in all_errors:
            logger.error(f"  - {error}")

    if all_warnings:
        logger.warning("Configuration validation completed with warnings:")
        for warning in all_warnings:
            logger.warning(f"  - {warning}")

    if all_valid and not all_warnings:
        logger.info("Configuration validation passed successfully")

    if not all_valid:
        raise ValueError(
            f"Configuration validation failed with {len(all_errors)} error(s). "
            "Check logs for details."
        )

    return all_valid


def log_startup_info():
    """
    Log startup information about the application configuration.

    This helps with debugging and verifying the environment is set up correctly.
    """
    logger.info("=" * 80)
    logger.info("Application Configuration")
    logger.info("=" * 80)
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info("-" * 80)
    logger.info(f"Server Host: {settings.HOST}")
    logger.info(f"Server Port: {settings.PORT}")
    logger.info("-" * 80)
    logger.info(f"Database URL: {_mask_url(settings.DATABASE_URL)}")
    logger.info(f"Database Pool Size: {settings.DB_POOL_SIZE}")
    logger.info(f"Database Max Overflow: {settings.DB_MAX_OVERFLOW}")
    logger.info(f"Database Echo SQL: {settings.DB_ECHO}")
    logger.info("-" * 80)
    logger.info(f"Redis URL: {_mask_url(settings.REDIS_URL)}")
    logger.info(f"Redis Cache TTL: {settings.REDIS_CACHE_TTL}s")
    logger.info(f"Redis Max Connections: {settings.REDIS_MAX_CONNECTIONS}")
    logger.info("-" * 80)
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"CORS Allow Credentials: {settings.CORS_ALLOW_CREDENTIALS}")
    logger.info("-" * 80)
    logger.info(f"FRED API Base URL: {settings.FRED_API_BASE_URL}")
    logger.info(f"FRED API Timeout: {settings.FRED_API_TIMEOUT}s")
    logger.info(f"FRED Rate Limit: {settings.FRED_RATE_LIMIT_PER_MINUTE}/min")
    logger.info(f"FRED API Key: {'*' * 8}...{settings.FRED_API_KEY[-4:]}")
    logger.info("-" * 80)
    logger.info(f"JWT Algorithm: {settings.ALGORITHM}")
    logger.info(f"Access Token Expire: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    logger.info("=" * 80)


def _mask_url(url: str) -> str:
    """
    Mask sensitive information in URLs for logging.

    Args:
        url: URL to mask

    Returns:
        str: Masked URL with password hidden
    """
    # Pattern: protocol://user:password@host:port/database
    pattern = r"(^[^:]+://[^:]+:)([^@]+)(@.+$)"
    return re.sub(pattern, r"\1********\3", url)
