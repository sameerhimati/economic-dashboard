"""
API dependency functions.

Provides reusable dependencies for FastAPI endpoints.
"""
import logging
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.database import get_db, get_redis
from app.core.security import decode_access_token
from app.models.user import User
from app.schemas.user import TokenData

# Configure logging
logger = logging.getLogger(__name__)

# HTTP Bearer token security scheme
security = HTTPBearer(
    scheme_name="Bearer",
    description="JWT Bearer token authentication"
)


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    """
    Extract and validate JWT token from Authorization header.

    Args:
        credentials: HTTP Bearer credentials from request header

    Returns:
        TokenData: Decoded token data

    Raises:
        HTTPException: If token is invalid or missing
    """
    try:
        token = credentials.credentials

        # Decode and validate token
        payload = decode_access_token(token)

        if payload is None:
            logger.warning("Invalid token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token data
        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")

        if email is None or user_id is None:
            logger.warning(f"Token missing required claims: email={email}, user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(
            email=email,
            user_id=user_id,
            exp=payload.get("exp")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_data: TokenData = Depends(get_current_user_token),
) -> User:
    """
    Get the current authenticated user from the database.

    Args:
        db: Database session
        token_data: Decoded token data

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If user not found or inactive
    """
    try:
        # Query user by ID
        result = await db.execute(
            select(User).where(User.id == token_data.user_id)
        )
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(f"User not found: user_id={token_data.user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempted access: user_id={user.id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account"
            )

        logger.debug(f"Authenticated user: {user.email}")
        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error authenticating user"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.

    This is an alias for get_current_user but makes intent clearer.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current active user
    """
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current user and verify they have superuser privileges.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current superuser

    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        logger.warning(
            f"Non-superuser attempted admin action: user_id={current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )

    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_superuser),
) -> User:
    """
    Get the current user and verify they have admin privileges.

    This is an alias for get_current_superuser to make intent clearer in admin routes.

    Args:
        current_user: Current authenticated superuser

    Returns:
        User: Current admin user
    """
    return current_user


async def get_optional_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Get the current user if authenticated, or None if not.

    Useful for endpoints that work both with and without authentication.

    Args:
        db: Database session
        credentials: Optional HTTP Bearer credentials

    Returns:
        Optional[User]: Current user if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        token_data = await get_current_user_token(credentials)
        user = await get_current_user(db, token_data)
        return user
    except HTTPException:
        return None
    except Exception as e:
        logger.error(f"Error in optional auth: {str(e)}", exc_info=True)
        return None


def get_redis_client() -> Redis:
    """
    Get Redis client for dependency injection.

    Returns:
        Redis: Redis client instance
    """
    return get_redis()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session for dependency injection.

    This is an alias for get_db to make intent clearer.

    Yields:
        AsyncSession: Database session
    """
    async for session in get_db():
        yield session


class CommonQueryParams:
    """
    Common query parameters for list endpoints.

    Provides pagination and filtering parameters.
    """

    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
    ):
        """
        Initialize common query parameters.

        Args:
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
        """
        self.skip = max(0, skip)  # Ensure non-negative
        self.limit = min(1000, max(1, limit))  # Between 1 and 1000
        self.sort_by = sort_by
        self.sort_order = sort_order.lower() if sort_order else "asc"

        if self.sort_order not in ["asc", "desc"]:
            self.sort_order = "asc"
