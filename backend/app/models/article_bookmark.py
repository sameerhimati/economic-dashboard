"""
ArticleBookmark junction table for many-to-many relationship between articles and bookmark lists.

Represents which articles are saved in which bookmark lists. Replaces the old
newsletter_bookmarks table - users now bookmark individual articles instead of entire newsletters.
"""
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, DateTime, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ArticleBookmark(Base):
    """
    ArticleBookmark junction table for article-to-bookmark-list relationships.

    Represents which articles are saved in which bookmark lists.
    This is a many-to-many relationship: an article can be in multiple
    bookmark lists, and a bookmark list can contain multiple articles.

    Attributes:
        article_id: UUID foreign key to articles table
        bookmark_list_id: UUID foreign key to bookmark_lists table
        created_at: When the article was added to the bookmark list
    """

    __tablename__ = "article_bookmarks"

    # Foreign key to articles table with CASCADE delete
    article_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the article being bookmarked"
    )

    # Foreign key to bookmark_lists table with CASCADE delete
    bookmark_list_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bookmark_lists.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the bookmark list containing this article"
    )

    # Timestamp when the article was added to the bookmark list
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="When the article was added to the bookmark list"
    )

    # Composite primary key: (article_id, bookmark_list_id)
    # This ensures an article can only be added once to a specific bookmark list
    __table_args__ = (
        PrimaryKeyConstraint('article_id', 'bookmark_list_id', name='pk_article_bookmarks'),
        # Index on article_id for queries like "what lists is this article in?"
        Index('ix_article_bookmark_article', 'article_id'),
        # Index on bookmark_list_id for queries like "what articles are in this list?"
        Index('ix_article_bookmark_list', 'bookmark_list_id'),
    )

    def __repr__(self) -> str:
        """String representation of the article bookmark."""
        return (
            f"<ArticleBookmark(article_id={self.article_id}, "
            f"bookmark_list_id={self.bookmark_list_id}, created_at={self.created_at})>"
        )
