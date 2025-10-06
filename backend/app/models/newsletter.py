"""
Newsletter database model for storing email newsletter data.

Stores parsed email newsletters from Bisnow and other real estate sources.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING
import uuid

from sqlalchemy import String, Text, DateTime, JSON, Index, UniqueConstraint, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.bookmark_list import BookmarkList
    from app.models.article_source import ArticleSource


class Newsletter(Base, TimestampMixin):
    """
    Newsletter model for storing email newsletter data.

    Stores email newsletters with extracted content, metadata, and key points
    from real estate newsletters (primarily Bisnow).

    Attributes:
        id: Unique newsletter identifier (UUID)
        user_id: ID of user who owns this newsletter
        user: User relationship
        source: Email sender/source (e.g., 'alerts@mail.bisnow.com')
        category: Newsletter type (e.g., 'Houston', 'Austin', 'National Deal Brief')
        subject: Email subject line
        content_html: Full HTML content of the email
        content_text: Extracted plain text content
        key_points: JSON structure with extracted headlines, metrics, locations, companies
        received_date: When the email was received
        parsed_date: When the email was parsed
        created_at: When the record was created (from TimestampMixin)
        updated_at: When the record was last updated (from TimestampMixin)
    """

    __tablename__ = "newsletters"

    # Primary key - UUID for better distributed systems support
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique newsletter identifier"
    )

    # User foreign key
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of user who owns this newsletter"
    )

    # User relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="newsletters"
    )

    # Relationship to articles through article_sources junction table
    article_sources: Mapped[list["ArticleSource"]] = relationship(
        "ArticleSource",
        back_populates="newsletter",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="Articles extracted from this newsletter"
    )

    # Email source/sender
    source: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
        doc="Email sender address (e.g., 'alerts@mail.bisnow.com')"
    )

    # Newsletter category/type
    category: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Newsletter category (e.g., 'Houston Morning Brief', 'National Deal Brief')"
    )

    # Email subject
    subject: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        doc="Email subject line"
    )

    # Full HTML content
    content_html: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Full HTML content of the email"
    )

    # Extracted plain text
    content_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Extracted plain text content from HTML"
    )

    # Extracted key points as JSON
    key_points: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="Extracted key points including headlines, metrics, locations, companies"
    )

    # Email received timestamp
    received_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="When the email was received"
    )

    # Parsing timestamp
    parsed_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="When the email was parsed and stored"
    )

    # Composite unique constraint: one entry per user + subject + received_date
    # This prevents duplicate newsletter entries for each user
    __table_args__ = (
        UniqueConstraint('user_id', 'subject', 'received_date', name='uix_newsletter_user_subject_date'),
        Index('ix_newsletter_user_id', 'user_id'),  # For user-based queries
        Index('ix_newsletter_user_category_date', 'user_id', 'category', 'received_date'),  # For user category queries
        Index('ix_newsletter_user_received', 'user_id', 'received_date'),  # For user date queries
        Index('ix_newsletter_category_date', 'category', 'received_date'),  # For category-based queries
        Index('ix_newsletter_source_date', 'source', 'received_date'),  # For source-based queries
    )

    def __repr__(self) -> str:
        """String representation of the newsletter."""
        return (
            f"<Newsletter(id={self.id}, category='{self.category}', "
            f"subject='{self.subject[:50]}...', received={self.received_date})>"
        )

    def to_dict(self) -> dict:
        """
        Convert newsletter to dictionary.

        Returns:
            dict: Newsletter as dictionary
        """
        return {
            "id": str(self.id),
            "source": self.source,
            "category": self.category,
            "subject": self.subject,
            "content_html": self.content_html,
            "content_text": self.content_text,
            "key_points": self.key_points,
            "received_date": self.received_date.isoformat() if self.received_date else None,
            "parsed_date": self.parsed_date.isoformat() if self.parsed_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
