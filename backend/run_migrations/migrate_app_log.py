#!/usr/bin/env python3
"""
Migration script to move app.log to new directory structure
Run this script from the backend directory: python migrate_app_log.py
"""

import shutil
from pathlib import Path
import logging

def migrate_app_log():
    """Migrate existing app.log to new directory structure"""
    
    # Paths
    backend_dir = Path(__file__).parent
    old_log_path = backend_dir / "app.log"
    new_log_dir = backend_dir / "logs" / "app"
    new_log_path = new_log_dir / "app.log"
    backup_path = new_log_dir / "app-backup.log"
    
    print("=== CertAlert App Log Migration ===")
    print(f"Backend directory: {backend_dir}")
    print(f"Old log location: {old_log_path}")
    print(f"New log location: {new_log_path}")
    
    # Ensure new directory exists
    new_log_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created directory: {new_log_dir}")
    
    # Check if old log exists
    if not old_log_path.exists():
        print("ℹ No existing app.log found - migration not needed")
        return
    
    # Get old log size
    old_size = old_log_path.stat().st_size
    print(f"ℹ Found existing app.log ({old_size:,} bytes)")
    
    try:
        # If new log already exists, back it up
        if new_log_path.exists():
            shutil.copy2(new_log_path, backup_path)
            print(f"✓ Backed up existing new log to: {backup_path}")
        
        # Copy old log to new location (preserve original)
        shutil.copy2(old_log_path, new_log_path)
        print(f"✓ Copied app.log to new location")
        
        # Verify the copy
        new_size = new_log_path.stat().st_size
        if new_size == old_size:
            print(f"✓ Migration successful! ({new_size:,} bytes)")
            
            # Rename old file instead of deleting (safety)
            old_backup_path = backend_dir / "app-old.log"
            old_log_path.rename(old_backup_path)
            print(f"✓ Renamed old log to: {old_backup_path}")
            print(f"  (You can delete this file after confirming everything works)")
            
        else:
            print(f"✗ Size mismatch! Old: {old_size}, New: {new_size}")
            return False
            
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False
    
    print("\n=== Migration Complete ===")
    print("Next steps:")
    print("1. Restart your FastAPI application")
    print("2. Check that /logs/app-log endpoint works")
    print("3. Verify new logs are written to logs/app/app.log")
    print("4. Delete app-old.log when you're confident everything works")
    
    return True

if __name__ == "__main__":
    migrate_app_log()
