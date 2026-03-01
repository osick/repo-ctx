"""Base service classes for the service layer.

This module provides the foundation for all services including
ServiceContext for dependency injection and BaseService as
the parent class for all services.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from repo_ctx.storage.protocols import (
    ContentStorageProtocol,
    VectorStorageProtocol,
    GraphStorageProtocol,
)


@dataclass
class ServiceContext:
    """Context for service dependency injection.

    Holds references to all storage backends and provides
    health checking capabilities.

    Attributes:
        content_storage: SQLite content storage (required).
        vector_storage: Qdrant vector storage (optional).
        graph_storage: Neo4j graph storage (optional).
    """

    content_storage: ContentStorageProtocol
    vector_storage: Optional[VectorStorageProtocol] = None
    graph_storage: Optional[GraphStorageProtocol] = None

    async def health_check(self) -> dict[str, Any]:
        """Check health of all configured storage backends.

        Returns:
            Dictionary with health status of each storage and overall status.
        """
        health: dict[str, Any] = {}
        all_healthy = True

        # Check content storage (required)
        try:
            content_healthy = await self.content_storage.health_check()
            health["content_storage"] = {
                "status": "healthy" if content_healthy else "unhealthy",
            }
            if not content_healthy:
                all_healthy = False
        except Exception as e:
            health["content_storage"] = {"status": "unhealthy", "error": str(e)}
            all_healthy = False

        # Check vector storage (optional)
        if self.vector_storage is not None:
            try:
                vector_healthy = await self.vector_storage.health_check()
                health["vector_storage"] = {
                    "status": "healthy" if vector_healthy else "unhealthy",
                }
                if not vector_healthy:
                    all_healthy = False
            except Exception as e:
                health["vector_storage"] = {"status": "unhealthy", "error": str(e)}
                all_healthy = False
        else:
            health["vector_storage"] = {"status": "not_configured"}

        # Check graph storage (optional)
        if self.graph_storage is not None:
            try:
                graph_healthy = await self.graph_storage.health_check()
                health["graph_storage"] = {
                    "status": "healthy" if graph_healthy else "unhealthy",
                }
                if not graph_healthy:
                    all_healthy = False
            except Exception as e:
                health["graph_storage"] = {"status": "unhealthy", "error": str(e)}
                all_healthy = False
        else:
            health["graph_storage"] = {"status": "not_configured"}

        # Determine overall status
        statuses = [v["status"] for v in health.values() if v["status"] != "not_configured"]
        if all(s == "healthy" for s in statuses):
            health["overall"] = "healthy"
        elif any(s == "healthy" for s in statuses):
            health["overall"] = "degraded"
        else:
            health["overall"] = "unhealthy"

        return health


class BaseService:
    """Base class for all services.

    Provides access to storage backends through the service context.

    Attributes:
        context: ServiceContext with storage references.
    """

    def __init__(self, context: ServiceContext) -> None:
        """Initialize the service.

        Args:
            context: ServiceContext with storage backends.
        """
        self._context = context

    @property
    def context(self) -> ServiceContext:
        """Get the service context."""
        return self._context

    @property
    def content_storage(self) -> ContentStorageProtocol:
        """Get the content storage backend."""
        return self._context.content_storage

    @property
    def vector_storage(self) -> Optional[VectorStorageProtocol]:
        """Get the vector storage backend (may be None)."""
        return self._context.vector_storage

    @property
    def graph_storage(self) -> Optional[GraphStorageProtocol]:
        """Get the graph storage backend (may be None)."""
        return self._context.graph_storage
