#!/usr/bin/env python3
"""
Startup script for Render deployment
Ensures admin_settings table exists before starting the app
"""

import os
import sys
import subprocess
import logging

def setup_database():
    """Setup database tables and run migrations"""
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info("🚀 Starting database setup...")
        
        # Try to run alembic migration first
        try:
            logger.info("Running alembic migration...")
            result = subprocess.run(
                ["python", "-m", "alembic", "upgrade", "head"],
                cwd="/opt/render/project/src",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ Alembic migration completed successfully")
                return True
            else:
                logger.warning(f"⚠️ Alembic migration failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Alembic migration error: {e}")
        
        # If alembic fails, try manual table creation
        logger.info("Attempting manual table creation...")
        try:
            result = subprocess.run(
                ["python", "create_admin_table.py"],
                cwd="/opt/render/project/src",
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ Manual table creation successful")
                return True
            else:
                logger.error(f"❌ Manual table creation failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Manual table creation error: {e}")
            
        return False
        
    except Exception as e:
        logger.error(f"❌ Database setup failed: {e}")
        return False

def start_app():
    """Start the FastAPI application"""
    try:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        logger.info("🚀 Starting FastAPI application...")
        
        # Start uvicorn server
        os.execvp("uvicorn", [
            "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", str(os.getenv("PORT", "10000"))
        ])
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Setup database first
    db_success = setup_database()
    if not db_success:
        print("⚠️ Database setup failed, but starting app anyway...")
        print("⚠️ Admin settings will use in-memory fallback")
    
    # Start the application
    start_app()
