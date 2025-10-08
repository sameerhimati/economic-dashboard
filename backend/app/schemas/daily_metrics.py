"""
Pydantic schemas for Daily Metrics API responses.
"""
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class MetricChange(BaseModel):
    """Multi-period percentage changes."""
    vs_yesterday: float = Field(description="% change vs 1 day ago")
    vs_last_week: float = Field(description="% change vs 1 week ago")
    vs_last_month: float = Field(description="% change vs 1 month ago")
    vs_last_year: float = Field(description="% change vs 1 year ago")


class MetricSignificance(BaseModel):
    """Statistical significance metrics (simplified for frontend)."""
    percentile: float = Field(description="Percentile rank (0-100)")
    is_outlier: bool = Field(description="Whether value is a statistical outlier")


class SparklinePoint(BaseModel):
    """Single point in sparkline data."""
    date: str
    value: float


class DailyMetric(BaseModel):
    """Single metric in daily briefing (flattened structure for frontend)."""
    code: str
    display_name: str
    description: str
    unit: str
    latest_value: float
    latest_date: str
    sparkline_data: List[SparklinePoint] = Field(description="Last 30 days for mini chart")
    alerts: List[str] = Field(description="Contextual alerts")
    context: str = Field(description="Human-readable context summary")
    changes: MetricChange
    significance: MetricSignificance


class DailyMetricsResponse(BaseModel):
    """Response for GET /api/daily-metrics/daily (flattened structure)."""
    date: str
    weekday: int = Field(description="0=Monday, 6=Sunday")
    theme: str = Field(description="Theme for this weekday")
    summary: str = Field(description="AI-generated summary text for the day")
    metrics_up: int = Field(description="Metrics trending up")
    metrics_down: int = Field(description="Metrics trending down")
    alerts_count: int = Field(description="Total number of metrics with alerts")
    metrics: List[DailyMetric]


class HistoricalDataPoint(BaseModel):
    """Single historical data point."""
    date: str
    value: float


class HistoricalMetricResponse(BaseModel):
    """Response for GET /api/daily-metrics/historical/{code}"""
    metric_code: str
    display_name: str
    unit: str
    data: List[HistoricalDataPoint]
    count: int


class TopMover(BaseModel):
    """Top moving metric for weekly reflection."""
    code: str
    display_name: str
    change_percent: float = Field(description="Percentage change for the week")
    latest_value: float = Field(description="Current value of the metric")
    unit: str = Field(description="Unit of measurement")


class ThresholdCrossing(BaseModel):
    """Significant threshold crossing event."""
    code: str
    display_name: str
    threshold_type: str = Field(description="Type of threshold (e.g., 'above_7_percent')")
    description: str = Field(description="Human-readable description of the crossing")


class WeeklyReflectionResponse(BaseModel):
    """Response for GET /api/daily-metrics/weekly-reflection"""
    week_start: str = Field(description="Start date of the week (YYYY-MM-DD)")
    week_end: str = Field(description="End date of the week (YYYY-MM-DD)")
    summary: str = Field(description="AI-generated summary of the week")
    top_movers: List[TopMover]
    threshold_crossings: List[ThresholdCrossing] = Field(description="Significant threshold events")


class RefreshMetricRequest(BaseModel):
    """Request for POST /api/daily-metrics/refresh/{code}"""
    force: bool = Field(default=False, description="Force refresh even if recently updated")


class RefreshMetricResponse(BaseModel):
    """Response for POST /api/daily-metrics/refresh/{code}"""
    status: str
    metric_code: str
    data_points_updated: int
    message: str
