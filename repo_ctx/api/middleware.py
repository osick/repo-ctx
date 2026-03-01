"""Middleware for the repo-ctx API.

This module provides middleware components for:
- Request logging with timing
- Rate limit headers
- Security headers
"""

import logging
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("repo_ctx.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log timing.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response from handler.
        """
        start_time = time.time()

        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Log request
        status_code = response.status_code
        log_level = logging.INFO if status_code < 400 else logging.WARNING

        logger.log(
            log_level,
            f"{method} {path} - {status_code} - {duration_ms:.2f}ms - {client_ip}",
        )

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with security headers.
        """
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding rate limit headers."""

    def __init__(self, app, limit: int = 100, window: int = 60):
        """Initialize middleware.

        Args:
            app: FastAPI application.
            limit: Rate limit (requests per window).
            window: Rate limit window in seconds.
        """
        super().__init__(app)
        self.limit = limit
        self.window = window

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add rate limit headers to response.

        Args:
            request: Incoming request.
            call_next: Next middleware/handler.

        Returns:
            Response with rate limit headers.
        """
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.limit)
        response.headers["X-RateLimit-Window"] = str(self.window)

        return response
