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
    """Statistical significance metrics."""
    z_score: float = Field(description="Z-score (std deviations from mean)")
    percentile: float = Field(description="Percentile rank (0-100)")
    is_outlier: bool = Field(description="Whether value is a statistical outlier")
    avg_30d: float = Field(description="30-day rolling average")
    avg_90d: float = Field(description="90-day rolling average")
    avg_1y: float = Field(description="1-year rolling average")


class MetricAnalysis(BaseModel):
    """Complete analysis for a metric."""
    metric_code: str
    current_value: float
    current_date: str
    changes: MetricChange
    significance: MetricSignificance
    alerts: List[str] = Field(description="Contextual alerts")
    context: str = Field(description="Human-readable context summary")


class DailyMetric(BaseModel):
    """Single metric in daily briefing."""
    code: str
    display_name: str
    description: str
    source: str
    unit: str
    current_value: float
    current_date: str
    analysis: MetricAnalysis


class DailySummary(BaseModel):
    """Summary statistics for the day."""
    total_metrics: int
    metrics_up: int = Field(description="Metrics trending up")
    metrics_down: int = Field(description="Metrics trending down")
    metrics_with_alerts: int = Field(description="Metrics with significant alerts")
    outliers_count: int = Field(description="Number of statistical outliers")


class DailyMetricsResponse(BaseModel):
    """Response for GET /api/daily-metrics/daily"""
    date: str
    weekday: int = Field(description="0=Monday, 6=Sunday")
    theme: str = Field(description="Theme for this weekday")
    summary: DailySummary
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
    category: str
    change_pct: float
    direction: str = Field(description="'up' or 'down'")
    significance: str = Field(description="Why this move matters")


class WeeklyReflectionResponse(BaseModel):
    """Response for GET /api/daily-metrics/weekly-reflection"""
    week_ending: str
    top_movers: List[TopMover]
    key_themes: List[str]
    summary: str


class RefreshMetricRequest(BaseModel):
    """Request for POST /api/daily-metrics/refresh/{code}"""
    force: bool = Field(default=False, description="Force refresh even if recently updated")


class RefreshMetricResponse(BaseModel):
    """Response for POST /api/daily-metrics/refresh/{code}"""
    status: str
    metric_code: str
    data_points_updated: int
    message: str
