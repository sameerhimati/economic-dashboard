#!/usr/bin/env python3
"""
Clear all newsletter and bookmark data to prepare for fresh article-based fetch.

This script deletes all existing newsletters and bookmark lists from the database.
It should be run AFTER the migration to the article-centric schema but BEFORE
fetching new newsletters.

Usage:
    python scripts/clear_newsletter_data.py

Warning: This will delete all newsletters and bookmarks. This action cannot be undone.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import init_db, close_db, get_session_maker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def clear_newsletter_data() -> None:
    """
    Clear all newsletter and bookmark data from the database.

    Deletes:
    - All bookmark lists (will cascade to article_bookmarks)
    - All newsletters (will cascade to articles and article_sources)

    This prepares the database for a fresh fetch with the new article-centric schema.
    """
    try:
        # Initialize database connection
        logger.info("Initializing database connection...")
        await init_db()

        # Get session maker
        session_maker = get_session_maker()

        # Create session and execute cleanup
        async with session_maker() as db:
            logger.info("Starting data cleanup...")

            # Count existing data before deletion
            bookmark_count_result = await db.execute(text('SELECT COUNT(*) FROM bookmark_lists'))
            bookmark_count = bookmark_count_result.scalar()

            newsletter_count_result = await db.execute(text('SELECT COUNT(*) FROM newsletters'))
            newsletter_count = newsletter_count_result.scalar()

            logger.info(f"Found {bookmark_count} bookmark lists and {newsletter_count} newsletters")

            # Delete bookmark lists (will cascade to article_bookmarks if any exist)
            logger.info("Deleting all bookmark lists...")
            await db.execute(text('DELETE FROM bookmark_lists'))

            # Delete newsletters (will cascade to articles and article_sources)
            logger.info("Deleting all newsletters (and cascading to articles)...")
            await db.execute(text('DELETE FROM newsletters'))

            # Commit the transaction
            await db.commit()

            logger.info("Data cleanup completed successfully!")
            logger.info(f"Deleted {bookmark_count} bookmark lists")
            logger.info(f"Deleted {newsletter_count} newsletters (plus all related articles)")

        # Close database connection
        await close_db()
        logger.info("Database connection closed")

    except Exception as e:
        logger.error(f"Error during data cleanup: {str(e)}", exc_info=True)
        raise


def main() -> None:
    """Main entry point for the script."""
    logger.info("=" * 80)
    logger.info("Newsletter Data Cleanup Script")
    logger.info("=" * 80)
    logger.info("WARNING: This will delete ALL newsletters and bookmark lists!")
    logger.info("This action cannot be undone.")
    logger.info("=" * 80)

    # Run the async cleanup function
    try:
        asyncio.run(clear_newsletter_data())
        logger.info("=" * 80)
        logger.info("Cleanup completed successfully!")
        logger.info("You can now fetch newsletters with the new article-centric schema.")
        logger.info("=" * 80)
        sys.exit(0)
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"Cleanup failed: {str(e)}")
        logger.error("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()
