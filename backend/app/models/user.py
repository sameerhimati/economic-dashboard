"""
User database model.

Defines the User table structure for authentication and user management.
"""
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, String, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.newsletter import Newsletter
    from app.models.bookmark_list import BookmarkList


class User(Base, TimestampMixin):
    """
    User model for authentication and user management.

    Attributes:
        id: Unique user identifier
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        full_name: User's full name (optional)

        # Email configuration for newsletter fetching
        email_address: User's email address for newsletter fetching (encrypted)
        email_app_password: User's email app password (encrypted)
        imap_server: IMAP server for email fetching
        imap_port: IMAP port for email fetching

        # Newsletter preferences
        newsletter_preferences: JSON object with newsletter settings

        # Relationships
        newsletters: User's newsletters

        created_at: When the user was created (from TimestampMixin)
        updated_at: When the user was last updated (from TimestampMixin)
    """

    __tablename__ = "users"

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique user identifier"
    )

    # Email (unique identifier for login)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        doc="User's email address (unique, used for login)"
    )

    # Password (stored as bcrypt hash)
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Bcrypt hashed password"
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active"
    )

    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user has admin privileges"
    )

    # Profile information (optional)
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="User's full name"
    )

    # Email configuration for newsletter fetching (encrypted)
    email_address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="User's email address for newsletter fetching"
    )

    email_app_password: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="User's encrypted email app password for IMAP access"
    )

    imap_server: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="imap.gmail.com",
        server_default="imap.gmail.com",
        doc="IMAP server for email fetching"
    )

    imap_port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=993,
        server_default="993",
        doc="IMAP port for email fetching"
    )

    # Newsletter preferences (JSON)
    newsletter_preferences: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        doc="Newsletter preferences including categories, fetch settings, and last fetch timestamp"
    )

    # Relationships
    newsletters: Mapped[list["Newsletter"]] = relationship(
        "Newsletter",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    bookmark_lists: Mapped[list["BookmarkList"]] = relationship(
        "BookmarkList",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        doc="User's custom bookmark lists for organizing newsletters"
    )

    def __repr__(self) -> str:
        """String representation of the user."""
        return f"<User(id={self.id}, email='{self.email}', active={self.is_active})>"

    def to_dict(self) -> dict:
        """
        Convert user to dictionary (excluding sensitive data).

        Returns:
            dict: User data without password
        """
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_superuser": self.is_superuser,
            "full_name": self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
