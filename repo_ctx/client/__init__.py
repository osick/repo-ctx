"""Unified client for repo-ctx operations.

This module provides RepoCtxClient, a unified interface for all repo-ctx
operations that can be used by CLI, MCP, and other integrations.

The client supports two modes:
- Direct mode (default): Uses service layer directly for best performance
- HTTP mode: Uses REST API for remote access

Example usage:
    from repo_ctx.client import RepoCtxClient

    # Direct mode (for CLI/MCP)
    async with RepoCtxClient() as client:
        libraries = await client.list_libraries()

    # HTTP mode (for remote access)
    client = RepoCtxClient(api_url="http://localhost:8000")
    await client.connect()
"""

from repo_ctx.client.client import (
    RepoCtxClient,
    ClientMode,
)
from repo_ctx.client.models import (
    Library,
    Document,
    Symbol,
    SearchResult,
    IndexResult,
    AnalysisResult,
)

__all__ = [
    "RepoCtxClient",
    "ClientMode",
    "Library",
    "Document",
    "Symbol",
    "SearchResult",
    "IndexResult",
    "AnalysisResult",
]
