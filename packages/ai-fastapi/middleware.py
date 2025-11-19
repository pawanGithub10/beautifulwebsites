"""
FastAPI middleware for AI platform error handling and logging
"""

from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import logging
import time
import traceback

logger = logging.getLogger(__name__)


class AIErrorHandler(BaseHTTPMiddleware):
    """
    Middleware for handling AI-related errors consistently.

    Catches exceptions from AI operations and returns user-friendly error responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and handle any errors"""
        try:
            response = await call_next(request)
            return response

        except ValueError as e:
            # Validation errors
            logger.warning(f"Validation error: {str(e)}")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Validation Error",
                    "detail": str(e),
                    "status_code": 400
                }
            )

        except PermissionError as e:
            # Permission/quota errors
            logger.warning(f"Permission error: {str(e)}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Permission Denied",
                    "detail": str(e),
                    "status_code": 403
                }
            )

        except ConnectionError as e:
            # Provider connection errors
            logger.error(f"Provider connection error: {str(e)}")
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "detail": "AI provider is temporarily unavailable. Please try again.",
                    "status_code": 503
                }
            )

        except TimeoutError as e:
            # Request timeout errors
            logger.error(f"Timeout error: {str(e)}")
            return JSONResponse(
                status_code=504,
                content={
                    "error": "Request Timeout",
                    "detail": "AI request took too long. Please try again with a simpler request.",
                    "status_code": 504
                }
            )

        except Exception as e:
            # Unexpected errors
            logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred. Please try again later.",
                    "status_code": 500
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging AI requests and performance metrics.

    Logs request details, response times, and token usage for monitoring.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details"""
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"AI Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown"
            }
        )

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"AI Response: {response.status_code} in {duration:.3f}s",
            extra={
                "status_code": response.status_code,
                "duration": duration,
                "path": request.url.path
            }
        )

        # Add performance headers
        response.headers["X-Process-Time"] = str(duration)

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware for AI endpoints.

    Prevents abuse by limiting requests per IP address.
    """

    def __init__(self, app: FastAPI, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds (default: 1 hour)
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # In production, use Redis

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and process request"""
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)

        # Get current timestamp
        current_time = time.time()

        # Initialize or clean up old requests
        if client_ip not in self.requests:
            self.requests[client_ip] = []

        # Remove old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate Limit Exceeded",
                    "detail": f"Maximum {self.max_requests} requests per {self.window_seconds}s allowed",
                    "status_code": 429
                }
            )

        # Record this request
        self.requests[client_ip].append(current_time)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))

        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """
    Custom CORS middleware for AI endpoints.

    Handles cross-origin requests for web applications.
    """

    def __init__(
        self,
        app: FastAPI,
        allow_origins: list = ["*"],
        allow_methods: list = ["*"],
        allow_headers: list = ["*"]
    ):
        """
        Initialize CORS middleware.

        Args:
            app: FastAPI application
            allow_origins: List of allowed origins
            allow_methods: List of allowed HTTP methods
            allow_headers: List of allowed headers
        """
        super().__init__(app)
        self.allow_origins = allow_origins
        self.allow_methods = allow_methods
        self.allow_headers = allow_headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add CORS headers to response"""
        # Handle preflight requests
        if request.method == "OPTIONS":
            return Response(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": ", ".join(self.allow_origins),
                    "Access-Control-Allow-Methods": ", ".join(self.allow_methods),
                    "Access-Control-Allow-Headers": ", ".join(self.allow_headers),
                }
            )

        # Process request
        response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = ", ".join(self.allow_origins)
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)

        return response


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def add_ai_middleware(
    app: FastAPI,
    enable_error_handler: bool = True,
    enable_logging: bool = True,
    enable_rate_limit: bool = False,
    rate_limit_requests: int = 100,
    rate_limit_window: int = 3600
) -> FastAPI:
    """
    Add AI middleware to FastAPI application.

    Call this function to configure all AI-related middleware at once.

    Args:
        app: FastAPI application
        enable_error_handler: Enable error handling middleware
        enable_logging: Enable request logging middleware
        enable_rate_limit: Enable rate limiting middleware
        rate_limit_requests: Max requests per window
        rate_limit_window: Rate limit window in seconds

    Returns:
        FastAPI app with middleware configured

    Example:
        ```python
        from fastapi import FastAPI
        from ai_fastapi.middleware import add_ai_middleware

        app = FastAPI()
        app = add_ai_middleware(
            app,
            enable_error_handler=True,
            enable_logging=True,
            enable_rate_limit=True,
            rate_limit_requests=100
        )
        ```
    """
    # Add middleware in reverse order (last added is executed first)

    if enable_rate_limit:
        app.add_middleware(
            RateLimitMiddleware,
            max_requests=rate_limit_requests,
            window_seconds=rate_limit_window
        )
        logger.info(f"Rate limiting enabled: {rate_limit_requests} requests per {rate_limit_window}s")

    if enable_logging:
        app.add_middleware(RequestLoggingMiddleware)
        logger.info("Request logging enabled")

    if enable_error_handler:
        app.add_middleware(AIErrorHandler)
        logger.info("Error handling enabled")

    return app


def configure_logging(level: str = "INFO", format_json: bool = False) -> None:
    """
    Configure logging for the AI platform.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_json: Use JSON format for structured logging

    Example:
        ```python
        from ai_fastapi.middleware import configure_logging

        configure_logging(level="INFO", format_json=True)
        ```
    """
    if format_json:
        # JSON formatted logging for production
        import json_logging
        json_logging.init_fastapi(enable_json=True)
        json_logging.init_request_instrument(app)
    else:
        # Standard logging format
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    logger.info(f"Logging configured: level={level}, json={format_json}")
