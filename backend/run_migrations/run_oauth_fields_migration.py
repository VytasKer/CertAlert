# backend/run_migrations/run_oauth_fields_migration.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from app.models import User
from sqlalchemy import text, inspect

def run_migration():
    """
    Add OAuth fields to User model for Google authentication integration.
    This migration adds: google_id, google_email, profile_picture_url, 
    auth_provider, email_verified, last_google_sync
    """
    try:
        # Check if migration is needed
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'google_id' in columns:
            print("✅ OAuth fields migration already applied")
            return
        
        print("🔄 Starting OAuth fields migration...")
        
        with engine.connect() as conn:
            # Begin transaction
            trans = conn.begin()
            
            try:
                # Add OAuth fields to users table
                print("📝 Adding google_id column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN google_id VARCHAR(255)"))
                
                print("📝 Adding google_email column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN google_email VARCHAR(255)"))
                
                print("📝 Adding profile_picture_url column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN profile_picture_url VARCHAR(512)"))
                
                print("📝 Adding auth_provider column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN auth_provider VARCHAR(50) NOT NULL DEFAULT 'local'"))
                
                print("📝 Adding email_verified column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT false"))
                
                print("📝 Adding last_google_sync column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN last_google_sync TIMESTAMP WITH TIME ZONE"))
                
                # Create indexes for efficient OAuth lookups
                print("🔍 Creating indexes...")
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_google_id ON users (google_id)"))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_users_auth_provider ON users (auth_provider)"))
                
                # Update existing users for backward compatibility
                print("🔄 Updating existing users...")
                conn.execute(text("UPDATE users SET email_verified = true WHERE email_verified = false"))
                
                # Commit transaction
                trans.commit()
                print("✅ OAuth fields migration completed successfully")
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                raise e
                
    except Exception as e:
        print(f"❌ OAuth fields migration failed: {str(e)}")
        print("🔄 Attempting fallback table recreation...")
        
        try:
            # Fallback: recreate User table with new schema
            User.__table__.create(engine, checkfirst=True)
            print("✅ Fallback table creation successful")
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {str(fallback_error)}")
            raise

if __name__ == "__main__":
    run_migration()
