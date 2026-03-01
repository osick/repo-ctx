"""Authentication and authorization for the repo-ctx API.

This module provides:
- API key authentication for remote access
- No auth required for local access (localhost/127.0.0.1)
- Rate limiting
- Request logging
"""

import hashlib
import logging
import os
import time
from collections import defaultdict
from datetime import datetime
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger("repo_ctx.api.auth")

# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class AuthConfig(BaseModel):
    """Authentication configuration."""

    # API key (if set, authentication is required for remote access)
    api_key: Optional[str] = None

    # Hash of API key (computed from api_key)
    api_key_hash: Optional[str] = None

    # Whether to require auth for all requests (even local)
    require_auth_always: bool = False

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100  # Requests per window
    rate_limit_window: int = 60  # Window in seconds

    # Request logging
    log_requests: bool = True

    # Allowed origins for local access (no auth required)
    local_origins: list[str] = [
        "127.0.0.1",
        "localhost",
        "::1",
    ]


# Global configuration (can be updated at runtime)
_config = AuthConfig()

# Rate limit tracking: {client_ip: [(timestamp, count), ...]}
_rate_limit_tracker: dict[str, list[tuple[float, int]]] = defaultdict(list)


def configure_auth(
    api_key: Optional[str] = None,
    require_auth_always: bool = False,
    rate_limit_enabled: bool = True,
    rate_limit_requests: int = 100,
    rate_limit_window: int = 60,
    log_requests: bool = True,
) -> None:
    """Configure authentication settings.

    Args:
        api_key: API key for authentication. If None, uses REPO_CTX_API_KEY env var.
        require_auth_always: If True, require auth even for local requests.
        rate_limit_enabled: Enable rate limiting.
        rate_limit_requests: Max requests per window.
        rate_limit_window: Rate limit window in seconds.
        log_requests: Enable request logging.
    """
    global _config

    # Get API key from parameter or environment
    key = api_key or os.environ.get("REPO_CTX_API_KEY")

    _config = AuthConfig(
        api_key=key,
        api_key_hash=_hash_key(key) if key else None,
        require_auth_always=require_auth_always,
        rate_limit_enabled=rate_limit_enabled,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window=rate_limit_window,
        log_requests=log_requests,
    )

    if key:
        logger.info("API key authentication configured")
    else:
        logger.info("No API key configured - auth disabled")


def _hash_key(key: str) -> str:
    """Hash an API key for secure comparison.

    Args:
        key: Plain text API key.

    Returns:
        SHA-256 hash of the key.
    """
    return hashlib.sha256(key.encode()).hexdigest()


def _is_local_request(request: Request) -> bool:
    """Check if request is from a local origin.

    Args:
        request: FastAPI request object.

    Returns:
        True if request is from localhost.
    """
    client_host = request.client.host if request.client else None

    if not client_host:
        return False

    return client_host in _config.local_origins


def _check_rate_limit(client_ip: str) -> tuple[bool, int]:
    """Check if client has exceeded rate limit.

    Args:
        client_ip: Client IP address.

    Returns:
        Tuple of (allowed, remaining_requests).
    """
    if not _config.rate_limit_enabled:
        return True, _config.rate_limit_requests

    now = time.time()
    window_start = now - _config.rate_limit_window

    # Clean old entries and count recent requests
    recent = [(ts, count) for ts, count in _rate_limit_tracker[client_ip] if ts > window_start]
    _rate_limit_tracker[client_ip] = recent

    total_requests = sum(count for _, count in recent)
    remaining = max(0, _config.rate_limit_requests - total_requests)

    if total_requests >= _config.rate_limit_requests:
        return False, 0

    # Record this request
    _rate_limit_tracker[client_ip].append((now, 1))

    return True, remaining - 1


def _log_request(request: Request, authenticated: bool, client_ip: str) -> None:
    """Log an API request.

    Args:
        request: FastAPI request object.
        authenticated: Whether request was authenticated.
        client_ip: Client IP address.
    """
    if not _config.log_requests:
        return

    method = request.method
    path = request.url.path
    auth_status = "authenticated" if authenticated else "unauthenticated"

    logger.info(f"{method} {path} - {client_ip} - {auth_status}")


async def verify_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
) -> dict:
    """Verify API key and return auth context.

    This dependency can be used to protect endpoints.

    Args:
        request: FastAPI request object.
        api_key: API key from header.

    Returns:
        Auth context dictionary with client info.

    Raises:
        HTTPException: If authentication fails.
    """
    client_ip = request.client.host if request.client else "unknown"
    is_local = _is_local_request(request)

    # Check rate limit
    allowed, remaining = _check_rate_limit(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(_config.rate_limit_window)},
        )

    # Check if auth is required
    auth_required = _config.api_key is not None and (
        _config.require_auth_always or not is_local
    )

    authenticated = False

    if auth_required:
        if not api_key:
            _log_request(request, False, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required. Provide X-API-Key header.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Verify API key
        if _hash_key(api_key) != _config.api_key_hash:
            _log_request(request, False, client_ip)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key.",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        authenticated = True

    _log_request(request, authenticated or is_local, client_ip)

    return {
        "client_ip": client_ip,
        "is_local": is_local,
        "authenticated": authenticated,
        "rate_limit_remaining": remaining,
    }


async def optional_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
) -> dict:
    """Optional API key verification - doesn't raise on missing key.

    Use this for endpoints that should work without auth but provide
    enhanced features when authenticated.

    Args:
        request: FastAPI request object.
        api_key: API key from header.

    Returns:
        Auth context dictionary.
    """
    client_ip = request.client.host if request.client else "unknown"
    is_local = _is_local_request(request)

    # Check rate limit
    allowed, remaining = _check_rate_limit(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": str(_config.rate_limit_window)},
        )

    authenticated = False

    if api_key and _config.api_key_hash:
        authenticated = _hash_key(api_key) == _config.api_key_hash

    _log_request(request, authenticated or is_local, client_ip)

    return {
        "client_ip": client_ip,
        "is_local": is_local,
        "authenticated": authenticated,
        "rate_limit_remaining": remaining,
    }


def get_auth_config() -> AuthConfig:
    """Get current authentication configuration.

    Returns:
        Current AuthConfig.
    """
    return _config


def reset_rate_limits() -> None:
    """Reset all rate limit counters."""
    global _rate_limit_tracker
    _rate_limit_tracker = defaultdict(list)


def generate_api_key() -> str:
    """Generate a new random API key.

    Returns:
        Random API key string.
    """
    import secrets
    return f"rctx_{secrets.token_urlsafe(32)}"
