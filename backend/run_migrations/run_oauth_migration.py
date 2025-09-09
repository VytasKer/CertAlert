#!/usr/bin/env python3
"""
Direct migration script to add OAuth fields to users table
This follows the CertAlert pattern of using direct SQLAlchemy for production reliability
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text, inspect

def run_oauth_migration():
    """Add OAuth fields to the users table if they don't already exist."""
    
    print("🔄 Starting OAuth fields migration...")
    
    try:
        # Check current table structure
        inspector = inspect(engine)
        existing_columns = [col['name'] for col in inspector.get_columns('users')]
        print(f"📋 Current users table columns: {existing_columns}")
        
        # Define the OAuth columns we need to add
        oauth_columns = {
            'google_id': 'VARCHAR(255)',
            'google_email': 'VARCHAR(255)', 
            'profile_picture_url': 'VARCHAR(512)',
            'auth_provider': 'VARCHAR(50) NOT NULL DEFAULT \'local\'',
            'email_verified': 'BOOLEAN NOT NULL DEFAULT 0',
            'last_google_sync': 'DATETIME'
        }
        
        # Check which columns need to be added
        columns_to_add = []
        for col_name, col_type in oauth_columns.items():
            if col_name not in existing_columns:
                columns_to_add.append((col_name, col_type))
        
        if not columns_to_add:
            print("✅ All OAuth columns already exist in users table!")
            return True
            
        print(f"➕ Adding {len(columns_to_add)} missing OAuth columns...")
        
        with engine.connect() as conn:
            transaction = conn.begin()
            
            try:
                # Add missing columns
                for col_name, col_type in columns_to_add:
                    print(f"   Adding column: {col_name}")
                    sql = f"ALTER TABLE users ADD COLUMN {col_name} {col_type}"
                    conn.execute(text(sql))
                
                # Create indexes for OAuth lookups (if columns were added)
                oauth_indexes = [
                    ("ix_users_google_id", "google_id"),
                    ("ix_users_auth_provider", "auth_provider")
                ]
                
                for index_name, column_name in oauth_indexes:
                    if column_name in [col[0] for col in columns_to_add]:
                        try:
                            print(f"   Creating index: {index_name}")
                            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON users ({column_name})"
                            conn.execute(text(sql))
                        except Exception as e:
                            print(f"   ⚠️  Index {index_name} may already exist: {e}")
                
                # Update existing users for backward compatibility
                if 'email_verified' in [col[0] for col in columns_to_add]:
                    print("   Setting email_verified=1 for existing users...")
                    conn.execute(text("UPDATE users SET email_verified = 1 WHERE email_verified = 0 OR email_verified IS NULL"))
                
                transaction.commit()
                print("✅ OAuth migration completed successfully!")
                return True
                
            except Exception as e:
                transaction.rollback()
                print(f"❌ Migration failed: {str(e)}")
                raise
                
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        return False

def verify_migration():
    """Verify that all OAuth columns exist after migration."""
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        required_oauth_columns = [
            'google_id', 'google_email', 'profile_picture_url',
            'auth_provider', 'email_verified', 'last_google_sync'
        ]
        
        missing = [col for col in required_oauth_columns if col not in columns]
        
        if missing:
            print(f"❌ Missing OAuth columns: {missing}")
            return False
        else:
            print("✅ All OAuth columns verified present!")
            print(f"📋 Final users table columns: {columns}")
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("OAUTH FIELDS MIGRATION - CertAlert")
    print("=" * 50)
    
    # Run the migration
    if run_oauth_migration():
        # Verify the migration worked
        verify_migration()
    else:
        print("❌ Migration failed!")
        sys.exit(1)
    
    print("=" * 50)
    print("Migration complete!")
