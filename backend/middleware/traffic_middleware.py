# backend/middleware/traffic_middleware.py

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.traffic_logger import traffic_logger

# Configure logging
logger = logging.getLogger("traffic_middleware")

class TrafficLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log traffic data without interfering with existing functionality.
    
    This middleware is designed to be completely non-intrusive:
    - Does not modify request/response data
    - Does not add headers
    - Does not change authentication flow
    - Logs asynchronously to avoid performance impact
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        logger.info("Traffic logging middleware initialized")
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log traffic data without modifying request/response flow"""
        
        # Record start time for response time calculation
        start_time = time.time()
        
        # Extract user ID if available (without modifying auth flow)
        user_id = None
        try:
            # Try to get user ID from request state if available
            # This won't interfere with existing auth since we're just reading
            if hasattr(request.state, 'user_id'):
                user_id = request.state.user_id
        except Exception:
            # Silently ignore if user info not available
            pass
        
        # Call the next middleware/route handler
        response = await call_next(request)
        
        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000
        
        # Log the request asynchronously (fire and forget)
        # This won't block the response or interfere with existing functionality
        try:
            await traffic_logger.log_request(
                request=request,
                response_status=response.status_code,
                response_time_ms=response_time_ms,
                user_id=user_id
            )
        except Exception as e:
            # Log error but don't let it affect the response
            logger.error(f"Traffic logging error (non-blocking): {e}")
        
        # Return unmodified response
        return response
