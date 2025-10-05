"""
Newsletter API endpoints.

Provides access to email newsletters with search, fetch, and retrieval capabilities.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.newsletter import Newsletter
from app.models.user import User
from app.schemas.newsletter import (
    NewsletterResponse,
    NewsletterSummary,
    NewsletterListResponse,
    NewsletterSearchResponse,
    NewsletterFetchRequest,
    NewsletterFetchResponse,
    NewsletterStatsResponse,
)
from app.services.email_service import EmailService, EmailServiceError
from app.api.deps import get_current_active_user, get_optional_current_user
from app.core.encryption import decrypt_email_password, EncryptionError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/newsletters", tags=["Newsletters"])


@router.get(
    "/recent",
    response_model=NewsletterListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recent newsletters",
    description="Retrieve recent newsletters for the authenticated user with optional category filtering"
)
async def get_recent_newsletters(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of newsletters to return"),
    category: Optional[str] = Query(None, description="Filter by newsletter category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> NewsletterListResponse:
    """
    Get recent newsletters for the authenticated user.

    Only returns newsletters associated with the authenticated user's account.

    Args:
        limit: Maximum number of newsletters to return (1-100)
        category: Optional category filter
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        NewsletterListResponse: List of recent newsletters
    """
    logger.info(
        f"Fetching recent newsletters for user {current_user.id}: limit={limit}, category={category}"
    )

    try:
        # Build query - filter by user_id
        query = select(Newsletter).where(
            Newsletter.user_id == current_user.id
        ).order_by(Newsletter.received_date.desc())

        # Apply category filter if provided
        if category:
            query = query.where(Newsletter.category == category)

        # Apply limit
        query = query.limit(limit)

        # Execute query
        result = await db.execute(query)
        newsletters = result.scalars().all()

        # Convert to summary format
        newsletter_summaries = [
            NewsletterSummary.model_validate(newsletter)
            for newsletter in newsletters
        ]

        return NewsletterListResponse(
            newsletters=newsletter_summaries,
            count=len(newsletter_summaries),
            page=1,
            page_size=limit
        )

    except Exception as e:
        logger.error(f"Error fetching recent newsletters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching recent newsletters"
        )


@router.get(
    "/search",
    response_model=NewsletterSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search newsletters",
    description="Search user's newsletters by keyword in subject, content, or key points"
)
async def search_newsletters(
    query: str = Query(..., min_length=1, description="Search query"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    category: Optional[str] = Query(None, description="Category filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> NewsletterSearchResponse:
    """
    Search newsletters by keyword for the authenticated user.

    Only searches newsletters associated with the authenticated user's account.

    Searches in:
    - Subject line
    - Plain text content
    - Key points (headlines, locations, companies)

    Args:
        query: Search query string
        start_date: Optional start date filter
        end_date: Optional end date filter
        category: Optional category filter
        page: Page number (starts at 1)
        page_size: Number of items per page (1-100)
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        NewsletterSearchResponse: Search results with pagination
    """
    logger.info(
        f"Searching newsletters for user {current_user.id}: query='{query}', category={category}, "
        f"dates={start_date} to {end_date}, page={page}"
    )

    try:
        # Build base query with search conditions and user filter
        search_pattern = f"%{query}%"

        # Search in subject, content_text, and convert key_points to text for searching
        base_conditions = and_(
            Newsletter.user_id == current_user.id,  # Filter by user
            or_(
                Newsletter.subject.ilike(search_pattern),
                Newsletter.content_text.ilike(search_pattern),
            )
        )

        # Build query
        base_query = select(Newsletter).where(base_conditions)

        # Apply filters
        if category:
            base_query = base_query.where(Newsletter.category == category)

        if start_date:
            base_query = base_query.where(Newsletter.received_date >= start_date)

        if end_date:
            base_query = base_query.where(Newsletter.received_date <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total_count = total_result.scalar() or 0

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        query = base_query.order_by(Newsletter.received_date.desc()).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        newsletters = result.scalars().all()

        # Convert to summary format
        newsletter_summaries = [
            NewsletterSummary.model_validate(newsletter)
            for newsletter in newsletters
        ]

        logger.info(f"Search returned {len(newsletter_summaries)} results (total: {total_count})")

        return NewsletterSearchResponse(
            newsletters=newsletter_summaries,
            count=len(newsletter_summaries),
            total_count=total_count,
            query=query,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        logger.error(f"Error searching newsletters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching newsletters"
        )


@router.post(
    "/fetch",
    response_model=NewsletterFetchResponse,
    status_code=status.HTTP_200_OK,
    summary="Manually fetch newsletters",
    description="Trigger manual email fetch from IMAP server using user's email credentials (requires authentication)"
)
async def fetch_newsletters(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> NewsletterFetchResponse:
    """
    Manually trigger newsletter fetch from email using user's own credentials.

    Connects to IMAP server using the authenticated user's email credentials,
    fetches emails from Bisnow, parses content, and stores in database.

    The user must have configured their email settings first via /auth/settings/email-config

    Args:
        days: Number of days to look back (1-30)
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        NewsletterFetchResponse: Summary of fetch operation

    Raises:
        HTTPException 400: If days parameter is invalid or email not configured
        HTTPException 500: If fetch operation fails
    """
    logger.info(f"Manual newsletter fetch triggered by user {current_user.id} ({current_user.email}), days={days}")

    if days < 1 or days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days parameter must be between 1 and 30"
        )

    # Check if user has configured email
    if not current_user.email_address or not current_user.email_app_password:
        logger.warning(f"User {current_user.id} attempted newsletter fetch without email configuration")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please configure your email settings first. Go to /auth/settings/email-config to add your email credentials."
        )

    try:
        logger.info(f"Starting newsletter fetch operation for user {current_user.id}")

        # Decrypt user's email password
        try:
            decrypted_password = decrypt_email_password(current_user.email_app_password)
            if not decrypted_password:
                raise EncryptionError("Failed to decrypt email password")
        except EncryptionError as e:
            logger.error(f"Failed to decrypt email password for user {current_user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decrypt email credentials. Please re-configure your email settings."
            )

        # Create email service with user's credentials
        email_service = EmailService(
            email_address=current_user.email_address,
            email_password=decrypted_password,
            imap_server=current_user.imap_server,
            imap_port=current_user.imap_port
        )

        # Fetch and store emails with user_id
        try:
            result = await email_service.fetch_and_store_emails(
                db=db,
                days=days,
                sender_filter=None,  # Use default filter from EmailService (includes all Bisnow domains)
                user_id=current_user.id  # Associate newsletters with this user
            )
        except EmailServiceError as e:
            # Handle specific email service errors with detailed logging
            logger.error(
                f"Email service error during fetch for user {current_user.id}: {e.message}",
                exc_info=True,
                extra={
                    "user_id": current_user.id,
                    "user_email": current_user.email,
                    "days": days,
                    "error_type": type(e).__name__
                }
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Email service unavailable: {e.message}. Please check email credentials and IMAP server connectivity."
            )

        # Validate result structure
        if not result or not isinstance(result, dict):
            logger.error(f"Invalid result from email service: {result}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email service returned invalid response"
            )

        # Check operation status
        if result.get("status") != "success":
            error_msg = result.get("message", "Unknown error")
            logger.error(f"Newsletter fetch failed with status: {result.get('status')}, message: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Newsletter fetch failed: {error_msg}"
            )

        # Extract counts with defaults
        fetched = result.get("fetched", 0)
        stored = result.get("stored", 0)
        skipped = result.get("skipped", 0)
        timestamp = result.get("timestamp", datetime.now(timezone.utc).isoformat())

        logger.info(
            f"Newsletter fetch completed successfully for user {current_user.id}: "
            f"{stored} stored, {skipped} skipped out of {fetched} fetched",
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "days": days,
                "fetched": fetched,
                "stored": stored,
                "skipped": skipped
            }
        )

        # Update last_fetch timestamp in user's newsletter preferences
        try:
            newsletter_prefs = current_user.newsletter_preferences or {}
            newsletter_prefs["last_fetch"] = datetime.now(timezone.utc).isoformat()
            current_user.newsletter_preferences = newsletter_prefs
            await db.commit()
            await db.refresh(current_user)
            logger.info(f"Updated last_fetch timestamp for user {current_user.id}")
        except Exception as e:
            logger.warning(f"Failed to update last_fetch timestamp for user {current_user.id}: {str(e)}")
            # Don't fail the request if we can't update the timestamp

        return NewsletterFetchResponse(
            status=result["status"],
            fetched=fetched,
            stored=stored,
            skipped=skipped,
            timestamp=timestamp
        )

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except EmailServiceError as e:
        # Catch any EmailServiceError not caught in inner try block
        logger.error(
            f"Unexpected email service error for user {current_user.id}: {e.message}",
            exc_info=True,
            extra={"user_id": current_user.id, "user_email": current_user.email, "days": days}
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Email service error: {e.message}"
        )
    except Exception as e:
        # Catch all other exceptions
        await db.rollback()
        logger.error(
            f"Unexpected error in newsletter fetch endpoint for user {current_user.id}: {str(e)}",
            exc_info=True,
            extra={
                "user_id": current_user.id,
                "user_email": current_user.email,
                "days": days,
                "error_type": type(e).__name__
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching newsletters. Please try again later."
        )


@router.get(
    "/{newsletter_id}",
    response_model=NewsletterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get newsletter by ID",
    description="Retrieve a single newsletter with full content by UUID (must belong to authenticated user)"
)
async def get_newsletter_by_id(
    newsletter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> NewsletterResponse:
    """
    Get a single newsletter by ID for the authenticated user.

    Returns full newsletter details including HTML content, text content,
    and extracted key points. Only returns newsletters that belong to the
    authenticated user.

    Args:
        newsletter_id: Newsletter UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        NewsletterResponse: Full newsletter details

    Raises:
        HTTPException 404: If newsletter not found or doesn't belong to user
    """
    logger.info(f"Fetching newsletter {newsletter_id} for user {current_user.id}")

    try:
        # Query newsletter with user filter
        result = await db.execute(
            select(Newsletter).where(
                and_(
                    Newsletter.id == newsletter_id,
                    Newsletter.user_id == current_user.id  # Only user's newsletters
                )
            )
        )
        newsletter = result.scalar_one_or_none()

        if newsletter is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter not found: {newsletter_id}"
            )

        return NewsletterResponse.model_validate(newsletter)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching newsletter: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching newsletter"
        )


@router.get(
    "/stats/overview",
    response_model=NewsletterStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get newsletter statistics",
    description="Get overview statistics about user's stored newsletters"
)
async def get_newsletter_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> NewsletterStatsResponse:
    """
    Get newsletter statistics for the authenticated user.

    Provides overview of user's newsletters:
    - Total newsletter count
    - Count by category
    - Count by source
    - Date range
    - Recent activity (last 7 days)

    Args:
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        NewsletterStatsResponse: Newsletter statistics
    """
    logger.info(f"Fetching newsletter stats for user {current_user.id}")

    try:
        # Get total count for user
        total_result = await db.execute(
            select(func.count(Newsletter.id)).where(
                Newsletter.user_id == current_user.id
            )
        )
        total_newsletters = total_result.scalar() or 0

        # Get count by category for user
        category_result = await db.execute(
            select(
                Newsletter.category,
                func.count(Newsletter.id).label('count')
            ).where(
                Newsletter.user_id == current_user.id
            ).group_by(Newsletter.category)
        )
        by_category = {row[0]: row[1] for row in category_result.all()}

        # Get count by source for user
        source_result = await db.execute(
            select(
                Newsletter.source,
                func.count(Newsletter.id).label('count')
            ).where(
                Newsletter.user_id == current_user.id
            ).group_by(Newsletter.source)
        )
        by_source = {row[0]: row[1] for row in source_result.all()}

        # Get date range for user
        date_range_result = await db.execute(
            select(
                func.min(Newsletter.received_date).label('earliest'),
                func.max(Newsletter.received_date).label('latest')
            ).where(
                Newsletter.user_id == current_user.id
            )
        )
        date_range_row = date_range_result.one_or_none()

        date_range = {}
        if date_range_row and date_range_row[0] and date_range_row[1]:
            date_range = {
                "earliest": date_range_row[0],
                "latest": date_range_row[1]
            }

        # Get recent count (last 7 days) for user
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(Newsletter.id)).where(
                and_(
                    Newsletter.user_id == current_user.id,
                    Newsletter.received_date >= seven_days_ago
                )
            )
        )
        recent_count = recent_result.scalar() or 0

        return NewsletterStatsResponse(
            total_newsletters=total_newsletters,
            by_category=by_category,
            by_source=by_source,
            date_range=date_range,
            recent_count=recent_count
        )

    except Exception as e:
        logger.error(f"Error fetching newsletter stats: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching newsletter statistics"
        )


@router.get(
    "/categories/list",
    response_model=list,
    status_code=status.HTTP_200_OK,
    summary="List newsletter categories",
    description="Get list of unique newsletter categories for the authenticated user"
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),  # REQUIRE authentication
) -> list:
    """
    List unique newsletter categories for the authenticated user.

    Only returns categories from newsletters that belong to the user.

    Args:
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        list: List of category names
    """
    logger.info(f"Fetching categories for user {current_user.id}")

    try:
        result = await db.execute(
            select(Newsletter.category)
            .where(Newsletter.user_id == current_user.id)
            .distinct()
            .order_by(Newsletter.category)
        )
        categories = [row[0] for row in result.all()]

        return categories

    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching categories"
        )
