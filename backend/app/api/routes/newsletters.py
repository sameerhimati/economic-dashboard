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
from app.services.email_service import get_email_service, EmailService, EmailServiceError
from app.api.deps import get_current_active_user, get_optional_current_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/newsletters", tags=["Newsletters"])


@router.get(
    "/recent",
    response_model=NewsletterListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recent newsletters",
    description="Retrieve recent newsletters with optional category filtering"
)
async def get_recent_newsletters(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of newsletters to return"),
    category: Optional[str] = Query(None, description="Filter by newsletter category"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> NewsletterListResponse:
    """
    Get recent newsletters.

    Args:
        limit: Maximum number of newsletters to return (1-100)
        category: Optional category filter
        db: Database session
        current_user: Optional authenticated user

    Returns:
        NewsletterListResponse: List of recent newsletters
    """
    logger.info(
        f"Fetching recent newsletters: limit={limit}, category={category}, "
        f"user={current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Build query
        query = select(Newsletter).order_by(Newsletter.received_date.desc())

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
    description="Search newsletters by keyword in subject, content, or key points"
)
async def search_newsletters(
    query: str = Query(..., min_length=1, description="Search query"),
    start_date: Optional[datetime] = Query(None, description="Start date filter (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="End date filter (ISO format)"),
    category: Optional[str] = Query(None, description="Category filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> NewsletterSearchResponse:
    """
    Search newsletters by keyword.

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
        current_user: Optional authenticated user

    Returns:
        NewsletterSearchResponse: Search results with pagination
    """
    logger.info(
        f"Searching newsletters: query='{query}', category={category}, "
        f"dates={start_date} to {end_date}, page={page}, "
        f"user={current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Build base query with search conditions
        search_pattern = f"%{query}%"

        # Search in subject, content_text, and convert key_points to text for searching
        base_conditions = or_(
            Newsletter.subject.ilike(search_pattern),
            Newsletter.content_text.ilike(search_pattern),
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
    description="Trigger manual email fetch from IMAP server (requires authentication)"
)
async def fetch_newsletters(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    db: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> NewsletterFetchResponse:
    """
    Manually trigger newsletter fetch from email.

    Connects to IMAP server, fetches emails from Bisnow, parses content,
    and stores in database. Requires authentication.

    Args:
        days: Number of days to look back (1-30)
        db: Database session
        email_service: Email service instance
        current_user: Authenticated user

    Returns:
        NewsletterFetchResponse: Summary of fetch operation

    Raises:
        HTTPException 400: If days parameter is invalid
        HTTPException 500: If fetch operation fails
    """
    logger.info(f"Manual newsletter fetch triggered by user: {current_user.email}, days={days}")

    if days < 1 or days > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Days parameter must be between 1 and 30"
        )

    try:
        # Fetch and store emails
        result = await email_service.fetch_and_store_emails(
            db=db,
            days=days,
            sender_filter=['@bisnow.com', '@mail.bisnow.com']
        )

        if result["status"] != "success":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Newsletter fetch failed"
            )

        logger.info(
            f"Newsletter fetch completed: {result['stored']} stored, "
            f"{result['skipped']} skipped"
        )

        return NewsletterFetchResponse(
            status=result["status"],
            fetched=result["fetched"],
            stored=result["stored"],
            skipped=result["skipped"],
            timestamp=result["timestamp"]
        )

    except EmailServiceError as e:
        logger.error(f"Email service error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email service error: {e.message}"
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error fetching newsletters: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching newsletters: {str(e)}"
        )


@router.get(
    "/{newsletter_id}",
    response_model=NewsletterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get newsletter by ID",
    description="Retrieve a single newsletter with full content by UUID"
)
async def get_newsletter_by_id(
    newsletter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> NewsletterResponse:
    """
    Get a single newsletter by ID.

    Returns full newsletter details including HTML content, text content,
    and extracted key points.

    Args:
        newsletter_id: Newsletter UUID
        db: Database session
        current_user: Optional authenticated user

    Returns:
        NewsletterResponse: Full newsletter details

    Raises:
        HTTPException 404: If newsletter not found
    """
    logger.info(
        f"Fetching newsletter by ID: {newsletter_id}, "
        f"user={current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Query newsletter
        result = await db.execute(
            select(Newsletter).where(Newsletter.id == newsletter_id)
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
    description="Get overview statistics about stored newsletters"
)
async def get_newsletter_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user),
) -> NewsletterStatsResponse:
    """
    Get newsletter statistics.

    Provides overview of:
    - Total newsletter count
    - Count by category
    - Count by source
    - Date range
    - Recent activity (last 7 days)

    Args:
        db: Database session
        current_user: Optional authenticated user

    Returns:
        NewsletterStatsResponse: Newsletter statistics
    """
    logger.info(
        f"Fetching newsletter stats, "
        f"user={current_user.email if current_user else 'anonymous'}"
    )

    try:
        # Get total count
        total_result = await db.execute(select(func.count(Newsletter.id)))
        total_newsletters = total_result.scalar() or 0

        # Get count by category
        category_result = await db.execute(
            select(
                Newsletter.category,
                func.count(Newsletter.id).label('count')
            ).group_by(Newsletter.category)
        )
        by_category = {row[0]: row[1] for row in category_result.all()}

        # Get count by source
        source_result = await db.execute(
            select(
                Newsletter.source,
                func.count(Newsletter.id).label('count')
            ).group_by(Newsletter.source)
        )
        by_source = {row[0]: row[1] for row in source_result.all()}

        # Get date range
        date_range_result = await db.execute(
            select(
                func.min(Newsletter.received_date).label('earliest'),
                func.max(Newsletter.received_date).label('latest')
            )
        )
        date_range_row = date_range_result.one_or_none()

        date_range = {}
        if date_range_row and date_range_row[0] and date_range_row[1]:
            date_range = {
                "earliest": date_range_row[0],
                "latest": date_range_row[1]
            }

        # Get recent count (last 7 days)
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_result = await db.execute(
            select(func.count(Newsletter.id)).where(
                Newsletter.received_date >= seven_days_ago
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
    summary="List all newsletter categories",
    description="Get list of all unique newsletter categories"
)
async def list_categories(
    db: AsyncSession = Depends(get_db),
) -> list:
    """
    List all unique newsletter categories.

    Args:
        db: Database session

    Returns:
        list: List of category names
    """
    try:
        result = await db.execute(
            select(Newsletter.category)
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
