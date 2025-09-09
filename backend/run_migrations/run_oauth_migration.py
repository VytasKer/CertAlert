#!/usr/bin/env python3
"""
Production OAuth Migration Script
Adds OAuth fields to users table for both SQLite (local) and PostgreSQL (production)
Safe for automated deployment - checks before applying changes
"""

import sys
import os

# Add the parent directory to the Python path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from app.database import engine
    from sqlalchemy import text, inspect
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the backend directory with the virtual environment activated")
    sys.exit(1)

def detect_database_type():
    """Detect if we're using SQLite or PostgreSQL"""
    try:
        with engine.connect() as conn:
            # Try to get database version - this helps identify the DB type
            result = conn.execute(text("SELECT version()")).fetchone()
            if result and 'PostgreSQL' in str(result[0]):
                return 'postgresql'
            else:
                return 'sqlite'
    except:
        # If version() doesn't work, assume SQLite
        return 'sqlite'

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logger.error(f"Error checking if table {table_name} exists: {e}")
        return False

def get_existing_columns(table_name):
    """Get list of existing columns in a table"""
    try:
        inspector = inspect(engine)
        return [col['name'] for col in inspector.get_columns(table_name)]
    except Exception as e:
        logger.error(f"Error getting columns for {table_name}: {e}")
        return []

def run_oauth_migration():
    """Add OAuth fields to the users table - production safe"""
    
    logger.info("🔄 Starting OAuth Migration for Production...")
    
    # Check if users table exists
    if not check_table_exists('users'):
        logger.error("❌ Users table does not exist! Cannot run OAuth migration.")
        return False
    
    # Detect database type
    db_type = detect_database_type()
    logger.info(f"📋 Database type detected: {db_type}")
    
    # Get existing columns
    existing_columns = get_existing_columns('users')
    logger.info(f"📋 Current users table columns: {existing_columns}")
    
    # Define OAuth columns based on database type
    if db_type == 'postgresql':
        oauth_columns = {
            'google_id': 'VARCHAR(255)',
            'google_email': 'VARCHAR(255)', 
            'profile_picture_url': 'VARCHAR(512)',
            'auth_provider': 'VARCHAR(50) NOT NULL DEFAULT \'local\'',
            'email_verified': 'BOOLEAN NOT NULL DEFAULT false',
            'last_google_sync': 'TIMESTAMP WITH TIME ZONE'
        }
    else:  # SQLite
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
        logger.info("✅ All OAuth columns already exist in users table!")
        return True
        
    logger.info(f"➕ Adding {len(columns_to_add)} missing OAuth columns...")
    
    try:
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Add missing columns
                for col_name, col_type in columns_to_add:
                    logger.info(f"   Adding column: {col_name}")
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
                            logger.info(f"   Creating index: {index_name}")
                            if db_type == 'postgresql':
                                sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON users ({column_name})"
                            else:  # SQLite
                                sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON users ({column_name})"
                            conn.execute(text(sql))
                        except Exception as e:
                            logger.warning(f"   ⚠️  Index {index_name} creation failed (may already exist): {e}")
                
                # Update existing users for backward compatibility
                if 'email_verified' in [col[0] for col in columns_to_add]:
                    logger.info("   Setting email_verified=true for existing users...")
                    if db_type == 'postgresql':
                        conn.execute(text("UPDATE users SET email_verified = true WHERE email_verified = false OR email_verified IS NULL"))
                    else:  # SQLite
                        conn.execute(text("UPDATE users SET email_verified = 1 WHERE email_verified = 0 OR email_verified IS NULL"))
                
                # Commit transaction
                trans.commit()
                logger.info("✅ OAuth migration completed successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                logger.error(f"❌ Migration failed, rolled back: {str(e)}")
                raise
                
    except Exception as e:
        logger.error(f"❌ Migration error: {str(e)}")
        return False

def verify_migration():
    """Verify that all OAuth columns exist after migration"""
    try:
        existing_columns = get_existing_columns('users')
        
        required_oauth_columns = [
            'google_id', 'google_email', 'profile_picture_url',
            'auth_provider', 'email_verified', 'last_google_sync'
        ]
        
        missing = [col for col in required_oauth_columns if col not in existing_columns]
        
        if missing:
            logger.error(f"❌ Missing OAuth columns after migration: {missing}")
            return False
        else:
            logger.info("✅ All OAuth columns verified present!")
            logger.info(f"📋 Final users table columns: {existing_columns}")
            return True
            
    except Exception as e:
        logger.error(f"❌ Verification failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("OAUTH FIELDS MIGRATION - CertAlert Production")
    logger.info("=" * 60)
    
    try:
        # Run the migration
        if run_oauth_migration():
            # Verify the migration worked
            if verify_migration():
                logger.info("🎉 OAuth migration completed successfully!")
                return True
            else:
                logger.error("❌ Migration verification failed!")
                return False
        else:
            logger.error("❌ OAuth migration failed!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {str(e)}")
        return False
    
    finally:
        logger.info("=" * 60)

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    logger.info("Migration process completed successfully!")
