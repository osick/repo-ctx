"""MCP Context wrapping service layer.

This module provides MCPContext which wraps the service layer
and provides convenient access to all services for MCP tool handlers.
"""

from typing import Any

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.repository import RepositoryService
from repo_ctx.services.indexing import IndexingService
from repo_ctx.services.search import SearchService
from repo_ctx.services.analysis import AnalysisService


class MCPContext:
    """Context for MCP operations wrapping the service layer.

    Provides access to all services through a single interface
    for use by MCP tool handlers.
    """

    def __init__(self, services: ServiceContext) -> None:
        """Initialize MCP context with service context.

        Args:
            services: ServiceContext with storage backends.
        """
        self._services = services

        # Initialize service instances
        self._repository = RepositoryService(services)
        self._indexing = IndexingService(services)
        self._search = SearchService(services)
        self._analysis = AnalysisService(services)

    @property
    def services(self) -> ServiceContext:
        """Get the underlying service context."""
        return self._services

    @property
    def repository(self) -> RepositoryService:
        """Get repository service for managing indexed repositories."""
        return self._repository

    @property
    def indexing(self) -> IndexingService:
        """Get indexing service for repository indexing operations."""
        return self._indexing

    @property
    def search(self) -> SearchService:
        """Get search service for search operations."""
        return self._search

    @property
    def analysis(self) -> AnalysisService:
        """Get analysis service for code analysis operations."""
        return self._analysis

    async def init(self) -> None:
        """Initialize the MCP context (database setup, etc.)."""
        await self._services.content_storage.init_db()

    async def health_check(self) -> dict[str, Any]:
        """Check health of all services.

        Returns:
            Dictionary with health status of each component.
        """
        return await self._services.health_check()

    async def close(self) -> None:
        """Clean up resources."""
        # Close any connections if needed
        pass
