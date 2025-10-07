"""Add daily metrics infrastructure

Revision ID: 007
Revises: 006
Create Date: 2025-10-07 17:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create metric_data_points table
    op.create_table(
        'metric_data_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_code', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('metric_code', 'date', name='uix_metric_date')
    )
    op.create_index('idx_metric_code_date', 'metric_data_points', ['metric_code', 'date'])
    op.create_index('idx_metric_code_created', 'metric_data_points', ['metric_code', 'created_at'])
    op.create_index(op.f('ix_metric_data_points_id'), 'metric_data_points', ['id'], unique=False)
    op.create_index(op.f('ix_metric_data_points_metric_code'), 'metric_data_points', ['metric_code'], unique=False)
    op.create_index(op.f('ix_metric_data_points_date'), 'metric_data_points', ['date'], unique=False)

    # Create daily_metric_configs table
    op.create_table(
        'daily_metric_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_code', sa.String(length=50), nullable=False),
        sa.Column('source', sa.String(length=20), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('unit', sa.String(length=50), nullable=True),
        sa.Column('weekday', sa.Integer(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('refresh_frequency', sa.String(length=20), nullable=False, server_default='daily'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('metric_code')
    )
    op.create_index(op.f('ix_daily_metric_configs_id'), 'daily_metric_configs', ['id'], unique=False)
    op.create_index(op.f('ix_daily_metric_configs_metric_code'), 'daily_metric_configs', ['metric_code'], unique=True)

    # Create metric_insights table
    op.create_table(
        'metric_insights',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('metric_code', sa.String(length=50), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('insight_type', sa.String(length=50), nullable=True),
        sa.Column('message', sa.String(length=500), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_metric_insights_code_date', 'metric_insights', ['metric_code', 'date'])
    op.create_index(op.f('ix_metric_insights_id'), 'metric_insights', ['id'], unique=False)
    op.create_index(op.f('ix_metric_insights_metric_code'), 'metric_insights', ['metric_code'], unique=False)
    op.create_index(op.f('ix_metric_insights_date'), 'metric_insights', ['date'], unique=False)


def downgrade() -> None:
    # Drop metric_insights table
    op.drop_index(op.f('ix_metric_insights_date'), table_name='metric_insights')
    op.drop_index(op.f('ix_metric_insights_metric_code'), table_name='metric_insights')
    op.drop_index(op.f('ix_metric_insights_id'), table_name='metric_insights')
    op.drop_index('idx_metric_insights_code_date', table_name='metric_insights')
    op.drop_table('metric_insights')

    # Drop daily_metric_configs table
    op.drop_index(op.f('ix_daily_metric_configs_metric_code'), table_name='daily_metric_configs')
    op.drop_index(op.f('ix_daily_metric_configs_id'), table_name='daily_metric_configs')
    op.drop_table('daily_metric_configs')

    # Drop metric_data_points table
    op.drop_index(op.f('ix_metric_data_points_date'), table_name='metric_data_points')
    op.drop_index(op.f('ix_metric_data_points_metric_code'), table_name='metric_data_points')
    op.drop_index(op.f('ix_metric_data_points_id'), table_name='metric_data_points')
    op.drop_index('idx_metric_code_created', table_name='metric_data_points')
    op.drop_index('idx_metric_code_date', table_name='metric_data_points')
    op.drop_table('metric_data_points')
