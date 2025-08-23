"""
Alembic migration for Subscriptions table
"""
from alembic import op
import sqlalchemy as sa
import enum

# revision identifiers, used by Alembic.
revision = 'add_subscriptions_table'
down_revision = None
branch_labels = None
depends_on = None

class SubscriptionStatus(enum.Enum):
    INITIATED = "INITIATED"
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"

def upgrade():
    op.create_table(
        'subscriptions',
        sa.Column('sub_id', sa.Integer(), primary_key=True, autoincrement=True, index=True),
        sa.Column('sub_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('sub_source', sa.String(length=64), nullable=False, server_default='certalert_page'),
        sa.Column('sub_status', sa.Enum('INITIATED', 'ACTIVATED', 'DEACTIVATED', name='subscriptionstatus'), nullable=False, server_default='INITIATED'),
        sa.Column('sub_amount', sa.Float(), nullable=True),
        sa.Column('sub_start_date', sa.DateTime(), nullable=False),
        sa.Column('sub_end_date', sa.DateTime(), nullable=False),
        sa.Column('sub_ended', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
        sa.Column('sub_cancelled', sa.Boolean(), nullable=False, server_default=sa.text('FALSE')),
    )

def downgrade():
    op.drop_table('subscriptions')
    op.execute('DROP TYPE IF EXISTS subscriptionstatus')
