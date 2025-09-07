#!/usr/bin/env python3
"""
Run database migration to add traffic_logs table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import TrafficLog
from sqlalchemy import text

def run_migration():
    """Run the traffic logs table migration"""
    try:
        print("Running traffic logs table migration...")
        
        # Check if table already exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'traffic_logs'
                );
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("traffic_logs table already exists. Skipping migration.")
                return
        
        # Create the table using SQLAlchemy
        print("Creating traffic_logs table...")
        TrafficLog.__table__.create(engine)
        
        print("Migration completed successfully!")
        print("Traffic logs will now be persisted across server restarts!")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
