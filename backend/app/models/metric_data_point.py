"""
Metric Data Point model for storing time-series economic data.

Stores historical data for economic indicators from FRED, BEA, BLS, etc.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MetricDataPoint(Base, TimestampMixin):
    """
    Time-series data point for economic metrics.

    Stores historical values with 5 years of data for analysis.
    Supports multiple data sources (FRED, BEA, BLS).

    Attributes:
        id: Unique identifier
        metric_code: Metric identifier (e.g., "FEDFUNDS", "GDP")
        source: Data source ("FRED", "BEA", "BLS")
        date: Date of the observation
        value: Numeric value
        created_at: When the record was created (from TimestampMixin)
        updated_at: When the record was last updated (from TimestampMixin)
    """

    __tablename__ = "metric_data_points"

    # Primary key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
        autoincrement=True,
        doc="Unique identifier"
    )

    # Metric identification
    metric_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        doc="Metric code (e.g., FEDFUNDS, GDP)"
    )

    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Data source (FRED, BEA, BLS)"
    )

    # Data
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Observation date"
    )

    value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="Numeric value"
    )

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('metric_code', 'date', name='uix_metric_date'),
        Index('idx_metric_code_date', 'metric_code', 'date'),
        Index('idx_metric_code_created', 'metric_code', 'created_at'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<MetricDataPoint(code={self.metric_code}, date={self.date}, value={self.value})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "metric_code": self.metric_code,
            "source": self.source,
            "date": self.date.isoformat() if self.date else None,
            "value": self.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
