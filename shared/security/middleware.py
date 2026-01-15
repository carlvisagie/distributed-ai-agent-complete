"""
Security Middleware for FastAPI
Provides authentication, rate limiting, and CORS
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
import logging

from .auth import auth_manager

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for FastAPI
    Checks API key on all requests except public endpoints
    """
    
    def __init__(self, app, public_paths: list = None):
        super().__init__(app)
        self.public_paths = public_paths or [
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip auth for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Extract API key from header
        api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
        
        if api_key and api_key.startswith("Bearer "):
            api_key = api_key[7:]  # Remove "Bearer " prefix
        
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "API key required", "detail": "Provide X-API-Key header"}
            )
        
        # Verify API key
        key_obj = auth_manager.verify_key(api_key)
        if not key_obj:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"}
            )
        
        # Check rate limit
        if not auth_manager.check_rate_limit(api_key):
            rate_status = auth_manager.get_rate_limit_status(api_key)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "limit": rate_status['limit'],
                    "reset_at": rate_status['reset_at']
                }
            )
        
        # Add API key info to request state
        request.state.api_key = key_obj
        
        # Log request
        logger.info(f"API request from {key_obj.name}: {request.method} {request.url.path}")
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        rate_status = auth_manager.get_rate_limit_status(api_key)
        response.headers["X-RateLimit-Limit"] = str(rate_status['limit'])
        response.headers["X-RateLimit-Remaining"] = str(rate_status['remaining'])
        response.headers["X-RateLimit-Reset"] = rate_status['reset_at']
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request logging middleware
    Logs all requests with timing information
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Duration: {duration:.3f}s"
        )
        
        # Add timing header
        response.headers["X-Process-Time"] = f"{duration:.3f}"
        
        return response


def setup_security(app, allowed_origins: list = None):
    """
    Setup security middleware for FastAPI app
    
    Args:
        app: FastAPI application
        allowed_origins: List of allowed CORS origins
    """
    # CORS middleware
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8080",
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Authentication (add last so it runs first)
    app.add_middleware(
        AuthMiddleware,
        public_paths=[
            "/",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/health"
        ]
    )
    
    logger.info("Security middleware configured")


def require_permission(permission: str):
    """
    Dependency for FastAPI endpoints requiring specific permission
    
    Usage:
        @app.get("/api/admin")
        async def admin_endpoint(request: Request, _: None = Depends(require_permission("admin"))):
            return {"message": "Admin access granted"}
    """
    def check_permission(request: Request):
        if not hasattr(request.state, 'api_key'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        api_key = request.state.api_key
        if permission not in api_key.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required"
            )
        
        return None
    
    return check_permission


# Example FastAPI app setup
if __name__ == "__main__":
    from fastapi import FastAPI, Depends
    import uvicorn
    
    app = FastAPI(title="Secure API Example")
    
    # Setup security
    setup_security(app)
    
    @app.get("/")
    async def root():
        return {"message": "Public endpoint - no auth required"}
    
    @app.get("/api/data")
    async def get_data(request: Request):
        api_key = request.state.api_key
        return {
            "message": "Protected data",
            "authenticated_as": api_key.name
        }
    
    @app.get("/api/admin")
    async def admin_endpoint(
        request: Request,
        _: None = Depends(require_permission("admin"))
    ):
        return {"message": "Admin access granted"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    print("\n" + "="*60)
    print("🔒 Secure API Server Starting")
    print("="*60)
    print("\nEndpoints:")
    print("  Public:    GET  /")
    print("  Public:    GET  /health")
    print("  Protected: GET  /api/data      (requires API key)")
    print("  Admin:     GET  /api/admin     (requires admin permission)")
    print("\nTo generate an API key, run:")
    print("  python shared/security/auth.py")
    print("\nThen use it in requests:")
    print("  curl -H 'X-API-Key: YOUR_KEY' http://localhost:8000/api/data")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
