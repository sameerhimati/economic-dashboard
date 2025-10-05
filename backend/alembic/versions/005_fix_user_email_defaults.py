"""Fix user email defaults for existing users

Revision ID: 005
Revises: 004
Create Date: 2025-10-05 00:00:00.000000

This migration fixes existing users who have NULL values in imap_server
and imap_port columns after migration 004 was applied.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Fix existing users with NULL values in email configuration columns.

    This migration addresses an issue where migration 004 didn't properly
    set default values for existing users, causing login failures.
    """

    # Update any users who have NULL values in imap_server or imap_port
    # This handles the case where migration 004 was already applied but
    # didn't properly update existing users
    op.execute("""
        UPDATE users
        SET
            imap_server = COALESCE(imap_server, 'imap.gmail.com'),
            imap_port = COALESCE(imap_port, 993),
            newsletter_preferences = COALESCE(newsletter_preferences, '{}'::jsonb)
        WHERE imap_server IS NULL OR imap_port IS NULL OR newsletter_preferences IS NULL
    """)


def downgrade() -> None:
    """
    No downgrade needed - this migration only fixes data, doesn't change schema.
    """
    pass
