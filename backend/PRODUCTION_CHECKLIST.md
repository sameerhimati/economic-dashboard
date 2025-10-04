# Production Deployment Checklist

This checklist ensures all critical configuration is set correctly before deploying to Railway.

---

## Pre-Deployment Configuration

### 1. Environment Variables in Railway

Access Railway dashboard → Project → Variables and set:

#### Required Variables

- [ ] `ENVIRONMENT=production`
  - **Critical**: Must be exactly "production" (lowercase)
  - Controls database pooling and feature flags

- [ ] `DEBUG=false` (or remove to use default)
  - **Critical**: Prevents exposure of sensitive error details
  - Disables development-only features

- [ ] `DATABASE_URL=<railway-provided>`
  - Railway auto-provides this
  - Verify it starts with `postgresql+asyncpg://`
  - Should use `postgres.railway.internal` for internal connection

- [ ] `REDIS_URL=<railway-provided>`
  - Railway auto-provides this
  - Verify it starts with `redis://` or `rediss://` (TLS)
  - Should use `redis.railway.internal` for internal connection

- [ ] `SECRET_KEY=<strong-random-32+-chars>`
  - **Critical**: Generate using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Must be at least 32 characters
  - Never use development key in production

- [ ] `FRED_API_KEY=<your-fred-api-key>`
  - Get from https://fred.stlouisfed.org/
  - 32-character hexadecimal string

- [ ] `CORS_ORIGINS=<production-domains-only>`
  - **Critical**: NO localhost or 127.0.0.1!
  - Comma-separated list
  - Example: `https://yourdomain.com,https://www.yourdomain.com`

#### Optional Variables (can use defaults)

- [ ] `LOG_LEVEL=INFO` or `WARNING`
  - Don't use DEBUG in production
  - Default: INFO

- [ ] `DB_POOL_SIZE=10`
  - Default: 10 (good for most cases)
  - Increase if high load

- [ ] `DB_MAX_OVERFLOW=20`
  - Default: 20
  - Increase if high load

- [ ] `REDIS_MAX_CONNECTIONS=10`
  - Default: 10
  - Increase if high load

### 2. Code Review

- [ ] Latest code committed to main branch
- [ ] All migrations generated and committed
- [ ] No hardcoded localhost references in code
- [ ] No development-only code in production paths

---

## Deployment Steps

### 1. Deploy to Railway

```bash
# Push to main branch (Railway auto-deploys)
git push origin main

# Or manually trigger deployment
railway up
```

### 2. Monitor Deployment

```bash
# Watch logs in real-time
railway logs --tail

# Check for these success messages:
# ✅ "Configuration validation passed successfully"
# ✅ "Database connection initialized successfully"
# ✅ "Redis connection initialized successfully"
# ✅ "Application startup complete"
```

### 3. Run Database Migrations

Migrations run automatically on container startup via Dockerfile CMD:
```bash
alembic upgrade head
```

If you need to run manually:
```bash
railway run alembic upgrade head
```

---

## Post-Deployment Verification

### 1. Health Checks

Test all health endpoints:

```bash
# Get your Railway URL
RAILWAY_URL="https://your-app.railway.app"

# Test liveness (should return 200)
curl -v $RAILWAY_URL/health/liveness

# Test readiness (should return 200)
curl -v $RAILWAY_URL/health/readiness

# Test comprehensive health (should show all services healthy)
curl -v $RAILWAY_URL/health
```

Expected responses:
```json
// /health/liveness
{"status": "alive", "timestamp": "..."}

// /health/readiness
{"status": "ready", "timestamp": "...", "ready": true}

// /health
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0",
  "environment": "production",
  "services": {
    "database": {"status": "healthy", ...},
    "redis": {"status": "healthy", ...},
    "fred_api": {"status": "configured", ...}
  }
}
```

### 2. API Functionality

```bash
# Test root endpoint
curl $RAILWAY_URL/

# Test data endpoints (should work without auth)
curl $RAILWAY_URL/data/current

# Test documentation (should be disabled in production)
curl $RAILWAY_URL/docs  # Should return 404

# Test CORS from browser console (replace with your frontend domain)
fetch('https://your-app.railway.app/health', {
  method: 'GET',
  mode: 'cors'
}).then(r => r.json()).then(console.log)
```

### 3. Database Verification

```bash
# Connect to database
railway run psql $DATABASE_URL

# Check tables exist
\dt

# Should see:
# - users
# - data_points
# - series_metadata
# - fred_data_points
# - alembic_version

# Check data
SELECT * FROM alembic_version;  # Should show current migration version
SELECT COUNT(*) FROM users;     # Check users table

# Exit
\q
```

### 4. Redis Verification

```bash
# Connect to Redis
railway run redis-cli -u $REDIS_URL

# Test connection
PING  # Should return PONG

# Check if any keys exist (might be empty on first deploy)
KEYS *

# Exit
exit
```

### 5. Log Verification

Check Railway logs for correct configuration:

```bash
railway logs --tail 100

# Look for these log lines:
# ✅ "Environment: production"
# ✅ "Debug Mode: False"
# ✅ "Database Pool Size: 10"
# ✅ "CORS Origins: [your-production-domains]"
# ❌ NO "localhost" in CORS origins
# ❌ NO "Debug Mode: True"
```

---

## Monitoring Checklist

### Daily Monitoring (First Week)

- [ ] Check Railway metrics dashboard
  - CPU usage
  - Memory usage
  - Request count
  - Error rate

- [ ] Review logs for errors
  ```bash
  railway logs | grep -i error
  railway logs | grep -i warning
  ```

- [ ] Verify health checks are passing
  ```bash
  curl $RAILWAY_URL/health
  ```

### Set Up Alerts

- [ ] Railway health check monitoring
- [ ] Uptime monitoring (e.g., UptimeRobot, Pingdom)
- [ ] Log aggregation (optional: Railway Logs, CloudWatch, DataDog)

---

## Common Issues & Solutions

### Issue: Container keeps restarting

**Check logs:**
```bash
railway logs
```

**Common causes:**
1. **Database connection failed**
   - Verify `DATABASE_URL` is correct
   - Check database is running in Railway
   - Wait for retry logic (up to 5 attempts)

2. **Redis connection failed**
   - Verify `REDIS_URL` is correct
   - Check Redis is running in Railway
   - Wait for retry logic

3. **Configuration validation failed**
   - Check environment variables are set correctly
   - Look for error messages in logs

### Issue: Health checks failing

**Symptoms:** Railway shows "Unhealthy" status

**Solutions:**
1. Check if app is actually running:
   ```bash
   railway logs
   ```

2. Verify health endpoint directly:
   ```bash
   curl http://localhost:8000/health/liveness
   ```

3. Check startup time - health checks start after 40s

### Issue: CORS errors in browser

**Symptoms:** Frontend can't connect to API

**Solutions:**
1. Verify `CORS_ORIGINS` includes your frontend domain:
   ```bash
   railway variables
   ```

2. Must use exact domain (including https://)

3. No trailing slashes in origins

### Issue: Database queries timing out

**Symptoms:** Slow API responses, timeout errors in logs

**Solutions:**
1. Increase pool size:
   ```bash
   railway variables set DB_POOL_SIZE=20
   ```

2. Check database performance in Railway metrics

3. Review slow query logs

### Issue: FRED API rate limiting

**Symptoms:** "Rate limited" errors in logs

**Solutions:**
1. FRED allows 120 requests/minute
2. App has built-in rate limiter
3. Use caching (already enabled)
4. If multiple instances, rate limit is per-instance

---

## Rollback Procedure

If deployment fails or issues are found:

### 1. Quick Rollback

```bash
# Rollback to previous deployment
railway rollback
```

### 2. Check Previous Version

```bash
# View deployment history
railway status

# View logs of previous deployment
railway logs --deployment <deployment-id>
```

### 3. Fix and Redeploy

1. Identify issue from logs
2. Fix in code or environment variables
3. Redeploy:
   ```bash
   git push origin main
   ```

---

## Performance Tuning

### Database Connection Pool

Monitor pool usage in logs. If seeing "pool exhausted" warnings:

```bash
# Increase pool size
railway variables set DB_POOL_SIZE=20
railway variables set DB_MAX_OVERFLOW=40
```

### Redis Connections

If seeing Redis connection errors:

```bash
# Increase Redis connections
railway variables set REDIS_MAX_CONNECTIONS=20
```

### Worker Count

Default: 4 workers (set in Dockerfile)

For low traffic: 2-4 workers
For high traffic: 4-8 workers

Update in Dockerfile:
```bash
CMD [..., "--workers", "8"]
```

---

## Security Checklist

- [ ] `SECRET_KEY` is strong and unique (32+ characters)
- [ ] `DEBUG=false` in production
- [ ] `CORS_ORIGINS` doesn't include localhost
- [ ] Database credentials are secure (Railway-managed)
- [ ] Redis credentials are secure (Railway-managed)
- [ ] FRED API key is valid and not shared
- [ ] No sensitive data in logs
- [ ] HTTPS enforced (Railway provides this)

---

## Support & Resources

- **Railway Docs**: https://docs.railway.app/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **FRED API Docs**: https://fred.stlouisfed.org/docs/api/
- **Project README**: See backend/README.md

---

**Last Updated**: 2025-10-04
**Version**: 1.0.0
