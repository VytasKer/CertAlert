"""Add Stripe session and payment intent fields to Subscription"""

revision = 'e1a2b3c4d5f6'
down_revision = 'c0727d995ab3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('subscriptions', sa.Column('stripe_session_id', sa.String(length=128), nullable=True))
    op.add_column('subscriptions', sa.Column('stripe_payment_intent_id', sa.String(length=128), nullable=True))

def downgrade():
    op.drop_column('subscriptions', 'stripe_session_id')
    op.drop_column('subscriptions', 'stripe_payment_intent_id')