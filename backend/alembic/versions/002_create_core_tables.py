"""Create core tables (users, data_points, series_metadata)

Revision ID: 002
Revises: 001
Create Date: 2025-10-04 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create users, data_points, and series_metadata tables.

    Users table: Authentication and user management
    DataPoints table: FRED time-series data storage
    SeriesMetadata table: Metadata about FRED series
    """

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, comment='User email address (unique, used for login)'),
        sa.Column('hashed_password', sa.String(length=255), nullable=False, comment='Bcrypt hashed password'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true', comment='Whether the user account is active'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false', comment='Whether the user has admin privileges'),
        sa.Column('full_name', sa.String(length=255), nullable=True, comment='User full name'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        comment='User accounts for authentication and authorization'
    )

    # Create indexes for users table
    op.create_index(op.f('ix_users_id'), 'users', ['id'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'])

    # Create data_points table
    op.create_table(
        'data_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('series_id', sa.String(length=255), nullable=False, comment='FRED series identifier (e.g., GDP, UNRATE, CPIAUCSL)'),
        sa.Column('date', sa.Date(), nullable=False, comment='Date of the economic observation'),
        sa.Column('value', sa.Float(), nullable=False, comment='Numeric value of the observation'),
        sa.Column('realtime_start', sa.Date(), nullable=True, comment='Real-time period start date from FRED API'),
        sa.Column('realtime_end', sa.Date(), nullable=True, comment='Real-time period end date from FRED API'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('series_id', 'date', name='uix_series_date'),
        comment='FRED economic time-series data points'
    )

    # Create indexes for data_points table
    op.create_index(op.f('ix_data_points_id'), 'data_points', ['id'])
    op.create_index(op.f('ix_data_points_series_id'), 'data_points', ['series_id'])
    op.create_index(op.f('ix_data_points_date'), 'data_points', ['date'])
    op.create_index('ix_series_date', 'data_points', ['series_id', 'date'])
    op.create_index('ix_date_series', 'data_points', ['date', 'series_id'])

    # Create series_metadata table
    op.create_table(
        'series_metadata',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('series_id', sa.String(length=255), nullable=False, comment='FRED series identifier'),
        sa.Column('title', sa.String(length=500), nullable=True, comment='Human-readable series title'),
        sa.Column('units', sa.String(length=255), nullable=True, comment='Units of measurement'),
        sa.Column('frequency', sa.String(length=50), nullable=True, comment='Data frequency (Daily, Weekly, Monthly, Quarterly, Annual)'),
        sa.Column('seasonal_adjustment', sa.String(length=255), nullable=True, comment='Seasonal adjustment type'),
        sa.Column('last_updated', sa.Date(), nullable=True, comment='Last time FRED updated this series'),
        sa.Column('notes', sa.String(length=2000), nullable=True, comment='Additional notes about the series'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was created'),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='Timestamp when the record was last updated'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('series_id', name='uq_series_metadata_series_id'),
        comment='Metadata about FRED series for caching and reference'
    )

    # Create indexes for series_metadata table
    op.create_index(op.f('ix_series_metadata_id'), 'series_metadata', ['id'])
    op.create_index(op.f('ix_series_metadata_series_id'), 'series_metadata', ['series_id'])


def downgrade() -> None:
    """
    Drop all core tables and their indexes.
    """
    # Drop series_metadata table
    op.drop_index(op.f('ix_series_metadata_series_id'), table_name='series_metadata')
    op.drop_index(op.f('ix_series_metadata_id'), table_name='series_metadata')
    op.drop_table('series_metadata')

    # Drop data_points table
    op.drop_index('ix_date_series', table_name='data_points')
    op.drop_index('ix_series_date', table_name='data_points')
    op.drop_index(op.f('ix_data_points_date'), table_name='data_points')
    op.drop_index(op.f('ix_data_points_series_id'), table_name='data_points')
    op.drop_index(op.f('ix_data_points_id'), table_name='data_points')
    op.drop_table('data_points')

    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
