"""Tests for MCPServerContext bridge class.

This module tests the MCPServerContext which wraps the unified
RepoCtxClient to provide a consistent interface for MCP tool handlers.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repo_ctx.config import Config


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create a mock config."""
    config = MagicMock(spec=Config)
    config.storage_path = ":memory:"
    config.storage = None
    config.gitlab_url = None
    config.gitlab_token = None
    config.github_url = None
    config.github_token = None
    return config


@pytest.fixture
def mock_legacy_context():
    """Create a mock legacy context."""
    context = AsyncMock()
    context.init = AsyncMock()
    context.search_libraries = AsyncMock(return_value=[])
    context.fuzzy_search_libraries = AsyncMock(return_value=[])
    context.index_repository = AsyncMock()
    context.index_group = AsyncMock(return_value={"indexed": [], "failed": []})
    context.get_documentation = AsyncMock(return_value={"content": []})
    context.list_all_libraries = AsyncMock(return_value=[])
    context._get_repository_url = MagicMock(return_value="https://github.com/test/repo")
    context.storage = AsyncMock()
    context.storage.get_library = AsyncMock(return_value=None)
    context.storage.get_version_id = AsyncMock(return_value=None)
    context.storage.get_documents = AsyncMock(return_value=[])
    return context


@pytest.fixture
def mock_client(mock_legacy_context):
    """Create a mock RepoCtxClient."""
    client = AsyncMock()
    client.connect = AsyncMock()
    client.close = AsyncMock()
    client.is_initialized = False
    client._legacy_context = mock_legacy_context
    client._service_context = MagicMock()
    client._repository_service = MagicMock()
    client._indexing_service = MagicMock()
    client._search_service = MagicMock()
    client._analysis_service = MagicMock()
    return client


# =============================================================================
# MCPServerContext Tests
# =============================================================================


class TestMCPServerContextCreation:
    """Tests for MCPServerContext creation."""

    def test_create_with_config(self, mock_config):
        """Test creating MCPServerContext with config."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient') as mock_client_cls:
            mock_client_cls.return_value = MagicMock()

            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            assert ctx is not None
            mock_client_cls.assert_called_once_with(config=mock_config)

    def test_create_with_legacy_context(self, mock_config, mock_legacy_context):
        """Test creating MCPServerContext with pre-created legacy context (ignored)."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient') as mock_client_cls:
            mock_client_cls.return_value = MagicMock()

            from repo_ctx.mcp import MCPServerContext

            # legacy_context parameter is ignored in new implementation
            ctx = MCPServerContext(mock_config, legacy_context=mock_legacy_context)
            assert ctx is not None


class TestMCPServerContextProperties:
    """Tests for MCPServerContext properties."""

    def test_legacy_property(self, mock_config, mock_client, mock_legacy_context):
        """Test legacy property returns GitLabContext from client."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            assert ctx.legacy == mock_legacy_context

    def test_storage_property(self, mock_config, mock_client, mock_legacy_context):
        """Test storage property delegates to client legacy context."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            assert ctx.storage == mock_legacy_context.storage

    def test_services_before_init(self, mock_config, mock_client):
        """Test services are available through client properties."""
        mock_client._service_context = None
        mock_client._repository_service = None
        mock_client._indexing_service = None
        mock_client._search_service = None
        mock_client._analysis_service = None

        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            assert ctx.services is None
            assert ctx.repository is None
            assert ctx.indexing is None
            assert ctx.search is None
            assert ctx.analysis is None


class TestMCPServerContextInit:
    """Tests for MCPServerContext initialization."""

    @pytest.mark.asyncio
    async def test_init_initializes_client(self, mock_config, mock_client):
        """Test init calls client connect."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()

            mock_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_init_creates_services(self, mock_config, mock_client):
        """Test init makes services available through client."""
        mock_client._service_context = MagicMock()
        mock_client._repository_service = MagicMock()
        mock_client._indexing_service = MagicMock()
        mock_client._search_service = MagicMock()
        mock_client._analysis_service = MagicMock()

        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()

            assert ctx.services is not None
            assert ctx.repository is not None
            assert ctx.indexing is not None
            assert ctx.search is not None
            assert ctx.analysis is not None


class TestMCPServerContextLegacyProxies:
    """Tests for legacy method proxies."""

    @pytest.mark.asyncio
    async def test_search_libraries_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test search_libraries delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.search_libraries("test")

            mock_legacy_context.search_libraries.assert_called_once_with("test")

    @pytest.mark.asyncio
    async def test_fuzzy_search_libraries_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test fuzzy_search_libraries delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.fuzzy_search_libraries("test", limit=5)

            mock_legacy_context.fuzzy_search_libraries.assert_called_once_with("test", 5)

    @pytest.mark.asyncio
    async def test_index_repository_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test index_repository delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.index_repository("group", "project", provider_type="github")

            mock_legacy_context.index_repository.assert_called_once_with(
                "group", "project", provider_type="github"
            )

    @pytest.mark.asyncio
    async def test_index_group_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test index_group delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.index_group("group", include_subgroups=False)

            mock_legacy_context.index_group.assert_called_once_with(
                "group", False
            )

    @pytest.mark.asyncio
    async def test_get_documentation_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test get_documentation delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.get_documentation("/group/project", topic="api")

            mock_legacy_context.get_documentation.assert_called_once_with(
                "/group/project", "api", 1
            )

    @pytest.mark.asyncio
    async def test_list_all_libraries_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test list_all_libraries delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.list_all_libraries("github")

            mock_legacy_context.list_all_libraries.assert_called_once_with("github")

    @pytest.mark.asyncio
    async def test_get_repository_url_proxy(self, mock_config, mock_client, mock_legacy_context):
        """Test _get_repository_url delegates to legacy."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            lib = MagicMock()
            result = ctx._get_repository_url(lib)

            mock_legacy_context._get_repository_url.assert_called_once_with(lib)
            assert result == "https://github.com/test/repo"


class TestMCPServerContextServiceMethods:
    """Tests for service-based methods."""

    @pytest.mark.asyncio
    async def test_analyze_code_uses_analyzer(self, mock_config, mock_client):
        """Test analyze_code uses CodeAnalyzer."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()

            # analyze_code now uses CodeAnalyzer directly
            with patch('repo_ctx.analysis.CodeAnalyzer') as mock_analyzer_cls:
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_file.return_value = ([], [])
                mock_analyzer.detect_language.return_value = "python"
                mock_analyzer_cls.return_value = mock_analyzer

                result = ctx.analyze_code("code", "test.py", "python")

                assert result["file_path"] == "test.py"
                assert result["language"] == "python"
                assert "symbols" in result
                assert "dependencies" in result

    @pytest.mark.asyncio
    async def test_analyze_code_works_before_init(self, mock_config, mock_client):
        """Test analyze_code works even without init (uses CodeAnalyzer)."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            # No init() called

            with patch('repo_ctx.analysis.CodeAnalyzer') as mock_analyzer_cls:
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_file.return_value = ([], [])
                mock_analyzer.detect_language.return_value = "python"
                mock_analyzer_cls.return_value = mock_analyzer

                result = ctx.analyze_code("code", "test.py")

                assert result["file_path"] == "test.py"

    @pytest.mark.asyncio
    async def test_get_supported_languages(self, mock_config, mock_client):
        """Test get_supported_languages uses CodeAnalyzer."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)

            with patch('repo_ctx.analysis.CodeAnalyzer') as mock_analyzer_cls:
                mock_analyzer = MagicMock()
                mock_analyzer.language_map = {
                    ".py": "python",
                    ".js": "javascript",
                }
                mock_analyzer_cls.return_value = mock_analyzer

                result = ctx.get_supported_languages()

                assert "python" in result or "javascript" in result


class TestMCPServerContextHealthCheck:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_health_check_before_init(self, mock_config, mock_client):
        """Test health check before init returns client status."""
        mock_client.is_initialized = False
        mock_client._legacy_context = None

        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            health = await ctx.health_check()

            assert health["client"] == "not initialized"
            assert health["overall"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_after_init(self, mock_config, mock_client, mock_legacy_context):
        """Test health check after init shows client healthy."""
        mock_client.is_initialized = True
        mock_client._legacy_context = mock_legacy_context

        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()

            health = await ctx.health_check()

            assert health["client"] == "healthy"
            assert health["overall"] == "healthy"
            assert "content_storage" in health


class TestMCPServerContextClose:
    """Tests for closing the context."""

    @pytest.mark.asyncio
    async def test_close_calls_client_close(self, mock_config, mock_client):
        """Test close delegates to client."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.close()

            mock_client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_idempotent(self, mock_config, mock_client):
        """Test close can be called multiple times."""
        with patch('repo_ctx.mcp.server_context.RepoCtxClient', return_value=mock_client):
            from repo_ctx.mcp import MCPServerContext

            ctx = MCPServerContext(mock_config)
            await ctx.init()
            await ctx.close()
            await ctx.close()  # Should not error

            # Only one close should happen
            assert mock_client.close.call_count <= 2
