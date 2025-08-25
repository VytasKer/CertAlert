# backend/tests/test_origin_validation.py

"""
Test script for origin validation middleware configuration and functionality.
Run this to verify the middleware is working correctly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.config import security_config
from app.security_utils import SecurityValidator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_configuration():
    """Test that configuration loads correctly"""
    print("=== Testing Configuration ===")
    print(f"Allowed Origins: {security_config.ALLOWED_ORIGINS}")
    print(f"Admin API Key: {'***' + security_config.ADMIN_API_KEY[-4:] if security_config.ADMIN_API_KEY else 'NOT SET'}")
    print(f"Dev Mode: {security_config.DEV_MODE}")
    print(f"Enable Validation: {security_config.ENABLE_ORIGIN_VALIDATION}")
    print(f"Allowed Dev IPs: {security_config.ALLOWED_DEV_IPS}")
    print(f"Strict Validation: {security_config.STRICT_ORIGIN_VALIDATION}")
    print(f"Should Validate: {security_config.should_validate_origin()}")
    print()

def test_origin_validation():
    """Test origin validation logic"""
    print("=== Testing Origin Validation ===")
    
    test_cases = [
        ("http://localhost:5173", True, "Valid development origin"),
        ("http://localhost:3000", True, "Valid development origin (alternate port)"),
        ("https://evil-site.com", False, "Invalid origin"),
        ("http://127.0.0.1:5173", True, "Valid localhost IP"),
        (None, None, "No origin (depends on dev mode)"),
        ("", False, "Empty origin"),
    ]
    
    for origin, expected, description in test_cases:
        result = SecurityValidator.is_valid_origin(origin, security_config.get_all_allowed_origins())
        status = "✓" if (result == expected or expected is None) else "✗"
        print(f"{status} {description}: {origin} -> {result}")
    print()

def test_ip_validation():
    """Test IP validation logic"""
    print("=== Testing IP Validation ===")
    
    test_cases = [
        ("127.0.0.1", True, "Localhost IPv4"),
        ("::1", True, "Localhost IPv6"),
        ("192.168.1.1", False, "Private network IP"),
        ("8.8.8.8", False, "Public IP"),
        (None, False, "No IP"),
        ("invalid-ip", False, "Invalid IP format"),
    ]
    
    for ip, expected, description in test_cases:
        result = SecurityValidator.is_dev_ip(ip, security_config.ALLOWED_DEV_IPS)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}: {ip} -> {result}")
    print()

def test_admin_route_detection():
    """Test admin route detection"""
    print("=== Testing Admin Route Detection ===")
    
    test_cases = [
        ("/admin/users", True, "Admin users route"),
        ("/api/admin/logs", True, "API admin logs route"),
        ("/logs/system", True, "System logs route"),
        ("/admin/login", False, "Admin login route (should be excluded)"),
        ("/api/admin/login", False, "API admin login route (should be excluded)"),
        ("/users/profile", False, "Regular user route"),
        ("/certificates", False, "Regular certificate route"),
        ("/", False, "Root route"),
    ]
    
    for path, expected, description in test_cases:
        result = SecurityValidator.is_admin_route(path)
        status = "✓" if result == expected else "✗"
        print(f"{status} {description}: {path} -> {result}")
    print()

if __name__ == "__main__":
    print("CertAlert Origin Validation Middleware Test")
    print("=" * 50)
    print()
    
    test_configuration()
    test_origin_validation()
    test_ip_validation()
    test_admin_route_detection()
    
    print("Testing completed!")
    print()
    print("Configuration Summary:")
    print(f"  - Validation {'ENABLED' if security_config.should_validate_origin() else 'DISABLED'}")
    print(f"  - Mode: {'DEVELOPMENT' if security_config.is_dev_environment() else 'PRODUCTION'}")
    print(f"  - Strictness: {'STRICT' if security_config.STRICT_ORIGIN_VALIDATION else 'PERMISSIVE'}")
