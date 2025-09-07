"""Add traffic logs table

Revision ID: 6b40758dece0
Revises: a3b4c5d6e7f8
Create Date: 2025-09-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision: str = '6b40758dece0'
down_revision: Union[str, Sequence[str], None] = 'a3b4c5d6e7f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add traffic_logs table for persistent storage."""
    op.create_table('traffic_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),  # For efficient date-based queries
        sa.Column('log_data', JSON(), nullable=False),  # Store the full JSON log entry
        sa.Column('ip_hash', sa.String(64), nullable=True),  # For efficient IP-based queries
        sa.Column('path', sa.String(255), nullable=True),  # For efficient path-based queries
        sa.Column('status_code', sa.Integer(), nullable=True),  # For efficient status queries
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for common queries
    op.create_index('idx_traffic_logs_date', 'traffic_logs', ['date'])
    op.create_index('idx_traffic_logs_timestamp', 'traffic_logs', ['timestamp'])
    op.create_index('idx_traffic_logs_ip_hash', 'traffic_logs', ['ip_hash'])
    op.create_index('idx_traffic_logs_path', 'traffic_logs', ['path'])
    op.create_index('idx_traffic_logs_status_code', 'traffic_logs', ['status_code'])


def downgrade() -> None:
    """Remove traffic_logs table."""
    op.drop_table('traffic_logs')
