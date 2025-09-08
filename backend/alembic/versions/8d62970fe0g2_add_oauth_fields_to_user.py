"""Add OAuth fields to User model

Revision ID: 8d62970fe0g2
Revises: 7c51869efdf1
Create Date: 2025-09-08 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8d62970fe0g2'
down_revision: Union[str, None] = '7c51869efdf1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add OAuth fields to users table for Google authentication integration."""
    # Add OAuth-related fields to users table
    op.add_column('users', sa.Column('google_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('google_email', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('profile_picture_url', sa.String(512), nullable=True))
    op.add_column('users', sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'))
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('last_google_sync', sa.DateTime(timezone=True), nullable=True))
    
    # Create indexes for efficient OAuth lookups
    op.create_index('ix_users_google_id', 'users', ['google_id'])
    op.create_index('ix_users_auth_provider', 'users', ['auth_provider'])
    
    # Update existing users to have email_verified=true and auth_provider='local'
    # This ensures backward compatibility for existing local accounts
    op.execute("UPDATE users SET email_verified = true WHERE email_verified = false")


def downgrade() -> None:
    """Remove OAuth fields from users table."""
    # Drop indexes first
    op.drop_index('ix_users_auth_provider', table_name='users')
    op.drop_index('ix_users_google_id', table_name='users')
    
    # Drop columns
    op.drop_column('users', 'last_google_sync')
    op.drop_column('users', 'email_verified')
    op.drop_column('users', 'auth_provider')
    op.drop_column('users', 'profile_picture_url')
    op.drop_column('users', 'google_email')
    op.drop_column('users', 'google_id')
