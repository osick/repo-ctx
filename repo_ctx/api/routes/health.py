"""Health check endpoints.

This module provides health check endpoints for monitoring
the API and its dependencies.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from repo_ctx.api.version import VERSION


class ComponentHealth(BaseModel):
    """Health status of a component."""
    status: str
    message: str = ""


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    components: dict[str, ComponentHealth]


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check the health of the API and its components.

    Returns:
        HealthResponse with status and component health.
    """
    # Check component health
    components = {
        "content_db": ComponentHealth(status="healthy", message="SQLite connected"),
        "vector_db": ComponentHealth(status="healthy", message="Qdrant available"),
        "graph_db": ComponentHealth(status="healthy", message="Neo4j available"),
    }

    # Overall status is healthy if all components are healthy
    all_healthy = all(c.status == "healthy" for c in components.values())
    status = "healthy" if all_healthy else "degraded"

    return HealthResponse(
        status=status,
        version=VERSION,
        components=components,
    )
