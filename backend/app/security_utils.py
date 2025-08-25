# backend/app/security_utils.py

import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse
import ipaddress
from fastapi import Request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityValidator:
    """Utility class for security validation operations"""
    
    @staticmethod
    def extract_origin_from_request(request: Request) -> Optional[str]:
        """Extract origin from request headers with fallbacks"""
        # Try Origin header first (most reliable for CORS)
        origin = request.headers.get('origin')
        if origin:
            return origin.lower().rstrip('/')
        
        # Fallback to Referer header
        referer = request.headers.get('referer')
        if referer:
            try:
                parsed = urlparse(referer)
                return f"{parsed.scheme}://{parsed.netloc}".lower()
            except Exception as e:
                logger.warning(f"Failed to parse referer header: {referer}, error: {e}")
        
        return None
    
    @staticmethod
    def get_client_ip(request: Request) -> Optional[str]:
        """Get client IP address from request"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get('x-forwarded-for')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        forwarded = request.headers.get('x-forwarded-host')
        if forwarded:
            return forwarded.strip()
        
        # Check for real IP header
        real_ip = request.headers.get('x-real-ip')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to client IP
        if hasattr(request, 'client') and request.client:
            return request.client.host
        
        return None
    
    @staticmethod
    def is_valid_origin(origin: Optional[str], allowed_origins: list) -> bool:
        """Check if origin is in allowed list"""
        if not origin:
            return False
        
        origin = origin.lower().rstrip('/')
        allowed_origins_normalized = [o.lower().rstrip('/') for o in allowed_origins]
        
        return origin in allowed_origins_normalized
    
    @staticmethod
    def is_dev_ip(client_ip: Optional[str], allowed_dev_ips: list) -> bool:
        """Check if client IP is in development IP allowlist"""
        if not client_ip:
            return False
        
        try:
            client_addr = ipaddress.ip_address(client_ip)
            
            for allowed_ip in allowed_dev_ips:
                try:
                    # Handle localhost variations
                    if allowed_ip.lower() in ['localhost', 'local']:
                        if client_addr.is_loopback:
                            return True
                        continue
                    
                    # Handle IP addresses or networks
                    allowed_addr = ipaddress.ip_address(allowed_ip)
                    if client_addr == allowed_addr:
                        return True
                        
                except ValueError:
                    # Not a valid IP, try as network
                    try:
                        network = ipaddress.ip_network(allowed_ip, strict=False)
                        if client_addr in network:
                            return True
                    except ValueError:
                        continue
                        
        except ValueError:
            logger.warning(f"Invalid client IP format: {client_ip}")
            return False
        
        return False
    
    @staticmethod
    def is_admin_route(path: str) -> bool:
        """Check if the request path is an admin route that requires API key"""
        admin_prefixes = ['/admin', '/api/admin', '/logs', '/api/logs']
        
        # Exclude admin login routes from API key requirement
        admin_login_exceptions = ['/admin/login', '/api/admin/login']
        
        # If it's an admin login route, don't treat as protected admin route
        if any(path.startswith(exception) for exception in admin_login_exceptions):
            return False
            
        return any(path.startswith(prefix) for prefix in admin_prefixes)
    
    @staticmethod
    def validate_api_key(request: Request, expected_key: str) -> bool:
        """Validate API key from request headers"""
        api_key = request.headers.get('x-api-key') or request.headers.get('api-key')
        return api_key == expected_key if api_key and expected_key else False
    
    @staticmethod
    def create_validation_context(request: Request) -> Dict[str, Any]:
        """Create context dictionary for validation logging"""
        return {
            'method': request.method,
            'path': request.url.path,
            'origin': SecurityValidator.extract_origin_from_request(request),
            'client_ip': SecurityValidator.get_client_ip(request),
            'user_agent': request.headers.get('user-agent', 'Unknown'),
            'referer': request.headers.get('referer'),
            'has_api_key': bool(request.headers.get('x-api-key') or request.headers.get('api-key'))
        }
