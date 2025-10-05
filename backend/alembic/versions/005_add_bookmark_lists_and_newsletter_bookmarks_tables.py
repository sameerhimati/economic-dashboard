"""Add bookmark lists and newsletter bookmarks tables

Revision ID: 005
Revises: 004
Create Date: 2025-10-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create bookmark_lists and newsletter_bookmarks tables.

    Allows users to create custom bookmark lists (max 10) to organize
    their newsletters. Implements many-to-many relationship between
    newsletters and bookmark lists.
    """

    # Create bookmark_lists table
    op.create_table(
        'bookmark_lists',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text('gen_random_uuid()'),
            comment='Unique bookmark list identifier'
        ),
        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=False,
            comment='ID of user who owns this bookmark list'
        ),
        sa.Column(
            'name',
            sa.String(length=255),
            nullable=False,
            comment='Name of the bookmark list (e.g., Houston Deals, Market Trends)'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Timestamp when the record was created'
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='Timestamp when the record was last updated'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_bookmark_lists_user_id',
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint(
            'user_id',
            'name',
            name='uix_bookmark_list_user_name'
        ),
        comment='User-created bookmark lists for organizing newsletters'
    )

    # Create indexes for bookmark_lists table
    op.create_index(
        op.f('ix_bookmark_lists_id'),
        'bookmark_lists',
        ['id']
    )

    op.create_index(
        'ix_bookmark_list_user_id',
        'bookmark_lists',
        ['user_id']
    )

    # Create newsletter_bookmarks junction table
    op.create_table(
        'newsletter_bookmarks',
        sa.Column(
            'newsletter_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the newsletter being bookmarked'
        ),
        sa.Column(
            'bookmark_list_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the bookmark list containing this newsletter'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='When the newsletter was added to the bookmark list'
        ),
        sa.PrimaryKeyConstraint(
            'newsletter_id',
            'bookmark_list_id',
            name='pk_newsletter_bookmarks'
        ),
        sa.ForeignKeyConstraint(
            ['newsletter_id'],
            ['newsletters.id'],
            name='fk_newsletter_bookmarks_newsletter_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['bookmark_list_id'],
            ['bookmark_lists.id'],
            name='fk_newsletter_bookmarks_bookmark_list_id',
            ondelete='CASCADE'
        ),
        comment='Junction table for many-to-many relationship between newsletters and bookmark lists'
    )

    # Create indexes for newsletter_bookmarks junction table
    op.create_index(
        'ix_newsletter_bookmarks_newsletter_id',
        'newsletter_bookmarks',
        ['newsletter_id']
    )

    op.create_index(
        'ix_newsletter_bookmarks_bookmark_list_id',
        'newsletter_bookmarks',
        ['bookmark_list_id']
    )


def downgrade() -> None:
    """
    Drop bookmark_lists and newsletter_bookmarks tables.
    """

    # Drop newsletter_bookmarks indexes
    op.drop_index('ix_newsletter_bookmarks_bookmark_list_id', table_name='newsletter_bookmarks')
    op.drop_index('ix_newsletter_bookmarks_newsletter_id', table_name='newsletter_bookmarks')

    # Drop newsletter_bookmarks table
    op.drop_table('newsletter_bookmarks')

    # Drop bookmark_lists indexes
    op.drop_index('ix_bookmark_list_user_id', table_name='bookmark_lists')
    op.drop_index(op.f('ix_bookmark_lists_id'), table_name='bookmark_lists')

    # Drop bookmark_lists table
    op.drop_table('bookmark_lists')
