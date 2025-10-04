"""
Pydantic schemas for FRED data-related requests and responses.

Defines data validation and serialization for economic data endpoints.
"""
from datetime import date as date_type, datetime
from typing import Optional, List
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict


# Data Point schemas
class DataPointBase(BaseModel):
    """Base schema for data points."""

    series_id: str = Field(
        ...,
        max_length=255,
        description="FRED series identifier",
        examples=["GDP", "UNRATE", "CPIAUCSL"]
    )
    date: date_type = Field(
        ...,
        description="Observation date",
        examples=["2024-01-01"]
    )
    value: float = Field(
        ...,
        description="Observation value",
        examples=[27000.0]
    )


class DataPointCreate(DataPointBase):
    """Schema for creating a data point."""

    realtime_start: Optional[date_type] = Field(
        None,
        description="Real-time period start date from FRED"
    )
    realtime_end: Optional[date_type] = Field(
        None,
        description="Real-time period end date from FRED"
    )


class DataPointResponse(DataPointBase):
    """Schema for data point response."""

    id: int = Field(..., description="Unique data point identifier")
    realtime_start: Optional[date_type] = Field(None, description="Real-time period start")
    realtime_end: Optional[date_type] = Field(None, description="Real-time period end")
    created_at: datetime = Field(..., description="When the record was created")
    updated_at: datetime = Field(..., description="When the record was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "series_id": "GDP",
                "date": "2024-01-01",
                "value": 27000.0,
                "realtime_start": "2024-01-01",
                "realtime_end": "2024-12-31",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


class DataPointListResponse(BaseModel):
    """Schema for list of data points."""

    data: List[DataPointResponse] = Field(
        ...,
        description="List of data points"
    )
    count: int = Field(
        ...,
        description="Total number of data points"
    )
    series_id: str = Field(
        ...,
        description="FRED series identifier"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "series_id": "GDP",
                        "date": "2024-01-01",
                        "value": 27000.0,
                        "realtime_start": "2024-01-01",
                        "realtime_end": "2024-12-31",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "count": 1,
                "series_id": "GDP"
            }
        }
    )


# Series Metadata schemas
class SeriesMetadataBase(BaseModel):
    """Base schema for series metadata."""

    series_id: str = Field(
        ...,
        max_length=255,
        description="FRED series identifier"
    )
    title: Optional[str] = Field(
        None,
        max_length=500,
        description="Human-readable series title"
    )
    units: Optional[str] = Field(
        None,
        max_length=255,
        description="Units of measurement"
    )
    frequency: Optional[str] = Field(
        None,
        max_length=50,
        description="Data frequency"
    )
    seasonal_adjustment: Optional[str] = Field(
        None,
        max_length=255,
        description="Seasonal adjustment type"
    )
    notes: Optional[str] = Field(
        None,
        max_length=2000,
        description="Additional notes"
    )


class SeriesMetadataResponse(SeriesMetadataBase):
    """Schema for series metadata response."""

    id: int = Field(..., description="Unique identifier")
    last_updated: Optional[date_type] = Field(None, description="Last FRED update")
    created_at: datetime = Field(..., description="When the record was created")
    updated_at: datetime = Field(..., description="When the record was last updated")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "series_id": "GDP",
                "title": "Gross Domestic Product",
                "units": "Billions of Dollars",
                "frequency": "Quarterly",
                "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
                "last_updated": "2024-01-15",
                "notes": "BEA Account Code: A191RC",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }
    )


# FRED API request/response schemas
class FREDSeriesRequest(BaseModel):
    """Schema for FRED series data request."""

    observation_start: Optional[date_type] = Field(
        None,
        description="Start date for observations",
        examples=["2020-01-01"]
    )
    observation_end: Optional[date_type] = Field(
        None,
        description="End date for observations",
        examples=["2024-12-31"]
    )
    sort_order: Optional[str] = Field(
        "asc",
        description="Sort order: 'asc' or 'desc'",
        pattern="^(asc|desc)$"
    )
    units: Optional[str] = Field(
        None,
        description="Data value transformation",
        examples=["lin", "chg", "pch", "pc1"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "observation_start": "2020-01-01",
                "observation_end": "2024-12-31",
                "sort_order": "asc"
            }
        }
    )


class FREDSeriesResponse(BaseModel):
    """Schema for FRED series data response."""

    series_id: str = Field(..., description="FRED series identifier")
    metadata: Optional[SeriesMetadataResponse] = Field(
        None,
        description="Series metadata"
    )
    observations: List[DataPointResponse] = Field(
        ...,
        description="List of observations"
    )
    count: int = Field(..., description="Number of observations")
    from_cache: bool = Field(
        False,
        description="Whether data was retrieved from cache"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "series_id": "GDP",
                "metadata": {
                    "id": 1,
                    "series_id": "GDP",
                    "title": "Gross Domestic Product",
                    "units": "Billions of Dollars",
                    "frequency": "Quarterly",
                    "seasonal_adjustment": "Seasonally Adjusted Annual Rate",
                    "last_updated": "2024-01-15",
                    "notes": "BEA Account Code: A191RC",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T10:30:00Z"
                },
                "observations": [],
                "count": 0,
                "from_cache": False
            }
        }
    )


# FRED Data Point schemas (for new fred_data_points table)
class FredDataPointBase(BaseModel):
    """Base schema for FRED data points."""

    series_id: str = Field(
        ...,
        max_length=50,
        description="FRED series identifier",
        examples=["DFF", "UNRATE", "CPIAUCSL"]
    )
    series_name: str = Field(
        ...,
        max_length=255,
        description="Human-readable series name"
    )
    value: float = Field(
        ...,
        description="Observation value"
    )
    unit: str = Field(
        ...,
        max_length=100,
        description="Unit of measurement"
    )
    date: date_type = Field(
        ...,
        description="Observation date"
    )


class FredDataPointResponse(FredDataPointBase):
    """Schema for FRED data point response."""

    id: int = Field(..., description="Unique data point identifier")
    fetched_at: datetime = Field(..., description="When this data was fetched from FRED API")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "series_id": "DFF",
                "series_name": "Federal Funds Rate",
                "value": 5.33,
                "unit": "Percent",
                "date": "2025-10-01",
                "fetched_at": "2025-10-04T10:30:00Z"
            }
        }
    )


class CurrentDataResponse(BaseModel):
    """Schema for current economic data response."""

    data: List[FredDataPointResponse] = Field(
        ...,
        description="List of current data points"
    )
    cached: bool = Field(
        False,
        description="Whether data was retrieved from cache"
    )
    cache_expires_in: int = Field(
        0,
        description="Seconds until cache expires"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "data": [
                    {
                        "id": 1,
                        "series_id": "DFF",
                        "series_name": "Federal Funds Rate",
                        "value": 5.33,
                        "unit": "Percent",
                        "date": "2025-10-01",
                        "fetched_at": "2025-10-04T10:30:00Z"
                    }
                ],
                "cached": True,
                "cache_expires_in": 298
            }
        }
    )


class HistoricalDataPoint(BaseModel):
    """Schema for a single historical data point."""

    date: date_type = Field(..., description="Observation date")
    value: float = Field(..., description="Observation value")


class HistoricalDataResponse(BaseModel):
    """Schema for historical data response."""

    series_id: str = Field(..., description="FRED series identifier")
    series_name: str = Field(..., description="Human-readable series name")
    unit: str = Field(..., description="Unit of measurement")
    data: List[HistoricalDataPoint] = Field(..., description="Historical data points")
    count: int = Field(..., description="Number of data points")
    cached: bool = Field(False, description="Whether data was retrieved from cache")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "series_id": "DFF",
                "series_name": "Federal Funds Rate",
                "unit": "Percent",
                "data": [
                    {"date": "2025-10-01", "value": 5.33},
                    {"date": "2025-09-01", "value": 5.25}
                ],
                "count": 2,
                "cached": False
            }
        }
    )


class RefreshDataResponse(BaseModel):
    """Schema for data refresh response."""

    status: str = Field(..., description="Status of the refresh operation")
    series_fetched: List[str] = Field(..., description="List of series that were fetched")
    data_points_stored: int = Field(..., description="Number of data points stored")
    timestamp: str = Field(..., description="Timestamp of the refresh operation")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "series_fetched": ["DFF", "DGS10", "UNRATE", "CPIAUCSL", "MORTGAGE30US"],
                "data_points_stored": 5,
                "timestamp": "2025-10-04T10:35:00Z"
            }
        }
    )


# Error response schema
class ErrorResponse(BaseModel):
    """Schema for error responses."""

    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[datetime] = Field(
        default=None,
        description="Error timestamp"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Series not found",
                "error_code": "SERIES_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
    )
