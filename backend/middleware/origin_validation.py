# backend/middleware/origin_validation.py

import logging
from typing import Callable
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import security_config
from app.security_utils import SecurityValidator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OriginValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate request origins and protect against unauthorized API access.
    
    Features:
    - Origin/Referer header validation
    - Admin route API key protection
    - Development IP allowlist
    - Configurable strict/permissive modes
    - Comprehensive logging
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.allowed_origins = security_config.get_all_allowed_origins()
        self.admin_api_key = security_config.ADMIN_API_KEY
        self.dev_mode = security_config.is_dev_environment()
        self.enable_validation = security_config.should_validate_origin()
        self.allowed_dev_ips = security_config.ALLOWED_DEV_IPS
        self.strict_mode = security_config.STRICT_ORIGIN_VALIDATION
        
        logger.info(f"Origin Validation Middleware initialized:")
        logger.info(f"  - Validation enabled: {self.enable_validation}")
        logger.info(f"  - Development mode: {self.dev_mode}")
        logger.info(f"  - Strict mode: {self.strict_mode}")
        logger.info(f"  - Allowed origins: {self.allowed_origins}")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Main middleware dispatch method"""
        
        # Skip validation if disabled
        if not self.enable_validation:
            return await call_next(request)
        
        # Handle CORS preflight requests - let CORS middleware handle these
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Skip validation for health checks and static files
        if self._should_skip_validation(request):
            return await call_next(request)
        
        # Create validation context for logging
        context = SecurityValidator.create_validation_context(request)
        
        try:
            # Validate the request
            validation_result = await self._validate_request(request, context)
            
            if not validation_result['valid']:
                return self._create_error_response(
                    validation_result['status_code'],
                    validation_result['message'],
                    context
                )
            
            # Log successful validation in dev mode
            if self.dev_mode and validation_result.get('log_success', False):
                logger.info(f"Request validated successfully: {context['method']} {context['path']}")
            
            # Continue to next middleware/route handler
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Error in origin validation middleware: {e}", extra={'context': context})
            # In case of middleware error, allow request to proceed but log the issue
            return await call_next(request)
    
    async def _validate_request(self, request: Request, context: dict) -> dict:
        """Perform request validation and return result"""
        
        path = request.url.path
        origin = context['origin']
        client_ip = context['client_ip']
        
        # Check if this is an API docs request
        docs_paths = ['/docs', '/redoc', '/openapi.json']
        if any(path.startswith(dp) for dp in docs_paths):
            return await self._validate_docs_request(request, context)
        
        # Check if this is an admin route
        is_admin_route = SecurityValidator.is_admin_route(path)
        
        if is_admin_route:
            return await self._validate_admin_request(request, context)
        
        # For non-admin routes, validate origin
        return await self._validate_origin_request(request, context)
    
    async def _validate_docs_request(self, request: Request, context: dict) -> dict:
        """Validate API documentation access"""
        
        # If docs are disabled entirely, block access
        if not security_config.ENABLE_API_DOCS:
            logger.warning(f"API docs access denied - documentation disabled", extra={'context': context})
            return {
                'valid': False,
                'status_code': 404,  # Return 404 to hide existence
                'message': 'Not Found'
            }
        
        # If docs protection is disabled (development), allow access
        if not security_config.PROTECT_API_DOCS:
            return {'valid': True, 'log_success': True}
        
        # Apply same validation as admin routes for protected docs
        # Option 1: Require API key for docs access
        if not SecurityValidator.validate_api_key(request, self.admin_api_key):
            logger.warning(f"API docs access denied - invalid/missing API key", extra={'context': context})
            return {
                'valid': False,
                'status_code': 401,
                'message': 'API key required to access documentation'
            }
        
        # Option 2: Also validate origin for docs
        origin_validation = await self._validate_origin_request(request, context, is_admin=False)
        if not origin_validation['valid']:
            logger.warning(f"API docs access denied - invalid origin", extra={'context': context})
            return origin_validation
        
        logger.info(f"API docs access granted", extra={'context': context})
        return {'valid': True, 'log_success': True}
    
    async def _validate_admin_request(self, request: Request, context: dict) -> dict:
        """Validate admin route requests"""
        
        # Check for API key first
        if not SecurityValidator.validate_api_key(request, self.admin_api_key):
            logger.warning(f"Admin route access denied - invalid/missing API key", extra={'context': context})
            return {
                'valid': False,
                'status_code': 401,
                'message': 'Valid API key required for admin operations'
            }
        
        # Also validate origin for admin routes
        origin_validation = await self._validate_origin_request(request, context, is_admin=True)
        if not origin_validation['valid']:
            logger.warning(f"Admin route access denied - invalid origin", extra={'context': context})
            return origin_validation
        
        logger.info(f"Admin route access granted", extra={'context': context})
        return {'valid': True, 'log_success': True}
    
    async def _validate_origin_request(self, request: Request, context: dict, is_admin: bool = False) -> dict:
        """Validate origin for regular requests"""
        
        origin = context['origin']
        client_ip = context['client_ip']
        path = context['path']
        
        # In development mode with non-strict validation, allow dev IPs
        if self.dev_mode and not self.strict_mode:
            if SecurityValidator.is_dev_ip(client_ip, self.allowed_dev_ips):
                return {'valid': True, 'log_success': True}
        
        # Validate origin header
        if SecurityValidator.is_valid_origin(origin, self.allowed_origins):
            return {'valid': True}
        
        # Handle requests without origin (direct API calls, postman, curl, etc.)
        if not origin:
            if self.dev_mode and not self.strict_mode:
                # Allow direct API calls in development
                logger.info(f"Direct API call allowed in dev mode: {path}", extra={'context': context})
                return {'valid': True, 'log_success': True}
            else:
                # In production or strict mode, reject requests without origin
                logger.warning(f"Request rejected - no origin header", extra={'context': context})
                return {
                    'valid': False,
                    'status_code': 403,
                    'message': 'Request must include valid origin header'
                }
        
        # Invalid origin
        logger.warning(f"Request rejected - invalid origin: {origin}", extra={'context': context})
        return {
            'valid': False,
            'status_code': 403,
            'message': f'Origin not allowed: {origin}'
        }
    
    def _should_skip_validation(self, request: Request) -> bool:
        """Determine if validation should be skipped for this request"""
        path = request.url.path.lower()
        
        # Skip for health checks
        health_paths = ['/health', '/ping', '/status', '/ready']
        if any(path.startswith(hp) for hp in health_paths):
            return True
        
        # Skip for webhook endpoints (server-to-server requests without Origin headers)
        webhook_paths = ['/stripe/webhook', '/webhook', '/webhooks']
        if any(path.startswith(wp) for wp in webhook_paths):
            logger.info(f"Webhook request - skipping origin validation: {path}")
            return True
        
        # Skip for static files
        static_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.woff', '.woff2']
        if any(path.endswith(ext) for ext in static_extensions):
            return True
        
        # Handle API docs based on configuration
        docs_paths = ['/docs', '/redoc', '/openapi.json']
        if any(path.startswith(dp) for dp in docs_paths):
            # If API docs are disabled entirely, block access
            if not security_config.ENABLE_API_DOCS:
                logger.warning(f"API docs access blocked - docs disabled", extra={'path': path})
                return False  # Don't skip validation, will be blocked
            
            # If docs protection is enabled, apply normal validation
            if security_config.PROTECT_API_DOCS:
                logger.info(f"API docs access requires validation", extra={'path': path})
                return False  # Don't skip validation, apply origin/API key checks
            
            # If docs protection is disabled (dev mode), skip validation
            logger.info(f"API docs access allowed without validation", extra={'path': path})
            return True
        
        return False
    
    def _create_error_response(self, status_code: int, message: str, context: dict) -> JSONResponse:
        """Create standardized error response with proper CORS headers"""
        
        logger.warning(f"Origin validation failed: {message}", extra={'context': context})
        
        # Get the origin from the request context for CORS headers
        origin = context.get('origin', '*')
        
        # Create response with CORS headers to allow browser to read the error
        return JSONResponse(
            status_code=status_code,
            content={
                'error': 'Access Denied',
                'message': message,
                'status_code': status_code
            },
            headers={
                'Access-Control-Allow-Origin': origin if origin and origin in self.allowed_origins else '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
                'Access-Control-Allow-Credentials': 'true'
            }
        )
