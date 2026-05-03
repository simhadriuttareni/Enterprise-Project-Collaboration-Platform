from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

# Define which paths require admin access
ADMIN_PATHS: Set[str] = {
    "/api/v1/admin",
    "/api/v1/users/admin",
}

class RoleMiddleware(BaseHTTPMiddleware):
    """Middleware for role-based access control"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add request ID for tracking
        request_id = request.headers.get("X-Request-ID", str(start_time))
        request.state.request_id = request_id
        
        # Process request
        try:
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Request-ID"] = request_id
            
            # Log request
            process_time = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def check_admin_access(self, path: str, user_role: str) -> bool:
        """Check if user has admin access to path"""
        for admin_path in ADMIN_PATHS:
            if path.startswith(admin_path):
                return user_role == "admin"
        return True