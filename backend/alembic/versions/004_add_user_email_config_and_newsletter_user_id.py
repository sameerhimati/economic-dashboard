"""Add user email config and newsletter user_id

Revision ID: 004
Revises: 003
Create Date: 2025-10-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add email configuration and newsletter preferences to users table.
    Add user_id foreign key to newsletters table.

    This enables user-specific email fetching where each user can:
    - Configure their own email credentials
    - Select which newsletters to track
    - Have newsletters associated with their account
    """

    # Add email configuration columns to users table
    op.add_column(
        'users',
        sa.Column(
            'email_address',
            sa.String(length=500),
            nullable=True,
            comment='User email address for newsletter fetching'
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'email_app_password',
            sa.Text(),
            nullable=True,
            comment='Encrypted email app password for IMAP access'
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'imap_server',
            sa.String(length=255),
            nullable=True,  # Temporarily nullable for migration
            comment='IMAP server for email fetching'
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'imap_port',
            sa.Integer(),
            nullable=True,  # Temporarily nullable for migration
            comment='IMAP port for email fetching'
        )
    )

    op.add_column(
        'users',
        sa.Column(
            'newsletter_preferences',
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment='Newsletter preferences including categories, fetch settings, and last fetch timestamp'
        )
    )

    # Update existing users with default values
    # This ensures all existing users have valid values before making columns non-nullable
    op.execute("""
        UPDATE users
        SET
            imap_server = 'imap.gmail.com',
            imap_port = 993,
            newsletter_preferences = '{}'::json
        WHERE imap_server IS NULL
    """)

    # Now make imap_server and imap_port non-nullable with server defaults
    op.alter_column('users', 'imap_server', nullable=False, server_default='imap.gmail.com')
    op.alter_column('users', 'imap_port', nullable=False, server_default='993')

    # Add user_id column to newsletters table (nullable initially for migration)
    op.add_column(
        'newsletters',
        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=True,  # Temporarily nullable for migration
            comment='ID of user who owns this newsletter'
        )
    )

    # For existing newsletters, we could either:
    # 1. Delete them (clean slate for multi-user)
    # 2. Assign them to a default user (if one exists)
    #
    # For now, we'll delete existing newsletters since this is a breaking change
    # and we want a clean multi-user setup
    op.execute('DELETE FROM newsletters')

    # Now make user_id non-nullable
    op.alter_column(
        'newsletters',
        'user_id',
        nullable=False
    )

    # Add foreign key constraint
    op.create_foreign_key(
        'fk_newsletters_user_id',
        'newsletters',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Create index on user_id
    op.create_index(
        op.f('ix_newsletters_user_id'),
        'newsletters',
        ['user_id']
    )

    # Drop old unique constraint (subject + received_date)
    op.drop_constraint(
        'uix_newsletter_subject_date',
        'newsletters',
        type_='unique'
    )

    # Create new unique constraint (user_id + subject + received_date)
    op.create_unique_constraint(
        'uix_newsletter_user_subject_date',
        'newsletters',
        ['user_id', 'subject', 'received_date']
    )

    # Create composite indexes for user-specific queries
    op.create_index(
        'ix_newsletter_user_category_date',
        'newsletters',
        ['user_id', 'category', 'received_date']
    )

    op.create_index(
        'ix_newsletter_user_received',
        'newsletters',
        ['user_id', 'received_date']
    )


def downgrade() -> None:
    """
    Remove user email configuration and newsletter user_id relationship.
    Reverts to shared email account model.
    """

    # Drop composite indexes
    op.drop_index('ix_newsletter_user_received', table_name='newsletters')
    op.drop_index('ix_newsletter_user_category_date', table_name='newsletters')

    # Drop new unique constraint
    op.drop_constraint(
        'uix_newsletter_user_subject_date',
        'newsletters',
        type_='unique'
    )

    # Recreate old unique constraint
    op.create_unique_constraint(
        'uix_newsletter_subject_date',
        'newsletters',
        ['subject', 'received_date']
    )

    # Drop user_id index and foreign key
    op.drop_index(op.f('ix_newsletters_user_id'), table_name='newsletters')
    op.drop_constraint('fk_newsletters_user_id', 'newsletters', type_='foreignkey')

    # Drop user_id column
    op.drop_column('newsletters', 'user_id')

    # Drop email configuration columns from users table
    op.drop_column('users', 'newsletter_preferences')
    op.drop_column('users', 'imap_port')
    op.drop_column('users', 'imap_server')
    op.drop_column('users', 'email_app_password')
    op.drop_column('users', 'email_address')
