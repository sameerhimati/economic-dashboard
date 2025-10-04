"""
Pydantic schemas package.

Exports all schemas for easy importing.
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    UserResponse,
    UserInDB,
    Token,
    TokenData,
    LoginResponse,
)
from app.schemas.data import (
    DataPointBase,
    DataPointCreate,
    DataPointResponse,
    DataPointListResponse,
    SeriesMetadataBase,
    SeriesMetadataResponse,
    FREDSeriesRequest,
    FREDSeriesResponse,
    ErrorResponse,
)

__all__ = [
    # User schemas
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserResponse",
    "UserInDB",
    "Token",
    "TokenData",
    "LoginResponse",
    # Data schemas
    "DataPointBase",
    "DataPointCreate",
    "DataPointResponse",
    "DataPointListResponse",
    "SeriesMetadataBase",
    "SeriesMetadataResponse",
    "FREDSeriesRequest",
    "FREDSeriesResponse",
    "ErrorResponse",
]
