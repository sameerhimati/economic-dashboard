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
from app.schemas.newsletter import (
    NewsletterBase,
    NewsletterCreate,
    NewsletterUpdate,
    NewsletterResponse,
    NewsletterSummary,
    NewsletterListResponse,
    NewsletterSearchRequest,
    NewsletterSearchResponse,
    NewsletterFetchRequest,
    NewsletterFetchResponse,
    MetricExtract,
    KeyPointsResponse,
    NewsletterStatsResponse,
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
    # Newsletter schemas
    "NewsletterBase",
    "NewsletterCreate",
    "NewsletterUpdate",
    "NewsletterResponse",
    "NewsletterSummary",
    "NewsletterListResponse",
    "NewsletterSearchRequest",
    "NewsletterSearchResponse",
    "NewsletterFetchRequest",
    "NewsletterFetchResponse",
    "MetricExtract",
    "KeyPointsResponse",
    "NewsletterStatsResponse",
]
