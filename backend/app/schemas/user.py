"""
Pydantic schemas for user-related requests and responses.

Defines data validation and serialization for user endpoints.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Bisnow newsletter categories (available options)
BISNOW_CATEGORIES = [
    "Houston Morning Brief",
    "Austin/San Antonio Morning Brief",
    "National Deal Brief",
    "Capital Markets/Finance",
    "Multifamily",
    "Retail",
    "Investment",
    "Student Housing Brief",
    "The Texas Tea",
    "What Tenants Want",
]


# Base schemas
class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["user@example.com"]
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name",
        examples=["John Doe"]
    )


# Request schemas
class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 chars, must contain letter and digit)",
        examples=["SecurePass123"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123",
                "full_name": "John Doe"
            }
        }
    )


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr = Field(
        ...,
        description="User's email address"
    )
    password: str = Field(
        ...,
        description="User's password"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    )


class UserUpdate(BaseModel):
    """Schema for updating user information."""

    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="New full name"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=128,
        description="New password"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Jane Doe",
                "email": "newemail@example.com"
            }
        }
    )


# Response schemas
class UserResponse(UserBase):
    """Schema for user response (without sensitive data)."""

    id: int = Field(..., description="User's unique identifier")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_superuser: bool = Field(..., description="Whether the user has admin privileges")
    created_at: datetime = Field(..., description="When the user was created")
    updated_at: datetime = Field(..., description="When the user was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)."""

    hashed_password: str = Field(..., description="Bcrypt hashed password")


# Token schemas
class Token(BaseModel):
    """Schema for JWT token response."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


class TokenData(BaseModel):
    """Schema for token payload data."""

    email: Optional[str] = None
    user_id: Optional[int] = None
    exp: Optional[datetime] = None


class LoginResponse(BaseModel):
    """Schema for login response."""

    user: UserResponse = Field(..., description="User information")
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                },
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }
    )


# Newsletter preferences schemas
class NewsletterPreferences(BaseModel):
    """Schema for newsletter preferences."""

    bisnow_categories: List[str] = Field(
        default_factory=list,
        description="List of Bisnow newsletter categories the user is subscribed to"
    )
    fetch_enabled: bool = Field(
        default=False,
        description="Whether automatic newsletter fetching is enabled"
    )
    last_fetch: Optional[datetime] = Field(
        None,
        description="Timestamp of last newsletter fetch"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bisnow_categories": ["Houston Morning Brief", "National Deal Brief"],
                "fetch_enabled": True,
                "last_fetch": "2024-01-15T10:30:00Z"
            }
        }
    )


class UserEmailConfigUpdate(BaseModel):
    """Schema for updating user email configuration."""

    email_address: Optional[str] = Field(
        None,
        description="Email address for newsletter fetching (e.g., Gmail address)"
    )
    email_app_password: Optional[str] = Field(
        None,
        description="Email app password for IMAP access (will be encrypted)"
    )
    imap_server: str = Field(
        default="imap.gmail.com",
        description="IMAP server address"
    )
    imap_port: int = Field(
        default=993,
        ge=1,
        le=65535,
        description="IMAP server port"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email_address": "user@gmail.com",
                "email_app_password": "app-specific-password",
                "imap_server": "imap.gmail.com",
                "imap_port": 993
            }
        }
    )


class UserEmailConfigResponse(BaseModel):
    """Schema for email configuration response (password masked)."""

    email_address: Optional[str] = Field(None, description="Email address")
    imap_server: str = Field(..., description="IMAP server")
    imap_port: int = Field(..., description="IMAP port")
    is_configured: bool = Field(..., description="Whether email is configured")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email_address": "user@gmail.com",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "is_configured": True
            }
        }
    )


class UserNewsletterPreferencesUpdate(BaseModel):
    """Schema for updating newsletter preferences."""

    bisnow_categories: List[str] = Field(
        ...,
        description="List of Bisnow newsletter categories to subscribe to"
    )
    fetch_enabled: bool = Field(
        default=True,
        description="Enable automatic newsletter fetching"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "bisnow_categories": ["Houston Morning Brief", "National Deal Brief"],
                "fetch_enabled": True
            }
        }
    )


class NewsletterCategoriesResponse(BaseModel):
    """Schema for available newsletter categories response."""

    categories: List[str] = Field(..., description="List of available newsletter categories")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "categories": BISNOW_CATEGORIES
            }
        }
    )
