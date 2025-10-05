"""
User settings endpoints for email configuration and newsletter preferences.

Handles user-specific email setup and newsletter category selection.
"""
import logging
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.encryption import encrypt_email_password, decrypt_email_password, EncryptionError
from app.models.user import User
from app.schemas.user import (
    UserEmailConfigUpdate,
    UserEmailConfigResponse,
    UserNewsletterPreferencesUpdate,
    NewsletterPreferences,
    NewsletterCategoriesResponse,
    BISNOW_CATEGORIES,
)
from app.api.deps import get_current_active_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/auth/settings", tags=["User Settings"])


@router.get(
    "/email-config",
    response_model=UserEmailConfigResponse,
    summary="Get email configuration",
    description="Get current user's email configuration (password is never returned)"
)
async def get_email_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserEmailConfigResponse:
    """
    Get user's email configuration.

    Returns email address and IMAP settings, but never returns the password
    for security reasons.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        UserEmailConfigResponse: Email configuration (password masked)
    """
    logger.info(f"Fetching email config for user {current_user.id}")

    is_configured = bool(
        current_user.email_address and current_user.email_app_password
    )

    return UserEmailConfigResponse(
        email_address=current_user.email_address,
        imap_server=current_user.imap_server or "imap.gmail.com",
        imap_port=current_user.imap_port or 993,
        is_configured=is_configured
    )


@router.put(
    "/email-config",
    response_model=UserEmailConfigResponse,
    summary="Update email configuration",
    description="Update user's email settings for newsletter fetching"
)
async def update_email_config(
    config: UserEmailConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserEmailConfigResponse:
    """
    Update user's email configuration.

    Encrypts the email password before storing it in the database.

    Args:
        config: Email configuration update
        current_user: Authenticated user
        db: Database session

    Returns:
        UserEmailConfigResponse: Updated email configuration

    Raises:
        HTTPException 500: If encryption fails
    """
    logger.info(f"Updating email config for user {current_user.id}")

    try:
        # Update email address if provided
        if config.email_address is not None:
            current_user.email_address = config.email_address
            logger.info(f"Updated email address for user {current_user.id}")

        # Encrypt and update password if provided
        if config.email_app_password is not None:
            try:
                encrypted_password = encrypt_email_password(config.email_app_password)
                current_user.email_app_password = encrypted_password
                logger.info(f"Updated encrypted email password for user {current_user.id}")
            except EncryptionError as e:
                logger.error(f"Failed to encrypt email password for user {current_user.id}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to encrypt email password. Please try again."
                )

        # Update IMAP settings
        current_user.imap_server = config.imap_server
        current_user.imap_port = config.imap_port

        await db.commit()
        await db.refresh(current_user)

        logger.info(f"Email config updated successfully for user {current_user.id}")

        is_configured = bool(
            current_user.email_address and current_user.email_app_password
        )

        return UserEmailConfigResponse(
            email_address=current_user.email_address,
            imap_server=current_user.imap_server or "imap.gmail.com",
            imap_port=current_user.imap_port or 993,
            is_configured=is_configured
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating email config for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update email configuration"
        )


@router.delete(
    "/email-config",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete email configuration",
    description="Remove user's email credentials"
)
async def delete_email_config(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete user's email configuration.

    Removes email address and encrypted password from the database.

    Args:
        current_user: Authenticated user
        db: Database session

    Raises:
        HTTPException 500: If deletion fails
    """
    logger.info(f"Deleting email config for user {current_user.id}")

    try:
        current_user.email_address = None
        current_user.email_app_password = None
        # Keep IMAP settings at defaults

        await db.commit()
        logger.info(f"Email config deleted successfully for user {current_user.id}")

    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting email config for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete email configuration"
        )


@router.get(
    "/newsletter-preferences",
    response_model=NewsletterPreferences,
    summary="Get newsletter preferences",
    description="Get user's newsletter category preferences and settings"
)
async def get_newsletter_preferences(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> NewsletterPreferences:
    """
    Get user's newsletter preferences.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        NewsletterPreferences: User's newsletter settings
    """
    logger.info(f"Fetching newsletter preferences for user {current_user.id}")

    # Default preferences if not set
    if not current_user.newsletter_preferences:
        return NewsletterPreferences(
            bisnow_categories=[],
            fetch_enabled=False,
            last_fetch=None
        )

    # Parse last_fetch from ISO string if it exists
    last_fetch = None
    if current_user.newsletter_preferences.get("last_fetch"):
        try:
            last_fetch = datetime.fromisoformat(
                current_user.newsletter_preferences["last_fetch"]
            )
        except (ValueError, TypeError):
            logger.warning(f"Invalid last_fetch timestamp for user {current_user.id}")

    return NewsletterPreferences(
        bisnow_categories=current_user.newsletter_preferences.get("bisnow_categories", []),
        fetch_enabled=current_user.newsletter_preferences.get("fetch_enabled", False),
        last_fetch=last_fetch
    )


@router.put(
    "/newsletter-preferences",
    response_model=NewsletterPreferences,
    summary="Update newsletter preferences",
    description="Update user's newsletter category subscriptions and fetch settings"
)
async def update_newsletter_preferences(
    preferences: UserNewsletterPreferencesUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> NewsletterPreferences:
    """
    Update user's newsletter preferences.

    Args:
        preferences: Newsletter preferences update
        current_user: Authenticated user
        db: Database session

    Returns:
        NewsletterPreferences: Updated preferences

    Raises:
        HTTPException 400: If invalid categories are provided
        HTTPException 500: If update fails
    """
    logger.info(f"Updating newsletter preferences for user {current_user.id}")

    try:
        # Validate categories
        invalid_categories = [
            cat for cat in preferences.bisnow_categories
            if cat not in BISNOW_CATEGORIES
        ]
        if invalid_categories:
            logger.warning(
                f"Invalid categories provided for user {current_user.id}: {invalid_categories}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid categories: {', '.join(invalid_categories)}. "
                       f"Valid categories: {', '.join(BISNOW_CATEGORIES)}"
            )

        # Get existing preferences or create new
        newsletter_prefs = current_user.newsletter_preferences or {}

        # Update preferences
        newsletter_prefs["bisnow_categories"] = preferences.bisnow_categories
        newsletter_prefs["fetch_enabled"] = preferences.fetch_enabled

        # Keep last_fetch if it exists
        last_fetch = newsletter_prefs.get("last_fetch")

        # Update user
        current_user.newsletter_preferences = newsletter_prefs

        await db.commit()
        await db.refresh(current_user)

        logger.info(
            f"Newsletter preferences updated for user {current_user.id}: "
            f"{len(preferences.bisnow_categories)} categories, "
            f"fetch_enabled={preferences.fetch_enabled}"
        )

        # Parse last_fetch for response
        last_fetch_dt = None
        if last_fetch:
            try:
                last_fetch_dt = datetime.fromisoformat(last_fetch)
            except (ValueError, TypeError):
                pass

        return NewsletterPreferences(
            bisnow_categories=preferences.bisnow_categories,
            fetch_enabled=preferences.fetch_enabled,
            last_fetch=last_fetch_dt
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error updating newsletter preferences for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update newsletter preferences"
        )


@router.get(
    "/newsletter-categories",
    response_model=NewsletterCategoriesResponse,
    summary="Get available newsletter categories",
    description="Get list of all available Bisnow newsletter categories"
)
async def get_newsletter_categories() -> NewsletterCategoriesResponse:
    """
    Get list of available newsletter categories.

    Returns:
        NewsletterCategoriesResponse: Available categories
    """
    logger.info("Fetching available newsletter categories")

    return NewsletterCategoriesResponse(
        categories=BISNOW_CATEGORIES
    )
