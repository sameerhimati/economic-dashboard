"""
Database connection management for PostgreSQL and Redis.

Provides async SQLAlchemy engine and session management, plus Redis client.
"""
import asyncio
import logging
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
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


async def init_db(max_retries: int = 5) -> None:
    """
    Initialize the database engine and session maker with retry logic.

    Creates async engine with connection pooling and configures session maker.
    Should be called on application startup.

    Args:
        max_retries: Maximum number of retry attempts for transient failures
    """
    global _engine, _async_session_maker

    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing database connection (attempt {attempt + 1}/{max_retries})...")

            # Determine pooling strategy based on environment
            poolclass = AsyncAdaptedQueuePool if settings.is_production else NullPool

            # Create engine kwargs
            engine_kwargs = {
                "echo": settings.DB_ECHO,
                "poolclass": poolclass,
            }

            # Only add pool settings if using AsyncAdaptedQueuePool
            if poolclass == AsyncAdaptedQueuePool:
                engine_kwargs.update({
                    "pool_size": settings.DB_POOL_SIZE,
                    "max_overflow": settings.DB_MAX_OVERFLOW,
                    "pool_pre_ping": True,  # Verify connections before using
                    "pool_recycle": 3600,  # Recycle connections after 1 hour
                    "connect_args": {
                        "timeout": 10,  # Connection timeout in seconds
                        "command_timeout": 30,  # Query timeout in seconds
                    }
                })
            else:
                # NullPool for development - still add timeouts
                engine_kwargs["connect_args"] = {
                    "timeout": 10,
                    "command_timeout": 30,
                }

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

            # Test the connection
            from sqlalchemy import text
            async with _engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            logger.info("Database connection initialized successfully")
            return

        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                logger.warning(
                    f"Database initialization failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                    f"Retrying in {sleep_time}s..."
                )
                await asyncio.sleep(sleep_time)
            else:
                logger.error(
                    f"Failed to initialize database after {max_retries} attempts: {str(e)}",
                    exc_info=True
                )
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


async def init_redis(max_retries: int = 5) -> None:
    """
    Initialize Redis connection pool and client with retry logic.

    Creates Redis client with connection pooling for efficient connection reuse.
    Should be called on application startup.

    Args:
        max_retries: Maximum number of retry attempts for transient failures
    """
    global _redis_client, _redis_pool

    for attempt in range(max_retries):
        try:
            logger.info(f"Initializing Redis connection (attempt {attempt + 1}/{max_retries})...")

            # Create connection pool with timeouts
            _redis_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,  # Automatically decode responses to strings
                socket_connect_timeout=5,  # Connection timeout
                socket_timeout=10,  # Operation timeout (NEW)
                socket_keepalive=True,
                retry_on_timeout=True,  # Retry on timeout (NEW)
            )

            # Create Redis client
            _redis_client = Redis(connection_pool=_redis_pool)

            # Test connection
            await _redis_client.ping()

            logger.info("Redis connection initialized successfully")
            return

        except RedisError as e:
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 seconds
                logger.warning(
                    f"Redis initialization failed (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                    f"Retrying in {sleep_time}s..."
                )
                await asyncio.sleep(sleep_time)
            else:
                logger.error(
                    f"Failed to initialize Redis after {max_retries} attempts: {str(e)}",
                    exc_info=True
                )
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt
                logger.warning(
                    f"Unexpected error initializing Redis (attempt {attempt + 1}/{max_retries}): {str(e)}. "
                    f"Retrying in {sleep_time}s..."
                )
                await asyncio.sleep(sleep_time)
            else:
                logger.error(
                    f"Unexpected error initializing Redis after {max_retries} attempts: {str(e)}",
                    exc_info=True
                )
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
