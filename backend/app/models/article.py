"""
Article database model for storing individual newsletter articles.

Individual articles are the primary entity in the system. Each article can appear
in multiple newsletters via the article_sources junction table.
"""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.article_source import ArticleSource
    from app.models.bookmark_list import BookmarkList


class Article(Base, TimestampMixin):
    """
    Individual article from a newsletter.

    An article can appear in multiple newsletters (via article_sources junction table).
    Primary entity for bookmarking and display.

    Attributes:
        id: Unique article identifier (UUID)
        user_id: ID of user who owns this article
        headline: Article headline/title
        url: Article URL (optional - some articles may not have URLs)
        category: Newsletter category (e.g., 'Houston Morning Brief')
        received_date: When the newsletter containing this article was received
        position: Position in the original newsletter (for ordering)
        user: User relationship
        sources: Article sources (which newsletters contain this article)
        bookmark_lists: Bookmark lists that contain this article
        created_at: When the article was created (from TimestampMixin)
        updated_at: When the article was last updated (from TimestampMixin)
    """

    __tablename__ = "articles"

    # Primary key - UUID for consistency with Newsletter model
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique article identifier"
    )

    # User foreign key with CASCADE delete
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of user who owns this article"
    )

    # Article content
    headline: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Article headline/title"
    )

    url: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Article URL (optional - some articles may not have URLs)"
    )

    # Denormalized fields for fast querying (from newsletter)
    category: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Newsletter category (e.g., 'Houston Morning Brief', 'National Deal Brief')"
    )

    received_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="When the newsletter containing this article was received"
    )

    # Position in the original newsletter (for ordering)
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="Position in the original newsletter (for ordering)"
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="articles"
    )

    sources: Mapped[list["ArticleSource"]] = relationship(
        "ArticleSource",
        back_populates="article",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="Source newsletters containing this article"
    )

    bookmark_lists: Mapped[list["BookmarkList"]] = relationship(
        "BookmarkList",
        secondary="article_bookmarks",
        back_populates="articles",
        lazy="selectin",
        doc="Bookmark lists that contain this article"
    )

    # Table constraints and indexes
    __table_args__ = (
        # Prevent exact duplicates: same user + URL + date
        # Note: URL can be NULL, so this constraint allows multiple NULL URLs
        UniqueConstraint('user_id', 'url', 'received_date', name='uix_article_user_url_date'),
        # Composite index for user + category + date queries
        Index('ix_article_user_category_date', 'user_id', 'category', 'received_date'),
        # Index for user + URL lookups
        Index('ix_article_user_url', 'user_id', 'url'),
    )

    def __repr__(self) -> str:
        """String representation of the article."""
        headline_preview = self.headline[:50] + "..." if len(self.headline) > 50 else self.headline
        return (
            f"<Article(id={self.id}, category='{self.category}', "
            f"headline='{headline_preview}', received={self.received_date})>"
        )

    def to_dict(self) -> dict:
        """
        Convert article to dictionary.

        Returns:
            dict: Article as dictionary
        """
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "headline": self.headline,
            "url": self.url,
            "category": self.category,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "position": self.position,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
