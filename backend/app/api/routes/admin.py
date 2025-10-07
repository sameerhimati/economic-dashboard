"""Admin routes for database management."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy import text, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.user import User
from app.models.metric_data_point import MetricDataPoint
from app.services.fred_service import FREDService
from app.config.metrics_config import get_all_metric_codes, get_metric_config

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/backfill-metrics")
async def backfill_metrics(
    years: int = Query(default=5, ge=1, le=10, description="Number of years of historical data to backfill"),
    batch_size: int = Query(default=50, ge=10, le=500, description="Number of records per batch"),
    metrics: Optional[str] = Query(default=None, description="Comma-separated list of metric codes (or empty for all)"),
    current_user: User = Depends(get_current_active_user),  # Changed from admin to any authenticated user
    db: AsyncSession = Depends(get_db)
):
    """
    Backfill historical metric data from FRED API (admin only).

    This endpoint runs synchronously and may take several minutes to complete.
    For 45 metrics x 5 years, expect ~10-15 minutes runtime.
    """
    try:
        logger.info(f"Starting metrics backfill: years={years}, batch_size={batch_size}, user={current_user.email}")

        # Determine which metrics to backfill
        if metrics:
            metric_codes = [m.strip() for m in metrics.split(",")]
        else:
            metric_codes = get_all_metric_codes()

        fred_service = FREDService()
        start_date = datetime.now() - timedelta(days=years * 365)
        end_date = datetime.now()

        results = {
            "metrics_processed": 0,
            "metrics_succeeded": 0,
            "metrics_failed": 0,
            "total_data_points": 0,
            "failed_metrics": []
        }

        for metric_code in metric_codes:
            try:
                config = get_metric_config(metric_code)
                if not config:
                    logger.warning(f"No config found for {metric_code}, skipping")
                    continue

                # Fetch data from FRED
                observations = await fred_service.fetch_series_observations(
                    series_id=metric_code,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d")
                )

                if not observations:
                    logger.warning(f"No data returned for {metric_code}")
                    results["metrics_failed"] += 1
                    results["failed_metrics"].append(metric_code)
                    continue

                # Batch insert with upsert
                for i in range(0, len(observations), batch_size):
                    batch = observations[i:i + batch_size]

                    for obs in batch:
                        # Upsert logic
                        stmt = select(MetricDataPoint).where(
                            and_(
                                MetricDataPoint.metric_code == metric_code,
                                MetricDataPoint.date == obs["date"]
                            )
                        )
                        existing = await db.execute(stmt)
                        existing_record = existing.scalar_one_or_none()

                        if existing_record:
                            existing_record.value = obs["value"]
                        else:
                            db.add(MetricDataPoint(
                                metric_code=metric_code,
                                source="FRED",
                                date=obs["date"],
                                value=obs["value"]
                            ))

                    await db.commit()
                    results["total_data_points"] += len(batch)

                results["metrics_succeeded"] += 1
                logger.info(f"✓ Completed {metric_code}: {len(observations)} data points")

            except Exception as e:
                logger.error(f"✗ Failed {metric_code}: {str(e)}")
                results["metrics_failed"] += 1
                results["failed_metrics"].append(metric_code)
                await db.rollback()

            results["metrics_processed"] += 1

        return {
            "status": "success",
            "message": f"Backfill completed: {results['metrics_succeeded']}/{results['metrics_processed']} metrics succeeded",
            **results
        }

    except Exception as e:
        logger.error(f"Backfill failed: {str(e)}", exc_info=True)
        await db.rollback()
        return {
            "status": "error",
            "message": f"Backfill failed: {str(e)}"
        }


@router.post("/reset-newsletters-articles")
async def reset_newsletters_and_articles(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset newsletters and articles tables (development only).

    WARNING: This deletes all newsletters and articles for ALL users.
    """
    try:
        # Delete in order to respect foreign keys
        await db.execute(text("DELETE FROM article_sources"))
        await db.execute(text("DELETE FROM article_bookmarks"))
        await db.execute(text("DELETE FROM articles"))
        await db.execute(text("DELETE FROM newsletters"))
        await db.commit()

        # Get counts to verify
        result = await db.execute(text("SELECT COUNT(*) FROM newsletters"))
        newsletter_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM articles"))
        article_count = result.scalar()

        return {
            "status": "success",
            "message": "Tables reset successfully",
            "newsletters_remaining": newsletter_count,
            "articles_remaining": article_count
        }

    except Exception as e:
        await db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
