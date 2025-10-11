"""
Automated script to refresh all metrics via API.
Used by GitHub Actions for daily updates.
"""
import httpx
import asyncio
import sys
import os
from datetime import datetime

async def login(api_url: str, email: str, password: str) -> str:
    """Login and get access token."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{api_url}/auth/login",
            json={"email": email, "password": password}
        )

        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            sys.exit(1)

        result = response.json()
        return result["access_token"]

async def refresh_all_metrics(api_url: str, token: str):
    """Refresh all metrics using the bulk refresh endpoint."""
    print(f"🔄 Refreshing all metrics at {datetime.now()}")

    async with httpx.AsyncClient(timeout=600.0) as client:
        # Call the refresh-all endpoint
        response = await client.post(
            f"{api_url}/api/daily-metrics/refresh-all",
            headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully refreshed metrics")
            print(f"   Updated: {result.get('updated_count', 0)}")
            print(f"   Failed: {result.get('failed_count', 0)}")

            if result.get('failures'):
                print(f"   Failures: {result['failures']}")

            return result
        else:
            print(f"❌ Failed to refresh: {response.status_code}")
            print(f"   Response: {response.text}")
            sys.exit(1)

async def main():
    api_url = os.getenv("API_URL")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not api_url or not email or not password:
        print("❌ Error: API_URL, ADMIN_EMAIL, and ADMIN_PASSWORD must be set")
        sys.exit(1)

    # Remove trailing slash from API URL
    api_url = api_url.rstrip('/')

    print(f"🚀 Starting metric refresh for {api_url}")

    # Login
    print("🔐 Logging in...")
    token = await login(api_url, email, password)
    print("✅ Login successful")

    # Refresh metrics
    await refresh_all_metrics(api_url, token)

    print("✅ Metric refresh complete")

if __name__ == "__main__":
    asyncio.run(main())
