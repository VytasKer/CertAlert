"""
Revision ID: a3b4c5d6e7f8
Revises: a2b3c4d5e6f7
Create Date: 2025-08-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a3b4c5d6e7f8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None

def upgrade():
    op.alter_column('stripe_checkouts', 'session_id',
        existing_type=sa.String(length=128),
        type_=sa.String(length=256),
        existing_nullable=True
    )

def downgrade():
    op.alter_column('stripe_checkouts', 'session_id',
        existing_type=sa.String(length=256),
        type_=sa.String(length=128),
        existing_nullable=True
    )
