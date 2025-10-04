"""
Authentication endpoints.

Handles user registration, login, and profile management.
"""
import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    validate_password_strength,
)
from app.core.config import settings
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    LoginResponse,
)
from app.api.deps import get_current_active_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data (email, password, optional full_name)
        db: Database session

    Returns:
        UserResponse: Created user information

    Raises:
        HTTPException 400: If email already exists or password is weak
        HTTPException 500: If user creation fails
    """
    logger.info(f"Registration attempt for email: {user_data.email}")

    try:
        # Validate password strength
        is_valid, error_message = validate_password_strength(user_data.password)
        if not is_valid:
            logger.warning(f"Weak password for {user_data.email}: {error_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        # Check if user already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            logger.warning(f"Registration failed: email already exists - {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        hashed_password = get_password_hash(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False,
        )

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        logger.info(f"User registered successfully: {new_user.email} (ID: {new_user.id})")

        return UserResponse.model_validate(new_user)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user account"
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description="Authenticate user and return JWT token"
)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Authenticate user and return access token.

    Args:
        credentials: User login credentials (email and password)
        db: Database session

    Returns:
        LoginResponse: User info and JWT access token

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If user account is inactive
        HTTPException 500: If login process fails
    """
    logger.info(f"Login attempt for email: {credentials.email}")

    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == credentials.email)
        )
        user = result.scalar_one_or_none()

        # Verify user exists and password is correct
        if user is None or not verify_password(credentials.password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )

        logger.info(f"User logged in successfully: {user.email} (ID: {user.id})")

        return LoginResponse(
            user=UserResponse.model_validate(user),
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing login request"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get the profile of the currently authenticated user"
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current user profile.

    Args:
        current_user: Currently authenticated user (from JWT token)

    Returns:
        UserResponse: Current user information
    """
    logger.debug(f"Profile accessed by user: {current_user.email} (ID: {current_user.id})")

    return UserResponse.model_validate(current_user)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout the current user (client-side token deletion)"
)
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Logout user.

    Since we're using stateless JWT tokens, logout is primarily a client-side operation.
    The client should delete the token. This endpoint exists for logging purposes
    and future token blacklisting if needed.

    Args:
        current_user: Currently authenticated user

    Returns:
        dict: Logout confirmation message
    """
    logger.info(f"User logged out: {current_user.email} (ID: {current_user.id})")

    return {
        "message": "Successfully logged out",
        "detail": "Please delete the access token from your client"
    }


@router.post(
    "/refresh",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get a new access token using the current valid token"
)
async def refresh_token(
    current_user: User = Depends(get_current_active_user),
) -> LoginResponse:
    """
    Refresh access token.

    Generate a new access token for the authenticated user.

    Args:
        current_user: Currently authenticated user

    Returns:
        LoginResponse: New access token and user info
    """
    logger.info(f"Token refresh for user: {current_user.email} (ID: {current_user.id})")

    try:
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user.email, "user_id": current_user.id},
            expires_delta=access_token_expires
        )

        logger.debug(f"New token issued for user: {current_user.email}")

        return LoginResponse(
            user=UserResponse.model_validate(current_user),
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing access token"
        )
