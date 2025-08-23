"""Merge heads

Revision ID: c0727d995ab3
Revises: add_subscriptions_table, add_user_created_at_column
Create Date: 2025-08-15 12:50:39.347878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0727d995ab3'
down_revision: Union[str, Sequence[str], None] = ('add_subscriptions_table', 'add_user_created_at_column')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
