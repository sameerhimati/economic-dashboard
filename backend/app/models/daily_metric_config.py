"""
Daily Metric Configuration model.

Stores metadata about which metrics to track for each day of the week.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DailyMetricConfig(Base, TimestampMixin):
    """
    Configuration for daily metrics tracking.

    Defines which metrics to display on which days, with themed groupings:
    - Monday: Fed & Interest Rates
    - Tuesday: Real Estate & Housing
    - Wednesday: Economic Health (GDP, Jobs, Spending)
    - Thursday: Regional & Energy
    - Friday: Markets & Week Summary
    - Weekend: Weekly Reflection

    Attributes:
        id: Unique identifier
        metric_code: Metric identifier (must match MetricDataPoint.metric_code)
        source: Data source (FRED, BEA, BLS)
        display_name: Human-readable name
        description: Description of the metric
        unit: Unit of measurement (%, $, index, etc.)
        weekday: Day of week (0=Monday, 6=Sunday, null=all days)
        display_order: Display order within the day
        is_active: Whether this metric is currently active
        refresh_frequency: How often to fetch (daily, weekly, monthly)
        created_at: When created (from TimestampMixin)
        updated_at: When updated (from TimestampMixin)
    """

    __tablename__ = "daily_metric_configs"

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
        unique=True,
        nullable=False,
        index=True,
        doc="Metric code (must match MetricDataPoint.metric_code)"
    )

    source: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Data source (FRED, BEA, BLS)"
    )

    # Display metadata
    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Human-readable name"
    )

    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
        doc="Description of the metric"
    )

    unit: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Unit of measurement (%, $, index, etc.)"
    )

    # Scheduling
    weekday: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        doc="Day of week (0=Monday, 6=Sunday, null=all days)"
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Display order within the day"
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether this metric is currently active"
    )

    refresh_frequency: Mapped[str] = mapped_column(
        String(20),
        default="daily",
        nullable=False,
        doc="Refresh frequency (daily, weekly, monthly)"
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<DailyMetricConfig(code={self.metric_code}, name={self.display_name})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "metric_code": self.metric_code,
            "source": self.source,
            "display_name": self.display_name,
            "description": self.description,
            "unit": self.unit,
            "weekday": self.weekday,
            "display_order": self.display_order,
            "is_active": self.is_active,
            "refresh_frequency": self.refresh_frequency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
