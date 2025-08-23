"""
Alembic migration script to add 'created_at' column to users table.
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_user_created_at_column'
down_revision = 'add_user_level_column'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

def downgrade():
    op.drop_column('users', 'created_at')