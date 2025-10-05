"""Create newsletters table for email newsletter storage

Revision ID: 003
Revises: 002
Create Date: 2025-10-04 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create newsletters table for storing parsed email newsletters.

    Stores email newsletters from Bisnow and other real estate sources
    with extracted content, metadata, and key points.
    """

    # Create newsletters table
    op.create_table(
        'newsletters',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text('gen_random_uuid()'),
            comment='Unique newsletter identifier'
        ),
        sa.Column(
            'source',
            sa.String(length=500),
            nullable=False,
            comment='Email sender address (e.g., alerts@mail.bisnow.com)'
        ),
        sa.Column(
            'category',
            sa.String(length=255),
            nullable=False,
            comment='Newsletter category (e.g., Houston Morning Brief, National Deal Brief)'
        ),
        sa.Column(
            'subject',
            sa.String(length=1000),
            nullable=False,
            comment='Email subject line'
        ),
        sa.Column(
            'content_html',
            sa.Text(),
            nullable=True,
            comment='Full HTML content of the email'
        ),
        sa.Column(
            'content_text',
            sa.Text(),
            nullable=True,
            comment='Extracted plain text content from HTML'
        ),
        sa.Column(
            'key_points',
            postgresql.JSON(astext_type=sa.Text()),
            nullable=True,
            comment='Extracted key points including headlines, metrics, locations, companies'
        ),
        sa.Column(
            'received_date',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='When the email was received'
        ),
        sa.Column(
            'parsed_date',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='When the email was parsed and stored'
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
        sa.UniqueConstraint(
            'subject',
            'received_date',
            name='uix_newsletter_subject_date'
        ),
        comment='Email newsletters with parsed content and metadata'
    )

    # Create indexes for efficient querying
    op.create_index(
        op.f('ix_newsletters_id'),
        'newsletters',
        ['id']
    )

    op.create_index(
        op.f('ix_newsletters_source'),
        'newsletters',
        ['source']
    )

    op.create_index(
        op.f('ix_newsletters_category'),
        'newsletters',
        ['category']
    )

    op.create_index(
        op.f('ix_newsletters_received_date'),
        'newsletters',
        ['received_date']
    )

    op.create_index(
        op.f('ix_newsletters_parsed_date'),
        'newsletters',
        ['parsed_date']
    )

    # Composite indexes for common query patterns
    op.create_index(
        'ix_newsletter_category_date',
        'newsletters',
        ['category', 'received_date']
    )

    op.create_index(
        'ix_newsletter_source_date',
        'newsletters',
        ['source', 'received_date']
    )


def downgrade() -> None:
    """
    Drop newsletters table and all associated indexes.
    """

    # Drop composite indexes
    op.drop_index('ix_newsletter_source_date', table_name='newsletters')
    op.drop_index('ix_newsletter_category_date', table_name='newsletters')

    # Drop single-column indexes
    op.drop_index(op.f('ix_newsletters_parsed_date'), table_name='newsletters')
    op.drop_index(op.f('ix_newsletters_received_date'), table_name='newsletters')
    op.drop_index(op.f('ix_newsletters_category'), table_name='newsletters')
    op.drop_index(op.f('ix_newsletters_source'), table_name='newsletters')
    op.drop_index(op.f('ix_newsletters_id'), table_name='newsletters')

    # Drop table
    op.drop_table('newsletters')
