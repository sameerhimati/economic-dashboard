"""Create fred_data_points table

Revision ID: 001
Revises:
Create Date: 2025-10-04 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create fred_data_points table for storing key economic indicators.

    This table stores:
    - DFF (Federal Funds Rate)
    - DGS10 (10-Year Treasury Constant Maturity Rate)
    - UNRATE (Unemployment Rate)
    - CPIAUCSL (Consumer Price Index)
    - MORTGAGE30US (30-Year Fixed Rate Mortgage Average)
    """
    op.create_table(
        'fred_data_points',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('series_id', sa.String(length=50), nullable=False, comment='FRED series identifier (e.g., DFF, UNRATE, CPIAUCSL)'),
        sa.Column('series_name', sa.String(length=255), nullable=False, comment='Human-readable series name (e.g., Federal Funds Rate)'),
        sa.Column('value', sa.Numeric(precision=20, scale=6), nullable=False, comment='Numeric value of the observation'),
        sa.Column('unit', sa.String(length=100), nullable=False, comment='Unit of measurement (e.g., Percent, Index, Billions of Dollars)'),
        sa.Column('date', sa.Date(), nullable=False, comment='Date of the economic observation'),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False, comment='Timestamp when this data was fetched from FRED API'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('series_id', 'date', name='uix_fred_series_date'),
        comment='FRED economic data points for key indicators'
    )

    # Create indexes
    op.create_index('ix_fred_series_id', 'fred_data_points', ['series_id'])
    op.create_index('ix_fred_date', 'fred_data_points', ['date'])
    op.create_index('ix_fred_series_date', 'fred_data_points', ['series_id', 'date'])
    op.create_index('ix_fred_fetched_at', 'fred_data_points', ['fetched_at'])
    op.create_index(op.f('ix_fred_data_points_id'), 'fred_data_points', ['id'])


def downgrade() -> None:
    """
    Drop fred_data_points table and all associated indexes.
    """
    op.drop_index(op.f('ix_fred_data_points_id'), table_name='fred_data_points')
    op.drop_index('ix_fred_fetched_at', table_name='fred_data_points')
    op.drop_index('ix_fred_series_date', table_name='fred_data_points')
    op.drop_index('ix_fred_date', table_name='fred_data_points')
    op.drop_index('ix_fred_series_id', table_name='fred_data_points')
    op.drop_table('fred_data_points')
