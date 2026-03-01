"""Info endpoint.

This module provides the info endpoint with API metadata
and capabilities.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from repo_ctx.api.version import VERSION


class Capabilities(BaseModel):
    """API capabilities."""
    indexing: bool = True
    search: bool = True
    analysis: bool = True
    genai: bool = False  # Disabled by default


class InfoResponse(BaseModel):
    """Info response."""
    name: str
    version: str
    description: str
    capabilities: Capabilities


router = APIRouter(tags=["info"])


@router.get("/info", response_model=InfoResponse)
async def get_info() -> InfoResponse:
    """Get API information and capabilities.

    Returns:
        InfoResponse with API metadata.
    """
    return InfoResponse(
        name="repo-ctx",
        version=VERSION,
        description="Git repository documentation indexer and search API",
        capabilities=Capabilities(),
    )
