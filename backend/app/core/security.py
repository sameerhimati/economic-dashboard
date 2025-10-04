"""
Security utilities for authentication and authorization.

Handles JWT token creation/validation and password hashing/verification.
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Password hashing context using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password

    Example:
        ```python
        hashed = get_password_hash("my_secure_password")
        ```
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}", exc_info=True)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise

    Example:
        ```python
        is_valid = verify_password("user_input", user.hashed_password)
        ```
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}", exc_info=True)
        # Return False on error to prevent authentication bypass
        return False


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time delta

    Returns:
        str: Encoded JWT token

    Raises:
        Exception: If token creation fails

    Example:
        ```python
        token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=timedelta(minutes=30)
        )
        ```
    """
    try:
        # Create a copy to avoid mutating the original data
        to_encode = data.copy()

        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        # Add standard JWT claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"  # Token type
        })

        # Encode the JWT
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        logger.debug(f"Created access token for subject: {data.get('sub')}")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating access token: {str(e)}", exc_info=True)
        raise


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string to decode

    Returns:
        Optional[Dict[str, Any]]: Decoded token payload if valid, None otherwise

    Example:
        ```python
        payload = decode_access_token(token)
        if payload:
            user_email = payload.get("sub")
            user_id = payload.get("user_id")
        ```
    """
    try:
        # Decode and validate the JWT
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        # Verify token type
        if payload.get("type") != "access":
            logger.warning(f"Invalid token type: {payload.get('type')}")
            return None

        # Verify expiration (jwt.decode already checks this, but we log it)
        exp = payload.get("exp")
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return None

        logger.debug(f"Successfully decoded token for subject: {payload.get('sub')}")
        return payload

    except JWTError as e:
        logger.warning(f"JWT validation error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}", exc_info=True)
        return None


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token (longer expiration).

    Args:
        data: Dictionary of claims to encode in the token
        expires_delta: Optional custom expiration time delta (default: 7 days)

    Returns:
        str: Encoded JWT refresh token

    Example:
        ```python
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        ```
    """
    try:
        to_encode = data.copy()

        # Refresh tokens typically last longer (7 days default)
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"  # Mark as refresh token
        })

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        logger.debug(f"Created refresh token for subject: {data.get('sub')}")
        return encoded_jwt

    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}", exc_info=True)
        raise


def verify_token_type(token: str, expected_type: str) -> bool:
    """
    Verify that a token is of the expected type.

    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        bool: True if token type matches, False otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload.get("type") == expected_type
    except JWTError:
        return False


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from a JWT token.

    Args:
        token: JWT token string

    Returns:
        Optional[int]: User ID if found, None otherwise
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("user_id")
    return None


def extract_email_from_token(token: str) -> Optional[str]:
    """
    Extract email (subject) from a JWT token.

    Args:
        token: JWT token string

    Returns:
        Optional[str]: Email if found, None otherwise
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        tuple[bool, Optional[str]]: (is_valid, error_message)

    Example:
        ```python
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            raise ValueError(error)
        ```
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if len(password) > 128:
        return False, "Password must not exceed 128 characters"

    # Check for at least one digit
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"

    # Check for at least one letter
    if not any(char.isalpha() for char in password):
        return False, "Password must contain at least one letter"

    return True, None
