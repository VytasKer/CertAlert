# backend/app/logging_config.py

import logging
import os
from pathlib import Path

# Ensure logs directory structure exists
log_dir = Path(__file__).parent.parent / "logs" / "app"
log_dir.mkdir(parents=True, exist_ok=True)

# Use the new app log location
app_log_path = log_dir / "app.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(app_log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)