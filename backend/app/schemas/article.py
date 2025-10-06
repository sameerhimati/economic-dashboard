"""
Pydantic schemas for article API endpoints.

Defines request/response models for article operations.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ArticleBase(BaseModel):
    """Base article schema with common fields."""

    headline: str = Field(..., description="Article headline/title")
    url: Optional[str] = Field(None, description="Article URL (optional)")
    category: str = Field(..., description="Newsletter category")
    received_date: datetime = Field(..., description="When newsletter containing article was received")
    position: int = Field(..., description="Position in the original newsletter")


class ArticleResponse(ArticleBase):
    """Schema for article response."""

    id: UUID = Field(..., description="Article unique ID")
    user_id: int = Field(..., description="ID of user who owns this article")
    created_at: datetime = Field(..., description="When article record was created")
    updated_at: datetime = Field(..., description="When article record was updated")

    # Newsletter sources this article appeared in
    source_count: int = Field(default=1, description="Number of newsletters this article appeared in")

    model_config = ConfigDict(from_attributes=True)


class ArticleWithSources(ArticleResponse):
    """Article with all its newsletter sources."""

    newsletter_subjects: List[str] = Field(
        default_factory=list,
        description="Subjects of newsletters containing this article"
    )


class ArticleListResponse(BaseModel):
    """Schema for list of articles."""

    articles: List[ArticleResponse] = Field(..., description="List of articles")
    count: int = Field(..., description="Number of articles in response")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(20, description="Number of items per page")


class ArticlesByCategoryResponse(BaseModel):
    """Articles grouped by category."""

    category: str = Field(..., description="Newsletter category")
    article_count: int = Field(..., description="Number of articles in this category")
    articles: List[ArticleResponse] = Field(..., description="Articles in this category")
