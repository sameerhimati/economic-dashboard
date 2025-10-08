# Economic Dashboard API

Production-ready FastAPI backend for the Economic Dashboard application. Provides access to Federal Reserve Economic Data (FRED) with caching, authentication, and analytics capabilities.

## Features

- **FRED API Integration**: Fetch and cache economic data from the Federal Reserve Economic Data API
- **JWT Authentication**: Secure user authentication with JWT tokens
- **PostgreSQL Database**: Persistent storage for users and cached economic data
- **Redis Caching**: High-performance caching for FRED API responses
- **Health Checks**: Comprehensive health monitoring for all services
- **Auto-generated API Documentation**: Interactive Swagger UI and ReDoc
- **Production-Ready**: Optimized Docker container for Railway deployment

## Tech Stack

- **Framework**: FastAPI (async/await)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **Cache**: Redis (async)
- **Authentication**: JWT with bcrypt password hashing
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **HTTP Client**: httpx (async)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py           # Settings and configuration
│   │   ├── database.py         # Database connections (PostgreSQL + Redis)
│   │   └── security.py         # JWT and password hashing
│   ├── models/
│   │   ├── base.py             # SQLAlchemy base model
│   │   ├── user.py             # User model
│   │   └── data_point.py       # FRED data models
│   ├── schemas/
│   │   ├── data.py             # Data-related Pydantic schemas
│   │   └── user.py             # User-related Pydantic schemas
│   ├── api/
│   │   ├── deps.py             # Shared dependencies
│   │   └── routes/
│   │       ├── health.py       # Health check endpoints
│   │       ├── auth.py         # Authentication endpoints
│   │       └── data.py         # FRED data endpoints
│   └── services/
│       └── fred_service.py     # FRED API client with caching
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── Dockerfile                  # Production Docker image
└── railway.json                # Railway deployment config
```

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14+
- Redis 6+
- FRED API Key (free from https://fredaccount.stlouisfed.org/apikey)

### Installation

1. **Clone the repository and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your actual values
   ```

5. **Create PostgreSQL database**:
   ```bash
   createdb economic_dashboard
   ```

6. **Run database migrations**:
   ```bash
   alembic upgrade head
   ```

7. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

8. **Access the API**:
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `DATABASE_URL`: PostgreSQL connection string (async driver)
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: Secret key for JWT tokens (min 32 chars)
- `FRED_API_KEY`: Your FRED API key
- `CORS_ORIGINS`: Comma-separated list of allowed origins

## API Endpoints

### Health
- `GET /health` - Comprehensive health check (all services)
- `GET /health/liveness` - Liveness probe
- `GET /health/readiness` - Readiness probe
- `GET /health/ping` - Simple ping endpoint

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile
- `POST /auth/logout` - Logout (client-side token deletion)
- `POST /auth/refresh` - Refresh access token

### Economic Data
- `GET /data/series/{series_id}` - Fetch FRED series data with caching
- `GET /data/series/{series_id}/latest` - Get latest observation
- `GET /data/series/{series_id}/history` - Get stored historical data
- `DELETE /data/cache/{series_id}` - Invalidate cache (authenticated)

## Database Access

### Production Database (Railway)

Access the production PostgreSQL database via Railway's public TCP proxy:

```bash
# Connection details
Host: switchback.proxy.rlwy.net
Port: 23551
Database: railway
User: postgres
Password: [See Railway dashboard or .env]

# Connect via psql
PGPASSWORD="your-password" psql -h switchback.proxy.rlwy.net -p 23551 -U postgres -d railway

# Quick queries
# Count total metric data points
PGPASSWORD="..." psql -h switchback.proxy.rlwy.net -p 23551 -U postgres -d railway \
  -c "SELECT COUNT(*) FROM metric_data_points;"

# View all metrics with data
PGPASSWORD="..." psql -h switchback.proxy.rlwy.net -p 23551 -U postgres -d railway \
  -c "SELECT metric_code, COUNT(*) as count FROM metric_data_points GROUP BY metric_code ORDER BY metric_code;"

# Check user accounts
PGPASSWORD="..." psql -h switchback.proxy.rlwy.net -p 23551 -U postgres -d railway \
  -c "SELECT id, email, is_superuser FROM users;"
```

### Data Backfill

The `scripts/backfill_metrics.py` script populates historical data for all configured metrics:

```bash
# Activate virtual environment
source .venv/bin/activate

# For local development (uses DATABASE_URL from .env)
python scripts/backfill_metrics.py --years 5 --batch-size 100

# For production (via Railway public proxy)
export DATABASE_URL='postgresql+asyncpg://postgres:PASSWORD@switchback.proxy.rlwy.net:23551/railway'
python scripts/backfill_metrics.py --years 5 --batch-size 100

# Options:
# --years: Number of years of historical data (default: 5, max: 10)
# --batch-size: Records per database batch (default: 50, range: 10-500)
# --metrics: Specific metrics to backfill (comma-separated, or empty for all)
```

**Note**: Backfill script is rate-limited to respect FRED API limits (120 requests/minute). For 39 metrics × 5 years, expect ~30 minutes runtime.

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback migration:
```bash
alembic downgrade -1
```

## Testing

### Run health check:
```bash
curl http://localhost:8000/health
```

### Register a user:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123","full_name":"Test User"}'
```

### Login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"SecurePass123"}'
```

### Fetch FRED data:
```bash
curl "http://localhost:8000/data/series/GDP?observation_start=2020-01-01"
```

## Railway Deployment

### Prerequisites
- Railway account
- Railway CLI installed (optional)

### Deployment Steps

1. **Create a new Railway project**

2. **Add PostgreSQL service**:
   - Railway will automatically provide `DATABASE_URL`

3. **Add Redis service**:
   - Railway will automatically provide `REDIS_URL`

4. **Configure environment variables** in Railway dashboard:
   ```
   ENVIRONMENT=production
   DEBUG=false
   SECRET_KEY=<generate-strong-secret-key>
   FRED_API_KEY=<your-fred-api-key>
   CORS_ORIGINS=https://your-frontend-domain.com
   LOG_LEVEL=WARNING
   ```

5. **Deploy**:
   - Railway will automatically detect the Dockerfile and deploy
   - Run migrations: `alembic upgrade head` (via Railway console)

6. **Verify deployment**:
   - Check health: `https://your-app.railway.app/health`

## Docker

### Build image:
```bash
docker build -t economic-dashboard-api .
```

### Run container:
```bash
docker run -p 8000:8000 --env-file .env economic-dashboard-api
```

### Docker Compose (for local development):
```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: economic_dashboard
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Logging

The application uses Python's logging module with configurable levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

Configure via `LOG_LEVEL` environment variable.

## Security Best Practices

1. **Never commit .env files** to version control
2. **Use strong SECRET_KEY** (min 32 characters, random)
3. **Rotate JWT tokens** regularly in production
4. **Use HTTPS** in production (Railway provides this automatically)
5. **Validate all input** (Pydantic schemas handle this)
6. **Rate limit** API endpoints (consider adding rate limiting middleware)
7. **Monitor logs** for suspicious activity

## Common Issues

### Database connection failed
- Check `DATABASE_URL` format: `postgresql+asyncpg://user:password@host:port/dbname`
- Ensure PostgreSQL is running
- Verify credentials

### Redis connection failed
- Check `REDIS_URL` format: `redis://host:port/db`
- Ensure Redis is running
- For Railway, use `rediss://` for TLS

### FRED API errors
- Verify `FRED_API_KEY` is correct
- Check API rate limits (120 requests/minute)
- Ensure series ID exists

### JWT token errors
- Verify `SECRET_KEY` is set and consistent
- Check token expiration time
- Ensure token is passed in Authorization header: `Bearer <token>`

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.
