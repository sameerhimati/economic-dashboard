#!/usr/bin/env python3
"""
Test script for Daily Metrics API endpoints.

Verifies that the backend API is working correctly by testing key endpoints.

Usage:
    python scripts/test_daily_metrics_api.py [--base-url BASE_URL] [--verbose]

Examples:
    # Test local development server
    python scripts/test_daily_metrics_api.py --base-url http://localhost:8000

    # Test production (requires authentication)
    python scripts/test_daily_metrics_api.py --base-url https://your-app.railway.app
"""
import asyncio
import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


class APITester:
    """Test Daily Metrics API endpoints."""

    def __init__(self, base_url: str, verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.client = httpx.AsyncClient(timeout=30.0)
        self.tests_passed = 0
        self.tests_failed = 0
        self.token: Optional[str] = None

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    def log_test(self, test_name: str):
        """Log test start."""
        logger.info(f"\n{'=' * 60}")
        logger.info(f"TEST: {test_name}")
        logger.info('=' * 60)

    def log_success(self, message: str):
        """Log test success."""
        self.tests_passed += 1
        logger.info(f"✓ PASS: {message}")

    def log_failure(self, message: str):
        """Log test failure."""
        self.tests_failed += 1
        logger.error(f"✗ FAIL: {message}")

    async def test_health_check(self) -> bool:
        """Test health check endpoint."""
        self.log_test("Health Check")

        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()
                if self.verbose:
                    logger.info(f"Response: {data}")

                if data.get("status") == "healthy":
                    self.log_success("Health check passed")
                    return True
                else:
                    self.log_failure(f"Health check returned unhealthy status: {data}")
                    return False
            else:
                self.log_failure(f"Health check returned status {response.status_code}")
                return False

        except Exception as e:
            self.log_failure(f"Health check failed with error: {str(e)}")
            return False

    async def test_root_endpoint(self) -> bool:
        """Test root endpoint."""
        self.log_test("Root Endpoint")

        try:
            response = await self.client.get(f"{self.base_url}/")

            if response.status_code == 200:
                data = response.json()
                if self.verbose:
                    logger.info(f"Response: {data}")

                if "name" in data and "version" in data:
                    self.log_success(f"Root endpoint returned: {data.get('name')} v{data.get('version')}")
                    return True
                else:
                    self.log_failure("Root endpoint missing required fields")
                    return False
            else:
                self.log_failure(f"Root endpoint returned status {response.status_code}")
                return False

        except Exception as e:
            self.log_failure(f"Root endpoint failed with error: {str(e)}")
            return False

    async def test_database_health(self) -> bool:
        """Test database connectivity."""
        self.log_test("Database Connectivity")

        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()

                db_status = data.get("database", {}).get("status")
                if db_status == "healthy":
                    self.log_success("Database is connected and healthy")
                    return True
                else:
                    self.log_failure(f"Database status: {db_status}")
                    return False
            else:
                self.log_failure(f"Health endpoint returned status {response.status_code}")
                return False

        except Exception as e:
            self.log_failure(f"Database health check failed: {str(e)}")
            return False

    async def test_redis_health(self) -> bool:
        """Test Redis connectivity."""
        self.log_test("Redis Connectivity")

        try:
            response = await self.client.get(f"{self.base_url}/health")

            if response.status_code == 200:
                data = response.json()

                redis_status = data.get("redis", {}).get("status")
                if redis_status == "healthy":
                    self.log_success("Redis is connected and healthy")
                    return True
                else:
                    self.log_failure(f"Redis status: {redis_status}")
                    return False
            else:
                self.log_failure(f"Health endpoint returned status {response.status_code}")
                return False

        except Exception as e:
            self.log_failure(f"Redis health check failed: {str(e)}")
            return False

    async def test_daily_metrics_endpoint(self) -> bool:
        """Test daily metrics endpoint (requires authentication)."""
        self.log_test("Daily Metrics Endpoint")

        try:
            # Try without authentication first
            response = await self.client.get(f"{self.base_url}/api/daily-metrics/daily")

            if response.status_code == 401:
                self.log_success("Daily metrics endpoint correctly requires authentication")
                logger.info("Note: To test with authentication, provide credentials")
                return True
            elif response.status_code == 200:
                data = response.json()
                if self.verbose:
                    logger.info(f"Response: {data}")

                if "date" in data and "metrics" in data:
                    self.log_success(f"Daily metrics endpoint returned data for {data.get('date')}")
                    logger.info(f"  - Theme: {data.get('theme')}")
                    logger.info(f"  - Total metrics: {data.get('summary', {}).get('total_metrics', 0)}")
                    return True
                else:
                    self.log_failure("Daily metrics missing required fields")
                    return False
            else:
                self.log_failure(f"Daily metrics endpoint returned unexpected status {response.status_code}")
                if self.verbose:
                    logger.info(f"Response: {response.text}")
                return False

        except Exception as e:
            self.log_failure(f"Daily metrics endpoint failed: {str(e)}")
            return False

    async def test_metrics_config(self) -> bool:
        """Test that metrics configuration is loaded."""
        self.log_test("Metrics Configuration")

        try:
            # This is an indirect test - we check if the system can access metric configs
            from app.config.metrics_config import get_all_metric_codes, WEEKDAY_THEMES

            codes = get_all_metric_codes()
            if len(codes) > 0:
                self.log_success(f"Metrics configuration loaded: {len(codes)} metrics configured")
                logger.info(f"  - Sample metrics: {', '.join(codes[:5])}")
                logger.info(f"  - Weekday themes configured: {len(WEEKDAY_THEMES)}")
                return True
            else:
                self.log_failure("No metrics found in configuration")
                return False

        except Exception as e:
            self.log_failure(f"Metrics configuration test failed: {str(e)}")
            return False

    async def run_all_tests(self):
        """Run all tests."""
        logger.info("\n" + "=" * 80)
        logger.info("DAILY METRICS API TEST SUITE")
        logger.info("=" * 80)
        logger.info(f"Testing: {self.base_url}")
        logger.info("")

        # Run tests in order
        await self.test_root_endpoint()
        await self.test_health_check()
        await self.test_database_health()
        await self.test_redis_health()
        await self.test_metrics_config()
        await self.test_daily_metrics_endpoint()

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Tests passed: {self.tests_passed}")
        logger.info(f"Tests failed: {self.tests_failed}")
        logger.info(f"Total tests: {self.tests_passed + self.tests_failed}")
        logger.info("=" * 80)

        return self.tests_failed == 0


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test Daily Metrics API endpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed response data"
    )

    args = parser.parse_args()

    # Create tester
    tester = APITester(args.base_url, args.verbose)

    try:
        # Run all tests
        success = await tester.run_all_tests()

        # Close client
        await tester.close()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.warning("\nTests interrupted by user")
        await tester.close()
        sys.exit(130)

    except Exception as e:
        logger.error(f"Fatal error during testing: {str(e)}", exc_info=True)
        await tester.close()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
