"""Repository management endpoints for the repo-ctx API.

This module provides endpoints for listing, retrieving, and deleting repositories.
"""

from typing import Any, Optional

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.repository import RepositoryService


class RepositoryInfo(BaseModel):
    """Repository information."""
    id: str = Field(..., description="Repository ID (e.g., /owner/repo)")
    name: str = Field(..., description="Project name")
    group: str = Field(..., description="Group/owner name")
    description: Optional[str] = Field(None, description="Repository description")
    provider: str = Field(default="github", description="Provider (github, gitlab, local)")
    default_version: Optional[str] = Field(None, description="Default version/branch")
    last_indexed: Optional[str] = Field(None, description="Last indexed timestamp")


class RepositoryListResponse(BaseModel):
    """Response with list of repositories."""
    count: int
    repositories: list[RepositoryInfo]


class RepositoryDeleteResponse(BaseModel):
    """Response from delete operation."""
    deleted: bool
    repository: str
    message: str


def create_repositories_router(context: ServiceContext) -> APIRouter:
    """Create a repositories router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["repositories"])
    service = RepositoryService(context)

    @router.get("/repositories", response_model=RepositoryListResponse)
    async def list_repositories(
        provider: Optional[str] = Query(None, description="Filter by provider (github, gitlab, local)"),
        limit: int = Query(100, ge=1, le=1000, description="Maximum repositories to return"),
        offset: int = Query(0, ge=0, description="Offset for pagination"),
    ) -> RepositoryListResponse:
        """List all indexed repositories.

        Args:
            provider: Optional provider filter.
            limit: Maximum results.
            offset: Pagination offset.

        Returns:
            RepositoryListResponse with list of repositories.
        """
        try:
            libraries = await service.list_repositories()

            # Filter by provider if specified
            if provider:
                libraries = [lib for lib in libraries if lib.provider == provider]

            # Apply pagination
            total = len(libraries)
            libraries = libraries[offset:offset + limit]

            return RepositoryListResponse(
                count=total,
                repositories=[
                    RepositoryInfo(
                        id=f"/{lib.group_name}/{lib.project_name}",
                        name=lib.project_name,
                        group=lib.group_name,
                        description=lib.description,
                        provider=lib.provider or "github",
                        default_version=lib.default_version,
                        last_indexed=str(lib.last_indexed) if lib.last_indexed else None,
                    )
                    for lib in libraries
                ],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/repositories/{group}/{project}", response_model=RepositoryInfo)
    async def get_repository(
        group: str,
        project: str,
    ) -> RepositoryInfo:
        """Get details for a specific repository.

        Args:
            group: Group/owner name.
            project: Project name.

        Returns:
            RepositoryInfo with repository details.

        Raises:
            HTTPException: If repository not found.
        """
        try:
            repository_id = f"/{group}/{project}"
            lib = await service.get_repository(repository_id)

            if not lib:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            return RepositoryInfo(
                id=f"/{lib.group_name}/{lib.project_name}",
                name=lib.project_name,
                group=lib.group_name,
                description=lib.description,
                provider=lib.provider or "github",
                default_version=lib.default_version,
                last_indexed=str(lib.last_indexed) if lib.last_indexed else None,
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/repositories/{group}/{project}", response_model=RepositoryDeleteResponse)
    async def delete_repository(
        group: str,
        project: str,
    ) -> RepositoryDeleteResponse:
        """Delete an indexed repository.

        Args:
            group: Group/owner name.
            project: Project name.

        Returns:
            RepositoryDeleteResponse with deletion result.
        """
        try:
            repository_id = f"/{group}/{project}"
            deleted = await service.delete_repository(repository_id)

            if not deleted:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            return RepositoryDeleteResponse(
                deleted=True,
                repository=repository_id,
                message=f"Successfully deleted repository: {repository_id}",
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/repositories/{group}/{project}/stats")
    async def get_repository_stats(
        group: str,
        project: str,
    ) -> dict[str, Any]:
        """Get statistics for a repository.

        Args:
            group: Group/owner name.
            project: Project name.

        Returns:
            Dictionary with repository statistics.
        """
        try:
            repository_id = f"/{group}/{project}"
            stats = await service.get_repository_stats(repository_id)

            if stats is None:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            return stats
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
