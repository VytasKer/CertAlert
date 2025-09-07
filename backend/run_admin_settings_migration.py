#!/usr/bin/env python3
"""Run Alembic migration to add admin settings table"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alembic.config import Config
from alembic import command
import logging

def run_migration():
    """Run the admin settings table migration"""
    try:
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Create Alembic configuration
        alembic_cfg = Config("alembic.ini")
        
        # Run the migration
        logger.info("Running migration: Add admin settings table")
        command.upgrade(alembic_cfg, "head")
        logger.info("Migration completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    if not success:
        sys.exit(1)
    print("✅ Admin settings table migration completed successfully!")
