"""
Bookmark API endpoints.

Provides endpoints for managing bookmark lists and organizing newsletters.
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.bookmark_list import BookmarkList
from app.models.article import Article
from app.models.article_bookmark import ArticleBookmark
from app.models.newsletter import Newsletter
from app.models.newsletter_bookmark import NewsletterBookmark
from app.models.user import User
from app.schemas.bookmark import (
    BookmarkListCreate,
    BookmarkListUpdate,
    BookmarkListResponse,
    BookmarkListSummary,
    BookmarkListsResponse,
    ArticleBookmarkResponse,
    BookmarkListArticlesResponse,
    NewsletterBookmarkResponse,
    BookmarkListNewslettersResponse,
    BookmarkOperationResponse,
)
from app.api.deps import get_current_active_user

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/bookmarks", tags=["Bookmarks"])


@router.get(
    "/lists",
    response_model=BookmarkListsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user's bookmark lists",
    description="Retrieve all bookmark lists for the authenticated user with newsletter counts"
)
async def get_bookmark_lists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkListsResponse:
    """
    Get all bookmark lists for the authenticated user.

    Returns all bookmark lists owned by the user, sorted by creation date (newest first).
    Each list includes the count of newsletters it contains.

    Args:
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkListsResponse: List of bookmark lists with counts
    """
    logger.info(f"Fetching bookmark lists for user {current_user.id}")

    try:
        # Query bookmark lists for this user with article count
        # Use a subquery to count articles in each list
        stmt = (
            select(
                BookmarkList,
                func.count(ArticleBookmark.article_id).label('article_count')
            )
            .outerjoin(
                ArticleBookmark,
                BookmarkList.id == ArticleBookmark.bookmark_list_id
            )
            .where(BookmarkList.user_id == current_user.id)
            .group_by(BookmarkList.id)
            .order_by(desc(BookmarkList.created_at))
        )

        result = await db.execute(stmt)
        rows = result.all()

        # Build response with counts
        bookmark_lists = []
        for row in rows:
            bookmark_list = row[0]
            article_count = row[1]

            bookmark_lists.append(
                BookmarkListSummary(
                    id=bookmark_list.id,
                    name=bookmark_list.name,
                    article_count=article_count,
                    created_at=bookmark_list.created_at,
                    updated_at=bookmark_list.updated_at,
                )
            )

        logger.info(f"Found {len(bookmark_lists)} bookmark lists for user {current_user.id}")

        return BookmarkListsResponse(
            bookmark_lists=bookmark_lists,
            count=len(bookmark_lists)
        )

    except Exception as e:
        logger.error(
            f"Error fetching bookmark lists for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching bookmark lists"
        )


@router.post(
    "/lists",
    response_model=BookmarkListResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new bookmark list",
    description="Create a new bookmark list for the authenticated user (max 10 lists per user)"
)
async def create_bookmark_list(
    bookmark_data: BookmarkListCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkListResponse:
    """
    Create a new bookmark list for the authenticated user.

    Users can create up to 10 bookmark lists. List names must be unique per user.

    Args:
        bookmark_data: Bookmark list creation data
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkListResponse: Created bookmark list

    Raises:
        HTTPException 400: If user has reached max lists (10)
        HTTPException 409: If list name already exists for user
    """
    logger.info(f"Creating bookmark list '{bookmark_data.name}' for user {current_user.id}")

    try:
        # Check if user has reached the maximum number of lists (10)
        count_stmt = select(func.count(BookmarkList.id)).where(
            BookmarkList.user_id == current_user.id
        )
        count_result = await db.execute(count_stmt)
        list_count = count_result.scalar() or 0

        if list_count >= 10:
            logger.warning(
                f"User {current_user.id} attempted to create bookmark list "
                f"but already has {list_count} lists (max 10)"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum number of bookmark lists reached (10). Please delete an existing list before creating a new one."
            )

        # Check if a list with this name already exists for the user
        existing_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.user_id == current_user.id,
                BookmarkList.name == bookmark_data.name
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_list = existing_result.scalar_one_or_none()

        if existing_list:
            logger.warning(
                f"User {current_user.id} attempted to create bookmark list "
                f"with duplicate name '{bookmark_data.name}'"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A bookmark list with the name '{bookmark_data.name}' already exists"
            )

        # Create new bookmark list
        new_list = BookmarkList(
            user_id=current_user.id,
            name=bookmark_data.name
        )

        db.add(new_list)
        await db.commit()
        await db.refresh(new_list)

        logger.info(
            f"Successfully created bookmark list '{new_list.name}' "
            f"(id={new_list.id}) for user {current_user.id}"
        )

        return BookmarkListResponse(
            id=new_list.id,
            user_id=new_list.user_id,
            name=new_list.name,
            newsletter_count=0,  # New list has no newsletters
            created_at=new_list.created_at,
            updated_at=new_list.updated_at,
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error creating bookmark list for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating bookmark list"
        )


@router.put(
    "/lists/{list_id}",
    response_model=BookmarkListResponse,
    status_code=status.HTTP_200_OK,
    summary="Update bookmark list name",
    description="Update the name of a bookmark list owned by the authenticated user"
)
async def update_bookmark_list(
    list_id: UUID,
    bookmark_data: BookmarkListUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkListResponse:
    """
    Update a bookmark list's name.

    Only the list owner can update it. The new name must be unique among the user's lists.

    Args:
        list_id: Bookmark list UUID
        bookmark_data: Updated bookmark list data
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkListResponse: Updated bookmark list

    Raises:
        HTTPException 404: If list not found or doesn't belong to user
        HTTPException 409: If new name conflicts with existing list
    """
    logger.info(f"Updating bookmark list {list_id} for user {current_user.id}")

    try:
        # Fetch the bookmark list and verify ownership
        stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        bookmark_list = result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # If name is changing, check for conflicts
        if bookmark_data.name != bookmark_list.name:
            conflict_stmt = select(BookmarkList).where(
                and_(
                    BookmarkList.user_id == current_user.id,
                    BookmarkList.name == bookmark_data.name,
                    BookmarkList.id != list_id  # Exclude current list
                )
            )
            conflict_result = await db.execute(conflict_stmt)
            conflict_list = conflict_result.scalar_one_or_none()

            if conflict_list:
                logger.warning(
                    f"User {current_user.id} attempted to rename list {list_id} "
                    f"to '{bookmark_data.name}' which conflicts with existing list"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"A bookmark list with the name '{bookmark_data.name}' already exists"
                )

        # Update the list
        old_name = bookmark_list.name
        bookmark_list.name = bookmark_data.name
        await db.commit()
        await db.refresh(bookmark_list)

        # Get newsletter count
        count_stmt = select(func.count(NewsletterBookmark.newsletter_id)).where(
            NewsletterBookmark.bookmark_list_id == list_id
        )
        count_result = await db.execute(count_stmt)
        newsletter_count = count_result.scalar() or 0

        logger.info(
            f"Successfully updated bookmark list {list_id} for user {current_user.id}: "
            f"'{old_name}' -> '{bookmark_list.name}'"
        )

        return BookmarkListResponse(
            id=bookmark_list.id,
            user_id=bookmark_list.user_id,
            name=bookmark_list.name,
            newsletter_count=newsletter_count,
            created_at=bookmark_list.created_at,
            updated_at=bookmark_list.updated_at,
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error updating bookmark list {list_id} for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating bookmark list"
        )


@router.delete(
    "/lists/{list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete bookmark list",
    description="Delete a bookmark list owned by the authenticated user (CASCADE deletes newsletter associations)"
)
async def delete_bookmark_list(
    list_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Delete a bookmark list.

    Only the list owner can delete it. CASCADE delete will automatically remove
    all article_bookmarks and newsletter_bookmarks entries associated with this list.

    Args:
        list_id: Bookmark list UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Raises:
        HTTPException 404: If list not found or doesn't belong to user
    """
    logger.info(f"Deleting bookmark list {list_id} for user {current_user.id}")

    try:
        # Fetch the bookmark list and verify ownership
        stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        result = await db.execute(stmt)
        bookmark_list = result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Delete the list (CASCADE will handle newsletter_bookmarks)
        await db.delete(bookmark_list)
        await db.commit()

        logger.info(
            f"Successfully deleted bookmark list '{bookmark_list.name}' "
            f"(id={list_id}) for user {current_user.id}"
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error deleting bookmark list {list_id} for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting bookmark list"
        )


@router.post(
    "/lists/{list_id}/newsletters/{newsletter_id}",
    response_model=BookmarkOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Add newsletter to bookmark list",
    description="Add a newsletter to a bookmark list (both must belong to authenticated user)"
)
async def add_newsletter_to_list(
    list_id: UUID,
    newsletter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkOperationResponse:
    """
    Add a newsletter to a bookmark list.

    Both the bookmark list and newsletter must belong to the authenticated user.
    If the newsletter is already in the list, returns success (idempotent operation).

    Args:
        list_id: Bookmark list UUID
        newsletter_id: Newsletter UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkOperationResponse: Operation result

    Raises:
        HTTPException 404: If list or newsletter not found or doesn't belong to user
    """
    logger.info(
        f"Adding newsletter {newsletter_id} to bookmark list {list_id} "
        f"for user {current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Verify newsletter exists and belongs to user
        newsletter_stmt = select(Newsletter).where(
            and_(
                Newsletter.id == newsletter_id,
                Newsletter.user_id == current_user.id
            )
        )
        newsletter_result = await db.execute(newsletter_stmt)
        newsletter = newsletter_result.scalar_one_or_none()

        if not newsletter:
            logger.warning(
                f"Newsletter {newsletter_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter not found: {newsletter_id}"
            )

        # Check if association already exists
        existing_stmt = select(NewsletterBookmark).where(
            and_(
                NewsletterBookmark.bookmark_list_id == list_id,
                NewsletterBookmark.newsletter_id == newsletter_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_bookmark = existing_result.scalar_one_or_none()

        if existing_bookmark:
            logger.info(
                f"Newsletter {newsletter_id} already in bookmark list {list_id} "
                f"for user {current_user.id} - returning success"
            )
            return BookmarkOperationResponse(
                success=True,
                message="Newsletter already in bookmark list",
                bookmark_list_id=list_id,
                newsletter_id=newsletter_id
            )

        # Create new association
        new_bookmark = NewsletterBookmark(
            bookmark_list_id=list_id,
            newsletter_id=newsletter_id
        )

        db.add(new_bookmark)
        await db.commit()

        logger.info(
            f"Successfully added newsletter {newsletter_id} to bookmark list "
            f"'{bookmark_list.name}' (id={list_id}) for user {current_user.id}"
        )

        return BookmarkOperationResponse(
            success=True,
            message=f"Newsletter added to bookmark list '{bookmark_list.name}'",
            bookmark_list_id=list_id,
            newsletter_id=newsletter_id
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error adding newsletter {newsletter_id} to bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding newsletter to bookmark list"
        )


@router.delete(
    "/lists/{list_id}/newsletters/{newsletter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove newsletter from bookmark list",
    description="Remove a newsletter from a bookmark list (list must belong to authenticated user)"
)
async def remove_newsletter_from_list(
    list_id: UUID,
    newsletter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Remove a newsletter from a bookmark list.

    The bookmark list must belong to the authenticated user.

    Args:
        list_id: Bookmark list UUID
        newsletter_id: Newsletter UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Raises:
        HTTPException 404: If list not found or association doesn't exist
    """
    logger.info(
        f"Removing newsletter {newsletter_id} from bookmark list {list_id} "
        f"for user {current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Check if association exists
        existing_stmt = select(NewsletterBookmark).where(
            and_(
                NewsletterBookmark.bookmark_list_id == list_id,
                NewsletterBookmark.newsletter_id == newsletter_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_bookmark = existing_result.scalar_one_or_none()

        if not existing_bookmark:
            logger.warning(
                f"Newsletter {newsletter_id} not found in bookmark list {list_id} "
                f"for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Newsletter not found in bookmark list"
            )

        # Delete the association
        delete_stmt = delete(NewsletterBookmark).where(
            and_(
                NewsletterBookmark.bookmark_list_id == list_id,
                NewsletterBookmark.newsletter_id == newsletter_id
            )
        )
        await db.execute(delete_stmt)
        await db.commit()

        logger.info(
            f"Successfully removed newsletter {newsletter_id} from bookmark list "
            f"'{bookmark_list.name}' (id={list_id}) for user {current_user.id}"
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error removing newsletter {newsletter_id} from bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing newsletter from bookmark list"
        )


@router.get(
    "/lists/{list_id}/newsletters",
    response_model=BookmarkListNewslettersResponse,
    status_code=status.HTTP_200_OK,
    summary="Get newsletters in a bookmark list",
    description="Retrieve all newsletters in a bookmark list with pagination (list must belong to authenticated user)"
)
async def get_list_newsletters(
    list_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkListNewslettersResponse:
    """
    Get all newsletters in a bookmark list.

    Returns paginated newsletters sorted by date added (newest first).
    The bookmark list must belong to the authenticated user.

    Args:
        list_id: Bookmark list UUID
        page: Page number (starts at 1)
        page_size: Number of items per page (1-100)
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkListNewslettersResponse: Newsletters in the list with pagination

    Raises:
        HTTPException 404: If list not found or doesn't belong to user
    """
    logger.info(
        f"Fetching newsletters for bookmark list {list_id}, "
        f"page={page}, page_size={page_size}, user={current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Get total count of newsletters in this list
        count_stmt = select(func.count(NewsletterBookmark.newsletter_id)).where(
            NewsletterBookmark.bookmark_list_id == list_id
        )
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Query newsletters in this list with pagination
        offset = (page - 1) * page_size

        newsletters_stmt = (
            select(Newsletter, NewsletterBookmark.created_at)
            .join(
                NewsletterBookmark,
                Newsletter.id == NewsletterBookmark.newsletter_id
            )
            .where(NewsletterBookmark.bookmark_list_id == list_id)
            .order_by(desc(NewsletterBookmark.created_at))  # Sort by date added
            .offset(offset)
            .limit(page_size)
        )

        newsletters_result = await db.execute(newsletters_stmt)
        rows = newsletters_result.all()

        # Build newsletter response
        newsletters = []
        for row in rows:
            newsletter = row[0]
            bookmarked_at = row[1]

            newsletters.append(
                NewsletterBookmarkResponse(
                    id=newsletter.id,
                    source=newsletter.source,
                    category=newsletter.category,
                    subject=newsletter.subject,
                    received_date=newsletter.received_date,
                    created_at=newsletter.created_at,
                    bookmarked_at=bookmarked_at,
                )
            )

        logger.info(
            f"Found {len(newsletters)} newsletters in bookmark list '{bookmark_list.name}' "
            f"(total: {total_count}) for user {current_user.id}"
        )

        return BookmarkListNewslettersResponse(
            bookmark_list_id=list_id,
            bookmark_list_name=bookmark_list.name,
            newsletters=newsletters,
            count=len(newsletters),
            total_count=total_count,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching newsletters for bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching newsletters from bookmark list"
        )


# ===== ARTICLE BOOKMARK ENDPOINTS =====
# These are the new primary endpoints for bookmarking individual articles


@router.post(
    "/lists/{list_id}/articles/{article_id}",
    response_model=BookmarkOperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Add article to bookmark list",
    description="Add an article to a bookmark list (both must belong to authenticated user)"
)
async def add_article_to_list(
    list_id: UUID,
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkOperationResponse:
    """
    Add an article to a bookmark list.

    Both the bookmark list and article must belong to the authenticated user.
    If the article is already in the list, returns success (idempotent operation).

    Args:
        list_id: Bookmark list UUID
        article_id: Article UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkOperationResponse: Operation result

    Raises:
        HTTPException 404: If list or article not found or doesn't belong to user
    """
    logger.info(
        f"Adding article {article_id} to bookmark list {list_id} "
        f"for user {current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Verify article exists and belongs to user
        article_stmt = select(Article).where(
            and_(
                Article.id == article_id,
                Article.user_id == current_user.id
            )
        )
        article_result = await db.execute(article_stmt)
        article = article_result.scalar_one_or_none()

        if not article:
            logger.warning(
                f"Article {article_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article not found: {article_id}"
            )

        # Check if association already exists
        existing_stmt = select(ArticleBookmark).where(
            and_(
                ArticleBookmark.bookmark_list_id == list_id,
                ArticleBookmark.article_id == article_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_bookmark = existing_result.scalar_one_or_none()

        if existing_bookmark:
            logger.info(
                f"Article {article_id} already in bookmark list {list_id} "
                f"for user {current_user.id} - returning success"
            )
            return BookmarkOperationResponse(
                success=True,
                message="Article already in bookmark list",
                bookmark_list_id=list_id,
                article_id=article_id
            )

        # Create new association
        new_bookmark = ArticleBookmark(
            bookmark_list_id=list_id,
            article_id=article_id
        )

        db.add(new_bookmark)
        await db.commit()

        logger.info(
            f"Successfully added article {article_id} to bookmark list "
            f"'{bookmark_list.name}' (id={list_id}) for user {current_user.id}"
        )

        return BookmarkOperationResponse(
            success=True,
            message=f"Article added to bookmark list '{bookmark_list.name}'",
            bookmark_list_id=list_id,
            article_id=article_id
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error adding article {article_id} to bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding article to bookmark list"
        )


@router.delete(
    "/lists/{list_id}/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove article from bookmark list",
    description="Remove an article from a bookmark list (list must belong to authenticated user)"
)
async def remove_article_from_list(
    list_id: UUID,
    article_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Remove an article from a bookmark list.

    The bookmark list must belong to the authenticated user.

    Args:
        list_id: Bookmark list UUID
        article_id: Article UUID
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Raises:
        HTTPException 404: If list not found or association doesn't exist
    """
    logger.info(
        f"Removing article {article_id} from bookmark list {list_id} "
        f"for user {current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Check if association exists
        existing_stmt = select(ArticleBookmark).where(
            and_(
                ArticleBookmark.bookmark_list_id == list_id,
                ArticleBookmark.article_id == article_id
            )
        )
        existing_result = await db.execute(existing_stmt)
        existing_bookmark = existing_result.scalar_one_or_none()

        if not existing_bookmark:
            logger.warning(
                f"Article {article_id} not found in bookmark list {list_id} "
                f"for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Article not found in bookmark list"
            )

        # Delete the association
        delete_stmt = delete(ArticleBookmark).where(
            and_(
                ArticleBookmark.bookmark_list_id == list_id,
                ArticleBookmark.article_id == article_id
            )
        )
        await db.execute(delete_stmt)
        await db.commit()

        logger.info(
            f"Successfully removed article {article_id} from bookmark list "
            f"'{bookmark_list.name}' (id={list_id}) for user {current_user.id}"
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error removing article {article_id} from bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing article from bookmark list"
        )


@router.get(
    "/lists/{list_id}/articles",
    response_model=BookmarkListArticlesResponse,
    status_code=status.HTTP_200_OK,
    summary="Get articles in a bookmark list",
    description="Retrieve all articles in a bookmark list with pagination (list must belong to authenticated user)"
)
async def get_list_articles(
    list_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> BookmarkListArticlesResponse:
    """
    Get all articles in a bookmark list.

    Returns paginated articles sorted by date added (newest first).
    The bookmark list must belong to the authenticated user.

    Args:
        list_id: Bookmark list UUID
        page: Page number (starts at 1)
        page_size: Number of items per page (1-100)
        db: Database session
        current_user: Authenticated user (REQUIRED)

    Returns:
        BookmarkListArticlesResponse: Articles in the list with pagination

    Raises:
        HTTPException 404: If list not found or doesn't belong to user
    """
    logger.info(
        f"Fetching articles for bookmark list {list_id}, "
        f"page={page}, page_size={page_size}, user={current_user.id}"
    )

    try:
        # Verify bookmark list exists and belongs to user
        list_stmt = select(BookmarkList).where(
            and_(
                BookmarkList.id == list_id,
                BookmarkList.user_id == current_user.id
            )
        )
        list_result = await db.execute(list_stmt)
        bookmark_list = list_result.scalar_one_or_none()

        if not bookmark_list:
            logger.warning(
                f"Bookmark list {list_id} not found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bookmark list not found: {list_id}"
            )

        # Get total count of articles in this list
        count_stmt = select(func.count(ArticleBookmark.article_id)).where(
            ArticleBookmark.bookmark_list_id == list_id
        )
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar() or 0

        # Query articles in this list with pagination
        offset = (page - 1) * page_size

        articles_stmt = (
            select(Article, ArticleBookmark.created_at)
            .join(
                ArticleBookmark,
                Article.id == ArticleBookmark.article_id
            )
            .where(ArticleBookmark.bookmark_list_id == list_id)
            .order_by(desc(ArticleBookmark.created_at))  # Sort by date added
            .offset(offset)
            .limit(page_size)
        )

        articles_result = await db.execute(articles_stmt)
        rows = articles_result.all()

        # Build article response
        articles = []
        for row in rows:
            article = row[0]
            bookmarked_at = row[1]

            articles.append(
                ArticleBookmarkResponse(
                    id=article.id,
                    headline=article.headline,
                    url=article.url,
                    category=article.category,
                    received_date=article.received_date,
                    position=article.position,
                    created_at=article.created_at,
                    bookmarked_at=bookmarked_at,
                )
            )

        logger.info(
            f"Found {len(articles)} articles in bookmark list '{bookmark_list.name}' "
            f"(total: {total_count}) for user {current_user.id}"
        )

        return BookmarkListArticlesResponse(
            bookmark_list_id=list_id,
            bookmark_list_name=bookmark_list.name,
            articles=articles,
            count=len(articles),
            total_count=total_count,
            page=page,
            page_size=page_size
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching articles for bookmark list {list_id} "
            f"for user {current_user.id}: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching articles from bookmark list"
        )
