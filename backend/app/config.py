# backend/app/config.py

import os
from typing import List, Optional
from dotenv import load_dotenv
import sys

# Determine the correct path to the .env file
if os.path.exists("../../.env"):
    env_path = "../../.env"
elif os.path.exists("../.env"):
    env_path = "../.env"
elif os.path.exists(".env"):
    env_path = ".env"
else:
    # Look for .env in the CertAlert root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    env_path = os.path.join(project_root, ".env")

# Load environment variables
load_dotenv(dotenv_path=env_path)

class SecurityConfig:
    """Configuration class for origin validation and security settings"""
    
    # Origin Validation Settings
    ALLOWED_ORIGINS: List[str] = os.getenv(
        'ALLOWED_ORIGINS', 
        'http://localhost:5173,http://localhost:3000'
    ).split(',')
    
    # Remove any empty strings and strip whitespace
    ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]
    
    # Admin API Key for administrative operations
    ADMIN_API_KEY: str = os.getenv('ADMIN_API_KEY', 'default-insecure-key')
    
    # Development mode settings
    DEV_MODE: bool = os.getenv('DEV_MODE', 'false').lower() == 'true'
    
    # Enable/disable origin validation entirely
    ENABLE_ORIGIN_VALIDATION: bool = os.getenv('ENABLE_ORIGIN_VALIDATION', 'true').lower() == 'true'
    
    # Allowed development IPs (for direct API testing)
    ALLOWED_DEV_IPS: List[str] = os.getenv(
        'ALLOWED_DEV_IPS', 
        '127.0.0.1,localhost,::1'
    ).split(',')
    ALLOWED_DEV_IPS = [ip.strip() for ip in ALLOWED_DEV_IPS if ip.strip()]
    
    # Strict validation (reject requests without proper headers)
    STRICT_ORIGIN_VALIDATION: bool = os.getenv('STRICT_ORIGIN_VALIDATION', 'false').lower() == 'true'
    
    # API Documentation settings
    ENABLE_API_DOCS: bool = os.getenv('ENABLE_API_DOCS', 'true').lower() == 'true'
    PROTECT_API_DOCS: bool = os.getenv('PROTECT_API_DOCS', 'true').lower() == 'true'
    
    # Base URLs for reference
    FRONTEND_BASE_URL: str = os.getenv('FRONTEND_BASE_URL', 'http://localhost:5173')
    BACKEND_BASE_URL: str = os.getenv('BACKEND_BASE_URL', 'http://localhost:8000')
    
    @classmethod
    def get_all_allowed_origins(cls) -> List[str]:
        """Get all allowed origins including base URL if not already included"""
        origins = cls.ALLOWED_ORIGINS.copy()
        if cls.FRONTEND_BASE_URL not in origins:
            origins.append(cls.FRONTEND_BASE_URL)
        return origins
    
    @classmethod
    def is_dev_environment(cls) -> bool:
        """Check if we're in development environment"""
        return cls.DEV_MODE or os.getenv('ENVIRONMENT', 'development').lower() == 'development'
    
    @classmethod
    def should_validate_origin(cls) -> bool:
        """Determine if origin validation should be applied"""
        return cls.ENABLE_ORIGIN_VALIDATION and not (cls.is_dev_environment() and not cls.STRICT_ORIGIN_VALIDATION)

# Create global config instance
security_config = SecurityConfig()
