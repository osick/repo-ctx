"""Tests for MCP service layer integration.

This module tests the integration between MCP tools and the service layer,
ensuring MCP tools can use the same services as the API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repo_ctx.config import Config
from repo_ctx.services.base import ServiceContext
from repo_ctx.services import (
    create_service_context,
    RepositoryService,
    IndexingService,
    SearchService,
    AnalysisService,
)


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_content_storage():
    """Create a mock content storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.init_db = AsyncMock()
    storage.search = AsyncMock(return_value=[])
    storage.fuzzy_search = AsyncMock(return_value=[])
    storage.get_library = AsyncMock(return_value=None)
    storage.get_all_libraries = AsyncMock(return_value=[])
    storage.get_symbols = AsyncMock(return_value=[])
    storage.save_symbols = AsyncMock()
    return storage


@pytest.fixture
def mock_vector_storage():
    """Create a mock vector storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    return storage


@pytest.fixture
def mock_graph_storage():
    """Create a mock graph storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.create_nodes = AsyncMock()
    storage.create_relationships = AsyncMock()
    return storage


@pytest.fixture
def service_context(mock_content_storage, mock_vector_storage, mock_graph_storage):
    """Create a service context with all mock storages."""
    return ServiceContext(
        content_storage=mock_content_storage,
        vector_storage=mock_vector_storage,
        graph_storage=mock_graph_storage,
    )


# =============================================================================
# MCPContext Tests - Service Integration
# =============================================================================


class TestMCPContext:
    """Tests for MCP context that wraps services."""

    def test_mcp_context_creation(self, service_context):
        """Test creating an MCP context from service context."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        assert mcp is not None
        assert mcp.services == service_context

    def test_mcp_context_has_repository_service(self, service_context):
        """Test MCP context provides repository service."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        assert hasattr(mcp, 'repository')
        assert isinstance(mcp.repository, RepositoryService)

    def test_mcp_context_has_indexing_service(self, service_context):
        """Test MCP context provides indexing service."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        assert hasattr(mcp, 'indexing')
        assert isinstance(mcp.indexing, IndexingService)

    def test_mcp_context_has_search_service(self, service_context):
        """Test MCP context provides search service."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        assert hasattr(mcp, 'search')
        assert isinstance(mcp.search, SearchService)

    def test_mcp_context_has_analysis_service(self, service_context):
        """Test MCP context provides analysis service."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        assert hasattr(mcp, 'analysis')
        assert isinstance(mcp.analysis, AnalysisService)


# =============================================================================
# MCP Response Formatting Tests
# =============================================================================


class TestMCPResponseFormatting:
    """Tests for MCP response formatting."""

    def test_format_search_results(self):
        """Test formatting search results for MCP."""
        from repo_ctx.mcp.formatters import format_search_results

        results = [
            MagicMock(
                library_id="/owner/repo1",
                name="repo1",
                group="owner",
                description="Test repo 1",
                match_type="fuzzy",
                matched_field="name",
                score=0.95,
            ),
            MagicMock(
                library_id="/owner/repo2",
                name="repo2",
                group="owner",
                description="Test repo 2",
                match_type="exact",
                matched_field="name",
                score=1.0,
            ),
        ]

        formatted = format_search_results(results, query="repo")

        assert "repo1" in formatted
        assert "repo2" in formatted
        assert "owner" in formatted

    def test_format_repository_list(self):
        """Test formatting repository list for MCP."""
        from repo_ctx.mcp.formatters import format_repository_list

        from repo_ctx.models import Library

        repositories = [
            Library(
                group_name="owner",
                project_name="repo1",
                description="Test repo 1",
                default_version="main",
            ),
            Library(
                group_name="owner",
                project_name="repo2",
                description="Test repo 2",
                default_version="main",
            ),
        ]

        formatted = format_repository_list(repositories)

        assert "repo1" in formatted
        assert "repo2" in formatted

    def test_format_analysis_results(self):
        """Test formatting analysis results for MCP."""
        from repo_ctx.mcp.formatters import format_analysis_results

        analysis = {
            "file_path": "test.py",
            "language": "python",
            "symbols": [
                {"name": "hello", "symbol_type": "function", "line_start": 1},
            ],
            "dependencies": [],
        }

        formatted = format_analysis_results(analysis, output_format="text")

        assert "hello" in formatted
        assert "function" in formatted

    def test_format_analysis_results_json(self):
        """Test formatting analysis results as JSON."""
        from repo_ctx.mcp.formatters import format_analysis_results
        import json

        analysis = {
            "file_path": "test.py",
            "language": "python",
            "symbols": [
                {"name": "hello", "symbol_type": "function", "line_start": 1},
            ],
            "dependencies": [],
        }

        formatted = format_analysis_results(analysis, output_format="json")

        # Should be valid JSON
        data = json.loads(formatted)
        assert data["file_path"] == "test.py"
        assert len(data["symbols"]) == 1


# =============================================================================
# MCP Server Integration Tests
# =============================================================================


class TestMCPServerIntegration:
    """Integration tests for MCP server with services."""

    @pytest.fixture
    def mcp_context(self, service_context):
        """Create MCP context."""
        from repo_ctx.mcp.context import MCPContext
        return MCPContext(service_context)

    @pytest.mark.asyncio
    async def test_mcp_context_initialization(self, service_context, mock_content_storage):
        """Test MCP context initializes storage."""
        from repo_ctx.mcp.context import MCPContext

        mcp = MCPContext(service_context)
        await mcp.init()

        mock_content_storage.init_db.assert_called_once()

    @pytest.mark.asyncio
    async def test_mcp_context_health_check(self, mcp_context):
        """Test MCP context health check."""
        health = await mcp_context.health_check()

        assert health is not None
        assert "content_storage" in health
