# Railway Cron Jobs Setup Guide

This guide explains how to set up automated cron jobs on Railway to fetch newsletters and clean up old data.

## Overview

We'll configure two cron jobs:
1. **Auto-Fetch**: Fetch new newsletters from Gmail every 6-12 hours
2. **Auto-Cleanup**: Delete old newsletters (7+ days) daily, preserving bookmarked items

## Prerequisites

- Railway account with project deployed
- Backend API deployed on Railway
- Valid user credentials (email/password for authentication)

## Method 1: Railway Cron Jobs (Recommended)

Railway supports native cron jobs via GitHub Actions or Railway's built-in cron feature.

### Step 1: Create Cron Service Scripts

Create a new directory for cron scripts:

```bash
mkdir -p backend/cron
```

Create `backend/cron/fetch_newsletters.py`:

```python
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

    async with httpx.AsyncClient(timeout=300.0) as client:
        # Step 1: Login
        print("Logging in...")
        login_response = await client.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": CRON_USER_EMAIL, "password": CRON_USER_PASSWORD}
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return

        token = login_response.json()["access_token"]
        print("Login successful")

        # Step 2: Fetch newsletters (last 1 day to avoid duplicates)
        print("Fetching newsletters from last 24 hours...")
        fetch_response = await client.post(
            f"{API_BASE_URL}/newsletters/fetch?days=1",
            headers={"Authorization": f"Bearer {token}"}
        )

        if fetch_response.status_code != 200:
            print(f"Fetch failed: {fetch_response.text}")
            return

        result = fetch_response.json()
        print(f"✅ Fetch complete: {result['fetched']} fetched, {result['stored']} stored, {result['skipped']} skipped")

if __name__ == "__main__":
    asyncio.run(fetch_newsletters())
```

Create `backend/cron/cleanup_newsletters.py`:

```python
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

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Login
        print("Logging in...")
        login_response = await client.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": CRON_USER_EMAIL, "password": CRON_USER_PASSWORD}
        )

        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return

        token = login_response.json()["access_token"]
        print("Login successful")

        # Step 2: Clean up old newsletters
        print("Cleaning up newsletters older than 7 days...")
        cleanup_response = await client.post(
            f"{API_BASE_URL}/newsletters/cleanup",
            headers={"Authorization": f"Bearer {token}"}
        )

        if cleanup_response.status_code != 200:
            print(f"Cleanup failed: {cleanup_response.text}")
            return

        result = cleanup_response.json()
        print(f"✅ Cleanup complete: {result['deleted_count']} newsletters deleted")

if __name__ == "__main__":
    asyncio.run(cleanup_newsletters())
```

Make scripts executable:

```bash
chmod +x backend/cron/*.py
```

### Step 2: Add Dependencies

Add to `backend/requirements.txt`:

```txt
httpx>=0.24.0
```

Install locally:

```bash
cd backend
pip install httpx
```

### Step 3: Set Environment Variables on Railway

In Railway dashboard:

1. Go to your backend service
2. Navigate to **Variables** tab
3. Add these variables:

```
CRON_USER_EMAIL=your-email@gmail.com
CRON_USER_PASSWORD=your-password
API_BASE_URL=https://economic-dashboard-production.up.railway.app
```

### Step 4: Configure Railway Cron Jobs

Railway supports cron jobs via the `railway.json` file:

Create `railway.json` in project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE"
  },
  "crons": [
    {
      "name": "fetch-newsletters",
      "schedule": "0 */12 * * *",
      "command": "cd backend && python3 cron/fetch_newsletters.py"
    },
    {
      "name": "cleanup-newsletters",
      "schedule": "0 2 * * *",
      "command": "cd backend && python3 cron/cleanup_newsletters.py"
    }
  ]
}
```

**Cron Schedule Explanation:**
- `0 */12 * * *` - Every 12 hours (12am, 12pm)
- `0 2 * * *` - Daily at 2:00 AM UTC

### Step 5: Deploy and Verify

1. Commit and push changes:

```bash
git add .
git commit -m "Add Railway cron jobs for auto-fetch and cleanup"
git push
```

2. Railway will automatically detect `railway.json` and set up cron jobs

3. Verify in Railway dashboard:
   - Go to **Deployments** tab
   - Look for cron job execution logs

## Method 2: GitHub Actions (Alternative)

If Railway cron doesn't work, use GitHub Actions:

Create `.github/workflows/newsletter-cron.yml`:

```yaml
name: Newsletter Cron Jobs

on:
  schedule:
    # Fetch newsletters every 12 hours
    - cron: '0 */12 * * *'
    # Cleanup daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch: # Allow manual trigger

jobs:
  fetch-newsletters:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 */12 * * *' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install httpx

      - name: Fetch newsletters
        env:
          API_BASE_URL: https://economic-dashboard-production.up.railway.app
          CRON_USER_EMAIL: ${{ secrets.CRON_USER_EMAIL }}
          CRON_USER_PASSWORD: ${{ secrets.CRON_USER_PASSWORD }}
        run: |
          cd backend
          python3 cron/fetch_newsletters.py

  cleanup-newsletters:
    runs-on: ubuntu-latest
    if: github.event.schedule == '0 2 * * *' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install httpx

      - name: Cleanup old newsletters
        env:
          API_BASE_URL: https://economic-dashboard-production.up.railway.app
          CRON_USER_EMAIL: ${{ secrets.CRON_USER_EMAIL }}
          CRON_USER_PASSWORD: ${{ secrets.CRON_USER_PASSWORD }}
        run: |
          cd backend
          python3 cron/cleanup_newsletters.py
```

**Set GitHub Secrets:**

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add secrets:
   - `CRON_USER_EMAIL`
   - `CRON_USER_PASSWORD`

## Testing

### Test Locally

```bash
cd backend

# Set environment variables
export API_BASE_URL="https://economic-dashboard-production.up.railway.app"
export CRON_USER_EMAIL="your-email@gmail.com"
export CRON_USER_PASSWORD="your-password"

# Test fetch
python3 cron/fetch_newsletters.py

# Test cleanup
python3 cron/cleanup_newsletters.py
```

### Test in Production

Trigger manually via Railway CLI:

```bash
railway run python3 backend/cron/fetch_newsletters.py
railway run python3 backend/cron/cleanup_newsletters.py
```

Or via GitHub Actions:
- Go to Actions tab → Select workflow → Click "Run workflow"

## Monitoring

### Railway Dashboard

1. Go to Railway project
2. Click on backend service
3. Go to **Logs** tab
4. Filter by cron job name or search for timestamps

### Set Up Alerts

Create a monitoring script `backend/cron/monitor_health.py`:

```python
#!/usr/bin/env python3
"""Monitor newsletter system health and send alerts."""
import os
import asyncio
import httpx
from datetime import datetime, timedelta

API_BASE_URL = os.getenv("API_BASE_URL")
CRON_USER_EMAIL = os.getenv("CRON_USER_EMAIL")
CRON_USER_PASSWORD = os.getenv("CRON_USER_PASSWORD")

async def check_health():
    """Check if newsletters are being fetched regularly."""
    async with httpx.AsyncClient() as client:
        # Login
        login_resp = await client.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": CRON_USER_EMAIL, "password": CRON_USER_PASSWORD}
        )
        token = login_resp.json()["access_token"]

        # Get recent newsletters
        newsletters_resp = await client.get(
            f"{API_BASE_URL}/newsletters/recent?limit=1",
            headers={"Authorization": f"Bearer {token}"}
        )

        newsletters = newsletters_resp.json()["newsletters"]

        if not newsletters:
            print("⚠️  WARNING: No newsletters found!")
            return

        latest = newsletters[0]
        received_date = datetime.fromisoformat(latest["received_date"].replace("Z", "+00:00"))
        hours_ago = (datetime.now(received_date.tzinfo) - received_date).total_seconds() / 3600

        if hours_ago > 24:
            print(f"⚠️  WARNING: Latest newsletter is {hours_ago:.1f} hours old!")
        else:
            print(f"✅ System healthy: Latest newsletter is {hours_ago:.1f} hours old")

if __name__ == "__main__":
    asyncio.run(check_health())
```

Run daily via cron or GitHub Actions.

## Troubleshooting

### Issue: Cron jobs not running

**Solution:**
- Check Railway dashboard logs
- Verify `railway.json` is committed and in root directory
- Check environment variables are set
- Try GitHub Actions alternative

### Issue: Authentication failures

**Solution:**
- Verify `CRON_USER_EMAIL` and `CRON_USER_PASSWORD` are correct
- Check if user exists in database
- Test login manually via API

### Issue: Timeout errors

**Solution:**
- Increase timeout in scripts (default 300s for fetch, 60s for cleanup)
- Check API server is healthy
- Verify database connection

### Issue: Duplicate newsletters

**Solution:**
- Reduce fetch window to 1 day (`?days=1`)
- Check duplicate prevention logic in backend
- Verify `uix_newsletter_user_subject_date` constraint

## Best Practices

1. **Use short fetch windows**: Fetch last 1 day instead of 7 to avoid duplicates
2. **Monitor logs regularly**: Check Railway dashboard or GitHub Actions logs
3. **Set up health checks**: Run monitor script to detect issues early
4. **Test before production**: Always test cron scripts locally first
5. **Keep credentials secure**: Use environment variables, never commit secrets
6. **Document changes**: Update this file when modifying cron jobs

## Customization

### Change Fetch Frequency

Edit cron schedule in `railway.json`:

```json
{
  "schedule": "0 */6 * * *"  // Every 6 hours instead of 12
}
```

### Change Cleanup Age Threshold

Modify backend API endpoint `backend/app/api/routes/newsletters.py`:

```python
# Change from 7 days to 14 days
cutoff_date = datetime.now(timezone.utc) - timedelta(days=14)
```

### Fetch for Multiple Users

Modify `fetch_newsletters.py` to loop through multiple users:

```python
USERS = [
    {"email": "user1@example.com", "password": "pass1"},
    {"email": "user2@example.com", "password": "pass2"},
]

for user in USERS:
    # Login with user credentials
    # Fetch newsletters
    # Log results
```

## Summary

- ✅ Two cron jobs: fetch (every 12h) and cleanup (daily)
- ✅ Railway native cron or GitHub Actions
- ✅ Environment variables for security
- ✅ Comprehensive logging
- ✅ Error handling and monitoring
- ✅ Preserves bookmarked newsletters

Your newsletter system is now fully automated! 🎉
