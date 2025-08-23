"""
Alembic migration script to add 'level' column to users table.
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_level_column'
down_revision = 'ffd9ea1960c8'  # Use the revision ID of your last migration
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('level', sa.String(length=32), nullable=False, server_default='free_user'))

def downgrade():
    op.drop_column('users', 'level')