"""
Incremental update service for refreshing metric data.
Fetches only new data since last update.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from typing import Optional, Dict
from decimal import Decimal

from app.models.metric_data_point import MetricDataPoint
from app.services.fred_service import FREDService
from app.config.metrics_config import get_all_metric_configs

logger = logging.getLogger(__name__)


class IncrementalUpdateService:
    """
    Service for incrementally updating metric data.

    Fetches only new data points since the last update to minimize
    API calls and database operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize incremental update service.

        Args:
            db: Database session
        """
        self.db = db
        self.fred = FREDService()

    async def update_metric_since_last(self, metric_code: str) -> Dict:
        """
        Update metric data since last stored date.

        Args:
            metric_code: FRED series code to update

        Returns:
            Dict with status, count, and message
        """
        try:
            # Get last stored date
            last_date = await self._get_last_date(metric_code)

            if not last_date:
                logger.info(f"No existing data for {metric_code}, fetching last year")
                last_date = datetime.now() - timedelta(days=365)  # Default to 1 year

            # Fetch new data from FRED
            logger.info(f"Fetching {metric_code} from {last_date} to now")

            result = await self.fred.fetch_historical(
                series_id=metric_code,
                use_cache=False
            )

            if not result or not result.get("data"):
                return {
                    "status": "error",
                    "error": "No data returned from FRED",
                    "count": 0
                }

            # Filter to only new data points
            all_data = result["data"]
            new_data = [
                point for point in all_data
                if datetime.strptime(point["date"], "%Y-%m-%d") > last_date
            ]

            if not new_data:
                logger.info(f"No new data for {metric_code}")
                return {
                    "status": "success",
                    "count": 0,
                    "message": "Already up to date"
                }

            # Store new data points
            stored_count = 0
            for point in new_data:
                try:
                    dp = MetricDataPoint(
                        metric_code=metric_code,
                        source="FRED",
                        date=datetime.strptime(point["date"], "%Y-%m-%d"),
                        value=Decimal(str(point["value"]))
                    )

                    self.db.add(dp)
                    stored_count += 1

                except Exception as e:
                    logger.error(f"Error storing data point for {metric_code}: {str(e)}")
                    continue

            await self.db.commit()

            logger.info(f"Stored {stored_count} new data points for {metric_code}")

            return {
                "status": "success",
                "count": stored_count,
                "message": f"Added {stored_count} new data points"
            }

        except Exception as e:
            logger.error(f"Error updating {metric_code}: {str(e)}", exc_info=True)
            await self.db.rollback()
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }

    async def update_all_metrics(self) -> Dict[str, Dict]:
        """
        Update all active metrics incrementally.

        Returns:
            Dict mapping metric codes to update results
        """
        configs = get_all_metric_configs()

        logger.info(f"Updating {len(configs)} metrics incrementally")

        results = {}
        for config in configs:
            metric_code = config["code"]
            try:
                result = await self.update_metric_since_last(metric_code)
                results[metric_code] = result

            except Exception as e:
                logger.error(f"Failed to update {metric_code}: {str(e)}", exc_info=True)
                results[metric_code] = {
                    "status": "error",
                    "error": str(e),
                    "count": 0
                }

        # Close FRED service
        await self.fred.close()

        return results

    async def _get_last_date(self, metric_code: str) -> Optional[datetime]:
        """
        Get the most recent date for a metric.

        Args:
            metric_code: Metric code to check

        Returns:
            Most recent date or None if no data exists
        """
        try:
            query = select(MetricDataPoint.date).where(
                MetricDataPoint.metric_code == metric_code
            ).order_by(desc(MetricDataPoint.date)).limit(1)

            result = await self.db.execute(query)
            last_date = result.scalar_one_or_none()

            return last_date

        except Exception as e:
            logger.error(f"Error getting last date for {metric_code}: {str(e)}", exc_info=True)
            return None
