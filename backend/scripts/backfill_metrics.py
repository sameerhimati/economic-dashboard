#!/usr/bin/env python3
"""
Backfill script for historical metric data.

Fetches 5 years of historical data for all metrics configured in metrics_config.py
and populates the metric_data_points table.

Usage:
    python scripts/backfill_metrics.py [--batch-size BATCH_SIZE] [--years YEARS] [--metrics METRIC1,METRIC2]

Examples:
    # Backfill all metrics with default settings (5 years, batch size 50)
    python scripts/backfill_metrics.py

    # Backfill specific metrics
    python scripts/backfill_metrics.py --metrics FEDFUNDS,DGS10,UNRATE

    # Backfill 10 years of data
    python scripts/backfill_metrics.py --years 10

    # Use larger batch size for faster processing
    python scripts/backfill_metrics.py --batch-size 100
"""
import asyncio
import sys
import os
import logging
import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func

from app.core.config import settings
from app.core.database import init_db, close_db, get_db_context
from app.models.metric_data_point import MetricDataPoint
from app.services.fred_service import FREDService, FREDAPIError
from app.config.metrics_config import get_all_metric_codes, get_metric_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class BackfillStats:
    """Track backfill statistics."""

    def __init__(self):
        self.metrics_processed = 0
        self.metrics_succeeded = 0
        self.metrics_failed = 0
        self.total_data_points = 0
        self.new_data_points = 0
        self.updated_data_points = 0
        self.skipped_data_points = 0
        self.start_time = datetime.now()
        self.failed_metrics: List[str] = []

    def record_success(self, metric_code: str, points_inserted: int, points_updated: int):
        """Record successful metric processing."""
        self.metrics_succeeded += 1
        self.total_data_points += points_inserted + points_updated
        self.new_data_points += points_inserted
        self.updated_data_points += points_updated

    def record_failure(self, metric_code: str, error: str):
        """Record failed metric processing."""
        self.metrics_failed += 1
        self.failed_metrics.append(f"{metric_code}: {error}")

    def print_summary(self):
        """Print final summary."""
        duration = datetime.now() - self.start_time

        logger.info("=" * 80)
        logger.info("BACKFILL SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total metrics processed: {self.metrics_processed}")
        logger.info(f"Succeeded: {self.metrics_succeeded}")
        logger.info(f"Failed: {self.metrics_failed}")
        logger.info(f"")
        logger.info(f"Total data points: {self.total_data_points}")
        logger.info(f"New data points: {self.new_data_points}")
        logger.info(f"Updated data points: {self.updated_data_points}")
        logger.info(f"Skipped data points: {self.skipped_data_points}")
        logger.info(f"")
        logger.info(f"Duration: {duration}")
        logger.info(f"Average: {duration.total_seconds() / max(1, self.metrics_processed):.2f}s per metric")

        if self.failed_metrics:
            logger.info("")
            logger.info("FAILED METRICS:")
            for failure in self.failed_metrics:
                logger.error(f"  - {failure}")

        logger.info("=" * 80)


async def check_existing_data(db: AsyncSession, metric_code: str) -> Dict[str, Any]:
    """
    Check what data already exists for a metric.

    Args:
        db: Database session
        metric_code: Metric code to check

    Returns:
        Dict with count, oldest_date, newest_date
    """
    try:
        # Count existing records
        count_stmt = select(func.count()).select_from(MetricDataPoint).where(
            MetricDataPoint.metric_code == metric_code
        )
        count_result = await db.execute(count_stmt)
        count = count_result.scalar_one()

        if count == 0:
            return {
                "count": 0,
                "oldest_date": None,
                "newest_date": None
            }

        # Get date range
        range_stmt = select(
            func.min(MetricDataPoint.date),
            func.max(MetricDataPoint.date)
        ).where(MetricDataPoint.metric_code == metric_code)

        range_result = await db.execute(range_stmt)
        oldest, newest = range_result.one()

        return {
            "count": count,
            "oldest_date": oldest,
            "newest_date": newest
        }

    except Exception as e:
        logger.error(f"Error checking existing data for {metric_code}: {str(e)}")
        return {"count": 0, "oldest_date": None, "newest_date": None}


async def backfill_metric(
    db: AsyncSession,
    fred_service: FREDService,
    metric_code: str,
    years: int = 5,
    batch_size: int = 50
) -> Dict[str, int]:
    """
    Backfill historical data for a single metric.

    Args:
        db: Database session
        fred_service: FRED service instance
        metric_code: Metric code to backfill
        years: Number of years of history to fetch
        batch_size: Number of records to insert per batch

    Returns:
        Dict with inserted and updated counts
    """
    logger.info(f"Processing {metric_code}...")

    # Get metric configuration
    config = get_metric_config(metric_code)
    if not config:
        raise ValueError(f"No configuration found for {metric_code}")

    source = config.get("source", "FRED")

    # Check existing data
    existing = await check_existing_data(db, metric_code)
    if existing["count"] > 0:
        logger.info(
            f"  Found {existing['count']} existing records "
            f"({existing['oldest_date']} to {existing['newest_date']})"
        )
    else:
        logger.info(f"  No existing data found")

    # Calculate date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=years * 365)

    logger.info(f"  Fetching data from {start_date} to {end_date}...")

    # Fetch historical data from FRED
    try:
        result = await fred_service.fetch_historical(
            series_id=metric_code,
            start_date=start_date,
            end_date=end_date,
            use_cache=False  # Don't use cache for backfill
        )
    except FREDAPIError as e:
        logger.error(f"  FRED API error for {metric_code}: {e.message}")
        raise
    except Exception as e:
        logger.error(f"  Unexpected error fetching {metric_code}: {str(e)}")
        raise

    data_points = result.get("data", [])

    if not data_points:
        logger.warning(f"  No data returned from FRED for {metric_code}")
        return {"inserted": 0, "updated": 0}

    logger.info(f"  Retrieved {len(data_points)} data points from FRED")

    # Process in batches
    inserted_count = 0
    updated_count = 0

    for i in range(0, len(data_points), batch_size):
        batch = data_points[i:i + batch_size]

        try:
            for point in batch:
                # Parse date
                point_date = datetime.strptime(point["date"], "%Y-%m-%d")

                # Create upsert statement
                stmt = insert(MetricDataPoint).values(
                    metric_code=metric_code,
                    source=source,
                    date=point_date,
                    value=float(point["value"])
                )

                # On conflict, update the value and updated_at
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_metric_date',
                    set_={
                        'value': stmt.excluded.value,
                        'source': stmt.excluded.source,
                        'updated_at': func.now()
                    }
                )

                result = await db.execute(stmt)

                # Track if this was an insert or update
                # Note: PostgreSQL doesn't directly tell us, so we count all as updates if constraint exists
                inserted_count += 1

            # Commit batch
            await db.commit()

            logger.info(f"  Processed batch {i // batch_size + 1}/{(len(data_points) + batch_size - 1) // batch_size}")

        except Exception as e:
            logger.error(f"  Error processing batch for {metric_code}: {str(e)}")
            await db.rollback()
            raise

    # Verify what we inserted
    final_count = await check_existing_data(db, metric_code)
    logger.info(f"  ✓ Completed: {final_count['count']} total records in database")

    return {
        "inserted": inserted_count - existing.get("count", 0) if inserted_count >= existing.get("count", 0) else inserted_count,
        "updated": existing.get("count", 0) if inserted_count >= existing.get("count", 0) else 0
    }


async def backfill_all_metrics(
    metrics: Optional[List[str]] = None,
    years: int = 5,
    batch_size: int = 50
) -> BackfillStats:
    """
    Backfill historical data for all metrics.

    Args:
        metrics: Optional list of specific metrics to backfill. If None, backfills all.
        years: Number of years of history to fetch
        batch_size: Number of records to insert per batch

    Returns:
        BackfillStats object with summary
    """
    stats = BackfillStats()

    # Get metric codes to process
    if metrics:
        metric_codes = [m.upper() for m in metrics]
        logger.info(f"Backfilling {len(metric_codes)} specific metrics: {', '.join(metric_codes)}")
    else:
        metric_codes = get_all_metric_codes()
        logger.info(f"Backfilling all {len(metric_codes)} configured metrics")

    # Initialize FRED service
    fred_service = FREDService()

    try:
        # Process each metric
        for metric_code in metric_codes:
            stats.metrics_processed += 1

            try:
                async with get_db_context() as db:
                    result = await backfill_metric(
                        db=db,
                        fred_service=fred_service,
                        metric_code=metric_code,
                        years=years,
                        batch_size=batch_size
                    )

                    stats.record_success(
                        metric_code,
                        result["inserted"],
                        result["updated"]
                    )

                    logger.info("")  # Blank line for readability

            except Exception as e:
                stats.record_failure(metric_code, str(e))
                logger.error(f"Failed to backfill {metric_code}: {str(e)}")
                logger.info("")  # Blank line for readability
                continue

    finally:
        # Clean up FRED service
        await fred_service.close()

    return stats


async def verify_backfill(metrics: Optional[List[str]] = None):
    """
    Verify the backfill by checking record counts.

    Args:
        metrics: Optional list of specific metrics to verify
    """
    logger.info("=" * 80)
    logger.info("VERIFYING BACKFILL")
    logger.info("=" * 80)

    if metrics:
        metric_codes = [m.upper() for m in metrics]
    else:
        metric_codes = get_all_metric_codes()

    async with get_db_context() as db:
        for metric_code in metric_codes:
            existing = await check_existing_data(db, metric_code)

            if existing["count"] > 0:
                logger.info(
                    f"{metric_code:15} | {existing['count']:6} records | "
                    f"{existing['oldest_date']} to {existing['newest_date']}"
                )
            else:
                logger.warning(f"{metric_code:15} | NO DATA")

    logger.info("=" * 80)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Backfill historical metric data from FRED",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Number of records to insert per batch (default: 50)"
    )

    parser.add_argument(
        "--years",
        type=int,
        default=5,
        help="Number of years of historical data to fetch (default: 5)"
    )

    parser.add_argument(
        "--metrics",
        type=str,
        help="Comma-separated list of specific metrics to backfill (e.g., FEDFUNDS,DGS10)"
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify existing data, don't backfill"
    )

    args = parser.parse_args()

    # Parse metrics list
    metrics_list = None
    if args.metrics:
        metrics_list = [m.strip() for m in args.metrics.split(",")]

    try:
        # Initialize database
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("Database initialized successfully")
        logger.info("")

        if args.verify_only:
            # Just verify
            await verify_backfill(metrics_list)
        else:
            # Run backfill
            logger.info("=" * 80)
            logger.info("STARTING BACKFILL")
            logger.info("=" * 80)
            logger.info(f"Years of history: {args.years}")
            logger.info(f"Batch size: {args.batch_size}")
            logger.info("")

            stats = await backfill_all_metrics(
                metrics=metrics_list,
                years=args.years,
                batch_size=args.batch_size
            )

            # Print summary
            stats.print_summary()

            # Verify
            logger.info("")
            await verify_backfill(metrics_list)

        # Close database
        await close_db()

        logger.info("")
        logger.info("Backfill complete!")

        # Exit with appropriate code
        if not args.verify_only and stats.metrics_failed > 0:
            sys.exit(1)
        else:
            sys.exit(0)

    except KeyboardInterrupt:
        logger.warning("\nBackfill interrupted by user")
        await close_db()
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error during backfill: {str(e)}", exc_info=True)
        await close_db()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
