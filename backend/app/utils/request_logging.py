import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.

    Logs request details including method, path, execution time,
    status code, and response size for monitoring and debugging.
    """

    def __init__(self, app, log_bodies: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_bodies = log_bodies
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Start timing
        start_time = time.time()

        # Extract client info
        client_ip = self.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # Log request start
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query_params": str(request.url.query) if request.url.query else None,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
            },
        )

        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id

        try:
            # Process request
            response = await call_next(request)

            # Calculate execution time
            execution_time = time.time() - start_time

            # Get response size
            response_size = None
            if hasattr(response, "headers") and "content-length" in response.headers:
                response_size = response.headers["content-length"]

            # Log successful request completion
            logger.info(
                f"Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": response.status_code,
                    "execution_time": round(execution_time, 4),
                    "response_size": response_size,
                },
            )

            # Add request ID to response headers for tracking
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Calculate execution time for failed requests
            execution_time = time.time() - start_time

            # Log request failure
            logger.error(
                f"Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "execution_time": round(execution_time, 4),
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )

            # Re-raise the exception
            raise

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (when behind proxy/load balancer)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client address
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"


def setup_request_logging(app, **kwargs):
    """
    Add request logging middleware to FastAPI application.

    Args:
        app: FastAPI application instance
        **kwargs: Additional configuration for RequestLoggingMiddleware
    """
    app.add_middleware(RequestLoggingMiddleware, **kwargs)
    logger.info("Request logging middleware added to application")


def get_request_id(request: Request) -> str:
    """
    Get the request ID from the request state.

    Args:
        request: FastAPI request object

    Returns:
        Request ID string, or 'unknown' if not found
    """
    return getattr(request.state, "request_id", "unknown")


class RequestLogger:
    """
    Context manager for adding request context to log messages.

    Usage:
        with RequestLogger(request) as req_logger:
            req_logger.info("Processing user data")
    """

    def __init__(self, request: Request):
        self.request = request
        self.request_id = get_request_id(request)
        self.logger = logging.getLogger(__name__)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def info(self, message: str, **kwargs):
        """Log info message with request context."""
        extra = kwargs.get("extra", {})
        extra["request_id"] = self.request_id
        kwargs["extra"] = extra
        self.logger.info(message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with request context."""
        extra = kwargs.get("extra", {})
        extra["request_id"] = self.request_id
        kwargs["extra"] = extra
        self.logger.error(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with request context."""
        extra = kwargs.get("extra", {})
        extra["request_id"] = self.request_id
        kwargs["extra"] = extra
        self.logger.warning(message, **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with request context."""
        extra = kwargs.get("extra", {})
        extra["request_id"] = self.request_id
        kwargs["extra"] = extra
        self.logger.debug(message, **kwargs)
