"""
BLS (Bureau of Labor Statistics) API Service.

Handles interaction with the BLS API for unemployment and labor market data.
"""
import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BLSService:
    """
    Service for interacting with the Bureau of Labor Statistics API.

    Fetches unemployment rate, job openings, and other labor market data.
    """

    BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    # BLS Series IDs
    SERIES = {
        "UNEMPLOYMENT": "LNS14000000",  # Unemployment rate
        "NONFARM_PAYROLLS": "CES0000000001",  # Total nonfarm employment
        "JOB_OPENINGS": "JTS00000000JOL",  # Job openings (JOLTS)
    }

    def __init__(self):
        """Initialize BLS service."""
        self.api_key = getattr(settings, "BLS_API_KEY", None)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
        return False

    async def close(self):
        """Close HTTP client."""
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()

    async def fetch_series_data(
        self,
        series_id: str,
        years: int = 5
    ) -> List[Dict]:
        """
        Fetch data for a BLS series.

        Args:
            series_id: BLS series identifier
            years: Number of years of historical data

        Returns:
            List of data points with date and value
        """
        try:
            # Calculate year range
            end_year = datetime.now().year
            start_year = end_year - years

            # Build request payload
            payload = {
                "seriesid": [series_id],
                "startyear": str(start_year),
                "endyear": str(end_year)
            }

            # Add API key if available
            if self.api_key:
                payload["registrationkey"] = self.api_key

            # Make request
            response = await self.client.post(
                self.BASE_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            data = response.json()

            # Transform response
            return self._transform_bls_response(data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching BLS data for {series_id}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching BLS data for {series_id}: {str(e)}")
            return []

    def _transform_bls_response(self, response: Dict) -> List[Dict]:
        """
        Transform BLS API response to standard format.

        Args:
            response: BLS API response

        Returns:
            List of {"date": datetime, "value": float}
        """
        try:
            results = []

            if response.get("status") != "REQUEST_SUCCEEDED":
                logger.error(f"BLS API request failed: {response.get('message')}")
                return []

            series_data = response.get("Results", {}).get("series", [])

            if not series_data:
                return []

            data_points = series_data[0].get("data", [])

            for point in data_points:
                year = int(point.get("year", 0))
                period = point.get("period", "")

                # Parse period (M01-M12 for monthly, Q01-Q04 for quarterly)
                if period.startswith("M"):
                    month = int(period[1:])
                elif period.startswith("Q"):
                    quarter = int(period[1:])
                    month = (quarter - 1) * 3 + 1
                else:
                    continue

                # Parse value
                try:
                    value = float(point.get("value", 0))
                    date = datetime(year, month, 1)
                    results.append({"date": date, "value": value})
                except (ValueError, TypeError):
                    continue

            return sorted(results, key=lambda x: x["date"])

        except Exception as e:
            logger.error(f"Error transforming BLS response: {str(e)}")
            return []

    async def fetch_unemployment_rate(self, years: int = 5) -> List[Dict]:
        """
        Fetch unemployment rate data.

        Args:
            years: Number of years of historical data

        Returns:
            List of data points
        """
        return await self.fetch_series_data(self.SERIES["UNEMPLOYMENT"], years)

    async def fetch_job_openings(self, years: int = 5) -> List[Dict]:
        """
        Fetch job openings data.

        Args:
            years: Number of years of historical data

        Returns:
            List of data points
        """
        return await self.fetch_series_data(self.SERIES["JOB_OPENINGS"], years)

    async def fetch_latest_unemployment(self) -> Optional[Dict]:
        """
        Fetch the latest unemployment rate.

        Returns:
            Dict with date and value, or None
        """
        data = await self.fetch_unemployment_rate(years=1)
        return data[-1] if data else None
