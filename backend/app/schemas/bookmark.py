"""
Pydantic schemas for bookmark list API endpoints.

Defines request/response models for bookmark operations.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, field_validator


class BookmarkListBase(BaseModel):
    """Base bookmark list schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Name of the bookmark list")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean the bookmark list name."""
        # Strip whitespace
        cleaned = v.strip()

        if not cleaned:
            raise ValueError("Bookmark list name cannot be empty or whitespace only")

        if len(cleaned) > 255:
            raise ValueError("Bookmark list name must be 255 characters or less")

        return cleaned


class BookmarkListCreate(BookmarkListBase):
    """Schema for creating a bookmark list."""
    pass


class BookmarkListUpdate(BookmarkListBase):
    """Schema for updating a bookmark list."""
    pass


class BookmarkListResponse(BookmarkListBase):
    """Schema for bookmark list response."""

    id: UUID = Field(..., description="Bookmark list unique ID")
    user_id: int = Field(..., description="ID of user who owns this list")
    newsletter_count: int = Field(0, description="Number of newsletters in this list")
    created_at: datetime = Field(..., description="When the list was created")
    updated_at: datetime = Field(..., description="When the list was last updated")

    model_config = ConfigDict(from_attributes=True)


class BookmarkListSummary(BaseModel):
    """Schema for bookmark list summary (without newsletter details)."""

    id: UUID = Field(..., description="Bookmark list unique ID")
    name: str = Field(..., description="Name of the bookmark list")
    newsletter_count: int = Field(0, description="Number of newsletters in this list")
    created_at: datetime = Field(..., description="When the list was created")
    updated_at: datetime = Field(..., description="When the list was last updated")

    model_config = ConfigDict(from_attributes=True)


class BookmarkListsResponse(BaseModel):
    """Schema for list of bookmark lists."""

    bookmark_lists: List[BookmarkListSummary] = Field(..., description="List of bookmark lists")
    count: int = Field(..., description="Total number of bookmark lists")


class NewsletterBookmarkResponse(BaseModel):
    """Schema for newsletter in bookmark list context."""

    id: UUID = Field(..., description="Newsletter unique ID")
    source: str = Field(..., description="Email sender")
    category: str = Field(..., description="Newsletter category")
    subject: str = Field(..., description="Email subject")
    received_date: datetime = Field(..., description="When email was received")
    created_at: datetime = Field(..., description="When record was created")
    bookmarked_at: Optional[datetime] = Field(None, description="When newsletter was added to this list")

    model_config = ConfigDict(from_attributes=True)


class BookmarkListNewslettersResponse(BaseModel):
    """Schema for newsletters in a bookmark list."""

    bookmark_list_id: UUID = Field(..., description="Bookmark list ID")
    bookmark_list_name: str = Field(..., description="Bookmark list name")
    newsletters: List[NewsletterBookmarkResponse] = Field(..., description="Newsletters in this list")
    count: int = Field(..., description="Number of newsletters in response")
    total_count: int = Field(..., description="Total newsletters in this list")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")


class BookmarkOperationResponse(BaseModel):
    """Schema for bookmark operation results."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Operation result message")
    bookmark_list_id: Optional[UUID] = Field(None, description="Bookmark list ID")
    newsletter_id: Optional[UUID] = Field(None, description="Newsletter ID")
