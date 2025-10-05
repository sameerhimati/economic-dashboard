"""Redesign for article-centric system

Revision ID: 006
Revises: 005
Create Date: 2025-10-05 14:00:00.000000

Major schema redesign to make articles the primary entity instead of newsletters.
Articles can now appear in multiple newsletters via the article_sources junction table.
Users bookmark individual articles instead of entire newsletters.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create article-centric schema.

    Creates:
    1. articles table - primary entity for individual newsletter articles
    2. article_sources - junction table linking articles to newsletters
    3. article_bookmarks - junction table for bookmarking articles

    Drops:
    1. newsletter_bookmarks - replaced by article_bookmarks
    """

    # Step 1: Drop old newsletter_bookmarks table
    # Drop indexes first
    op.drop_index('ix_newsletter_bookmarks_bookmark_list_id', table_name='newsletter_bookmarks')
    op.drop_index('ix_newsletter_bookmarks_newsletter_id', table_name='newsletter_bookmarks')

    # Drop table
    op.drop_table('newsletter_bookmarks')

    # Step 2: Create articles table
    op.create_table(
        'articles',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            server_default=sa.text('gen_random_uuid()'),
            comment='Unique article identifier'
        ),
        sa.Column(
            'user_id',
            sa.Integer(),
            nullable=False,
            comment='ID of user who owns this article'
        ),
        sa.Column(
            'headline',
            sa.Text(),
            nullable=False,
            comment='Article headline/title'
        ),
        sa.Column(
            'url',
            sa.Text(),
            nullable=True,
            comment='Article URL (optional - some articles may not have URLs)'
        ),
        sa.Column(
            'category',
            sa.String(length=255),
            nullable=False,
            comment='Newsletter category (e.g., Houston Morning Brief, National Deal Brief)'
        ),
        sa.Column(
            'received_date',
            sa.DateTime(timezone=True),
            nullable=False,
            comment='When the newsletter containing this article was received'
        ),
        sa.Column(
            'position',
            sa.Integer(),
            nullable=False,
            server_default='0',
            comment='Position in the original newsletter (for ordering)'
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
            name='fk_articles_user_id',
            ondelete='CASCADE'
        ),
        sa.UniqueConstraint(
            'user_id',
            'url',
            'received_date',
            name='uix_article_user_url_date'
        ),
        comment='Individual articles extracted from newsletters'
    )

    # Create indexes for articles table
    op.create_index(
        op.f('ix_articles_id'),
        'articles',
        ['id']
    )

    op.create_index(
        op.f('ix_articles_user_id'),
        'articles',
        ['user_id']
    )

    op.create_index(
        op.f('ix_articles_category'),
        'articles',
        ['category']
    )

    op.create_index(
        op.f('ix_articles_received_date'),
        'articles',
        ['received_date']
    )

    op.create_index(
        'ix_article_user_category_date',
        'articles',
        ['user_id', 'category', 'received_date']
    )

    op.create_index(
        'ix_article_user_url',
        'articles',
        ['user_id', 'url']
    )

    # Step 3: Create article_sources junction table
    op.create_table(
        'article_sources',
        sa.Column(
            'article_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the article'
        ),
        sa.Column(
            'newsletter_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the newsletter containing this article'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='When the article was extracted from the newsletter'
        ),
        sa.PrimaryKeyConstraint(
            'article_id',
            'newsletter_id',
            name='pk_article_sources'
        ),
        sa.ForeignKeyConstraint(
            ['article_id'],
            ['articles.id'],
            name='fk_article_sources_article_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['newsletter_id'],
            ['newsletters.id'],
            name='fk_article_sources_newsletter_id',
            ondelete='CASCADE'
        ),
        comment='Junction table linking articles to their source newsletters'
    )

    # Create indexes for article_sources junction table
    op.create_index(
        'ix_article_source_article',
        'article_sources',
        ['article_id']
    )

    op.create_index(
        'ix_article_source_newsletter',
        'article_sources',
        ['newsletter_id']
    )

    # Step 4: Create article_bookmarks junction table
    op.create_table(
        'article_bookmarks',
        sa.Column(
            'article_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the article being bookmarked'
        ),
        sa.Column(
            'bookmark_list_id',
            postgresql.UUID(as_uuid=True),
            nullable=False,
            comment='ID of the bookmark list containing this article'
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
            comment='When the article was added to the bookmark list'
        ),
        sa.PrimaryKeyConstraint(
            'article_id',
            'bookmark_list_id',
            name='pk_article_bookmarks'
        ),
        sa.ForeignKeyConstraint(
            ['article_id'],
            ['articles.id'],
            name='fk_article_bookmarks_article_id',
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['bookmark_list_id'],
            ['bookmark_lists.id'],
            name='fk_article_bookmarks_bookmark_list_id',
            ondelete='CASCADE'
        ),
        comment='Junction table for many-to-many relationship between articles and bookmark lists'
    )

    # Create indexes for article_bookmarks junction table
    op.create_index(
        'ix_article_bookmark_article',
        'article_bookmarks',
        ['article_id']
    )

    op.create_index(
        'ix_article_bookmark_list',
        'article_bookmarks',
        ['bookmark_list_id']
    )


def downgrade() -> None:
    """
    Rollback to newsletter-centric schema.

    Warning: This will delete all articles and article bookmarks.
    Recreates the old newsletter_bookmarks table.
    """

    # Step 1: Drop article_bookmarks table
    op.drop_index('ix_article_bookmark_list', table_name='article_bookmarks')
    op.drop_index('ix_article_bookmark_article', table_name='article_bookmarks')
    op.drop_table('article_bookmarks')

    # Step 2: Drop article_sources table
    op.drop_index('ix_article_source_newsletter', table_name='article_sources')
    op.drop_index('ix_article_source_article', table_name='article_sources')
    op.drop_table('article_sources')

    # Step 3: Drop articles table
    op.drop_index('ix_article_user_url', table_name='articles')
    op.drop_index('ix_article_user_category_date', table_name='articles')
    op.drop_index(op.f('ix_articles_received_date'), table_name='articles')
    op.drop_index(op.f('ix_articles_category'), table_name='articles')
    op.drop_index(op.f('ix_articles_user_id'), table_name='articles')
    op.drop_index(op.f('ix_articles_id'), table_name='articles')
    op.drop_table('articles')

    # Step 4: Recreate newsletter_bookmarks table
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

    # Recreate indexes for newsletter_bookmarks
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
