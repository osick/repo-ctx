"""Authentication endpoints for the repo-ctx API.

This module provides endpoints for authentication management.
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from repo_ctx.api.auth import (
    verify_api_key,
    optional_api_key,
    get_auth_config,
    generate_api_key,
)


class AuthStatusResponse(BaseModel):
    """Authentication status response."""
    authenticated: bool = Field(..., description="Whether request is authenticated")
    is_local: bool = Field(..., description="Whether request is from localhost")
    auth_required: bool = Field(..., description="Whether auth is required for this server")
    client_ip: str = Field(..., description="Client IP address")
    rate_limit_remaining: int = Field(..., description="Remaining requests in current window")


class AuthConfigResponse(BaseModel):
    """Authentication configuration response (safe to expose)."""
    auth_enabled: bool = Field(..., description="Whether API key auth is configured")
    rate_limit_enabled: bool = Field(..., description="Whether rate limiting is enabled")
    rate_limit_requests: int = Field(..., description="Max requests per window")
    rate_limit_window: int = Field(..., description="Rate limit window in seconds")
    require_auth_always: bool = Field(..., description="Whether auth is required for local requests")


class GenerateKeyResponse(BaseModel):
    """Response with generated API key."""
    api_key: str = Field(..., description="Generated API key")
    message: str = Field(..., description="Instructions for using the key")


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/status", response_model=AuthStatusResponse)
async def get_auth_status(
    auth_context: dict = Depends(optional_api_key),
) -> AuthStatusResponse:
    """Get authentication status for current request.

    This endpoint allows clients to check their authentication status
    and remaining rate limit.

    Returns:
        AuthStatusResponse with current auth status.
    """
    config = get_auth_config()

    return AuthStatusResponse(
        authenticated=auth_context["authenticated"],
        is_local=auth_context["is_local"],
        auth_required=config.api_key is not None,
        client_ip=auth_context["client_ip"],
        rate_limit_remaining=auth_context["rate_limit_remaining"],
    )


@router.get("/config", response_model=AuthConfigResponse)
async def get_auth_configuration() -> AuthConfigResponse:
    """Get authentication configuration (public info only).

    Returns:
        AuthConfigResponse with configuration details.
    """
    config = get_auth_config()

    return AuthConfigResponse(
        auth_enabled=config.api_key is not None,
        rate_limit_enabled=config.rate_limit_enabled,
        rate_limit_requests=config.rate_limit_requests,
        rate_limit_window=config.rate_limit_window,
        require_auth_always=config.require_auth_always,
    )


@router.post("/generate-key", response_model=GenerateKeyResponse)
async def generate_new_api_key(
    auth_context: dict = Depends(verify_api_key),
) -> GenerateKeyResponse:
    """Generate a new API key.

    This endpoint requires authentication (existing API key or local access).
    The generated key can be used to configure the server.

    Returns:
        GenerateKeyResponse with new API key.
    """
    new_key = generate_api_key()

    return GenerateKeyResponse(
        api_key=new_key,
        message="Store this key securely. Set REPO_CTX_API_KEY environment variable to enable it.",
    )


@router.get("/verify")
async def verify_authentication(
    auth_context: dict = Depends(verify_api_key),
) -> dict:
    """Verify that authentication is working.

    This endpoint requires valid authentication.

    Returns:
        Success message if authenticated.
    """
    return {
        "status": "authenticated",
        "message": "API key is valid",
        "client_ip": auth_context["client_ip"],
        "is_local": auth_context["is_local"],
    }
