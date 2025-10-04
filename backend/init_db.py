#!/usr/bin/env python
"""
Database initialization script.

Creates all tables and seeds initial data including a test user.
Safe to run multiple times (idempotent).

Usage:
    python init_db.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.user import User
from app.models.data_point import DataPoint, SeriesMetadata
from app.models.fred_data import FredDataPoint


async def init_database():
    """
    Initialize the database by creating all tables and seeding initial data.
    """
    print("=" * 80)
    print("DATABASE INITIALIZATION")
    print("=" * 80)
    print(f"\nConnecting to database: {settings.DATABASE_URL[:50]}...")

    # Create async engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )

    try:
        # Create all tables
        print("\n[1/3] Creating database tables...")
        async with engine.begin() as conn:
            # This will create all tables defined in Base.metadata
            await conn.run_sync(Base.metadata.create_all)
        print("     Tables created successfully!")

        # Create async session factory
        async_session_factory = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Seed initial data
        print("\n[2/3] Seeding initial data...")
        async with async_session_factory() as session:
            await seed_test_user(session)
        print("     Initial data seeded successfully!")

        print("\n[3/3] Verifying database setup...")
        async with async_session_factory() as session:
            await verify_setup(session)
        print("     Database verification complete!")

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("=" * 80)
        print("\nTest User Credentials:")
        print("  Email:    test@example.com")
        print("  Password: test123")
        print("\nYou can now start the application with:")
        print("  uvicorn app.main:app --reload")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR: Database initialization failed!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Clean up
        await engine.dispose()


async def seed_test_user(session: AsyncSession):
    """
    Create a test user if it doesn't already exist.

    Args:
        session: Database session
    """
    # Check if test user already exists
    result = await session.execute(
        select(User).where(User.email == "test@example.com")
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print("     - Test user already exists, skipping...")
        return

    # Create test user
    test_user = User(
        email="test@example.com",
        hashed_password=get_password_hash("test123"),
        is_active=True,
        is_superuser=False,
        full_name="Test User",
    )

    session.add(test_user)
    await session.commit()
    await session.refresh(test_user)

    print(f"     - Created test user: {test_user.email} (ID: {test_user.id})")


async def verify_setup(session: AsyncSession):
    """
    Verify that the database setup is correct.

    Args:
        session: Database session
    """
    # Count users
    result = await session.execute(select(User))
    user_count = len(result.scalars().all())
    print(f"     - Users table: {user_count} records")

    # Count data points
    result = await session.execute(select(DataPoint))
    data_point_count = len(result.scalars().all())
    print(f"     - DataPoints table: {data_point_count} records")

    # Count series metadata
    result = await session.execute(select(SeriesMetadata))
    series_count = len(result.scalars().all())
    print(f"     - SeriesMetadata table: {series_count} records")

    # Count FRED data points
    result = await session.execute(select(FredDataPoint))
    fred_count = len(result.scalars().all())
    print(f"     - FredDataPoints table: {fred_count} records")


async def reset_database():
    """
    Drop all tables and recreate them (DESTRUCTIVE).

    Only use this for development/testing!
    """
    print("=" * 80)
    print("DATABASE RESET (DESTRUCTIVE)")
    print("=" * 80)
    print("\nWARNING: This will delete all data in the database!")

    if settings.ENVIRONMENT == "production":
        print("\nERROR: Cannot reset database in production environment!")
        sys.exit(1)

    response = input("\nAre you sure you want to continue? (yes/no): ")
    if response.lower() != "yes":
        print("Database reset cancelled.")
        sys.exit(0)

    print(f"\nConnecting to database: {settings.DATABASE_URL[:50]}...")

    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
    )

    try:
        print("\nDropping all tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("All tables dropped!")

        print("\nRecreating all tables...")
        await init_database()

    except Exception as e:
        print(f"\nERROR: Database reset failed!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


def main():
    """Main entry point."""
    # Check if reset flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        asyncio.run(reset_database())
    else:
        asyncio.run(init_database())


if __name__ == "__main__":
    main()
