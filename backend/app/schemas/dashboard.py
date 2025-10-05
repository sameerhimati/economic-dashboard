"""
Pydantic schemas for dashboard endpoints.

Defines data validation and serialization for the dashboard feed.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class HistoricalPoint(BaseModel):
    """Schema for a single historical data point."""

    date: str = Field(
        ...,
        description="Observation date in ISO format",
        examples=["2025-10-01"]
    )
    value: float = Field(
        ...,
        description="Observation value",
        examples=[5.33]
    )


class DashboardIndicator(BaseModel):
    """Schema for a dashboard indicator."""

    id: str = Field(
        ...,
        description="FRED series identifier",
        examples=["DFF"]
    )
    name: str = Field(
        ...,
        description="Human-readable indicator name",
        examples=["Federal Funds Rate"]
    )
    value: float = Field(
        ...,
        description="Current value",
        examples=[5.33]
    )
    change: float = Field(
        ...,
        description="Absolute change from previous period",
        examples=[0.25]
    )
    changePercent: float = Field(
        ...,
        description="Percentage change from previous period",
        examples=[4.92]
    )
    lastUpdated: str = Field(
        ...,
        description="Date of last update in ISO format",
        examples=["2025-10-04"]
    )
    source: str = Field(
        default="FRED",
        description="Data source",
        examples=["FRED"]
    )
    description: Optional[str] = Field(
        None,
        description="Brief description of the indicator",
        examples=["The interest rate at which banks lend to each other overnight"]
    )
    historicalData: Optional[List[HistoricalPoint]] = Field(
        None,
        description="Recent historical data points for charting"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "DFF",
                "name": "Federal Funds Rate",
                "value": 5.33,
                "change": 0.25,
                "changePercent": 4.92,
                "lastUpdated": "2025-10-04",
                "source": "FRED",
                "description": "The interest rate at which banks lend to each other overnight",
                "historicalData": [
                    {"date": "2025-10-01", "value": 5.08},
                    {"date": "2025-10-02", "value": 5.15},
                    {"date": "2025-10-03", "value": 5.25},
                    {"date": "2025-10-04", "value": 5.33}
                ]
            }
        }
    )


class DashboardNewsItem(BaseModel):
    """Schema for a dashboard news item."""

    id: str = Field(
        ...,
        description="Unique news item identifier",
        examples=["1"]
    )
    title: str = Field(
        ...,
        description="News headline",
        examples=["Fed Holds Rates Steady"]
    )
    summary: str = Field(
        ...,
        description="Brief summary of the news",
        examples=["Federal Reserve maintains interest rates at current levels..."]
    )
    source: str = Field(
        ...,
        description="News source",
        examples=["Federal Reserve"]
    )
    publishedAt: str = Field(
        ...,
        description="Publication timestamp in ISO format",
        examples=["2025-10-04T14:00:00Z"]
    )
    importance: str = Field(
        default="medium",
        description="Importance level: low, medium, or high",
        examples=["high"]
    )
    category: Optional[str] = Field(
        None,
        description="News category",
        examples=["monetary-policy"]
    )
    url: Optional[str] = Field(
        None,
        description="Link to full article",
        examples=["https://www.federalreserve.gov/newsevents/pressreleases/monetary20251004a.htm"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "1",
                "title": "Fed Holds Rates Steady",
                "summary": "Federal Reserve maintains interest rates at current levels amid economic uncertainty",
                "source": "Federal Reserve",
                "publishedAt": "2025-10-04T14:00:00Z",
                "importance": "high",
                "category": "monetary-policy",
                "url": "https://www.federalreserve.gov/newsevents/"
            }
        }
    )


class DashboardTodayResponse(BaseModel):
    """Schema for the /dashboard/today response."""

    marketStatus: str = Field(
        ...,
        description="Current market status: open, closed, pre-market, or after-hours",
        examples=["open"]
    )
    lastUpdated: str = Field(
        ...,
        description="When the data was last updated in ISO format",
        examples=["2025-10-04T18:00:00Z"]
    )
    indicators: List[DashboardIndicator] = Field(
        ...,
        description="List of economic indicators"
    )
    news: List[DashboardNewsItem] = Field(
        default=[],
        description="List of relevant news items"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marketStatus": "open",
                "lastUpdated": "2025-10-04T18:00:00Z",
                "indicators": [
                    {
                        "id": "DFF",
                        "name": "Federal Funds Rate",
                        "value": 5.33,
                        "change": 0.25,
                        "changePercent": 4.92,
                        "lastUpdated": "2025-10-04",
                        "source": "FRED",
                        "description": "The interest rate at which banks lend to each other overnight"
                    }
                ],
                "news": []
            }
        }
    )


class DashboardMetricsResponse(BaseModel):
    """Schema for the /dashboard/metrics response."""

    marketStatus: str = Field(
        ...,
        description="Current market status",
        examples=["open"]
    )
    lastUpdated: str = Field(
        ...,
        description="When the data was last updated in ISO format",
        examples=["2025-10-04T18:00:00Z"]
    )
    metrics: List[DashboardIndicator] = Field(
        ...,
        description="List of economic metrics"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "marketStatus": "open",
                "lastUpdated": "2025-10-04T18:00:00Z",
                "metrics": [
                    {
                        "id": "UNRATE",
                        "name": "Unemployment Rate",
                        "value": 3.8,
                        "change": -0.1,
                        "changePercent": -2.56,
                        "lastUpdated": "2025-10-04",
                        "source": "FRED",
                        "description": "The percentage of the labor force that is unemployed"
                    }
                ]
            }
        }
    )


class DashboardBreakingResponse(BaseModel):
    """Schema for the /dashboard/breaking response."""

    news: List[DashboardNewsItem] = Field(
        default=[],
        description="List of breaking news items"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "news": []
            }
        }
    )


class DashboardWeeklyResponse(BaseModel):
    """Schema for the /dashboard/weekly response."""

    summary: Optional[str] = Field(
        None,
        description="Weekly economic summary",
        examples=["Markets showed mixed performance this week..."]
    )
    highlights: List[str] = Field(
        default=[],
        description="Key highlights from the week"
    )
    weekStart: Optional[str] = Field(
        None,
        description="Week start date in ISO format",
        examples=["2025-09-29"]
    )
    weekEnd: Optional[str] = Field(
        None,
        description="Week end date in ISO format",
        examples=["2025-10-04"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary": None,
                "highlights": [],
                "weekStart": None,
                "weekEnd": None
            }
        }
    )
