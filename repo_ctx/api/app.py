"""FastAPI application definition.

This module creates and configures the FastAPI application instance.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repo_ctx.api.version import VERSION
from repo_ctx.api.routes import health, info
from repo_ctx.api.routes.indexing import create_indexing_router
from repo_ctx.api.routes.search import create_search_router
from repo_ctx.api.routes.analysis import create_analysis_router
from repo_ctx.api.routes.repositories import create_repositories_router
from repo_ctx.api.routes.docs import create_docs_router
from repo_ctx.api.routes.tasks import create_tasks_router
from repo_ctx.api.routes.progress import create_progress_router
from repo_ctx.api.routes import auth as auth_routes
from repo_ctx.api.auth import configure_auth, get_auth_config
from repo_ctx.api.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitHeadersMiddleware,
)
from repo_ctx.services import create_service_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("repo_ctx.api")

# Create service context for dependency injection
service_context = create_service_context()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize database and auth
    await service_context.content_storage.init_db()

    # Configure authentication from environment
    configure_auth(
        api_key=os.environ.get("REPO_CTX_API_KEY"),
        require_auth_always=os.environ.get("REPO_CTX_REQUIRE_AUTH", "").lower() == "true",
        rate_limit_enabled=os.environ.get("REPO_CTX_RATE_LIMIT", "true").lower() != "false",
        rate_limit_requests=int(os.environ.get("REPO_CTX_RATE_LIMIT_REQUESTS", "100")),
        rate_limit_window=int(os.environ.get("REPO_CTX_RATE_LIMIT_WINDOW", "60")),
        log_requests=os.environ.get("REPO_CTX_LOG_REQUESTS", "true").lower() != "false",
    )

    auth_config = get_auth_config()
    if auth_config.api_key:
        logger.info("API key authentication enabled")
    else:
        logger.info("Running without API key - local access only")

    yield
    # Shutdown: cleanup if needed
    logger.info("Shutting down repo-ctx API")


# Create FastAPI application
app = FastAPI(
    title="repo-ctx API",
    description="Git repository documentation indexer and search API",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware (order matters - last added is first executed)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitHeadersMiddleware, limit=100, window=60)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include static routers
app.include_router(health.router)
app.include_router(info.router)

# Include dynamic routers (require service context)
indexing_router = create_indexing_router(service_context)
search_router = create_search_router(service_context)
analysis_router = create_analysis_router(service_context)
repositories_router = create_repositories_router(service_context)
docs_router = create_docs_router(service_context)
tasks_router = create_tasks_router(service_context)
progress_router = create_progress_router()

# Versioned routes
app.include_router(health.router, prefix="/v1", tags=["v1"])
app.include_router(info.router, prefix="/v1", tags=["v1"])
app.include_router(indexing_router, prefix="/v1", tags=["v1", "indexing"])
app.include_router(search_router, prefix="/v1", tags=["v1", "search"])
app.include_router(analysis_router, prefix="/v1", tags=["v1", "analysis"])
app.include_router(repositories_router, prefix="/v1", tags=["v1", "repositories"])
app.include_router(docs_router, prefix="/v1", tags=["v1", "documentation"])
app.include_router(tasks_router, prefix="/v1", tags=["v1", "tasks"])
app.include_router(progress_router, prefix="/v1", tags=["v1", "progress"])
app.include_router(auth_routes.router, prefix="/v1", tags=["v1", "auth"])


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with welcome message."""
    return {
        "message": "Welcome to repo-ctx API",
        "docs_url": "/docs",
        "version": VERSION,
    }
