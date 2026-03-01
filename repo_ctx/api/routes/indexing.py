"""Indexing endpoints for the repo-ctx API.

This module provides endpoints for repository indexing operations.
"""

from typing import Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.indexing import IndexingService


class IndexRequest(BaseModel):
    """Request body for indexing a repository."""
    repository: str = Field(..., description="Repository path (e.g., 'owner/repo')")
    provider: str = Field(default="auto", description="Provider type (github, gitlab, local, auto)")
    version: Optional[str] = Field(default=None, description="Version/branch/tag to index")
    refresh: bool = Field(default=False, description="Force re-index if already indexed")


class IndexResponse(BaseModel):
    """Response from indexing operation."""
    status: str
    repository: str
    version: str
    document_count: int
    updated: bool


class StatusResponse(BaseModel):
    """Response from status check."""
    indexed: bool
    repository: str
    group_name: Optional[str] = None
    project_name: Optional[str] = None
    default_version: Optional[str] = None
    last_indexed: Optional[str] = None


def create_indexing_router(context: ServiceContext) -> APIRouter:
    """Create an indexing router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["indexing"])
    service = IndexingService(context)

    @router.post("/index", response_model=IndexResponse)
    async def index_repository(request: IndexRequest) -> IndexResponse:
        """Index a repository.

        Args:
            request: Index request with repository and provider info.

        Returns:
            IndexResponse with indexing result.
        """
        try:
            result = await service.index_repository(
                repository=request.repository,
                provider_type=request.provider,
                version=request.version,
                refresh=request.refresh,
            )
            return IndexResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/index/status", response_model=StatusResponse)
    async def get_indexing_status(
        repository: str = Query(..., description="Repository ID")
    ) -> StatusResponse:
        """Get indexing status for a repository.

        Args:
            repository: Repository identifier.

        Returns:
            StatusResponse with indexing status.
        """
        result = await service.get_indexing_status(repository)
        return StatusResponse(**result)

    return router
