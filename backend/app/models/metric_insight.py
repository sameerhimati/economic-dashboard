"""
Metric Insight model for storing generated alerts and insights.

Stores AI-generated insights, alerts, and notable events for metrics.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class MetricInsight(Base, TimestampMixin):
    """
    AI-generated insights and alerts for metrics.

    Stores notable events like threshold crossings, trend reversals,
    all-time highs/lows, and other significant changes.

    Attributes:
        id: Unique identifier
        metric_code: Metric this insight is for
        date: Date the insight applies to
        insight_type: Type of insight (alert, threshold, trend_reversal, etc.)
        message: Human-readable insight message
        severity: Severity level (info, warning, critical)
        created_at: When created (from TimestampMixin)
        updated_at: When updated (from TimestampMixin)
    """

    __tablename__ = "metric_insights"

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
        doc="Metric code this insight is for"
    )

    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        doc="Date the insight applies to"
    )

    # Insight data
    insight_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        doc="Type of insight (alert, threshold, trend_reversal, etc.)"
    )

    message: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Human-readable insight message"
    )

    severity: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        doc="Severity level (info, warning, critical)"
    )

    # Indexes
    __table_args__ = (
        Index('idx_metric_insights_code_date', 'metric_code', 'date'),
    )

    def __repr__(self) -> str:
        """String representation."""
        return f"<MetricInsight(code={self.metric_code}, type={self.insight_type}, date={self.date})>"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "metric_code": self.metric_code,
            "date": self.date.isoformat() if self.date else None,
            "insight_type": self.insight_type,
            "message": self.message,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
