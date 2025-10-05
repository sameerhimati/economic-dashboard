#!/usr/bin/env python3
"""
Cron script to automatically clean up old newsletters (7+ days).
Preserves all bookmarked newsletters.
"""
import os
import asyncio
import httpx
from datetime import datetime

API_BASE_URL = os.getenv("API_BASE_URL", "https://economic-dashboard-production.up.railway.app")
CRON_USER_EMAIL = os.getenv("CRON_USER_EMAIL")
CRON_USER_PASSWORD = os.getenv("CRON_USER_PASSWORD")

async def cleanup_newsletters():
    """Clean up old newsletters for authenticated user."""
    print(f"[{datetime.now()}] Starting newsletter cleanup cron job...")

    if not CRON_USER_EMAIL or not CRON_USER_PASSWORD:
        print("ERROR: CRON_USER_EMAIL and CRON_USER_PASSWORD must be set")
        return

    async with httpx.AsyncClient(timeout=60.0) as client:
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

        # Step 2: Clean up old newsletters
        print("Cleaning up newsletters older than 7 days...")
        try:
            cleanup_response = await client.post(
                f"{API_BASE_URL}/newsletters/cleanup",
                headers={"Authorization": f"Bearer {token}"}
            )

            if cleanup_response.status_code != 200:
                print(f"Cleanup failed: {cleanup_response.text}")
                return

            result = cleanup_response.json()
            print(f"✅ Cleanup complete: {result['deleted_count']} newsletters deleted")

        except Exception as e:
            print(f"Cleanup error: {str(e)}")
            return

if __name__ == "__main__":
    asyncio.run(cleanup_newsletters())
