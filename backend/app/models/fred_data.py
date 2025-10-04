"""
FRED data point database model for storing economic metrics.

Stores key economic indicators from FRED API with metadata.
"""
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import String, Numeric, Date, Integer, Index, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class FredDataPoint(Base):
    """
    FRED data point model for storing key economic indicators.

    Stores specific economic metrics tracked by the dashboard with
    human-readable names and units for display purposes.

    Attributes:
        id: Unique data point identifier
        series_id: FRED series identifier (e.g., 'DFF', 'UNRATE')
        series_name: Human-readable name (e.g., 'Federal Funds Rate')
        value: Numeric value of the observation
        unit: Unit of measurement (e.g., 'Percent', 'Index')
        date: Observation date
        fetched_at: When we fetched this data from FRED API
    """

    __tablename__ = "fred_data_points"

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
        String(50),
        nullable=False,
        index=True,
        doc="FRED series identifier (e.g., 'DFF', 'UNRATE', 'CPIAUCSL')"
    )

    # Human-readable series name
    series_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable series name (e.g., 'Federal Funds Rate')"
    )

    # Observation value (using Numeric for precision)
    value: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=6),
        nullable=False,
        doc="Numeric value of the observation"
    )

    # Unit of measurement
    unit: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Unit of measurement (e.g., 'Percent', 'Index', 'Billions of Dollars')"
    )

    # Observation date
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        doc="Date of the economic observation"
    )

    # When we fetched this data
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        doc="Timestamp when this data was fetched from FRED API"
    )

    # Composite unique constraint: one value per series per date
    # Composite indexes for efficient queries
    __table_args__ = (
        UniqueConstraint('series_id', 'date', name='uix_fred_series_date'),
        Index('ix_fred_series_id', 'series_id'),
        Index('ix_fred_date', 'date'),
        Index('ix_fred_series_date', 'series_id', 'date'),
        Index('ix_fred_fetched_at', 'fetched_at'),
    )

    def __repr__(self) -> str:
        """String representation of the data point."""
        return (
            f"<FredDataPoint(id={self.id}, series='{self.series_id}', "
            f"name='{self.series_name}', date={self.date}, value={self.value})>"
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
            "series_name": self.series_name,
            "value": float(self.value),
            "unit": self.unit,
            "date": self.date.isoformat() if self.date else None,
            "fetched_at": self.fetched_at.isoformat() if self.fetched_at else None,
        }
