"""
Database models package.

Exports all database models for easy importing.
"""
from app.models.base import Base, TimestampMixin
from app.models.user import User
from app.models.data_point import DataPoint, SeriesMetadata
from app.models.fred_data import FredDataPoint
from app.models.newsletter import Newsletter

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "DataPoint",
    "SeriesMetadata",
    "FredDataPoint",
    "Newsletter",
]
