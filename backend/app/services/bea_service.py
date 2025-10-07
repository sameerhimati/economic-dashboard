"""
BEA (Bureau of Economic Analysis) API Service.

Handles interaction with the BEA API for GDP and related economic data.
"""
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class BEAService:
    """
    Service for interacting with the Bureau of Economic Analysis API.

    Fetches GDP and other economic indicators.
    """

    BASE_URL = "https://apps.bea.gov/api/data"

    def __init__(self):
        """Initialize BEA service."""
        self.api_key = getattr(settings, "BEA_API_KEY", None)
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

    async def fetch_gdp_data(
        self,
        years: int = 5
    ) -> List[Dict]:
        """
        Fetch GDP quarterly data.

        Args:
            years: Number of years of historical data

        Returns:
            List of data points with date and value
        """
        if not self.api_key:
            logger.warning("BEA_API_KEY not configured")
            return []

        try:
            # Calculate year range
            end_year = datetime.now().year
            start_year = end_year - years

            # BEA API parameters for real GDP
            params = {
                "UserID": self.api_key,
                "method": "GetData",
                "datasetname": "NIPA",
                "TableName": "T10101",  # Real GDP table
                "Frequency": "Q",  # Quarterly
                "Year": "ALL",
                "ResultFormat": "JSON",
            }

            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()

            data = response.json()

            # Transform BEA response
            return self._transform_bea_response(data, start_year, end_year)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching BEA data: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching BEA data: {str(e)}")
            return []

    def _transform_bea_response(
        self,
        response: Dict,
        start_year: int,
        end_year: int
    ) -> List[Dict]:
        """
        Transform BEA API response to standard format.

        Args:
            response: BEA API response
            start_year: Start year filter
            end_year: End year filter

        Returns:
            List of {"date": datetime, "value": float}
        """
        try:
            results = []
            beadata = response.get("BEAAPI", {}).get("Results", {}).get("Data", [])

            for item in beadata:
                year = int(item.get("Year", 0))
                if year < start_year or year > end_year:
                    continue

                # Parse quarter (Q1, Q2, Q3, Q4)
                time_period = item.get("TimePeriod", "")
                if not time_period or len(time_period) < 2:
                    continue

                quarter = int(time_period[-1])
                month = (quarter - 1) * 3 + 1  # Q1->Jan, Q2->Apr, Q3->Jul, Q4->Oct

                # Parse value
                data_value = item.get("DataValue", "")
                if not data_value or data_value == "...":
                    continue

                try:
                    value = float(data_value.replace(",", ""))
                    date = datetime(year, month, 1)
                    results.append({"date": date, "value": value})
                except (ValueError, TypeError):
                    continue

            return sorted(results, key=lambda x: x["date"])

        except Exception as e:
            logger.error(f"Error transforming BEA response: {str(e)}")
            return []

    async def fetch_latest_gdp(self) -> Optional[Dict]:
        """
        Fetch the latest GDP value.

        Returns:
            Dict with date and value, or None
        """
        data = await self.fetch_gdp_data(years=1)
        return data[-1] if data else None
