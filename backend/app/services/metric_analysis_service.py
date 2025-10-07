"""
Metric Analysis Service - Intelligence Layer.

This is the KEY differentiator for Today's Focus.
Transforms raw economic data into actionable insights with:
- Multi-period change detection (1D, 1W, 1M, 1Y)
- Statistical significance analysis (z-scores, percentiles, outliers)
- Contextual alerts ("Highest since 2007", "Trend reversal")
- Human-readable context summaries
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import numpy as np

logger = logging.getLogger(__name__)


class MetricAnalysisService:
    """
    Intelligence analysis service for economic metrics.

    Analyzes raw time-series data to generate insights, alerts,
    and context that help users understand what changed and why it matters.
    """

    async def analyze_metric(
        self,
        metric_code: str,
        current_value: float,
        current_date: datetime,
        historical_data: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive analysis for a metric.

        Args:
            metric_code: Metric identifier
            current_value: Latest value
            current_date: Date of current value
            historical_data: List of {"date": datetime, "value": float}

        Returns:
            Dict with analysis including changes, significance, alerts, context
        """
        try:
            # Calculate multi-period changes
            changes = await self.calculate_changes(
                current_value,
                current_date,
                historical_data
            )

            # Assess statistical significance
            significance = await self.assess_significance(
                current_value,
                historical_data
            )

            # Generate contextual alerts
            alerts = await self.generate_alerts(
                metric_code,
                current_value,
                current_date,
                historical_data,
                changes,
                significance
            )

            # Generate human-readable context
            context = await self.generate_context(
                metric_code,
                current_value,
                historical_data,
                changes,
                significance
            )

            return {
                "metric_code": metric_code,
                "current_value": current_value,
                "current_date": current_date.isoformat(),
                "changes": changes,
                "significance": significance,
                "alerts": alerts,
                "context": context
            }

        except Exception as e:
            logger.error(f"Error analyzing metric {metric_code}: {str(e)}")
            return {
                "metric_code": metric_code,
                "current_value": current_value,
                "current_date": current_date.isoformat(),
                "changes": {},
                "significance": {},
                "alerts": [],
                "context": "Analysis unavailable"
            }

    async def calculate_changes(
        self,
        current: float,
        current_date: datetime,
        historical: List[Dict]
    ) -> Dict:
        """
        Calculate percentage changes vs different time periods.

        Args:
            current: Current value
            current_date: Current date
            historical: Historical data points

        Returns:
            Dict with vs_yesterday, vs_last_week, vs_last_month, vs_last_year
        """
        changes = {
            "vs_yesterday": 0.0,
            "vs_last_week": 0.0,
            "vs_last_month": 0.0,
            "vs_last_year": 0.0
        }

        if not historical:
            return changes

        # Sort by date
        sorted_data = sorted(historical, key=lambda x: x["date"], reverse=True)

        # Calculate changes for each period
        for period_name, days in [
            ("vs_yesterday", 1),
            ("vs_last_week", 7),
            ("vs_last_month", 30),
            ("vs_last_year", 365)
        ]:
            target_date = current_date - timedelta(days=days)
            past_value = self._find_closest_value(target_date, sorted_data)

            if past_value is not None and past_value != 0:
                pct_change = ((current - past_value) / past_value) * 100
                changes[period_name] = round(pct_change, 2)

        return changes

    async def assess_significance(
        self,
        current: float,
        historical: List[Dict]
    ) -> Dict:
        """
        Assess statistical significance of current value.

        Args:
            current: Current value
            historical: Historical data points

        Returns:
            Dict with z_score, percentile, is_outlier, averages
        """
        if not historical or len(historical) < 2:
            return {
                "z_score": 0.0,
                "percentile": 50.0,
                "is_outlier": False,
                "avg_30d": current,
                "avg_90d": current,
                "avg_1y": current
            }

        values = np.array([d["value"] for d in historical])

        # Calculate basic statistics
        mean = np.mean(values)
        std = np.std(values)

        # Z-score (how many standard deviations from mean)
        z_score = (current - mean) / std if std > 0 else 0

        # Percentile rank
        percentile = (np.sum(values <= current) / len(values)) * 100

        # Outlier detection (|z-score| > 2)
        is_outlier = abs(z_score) > 2

        # Calculate rolling averages
        sorted_data = sorted(historical, key=lambda x: x["date"], reverse=True)
        avg_30d = self._calculate_average(sorted_data, days=30)
        avg_90d = self._calculate_average(sorted_data, days=90)
        avg_1y = self._calculate_average(sorted_data, days=365)

        return {
            "z_score": round(z_score, 2),
            "percentile": round(percentile, 1),
            "is_outlier": bool(is_outlier),
            "avg_30d": round(avg_30d, 2) if avg_30d else current,
            "avg_90d": round(avg_90d, 2) if avg_90d else current,
            "avg_1y": round(avg_1y, 2) if avg_1y else current
        }

    async def generate_alerts(
        self,
        metric_code: str,
        current: float,
        current_date: datetime,
        historical: List[Dict],
        changes: Dict,
        significance: Dict
    ) -> List[str]:
        """
        Generate contextual alerts for significant events.

        Args:
            metric_code: Metric code
            current: Current value
            current_date: Current date
            historical: Historical data
            changes: Change percentages
            significance: Statistical significance

        Returns:
            List of alert messages
        """
        alerts = []

        if not historical:
            return alerts

        values = [d["value"] for d in historical]
        dates = [d["date"] for d in historical]

        max_val = max(values)
        min_val = min(values)

        # All-time high/low alerts
        if current >= max_val:
            first_date = min(dates).year
            alerts.append(f"🔴 Highest level since {first_date}")
        elif current <= min_val:
            first_date = min(dates).year
            alerts.append(f"🔵 Lowest level since {first_date}")

        # Significant day-over-day movement
        if abs(changes.get("vs_yesterday", 0)) > 5:
            direction = "surge" if changes["vs_yesterday"] > 0 else "drop"
            alerts.append(
                f"⚡ Significant {direction}: {changes['vs_yesterday']:+.1f}% in 1 day"
            )

        # Trend reversal detection
        if await self._detect_trend_reversal(historical, current_date):
            alerts.append("🔄 Trend reversal detected")

        # Outlier alert
        if significance.get("is_outlier"):
            if significance["z_score"] > 2:
                alerts.append(f"📊 Unusually high (z-score: +{significance['z_score']:.1f})")
            elif significance["z_score"] < -2:
                alerts.append(f"📊 Unusually low (z-score: {significance['z_score']:.1f})")

        return alerts

    async def generate_context(
        self,
        metric_code: str,
        current: float,
        historical: List[Dict],
        changes: Dict,
        significance: Dict
    ) -> str:
        """
        Generate human-readable context summary.

        Args:
            metric_code: Metric code
            current: Current value
            historical: Historical data
            changes: Change percentages
            significance: Statistical significance

        Returns:
            Human-readable context string
        """
        parts = []

        # Position relative to recent averages
        percentile = significance.get("percentile", 50)
        if percentile > 75:
            parts.append(f"well above recent averages (top {100-percentile:.0f}%)")
        elif percentile < 25:
            parts.append(f"below recent averages (bottom {percentile:.0f}%)")
        else:
            parts.append("near recent averages")

        # Short-term trend
        week_change = changes.get("vs_last_week", 0)
        if week_change > 2:
            parts.append("trending upward")
        elif week_change < -2:
            parts.append("trending downward")
        elif abs(week_change) <= 0.5:
            parts.append("relatively stable")

        # Year-over-year comparison
        year_change = changes.get("vs_last_year", 0)
        if abs(year_change) > 10:
            direction = "up" if year_change > 0 else "down"
            parts.append(f"{abs(year_change):.1f}% {direction} vs last year")

        # Combine parts into coherent sentence
        if parts:
            context = ", ".join(parts).capitalize()
            if not context.endswith("."):
                context += "."
            return context
        else:
            return "No significant changes detected."

    async def _detect_trend_reversal(
        self,
        historical: List[Dict],
        current_date: datetime
    ) -> bool:
        """
        Detect trend reversal in recent data.

        Compares trend in last 3 days vs previous 7 days.

        Args:
            historical: Historical data points
            current_date: Current date

        Returns:
            True if trend reversal detected
        """
        if len(historical) < 10:
            return False

        try:
            # Sort by date
            sorted_data = sorted(historical, key=lambda x: x["date"], reverse=True)

            # Get last 10 days
            cutoff = current_date - timedelta(days=10)
            recent_data = [d for d in sorted_data if d["date"] >= cutoff]

            if len(recent_data) < 10:
                return False

            # Last 3 days
            last_3 = [d["value"] for d in recent_data[:3]]
            # Previous 7 days
            prev_7 = [d["value"] for d in recent_data[3:10]]

            # Calculate trend slopes
            recent_trend = np.polyfit(range(len(last_3)), last_3, 1)[0]
            prev_trend = np.polyfit(range(len(prev_7)), prev_7, 1)[0]

            # Reversal if slopes have opposite signs and are significant
            reversal = (
                (recent_trend > 0.1 and prev_trend < -0.1) or
                (recent_trend < -0.1 and prev_trend > 0.1)
            )

            return reversal

        except Exception as e:
            logger.warning(f"Error detecting trend reversal: {str(e)}")
            return False

    def _find_closest_value(
        self,
        target_date: datetime,
        sorted_data: List[Dict]
    ) -> Optional[float]:
        """
        Find value closest to target date.

        Args:
            target_date: Target date
            sorted_data: Data sorted by date (newest first)

        Returns:
            Closest value or None
        """
        if not sorted_data:
            return None

        # Find closest date
        closest = min(
            sorted_data,
            key=lambda x: abs((x["date"] - target_date).total_seconds())
        )

        # Only return if within reasonable range (7 days)
        if abs((closest["date"] - target_date).days) <= 7:
            return closest["value"]

        return None

    def _calculate_average(
        self,
        sorted_data: List[Dict],
        days: int
    ) -> Optional[float]:
        """
        Calculate average over last N days.

        Args:
            sorted_data: Data sorted by date (newest first)
            days: Number of days to average

        Returns:
            Average value or None
        """
        if not sorted_data:
            return None

        # Get data within the time window
        cutoff = sorted_data[0]["date"] - timedelta(days=days)
        recent = [d["value"] for d in sorted_data if d["date"] >= cutoff]

        if recent:
            return float(np.mean(recent))

        return None
