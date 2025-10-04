"""
FRED API service with production-ready features.

Handles interaction with the Federal Reserve Economic Data (FRED) API
with comprehensive rate limiting, retry logic, caching, and error handling.
"""
import logging
import json
import asyncio
import time
from datetime import date, datetime, timezone
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode
from decimal import Decimal

import httpx
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.core.config import settings
from app.core.database import get_redis, get_db_context
from app.models.fred_data import FredDataPoint

# Configure logging
logger = logging.getLogger(__name__)


# Series metadata mapping
SERIES_METADATA = {
    "DFF": {
        "name": "Federal Funds Rate",
        "unit": "Percent"
    },
    "DGS10": {
        "name": "10-Year Treasury Constant Maturity Rate",
        "unit": "Percent"
    },
    "UNRATE": {
        "name": "Unemployment Rate",
        "unit": "Percent"
    },
    "CPIAUCSL": {
        "name": "Consumer Price Index for All Urban Consumers",
        "unit": "Index 1982-1984=100"
    },
    "MORTGAGE30US": {
        "name": "30-Year Fixed Rate Mortgage Average",
        "unit": "Percent"
    }
}


class FREDAPIError(Exception):
    """Custom exception for FRED API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        super().__init__(self.message)


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Implements a sliding window rate limiting algorithm to ensure
    we stay within FRED API rate limits (120 requests per minute).
    """

    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: List[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Blocks until a request slot is available within the rate limit.
        """
        async with self._lock:
            now = time.time()

            # Remove requests outside the current window
            self.requests = [req_time for req_time in self.requests
                           if now - req_time < self.window_seconds]

            # Check if we're at the limit
            if len(self.requests) >= self.max_requests:
                # Calculate sleep time until oldest request expires
                oldest_request = self.requests[0]
                sleep_time = self.window_seconds - (now - oldest_request) + 0.1  # Add 100ms buffer

                logger.warning(
                    f"Rate limit reached ({len(self.requests)}/{self.max_requests}). "
                    f"Sleeping for {sleep_time:.2f} seconds"
                )

                await asyncio.sleep(sleep_time)

                # Recursively try again
                return await self.acquire()

            # Add current request
            self.requests.append(now)
            logger.debug(
                f"Rate limiter: {len(self.requests)}/{self.max_requests} requests in current window"
            )


class FREDService:
    """
    Production-ready service for interacting with the FRED API.

    Features:
    - Rate limiting (120 requests/minute)
    - Exponential backoff retry logic
    - Redis caching with configurable TTL
    - PostgreSQL storage with upsert logic
    - Comprehensive error handling and logging
    - Context manager support for proper resource cleanup
    """

    def __init__(self, redis_client: Optional[Redis] = None, db_session: Optional[AsyncSession] = None):
        """
        Initialize FRED service.

        Args:
            redis_client: Optional Redis client for caching
            db_session: Optional database session for storage
        """
        self.api_key = settings.FRED_API_KEY
        self.base_url = settings.FRED_API_BASE_URL
        self.timeout = settings.FRED_API_TIMEOUT

        # Get Redis client
        try:
            self.redis = redis_client if redis_client else get_redis()
        except Exception as e:
            logger.warning(f"Redis not available for FRED service: {str(e)}")
            self.redis = None

        # Database session
        self.db_session = db_session

        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_requests=settings.FRED_RATE_LIMIT_PER_MINUTE,
            window_seconds=60
        )

        # HTTP client for making requests
        self.client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        )

    async def __aenter__(self):
        """Context manager entry - returns self."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures client is closed."""
        await self.close()
        return False  # Don't suppress exceptions

    async def close(self):
        """Close the HTTP client."""
        if hasattr(self, 'client') and self.client is not None:
            await self.client.aclose()

    def _get_cache_key(self, cache_type: str, series_id: Optional[str] = None, **kwargs) -> str:
        """
        Generate cache key for request.

        Args:
            cache_type: Type of cache ('current', 'historical')
            series_id: Optional series ID
            **kwargs: Additional parameters for the cache key

        Returns:
            str: Cache key
        """
        if cache_type == "current" and series_id:
            return f"fred:current:{series_id}"
        elif cache_type == "historical" and series_id:
            start = kwargs.get('start_date', '')
            end = kwargs.get('end_date', '')
            return f"fred:historical:{series_id}:{start}:{end}"
        elif cache_type == "all_current":
            return "fred:current:all"
        else:
            # Fallback to generic key
            param_str = urlencode(sorted(kwargs.items()))
            return f"fred:{cache_type}:{param_str}"

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Get data from Redis cache.

        Args:
            cache_key: Cache key

        Returns:
            Optional[Dict]: Cached data or None
        """
        if self.redis is None:
            return None

        try:
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                data = json.loads(cached_data)

                # Add cache metadata
                ttl = await self.redis.ttl(cache_key)
                data["_cache_metadata"] = {
                    "cached": True,
                    "cache_expires_in": ttl if ttl > 0 else 0
                }

                return data
        except RedisError as e:
            logger.warning(f"Redis error getting cache: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding cached data: {str(e)}")

        return None

    async def _set_cache(self, cache_key: str, data: Dict, ttl: int) -> None:
        """
        Store data in Redis cache.

        Args:
            cache_key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
        """
        if self.redis is None:
            return

        try:
            await self.redis.setex(
                cache_key,
                ttl,
                json.dumps(data, default=str)
            )
            logger.debug(f"Cached data with key: {cache_key} (TTL: {ttl}s)")
        except RedisError as e:
            logger.warning(f"Redis error setting cache: {str(e)}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error encoding data for cache: {str(e)}")

    async def _invalidate_cache_pattern(self, pattern: str) -> int:
        """
        Invalidate cache keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., 'fred:current:*')

        Returns:
            int: Number of keys deleted
        """
        if self.redis is None:
            return 0

        try:
            deleted = 0
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)
                deleted += 1

            if deleted > 0:
                logger.info(f"Invalidated {deleted} cache keys matching pattern: {pattern}")

            return deleted
        except RedisError as e:
            logger.error(f"Error invalidating cache: {str(e)}")
            return 0

    async def _make_request_with_retry(
        self,
        endpoint: str,
        params: Dict[str, Any],
        max_retries: int = 3
    ) -> Dict:
        """
        Make HTTP request to FRED API with exponential backoff retry logic.

        Args:
            endpoint: API endpoint (e.g., 'series/observations')
            params: Query parameters
            max_retries: Maximum number of retry attempts

        Returns:
            Dict: API response data

        Raises:
            FREDAPIError: If request fails after all retries
        """
        # Add API key and file type to params
        request_params = {
            **params,
            "api_key": self.api_key,
            "file_type": "json"
        }

        url = f"{self.base_url}/{endpoint}"

        for attempt in range(max_retries + 1):
            try:
                # Acquire rate limit token
                await self.rate_limiter.acquire()

                logger.info(
                    f"Making FRED API request (attempt {attempt + 1}/{max_retries + 1}): {endpoint}"
                )
                logger.debug(f"Request params: {request_params}")

                response = await self.client.get(url, params=request_params)

                # Check for rate limit (429) - always retry
                if response.status_code == 429:
                    if attempt < max_retries:
                        sleep_time = (2 ** attempt) + 1  # Exponential backoff: 1, 3, 5 seconds
                        logger.warning(
                            f"Rate limited by FRED API (429). "
                            f"Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(sleep_time)
                        continue
                    else:
                        raise FREDAPIError(
                            message="Rate limited by FRED API after all retries",
                            status_code=429
                        )

                # Check for server errors (5xx) - retry
                if 500 <= response.status_code < 600:
                    if attempt < max_retries:
                        sleep_time = (2 ** attempt) + 1
                        logger.warning(
                            f"FRED API server error ({response.status_code}). "
                            f"Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})"
                        )
                        await asyncio.sleep(sleep_time)
                        continue
                    else:
                        raise FREDAPIError(
                            message=f"FRED API server error after all retries: {response.status_code}",
                            status_code=response.status_code
                        )

                # Check for client errors (4xx) - don't retry (except 429 handled above)
                if 400 <= response.status_code < 500:
                    error_detail = response.text
                    logger.error(
                        f"FRED API client error: status={response.status_code}, detail={error_detail}"
                    )
                    raise FREDAPIError(
                        message=f"FRED API request failed: {error_detail}",
                        status_code=response.status_code,
                        response_data={"detail": error_detail}
                    )

                # Check for success
                if response.status_code != 200:
                    raise FREDAPIError(
                        message=f"FRED API returned unexpected status: {response.status_code}",
                        status_code=response.status_code
                    )

                # Parse JSON response
                data = response.json()

                # Check for API-level errors
                if "error_code" in data:
                    logger.error(f"FRED API error: {data}")
                    raise FREDAPIError(
                        message=data.get("error_message", "Unknown FRED API error"),
                        status_code=response.status_code,
                        response_data=data
                    )

                logger.info(f"FRED API request successful: {endpoint}")
                return data

            except httpx.TimeoutException as e:
                if attempt < max_retries:
                    sleep_time = (2 ** attempt) + 1
                    logger.warning(
                        f"FRED API timeout. Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    logger.error(f"FRED API timeout after all retries: {str(e)}")
                    raise FREDAPIError(
                        message=f"Request to FRED API timed out after {max_retries} retries",
                        status_code=408
                    )

            except httpx.HTTPError as e:
                if attempt < max_retries:
                    sleep_time = (2 ** attempt) + 1
                    logger.warning(
                        f"FRED API HTTP error: {str(e)}. "
                        f"Retrying in {sleep_time}s (attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(sleep_time)
                    continue
                else:
                    logger.error(f"FRED API HTTP error after all retries: {str(e)}", exc_info=True)
                    raise FREDAPIError(
                        message=f"HTTP error communicating with FRED API: {str(e)}"
                    )

            except json.JSONDecodeError as e:
                logger.error(f"Error decoding FRED API response: {str(e)}")
                raise FREDAPIError(
                    message="Invalid JSON response from FRED API"
                )

            except FREDAPIError:
                raise

            except Exception as e:
                logger.error(f"Unexpected error in FRED API request: {str(e)}", exc_info=True)
                raise FREDAPIError(
                    message=f"Unexpected error: {str(e)}"
                )

        # Should not reach here, but just in case
        raise FREDAPIError(
            message="Maximum retries exceeded"
        )

    async def fetch_current_values(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch the latest values for all tracked economic metrics.

        Fetches current values for: DFF, DGS10, UNRATE, CPIAUCSL, MORTGAGE30US

        Args:
            use_cache: Whether to use Redis cache (5-minute TTL)

        Returns:
            List[Dict]: List of current values with metadata

        Example:
            [
                {
                    "series_id": "DFF",
                    "series_name": "Federal Funds Rate",
                    "value": 5.33,
                    "unit": "Percent",
                    "date": "2025-10-01",
                    "fetched_at": "2025-10-04T10:30:00Z"
                },
                ...
            ]
        """
        cache_key = self._get_cache_key("all_current")

        # Check cache
        if use_cache:
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                return cached_data.get("data", [])

        # Fetch from API
        results = []
        fetched_at = datetime.now(timezone.utc)

        for series_id, metadata in SERIES_METADATA.items():
            try:
                # Fetch latest observation
                params = {
                    "series_id": series_id,
                    "sort_order": "desc",
                    "limit": 1
                }

                data = await self._make_request_with_retry("series/observations", params)
                observations = data.get("observations", [])

                if observations:
                    obs = observations[0]
                    value_str = obs.get("value")

                    # Skip if value is missing
                    if value_str == "." or value_str is None:
                        logger.warning(f"Missing value for {series_id}, skipping")
                        continue

                    try:
                        value = float(value_str)
                    except ValueError:
                        logger.error(f"Invalid value for {series_id}: {value_str}")
                        continue

                    result = {
                        "series_id": series_id,
                        "series_name": metadata["name"],
                        "value": value,
                        "unit": metadata["unit"],
                        "date": obs.get("date"),
                        "fetched_at": fetched_at.isoformat()
                    }
                    results.append(result)

                    logger.info(
                        f"Fetched current value for {series_id}: {value} ({obs.get('date')})"
                    )

            except FREDAPIError as e:
                logger.error(f"Error fetching {series_id}: {e.message}")
                # Continue with other series
                continue

        # Cache results (5-minute TTL)
        if use_cache and results:
            cache_data = {"data": results}
            await self._set_cache(cache_key, cache_data, ttl=300)  # 5 minutes

        return results

    async def fetch_historical(
        self,
        series_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch historical data for a specific series.

        Args:
            series_id: FRED series ID (e.g., 'DFF', 'UNRATE')
            start_date: Optional start date
            end_date: Optional end date
            use_cache: Whether to use Redis cache (1-hour TTL)

        Returns:
            Dict: Historical data with metadata

        Example:
            {
                "series_id": "DFF",
                "series_name": "Federal Funds Rate",
                "unit": "Percent",
                "data": [
                    {"date": "2025-10-01", "value": 5.33},
                    {"date": "2025-09-01", "value": 5.25},
                    ...
                ],
                "count": 100
            }
        """
        series_id = series_id.upper()

        # Validate series
        if series_id not in SERIES_METADATA:
            raise FREDAPIError(
                message=f"Unknown series: {series_id}. Must be one of: {list(SERIES_METADATA.keys())}",
                status_code=400
            )

        # Check cache
        cache_key = self._get_cache_key(
            "historical",
            series_id=series_id,
            start_date=start_date.isoformat() if start_date else "",
            end_date=end_date.isoformat() if end_date else ""
        )

        if use_cache:
            cached_data = await self._get_from_cache(cache_key)
            if cached_data:
                return cached_data

        # Build request params
        params = {
            "series_id": series_id,
            "sort_order": "desc"
        }

        if start_date:
            params["observation_start"] = start_date.isoformat()
        if end_date:
            params["observation_end"] = end_date.isoformat()

        # Fetch from API
        data = await self._make_request_with_retry("series/observations", params)
        observations = data.get("observations", [])

        # Process observations
        processed_data = []
        for obs in observations:
            value_str = obs.get("value")

            # Skip missing values
            if value_str == "." or value_str is None:
                continue

            try:
                value = float(value_str)
                processed_data.append({
                    "date": obs.get("date"),
                    "value": value
                })
            except ValueError:
                logger.warning(f"Invalid value in {series_id}: {value_str}")
                continue

        metadata = SERIES_METADATA[series_id]
        result = {
            "series_id": series_id,
            "series_name": metadata["name"],
            "unit": metadata["unit"],
            "data": processed_data,
            "count": len(processed_data)
        }

        # Cache result (1-hour TTL)
        if use_cache:
            await self._set_cache(cache_key, result, ttl=3600)  # 1 hour

        logger.info(f"Fetched {len(processed_data)} historical observations for {series_id}")

        return result

    async def fetch_and_store_all(self, db: Optional[AsyncSession] = None) -> Dict[str, Any]:
        """
        Fetch all tracked metrics and store them in PostgreSQL.

        This method fetches current values for all tracked series and
        stores them in the fred_data_points table using upsert logic.

        Args:
            db: Optional database session (will create one if not provided)

        Returns:
            Dict: Summary of what was fetched and stored

        Example:
            {
                "status": "success",
                "series_fetched": ["DFF", "DGS10", "UNRATE", "CPIAUCSL", "MORTGAGE30US"],
                "data_points_stored": 5,
                "timestamp": "2025-10-04T10:35:00Z"
            }
        """
        # Fetch current values (bypass cache to get fresh data)
        current_values = await self.fetch_current_values(use_cache=False)

        if not current_values:
            logger.warning("No current values fetched from FRED API")
            return {
                "status": "error",
                "message": "No data fetched from FRED API",
                "series_fetched": [],
                "data_points_stored": 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        # Store in database
        stored_count = 0
        series_fetched = []

        # Use provided session or create context
        if db is not None:
            stored_count = await self._store_data_points(db, current_values)
            series_fetched = [item["series_id"] for item in current_values]
        else:
            async with get_db_context() as db_session:
                stored_count = await self._store_data_points(db_session, current_values)
                series_fetched = [item["series_id"] for item in current_values]

        # Invalidate relevant caches
        await self._invalidate_cache_pattern("fred:current:*")

        logger.info(
            f"Stored {stored_count} data points for series: {series_fetched}"
        )

        return {
            "status": "success",
            "series_fetched": series_fetched,
            "data_points_stored": stored_count,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _store_data_points(
        self,
        db: AsyncSession,
        data_points: List[Dict[str, Any]]
    ) -> int:
        """
        Store data points in the database using upsert logic.

        Args:
            db: Database session
            data_points: List of data points to store

        Returns:
            int: Number of data points stored
        """
        stored_count = 0

        for point in data_points:
            try:
                # Parse date
                obs_date = datetime.strptime(point["date"], "%Y-%m-%d").date()
                fetched_at = datetime.fromisoformat(point["fetched_at"].replace("Z", "+00:00"))

                # Prepare upsert statement
                stmt = insert(FredDataPoint).values(
                    series_id=point["series_id"],
                    series_name=point["series_name"],
                    value=Decimal(str(point["value"])),
                    unit=point["unit"],
                    date=obs_date,
                    fetched_at=fetched_at
                )

                # On conflict, update the value and fetched_at
                stmt = stmt.on_conflict_do_update(
                    constraint='uix_fred_series_date',
                    set_={
                        'value': stmt.excluded.value,
                        'fetched_at': stmt.excluded.fetched_at,
                        'series_name': stmt.excluded.series_name,
                        'unit': stmt.excluded.unit
                    }
                )

                await db.execute(stmt)
                stored_count += 1

            except Exception as e:
                logger.error(f"Error storing data point {point}: {str(e)}")
                continue

        await db.commit()

        return stored_count

    async def invalidate_cache(self, series_id: Optional[str] = None) -> int:
        """
        Invalidate cached data for a specific series or all FRED data.

        Args:
            series_id: Series to invalidate (e.g., 'DFF'). If None, invalidates all FRED cache.

        Returns:
            int: Number of cache keys deleted

        Example:
            ```python
            # Invalidate cache for specific series
            deleted = await fred_service.invalidate_cache("DFF")

            # Invalidate all FRED cache
            deleted = await fred_service.invalidate_cache()
            ```
        """
        if series_id:
            # Invalidate all cache keys for this series (current + historical with any date range)
            pattern = f"fred:*:{series_id.upper()}*"
            logger.info(f"Invalidating cache for series: {series_id}")
        else:
            # Invalidate all FRED cache
            pattern = "fred:*"
            logger.info("Invalidating all FRED cache")

        deleted_count = await self._invalidate_cache_pattern(pattern)

        return deleted_count


async def get_fred_service() -> FREDService:
    """
    Dependency function to get FRED service instance.

    Returns:
        FREDService: FRED service instance
    """
    return FREDService()
