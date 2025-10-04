"""
SQLAlchemy base model configuration.

Provides the declarative base for all database models.
"""
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all database models.

    Provides common functionality and configuration for all models.
    """
    pass


class TimestampMixin:
    """
    Mixin to add timestamp fields to models.

    Adds created_at and updated_at fields with automatic management.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when the record was created"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when the record was last updated"
    )


def serialize_model(obj: Any) -> dict:
    """
    Serialize a SQLAlchemy model instance to a dictionary.

    Args:
        obj: SQLAlchemy model instance

    Returns:
        dict: Dictionary representation of the model
    """
    if obj is None:
        return {}

    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # Handle datetime serialization
        if isinstance(value, datetime):
            result[column.name] = value.isoformat()
        else:
            result[column.name] = value

    return result
