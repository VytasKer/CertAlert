# backend/app/startup_cleanup.py

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def cleanup_old_log_files():
    """One-time cleanup of old log files on production startup"""
    try:
        backend_dir = Path(__file__).parent.parent
        old_log_path = backend_dir / "app.log"
        
        if old_log_path.exists():
            old_size = old_log_path.stat().st_size
            old_log_path.unlink()  # Delete the old log
            logger.info(f"Cleaned up old app.log file ({old_size:,} bytes)")
        else:
            logger.info("No old app.log file found to cleanup")
            
    except Exception as e:
        logger.warning(f"Failed to cleanup old log file: {e}")
        # Don't let cleanup failure affect app startup
