#!/usr/bin/env python3
"""
Cron script to automatically fetch newsletters for all users.
Run this via Railway cron or GitHub Actions.
"""
import os
import asyncio
import httpx
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "https://economic-dashboard-production.up.railway.app")
CRON_USER_EMAIL = os.getenv("CRON_USER_EMAIL")
CRON_USER_PASSWORD = os.getenv("CRON_USER_PASSWORD")

async def fetch_newsletters():
    """Fetch newsletters for authenticated user."""
    print(f"[{datetime.now()}] Starting newsletter fetch cron job...")

    if not CRON_USER_EMAIL or not CRON_USER_PASSWORD:
        print("ERROR: CRON_USER_EMAIL and CRON_USER_PASSWORD must be set")
        return

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Login
        print("Logging in...")
        try:
            login_response = await client.post(
                f"{API_BASE_URL}/auth/login",
                json={"email": CRON_USER_EMAIL, "password": CRON_USER_PASSWORD}
            )

            if login_response.status_code != 200:
                print(f"Login failed: {login_response.text}")
                return

            token = login_response.json()["access_token"]
            print("Login successful")

        except Exception as e:
            print(f"Login error: {str(e)}")
            return

        # Step 2: Fetch newsletters (last 1 day to avoid duplicates)
        print("Fetching newsletters from last 24 hours...")
        try:
            fetch_response = await client.post(
                f"{API_BASE_URL}/newsletters/fetch?days=1",
                headers={"Authorization": f"Bearer {token}"}
            )

            if fetch_response.status_code != 200:
                print(f"Fetch failed: {fetch_response.text}")
                return

            result = fetch_response.json()
            print(f"✅ Fetch complete: {result['fetched']} fetched, {result['stored']} stored, {result['skipped']} skipped")

        except Exception as e:
            print(f"Fetch error: {str(e)}")
            return

if __name__ == "__main__":
    asyncio.run(fetch_newsletters())
