"""
Dashboard endpoints for the Economic Dashboard frontend.

Provides formatted, user-friendly economic data for dashboard display.
"""
import logging
from datetime import datetime, time, timedelta
from typing import List, Optional, Dict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.fred_data import FredDataPoint
from app.schemas.dashboard import (
    DashboardTodayResponse,
    DashboardMetricsResponse,
    DashboardBreakingResponse,
    DashboardWeeklyResponse,
    DashboardIndicator,
    DashboardNewsItem,
    HistoricalPoint,
)
from app.api.deps import get_optional_current_user
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Series metadata for transformation
SERIES_METADATA = {
    "DFF": {
        "name": "Federal Funds Rate",
        "description": "The interest rate at which banks lend to each other overnight",
    },
    "DGS10": {
        "name": "10-Year Treasury Yield",
        "description": "The yield on U.S. Treasury bonds with 10 years to maturity",
    },
    "UNRATE": {
        "name": "Unemployment Rate",
        "description": "The percentage of the labor force that is unemployed",
    },
    "CPIAUCSL": {
        "name": "Consumer Price Index",
        "description": "Measure of the average change in prices paid by consumers",
    },
    "MORTGAGE30US": {
        "name": "30-Year Mortgage Rate",
        "description": "Average interest rate for 30-year fixed-rate mortgages",
    },
}


def get_market_status() -> str:
    """
    Determine current market status based on time.

    Uses UTC time and converts to ET for NYSE hours.
    NYSE hours: 9:30 AM - 4:00 PM ET (14:30 - 21:00 UTC)

    Returns:
        str: Market status - "open", "closed", "pre-market", or "after-hours"
    """
    try:
        # Get current time in UTC
        now_utc = datetime.utcnow()
        current_time = now_utc.time()

        # Convert to approximate ET (UTC - 4 hours for EDT, UTC - 5 for EST)
        # For simplicity, using EDT offset (subtract 4 hours)
        et_hour = (now_utc.hour - 4) % 24

        # NYSE hours in ET: 9:30 AM - 4:00 PM
        market_open_et = 9.5  # 9:30 AM
        market_close_et = 16.0  # 4:00 PM
        pre_market_start_et = 4.0  # 4:00 AM
        after_hours_end_et = 20.0  # 8:00 PM

        # Convert current time to decimal hours in ET
        et_decimal = et_hour + now_utc.minute / 60.0

        # Determine status based on ET time
        if et_decimal < pre_market_start_et or et_decimal >= after_hours_end_et:
            return "closed"
        elif et_decimal < market_open_et:
            return "pre-market"
        elif et_decimal < market_close_et:
            return "open"
        else:
            return "after-hours"

    except Exception as e:
        logger.error(f"Error determining market status: {str(e)}", exc_info=True)
        # Default to closed on error
        return "closed"


async def get_historical_data(
    db: AsyncSession,
    series_id: str,
    days: int = 30
) -> List[HistoricalPoint]:
    """
    Fetch historical data for a series.

    Args:
        db: Database session
        series_id: FRED series identifier
        days: Number of days of historical data to fetch

    Returns:
        List[HistoricalPoint]: Historical data points
    """
    try:
        # Calculate start date
        start_date = (datetime.utcnow() - timedelta(days=days)).date()

        # Query historical data
        result = await db.execute(
            select(FredDataPoint)
            .where(
                and_(
                    FredDataPoint.series_id == series_id,
                    FredDataPoint.date >= start_date
                )
            )
            .order_by(FredDataPoint.date.asc())
        )
        points = result.scalars().all()

        # Convert to HistoricalPoint schema
        return [
            HistoricalPoint(
                date=point.date.isoformat(),
                value=float(point.value)
            )
            for point in points
        ]

    except Exception as e:
        logger.error(
            f"Error fetching historical data for {series_id}: {str(e)}",
            exc_info=True
        )
        return []


async def calculate_change(
    db: AsyncSession,
    current_point: FredDataPoint
) -> tuple[float, float]:
    """
    Calculate absolute and percentage change from previous period.

    Args:
        db: Database session
        current_point: Current data point

    Returns:
        tuple[float, float]: (absolute_change, percent_change)
    """
    try:
        # Get previous data point (most recent before current date)
        result = await db.execute(
            select(FredDataPoint)
            .where(
                and_(
                    FredDataPoint.series_id == current_point.series_id,
                    FredDataPoint.date < current_point.date
                )
            )
            .order_by(desc(FredDataPoint.date))
            .limit(1)
        )
        previous_point = result.scalar_one_or_none()

        if previous_point:
            current_value = float(current_point.value)
            previous_value = float(previous_point.value)

            absolute_change = current_value - previous_value

            # Avoid division by zero
            if previous_value != 0:
                percent_change = (absolute_change / previous_value) * 100
            else:
                percent_change = 0.0

            return absolute_change, percent_change
        else:
            # No previous data point
            return 0.0, 0.0

    except Exception as e:
        logger.error(
            f"Error calculating change for {current_point.series_id}: {str(e)}",
            exc_info=True
        )
        return 0.0, 0.0


async def transform_to_indicator(
    db: AsyncSession,
    data_point: FredDataPoint,
    include_historical: bool = True
) -> DashboardIndicator:
    """
    Transform a FRED data point to a dashboard indicator.

    Args:
        db: Database session
        data_point: FRED data point from database
        include_historical: Whether to include historical data

    Returns:
        DashboardIndicator: Formatted indicator
    """
    try:
        # Get metadata
        metadata = SERIES_METADATA.get(
            data_point.series_id,
            {
                "name": data_point.series_name,
                "description": f"Economic indicator: {data_point.series_name}"
            }
        )

        # Calculate change from previous period
        absolute_change, percent_change = await calculate_change(db, data_point)

        # Get historical data if requested
        historical_data = None
        if include_historical:
            historical_data = await get_historical_data(db, data_point.series_id)

        return DashboardIndicator(
            id=data_point.series_id,
            name=metadata["name"],
            value=float(data_point.value),
            change=round(absolute_change, 2),
            changePercent=round(percent_change, 2),
            lastUpdated=data_point.date.isoformat(),
            source="FRED",
            description=metadata.get("description"),
            historicalData=historical_data
        )

    except Exception as e:
        logger.error(
            f"Error transforming data point to indicator: {str(e)}",
            exc_info=True
        )
        # Return basic indicator on error
        return DashboardIndicator(
            id=data_point.series_id,
            name=data_point.series_name,
            value=float(data_point.value),
            change=0.0,
            changePercent=0.0,
            lastUpdated=data_point.date.isoformat(),
            source="FRED",
            description=None,
            historicalData=None
        )


async def get_latest_indicators(
    db: AsyncSession,
    include_historical: bool = True
) -> List[DashboardIndicator]:
    """
    Get latest indicators for all tracked series.

    Args:
        db: Database session
        include_historical: Whether to include historical data

    Returns:
        List[DashboardIndicator]: List of indicators
    """
    try:
        # Get all tracked series
        tracked_series = list(SERIES_METADATA.keys())

        # Query latest data point for each series
        indicators = []

        for series_id in tracked_series:
            result = await db.execute(
                select(FredDataPoint)
                .where(FredDataPoint.series_id == series_id)
                .order_by(desc(FredDataPoint.date))
                .limit(1)
            )
            latest_point = result.scalar_one_or_none()

            if latest_point:
                indicator = await transform_to_indicator(
                    db,
                    latest_point,
                    include_historical
                )
                indicators.append(indicator)

        # Sort by series_id for consistent ordering
        indicators.sort(key=lambda x: x.id)

        return indicators

    except Exception as e:
        logger.error(
            f"Error fetching latest indicators: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching economic indicators: {str(e)}"
        )


def generate_mock_news() -> List[DashboardNewsItem]:
    """
    Generate mock news items for demonstration.

    In production, this would integrate with a real news API.

    Returns:
        List[DashboardNewsItem]: List of news items
    """
    # Return empty list for now
    # TODO: Integrate with real news API
    return []


@router.get(
    "/today",
    response_model=DashboardTodayResponse,
    status_code=status.HTTP_200_OK,
    summary="Get today's economic dashboard feed",
    description="Returns current market status, economic indicators, and news"
)
async def get_dashboard_today(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> DashboardTodayResponse:
    """
    Get today's economic dashboard feed.

    Returns:
        - Market status (open/closed/pre-market/after-hours)
        - Latest economic indicators with historical data
        - Relevant news items

    Args:
        db: Database session
        current_user: Optional authenticated user

    Returns:
        DashboardTodayResponse: Today's dashboard feed

    Raises:
        HTTPException 500: If data fetch fails
    """
    logger.info(
        f"Fetching dashboard today feed for user: "
        f"{current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Get market status
        market_status = get_market_status()
        logger.debug(f"Market status: {market_status}")

        # Get latest indicators with historical data
        indicators = await get_latest_indicators(db, include_historical=True)
        logger.info(f"Retrieved {len(indicators)} indicators")

        # Get news items
        news = generate_mock_news()

        # Build response
        response = DashboardTodayResponse(
            marketStatus=market_status,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            indicators=indicators,
            news=news
        )

        logger.info(
            f"Successfully built dashboard today feed with "
            f"{len(indicators)} indicators and {len(news)} news items"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching dashboard today feed: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard feed: {str(e)}"
        )


@router.get(
    "/metrics",
    response_model=DashboardMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get additional economic metrics",
    description="Returns supplementary economic metrics and indicators"
)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> DashboardMetricsResponse:
    """
    Get additional economic metrics.

    Currently returns the same data as /dashboard/today but without news.
    Can be extended to provide different metrics in the future.

    Args:
        db: Database session
        current_user: Optional authenticated user

    Returns:
        DashboardMetricsResponse: Economic metrics

    Raises:
        HTTPException 500: If data fetch fails
    """
    logger.info(
        f"Fetching dashboard metrics for user: "
        f"{current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Get market status
        market_status = get_market_status()

        # Get latest indicators (without historical data for lighter response)
        metrics = await get_latest_indicators(db, include_historical=False)
        logger.info(f"Retrieved {len(metrics)} metrics")

        # Build response
        response = DashboardMetricsResponse(
            marketStatus=market_status,
            lastUpdated=datetime.utcnow().isoformat() + "Z",
            metrics=metrics
        )

        logger.info(f"Successfully built metrics response with {len(metrics)} metrics")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching dashboard metrics: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard metrics: {str(e)}"
        )


@router.get(
    "/breaking",
    response_model=DashboardBreakingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get breaking economic news",
    description="Returns breaking news items (placeholder for future implementation)"
)
async def get_dashboard_breaking(
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> DashboardBreakingResponse:
    """
    Get breaking economic news.

    Placeholder endpoint that returns empty news array.
    To be implemented with real news API integration.

    Args:
        current_user: Optional authenticated user

    Returns:
        DashboardBreakingResponse: Breaking news items
    """
    logger.info(
        f"Fetching breaking news for user: "
        f"{current_user.email if current_user else 'anonymous'}"
    )

    # Return empty news array for now
    return DashboardBreakingResponse(news=[])


@router.get(
    "/weekly",
    response_model=DashboardWeeklyResponse,
    status_code=status.HTTP_200_OK,
    summary="Get weekly economic summary",
    description="Returns weekly economic summary (placeholder for future implementation)"
)
async def get_dashboard_weekly(
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> DashboardWeeklyResponse:
    """
    Get weekly economic summary.

    Placeholder endpoint that returns null summary.
    To be implemented with real weekly analysis.

    Args:
        current_user: Optional authenticated user

    Returns:
        DashboardWeeklyResponse: Weekly summary
    """
    logger.info(
        f"Fetching weekly summary for user: "
        f"{current_user.email if current_user else 'anonymous'}"
    )

    # Return null summary for now
    return DashboardWeeklyResponse(
        summary=None,
        highlights=[],
        weekStart=None,
        weekEnd=None
    )
