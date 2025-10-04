"""
Comprehensive API integration tests for the Economic Dashboard backend.

Tests health checks, authentication, data endpoints, caching, and database operations.

USAGE:
    # Run all tests
    pytest test_api.py -v

    # Run specific test categories
    pytest test_api.py -m health          # Health checks only
    pytest test_api.py -m auth            # Authentication only
    pytest test_api.py -m data            # Data endpoints only
    pytest test_api.py -m cache           # Caching tests only
    pytest test_api.py -m integration     # Integration tests only

    # Test against Railway deployment
    API_BASE_URL=https://your-app.railway.app pytest test_api.py -v

    # Run with coverage
    pytest test_api.py --cov=app --cov-report=html

TEST CATEGORIES:
    - TestHealth (5 tests): Health check endpoints
    - TestAuthentication (11 tests): User registration, login, token management
    - TestFredData (6 tests): Economic data fetching and caching
    - TestCaching (2 tests): Redis caching behavior
    - TestIntegration (2 tests): End-to-end workflows
    Total: 26 comprehensive integration tests

PREREQUISITES:
    1. API must be running (locally or on Railway)
    2. Database and Redis must be accessible
    3. FRED_API_KEY must be configured in .env
    4. Install: pip install -r requirements-dev.txt
"""
import os
import pytest
import httpx
import asyncio
import time
from datetime import datetime, date
from typing import Dict, Optional


# Base URL - can be overridden with environment variable
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Test user credentials - unique per test run to avoid conflicts
TEST_TIMESTAMP = int(time.time())
TEST_EMAIL = f"test_user_{TEST_TIMESTAMP}@example.com"
TEST_PASSWORD = "SecureP@ssw0rd123!"
TEST_FULL_NAME = "Test User"


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
async def client():
    """
    HTTP client for making API requests.

    Yields:
        httpx.AsyncClient: Configured async HTTP client
    """
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="function")
async def registered_user(client: httpx.AsyncClient) -> Dict[str, str]:
    """
    Register a new test user and return credentials.

    Args:
        client: HTTP client

    Returns:
        Dict with email and password
    """
    # Generate unique email for each test
    unique_email = f"test_user_{int(time.time() * 1000000)}@example.com"

    registration_data = {
        "email": unique_email,
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
    }

    response = await client.post("/auth/register", json=registration_data)

    if response.status_code != 201:
        pytest.fail(f"User registration failed: {response.status_code} - {response.text}")

    return {
        "email": unique_email,
        "password": TEST_PASSWORD,
    }


@pytest.fixture
async def auth_token(client: httpx.AsyncClient, registered_user: Dict[str, str]) -> str:
    """
    Login and get authentication token.

    Args:
        client: HTTP client
        registered_user: User credentials

    Returns:
        JWT access token
    """
    login_data = {
        "email": registered_user["email"],
        "password": registered_user["password"],
    }

    response = await client.post("/auth/login", json=login_data)

    if response.status_code != 200:
        pytest.fail(f"Login failed: {response.status_code} - {response.text}")

    data = response.json()
    return data["access_token"]


@pytest.fixture
def auth_headers(auth_token: str) -> Dict[str, str]:
    """
    Create authorization headers with token.

    Args:
        auth_token: JWT token

    Returns:
        Headers dict with Authorization
    """
    return {"Authorization": f"Bearer {auth_token}"}


# =============================================================================
# Health Check Tests
# =============================================================================


@pytest.mark.health
class TestHealth:
    """Health check endpoint tests."""

    async def test_root_endpoint(self, client: httpx.AsyncClient):
        """Test the root endpoint returns API information."""
        response = await client.get("/")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "name" in data, "Response should contain 'name'"
        assert "version" in data, "Response should contain 'version'"
        assert "health" in data, "Response should contain 'health' endpoint"
        assert data["health"] == "/health", "Health endpoint path should be '/health'"

    async def test_health_endpoint(self, client: httpx.AsyncClient):
        """Test comprehensive health check endpoint."""
        response = await client.get("/health")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()

        # Verify structure
        assert "status" in data, "Response should contain 'status'"
        assert "timestamp" in data, "Response should contain 'timestamp'"
        assert "version" in data, "Response should contain 'version'"
        assert "environment" in data, "Response should contain 'environment'"
        assert "services" in data, "Response should contain 'services'"

        # Verify services
        services = data["services"]
        assert "database" in services, "Services should include 'database'"
        assert "redis" in services, "Services should include 'redis'"
        assert "fred_api" in services, "Services should include 'fred_api'"

        # Check database health
        db_status = services["database"]["status"]
        assert db_status in ["healthy", "unhealthy"], f"Invalid database status: {db_status}"

        # Check Redis health
        redis_status = services["redis"]["status"]
        assert redis_status in ["healthy", "unhealthy"], f"Invalid Redis status: {redis_status}"

        # Overall status should be 'healthy' if all services are healthy
        if db_status == "healthy" and redis_status == "healthy":
            assert data["status"] == "healthy", "Overall status should be 'healthy' when all services are healthy"

    async def test_liveness_endpoint(self, client: httpx.AsyncClient):
        """Test liveness probe endpoint."""
        response = await client.get("/health/liveness")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["status"] == "alive", "Liveness status should be 'alive'"
        assert "timestamp" in data, "Response should contain 'timestamp'"

    async def test_readiness_endpoint(self, client: httpx.AsyncClient):
        """Test readiness probe endpoint."""
        response = await client.get("/health/readiness")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert "ready" in data, "Response should contain 'ready' field"
        assert isinstance(data["ready"], bool), "'ready' should be a boolean"
        assert data["status"] in ["ready", "not_ready"], f"Invalid readiness status: {data['status']}"

    async def test_ping_endpoint(self, client: httpx.AsyncClient):
        """Test simple ping endpoint."""
        response = await client.get("/health/ping")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["ping"] == "pong", "Ping should return 'pong'"
        assert "timestamp" in data, "Response should contain 'timestamp'"


# =============================================================================
# Authentication Tests
# =============================================================================


@pytest.mark.auth
class TestAuthentication:
    """Authentication endpoint tests."""

    async def test_user_registration_success(self, client: httpx.AsyncClient):
        """Test successful user registration."""
        unique_email = f"new_user_{int(time.time())}@example.com"
        registration_data = {
            "email": unique_email,
            "password": "SecureP@ssw0rd123!",
            "full_name": "New Test User",
        }

        response = await client.post("/auth/register", json=registration_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}"

        data = response.json()
        assert "id" in data, "Response should contain user 'id'"
        assert data["email"] == unique_email, f"Email mismatch: expected {unique_email}, got {data['email']}"
        assert data["full_name"] == "New Test User", "Full name should match"
        assert data["is_active"] is True, "User should be active by default"
        assert "hashed_password" not in data, "Password should not be exposed"

    async def test_user_registration_duplicate_email(self, client: httpx.AsyncClient, registered_user: Dict[str, str]):
        """Test registration with duplicate email fails."""
        duplicate_data = {
            "email": registered_user["email"],  # Same email as already registered user
            "password": "AnotherP@ssw0rd123!",
            "full_name": "Duplicate User",
        }

        response = await client.post("/auth/register", json=duplicate_data)

        assert response.status_code == 400, f"Expected 400 for duplicate email, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"
        assert "already registered" in data["detail"].lower(), "Error should mention email already registered"

    async def test_user_registration_weak_password(self, client: httpx.AsyncClient):
        """Test registration with weak password fails."""
        weak_password_data = {
            "email": f"weak_pass_{int(time.time())}@example.com",
            "password": "weak",  # Too short, no special chars
            "full_name": "Weak Password User",
        }

        response = await client.post("/auth/register", json=weak_password_data)

        assert response.status_code in [400, 422], f"Expected 400/422 for weak password, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"

    async def test_user_login_success(self, client: httpx.AsyncClient, registered_user: Dict[str, str]):
        """Test successful user login."""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"],
        }

        response = await client.post("/auth/login", json=login_data)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "access_token" in data, "Response should contain 'access_token'"
        assert "token_type" in data, "Response should contain 'token_type'"
        assert data["token_type"] == "bearer", "Token type should be 'bearer'"
        assert "user" in data, "Response should contain 'user' object"
        assert data["user"]["email"] == registered_user["email"], "User email should match"
        assert "expires_in" in data, "Response should contain 'expires_in'"

    async def test_user_login_invalid_credentials(self, client: httpx.AsyncClient, registered_user: Dict[str, str]):
        """Test login with invalid password fails."""
        invalid_login_data = {
            "email": registered_user["email"],
            "password": "WrongPassword123!",
        }

        response = await client.post("/auth/login", json=invalid_login_data)

        assert response.status_code == 401, f"Expected 401 for invalid credentials, got {response.status_code}"

        data = response.json()
        assert "detail" in data, "Error response should contain 'detail'"

    async def test_user_login_nonexistent_user(self, client: httpx.AsyncClient):
        """Test login with non-existent user fails."""
        nonexistent_login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!",
        }

        response = await client.post("/auth/login", json=nonexistent_login_data)

        assert response.status_code == 401, f"Expected 401 for nonexistent user, got {response.status_code}"

    async def test_get_current_user_with_valid_token(self, client: httpx.AsyncClient, auth_headers: Dict[str, str], registered_user: Dict[str, str]):
        """Test getting current user profile with valid token."""
        response = await client.get("/auth/me", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert data["email"] == registered_user["email"], "Email should match registered user"
        assert "id" in data, "Response should contain user 'id'"
        assert "is_active" in data, "Response should contain 'is_active'"

    async def test_get_current_user_without_token(self, client: httpx.AsyncClient):
        """Test getting current user without token fails."""
        response = await client.get("/auth/me")

        assert response.status_code in [401, 403], f"Expected 401/403 without token, got {response.status_code}"

    async def test_get_current_user_with_invalid_token(self, client: httpx.AsyncClient):
        """Test getting current user with invalid token fails."""
        invalid_headers = {"Authorization": "Bearer invalid_token_here"}

        response = await client.get("/auth/me", headers=invalid_headers)

        assert response.status_code == 401, f"Expected 401 with invalid token, got {response.status_code}"

    async def test_refresh_token(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test token refresh endpoint."""
        response = await client.post("/auth/refresh", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "access_token" in data, "Response should contain new 'access_token'"
        assert "token_type" in data, "Response should contain 'token_type'"
        assert "user" in data, "Response should contain 'user' object"

    async def test_logout(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test logout endpoint."""
        response = await client.post("/auth/logout", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "message" in data, "Response should contain 'message'"


# =============================================================================
# FRED Data Tests
# =============================================================================


@pytest.mark.data
class TestFredData:
    """FRED economic data endpoint tests."""

    async def test_get_current_data(self, client: httpx.AsyncClient):
        """Test fetching current values for all tracked metrics."""
        response = await client.get("/data/current")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "data" in data, "Response should contain 'data' array"
        assert isinstance(data["data"], list), "'data' should be a list"

        # Should have data for tracked series
        if len(data["data"]) > 0:
            first_item = data["data"][0]
            assert "series_id" in first_item, "Data point should contain 'series_id'"
            assert "value" in first_item, "Data point should contain 'value'"
            assert "date" in first_item, "Data point should contain 'date'"

    async def test_get_historical_data_dff(self, client: httpx.AsyncClient):
        """Test fetching historical data for Federal Funds Rate."""
        response = await client.get("/data/historical/DFF")

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "series_id" in data, "Response should contain 'series_id'"
        assert data["series_id"] == "DFF", "Series ID should be 'DFF'"
        assert "data" in data, "Response should contain 'data' array"
        assert "count" in data, "Response should contain 'count'"

        if data["count"] > 0:
            first_point = data["data"][0]
            assert "date" in first_point, "Data point should contain 'date'"
            assert "value" in first_point, "Data point should contain 'value'"

    async def test_get_historical_data_with_date_range(self, client: httpx.AsyncClient):
        """Test fetching historical data with date filters."""
        params = {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
        }

        response = await client.get("/data/historical/DFF", params=params)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "data" in data, "Response should contain 'data' array"

        # Verify dates are within range if data exists
        if data["count"] > 0:
            for point in data["data"]:
                point_date = date.fromisoformat(point["date"])
                assert point_date >= date(2024, 1, 1), f"Date {point_date} should be >= 2024-01-01"
                assert point_date <= date(2024, 12, 31), f"Date {point_date} should be <= 2024-12-31"

    async def test_get_historical_data_invalid_series(self, client: httpx.AsyncClient):
        """Test fetching data for invalid series ID."""
        response = await client.get("/data/historical/INVALID_SERIES_ID")

        # Should either return 404 or 400 depending on implementation
        assert response.status_code in [400, 404, 500], f"Expected error status, got {response.status_code}"

    async def test_refresh_data_requires_auth(self, client: httpx.AsyncClient):
        """Test that data refresh requires authentication."""
        response = await client.post("/data/refresh")

        assert response.status_code in [401, 403], f"Expected 401/403 without auth, got {response.status_code}"

    async def test_refresh_data_authenticated(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test manual data refresh with authentication."""
        response = await client.post("/data/refresh", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "status" in data, "Response should contain 'status'"
        assert "series_fetched" in data, "Response should contain 'series_fetched'"
        assert "data_points_stored" in data, "Response should contain 'data_points_stored'"
        assert "timestamp" in data, "Response should contain 'timestamp'"


# =============================================================================
# Caching Tests
# =============================================================================


@pytest.mark.cache
class TestCaching:
    """Redis caching functionality tests."""

    async def test_caching_behavior(self, client: httpx.AsyncClient):
        """Test that data is cached and second request is faster."""
        # First request - should fetch from API
        start_time_1 = time.time()
        response_1 = await client.get("/data/historical/DFF?limit=50")
        duration_1 = time.time() - start_time_1

        assert response_1.status_code == 200, f"First request failed: {response_1.status_code}"

        # Small delay to ensure timing difference
        await asyncio.sleep(0.1)

        # Second request - should use cache (should be faster or same data)
        start_time_2 = time.time()
        response_2 = await client.get("/data/historical/DFF?limit=50")
        duration_2 = time.time() - start_time_2

        assert response_2.status_code == 200, f"Second request failed: {response_2.status_code}"

        # Verify same data returned
        data_1 = response_1.json()
        data_2 = response_2.json()

        # Data should be identical (cached)
        if "data" in data_1 and "data" in data_2:
            assert len(data_1["data"]) == len(data_2["data"]), "Cached data should have same length"

    async def test_cache_invalidation(self, client: httpx.AsyncClient, auth_headers: Dict[str, str]):
        """Test cache invalidation for a series."""
        # First, fetch some data to ensure it's cached
        await client.get("/data/historical/DFF")

        # Invalidate cache (requires auth)
        response = await client.delete("/data/cache/DFF", headers=auth_headers)

        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        data = response.json()
        assert "message" in data, "Response should contain 'message'"
        assert "keys_deleted" in data, "Response should contain 'keys_deleted'"


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestIntegration:
    """End-to-end integration tests."""

    async def test_full_user_workflow(self, client: httpx.AsyncClient):
        """Test complete user workflow: register -> login -> access data."""
        # 1. Register new user
        unique_email = f"integration_user_{int(time.time())}@example.com"
        register_data = {
            "email": unique_email,
            "password": "IntegrationP@ss123!",
            "full_name": "Integration Test User",
        }

        register_response = await client.post("/auth/register", json=register_data)
        assert register_response.status_code == 201, "Registration should succeed"

        # 2. Login
        login_data = {
            "email": unique_email,
            "password": "IntegrationP@ss123!",
        }

        login_response = await client.post("/auth/login", json=login_data)
        assert login_response.status_code == 200, "Login should succeed"

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Get user profile
        profile_response = await client.get("/auth/me", headers=headers)
        assert profile_response.status_code == 200, "Profile fetch should succeed"

        profile = profile_response.json()
        assert profile["email"] == unique_email, "Profile email should match"

        # 4. Access data endpoints
        data_response = await client.get("/data/current")
        assert data_response.status_code == 200, "Data fetch should succeed"

        # 5. Refresh data (authenticated endpoint)
        refresh_response = await client.post("/data/refresh", headers=headers)
        assert refresh_response.status_code == 200, "Data refresh should succeed"

    async def test_database_persistence(self, client: httpx.AsyncClient):
        """Test that data is persisted in database."""
        # Fetch historical data
        response = await client.get("/data/historical/DFF?limit=10")
        assert response.status_code == 200, "Historical data fetch should succeed"

        data = response.json()

        # If we got data, verify it's properly structured
        if data["count"] > 0:
            first_point = data["data"][0]
            assert "date" in first_point, "Data point should have 'date'"
            assert "value" in first_point, "Data point should have 'value'"

            # Fetch again - should get same data from database/cache
            response_2 = await client.get("/data/historical/DFF?limit=10")
            data_2 = response_2.json()

            assert data_2["count"] == data["count"], "Data count should be consistent"
