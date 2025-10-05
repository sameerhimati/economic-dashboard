"""
ArticleSource junction table for many-to-many relationship between articles and newsletters.

Represents which newsletters contain which articles. One article can appear in
multiple newsletters (e.g., same deal mentioned in both Houston and National briefs).
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.article import Article
    from app.models.newsletter import Newsletter


class ArticleSource(Base):
    """
    ArticleSource junction table linking articles to their source newsletters.

    One article can appear in multiple newsletters (e.g., same deal mentioned
    in both Houston Morning Brief and National Deal Brief).

    Attributes:
        article_id: UUID foreign key to articles table
        newsletter_id: UUID foreign key to newsletters table
        created_at: When the article was extracted from the newsletter
        article: Article relationship
        newsletter: Newsletter relationship
    """

    __tablename__ = "article_sources"

    # Foreign key to articles table with CASCADE delete
    article_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("articles.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the article"
    )

    # Foreign key to newsletters table with CASCADE delete
    newsletter_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("newsletters.id", ondelete="CASCADE"),
        nullable=False,
        doc="ID of the newsletter containing this article"
    )

    # Timestamp when the article-newsletter relationship was created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        doc="When the article was extracted from the newsletter"
    )

    # Relationships
    article: Mapped["Article"] = relationship(
        "Article",
        back_populates="sources"
    )

    newsletter: Mapped["Newsletter"] = relationship(
        "Newsletter",
        back_populates="article_sources"
    )

    # Composite primary key: (article_id, newsletter_id)
    # This ensures an article can only be linked once to a specific newsletter
    __table_args__ = (
        PrimaryKeyConstraint('article_id', 'newsletter_id', name='pk_article_sources'),
        # Index on article_id for queries like "what newsletters contain this article?"
        Index('ix_article_source_article', 'article_id'),
        # Index on newsletter_id for queries like "what articles are in this newsletter?"
        Index('ix_article_source_newsletter', 'newsletter_id'),
    )

    def __repr__(self) -> str:
        """String representation of the article source."""
        return (
            f"<ArticleSource(article_id={self.article_id}, "
            f"newsletter_id={self.newsletter_id}, created_at={self.created_at})>"
        )
