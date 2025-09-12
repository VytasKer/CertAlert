#!/usr/bin/env python3
"""
Manual script to create admin_settings table if migration fails
Uses the same approach as run_traffic_migration.py for consistency
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import AdminSetting
from sqlalchemy import text
import logging

def create_admin_settings_table():
    """Create the admin_settings table using direct SQLAlchemy approach"""
    try:
        print("Running admin_settings table creation...")
        
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'admin_settings'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("admin_settings table already exists. Skipping creation.")
            else:
                # Create the table using SQLAlchemy
                print("Creating admin_settings table...")
                AdminSetting.__table__.create(engine)
                print("✅ admin_settings table created successfully!")
        
        # Insert default values
        print("Ensuring default settings exist...")
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO admin_settings (key, value) 
                VALUES ('traffic_log_retention_days', '30')
                ON CONFLICT (key) DO NOTHING;
            """))
            conn.commit()
            print("✅ Default settings initialized!")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to create admin_settings table: {e}")
        return False

if __name__ == "__main__":
    success = create_admin_settings_table()
    if not success:
        print("❌ Table creation failed. Check logs for details.")
        sys.exit(1)
    print("✅ admin_settings table is ready!")
