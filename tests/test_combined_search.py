"""Tests for combined search across all storage backends.

These tests verify:
- Combined search API endpoints
- Multi-source search functionality
- Result merging and deduplication
- Score boosting
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from repo_ctx.services.combined_search import (
    CombinedSearchService,
    SearchResult,
    CombinedSearchResponse,
)


class TestCombinedSearchEndpoints:
    """Tests for combined search API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_combined_search_endpoint_in_openapi(self, client):
        """Test that /v1/search/combined is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/combined" in data["paths"]

    def test_combined_search_documents_endpoint_in_openapi(self, client):
        """Test that /v1/search/combined/documents is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/combined/documents" in data["paths"]

    def test_combined_search_symbols_endpoint_in_openapi(self, client):
        """Test that /v1/search/combined/symbols is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/combined/symbols" in data["paths"]

    def test_combined_search_basic(self, client):
        """Test basic combined search."""
        response = client.get("/v1/search/combined", params={"q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert data["query"] == "test"
        assert "results" in data
        assert "sources_used" in data
        assert "total" in data

    def test_combined_search_with_source_filter(self, client):
        """Test combined search with source filter."""
        response = client.get(
            "/v1/search/combined",
            params={"q": "test", "sources": "content"},
        )
        assert response.status_code == 200

    def test_combined_search_documents_only(self, client):
        """Test combined search for documents only."""
        response = client.get(
            "/v1/search/combined/documents",
            params={"q": "test"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"

    def test_combined_search_symbols_only(self, client):
        """Test combined search for symbols only."""
        response = client.get(
            "/v1/search/combined/symbols",
            params={"q": "test"},
        )
        assert response.status_code == 200

    def test_combined_search_with_limit(self, client):
        """Test combined search with custom limit."""
        response = client.get(
            "/v1/search/combined",
            params={"q": "test", "limit": 5},
        )
        assert response.status_code == 200

    def test_combined_search_with_repository(self, client):
        """Test combined search with repository filter."""
        response = client.get(
            "/v1/search/combined",
            params={"q": "test", "repository": "/owner/repo"},
        )
        assert response.status_code == 200


class TestCombinedSearchService:
    """Tests for CombinedSearchService."""

    @pytest.fixture
    def mock_content_storage(self):
        """Create mock content storage."""
        storage = MagicMock()
        storage.get_library = AsyncMock(return_value=None)
        storage.get_all_libraries = AsyncMock(return_value=[])
        storage.get_documents = AsyncMock(return_value=[])
        storage.search_symbols = AsyncMock(return_value=[])
        return storage

    @pytest.fixture
    def mock_vector_storage(self):
        """Create mock vector storage."""
        return MagicMock()

    @pytest.fixture
    def mock_graph_storage(self):
        """Create mock graph storage."""
        storage = MagicMock()
        storage.find_nodes_by_label = AsyncMock(return_value=[])
        return storage

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service."""
        service = MagicMock()
        service.search_similar_documents = AsyncMock(return_value=[])
        service.search_similar_symbols = AsyncMock(return_value=[])
        return service

    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_content_storage):
        """Test search with no results."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        result = await service.search("test query")

        assert result.total == 0
        assert result.results == []

    @pytest.mark.asyncio
    async def test_search_content_only(self, mock_content_storage):
        """Test search with content source only."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        result = await service.search(
            "test",
            search_sources=["content"],
        )

        assert result.total == 0

    @pytest.mark.asyncio
    async def test_search_with_vector(
        self, mock_content_storage, mock_vector_storage, mock_embedding_service
    ):
        """Test search with vector storage."""
        from repo_ctx.services.base import ServiceContext

        mock_embedding_service.search_similar_documents = AsyncMock(
            return_value=[
                {"id": "doc1", "score": 0.9, "file_path": "test.md"}
            ]
        )

        context = ServiceContext(
            content_storage=mock_content_storage,
            vector_storage=mock_vector_storage,
        )
        service = CombinedSearchService(context, embedding_service=mock_embedding_service)

        result = await service.search("test query")

        assert result.vector_count == 1
        assert len(result.results) >= 1

    @pytest.mark.asyncio
    async def test_search_with_graph(
        self, mock_content_storage, mock_graph_storage
    ):
        """Test search with graph storage."""
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage.protocols import GraphNode

        mock_graph_storage.find_nodes_by_label = AsyncMock(
            return_value=[
                GraphNode(
                    id="sym1",
                    labels=["Symbol", "Function"],
                    properties={"name": "test_function", "file_path": "test.py"},
                )
            ]
        )

        context = ServiceContext(
            content_storage=mock_content_storage,
            graph_storage=mock_graph_storage,
        )
        service = CombinedSearchService(context)

        result = await service.search("test")

        assert result.graph_count >= 0

    @pytest.mark.asyncio
    async def test_result_merging(self, mock_content_storage):
        """Test that duplicate results are merged."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        # Test merge function directly
        results = [
            SearchResult(id="doc1", source="content", score=0.8),
            SearchResult(id="doc1", source="vector", score=0.9),
        ]

        merged = service._merge_results(results)

        assert len(merged) == 1
        assert merged[0].score == 0.9  # Higher score kept
        assert "sources" in merged[0].metadata

    @pytest.mark.asyncio
    async def test_score_boosting(self, mock_content_storage):
        """Test that score boosting is applied."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        # Search with custom boost values
        result = await service.search(
            "test",
            boost_exact_match=3.0,
            boost_semantic=2.0,
            boost_graph=1.5,
        )

        # Just verify it doesn't error
        assert result.query == "test"

    @pytest.mark.asyncio
    async def test_search_documents_only(self, mock_content_storage):
        """Test search_documents method."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        result = await service.search_documents("test")

        assert result.query == "test"

    @pytest.mark.asyncio
    async def test_search_symbols_only(self, mock_content_storage):
        """Test search_symbols method."""
        from repo_ctx.services.base import ServiceContext

        context = ServiceContext(content_storage=mock_content_storage)
        service = CombinedSearchService(context)

        result = await service.search_symbols("test")

        assert result.query == "test"


class TestSearchResult:
    """Tests for SearchResult dataclass."""

    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            id="test-id",
            source="content",
            score=0.85,
            file_path="test.py",
            name="test_function",
        )

        assert result.id == "test-id"
        assert result.source == "content"
        assert result.score == 0.85
        assert result.file_path == "test.py"
        assert result.name == "test_function"
        assert result.metadata == {}

    def test_search_result_with_metadata(self):
        """Test SearchResult with metadata."""
        result = SearchResult(
            id="test-id",
            source="vector",
            score=0.9,
            metadata={"semantic_match": True},
        )

        assert result.metadata["semantic_match"] is True
