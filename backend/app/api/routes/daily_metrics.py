"""
Daily Metrics API Routes.

Provides intelligent daily economic briefings with context and analysis.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import get_db
from app.api.deps import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.models.metric_data_point import MetricDataPoint
from app.services.fred_service import FREDService
from app.services.metric_analysis_service import MetricAnalysisService
from app.config.metrics_config import (
    WEEKDAY_THEMES,
    get_metrics_for_weekday,
    get_metric_config,
    get_all_metric_codes
)
from app.schemas.daily_metrics import (
    DailyMetricsResponse,
    DailyMetric,
    DailySummary,
    MetricAnalysis,
    MetricChange,
    MetricSignificance,
    HistoricalMetricResponse,
    HistoricalDataPoint,
    WeeklyReflectionResponse,
    TopMover,
    RefreshMetricResponse,
    RefreshMetricRequest
)

router = APIRouter(prefix="/daily-metrics", tags=["Daily Metrics"])
logger = logging.getLogger(__name__)


@router.get("/daily", response_model=DailyMetricsResponse)
async def get_daily_metrics(
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format (default: today)"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's intelligent economic briefing.

    Returns metrics for the day with:
    - Multi-period change analysis
    - Statistical significance
    - Contextual alerts
    - Human-readable insights

    Metrics are organized by weekday themes:
    - Monday: Fed & Interest Rates
    - Tuesday: Real Estate & Housing
    - Wednesday: Economic Health (GDP, Jobs, Spending)
    - Thursday: Regional & Energy
    - Friday: Markets & Week Summary
    - Weekend: Weekly Reflection
    """
    try:
        # Parse date
        if date:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            target_date = datetime.now()

        weekday = target_date.weekday()
        theme = WEEKDAY_THEMES.get(weekday, "Economic Overview")

        # Get metrics for this weekday
        weekday_metrics = get_metrics_for_weekday(weekday)

        if not weekday_metrics:
            return DailyMetricsResponse(
                date=target_date.date().isoformat(),
                weekday=weekday,
                theme=theme,
                summary=DailySummary(
                    total_metrics=0,
                    metrics_up=0,
                    metrics_down=0,
                    metrics_with_alerts=0,
                    outliers_count=0
                ),
                metrics=[]
            )

        # Initialize services
        fred_service = FREDService()
        analysis_service = MetricAnalysisService()

        daily_metrics = []
        metrics_up = 0
        metrics_down = 0
        metrics_with_alerts = 0
        outliers_count = 0

        # Process each metric
        for metric_config in weekday_metrics:
            try:
                code = metric_config["code"]

                # Fetch current value from database or FRED
                current_data = await _get_current_metric_value(
                    db, fred_service, code, target_date
                )

                if not current_data:
                    logger.warning(f"No data available for {code}")
                    continue

                # Fetch historical data
                historical_data = await _get_historical_data(db, code, years=5)

                if not historical_data:
                    logger.warning(f"No historical data for {code}")
                    continue

                # Generate analysis
                analysis = await analysis_service.analyze_metric(
                    metric_code=code,
                    current_value=current_data["value"],
                    current_date=current_data["date"],
                    historical_data=historical_data
                )

                # Build response
                daily_metric = DailyMetric(
                    code=code,
                    display_name=metric_config["display_name"],
                    description=metric_config["description"],
                    source=metric_config["source"],
                    unit=metric_config["unit"],
                    current_value=current_data["value"],
                    current_date=current_data["date"].isoformat(),
                    analysis=MetricAnalysis(
                        metric_code=code,
                        current_value=current_data["value"],
                        current_date=current_data["date"].isoformat(),
                        changes=MetricChange(**analysis["changes"]),
                        significance=MetricSignificance(**analysis["significance"]),
                        alerts=analysis["alerts"],
                        context=analysis["context"]
                    )
                )

                daily_metrics.append(daily_metric)

                # Update summary stats
                week_change = analysis["changes"].get("vs_last_week", 0)
                if week_change > 1:
                    metrics_up += 1
                elif week_change < -1:
                    metrics_down += 1

                if analysis["alerts"]:
                    metrics_with_alerts += 1

                if analysis["significance"].get("is_outlier"):
                    outliers_count += 1

            except Exception as e:
                logger.error(f"Error processing metric {metric_config['code']}: {str(e)}")
                continue

        # Close FRED service
        await fred_service.close()

        # Build summary
        summary = DailySummary(
            total_metrics=len(daily_metrics),
            metrics_up=metrics_up,
            metrics_down=metrics_down,
            metrics_with_alerts=metrics_with_alerts,
            outliers_count=outliers_count
        )

        return DailyMetricsResponse(
            date=target_date.date().isoformat(),
            weekday=weekday,
            theme=theme,
            summary=summary,
            metrics=daily_metrics
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        logger.error(f"Error in get_daily_metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/historical/{metric_code}", response_model=HistoricalMetricResponse)
async def get_historical_metric(
    metric_code: str,
    range: str = Query("1y", description="Time range: 30d, 90d, 1y, 5y"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical data for a specific metric.

    Used for interactive charts in the frontend.
    """
    try:
        # Validate metric code
        metric_config = get_metric_config(metric_code)
        if not metric_config:
            raise HTTPException(status_code=404, detail=f"Metric {metric_code} not found")

        # Parse range
        range_days = {
            "30d": 30,
            "90d": 90,
            "1y": 365,
            "5y": 1825
        }

        days = range_days.get(range)
        if days is None:
            raise HTTPException(status_code=400, detail="Invalid range. Use: 30d, 90d, 1y, 5y")

        # Fetch historical data
        years = max(1, days // 365)
        historical_data = await _get_historical_data(db, metric_code, years=years)

        # Filter to requested range
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered_data = [
            HistoricalDataPoint(
                date=d["date"].isoformat(),
                value=d["value"]
            )
            for d in historical_data
            if d["date"] >= cutoff_date
        ]

        return HistoricalMetricResponse(
            metric_code=metric_code,
            display_name=metric_config.get("display_name", metric_code),
            unit=metric_config.get("unit", ""),
            data=filtered_data,
            count=len(filtered_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_historical_metric: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/weekly-reflection", response_model=WeeklyReflectionResponse)
async def get_weekly_reflection(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get weekly reflection summary.

    Shown on weekends with:
    - Top movers of the week
    - Key themes and events
    - Summary insights
    """
    try:
        # Calculate week dates
        today = datetime.now()
        week_start = today - timedelta(days=7)
        week_end = today

        # Get all metrics
        all_codes = get_all_metric_codes()

        fred_service = FREDService()
        analysis_service = MetricAnalysisService()
        top_movers = []

        # Analyze each metric for weekly change
        for code in all_codes[:15]:  # Limit to 15 for performance
            try:
                config = get_metric_config(code)
                historical = await _get_historical_data(db, code, years=1)

                if not historical or len(historical) < 2:
                    continue

                # Get current and week-ago values
                current = historical[-1]
                week_ago = None
                for point in reversed(historical):
                    if point["date"] <= week_start:
                        week_ago = point
                        break

                if not week_ago or week_ago["value"] == 0:
                    continue

                # Calculate weekly change
                change_pct = ((current["value"] - week_ago["value"]) / week_ago["value"]) * 100

                if abs(change_pct) > 2:  # Significant move
                    top_movers.append({
                        "code": code,
                        "change_pct": change_pct,
                        "config": config
                    })

            except Exception as e:
                logger.error(f"Error analyzing {code} for weekly: {str(e)}")
                continue

        await fred_service.close()

        # Sort by absolute change
        top_movers.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

        # Build top movers response
        movers_response = []
        for mover in top_movers[:10]:  # Top 10
            config = mover["config"]
            movers_response.append(TopMover(
                code=mover["code"],
                display_name=config.get("display_name", mover["code"]),
                category=WEEKDAY_THEMES.get(config.get("weekday", 0), "General"),
                change_pct=round(mover["change_pct"], 2),
                direction="up" if mover["change_pct"] > 0 else "down",
                significance=_generate_significance_text(mover["change_pct"], config)
            ))

        # Generate key themes
        key_themes = _generate_key_themes(movers_response)

        # Generate summary
        summary = _generate_weekly_summary(movers_response)

        return WeeklyReflectionResponse(
            week_ending=week_end.date().isoformat(),
            top_movers=movers_response,
            key_themes=key_themes,
            summary=summary
        )

    except Exception as e:
        logger.error(f"Error in get_weekly_reflection: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh/{metric_code}", response_model=RefreshMetricResponse)
async def refresh_metric(
    metric_code: str,
    request: RefreshMetricRequest,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually refresh a metric's data.

    Admin only. Fetches latest data from source and updates database.
    """
    try:
        # Validate metric
        config = get_metric_config(metric_code)
        if not config:
            raise HTTPException(status_code=404, detail=f"Metric {metric_code} not found")

        # Fetch fresh data
        fred_service = FREDService()

        try:
            # Fetch historical data (last year for now)
            result = await fred_service.fetch_historical(
                series_id=metric_code,
                use_cache=not request.force
            )

            data_points = result.get("data", [])

            # Store in database
            updated_count = 0
            for point in data_points:
                # Convert to our model format
                metric_point = MetricDataPoint(
                    metric_code=metric_code,
                    source=config["source"],
                    date=datetime.strptime(point["date"], "%Y-%m-%d"),
                    value=point["value"]
                )

                # Upsert
                db.add(metric_point)
                updated_count += 1

            await db.commit()

            await fred_service.close()

            return RefreshMetricResponse(
                status="success",
                metric_code=metric_code,
                data_points_updated=updated_count,
                message=f"Successfully refreshed {updated_count} data points for {metric_code}"
            )

        except Exception as e:
            await fred_service.close()
            raise e

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in refresh_metric: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


# ========== Helper Functions ==========

async def _get_current_metric_value(
    db: AsyncSession,
    fred_service: FREDService,
    code: str,
    target_date: datetime
) -> Optional[dict]:
    """Get current value for a metric."""
    try:
        # Try database first
        stmt = select(MetricDataPoint).where(
            MetricDataPoint.metric_code == code
        ).order_by(MetricDataPoint.date.desc()).limit(1)

        result = await db.execute(stmt)
        latest = result.scalar_one_or_none()

        if latest:
            return {"value": float(latest.value), "date": latest.date}

        # Fallback to FRED API
        result = await fred_service.fetch_historical(code, use_cache=True)
        if result and result.get("data"):
            latest_point = result["data"][-1]
            return {
                "value": latest_point["value"],
                "date": datetime.strptime(latest_point["date"], "%Y-%m-%d")
            }

        return None

    except Exception as e:
        logger.error(f"Error getting current value for {code}: {str(e)}")
        return None


async def _get_historical_data(
    db: AsyncSession,
    code: str,
    years: int = 5
) -> List[dict]:
    """Get historical data for a metric."""
    try:
        cutoff = datetime.now() - timedelta(days=years*365)

        stmt = select(MetricDataPoint).where(
            and_(
                MetricDataPoint.metric_code == code,
                MetricDataPoint.date >= cutoff
            )
        ).order_by(MetricDataPoint.date.asc())

        result = await db.execute(stmt)
        points = result.scalars().all()

        return [{"date": p.date, "value": float(p.value)} for p in points]

    except Exception as e:
        logger.error(f"Error getting historical data for {code}: {str(e)}")
        return []


def _generate_significance_text(change_pct: float, config: dict) -> str:
    """Generate significance text for a mover."""
    if abs(change_pct) > 10:
        return "Major movement - highest weekly change in months"
    elif abs(change_pct) > 5:
        return "Significant shift - notable weekly movement"
    else:
        return "Moderate change - worth monitoring"


def _generate_key_themes(movers: List[TopMover]) -> List[str]:
    """Generate key themes from top movers."""
    themes = []

    # Categorize by theme
    for mover in movers[:5]:
        if "Interest" in mover.category or "Fed" in mover.category:
            themes.append(f"{mover.category}: {mover.display_name} {mover.direction} {abs(mover.change_pct):.1f}%")
        elif "Housing" in mover.category or "Real Estate" in mover.category:
            themes.append(f"Housing: {mover.display_name} {mover.direction} {abs(mover.change_pct):.1f}%")

    return themes[:3] if themes else ["Markets showed mixed activity this week"]


def _generate_weekly_summary(movers: List[TopMover]) -> str:
    """Generate weekly summary text."""
    if not movers:
        return "Markets were relatively stable this week with no major movements."

    up_count = sum(1 for m in movers if m.direction == "up")
    down_count = sum(1 for m in movers if m.direction == "down")

    if up_count > down_count:
        return f"This week saw broadly positive momentum with {up_count} key indicators rising. Notable moves include {movers[0].display_name} and {movers[1].display_name if len(movers) > 1 else 'other indicators'}."
    elif down_count > up_count:
        return f"Markets showed weakness this week with {down_count} indicators declining. Key moves: {movers[0].display_name} and {movers[1].display_name if len(movers) > 1 else 'other indicators'}."
    else:
        return "Mixed signals this week with indicators moving in both directions. Key changes warrant continued monitoring."
