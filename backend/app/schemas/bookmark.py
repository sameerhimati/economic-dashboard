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
    article_count: int = Field(0, description="Number of articles in this list")
    created_at: datetime = Field(..., description="When the list was created")
    updated_at: datetime = Field(..., description="When the list was last updated")

    model_config = ConfigDict(from_attributes=True)


class BookmarkListSummary(BaseModel):
    """Schema for bookmark list summary (without article details)."""

    id: UUID = Field(..., description="Bookmark list unique ID")
    name: str = Field(..., description="Name of the bookmark list")
    article_count: int = Field(0, description="Number of articles in this list")
    created_at: datetime = Field(..., description="When the list was created")
    updated_at: datetime = Field(..., description="When the list was last updated")

    model_config = ConfigDict(from_attributes=True)


class BookmarkListsResponse(BaseModel):
    """Schema for list of bookmark lists."""

    bookmark_lists: List[BookmarkListSummary] = Field(..., description="List of bookmark lists")
    count: int = Field(..., description="Total number of bookmark lists")


class ArticleBookmarkResponse(BaseModel):
    """Schema for article in bookmark list context."""

    id: UUID = Field(..., description="Article unique ID")
    headline: str = Field(..., description="Article headline/title")
    url: Optional[str] = Field(None, description="Article URL")
    category: str = Field(..., description="Newsletter category")
    received_date: datetime = Field(..., description="When newsletter was received")
    position: int = Field(..., description="Position in newsletter")
    created_at: datetime = Field(..., description="When article was created")
    bookmarked_at: Optional[datetime] = Field(None, description="When article was added to this list")

    model_config = ConfigDict(from_attributes=True)




class BookmarkListArticlesResponse(BaseModel):
    """Schema for articles in a bookmark list."""

    bookmark_list_id: UUID = Field(..., description="Bookmark list ID")
    bookmark_list_name: str = Field(..., description="Bookmark list name")
    articles: List[ArticleBookmarkResponse] = Field(..., description="Articles in this list")
    count: int = Field(..., description="Number of articles in response")
    total_count: int = Field(..., description="Total articles in this list")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Number of items per page")




class BookmarkOperationResponse(BaseModel):
    """Schema for bookmark operation results."""

    success: bool = Field(..., description="Whether operation succeeded")
    message: str = Field(..., description="Operation result message")
    bookmark_list_id: Optional[UUID] = Field(None, description="Bookmark list ID")
    article_id: Optional[UUID] = Field(None, description="Article ID")
