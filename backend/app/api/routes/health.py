"""
Health check endpoints.

Provides system health status and service availability checks.
"""
import logging
from typing import Dict, Any
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.database import check_db_health, check_redis_health
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/health", tags=["Health"])


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Overall health status: 'healthy' or 'unhealthy'")
    timestamp: datetime = Field(..., description="Health check timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment name")
    services: Dict[str, Any] = Field(..., description="Service-specific health status")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-15T10:30:00Z",
                "version": "1.0.0",
                "environment": "production",
                "services": {
                    "database": {
                        "status": "healthy",
                        "message": "PostgreSQL connection successful"
                    },
                    "redis": {
                        "status": "healthy",
                        "message": "Redis connection successful"
                    },
                    "fred_api": {
                        "status": "configured",
                        "message": "FRED API key configured"
                    }
                }
            }
        }


class LivenessResponse(BaseModel):
    """Schema for liveness probe response."""

    status: str = Field(default="alive", description="Liveness status")
    timestamp: datetime = Field(..., description="Check timestamp")


class ReadinessResponse(BaseModel):
    """Schema for readiness probe response."""

    status: str = Field(..., description="Readiness status: 'ready' or 'not_ready'")
    timestamp: datetime = Field(..., description="Check timestamp")
    ready: bool = Field(..., description="Whether the service is ready")


@router.get(
    "",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive health check",
    description="Check the health of all system components including database, cache, and external APIs"
)
async def health_check() -> HealthCheckResponse:
    """
    Perform comprehensive health check of all services.

    Returns:
        HealthCheckResponse: Detailed health status of all services

    This endpoint checks:
    - PostgreSQL database connectivity
    - Redis cache connectivity
    - FRED API configuration
    - Overall system health

    Response codes:
    - 200: All services healthy
    - 503: One or more services unhealthy (but still returns JSON)
    """
    logger.info("Performing health check")

    services = {}
    overall_healthy = True

    # Check PostgreSQL
    try:
        db_healthy = await check_db_health()
        services["database"] = {
            "status": "healthy" if db_healthy else "unhealthy",
            "message": "PostgreSQL connection successful" if db_healthy else "PostgreSQL connection failed",
            "type": "postgresql"
        }
        if not db_healthy:
            overall_healthy = False
            logger.error("Database health check failed")
    except Exception as e:
        logger.error(f"Database health check error: {str(e)}", exc_info=True)
        services["database"] = {
            "status": "unhealthy",
            "message": f"Error checking database: {str(e)}",
            "type": "postgresql"
        }
        overall_healthy = False

    # Check Redis
    try:
        redis_healthy = await check_redis_health()
        services["redis"] = {
            "status": "healthy" if redis_healthy else "unhealthy",
            "message": "Redis connection successful" if redis_healthy else "Redis connection failed",
            "type": "redis"
        }
        if not redis_healthy:
            overall_healthy = False
            logger.error("Redis health check failed")
    except Exception as e:
        logger.error(f"Redis health check error: {str(e)}", exc_info=True)
        services["redis"] = {
            "status": "unhealthy",
            "message": f"Error checking Redis: {str(e)}",
            "type": "redis"
        }
        overall_healthy = False

    # Check FRED API configuration (not connectivity, just config)
    try:
        fred_configured = bool(settings.FRED_API_KEY)
        services["fred_api"] = {
            "status": "configured" if fred_configured else "not_configured",
            "message": "FRED API key configured" if fred_configured else "FRED API key not configured",
            "type": "external_api"
        }
        if not fred_configured:
            overall_healthy = False
            logger.warning("FRED API key not configured")
    except Exception as e:
        logger.error(f"FRED API config check error: {str(e)}", exc_info=True)
        services["fred_api"] = {
            "status": "error",
            "message": f"Error checking FRED API config: {str(e)}",
            "type": "external_api"
        }
        overall_healthy = False

    health_status = "healthy" if overall_healthy else "unhealthy"

    logger.info(f"Health check completed: status={health_status}")

    return HealthCheckResponse(
        status=health_status,
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        services=services
    )


@router.get(
    "/liveness",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Simple liveness check for Kubernetes/Railway health monitoring"
)
async def liveness() -> LivenessResponse:
    """
    Liveness probe endpoint.

    Always returns 200 if the application is running.
    Used by Kubernetes/Railway to determine if the pod/container should be restarted.

    Returns:
        LivenessResponse: Simple alive status
    """
    return LivenessResponse(
        status="alive",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    description="Check if the service is ready to accept traffic"
)
async def readiness() -> ReadinessResponse:
    """
    Readiness probe endpoint.

    Checks if critical services (database, cache) are available.
    Used by Kubernetes/Railway to determine if the service can accept traffic.

    Returns:
        ReadinessResponse: Readiness status

    Response codes:
    - 200: Service is ready
    - 503: Service is not ready
    """
    logger.debug("Performing readiness check")

    # Check critical services
    db_ready = await check_db_health()
    redis_ready = await check_redis_health()

    is_ready = db_ready and redis_ready

    if is_ready:
        logger.debug("Readiness check passed")
        return ReadinessResponse(
            status="ready",
            timestamp=datetime.utcnow(),
            ready=True
        )
    else:
        logger.warning(f"Readiness check failed: db={db_ready}, redis={redis_ready}")
        return ReadinessResponse(
            status="not_ready",
            timestamp=datetime.utcnow(),
            ready=False
        )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Simple ping endpoint",
    description="Minimal health check that just returns pong"
)
async def ping() -> Dict[str, str]:
    """
    Simple ping endpoint for basic connectivity testing.

    Returns:
        dict: Simple pong response
    """
    return {"ping": "pong", "timestamp": datetime.utcnow().isoformat()}
