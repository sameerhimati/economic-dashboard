"""
Article API endpoints.

Provides access to individual articles extracted from newsletters.
"""
import logging
from typing import Optional, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.article import Article
from app.models.article_source import ArticleSource
from app.models.newsletter import Newsletter
from app.models.user import User
from app.schemas.article import (
    ArticleResponse,
    ArticleWithSources,
    ArticleListResponse,
    ArticlesByCategoryResponse,
    CategorizedArticlesResponse,
)
from app.api.deps import get_current_active_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/articles", tags=["Articles"])


@router.get(
    "/recent",
    response_model=ArticleListResponse | CategorizedArticlesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get recent articles",
    description="Retrieve recent articles for the authenticated user, optionally grouped by category"
)
async def get_recent_articles(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles to return"),
    group_by_category: bool = Query(False, description="Group articles by category"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get recent articles for the authenticated user.

    Only returns articles associated with the authenticated user's account.

    Args:
        limit: Maximum number of articles to return (1-100)
        group_by_category: If True, return categorized array; if False, return flat list
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        ArticleListResponse or CategorizedArticlesResponse: Recent articles
    """
    logger.info(
        f"Fetching recent articles for user {current_user.id}: "
        f"limit={limit}, group_by_category={group_by_category}"
    )

    try:
        # Build query - filter by user_id and load sources with newsletters
        query = (
            select(Article)
            .where(Article.user_id == current_user.id)
            .options(
                selectinload(Article.sources).selectinload(ArticleSource.newsletter)
            )
            .order_by(desc(Article.received_date))
            .limit(limit)
        )

        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()

        if not group_by_category:
            # Return flat list
            article_responses = []
            for article in articles:
                # Calculate source count from loaded sources relationship
                source_count = len(article.sources) if article.sources else 1

                article_response = ArticleResponse.model_validate(article)
                article_response.source_count = source_count
                article_responses.append(article_response)

            logger.info(f"Returning {len(article_responses)} articles for user {current_user.id}")

            return ArticleListResponse(
                articles=article_responses,
                count=len(article_responses),
                page=1,
                page_size=limit
            )
        else:
            # Group by category
            category_dict: Dict[str, List[ArticleResponse]] = {}
            total_articles = 0

            for article in articles:
                # Calculate source count and extract newsletter subjects
                source_count = len(article.sources) if article.sources else 1
                newsletter_subjects = [
                    source.newsletter.subject
                    for source in article.sources
                    if source.newsletter
                ] if article.sources else []

                article_response = ArticleWithSources.model_validate(article)
                article_response.source_count = source_count
                article_response.newsletter_subjects = newsletter_subjects

                if article.category not in category_dict:
                    category_dict[article.category] = []

                category_dict[article.category].append(article_response)
                total_articles += 1

            # Build category response as array
            categories_list = []
            for category, articles_list in category_dict.items():
                categories_list.append(ArticlesByCategoryResponse(
                    category=category,
                    article_count=len(articles_list),
                    articles=articles_list
                ))

            # Get newsletter count
            newsletter_count_stmt = select(func.count(func.distinct(Newsletter.id))).where(
                Newsletter.user_id == current_user.id
            )
            newsletter_count_result = await db.execute(newsletter_count_stmt)
            newsletter_count = newsletter_count_result.scalar() or 0

            logger.info(
                f"Returning {total_articles} articles grouped into {len(categories_list)} categories "
                f"from {newsletter_count} newsletters for user {current_user.id}"
            )

            return CategorizedArticlesResponse(
                categories=categories_list,
                total_articles=total_articles,
                newsletter_count=newsletter_count
            )

    except Exception as e:
        logger.error(f"Error fetching recent articles: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching recent articles"
        )


@router.get(
    "/category/{category}",
    response_model=ArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get articles for specific category",
    description="Retrieve articles for a specific newsletter category with pagination"
)
async def get_articles_by_category(
    category: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ArticleListResponse:
    """
    Get articles for a specific category.

    Returns paginated articles for the specified category, sorted by received_date DESC.
    Only returns articles associated with the authenticated user's account.

    Args:
        category: Newsletter category to filter by
        limit: Maximum number of articles to return (1-100)
        offset: Number of articles to skip for pagination
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        ArticleListResponse: Paginated articles for the category
    """
    logger.info(
        f"Fetching articles for category '{category}' for user {current_user.id}: "
        f"limit={limit}, offset={offset}"
    )

    try:
        # Build query - filter by user_id and category
        query = (
            select(Article)
            .where(
                and_(
                    Article.user_id == current_user.id,
                    Article.category == category
                )
            )
            .options(selectinload(Article.sources))
            .order_by(desc(Article.received_date))
            .offset(offset)
            .limit(limit)
        )

        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()

        # Get total count for this category
        count_query = select(func.count(Article.id)).where(
            and_(
                Article.user_id == current_user.id,
                Article.category == category
            )
        )
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Convert to response format
        article_responses = []
        for article in articles:
            source_count = len(article.sources) if article.sources else 1

            article_response = ArticleResponse.model_validate(article)
            article_response.source_count = source_count
            article_responses.append(article_response)

        # Calculate page number
        page = (offset // limit) + 1 if limit > 0 else 1

        logger.info(
            f"Returning {len(article_responses)} articles (total: {total_count}) "
            f"for category '{category}' for user {current_user.id}"
        )

        return ArticleListResponse(
            articles=article_responses,
            count=len(article_responses),
            page=page,
            page_size=limit
        )

    except Exception as e:
        logger.error(
            f"Error fetching articles for category '{category}': {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching articles for category '{category}'"
        )


@router.get(
    "/search",
    response_model=ArticleListResponse,
    status_code=status.HTTP_200_OK,
    summary="Search articles by headline",
    description="Search user's articles by headline with case-insensitive matching"
)
async def search_articles(
    q: str = Query(..., min_length=1, description="Search query for headline"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ArticleListResponse:
    """
    Search articles by headline.

    Performs case-insensitive search on article headlines.
    Only searches articles associated with the authenticated user's account.

    Args:
        q: Search query string
        limit: Maximum number of articles to return (1-100)
        offset: Number of articles to skip for pagination
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        ArticleListResponse: Search results with pagination
    """
    logger.info(
        f"Searching articles for user {current_user.id}: query='{q}', "
        f"limit={limit}, offset={offset}"
    )

    try:
        # Build query - filter by user_id and search headline (case-insensitive)
        query = (
            select(Article)
            .where(
                and_(
                    Article.user_id == current_user.id,
                    Article.headline.ilike(f"%{q}%")
                )
            )
            .options(selectinload(Article.sources))
            .order_by(desc(Article.received_date))
            .offset(offset)
            .limit(limit)
        )

        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()

        # Get total count for this search
        count_query = select(func.count(Article.id)).where(
            and_(
                Article.user_id == current_user.id,
                Article.headline.ilike(f"%{q}%")
            )
        )
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0

        # Convert to response format
        article_responses = []
        for article in articles:
            source_count = len(article.sources) if article.sources else 1

            article_response = ArticleResponse.model_validate(article)
            article_response.source_count = source_count
            article_responses.append(article_response)

        # Calculate page number
        page = (offset // limit) + 1 if limit > 0 else 1

        logger.info(
            f"Found {len(article_responses)} articles (total: {total_count}) "
            f"matching query '{q}' for user {current_user.id}"
        )

        return ArticleListResponse(
            articles=article_responses,
            count=len(article_responses),
            page=page,
            page_size=limit
        )

    except Exception as e:
        logger.error(
            f"Error searching articles for query '{q}': {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error searching articles"
        )


@router.get(
    "/{id}",
    response_model=ArticleWithSources,
    status_code=status.HTTP_200_OK,
    summary="Get single article with sources",
    description="Retrieve a single article with all its newsletter sources"
)
async def get_article_by_id(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ArticleWithSources:
    """
    Get a single article with all newsletter sources.

    Returns the article with a list of all newsletter subjects that contain this article.
    Only returns articles associated with the authenticated user's account.

    Args:
        id: Article UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        ArticleWithSources: Article with newsletter sources

    Raises:
        HTTPException 404: If article not found or doesn't belong to user
    """
    logger.info(f"Fetching article {id} for user {current_user.id}")

    try:
        # Query article with sources eagerly loaded
        query = (
            select(Article)
            .where(
                and_(
                    Article.id == id,
                    Article.user_id == current_user.id
                )
            )
            .options(selectinload(Article.sources).selectinload(ArticleSource.newsletter))
        )

        result = await db.execute(query)
        article = result.scalar_one_or_none()

        if not article:
            logger.warning(f"Article {id} not found for user {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article not found: {id}"
            )

        # Extract newsletter subjects from sources
        newsletter_subjects = []
        if article.sources:
            for source in article.sources:
                if source.newsletter:
                    newsletter_subjects.append(source.newsletter.subject)

        # Build response
        source_count = len(article.sources) if article.sources else 1

        article_response = ArticleWithSources.model_validate(article)
        article_response.source_count = source_count
        article_response.newsletter_subjects = newsletter_subjects

        logger.info(
            f"Returning article {id} with {len(newsletter_subjects)} newsletter sources "
            f"for user {current_user.id}"
        )

        return article_response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching article {id} for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching article"
        )


@router.post(
    "/cleanup",
    status_code=status.HTTP_200_OK,
    summary="Clean up old articles",
    description="Delete articles older than specified days, preserving bookmarked articles"
)
async def cleanup_old_articles(
    days: int = Query(30, ge=1, le=365, description="Delete articles older than this many days"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Clean up old articles while preserving bookmarked ones.

    Deletes articles older than the specified number of days that are NOT in any bookmark list.
    This helps keep the database clean while preserving important saved articles.

    Args:
        days: Delete articles older than this many days (default: 30)
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        dict: Count of deleted and preserved articles
    """
    from datetime import datetime, timedelta, timezone

    logger.info(f"Starting article cleanup for user {current_user.id}: older than {days} days")

    try:
        # Calculate cutoff date
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        # Find old articles that are NOT bookmarked
        # An article is bookmarked if it appears in article_bookmarks table
        old_articles_query = (
            select(Article)
            .where(
                and_(
                    Article.user_id == current_user.id,
                    Article.received_date < cutoff_date
                )
            )
            .outerjoin(Article.bookmark_lists)
            .group_by(Article.id)
            .having(func.count(Article.bookmark_lists) == 0)
        )

        result = await db.execute(old_articles_query)
        old_articles = result.scalars().all()

        deleted_count = len(old_articles)

        # Delete articles (CASCADE will handle article_sources)
        for article in old_articles:
            await db.delete(article)

        await db.commit()

        # Count preserved bookmarked articles (older than cutoff but still exist)
        preserved_query = (
            select(func.count(Article.id))
            .where(
                and_(
                    Article.user_id == current_user.id,
                    Article.received_date < cutoff_date
                )
            )
        )
        preserved_result = await db.execute(preserved_query)
        preserved_count = preserved_result.scalar() or 0

        logger.info(
            f"Cleanup complete for user {current_user.id}: "
            f"deleted {deleted_count} articles, preserved {preserved_count} bookmarked articles"
        )

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "preserved_count": preserved_count,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"Deleted {deleted_count} articles older than {days} days, preserved {preserved_count} bookmarked articles"
        }

    except Exception as e:
        logger.error(f"Error during article cleanup: {str(e)}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error cleaning up articles"
        )
