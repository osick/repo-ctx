"""Repository service for managing indexed repositories.

This module provides the RepositoryService which handles
all repository-related operations including listing, getting,
and deleting repositories.
"""

from typing import Any, Optional

from repo_ctx.models import Library
from repo_ctx.services.base import BaseService, ServiceContext


class RepositoryService(BaseService):
    """Service for repository management operations.

    Handles CRUD operations for repositories across all storage backends.
    """

    def __init__(self, context: ServiceContext) -> None:
        """Initialize the repository service.

        Args:
            context: ServiceContext with storage backends.
        """
        super().__init__(context)

    async def list_repositories(self) -> list[Library]:
        """List all indexed repositories.

        Returns:
            List of all libraries/repositories.
        """
        return await self.content_storage.get_all_libraries()

    async def get_repository(self, repository_id: str) -> Optional[Library]:
        """Get a repository by its ID.

        Args:
            repository_id: Repository identifier (e.g., "/owner/repo").

        Returns:
            Library if found, None otherwise.
        """
        return await self.content_storage.get_library(repository_id)

    async def repository_exists(self, repository_id: str) -> bool:
        """Check if a repository exists.

        Args:
            repository_id: Repository identifier.

        Returns:
            True if repository exists, False otherwise.
        """
        repo = await self.get_repository(repository_id)
        return repo is not None

    async def delete_repository(self, repository_id: str) -> bool:
        """Delete a repository and all its data from all storage backends.

        Args:
            repository_id: Repository identifier.

        Returns:
            True if deleted, False if not found.
        """
        # Delete from content storage
        deleted = await self.content_storage.delete_library(repository_id)

        if deleted:
            # Clean up vector storage if available
            if self.vector_storage is not None:
                try:
                    await self.vector_storage.delete_by_library(
                        "documents", repository_id
                    )
                except Exception:
                    pass  # Best effort cleanup

            # Clean up graph storage if available
            if self.graph_storage is not None:
                try:
                    await self.graph_storage.delete_by_library(repository_id)
                except Exception:
                    pass  # Best effort cleanup

        return deleted

    async def get_repository_stats(
        self, repository_id: str
    ) -> Optional[dict[str, Any]]:
        """Get statistics for a repository.

        Args:
            repository_id: Repository identifier.

        Returns:
            Dictionary with repository statistics, or None if not found.
        """
        repo = await self.get_repository(repository_id)
        if repo is None:
            return None

        # Get document count
        documents = await self.content_storage.get_documents(
            version_id=repo.id,  # Use repo.id as version_id for now
            page=1,
            page_size=1000,
        )

        return {
            "id": repo.id,
            "group_name": repo.group_name,
            "project_name": repo.project_name,
            "description": repo.description,
            "document_count": len(documents),
        }
