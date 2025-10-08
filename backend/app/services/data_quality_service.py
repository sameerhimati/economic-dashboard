"""
Data quality monitoring service.
Checks for stale data, gaps, and other data quality issues.
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.models.metric_data_point import MetricDataPoint
from app.config.metrics_config import get_all_metric_configs

logger = logging.getLogger(__name__)


class DataQualityService:
    """
    Service for monitoring data quality.

    Checks metrics for:
    - Staleness (data not updated recently)
    - Missing data
    - Data gaps
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize data quality service.

        Args:
            db: Database session
        """
        self.db = db

    async def check_metric_freshness(self, metric_code: str) -> Dict:
        """
        Check if metric was updated recently.

        Args:
            metric_code: Metric code to check

        Returns:
            Dict with freshness status and details
        """
        try:
            query = select(
                MetricDataPoint.date,
                MetricDataPoint.created_at
            ).where(
                MetricDataPoint.metric_code == metric_code
            ).order_by(MetricDataPoint.date.desc()).limit(1)

            result = await self.db.execute(query)
            latest = result.first()

            if not latest:
                return {
                    "metric_code": metric_code,
                    "status": "error",
                    "message": "No data found"
                }

            # Check if data is stale (> 7 days old)
            age = datetime.now() - latest.created_at
            is_stale = age > timedelta(days=7)

            return {
                "metric_code": metric_code,
                "status": "stale" if is_stale else "fresh",
                "last_date": latest.date.isoformat(),
                "last_updated": latest.created_at.isoformat(),
                "age_hours": round(age.total_seconds() / 3600, 2)
            }

        except Exception as e:
            logger.error(f"Error checking freshness for {metric_code}: {str(e)}", exc_info=True)
            return {
                "metric_code": metric_code,
                "status": "error",
                "message": str(e)
            }

    async def check_data_gaps(self, metric_code: str, days_to_check: int = 30) -> Dict:
        """
        Check for gaps in data over the last N days.

        Args:
            metric_code: Metric code to check
            days_to_check: Number of days to check for gaps

        Returns:
            Dict with gap analysis
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_check)

            query = select(MetricDataPoint.date).where(
                MetricDataPoint.metric_code == metric_code,
                MetricDataPoint.date >= cutoff_date
            ).order_by(MetricDataPoint.date.asc())

            result = await self.db.execute(query)
            dates = [row[0] for row in result.all()]

            if not dates:
                return {
                    "metric_code": metric_code,
                    "has_gaps": False,
                    "gaps": [],
                    "data_points": 0
                }

            # Find gaps (more than 1 day between consecutive dates)
            gaps = []
            for i in range(len(dates) - 1):
                current_date = dates[i]
                next_date = dates[i + 1]
                gap_days = (next_date - current_date).days

                if gap_days > 1:
                    gaps.append({
                        "start": current_date.isoformat(),
                        "end": next_date.isoformat(),
                        "days": gap_days
                    })

            return {
                "metric_code": metric_code,
                "has_gaps": len(gaps) > 0,
                "gaps": gaps,
                "data_points": len(dates),
                "checked_days": days_to_check
            }

        except Exception as e:
            logger.error(f"Error checking gaps for {metric_code}: {str(e)}", exc_info=True)
            return {
                "metric_code": metric_code,
                "has_gaps": False,
                "gaps": [],
                "error": str(e)
            }

    async def get_metric_statistics(self, metric_code: str) -> Dict:
        """
        Get basic statistics for a metric.

        Args:
            metric_code: Metric code to analyze

        Returns:
            Dict with statistics
        """
        try:
            query = select(
                func.count(MetricDataPoint.id).label('count'),
                func.min(MetricDataPoint.date).label('first_date'),
                func.max(MetricDataPoint.date).label('last_date'),
                func.min(MetricDataPoint.value).label('min_value'),
                func.max(MetricDataPoint.value).label('max_value'),
                func.avg(MetricDataPoint.value).label('avg_value')
            ).where(
                MetricDataPoint.metric_code == metric_code
            )

            result = await self.db.execute(query)
            stats = result.first()

            if not stats or stats.count == 0:
                return {
                    "metric_code": metric_code,
                    "status": "no_data"
                }

            return {
                "metric_code": metric_code,
                "count": stats.count,
                "first_date": stats.first_date.isoformat() if stats.first_date else None,
                "last_date": stats.last_date.isoformat() if stats.last_date else None,
                "min_value": float(stats.min_value) if stats.min_value else None,
                "max_value": float(stats.max_value) if stats.max_value else None,
                "avg_value": float(stats.avg_value) if stats.avg_value else None
            }

        except Exception as e:
            logger.error(f"Error getting statistics for {metric_code}: {str(e)}", exc_info=True)
            return {
                "metric_code": metric_code,
                "status": "error",
                "error": str(e)
            }

    async def run_all_checks(self) -> Dict:
        """
        Run all quality checks on all metrics.

        Returns:
            Dict with comprehensive quality report
        """
        configs = get_all_metric_configs()

        logger.info(f"Running quality checks on {len(configs)} metrics")

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_metrics": len(configs),
            "checks": []
        }

        for config in configs:
            metric_code = config["code"]

            try:
                # Check freshness
                freshness = await self.check_metric_freshness(metric_code)

                # Check for gaps
                gaps = await self.check_data_gaps(metric_code, days_to_check=30)

                # Get statistics
                stats = await self.get_metric_statistics(metric_code)

                # Determine if there are issues
                has_issues = (
                    freshness["status"] == "stale" or
                    freshness["status"] == "error" or
                    gaps.get("has_gaps", False)
                )

                report["checks"].append({
                    "metric_code": metric_code,
                    "display_name": config.get("display_name", metric_code),
                    "freshness": freshness,
                    "gaps": gaps,
                    "statistics": stats,
                    "has_issues": has_issues
                })

            except Exception as e:
                logger.error(f"Error checking {metric_code}: {str(e)}", exc_info=True)
                report["checks"].append({
                    "metric_code": metric_code,
                    "display_name": config.get("display_name", metric_code),
                    "has_issues": True,
                    "error": str(e)
                })

        # Count total issues
        issues_count = sum(1 for c in report["checks"] if c.get("has_issues", False))
        report["issues_count"] = issues_count

        logger.info(f"Quality check complete: {issues_count} metrics with issues")

        return report

    async def get_stale_metrics(self, hours: int = 168) -> List[Dict]:
        """
        Get metrics that haven't been updated in N hours.

        Args:
            hours: Number of hours to consider stale (default: 168 = 1 week)

        Returns:
            List of stale metrics with details
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        try:
            # Get latest update time for each metric
            query = select(
                MetricDataPoint.metric_code,
                func.max(MetricDataPoint.created_at).label('last_update')
            ).group_by(
                MetricDataPoint.metric_code
            ).having(
                func.max(MetricDataPoint.created_at) < cutoff_time
            )

            result = await self.db.execute(query)
            stale_metrics = result.all()

            stale_list = []
            for metric in stale_metrics:
                config = next(
                    (c for c in get_all_metric_configs() if c["code"] == metric.metric_code),
                    None
                )

                stale_list.append({
                    "metric_code": metric.metric_code,
                    "display_name": config.get("display_name", metric.metric_code) if config else metric.metric_code,
                    "last_update": metric.last_update.isoformat(),
                    "hours_stale": round((datetime.now() - metric.last_update).total_seconds() / 3600, 2)
                })

            return stale_list

        except Exception as e:
            logger.error(f"Error getting stale metrics: {str(e)}", exc_info=True)
            return []
