"""Admin routes for database management."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/reset-newsletters-articles")
async def reset_newsletters_and_articles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Reset newsletters and articles tables (development only).

    WARNING: This deletes all newsletters and articles for ALL users.
    """
    try:
        # Delete in order to respect foreign keys
        await db.execute(text("DELETE FROM article_sources"))
        await db.execute(text("DELETE FROM article_bookmarks"))
        await db.execute(text("DELETE FROM articles"))
        await db.execute(text("DELETE FROM newsletters"))
        await db.commit()

        # Get counts to verify
        result = await db.execute(text("SELECT COUNT(*) FROM newsletters"))
        newsletter_count = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) FROM articles"))
        article_count = result.scalar()

        return {
            "status": "success",
            "message": "Tables reset successfully",
            "newsletters_remaining": newsletter_count,
            "articles_remaining": article_count
        }

    except Exception as e:
        await db.rollback()
        return {
            "status": "error",
            "message": str(e)
        }
