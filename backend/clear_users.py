#!/usr/bin/env python3
"""
Script to clear all users from the database.
Run this in Railway using: railway run --service backend python clear_users.py
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine, async_session_maker


async def clear_users():
    """Clear all users and related data from database."""
    async with engine.begin() as conn:
        # Delete in order due to foreign key constraints
        print("Deleting newsletters...")
        await conn.execute(text("DELETE FROM newsletters"))

        print("Deleting users...")
        await conn.execute(text("DELETE FROM users"))

        print("✅ All users and newsletters deleted successfully!")


if __name__ == "__main__":
    print("🗑️  Clearing all users from database...")
    asyncio.run(clear_users())
