"""
Data point database model for storing FRED economic data.

Stores time-series data fetched from the FRED API.
"""
from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Float, Date, Integer, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DataPoint(Base, TimestampMixin):
    """
    Data point model for storing FRED economic time-series data.

    Each record represents a single observation of an economic indicator
    (e.g., GDP, unemployment rate) at a specific date.

    Attributes:
        id: Unique data point identifier
        series_id: FRED series identifier (e.g., 'GDP', 'UNRATE')
        date: Observation date
        value: Numeric value of the observation
        realtime_start: Real-time period start date from FRED
        realtime_end: Real-time period end date from FRED
        created_at: When the record was created (from TimestampMixin)
        updated_at: When the record was last updated (from TimestampMixin)
    """

    __tablename__ = "data_points"

    # Primary key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique data point identifier"
    )

    # Series identifier from FRED API
    series_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="FRED series identifier (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')"
    )

    # Observation date
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date of the economic observation"
    )

    # Observation value
    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Numeric value of the observation"
    )

    # FRED real-time period (for data revisions tracking)
    realtime_start: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Real-time period start date from FRED API"
    )

    realtime_end: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Real-time period end date from FRED API"
    )

    # Composite unique constraint: one value per series per date
    __table_args__ = (
        UniqueConstraint('series_id', 'date', name='uix_series_date'),
        Index('ix_series_date', 'series_id', 'date'),  # Composite index for queries
        Index('ix_date_series', 'date', 'series_id'),  # Reverse index for date-based queries
    )

    def __repr__(self) -> str:
        """String representation of the data point."""
        return (
            f"<DataPoint(id={self.id}, series='{self.series_id}', "
            f"date={self.date}, value={self.value})>"
        )

    def to_dict(self) -> dict:
        """
        Convert data point to dictionary.

        Returns:
            dict: Data point as dictionary
        """
        return {
            "id": self.id,
            "series_id": self.series_id,
            "date": self.date.isoformat() if self.date else None,
            "value": self.value,
            "realtime_start": self.realtime_start.isoformat() if self.realtime_start else None,
            "realtime_end": self.realtime_end.isoformat() if self.realtime_end else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SeriesMetadata(Base, TimestampMixin):
    """
    Store metadata about FRED series for caching and reference.

    Attributes:
        id: Unique identifier
        series_id: FRED series identifier
        title: Human-readable series title
        units: Units of measurement
        frequency: Data frequency (Daily, Weekly, Monthly, etc.)
        seasonal_adjustment: Seasonal adjustment type
        last_updated: Last time FRED updated this series
        notes: Additional notes about the series
    """

    __tablename__ = "series_metadata"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True
    )

    series_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        doc="FRED series identifier"
    )

    title: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        doc="Human-readable series title"
    )

    units: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Units of measurement"
    )

    frequency: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Data frequency (Daily, Weekly, Monthly, Quarterly, Annual)"
    )

    seasonal_adjustment: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        doc="Seasonal adjustment type"
    )

    last_updated: Mapped[Optional[date]] = mapped_column(
        Date,
        nullable=True,
        doc="Last time FRED updated this series"
    )

    notes: Mapped[Optional[str]] = mapped_column(
        String(2000),
        nullable=True,
        doc="Additional notes about the series"
    )

    def __repr__(self) -> str:
        """String representation of the series metadata."""
        return f"<SeriesMetadata(series_id='{self.series_id}', title='{self.title}')>"

    def to_dict(self) -> dict:
        """Convert series metadata to dictionary."""
        return {
            "id": self.id,
            "series_id": self.series_id,
            "title": self.title,
            "units": self.units,
            "frequency": self.frequency,
            "seasonal_adjustment": self.seasonal_adjustment,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
