"""
BookmarkList database model for organizing newsletters into custom lists.

Allows users to create custom bookmark lists (max 10) to organize their newsletters.
"""
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String, Integer, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.newsletter import Newsletter


class BookmarkList(Base, TimestampMixin):
    """
    BookmarkList model for organizing newsletters into custom lists.

    Users can create custom bookmark lists to organize and categorize
    their newsletters. Each user can create up to 10 bookmark lists,
    and each list can contain multiple newsletters.

    Attributes:
        id: Unique bookmark list identifier (UUID)
        user_id: ID of user who owns this bookmark list
        name: Name of the bookmark list (e.g., 'Houston Deals', 'Market Trends')
        user: User relationship
        newsletters: Many-to-many relationship with Newsletter through newsletter_bookmarks
        created_at: When the bookmark list was created (from TimestampMixin)
        updated_at: When the bookmark list was last updated (from TimestampMixin)
    """

    __tablename__ = "bookmark_lists"

    # Primary key - UUID for consistency with Newsletter model
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique bookmark list identifier"
    )

    # User foreign key with CASCADE delete
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="ID of user who owns this bookmark list"
    )

    # List name
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Name of the bookmark list (e.g., 'Houston Deals', 'Market Trends')"
    )

    # User relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="bookmark_lists"
    )

    # Many-to-many relationship with Newsletter through newsletter_bookmarks
    newsletters: Mapped[list["Newsletter"]] = relationship(
        "Newsletter",
        secondary="newsletter_bookmarks",
        back_populates="bookmark_lists",
        lazy="selectin",
        doc="Newsletters saved to this bookmark list"
    )

    # Table constraints and indexes
    __table_args__ = (
        # Unique constraint: user cannot have duplicate list names
        UniqueConstraint('user_id', 'name', name='uix_bookmark_list_user_name'),
        # Index for user-based queries
        Index('ix_bookmark_list_user_id', 'user_id'),
    )

    def __repr__(self) -> str:
        """String representation of the bookmark list."""
        return f"<BookmarkList(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

    def to_dict(self) -> dict:
        """
        Convert bookmark list to dictionary.

        Returns:
            dict: Bookmark list as dictionary
        """
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
