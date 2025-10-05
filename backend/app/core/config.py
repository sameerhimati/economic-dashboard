"""
Configuration management using pydantic-settings.

Loads configuration from environment variables with proper validation and type hints.
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All sensitive configuration should be provided via environment variables.
    Use .env file for local development and configure Railway environment for production.
    """

    # Application Settings
    APP_NAME: str = "Economic Dashboard API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="production", description="Environment: development, staging, production")

    # Server Settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Database Settings
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string (async driver): postgresql+asyncpg://user:password@host:port/dbname"
    )
    DB_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DB_MAX_OVERFLOW: int = Field(default=20, description="Maximum number of connections above pool_size")
    DB_ECHO: bool = Field(default=False, description="Log all SQL statements")

    # Redis Settings
    REDIS_URL: str = Field(
        ...,
        description="Redis connection string: redis://host:port/db or rediss://host:port/db for TLS"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, description="Default cache TTL in seconds (1 hour)")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, description="Redis connection pool size")

    # Security Settings
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token generation (use strong random string)"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration in minutes")

    # CORS Settings
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated in env)"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], description="Allowed HTTP methods")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], description="Allowed HTTP headers")

    # FRED API Settings
    FRED_API_KEY: str = Field(..., description="FRED API key from https://fred.stlouisfed.org/")
    FRED_API_BASE_URL: str = Field(
        default="https://api.stlouisfed.org/fred",
        description="FRED API base URL"
    )
    FRED_API_TIMEOUT: int = Field(default=30, description="FRED API request timeout in seconds")
    FRED_RATE_LIMIT_PER_MINUTE: int = Field(default=120, description="FRED API rate limit")

    # Email Settings for Newsletter Parsing (Optional - users configure their own)
    EMAIL_ADDRESS: Optional[str] = Field(default=None, description="Email address for IMAP connection (deprecated - users configure their own)")
    EMAIL_APP_PASSWORD: Optional[str] = Field(default=None, description="Email app-specific password for IMAP (deprecated - users configure their own)")
    IMAP_SERVER: str = Field(default="imap.gmail.com", description="Default IMAP server address")
    IMAP_PORT: int = Field(default=993, description="Default IMAP server port (SSL)")

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"ENVIRONMENT must be one of {valid_environments}")
        return v

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"LOG_LEVEL must be one of {valid_levels}")
        return v_upper

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra environment variables
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()
