# Backend Scripts

This directory contains utility scripts for managing the economic-dashboard backend.

## Available Scripts

### 1. backfill_metrics.py

Backfills historical metric data from FRED API into the `metric_data_points` table.

**Purpose:**
- Populates the database with historical economic data (default: 5 years)
- Supports all metrics configured in `app/config/metrics_config.py`
- Uses batch processing for efficient data insertion
- Idempotent - safe to run multiple times (uses upsert logic)

**Usage:**

```bash
# Backfill all metrics with default settings (5 years)
python scripts/backfill_metrics.py

# Backfill specific metrics only
python scripts/backfill_metrics.py --metrics FEDFUNDS,DGS10,UNRATE

# Backfill 10 years of data
python scripts/backfill_metrics.py --years 10

# Use larger batch size for faster processing
python scripts/backfill_metrics.py --batch-size 100

# Verify existing data without backfilling
python scripts/backfill_metrics.py --verify-only
```

**Options:**
- `--batch-size`: Number of records to insert per batch (default: 50)
- `--years`: Number of years of historical data (default: 5)
- `--metrics`: Comma-separated list of specific metrics to backfill
- `--verify-only`: Only check what data exists, don't backfill

**Requirements:**
- Database must be initialized (migration 007 must be run)
- Valid FRED_API_KEY in environment variables
- PostgreSQL connection (DATABASE_URL)

**Output:**
- Progress logs for each metric
- Batch processing updates
- Final summary with:
  - Metrics processed/succeeded/failed
  - Total data points inserted/updated
  - Processing duration
  - List of any failed metrics

**Example Output:**
```
================================================================================
STARTING BACKFILL
================================================================================
Years of history: 5
Batch size: 50

Processing FEDFUNDS...
  No existing data found
  Fetching data from 2020-10-07 to 2025-10-07...
  Retrieved 1826 data points from FRED
  Processed batch 1/37
  Processed batch 2/37
  ...
  ✓ Completed: 1826 total records in database

Processing DGS10...
  Found 1826 existing records (2020-10-07 to 2025-10-07)
  Fetching data from 2020-10-07 to 2025-10-07...
  Retrieved 1826 data points from FRED
  ✓ Completed: 1826 total records in database

================================================================================
BACKFILL SUMMARY
================================================================================
Total metrics processed: 45
Succeeded: 45
Failed: 0

Total data points: 65,340
New data points: 32,670
Updated data points: 32,670

Duration: 0:12:34
Average: 16.76s per metric
================================================================================
```

---

### 2. test_daily_metrics_api.py

Tests the Daily Metrics API endpoints to verify deployment and functionality.

**Purpose:**
- Verifies backend API is running
- Checks database connectivity
- Checks Redis connectivity
- Tests key endpoints
- Validates configuration

**Usage:**

```bash
# Test local development server
python scripts/test_daily_metrics_api.py --base-url http://localhost:8000

# Test Railway production deployment
python scripts/test_daily_metrics_api.py --base-url https://your-app.railway.app

# Verbose mode with detailed responses
python scripts/test_daily_metrics_api.py --verbose
```

**Tests Performed:**
1. Root endpoint (GET /)
2. Health check endpoint (GET /health)
3. Database connectivity
4. Redis connectivity
5. Metrics configuration loading
6. Daily metrics endpoint (GET /api/daily-metrics/daily)

**Example Output:**
```
================================================================================
DAILY METRICS API TEST SUITE
================================================================================
Testing: http://localhost:8000

============================================================
TEST: Root Endpoint
============================================================
✓ PASS: Root endpoint returned: Economic Dashboard API v1.0.0

============================================================
TEST: Health Check
============================================================
✓ PASS: Health check passed

============================================================
TEST: Database Connectivity
============================================================
✓ PASS: Database is connected and healthy

============================================================
TEST: Redis Connectivity
============================================================
✓ PASS: Redis is connected and healthy

============================================================
TEST: Metrics Configuration
============================================================
✓ PASS: Metrics configuration loaded: 45 metrics configured
  - Sample metrics: FEDFUNDS, DFF, DFEDTARU, DGS10, DGS2
  - Weekday themes configured: 7

============================================================
TEST: Daily Metrics Endpoint
============================================================
✓ PASS: Daily metrics endpoint correctly requires authentication

================================================================================
TEST SUMMARY
================================================================================
Tests passed: 6
Tests failed: 0
Total tests: 6
================================================================================
```

---

### 3. clear_newsletter_data.py

Clears newsletter-related data from the database (existing script).

**Purpose:**
- Removes newsletter records for testing/development
- Cleans up old data

**Usage:**
```bash
python scripts/clear_newsletter_data.py
```

---

## Running Scripts in Production (Railway)

To run scripts against the Railway database:

```bash
# Using railway CLI
railway run python scripts/backfill_metrics.py

# Or connect to Railway shell
railway shell
python scripts/backfill_metrics.py
```

---

## Environment Variables Required

All scripts require the following environment variables (automatically loaded from .env in development):

- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `FRED_API_KEY` - FRED API key
- `SECRET_KEY` - Application secret key

In Railway, these are automatically provided by the platform.

---

## Best Practices

1. **Before Backfilling:**
   - Verify migration 007 has run successfully
   - Check database connectivity with `--verify-only` flag
   - Start with a small subset using `--metrics` flag

2. **During Backfilling:**
   - Monitor logs for errors
   - FRED API has rate limits (120 requests/minute) - the script handles this automatically
   - Use appropriate batch sizes based on your database performance

3. **After Backfilling:**
   - Run with `--verify-only` to check data
   - Test API endpoints with test_daily_metrics_api.py
   - Check Railway logs for any issues

4. **Production Backfilling:**
   - Run during off-peak hours if possible
   - Consider using smaller batch sizes to avoid timeouts
   - Monitor Railway database metrics during backfill

---

## Troubleshooting

**Issue: "Database engine not initialized"**
- Solution: Ensure DATABASE_URL environment variable is set
- Check Railway variables with: `railway variables`

**Issue: "FRED API rate limit exceeded"**
- Solution: The script handles this automatically with exponential backoff
- Wait a few minutes and retry, or reduce batch size

**Issue: "No data returned from FRED"**
- Solution: Check that the metric code exists in FRED
- Verify FRED_API_KEY is valid
- Check FRED API status at https://fred.stlouisfed.org/

**Issue: "Connection timeout"**
- Solution: Increase timeout in the script or reduce batch size
- Check Railway database is running: `railway status`

---

## Development

To add new scripts:

1. Create the script in `scripts/` directory
2. Add shebang line: `#!/usr/bin/env python3`
3. Make executable: `chmod +x scripts/your_script.py`
4. Add proper logging and error handling
5. Update this README with usage instructions
6. Test locally before deploying to Railway

---

## Support

For issues or questions:
- Check Railway logs: `railway logs`
- Review migration status: `railway run alembic current`
- Test API health: `curl https://your-app.railway.app/health`
