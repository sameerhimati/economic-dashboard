"""
NewsletterBookmark junction table for many-to-many relationship.

Represents the many-to-many relationship between newsletters and bookmark lists.
"""
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class NewsletterBookmark(Base):
    """
    NewsletterBookmark junction table for newsletter-to-bookmark-list relationships.

    Represents which newsletters are saved in which bookmark lists.
    This is a many-to-many relationship: a newsletter can be in multiple
    bookmark lists, and a bookmark list can contain multiple newsletters.

    Attributes:
        newsletter_id: UUID foreign key to newsletters table
        bookmark_list_id: UUID foreign key to bookmark_lists table
        created_at: When the newsletter was added to the bookmark list
    """

    __tablename__ = "newsletter_bookmarks"

    # Foreign key to newsletters table with CASCADE delete
    newsletter_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("newsletters.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the newsletter being bookmarked"
    )

    # Foreign key to bookmark_lists table with CASCADE delete
    bookmark_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookmark_lists.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the bookmark list containing this newsletter"
    )

    # Timestamp when the newsletter was added to the bookmark list
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="When the newsletter was added to the bookmark list"
    )

    # Composite primary key: (newsletter_id, bookmark_list_id)
    # This ensures a newsletter can only be added once to a specific bookmark list
    __table_args__ = (
        PrimaryKeyConstraint('newsletter_id', 'bookmark_list_id', name='pk_newsletter_bookmarks'),
        # Index on newsletter_id for queries like "what lists is this newsletter in?"
        Index('ix_newsletter_bookmarks_newsletter_id', 'newsletter_id'),
        # Index on bookmark_list_id for queries like "what newsletters are in this list?"
        Index('ix_newsletter_bookmarks_bookmark_list_id', 'bookmark_list_id'),
    )

    def __repr__(self) -> str:
        """String representation of the newsletter bookmark."""
        return (
            f"<NewsletterBookmark(newsletter_id={self.newsletter_id}, "
            f"bookmark_list_id={self.bookmark_list_id}, created_at={self.created_at})>"
        )
