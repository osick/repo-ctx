"""Tests for the unified RepoCtxClient.

This module tests the unified client that provides a single interface
for both direct service access and HTTP API access.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from repo_ctx.client import (
    RepoCtxClient,
    ClientMode,
    Library,
    Document,
    Symbol,
    SearchResult,
    IndexResult,
    AnalysisResult,
)
from repo_ctx.client.models import SymbolType, Visibility


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config():
    """Create mock configuration."""
    config = MagicMock()
    config.storage_path = ":memory:"
    config.storage = MagicMock()
    config.storage.content_db_path = ":memory:"
    return config


@pytest.fixture
def mock_legacy_context():
    """Create mock legacy GitLabContext."""
    context = AsyncMock()
    context.init = AsyncMock()
    context.storage = MagicMock()
    context.list_all_libraries = AsyncMock(return_value=[])
    context.search_libraries = AsyncMock(return_value=[])
    context.fuzzy_search_libraries = AsyncMock(return_value=[])
    context.index_repository = AsyncMock()
    context.index_group = AsyncMock(return_value={"indexed": [], "failed": []})
    context.get_documentation = AsyncMock(return_value={})
    return context


@pytest.fixture
def mock_http_session():
    """Create mock HTTP session."""
    session = AsyncMock()
    session.get = AsyncMock()
    session.post = AsyncMock()
    session.close = AsyncMock()
    return session


# =============================================================================
# Client Initialization Tests
# =============================================================================


class TestClientInitialization:
    """Test client initialization."""

    def test_default_mode_is_direct(self):
        """Default mode should be direct when no API URL provided."""
        client = RepoCtxClient()
        assert client.mode == ClientMode.DIRECT

    def test_http_mode_when_api_url_provided(self):
        """Mode should be HTTP when API URL is provided."""
        client = RepoCtxClient(api_url="http://localhost:8000")
        assert client.mode == ClientMode.HTTP

    def test_explicit_mode_override(self):
        """Explicit mode should override auto-detection."""
        client = RepoCtxClient(mode=ClientMode.HTTP)
        assert client.mode == ClientMode.HTTP

        client = RepoCtxClient(api_url="http://localhost:8000", mode=ClientMode.DIRECT)
        assert client.mode == ClientMode.DIRECT

    def test_is_initialized_false_initially(self):
        """Client should not be initialized initially."""
        client = RepoCtxClient()
        assert not client.is_initialized

    @pytest.mark.asyncio
    async def test_connect_initializes_client(self, mock_config, mock_legacy_context):
        """Connect should initialize the client."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            client = RepoCtxClient(config=mock_config)
            await client.connect()

            assert client.is_initialized
            mock_legacy_context.init.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_idempotent(self, mock_config, mock_legacy_context):
        """Multiple connect calls should be safe."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            client = RepoCtxClient(config=mock_config)
            await client.connect()
            await client.connect()  # Second call should be no-op

            # init should only be called once
            mock_legacy_context.init.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_cleans_up(self, mock_config, mock_legacy_context):
        """Close should clean up resources."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            client = RepoCtxClient(config=mock_config)
            await client.connect()
            await client.close()

            assert not client.is_initialized


# =============================================================================
# Context Manager Tests
# =============================================================================


class TestContextManager:
    """Test async context manager support."""

    @pytest.mark.asyncio
    async def test_context_manager_direct_mode(self, mock_config, mock_legacy_context):
        """Context manager should work in direct mode."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                assert client.is_initialized

            # Should be closed after context
            assert not client.is_initialized

    @pytest.mark.asyncio
    async def test_context_manager_http_mode(self, mock_http_session):
        """Context manager should work in HTTP mode."""
        with patch("httpx.AsyncClient", return_value=mock_http_session):
            async with RepoCtxClient(api_url="http://localhost:8000") as client:
                assert client.is_initialized

            mock_http_session.close.assert_called_once()


# =============================================================================
# Library Operations Tests
# =============================================================================


class TestLibraryOperations:
    """Test library management operations."""

    @pytest.mark.asyncio
    async def test_list_libraries_direct(self, mock_config, mock_legacy_context):
        """List libraries in direct mode."""
        mock_legacy_context.list_all_libraries.return_value = [
            {"id": "/owner/repo", "name": "repo", "group": "owner", "provider": "github"}
        ]

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                libraries = await client.list_libraries()

                assert len(libraries) == 1
                assert isinstance(libraries[0], Library)
                assert libraries[0].id == "/owner/repo"

    @pytest.mark.asyncio
    async def test_list_libraries_with_provider_filter(self, mock_config, mock_legacy_context):
        """List libraries filtered by provider."""
        mock_legacy_context.list_all_libraries.return_value = []

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                await client.list_libraries(provider="github")

                mock_legacy_context.list_all_libraries.assert_called_with("github")

    @pytest.mark.asyncio
    async def test_get_library_found(self, mock_config, mock_legacy_context):
        """Get library that exists."""
        mock_legacy_context.search_libraries.return_value = [
            {"id": "/owner/repo", "name": "repo", "group": "owner"}
        ]

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                lib = await client.get_library("/owner/repo")

                assert lib is not None
                assert lib.id == "/owner/repo"

    @pytest.mark.asyncio
    async def test_get_library_not_found(self, mock_config, mock_legacy_context):
        """Get library that doesn't exist."""
        mock_legacy_context.search_libraries.return_value = []

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                lib = await client.get_library("/nonexistent/repo")

                assert lib is None

    @pytest.mark.asyncio
    async def test_search_libraries_fuzzy(self, mock_config, mock_legacy_context):
        """Search libraries with fuzzy matching."""
        mock_legacy_context.fuzzy_search_libraries.return_value = [
            ("repo", 0.95),
            ("other-repo", 0.80),
        ]

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                results = await client.search_libraries("rep", fuzzy=True)

                assert len(results) == 2
                assert results[0].name == "repo"
                assert results[0].score == 0.95

    @pytest.mark.asyncio
    async def test_search_libraries_exact(self, mock_config, mock_legacy_context):
        """Search libraries with exact matching."""
        mock_legacy_context.search_libraries.return_value = ["repo"]

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                results = await client.search_libraries("repo", fuzzy=False)

                assert len(results) == 1
                mock_legacy_context.search_libraries.assert_called_with("repo")


# =============================================================================
# Indexing Operations Tests
# =============================================================================


class TestIndexingOperations:
    """Test repository indexing operations."""

    @pytest.mark.asyncio
    async def test_index_repository_github(self, mock_config, mock_legacy_context):
        """Index a GitHub repository."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                result = await client.index_repository("owner/repo", provider="github")

                assert result.status == "success"
                assert result.repository == "owner/repo"
                mock_legacy_context.index_repository.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_repository_local(self, mock_config, mock_legacy_context):
        """Index a local repository."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                result = await client.index_repository("/path/to/repo")

                assert result.status == "success"
                assert result.repository == "/path/to/repo"

    @pytest.mark.asyncio
    async def test_index_repository_failure(self, mock_config, mock_legacy_context):
        """Handle indexing failure."""
        mock_legacy_context.index_repository.side_effect = Exception("Network error")

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                result = await client.index_repository("owner/repo")

                assert result.status == "failed"
                assert "Network error" in result.error

    @pytest.mark.asyncio
    async def test_index_group(self, mock_config, mock_legacy_context):
        """Index all repositories in a group."""
        mock_legacy_context.index_group.return_value = {
            "indexed": ["repo1", "repo2"],
            "failed": ["repo3"],
        }

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                results = await client.index_group("org")

                assert len(results) == 3
                success_count = sum(1 for r in results if r.status == "success")
                assert success_count == 2


# =============================================================================
# Documentation Operations Tests
# =============================================================================


class TestDocumentationOperations:
    """Test documentation retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_documentation_basic(self, mock_config, mock_legacy_context):
        """Get basic documentation."""
        mock_legacy_context.get_documentation.return_value = {
            "content": "# README\n\nDocumentation here.",
            "library_id": "/owner/repo",
        }

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                docs = await client.get_documentation("/owner/repo")

                assert "content" in docs
                assert "library_id" in docs

    @pytest.mark.asyncio
    async def test_get_documentation_with_topic(self, mock_config, mock_legacy_context):
        """Get documentation filtered by topic."""
        mock_legacy_context.get_documentation.return_value = {}

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                await client.get_documentation("/owner/repo", topic="installation")

                call_args = mock_legacy_context.get_documentation.call_args
                assert call_args.kwargs["topic"] == "installation"

    @pytest.mark.asyncio
    async def test_get_documentation_with_max_tokens(self, mock_config, mock_legacy_context):
        """Get documentation with token limit."""
        mock_legacy_context.get_documentation.return_value = {}

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                await client.get_documentation("/owner/repo", max_tokens=5000)

                call_args = mock_legacy_context.get_documentation.call_args
                assert call_args.kwargs["max_tokens"] == 5000


# =============================================================================
# Analysis Operations Tests
# =============================================================================


class TestAnalysisOperations:
    """Test code analysis operations."""

    @pytest.mark.asyncio
    async def test_analyze_code_python(self, mock_config, mock_legacy_context):
        """Analyze Python code."""
        mock_symbol = MagicMock()
        mock_symbol.name = "test_func"
        mock_symbol.qualified_name = "module.test_func"
        mock_symbol.symbol_type = MagicMock(value="function")
        mock_symbol.file_path = "test.py"
        mock_symbol.line_start = 1
        mock_symbol.line_end = 5
        mock_symbol.signature = "def test_func()"
        mock_symbol.visibility = "public"
        mock_symbol.docstring = "Test function"

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_file.return_value = ([mock_symbol], ["os", "sys"])
        mock_analyzer.detect_language.return_value = "python"

        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            with patch("repo_ctx.analysis.CodeAnalyzer", return_value=mock_analyzer):
                async with RepoCtxClient(config=mock_config) as client:
                    result = await client.analyze_code(
                        "def test_func(): pass",
                        "test.py",
                    )

                    assert isinstance(result, AnalysisResult)
                    assert result.file_path == "test.py"
                    assert result.language == "python"

    @pytest.mark.asyncio
    async def test_search_symbols(self, mock_config, mock_legacy_context):
        """Search for symbols."""
        with patch("repo_ctx.core.GitLabContext", return_value=mock_legacy_context):
            async with RepoCtxClient(config=mock_config) as client:
                # Direct mode returns empty list (simplified impl)
                results = await client.search_symbols("test_func")
                assert isinstance(results, list)


# =============================================================================
# HTTP Mode Tests
# =============================================================================


class TestHttpMode:
    """Test HTTP API mode operations."""

    @pytest.mark.asyncio
    async def test_list_libraries_http(self, mock_http_session):
        """List libraries via HTTP API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "repositories": [
                {"id": "/owner/repo", "name": "repo", "group": "owner", "provider": "github"}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_http_session.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_http_session):
            async with RepoCtxClient(api_url="http://localhost:8000") as client:
                libraries = await client.list_libraries()

                assert len(libraries) == 1
                assert libraries[0].id == "/owner/repo"

    @pytest.mark.asyncio
    async def test_search_libraries_http(self, mock_http_session):
        """Search libraries via HTTP API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [
                {"id": "/owner/repo", "name": "repo", "result_type": "library", "score": 0.95}
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_http_session.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_http_session):
            async with RepoCtxClient(api_url="http://localhost:8000") as client:
                results = await client.search_libraries("repo")

                assert len(results) == 1
                assert results[0].score == 0.95

    @pytest.mark.asyncio
    async def test_index_repository_http(self, mock_http_session):
        """Index repository via HTTP API."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "repository": "owner/repo",
            "documents": 10,
            "symbols": 50,
        }
        mock_response.raise_for_status = MagicMock()
        mock_http_session.post.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_http_session):
            async with RepoCtxClient(api_url="http://localhost:8000") as client:
                result = await client.index_repository("owner/repo")

                assert result.status == "success"
                assert result.documents == 10

    @pytest.mark.asyncio
    async def test_get_library_http_not_found(self, mock_http_session):
        """Get library via HTTP when not found."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_http_session.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_http_session):
            async with RepoCtxClient(api_url="http://localhost:8000") as client:
                lib = await client.get_library("/nonexistent/repo")
                assert lib is None


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Test error handling."""

    @pytest.mark.asyncio
    async def test_not_initialized_error(self):
        """Operations should fail if not initialized."""
        client = RepoCtxClient()

        with pytest.raises(RuntimeError, match="Client not initialized"):
            await client.list_libraries()


# =============================================================================
# Model Conversion Tests
# =============================================================================


class TestModelConversions:
    """Test model conversion methods."""

    def test_convert_library_from_dict(self):
        """Convert library from dictionary."""
        client = RepoCtxClient()
        lib = client._convert_library({
            "id": "/owner/repo",
            "name": "repo",
            "group": "owner",
            "provider": "github",
            "description": "A test repo",
        })

        assert lib.id == "/owner/repo"
        assert lib.name == "repo"
        assert lib.provider == "github"

    def test_convert_library_from_object(self):
        """Convert library from legacy object."""
        client = RepoCtxClient()
        legacy = MagicMock()
        legacy.id = "/owner/repo"
        legacy.name = "repo"
        legacy.group = "owner"
        legacy.provider = "gitlab"
        legacy.description = "Test"
        legacy.last_indexed = datetime.now()

        lib = client._convert_library(legacy)

        assert lib.id == "/owner/repo"
        assert lib.provider == "gitlab"

    def test_convert_search_result_from_tuple(self):
        """Convert search result from tuple."""
        client = RepoCtxClient()
        result = client._convert_search_result(("repo", 0.85), "library")

        assert result.name == "repo"
        assert result.score == 0.85
        assert result.result_type == "library"

    def test_convert_search_result_from_string(self):
        """Convert search result from string."""
        client = RepoCtxClient()
        result = client._convert_search_result("repo", "library")

        assert result.name == "repo"
        assert result.score == 1.0

    def test_convert_symbol_from_dict(self):
        """Convert symbol from dictionary."""
        client = RepoCtxClient()
        sym = client._convert_symbol({
            "name": "test_func",
            "qualified_name": "module.test_func",
            "symbol_type": "function",
            "file_path": "test.py",
            "line_start": 1,
            "line_end": 5,
        })

        assert sym.name == "test_func"
        assert sym.symbol_type == SymbolType.FUNCTION

    def test_convert_symbol_from_object(self):
        """Convert symbol from legacy object."""
        client = RepoCtxClient()
        legacy = MagicMock()
        legacy.name = "MyClass"
        legacy.qualified_name = "module.MyClass"
        legacy.symbol_type = MagicMock(value="class")
        legacy.file_path = "module.py"
        legacy.line_start = 10
        legacy.line_end = 50
        legacy.signature = "class MyClass"
        legacy.visibility = "public"
        legacy.docstring = "A class"

        sym = client._convert_symbol(legacy)

        assert sym.name == "MyClass"
        assert sym.symbol_type == SymbolType.CLASS


# =============================================================================
# Model Dataclass Tests
# =============================================================================


class TestModels:
    """Test model dataclasses."""

    def test_library_from_dict(self):
        """Create Library from dictionary."""
        lib = Library.from_dict({
            "id": "/owner/repo",
            "name": "repo",
            "group": "owner",
            "provider": "github",
            "description": "A repo",
            "versions": ["v1.0", "v2.0"],
            "last_indexed": "2024-01-01T00:00:00",
        })

        assert lib.id == "/owner/repo"
        assert lib.versions == ["v1.0", "v2.0"]
        assert lib.last_indexed is not None

    def test_library_to_dict(self):
        """Convert Library to dictionary."""
        lib = Library(
            id="/owner/repo",
            name="repo",
            group="owner",
            provider="github",
        )
        data = lib.to_dict()

        assert data["id"] == "/owner/repo"
        assert data["provider"] == "github"

    def test_document_round_trip(self):
        """Document dict round-trip."""
        doc = Document(
            id="doc1",
            path="README.md",
            title="README",
            content="# Hello",
            library_id="/owner/repo",
        )
        data = doc.to_dict()
        doc2 = Document.from_dict(data)

        assert doc.id == doc2.id
        assert doc.content == doc2.content

    def test_symbol_round_trip(self):
        """Symbol dict round-trip."""
        sym = Symbol(
            name="test",
            qualified_name="module.test",
            symbol_type=SymbolType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=5,
        )
        data = sym.to_dict()
        sym2 = Symbol.from_dict(data)

        assert sym.name == sym2.name
        assert sym.symbol_type == sym2.symbol_type

    def test_search_result_round_trip(self):
        """SearchResult dict round-trip."""
        result = SearchResult(
            id="result1",
            name="test",
            result_type="library",
            score=0.95,
            snippet="Test snippet",
        )
        data = result.to_dict()
        result2 = SearchResult.from_dict(data)

        assert result.id == result2.id
        assert result.score == result2.score

    def test_index_result_round_trip(self):
        """IndexResult dict round-trip."""
        result = IndexResult(
            status="success",
            repository="/owner/repo",
            documents=10,
            symbols=50,
            duration_ms=1000,
        )
        data = result.to_dict()
        result2 = IndexResult.from_dict(data)

        assert result.status == result2.status
        assert result.documents == result2.documents

    def test_analysis_result_round_trip(self):
        """AnalysisResult dict round-trip."""
        result = AnalysisResult(
            file_path="test.py",
            language="python",
            symbols=[
                Symbol(
                    name="func",
                    qualified_name="func",
                    symbol_type=SymbolType.FUNCTION,
                    file_path="test.py",
                )
            ],
            dependencies=["os", "sys"],
        )
        data = result.to_dict()
        result2 = AnalysisResult.from_dict(data)

        assert result.file_path == result2.file_path
        assert len(result2.symbols) == 1

    def test_symbol_type_fallback(self):
        """Symbol type should fallback to FUNCTION for unknown types."""
        sym = Symbol.from_dict({
            "name": "test",
            "qualified_name": "test",
            "symbol_type": "unknown_type",
            "file_path": "test.py",
        })
        assert sym.symbol_type == SymbolType.FUNCTION

    def test_visibility_fallback(self):
        """Visibility should fallback to PUBLIC for unknown values."""
        sym = Symbol.from_dict({
            "name": "test",
            "qualified_name": "test",
            "symbol_type": "function",
            "file_path": "test.py",
            "visibility": "unknown_visibility",
        })
        assert sym.visibility == Visibility.PUBLIC


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunction:
    """Test the create_client factory function."""

    def test_create_client_direct_mode(self):
        """Create client in direct mode."""
        from repo_ctx.client.client import create_client

        client = create_client()
        assert client.mode == ClientMode.DIRECT

    def test_create_client_http_mode(self):
        """Create client in HTTP mode."""
        from repo_ctx.client.client import create_client

        client = create_client(api_url="http://localhost:8000")
        assert client.mode == ClientMode.HTTP

    def test_create_client_with_api_key(self):
        """Create client with API key."""
        from repo_ctx.client.client import create_client

        client = create_client(
            api_url="http://localhost:8000",
            api_key="secret-key"
        )
        assert client._api_key == "secret-key"
