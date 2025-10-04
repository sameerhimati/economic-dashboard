"""
FRED data endpoints.

Provides access to Federal Reserve Economic Data with caching.
"""
import logging
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.data_point import DataPoint, SeriesMetadata
from app.models.fred_data import FredDataPoint
from app.models.user import User
from app.schemas.data import (
    FREDSeriesRequest,
    FREDSeriesResponse,
    DataPointResponse,
    DataPointListResponse,
    SeriesMetadataResponse,
    FredDataPointResponse,
    CurrentDataResponse,
    HistoricalDataResponse,
    HistoricalDataPoint,
    RefreshDataResponse,
)
from app.services.fred_service import FREDService, FREDAPIError, get_fred_service
from app.api.deps import get_current_active_user, get_optional_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/data", tags=["Economic Data"])


@router.get(
    "/series/{series_id}",
    response_model=FREDSeriesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get FRED series data",
    description="Fetch economic data for a specific FRED series with optional date range"
)
async def get_series_data(
    series_id: str,
    observation_start: Optional[date] = Query(None, description="Start date for observations"),
    observation_end: Optional[date] = Query(None, description="End date for observations"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$", description="Sort order"),
    units: Optional[str] = Query(None, description="Data transformation"),
    use_cache: bool = Query(True, description="Use cached data if available"),
    fred_service: FREDService = Depends(get_fred_service),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> FREDSeriesResponse:
    """
    Get FRED series observations with metadata.

    Args:
        series_id: FRED series identifier (e.g., 'GDP', 'UNRATE', 'CPIAUCSL')
        observation_start: Optional start date for observations
        observation_end: Optional end date for observations
        sort_order: Sort order ('asc' or 'desc')
        units: Optional data transformation
        use_cache: Whether to use cached data
        fred_service: FRED service instance
        db: Database session
        current_user: Optional authenticated user

    Returns:
        FREDSeriesResponse: Series data with observations and metadata

    Raises:
        HTTPException 404: If series not found
        HTTPException 500: If data fetch fails
    """
    logger.info(
        f"Fetching series data: series_id={series_id}, "
        f"start={observation_start}, end={observation_end}, "
        f"user={current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Fetch series observations from FRED API
        observations_data = await fred_service.get_series_observations(
            series_id=series_id.upper(),
            observation_start=observation_start,
            observation_end=observation_end,
            sort_order=sort_order,
            units=units,
            use_cache=use_cache,
        )

        # Fetch series metadata
        series_info_data = await fred_service.get_series_info(
            series_id=series_id.upper(),
            use_cache=use_cache,
        )

        # Extract observations
        observations = observations_data.get("observations", [])

        # Process and store observations in database
        data_points = []
        for obs in observations:
            try:
                # Parse observation data
                obs_date = datetime.strptime(obs["date"], "%Y-%m-%d").date()
                obs_value = obs["value"]

                # Skip if value is "."  (missing data indicator)
                if obs_value == ".":
                    continue

                obs_value = float(obs_value)

                # Check if data point exists in database
                result = await db.execute(
                    select(DataPoint).where(
                        and_(
                            DataPoint.series_id == series_id.upper(),
                            DataPoint.date == obs_date
                        )
                    )
                )
                existing_point = result.scalar_one_or_none()

                if existing_point:
                    # Update if value changed
                    if existing_point.value != obs_value:
                        existing_point.value = obs_value
                        existing_point.realtime_start = datetime.strptime(
                            obs.get("realtime_start", obs["date"]), "%Y-%m-%d"
                        ).date()
                        existing_point.realtime_end = datetime.strptime(
                            obs.get("realtime_end", obs["date"]), "%Y-%m-%d"
                        ).date()
                        logger.debug(f"Updated data point: {series_id} @ {obs_date}")

                    data_points.append(existing_point)
                else:
                    # Create new data point
                    new_point = DataPoint(
                        series_id=series_id.upper(),
                        date=obs_date,
                        value=obs_value,
                        realtime_start=datetime.strptime(
                            obs.get("realtime_start", obs["date"]), "%Y-%m-%d"
                        ).date(),
                        realtime_end=datetime.strptime(
                            obs.get("realtime_end", obs["date"]), "%Y-%m-%d"
                        ).date(),
                    )
                    db.add(new_point)
                    data_points.append(new_point)
                    logger.debug(f"Created data point: {series_id} @ {obs_date}")

            except (ValueError, KeyError) as e:
                logger.warning(f"Error processing observation: {obs}, error: {str(e)}")
                continue

        # Commit data points
        await db.commit()

        # Refresh to get IDs and timestamps
        for point in data_points:
            await db.refresh(point)

        # Store/update series metadata
        series_info = series_info_data.get("seriess", [{}])[0]  # API returns array
        result = await db.execute(
            select(SeriesMetadata).where(SeriesMetadata.series_id == series_id.upper())
        )
        metadata = result.scalar_one_or_none()

        if metadata:
            # Update metadata
            metadata.title = series_info.get("title")
            metadata.units = series_info.get("units")
            metadata.frequency = series_info.get("frequency")
            metadata.seasonal_adjustment = series_info.get("seasonal_adjustment")
            metadata.notes = series_info.get("notes")
            if series_info.get("last_updated"):
                metadata.last_updated = datetime.strptime(
                    series_info["last_updated"], "%Y-%m-%d %H:%M:%S%z"
                ).date()
        else:
            # Create metadata
            metadata = SeriesMetadata(
                series_id=series_id.upper(),
                title=series_info.get("title"),
                units=series_info.get("units"),
                frequency=series_info.get("frequency"),
                seasonal_adjustment=series_info.get("seasonal_adjustment"),
                notes=series_info.get("notes"),
                last_updated=datetime.strptime(
                    series_info["last_updated"], "%Y-%m-%d %H:%M:%S%z"
                ).date() if series_info.get("last_updated") else None,
            )
            db.add(metadata)

        await db.commit()
        await db.refresh(metadata)

        logger.info(
            f"Successfully fetched {len(data_points)} observations for series {series_id}"
        )

        # Build response
        return FREDSeriesResponse(
            series_id=series_id.upper(),
            metadata=SeriesMetadataResponse.model_validate(metadata),
            observations=[DataPointResponse.model_validate(point) for point in data_points],
            count=len(data_points),
            from_cache=observations_data.get("from_cache", False),
        )

    except FREDAPIError as e:
        logger.error(f"FRED API error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error fetching series data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching series data: {str(e)}"
        )
    finally:
        await fred_service.close()


@router.get(
    "/series/{series_id}/latest",
    response_model=DataPointResponse,
    status_code=status.HTTP_200_OK,
    summary="Get latest observation",
    description="Get the most recent observation for a FRED series"
)
async def get_latest_observation(
    series_id: str,
    db: AsyncSession = Depends(get_db),
) -> DataPointResponse:
    """
    Get the latest observation for a series from the database.

    Args:
        series_id: FRED series identifier
        db: Database session

    Returns:
        DataPointResponse: Latest observation

    Raises:
        HTTPException 404: If no data found
    """
    logger.info(f"Fetching latest observation for series: {series_id}")

    try:
        result = await db.execute(
            select(DataPoint)
            .where(DataPoint.series_id == series_id.upper())
            .order_by(DataPoint.date.desc())
            .limit(1)
        )
        latest_point = result.scalar_one_or_none()

        if latest_point is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No data found for series: {series_id}"
            )

        return DataPointResponse.model_validate(latest_point)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest observation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching latest observation"
        )


@router.get(
    "/series/{series_id}/history",
    response_model=DataPointListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get historical data from database",
    description="Get stored historical observations for a series"
)
async def get_series_history(
    series_id: str,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    limit: int = Query(1000, ge=1, le=10000, description="Maximum results"),
    db: AsyncSession = Depends(get_db),
) -> DataPointListResponse:
    """
    Get historical data from the database (not from FRED API).

    Args:
        series_id: FRED series identifier
        start_date: Optional start date filter
        end_date: Optional end date filter
        limit: Maximum number of results
        db: Database session

    Returns:
        DataPointListResponse: List of observations

    Raises:
        HTTPException 404: If no data found
    """
    logger.info(f"Fetching history for series: {series_id}")

    try:
        # Build query
        query = select(DataPoint).where(DataPoint.series_id == series_id.upper())

        if start_date:
            query = query.where(DataPoint.date >= start_date)
        if end_date:
            query = query.where(DataPoint.date <= end_date)

        query = query.order_by(DataPoint.date.desc()).limit(limit)

        # Execute query
        result = await db.execute(query)
        data_points = result.scalars().all()

        if not data_points:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical data found for series: {series_id}"
            )

        return DataPointListResponse(
            data=[DataPointResponse.model_validate(point) for point in data_points],
            count=len(data_points),
            series_id=series_id.upper()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching series history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching series history"
        )


@router.delete(
    "/cache/{series_id}",
    status_code=status.HTTP_200_OK,
    summary="Invalidate cache for series",
    description="Clear cached data for a specific series (requires authentication)"
)
async def invalidate_series_cache(
    series_id: str,
    fred_service: FREDService = Depends(get_fred_service),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Invalidate cached data for a series.

    Args:
        series_id: FRED series identifier
        fred_service: FRED service instance
        current_user: Authenticated user

    Returns:
        dict: Invalidation result
    """
    logger.info(f"Invalidating cache for series: {series_id} by user: {current_user.email}")

    try:
        deleted_count = await fred_service.invalidate_cache(series_id.upper())

        return {
            "message": f"Cache invalidated for series: {series_id}",
            "keys_deleted": deleted_count
        }

    except Exception as e:
        logger.error(f"Error invalidating cache: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error invalidating cache"
        )
    finally:
        await fred_service.close()


# New endpoints for enhanced FRED integration


@router.get(
    "/current",
    response_model=CurrentDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current values for all tracked metrics",
    description="Returns the latest values for all 5 tracked economic indicators with caching"
)
async def get_current_values(
    fred_service: FREDService = Depends(get_fred_service),
    db: AsyncSession = Depends(get_db),
) -> CurrentDataResponse:
    """
    Get current (latest) values for all tracked economic metrics.

    Fetches current values for:
    - DFF (Federal Funds Rate)
    - DGS10 (10-Year Treasury Constant Maturity Rate)
    - UNRATE (Unemployment Rate)
    - CPIAUCSL (Consumer Price Index)
    - MORTGAGE30US (30-Year Fixed Rate Mortgage Average)

    Uses Redis caching with 5-minute TTL.

    Args:
        fred_service: FRED service instance
        db: Database session

    Returns:
        CurrentDataResponse: Current values with cache metadata

    Raises:
        HTTPException 500: If data fetch fails
    """
    logger.info("Fetching current values for all tracked metrics")

    try:
        # Fetch current values from FRED (with caching)
        current_values = await fred_service.fetch_current_values(use_cache=True)

        if not current_values:
            logger.warning("No current values available from FRED")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No current economic data available"
            )

        # Get cache metadata if available
        cached = False
        cache_expires_in = 0

        if current_values and len(current_values) > 0:
            # Check if first item has cache metadata
            first_item = current_values[0]
            if isinstance(first_item, dict):
                # Data is from API call, not from database
                # Store in database
                result = await fred_service.fetch_and_store_all(db=db)
                logger.info(f"Stored {result.get('data_points_stored', 0)} current values in database")

        # Query database for current values
        result = await db.execute(
            select(FredDataPoint)
            .where(
                FredDataPoint.series_id.in_(['DFF', 'DGS10', 'UNRATE', 'CPIAUCSL', 'MORTGAGE30US'])
            )
            .order_by(FredDataPoint.series_id, FredDataPoint.date.desc())
            .distinct(FredDataPoint.series_id)
        )
        db_points = result.scalars().all()

        # Group by series_id and get latest for each
        latest_points = {}
        for point in db_points:
            if point.series_id not in latest_points or point.date > latest_points[point.series_id].date:
                latest_points[point.series_id] = point

        response_data = [
            FredDataPointResponse.model_validate(point)
            for point in latest_points.values()
        ]

        # Sort by series_id for consistent ordering
        response_data.sort(key=lambda x: x.series_id)

        return CurrentDataResponse(
            data=response_data,
            cached=cached,
            cache_expires_in=cache_expires_in
        )

    except HTTPException:
        raise
    except FREDAPIError as e:
        logger.error(f"FRED API error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error fetching current values: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching current economic data: {str(e)}"
        )
    finally:
        await fred_service.close()


@router.get(
    "/historical/{series_id}",
    response_model=HistoricalDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Get historical data for a specific series",
    description="Returns historical observations for a FRED series with optional date filtering"
)
async def get_historical_data(
    series_id: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    fred_service: FREDService = Depends(get_fred_service),
) -> HistoricalDataResponse:
    """
    Get historical data for a specific FRED series.

    Valid series: DFF, DGS10, UNRATE, CPIAUCSL, MORTGAGE30US

    Uses Redis caching with 1-hour TTL.

    Args:
        series_id: FRED series identifier
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        limit: Maximum number of results (1-1000)
        fred_service: FRED service instance

    Returns:
        HistoricalDataResponse: Historical data with metadata

    Raises:
        HTTPException 400: If series is invalid or date range is invalid
        HTTPException 500: If data fetch fails
    """
    logger.info(f"Fetching historical data for series: {series_id}")

    # Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date"
        )

    try:
        # Fetch historical data from FRED (with caching)
        historical_data = await fred_service.fetch_historical(
            series_id=series_id.upper(),
            start_date=start_date,
            end_date=end_date,
            use_cache=True
        )

        # Extract cache metadata
        cache_metadata = historical_data.pop("_cache_metadata", {})
        cached = cache_metadata.get("cached", False)

        # Apply limit
        data_points = historical_data.get("data", [])
        if len(data_points) > limit:
            data_points = data_points[:limit]

        # Convert to response schema
        response = HistoricalDataResponse(
            series_id=historical_data["series_id"],
            series_name=historical_data["series_name"],
            unit=historical_data["unit"],
            data=[
                HistoricalDataPoint(date=point["date"], value=point["value"])
                for point in data_points
            ],
            count=len(data_points),
            cached=cached
        )

        logger.info(f"Returning {len(data_points)} historical observations for {series_id}")

        return response

    except FREDAPIError as e:
        logger.error(f"FRED API error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching historical data: {str(e)}"
        )
    finally:
        await fred_service.close()


@router.post(
    "/refresh",
    response_model=RefreshDataResponse,
    status_code=status.HTTP_200_OK,
    summary="Manually refresh all economic data",
    description="Fetches fresh data from FRED API and stores in database (requires authentication)"
)
async def refresh_all_data(
    fred_service: FREDService = Depends(get_fred_service),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> RefreshDataResponse:
    """
    Manually trigger a fresh fetch of all tracked economic metrics.

    This endpoint:
    1. Fetches fresh data from FRED API (bypasses cache)
    2. Stores data in PostgreSQL database using upsert logic
    3. Clears relevant Redis cache

    Requires authentication.

    Args:
        fred_service: FRED service instance
        db: Database session
        current_user: Authenticated user

    Returns:
        RefreshDataResponse: Summary of refresh operation

    Raises:
        HTTPException 500: If refresh fails
    """
    logger.info(f"Manual data refresh triggered by user: {current_user.email}")

    try:
        # Fetch and store all current values
        result = await fred_service.fetch_and_store_all(db=db)

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to refresh data")
            )

        logger.info(
            f"Data refresh successful: {result['data_points_stored']} points stored "
            f"for series: {result['series_fetched']}"
        )

        return RefreshDataResponse(
            status=result["status"],
            series_fetched=result["series_fetched"],
            data_points_stored=result["data_points_stored"],
            timestamp=result["timestamp"]
        )

    except HTTPException:
        raise
    except FREDAPIError as e:
        logger.error(f"FRED API error during refresh: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.status_code or status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Error refreshing data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error refreshing economic data: {str(e)}"
        )
    finally:
        await fred_service.close()
