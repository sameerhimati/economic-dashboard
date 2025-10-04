"""
Database connection management for PostgreSQL and Redis.

Provides async SQLAlchemy engine and session management, plus Redis client.
"""
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool
from redis.asyncio import Redis, ConnectionPool
from redis.exceptions import RedisError

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Global database engine
_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None

# Global Redis client
_redis_client: Redis | None = None
_redis_pool: ConnectionPool | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the global async database engine.

    Returns:
        AsyncEngine: SQLAlchemy async engine instance

    Raises:
        RuntimeError: If database is not initialized
    """
    global _engine
    if _engine is None:
        raise RuntimeError(
            "Database engine not initialized. Call init_db() first."
        )
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Get the global async session maker.

    Returns:
        async_sessionmaker: SQLAlchemy session maker

    Raises:
        RuntimeError: If database is not initialized
    """
    global _async_session_maker
    if _async_session_maker is None:
        raise RuntimeError(
            "Database session maker not initialized. Call init_db() first."
        )
    return _async_session_maker


async def init_db() -> None:
    """
    Initialize the database engine and session maker.

    Creates async engine with connection pooling and configures session maker.
    Should be called on application startup.
    """
    global _engine, _async_session_maker

    try:
        logger.info("Initializing database connection...")

        # Determine pooling strategy based on environment
        poolclass = QueuePool if settings.is_production else NullPool

        # Create engine kwargs
        engine_kwargs = {
            "echo": settings.DB_ECHO,
            "poolclass": poolclass,
        }

        # Only add pool settings if using QueuePool
        if poolclass == QueuePool:
            engine_kwargs.update({
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_pre_ping": True,  # Verify connections before using
                "pool_recycle": 3600,  # Recycle connections after 1 hour
            })

        # Create async engine
        _engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

        # Create session maker
        _async_session_maker = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )

        logger.info("Database connection initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise


async def close_db() -> None:
    """
    Close the database engine and cleanup connections.

    Should be called on application shutdown.
    """
    global _engine, _async_session_maker

    if _engine is not None:
        try:
            logger.info("Closing database connection...")
            await _engine.dispose()
            _engine = None
            _async_session_maker = None
            logger.info("Database connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing database connection: {str(e)}", exc_info=True)
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_redis() -> None:
    """
    Initialize Redis connection pool and client.

    Creates Redis client with connection pooling for efficient connection reuse.
    Should be called on application startup.
    """
    global _redis_client, _redis_pool

    try:
        logger.info("Initializing Redis connection...")

        # Create connection pool
        _redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=5,
            socket_keepalive=True,
        )

        # Create Redis client
        _redis_client = Redis(connection_pool=_redis_pool)

        # Test connection
        await _redis_client.ping()

        logger.info("Redis connection initialized successfully")

    except RedisError as e:
        logger.error(f"Failed to initialize Redis: {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error initializing Redis: {str(e)}", exc_info=True)
        raise


async def close_redis() -> None:
    """
    Close Redis connection and cleanup resources.

    Should be called on application shutdown.
    """
    global _redis_client, _redis_pool

    if _redis_client is not None:
        try:
            logger.info("Closing Redis connection...")
            await _redis_client.close()
            _redis_client = None

            if _redis_pool is not None:
                await _redis_pool.disconnect()
                _redis_pool = None

            logger.info("Redis connection closed successfully")
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}", exc_info=True)


def get_redis() -> Redis:
    """
    Get the global Redis client.

    Returns:
        Redis: Redis client instance

    Raises:
        RuntimeError: If Redis is not initialized

    Example:
        ```python
        @app.get("/cached-data")
        async def get_cached_data(redis: Redis = Depends(get_redis)):
            data = await redis.get("key")
            return {"data": data}
        ```
    """
    global _redis_client
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() first."
        )
    return _redis_client


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions outside of FastAPI dependencies.

    Useful for background tasks, scripts, or testing.

    Yields:
        AsyncSession: Database session

    Example:
        ```python
        async with get_db_context() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
        ```
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database context error: {str(e)}", exc_info=True)
            raise
        finally:
            await session.close()


async def check_db_health() -> bool:
    """
    Check database connectivity.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False


async def check_redis_health() -> bool:
    """
    Check Redis connectivity.

    Returns:
        bool: True if Redis is healthy, False otherwise
    """
    try:
        redis = get_redis()
        await redis.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False
