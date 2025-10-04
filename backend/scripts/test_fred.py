#!/usr/bin/env python
"""
FRED API Integration Test Script

Tests the FRED API integration by:
1. Fetching current values for key economic indicators
2. Fetching historical data
3. Testing caching functionality
4. Verifying data persistence

Usage:
    python scripts/test_fred.py
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.core.config import settings


# API base URL (default to localhost if not set)
API_BASE_URL = "http://localhost:8000"


async def test_health_check():
    """Test that the API is running."""
    print("\n" + "=" * 80)
    print("1. HEALTH CHECK")
    print("=" * 80)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health/liveness")
            if response.status_code == 200:
                print("SUCCESS: API is running")
                print(f"Response: {response.json()}")
                return True
            else:
                print(f"WARNING: API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"ERROR: Could not connect to API at {API_BASE_URL}")
        print(f"Error: {str(e)}")
        print("\nMake sure the server is running with:")
        print("  uvicorn app.main:app --reload")
        return False


async def test_fred_current_value(series_id: str):
    """
    Test fetching current value for a FRED series.

    Args:
        series_id: FRED series identifier (e.g., 'DFF', 'UNRATE')
    """
    print(f"\n--- Testing current value for {series_id} ---")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/api/v1/fred/{series_id}/current"
            )

            if response.status_code == 200:
                data = response.json()
                print(f"SUCCESS: {data.get('series_name', series_id)}")
                print(f"  Value: {data.get('value')} {data.get('unit')}")
                print(f"  Date: {data.get('date')}")
                print(f"  From cache: {data.get('from_cache', False)}")
                return True
            else:
                print(f"ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


async def test_fred_historical_data(series_id: str, days: int = 30):
    """
    Test fetching historical data for a FRED series.

    Args:
        series_id: FRED series identifier
        days: Number of days of historical data to fetch
    """
    print(f"\n--- Testing historical data for {series_id} ({days} days) ---")

    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{API_BASE_URL}/api/v1/fred/{series_id}/historical",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                }
            )

            if response.status_code == 200:
                data = response.json()
                data_points = data.get('data', [])
                print(f"SUCCESS: Retrieved {len(data_points)} data points")
                print(f"  Series: {data.get('series_name', series_id)}")
                print(f"  Unit: {data.get('unit', 'N/A')}")

                if data_points:
                    print(f"\n  First point:")
                    first = data_points[0]
                    print(f"    Date: {first.get('date')}")
                    print(f"    Value: {first.get('value')}")

                    print(f"\n  Last point:")
                    last = data_points[-1]
                    print(f"    Date: {last.get('date')}")
                    print(f"    Value: {last.get('value')}")

                return True
            else:
                print(f"ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


async def test_cache_functionality(series_id: str):
    """
    Test caching functionality by making the same request twice.

    Args:
        series_id: FRED series identifier
    """
    print(f"\n--- Testing cache functionality for {series_id} ---")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First request (should hit FRED API)
            print("  Request 1: Fetching from FRED API...")
            start_time = datetime.now()
            response1 = await client.get(
                f"{API_BASE_URL}/api/v1/fred/{series_id}/current"
            )
            duration1 = (datetime.now() - start_time).total_seconds()

            if response1.status_code != 200:
                print(f"ERROR: First request failed with status {response1.status_code}")
                return False

            data1 = response1.json()
            print(f"    Duration: {duration1:.3f}s")
            print(f"    From cache: {data1.get('from_cache', False)}")

            # Second request (should hit cache)
            print("\n  Request 2: Should be cached...")
            start_time = datetime.now()
            response2 = await client.get(
                f"{API_BASE_URL}/api/v1/fred/{series_id}/current"
            )
            duration2 = (datetime.now() - start_time).total_seconds()

            if response2.status_code != 200:
                print(f"ERROR: Second request failed with status {response2.status_code}")
                return False

            data2 = response2.json()
            print(f"    Duration: {duration2:.3f}s")
            print(f"    From cache: {data2.get('from_cache', False)}")

            # Verify cache is working
            if data2.get('from_cache', False):
                print(f"\n  SUCCESS: Cache is working!")
                print(f"  Speed improvement: {duration1/duration2:.1f}x faster")
                return True
            else:
                print(f"\n  WARNING: Second request did not hit cache")
                return False

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


async def main():
    """Main test runner."""
    print("=" * 80)
    print("FRED API INTEGRATION TESTS")
    print("=" * 80)
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"FRED API Key: {'*' * 20}{settings.FRED_API_KEY[-8:]}")

    # Test health check first
    if not await test_health_check():
        print("\nERROR: Cannot proceed without API connection")
        sys.exit(1)

    # Define test series
    test_series = [
        "DFF",        # Federal Funds Rate
        "UNRATE",     # Unemployment Rate
        "DGS10",      # 10-Year Treasury
    ]

    print("\n" + "=" * 80)
    print("2. CURRENT VALUE TESTS")
    print("=" * 80)

    results = []
    for series_id in test_series:
        result = await test_fred_current_value(series_id)
        results.append((f"Current value - {series_id}", result))

    print("\n" + "=" * 80)
    print("3. HISTORICAL DATA TESTS")
    print("=" * 80)

    for series_id in test_series[:2]:  # Test first 2 series
        result = await test_fred_historical_data(series_id, days=30)
        results.append((f"Historical data - {series_id}", result))

    print("\n" + "=" * 80)
    print("4. CACHE FUNCTIONALITY TEST")
    print("=" * 80)

    result = await test_cache_functionality("DFF")
    results.append(("Cache functionality", result))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"  {symbol} {test_name}: {status}")

    print(f"\n  Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n  ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print(f"\n  {total - passed} TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
