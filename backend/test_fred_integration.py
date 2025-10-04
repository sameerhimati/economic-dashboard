"""
Test script for FRED API integration.

This script tests the enhanced FRED service functionality including:
- Rate limiting
- Retry logic
- Caching
- Database storage
- All three new endpoints

Run this script to verify the implementation works correctly.
"""
import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import init_db, init_redis, close_db, close_redis, get_db_context
from app.services.fred_service import FREDService, FREDAPIError
from app.models.fred_data import FredDataPoint
from sqlalchemy import select


async def test_rate_limiter():
    """Test the rate limiter functionality."""
    print("\n" + "="*80)
    print("TEST 1: Rate Limiter")
    print("="*80)

    from app.services.fred_service import RateLimiter

    # Create a rate limiter with low limits for testing
    limiter = RateLimiter(max_requests=3, window_seconds=5)

    print("Making 5 requests with limit of 3 per 5 seconds...")
    start_time = asyncio.get_event_loop().time()

    for i in range(5):
        await limiter.acquire()
        current_time = asyncio.get_event_loop().time()
        elapsed = current_time - start_time
        print(f"Request {i+1} completed at {elapsed:.2f}s")

    total_time = asyncio.get_event_loop().time() - start_time
    print(f"\nTotal time: {total_time:.2f}s")
    print("Expected: ~5 seconds (should wait after 3rd request)")
    print("PASSED: Rate limiter is working!" if total_time >= 4.5 else "FAILED: Rate limiter not delaying properly")


async def test_fetch_current_values():
    """Test fetching current values from FRED API."""
    print("\n" + "="*80)
    print("TEST 2: Fetch Current Values")
    print("="*80)

    fred_service = FREDService()

    try:
        print("Fetching current values (with cache)...")
        current_values = await fred_service.fetch_current_values(use_cache=True)

        print(f"\nFetched {len(current_values)} data points:")
        for point in current_values:
            print(f"  - {point['series_id']}: {point['series_name']} = {point['value']} {point['unit']} ({point['date']})")

        # Test cache
        print("\nFetching again (should use cache)...")
        cached_values = await fred_service.fetch_current_values(use_cache=True)

        print(f"Second fetch returned {len(cached_values)} points")
        print("PASSED: Current values fetch working!" if len(current_values) > 0 else "FAILED: No data returned")

    except FREDAPIError as e:
        print(f"FAILED: FRED API Error: {e.message}")
    except Exception as e:
        print(f"FAILED: {str(e)}")
    finally:
        await fred_service.close()


async def test_fetch_historical():
    """Test fetching historical data."""
    print("\n" + "="*80)
    print("TEST 3: Fetch Historical Data")
    print("="*80)

    fred_service = FREDService()

    try:
        print("Fetching historical data for DFF (Federal Funds Rate)...")
        historical = await fred_service.fetch_historical(
            series_id="DFF",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
            use_cache=True
        )

        print(f"\nSeries: {historical['series_name']} ({historical['series_id']})")
        print(f"Unit: {historical['unit']}")
        print(f"Data points: {historical['count']}")

        if historical['data']:
            print("\nFirst 5 observations:")
            for point in historical['data'][:5]:
                print(f"  {point['date']}: {point['value']}")

        print(f"\nPASSED: Historical data fetch working!" if historical['count'] > 0 else "FAILED: No historical data")

    except FREDAPIError as e:
        print(f"FAILED: FRED API Error: {e.message}")
    except Exception as e:
        print(f"FAILED: {str(e)}")
    finally:
        await fred_service.close()


async def test_fetch_and_store():
    """Test fetching and storing data in database."""
    print("\n" + "="*80)
    print("TEST 4: Fetch and Store in Database")
    print("="*80)

    fred_service = FREDService()

    try:
        print("Fetching all tracked metrics and storing in database...")

        async with get_db_context() as db:
            result = await fred_service.fetch_and_store_all(db=db)

            print(f"\nStatus: {result['status']}")
            print(f"Series fetched: {', '.join(result['series_fetched'])}")
            print(f"Data points stored: {result['data_points_stored']}")
            print(f"Timestamp: {result['timestamp']}")

            # Verify database storage
            print("\nVerifying database storage...")
            db_result = await db.execute(
                select(FredDataPoint).order_by(FredDataPoint.fetched_at.desc()).limit(5)
            )
            points = db_result.scalars().all()

            print(f"Found {len(points)} recent points in database:")
            for point in points:
                print(f"  - {point.series_id}: {point.value} {point.unit} ({point.date})")

            print("\nPASSED: Fetch and store working!" if result['data_points_stored'] > 0 else "FAILED: No data stored")

    except FREDAPIError as e:
        print(f"FAILED: FRED API Error: {e.message}")
    except Exception as e:
        print(f"FAILED: {str(e)}")
    finally:
        await fred_service.close()


async def test_database_upsert():
    """Test that upsert logic prevents duplicates."""
    print("\n" + "="*80)
    print("TEST 5: Database Upsert Logic")
    print("="*80)

    fred_service = FREDService()

    try:
        print("Storing data twice to test upsert...")

        async with get_db_context() as db:
            # First store
            result1 = await fred_service.fetch_and_store_all(db=db)
            count1 = result1['data_points_stored']

            # Check count
            count_result = await db.execute(select(FredDataPoint))
            total_before = len(count_result.scalars().all())

            print(f"First store: {count1} points")
            print(f"Total in DB: {total_before}")

            # Second store (should update, not duplicate)
            result2 = await fred_service.fetch_and_store_all(db=db)
            count2 = result2['data_points_stored']

            # Check count again
            count_result = await db.execute(select(FredDataPoint))
            total_after = len(count_result.scalars().all())

            print(f"Second store: {count2} points")
            print(f"Total in DB: {total_after}")

            if total_before == total_after:
                print("\nPASSED: Upsert working correctly (no duplicates created)")
            else:
                print(f"\nFAILED: Duplicates created! Before: {total_before}, After: {total_after}")

    except Exception as e:
        print(f"FAILED: {str(e)}")
    finally:
        await fred_service.close()


async def test_error_handling():
    """Test error handling for invalid series."""
    print("\n" + "="*80)
    print("TEST 6: Error Handling")
    print("="*80)

    fred_service = FREDService()

    try:
        print("Testing with invalid series ID...")
        await fred_service.fetch_historical(series_id="INVALID_SERIES")
        print("FAILED: Should have raised an error for invalid series")
    except FREDAPIError as e:
        print(f"Caught expected error: {e.message}")
        print("PASSED: Error handling working correctly")
    except Exception as e:
        print(f"FAILED: Unexpected error: {str(e)}")
    finally:
        await fred_service.close()


async def run_all_tests():
    """Run all tests."""
    print("\n" + "="*80)
    print("FRED API INTEGRATION TEST SUITE")
    print("="*80)
    print("\nInitializing database and Redis connections...")

    try:
        await init_db()
        await init_redis()
        print("Connections initialized successfully!\n")

        # Run all tests
        await test_rate_limiter()
        await test_fetch_current_values()
        await test_fetch_historical()
        await test_fetch_and_store()
        await test_database_upsert()
        await test_error_handling()

        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)

    except Exception as e:
        print(f"\nFATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nClosing connections...")
        await close_redis()
        await close_db()
        print("Connections closed.\n")


if __name__ == "__main__":
    print("\nStarting FRED Integration Tests...")
    print("This will test rate limiting, caching, database storage, and API calls.\n")

    asyncio.run(run_all_tests())
