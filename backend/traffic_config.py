# backend/traffic_config.py

import os
from typing import List
from app.env_loader import load_env

load_env()

class TrafficConfig:
    """Configuration for traffic logging system"""
    
    # Enable/disable traffic logging
    ENABLED: bool = os.getenv('TRAFFIC_LOGGING_ENABLED', 'true').lower() == 'true'
    
    # Log file settings
    LOG_DIR: str = os.path.join(os.path.dirname(__file__), 'logs', 'traffic')
    RETENTION_DAYS: int = int(os.getenv('TRAFFIC_LOG_RETENTION_DAYS', '30'))
    
    # Privacy settings
    HASH_IP_ADDRESSES: bool = os.getenv('TRAFFIC_HASH_IPS', 'true').lower() == 'true'
    
    # Paths to exclude from traffic logging
    EXCLUDED_PATHS: List[str] = [
        '/health',
        '/ping', 
        '/status',
        '/ready',
        '/docs',
        '/redoc',
        '/openapi.json',
        '/favicon.ico'
    ]
    
    # File extensions to exclude (static files)
    EXCLUDED_EXTENSIONS: List[str] = [
        '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', 
        '.svg', '.woff', '.woff2', '.ttf', '.eot'
    ]
    
    # IP addresses to exclude (internal/admin IPs)
    EXCLUDED_IPS: List[str] = [
        '127.0.0.1',
        'localhost',
        '::1'
    ]

# Global configuration instance
traffic_config = TrafficConfig()

