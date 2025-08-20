import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

from fastapi import HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class RateLimitConfig(BaseModel):
    """Configuration for rate limiting."""

    window_seconds: int
    max_requests: int
    block_duration_seconds: Optional[int] = None


class RateLimiter:
    """
    In-memory rate limiter with configurable windows and limits.

    Tracks request counts per client and endpoint, with automatic cleanup
    of expired entries.
    """

    def __init__(self):
        # Structure: {client_id: {endpoint: [(timestamp, count), ...]}}
        self.requests: Dict[str, Dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        # Structure: {client_id: {endpoint: block_until_timestamp}}
        self.blocked: Dict[str, Dict[str, float]] = defaultdict(dict)

    def _cleanup_old_requests(self, client_id: str, endpoint: str, window_seconds: int):
        """Remove expired request records."""
        now = time.time()
        cutoff = now - window_seconds

        self.requests[client_id][endpoint] = [
            (timestamp, count)
            for timestamp, count in self.requests[client_id][endpoint]
            if timestamp > cutoff
        ]

    def _cleanup_expired_blocks(self):
        """Remove expired blocks."""
        now = time.time()
        for client_id in list(self.blocked.keys()):
            for endpoint in list(self.blocked[client_id].keys()):
                if self.blocked[client_id][endpoint] <= now:
                    del self.blocked[client_id][endpoint]
            if not self.blocked[client_id]:
                del self.blocked[client_id]

    def is_rate_limited(
        self, client_id: str, endpoint: str, config: RateLimitConfig
    ) -> bool:
        """
        Check if a client is rate limited for an endpoint.

        Args:
            client_id: Unique identifier for the client
            endpoint: Endpoint identifier
            config: Rate limit configuration

        Returns:
            True if rate limited, False otherwise
        """
        now = time.time()

        # Clean up expired data
        self._cleanup_expired_blocks()
        self._cleanup_old_requests(client_id, endpoint, config.window_seconds)

        # Check if currently blocked
        if endpoint in self.blocked[client_id]:
            if self.blocked[client_id][endpoint] > now:
                return True
            else:
                del self.blocked[client_id][endpoint]

        # Count recent requests
        recent_requests = self.requests[client_id][endpoint]
        total_requests = sum(count for _, count in recent_requests)

        # Check if limit exceeded
        if total_requests >= config.max_requests:
            # Block if configured
            if config.block_duration_seconds:
                self.blocked[client_id][endpoint] = now + config.block_duration_seconds

            logger.warning(
                f"Rate limit exceeded for client {client_id} on endpoint {endpoint}",
                extra={
                    "client_id": client_id,
                    "endpoint": endpoint,
                    "request_count": total_requests,
                    "limit": config.max_requests,
                    "window_seconds": config.window_seconds,
                },
            )
            return True

        return False

    def record_request(self, client_id: str, endpoint: str):
        """Record a request for rate limiting."""
        now = time.time()
        self.requests[client_id][endpoint].append((now, 1))

    def get_remaining_requests(
        self, client_id: str, endpoint: str, config: RateLimitConfig
    ) -> int:
        """Get number of remaining requests in the current window."""
        self._cleanup_old_requests(client_id, endpoint, config.window_seconds)
        recent_requests = self.requests[client_id][endpoint]
        total_requests = sum(count for _, count in recent_requests)
        return max(0, config.max_requests - total_requests)

    def get_reset_time(
        self, client_id: str, endpoint: str, config: RateLimitConfig
    ) -> Optional[datetime]:
        """Get time when rate limit resets."""
        if not self.requests[client_id][endpoint]:
            return None

        oldest_request = min(
            timestamp for timestamp, _ in self.requests[client_id][endpoint]
        )
        reset_time = oldest_request + config.window_seconds
        return datetime.fromtimestamp(reset_time)


# Singleton instance
limiter = RateLimiter()

# Standard rate limit configurations
RATE_LIMIT_CONFIGS = {
    "auth": RateLimitConfig(
        window_seconds=60, max_requests=5, block_duration_seconds=300
    ),
    "signup": RateLimitConfig(
        window_seconds=3600, max_requests=3, block_duration_seconds=3600
    ),
    "default": RateLimitConfig(window_seconds=60, max_requests=30),
    "api": RateLimitConfig(window_seconds=60, max_requests=120),
}


def rate_limit(endpoint_type: str = "default"):
    """
    Decorator for rate limiting endpoints.

    Args:
        endpoint_type: Type of endpoint (auth, signup, default, api)

    Usage:
        @router.post("/login")
        @rate_limit("auth")
        async def login(request: Request, ...):
            ...
    """

    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            # Find the request object in args or kwargs
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                # If no request found, proceed without rate limiting
                return await func(*args, **kwargs)

            # Get client identifier
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("user-agent", "")
            client_id = f"{client_ip}:{hash(user_agent) % 10000}"

            # Get endpoint identifier
            endpoint = f"{request.method}:{request.url.path}"

            # Get rate limit config
            config = RATE_LIMIT_CONFIGS.get(
                endpoint_type, RATE_LIMIT_CONFIGS["default"]
            )

            # Check rate limit
            if limiter.is_rate_limited(client_id, endpoint, config):
                reset_time = limiter.get_reset_time(client_id, endpoint, config)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": int(config.window_seconds),
                        "reset_time": reset_time.isoformat() if reset_time else None,
                    },
                )

            # Record the request
            limiter.record_request(client_id, endpoint)

            # Execute the function
            return await func(*args, **kwargs)

        return wrapper

    return decorator
