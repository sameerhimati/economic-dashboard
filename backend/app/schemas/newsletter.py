"""
Pydantic schemas for newsletter API endpoints.

Defines request/response models for newsletter operations.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class NewsletterBase(BaseModel):
    """Base newsletter schema with common fields."""

    source: str = Field(..., description="Email sender address")
    category: str = Field(..., description="Newsletter category")
    subject: str = Field(..., description="Email subject line")


class NewsletterCreate(NewsletterBase):
    """Schema for creating a newsletter."""

    content_html: Optional[str] = Field(None, description="Full HTML content")
    content_text: Optional[str] = Field(None, description="Plain text content")
    key_points: Optional[Dict[str, Any]] = Field(None, description="Extracted key points")
    received_date: datetime = Field(..., description="When email was received")
    parsed_date: datetime = Field(..., description="When email was parsed")


class NewsletterUpdate(BaseModel):
    """Schema for updating a newsletter."""

    category: Optional[str] = Field(None, description="Newsletter category")
    key_points: Optional[Dict[str, Any]] = Field(None, description="Updated key points")


class NewsletterResponse(NewsletterBase):
    """Schema for newsletter response."""

    id: UUID = Field(..., description="Newsletter unique ID")
    content_html: Optional[str] = Field(None, description="Full HTML content")
    content_text: Optional[str] = Field(None, description="Plain text content")
    key_points: Optional[Dict[str, Any]] = Field(None, description="Extracted key points")
    received_date: datetime = Field(..., description="When email was received")
    parsed_date: datetime = Field(..., description="When email was parsed")
    created_at: datetime = Field(..., description="When record was created")
    updated_at: datetime = Field(..., description="When record was updated")

    model_config = ConfigDict(from_attributes=True)


class NewsletterSummary(BaseModel):
    """Schema for newsletter summary (without full content)."""

    id: UUID = Field(..., description="Newsletter unique ID")
    source: str = Field(..., description="Email sender")
    category: str = Field(..., description="Newsletter category")
    subject: str = Field(..., description="Email subject")
    received_date: datetime = Field(..., description="When email was received")
    key_points: Optional[Dict[str, Any]] = Field(None, description="Extracted key points")
    created_at: datetime = Field(..., description="When record was created")

    model_config = ConfigDict(from_attributes=True)


class NewsletterListResponse(BaseModel):
    """Schema for list of newsletters."""

    newsletters: List[NewsletterSummary] = Field(..., description="List of newsletters")
    count: int = Field(..., description="Total number of newsletters")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")


class NewsletterSearchRequest(BaseModel):
    """Schema for newsletter search request."""

    query: str = Field(..., min_length=1, description="Search query")
    start_date: Optional[datetime] = Field(None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    category: Optional[str] = Field(None, description="Category filter")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")


class NewsletterSearchResponse(BaseModel):
    """Schema for newsletter search response."""

    newsletters: List[NewsletterSummary] = Field(..., description="Search results")
    count: int = Field(..., description="Number of results")
    total_count: int = Field(..., description="Total matching newsletters")
    query: str = Field(..., description="Search query used")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Items per page")


class NewsletterFetchRequest(BaseModel):
    """Schema for manual newsletter fetch request."""

    days: int = Field(7, ge=1, le=30, description="Number of days to look back")
    sender_filter: Optional[List[str]] = Field(
        None,
        description="List of sender domains to filter"
    )


class NewsletterFetchResponse(BaseModel):
    """Schema for newsletter fetch response."""

    status: str = Field(..., description="Operation status")
    fetched: int = Field(..., description="Number of emails fetched")
    stored: int = Field(..., description="Number of newsletters stored")
    skipped: int = Field(..., description="Number of duplicates skipped")
    timestamp: str = Field(..., description="Operation timestamp")


class MetricExtract(BaseModel):
    """Schema for extracted metric."""

    type: str = Field(..., description="Metric type (cap_rate, deal_value, etc.)")
    value: str = Field(..., description="Formatted value")
    context: str = Field(..., description="Surrounding context")


class KeyPointsResponse(BaseModel):
    """Schema for newsletter key points."""

    headlines: List[str] = Field(default_factory=list, description="Extracted headlines")
    metrics: List[MetricExtract] = Field(default_factory=list, description="Extracted metrics")
    locations: List[str] = Field(default_factory=list, description="Mentioned locations")
    companies: List[str] = Field(default_factory=list, description="Mentioned companies")


class NewsletterStatsResponse(BaseModel):
    """Schema for newsletter statistics."""

    total_newsletters: int = Field(..., description="Total number of newsletters")
    by_category: Dict[str, int] = Field(..., description="Count by category")
    by_source: Dict[str, int] = Field(..., description="Count by source")
    date_range: Dict[str, datetime] = Field(..., description="Earliest and latest dates")
    recent_count: int = Field(..., description="Count from last 7 days")


class NewsletterCleanupResponse(BaseModel):
    """Schema for newsletter cleanup response."""

    status: str = Field(..., description="Operation status")
    deleted_count: int = Field(..., description="Number of newsletters deleted")
    timestamp: str = Field(..., description="Operation timestamp")
