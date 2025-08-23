"""
Revision ID: a1b2c3d4e5f6
Revises: c0727d995ab3
Create Date: 2025-08-16

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a2b3c4d5e6f7'
# Use the last revision id from your versions folder
down_revision = 'e1a2b3c4d5f6'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'stripe_checkouts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sub_id', sa.Integer(), sa.ForeignKey('subscriptions.sub_id', ondelete='SET NULL'), nullable=True),
        sa.Column('price_id', sa.String(64), nullable=False),
        sa.Column('session_id', sa.String(128), nullable=True),
        sa.Column('success_url', sa.Text(), nullable=True),
        sa.Column('cancel_url', sa.Text(), nullable=True),
        sa.Column('status', sa.String(32), nullable=True),
        sa.Column('raw_request', sa.Text(), nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True)
    )
    op.create_table(
        'stripe_webhooks',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('received_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('event_id', sa.String(128), nullable=True),
        sa.Column('event_type', sa.String(64), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sub_id', sa.Integer(), sa.ForeignKey('subscriptions.sub_id', ondelete='SET NULL'), nullable=True),
        sa.Column('session_id', sa.String(128), nullable=True),
        sa.Column('payment_intent_id', sa.String(128), nullable=True),
        sa.Column('raw_payload', sa.Text(), nullable=True),
        sa.Column('processing_status', sa.String(32), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True)
    )

def downgrade():
    op.drop_table('stripe_webhooks')
    op.drop_table('stripe_checkouts')
