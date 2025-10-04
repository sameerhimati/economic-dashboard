#!/usr/bin/env python3
"""
Configuration validation script.

Run this script to validate your backend configuration before deploying.
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)-8s %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run all configuration checks."""
    logger.info("=" * 80)
    logger.info("Economic Dashboard Backend Configuration Check")
    logger.info("=" * 80)

    errors = []
    warnings = []

    # Check 1: Import configuration
    logger.info("\n[1/8] Checking configuration imports...")
    try:
        from app.core.config import settings
        logger.info("✓ Configuration imported successfully")
    except Exception as e:
        errors.append(f"Failed to import configuration: {e}")
        logger.error(f"✗ Failed to import configuration: {e}")
        return 1

    # Check 2: Validate configuration
    logger.info("\n[2/8] Validating configuration values...")
    try:
        from app.core.validation import validate_all_config
        validate_all_config()
        logger.info("✓ Configuration validation passed")
    except Exception as e:
        errors.append(f"Configuration validation failed: {e}")
        logger.error(f"✗ Configuration validation failed: {e}")

    # Check 3: Import models
    logger.info("\n[3/8] Checking database models...")
    try:
        from app.models.base import Base
        from app.models.user import User
        from app.models.data_point import DataPoint, SeriesMetadata
        from app.models.fred_data import FredDataPoint

        tables = list(Base.metadata.tables.keys())
        logger.info(f"✓ All models imported successfully")
        logger.info(f"  Tables: {', '.join(tables)}")
    except Exception as e:
        errors.append(f"Failed to import models: {e}")
        logger.error(f"✗ Failed to import models: {e}")

    # Check 4: Import schemas
    logger.info("\n[4/8] Checking Pydantic schemas...")
    try:
        from app.schemas.user import UserCreate, UserLogin, UserResponse
        from app.schemas.data import (
            DataPointResponse,
            FredDataPointResponse,
            CurrentDataResponse
        )
        logger.info("✓ All schemas imported successfully")
    except Exception as e:
        errors.append(f"Failed to import schemas: {e}")
        logger.error(f"✗ Failed to import schemas: {e}")

    # Check 5: Import routers
    logger.info("\n[5/8] Checking API routers...")
    try:
        from app.api.routes import health_router, auth_router, data_router
        logger.info("✓ All routers imported successfully")
    except Exception as e:
        errors.append(f"Failed to import routers: {e}")
        logger.error(f"✗ Failed to import routers: {e}")

    # Check 6: Create FastAPI app
    logger.info("\n[6/8] Checking FastAPI application...")
    try:
        from app.main import app
        route_count = len([r for r in app.routes if hasattr(r, 'path')])
        logger.info(f"✓ FastAPI app created successfully")
        logger.info(f"  Routes registered: {route_count}")
    except Exception as e:
        errors.append(f"Failed to create FastAPI app: {e}")
        logger.error(f"✗ Failed to create FastAPI app: {e}")

    # Check 7: Check Alembic configuration
    logger.info("\n[7/8] Checking Alembic configuration...")
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        alembic_cfg = Config("alembic.ini")
        script_dir = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(script_dir.walk_revisions())

        logger.info(f"✓ Alembic configuration valid")
        logger.info(f"  Migration revisions found: {len(revisions)}")
        for rev in reversed(revisions):
            logger.info(f"    - {rev.revision}: {rev.doc}")
    except Exception as e:
        warnings.append(f"Alembic check warning: {e}")
        logger.warning(f"⚠ Alembic check warning: {e}")

    # Check 8: Environment files
    logger.info("\n[8/8] Checking environment files...")
    env_file = Path(".env")
    if env_file.exists():
        logger.info(f"✓ .env file found")

        # Check required variables
        required_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "SECRET_KEY",
            "FRED_API_KEY"
        ]

        env_content = env_file.read_text()
        missing_vars = []
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)

        if missing_vars:
            warnings.append(f"Missing environment variables: {', '.join(missing_vars)}")
            logger.warning(f"⚠ Missing environment variables: {', '.join(missing_vars)}")
        else:
            logger.info(f"  All required variables present")
    else:
        errors.append(".env file not found")
        logger.error("✗ .env file not found")

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)

    if errors:
        logger.error(f"\n❌ Configuration check FAILED with {len(errors)} error(s):")
        for i, error in enumerate(errors, 1):
            logger.error(f"  {i}. {error}")

    if warnings:
        logger.warning(f"\n⚠ {len(warnings)} warning(s):")
        for i, warning in enumerate(warnings, 1):
            logger.warning(f"  {i}. {warning}")

    if not errors and not warnings:
        logger.info("\n✅ All checks passed! Configuration is valid.")
        logger.info("\nYou can now:")
        logger.info("  1. Run database migrations: alembic upgrade head")
        logger.info("  2. Start the development server: uvicorn app.main:app --reload")
        logger.info("\nNote: Database migrations require a valid database connection.")
        logger.info("      If using railway.internal, run migrations on Railway.")
    elif not errors:
        logger.info("\n✅ Configuration is valid (with warnings).")
        logger.info("\nReview warnings above before proceeding.")

    logger.info("=" * 80)

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
