"""
FastAPI application entry point.

Main application setup with middleware, routers, and event handlers.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import init_db, close_db, init_redis, close_redis
from app.core.validation import validate_all_config, log_startup_info
from app.api.routes import (
    health_router,
    auth_router,
    data_router,
    dashboard_router,
    newsletters_router,
    articles_router,
    user_settings_router,
    bookmarks_router,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.

    Args:
        app: FastAPI application instance

    Yields:
        None: Control to the application
    """
    # Startup
    try:
        # Validate configuration
        logger.info("Validating configuration...")
        validate_all_config()
        logger.info("Configuration validation passed")

        # Log startup information
        log_startup_info()

        # Initialize database
        logger.info("Initializing database connection...")
        await init_db()
        logger.info("Database initialized successfully")

        # Initialize Redis
        logger.info("Initializing Redis connection...")
        await init_redis()
        logger.info("Redis initialized successfully")

        logger.info("=" * 80)
        logger.info("Application startup complete")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")

    try:
        # Close Redis
        logger.info("Closing Redis connection...")
        await close_redis()
        logger.info("Redis connection closed")

        # Close database
        logger.info("Closing database connection...")
        await close_db()
        logger.info("Database connection closed")

        logger.info("Application shutdown complete")

    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}", exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Economic Dashboard API - Access Federal Reserve Economic Data (FRED) with caching and analytics",
    docs_url="/docs" if settings.is_development else None,  # Disable docs in production
    redoc_url="/redoc" if settings.is_development else None,
    openapi_url="/openapi.json" if settings.is_development else None,
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all incoming requests and responses.

    Args:
        request: Incoming request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    # Log request
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    logger.debug(f"Request headers: {dict(request.headers)}")

    # Process request
    try:
        response = await call_next(request)

        # Log response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code}"
        )

        return response

    except Exception as e:
        logger.error(
            f"Error processing request: {request.method} {request.url.path} - "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle request validation errors.

    Args:
        request: Request that caused the error
        exc: Validation error

    Returns:
        JSONResponse: Error details
    """
    logger.warning(
        f"Validation error for {request.method} {request.url.path}: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Request validation failed",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle SQLAlchemy database errors.

    Args:
        request: Request that caused the error
        exc: Database error

    Returns:
        JSONResponse: Error details
    """
    logger.error(
        f"Database error for {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "error": str(exc) if settings.DEBUG else "Internal server error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.

    Args:
        request: Request that caused the error
        exc: Exception

    Returns:
        JSONResponse: Error details
    """
    logger.error(
        f"Unhandled error for {request.method} {request.url.path}: {str(exc)}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else None,
        },
    )


# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(data_router)
app.include_router(dashboard_router)
app.include_router(newsletters_router)
app.include_router(articles_router)
app.include_router(user_settings_router)
app.include_router(bookmarks_router)


# Root endpoint
@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="API root",
    description="Get basic API information"
)
async def root():
    """
    Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.is_development else "disabled",
        "health": "/health",
    }


# Development-only routes
if settings.is_development:
    @app.get(
        "/debug/config",
        summary="Debug: View configuration",
        description="View current configuration (development only)"
    )
    async def debug_config():
        """
        Debug endpoint to view configuration.

        Only available in development mode.

        Returns:
            dict: Configuration settings (sanitized)
        """
        config = {
            "APP_NAME": settings.APP_NAME,
            "APP_VERSION": settings.APP_VERSION,
            "ENVIRONMENT": settings.ENVIRONMENT,
            "DEBUG": settings.DEBUG,
            "LOG_LEVEL": settings.LOG_LEVEL,
            "DATABASE_URL": "***" if settings.DATABASE_URL else None,
            "REDIS_URL": "***" if settings.REDIS_URL else None,
            "FRED_API_KEY": "***" if settings.FRED_API_KEY else None,
            "CORS_ORIGINS": settings.CORS_ORIGINS,
            "ACCESS_TOKEN_EXPIRE_MINUTES": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        }
        return config


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
