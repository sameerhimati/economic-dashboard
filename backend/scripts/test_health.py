#!/usr/bin/env python
"""
Health Check Script

Verifies that all services are working correctly:
1. PostgreSQL database connection
2. Redis cache connection
3. FRED API connection
4. API health endpoint

Usage:
    python scripts/test_health.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import redis.asyncio as redis

from app.core.config import settings


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def print_test(name: str, status: bool, details: str = ""):
    """Print test result."""
    symbol = "✓" if status else "✗"
    status_text = "OK" if status else "FAIL"
    print(f"\n{symbol} {name}: {status_text}")
    if details:
        print(f"  {details}")


async def test_database():
    """Test PostgreSQL database connection."""
    print_header("1. DATABASE CONNECTION TEST")

    try:
        # Create engine
        print(f"\nConnecting to: {settings.DATABASE_URL[:50]}...")
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )

        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()

        await engine.dispose()

        print_test(
            "PostgreSQL Connection",
            True,
            f"Version: {version[:50]}..."
        )
        return True

    except Exception as e:
        print_test(
            "PostgreSQL Connection",
            False,
            f"Error: {str(e)}"
        )
        return False


async def test_redis():
    """Test Redis cache connection."""
    print_header("2. REDIS CONNECTION TEST")

    try:
        # Create Redis client
        print(f"\nConnecting to: {settings.REDIS_URL[:50]}...")
        client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

        # Test connection with PING
        pong = await client.ping()
        if not pong:
            raise Exception("Redis PING failed")

        # Test SET and GET
        test_key = "health_check_test"
        test_value = "test_value_123"

        await client.set(test_key, test_value, ex=10)
        retrieved = await client.get(test_key)

        if retrieved != test_value:
            raise Exception(f"Value mismatch: expected {test_value}, got {retrieved}")

        # Clean up
        await client.delete(test_key)
        await client.close()

        print_test(
            "Redis Connection",
            True,
            "Successfully connected and verified SET/GET operations"
        )
        return True

    except Exception as e:
        print_test(
            "Redis Connection",
            False,
            f"Error: {str(e)}"
        )
        return False


async def test_fred_api():
    """Test FRED API connection."""
    print_header("3. FRED API CONNECTION TEST")

    try:
        # Test FRED API by fetching a simple series
        print(f"\nTesting FRED API with key: {'*' * 20}{settings.FRED_API_KEY[-8:]}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test fetching Federal Funds Rate (DFF)
            response = await client.get(
                f"{settings.FRED_API_BASE_URL}/series/observations",
                params={
                    "series_id": "DFF",
                    "api_key": settings.FRED_API_KEY,
                    "file_type": "json",
                    "limit": 1,
                    "sort_order": "desc"
                }
            )

            if response.status_code == 200:
                data = response.json()
                observations = data.get("observations", [])

                if observations:
                    latest = observations[0]
                    print_test(
                        "FRED API Connection",
                        True,
                        f"Latest DFF: {latest.get('value')} on {latest.get('date')}"
                    )
                    return True
                else:
                    print_test(
                        "FRED API Connection",
                        False,
                        "No data returned"
                    )
                    return False
            else:
                print_test(
                    "FRED API Connection",
                    False,
                    f"HTTP {response.status_code}: {response.text[:100]}"
                )
                return False

    except Exception as e:
        print_test(
            "FRED API Connection",
            False,
            f"Error: {str(e)}"
        )
        return False


async def test_api_health():
    """Test API health endpoint."""
    print_header("4. API HEALTH ENDPOINT TEST")

    api_url = "http://localhost:8000"

    try:
        print(f"\nChecking API at: {api_url}")

        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test liveness endpoint
            response = await client.get(f"{api_url}/health/liveness")

            if response.status_code == 200:
                data = response.json()
                print_test(
                    "API Liveness",
                    True,
                    f"Status: {data.get('status', 'unknown')}"
                )
                liveness_ok = True
            else:
                print_test(
                    "API Liveness",
                    False,
                    f"HTTP {response.status_code}"
                )
                liveness_ok = False

            # Test readiness endpoint
            response = await client.get(f"{api_url}/health/readiness")

            if response.status_code == 200:
                data = response.json()
                print_test(
                    "API Readiness",
                    True,
                    f"Database: {data.get('database', 'unknown')}, "
                    f"Cache: {data.get('cache', 'unknown')}"
                )
                readiness_ok = True
            else:
                print_test(
                    "API Readiness",
                    False,
                    f"HTTP {response.status_code}"
                )
                readiness_ok = False

            return liveness_ok and readiness_ok

    except httpx.ConnectError:
        print_test(
            "API Health",
            False,
            f"Could not connect to {api_url}. Is the server running?"
        )
        return False
    except Exception as e:
        print_test(
            "API Health",
            False,
            f"Error: {str(e)}"
        )
        return False


async def test_database_tables():
    """Test that all required database tables exist."""
    print_header("5. DATABASE TABLES CHECK")

    try:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
        )

        required_tables = [
            "users",
            "data_points",
            "series_metadata",
            "fred_data_points",
            "alembic_version"
        ]

        async with engine.begin() as conn:
            for table_name in required_tables:
                result = await conn.execute(
                    text(
                        "SELECT EXISTS ("
                        "  SELECT FROM information_schema.tables "
                        "  WHERE table_name = :table_name"
                        ")"
                    ),
                    {"table_name": table_name}
                )
                exists = result.scalar()

                print_test(
                    f"Table '{table_name}'",
                    exists,
                    "Exists" if exists else "Missing - run migrations!"
                )

        await engine.dispose()
        return True

    except Exception as e:
        print_test(
            "Database Tables Check",
            False,
            f"Error: {str(e)}"
        )
        return False


async def main():
    """Main test runner."""
    print("=" * 80)
    print("ECONOMIC DASHBOARD - HEALTH CHECK")
    print("=" * 80)
    print(f"\nEnvironment: {settings.ENVIRONMENT}")
    print(f"Debug Mode: {settings.DEBUG}")

    # Run all tests
    results = {}

    results["Database"] = await test_database()
    results["Redis"] = await test_redis()
    results["FRED API"] = await test_fred_api()
    results["Database Tables"] = await test_database_tables()
    results["API Health"] = await test_api_health()

    # Print summary
    print_header("SUMMARY")

    all_passed = True
    for service, status in results.items():
        symbol = "✓" if status else "✗"
        status_text = "OK" if status else "FAIL"
        print(f"{symbol} {service}: {status_text}")

        if not status:
            all_passed = False

    print("\n" + "=" * 80)

    if all_passed:
        print("ALL SERVICES HEALTHY!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("SOME SERVICES ARE UNHEALTHY - CHECK ERRORS ABOVE")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
