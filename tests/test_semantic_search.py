"""Tests for semantic search endpoints.

These tests verify:
- Semantic search API endpoints
- Integration with embedding service
- Search result formatting
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


class TestSemanticSearchEndpoints:
    """Tests for semantic search API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client without vector storage."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_semantic_search_endpoint_in_openapi(self, client):
        """Test that /v1/search/semantic is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/semantic" in data["paths"]

    def test_semantic_search_documents_endpoint_in_openapi(self, client):
        """Test that /v1/search/semantic/documents is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/semantic/documents" in data["paths"]

    def test_semantic_search_symbols_endpoint_in_openapi(self, client):
        """Test that /v1/search/semantic/symbols is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/semantic/symbols" in data["paths"]

    def test_semantic_search_no_vector_storage(self, client):
        """Test semantic search returns empty when no vector storage."""
        response = client.get("/v1/search/semantic", params={"q": "test query"})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test query"
        assert data["documents"] == []
        assert data["symbols"] == []
        assert data["chunks"] == []
        assert data["total"] == 0

    def test_semantic_search_documents_no_vector_storage(self, client):
        """Test semantic search documents returns empty when no vector storage."""
        response = client.get("/v1/search/semantic/documents", params={"q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["results"] == []
        assert data["total"] == 0

    def test_semantic_search_symbols_no_vector_storage(self, client):
        """Test semantic search symbols returns empty when no vector storage."""
        response = client.get("/v1/search/semantic/symbols", params={"q": "function"})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "function"
        assert data["results"] == []
        assert data["total"] == 0

    def test_semantic_search_with_repository_filter(self, client):
        """Test semantic search with repository filter."""
        response = client.get(
            "/v1/search/semantic",
            params={"q": "test", "repository": "/owner/repo"},
        )
        assert response.status_code == 200

    def test_semantic_search_with_type_filter(self, client):
        """Test semantic search with type filter."""
        response = client.get(
            "/v1/search/semantic",
            params={"q": "test", "search_type": "documents"},
        )
        assert response.status_code == 200

    def test_semantic_search_with_limit(self, client):
        """Test semantic search with custom limit."""
        response = client.get(
            "/v1/search/semantic",
            params={"q": "test", "limit": 5},
        )
        assert response.status_code == 200

    def test_semantic_search_requires_query(self, client):
        """Test semantic search requires query parameter."""
        response = client.get("/v1/search/semantic")
        assert response.status_code == 422  # Validation error

    def test_semantic_search_limit_bounds(self, client):
        """Test semantic search respects limit bounds."""
        # Above max
        response = client.get("/v1/search/semantic", params={"q": "test", "limit": 100})
        assert response.status_code == 422

        # Below min
        response = client.get("/v1/search/semantic", params={"q": "test", "limit": 0})
        assert response.status_code == 422


class TestSearchServiceSemanticMethods:
    """Tests for search service semantic methods."""

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service."""
        service = MagicMock()
        service.search_similar_documents = AsyncMock(return_value=[
            {"id": "doc-1", "score": 0.95, "file_path": "README.md"},
        ])
        service.search_similar_symbols = AsyncMock(return_value=[
            {"id": "sym-1", "score": 0.90, "name": "my_func"},
        ])
        service.search_similar_chunks = AsyncMock(return_value=[
            {"id": "chunk-1", "score": 0.85, "chunk_type": "code"},
        ])
        return service

    @pytest.mark.asyncio
    async def test_semantic_search_all(self, mock_embedding_service):
        """Test semantic search for all types."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context, embedding_service=mock_embedding_service)

        results = await service.semantic_search("test query")

        assert len(results["documents"]) == 1
        assert len(results["symbols"]) == 1
        assert len(results["chunks"]) == 1

    @pytest.mark.asyncio
    async def test_semantic_search_documents_only(self, mock_embedding_service):
        """Test semantic search for documents only."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context, embedding_service=mock_embedding_service)

        results = await service.semantic_search("test", search_type="documents")

        assert len(results["documents"]) == 1
        assert len(results["symbols"]) == 0
        assert len(results["chunks"]) == 0

    @pytest.mark.asyncio
    async def test_semantic_search_no_embedding_service(self):
        """Test semantic search without embedding service."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context, embedding_service=None)

        results = await service.semantic_search("test")

        assert results["documents"] == []
        assert results["symbols"] == []
        assert results["chunks"] == []

    @pytest.mark.asyncio
    async def test_semantic_search_documents_method(self, mock_embedding_service):
        """Test direct semantic_search_documents method."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context, embedding_service=mock_embedding_service)

        results = await service.semantic_search_documents("test")

        assert len(results) == 1
        assert results[0]["id"] == "doc-1"

    @pytest.mark.asyncio
    async def test_semantic_search_symbols_method(self, mock_embedding_service):
        """Test direct semantic_search_symbols method."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context, embedding_service=mock_embedding_service)

        results = await service.semantic_search_symbols("function that does X")

        assert len(results) == 1
        assert results[0]["name"] == "my_func"

    @pytest.mark.asyncio
    async def test_set_embedding_service(self, mock_embedding_service):
        """Test setting embedding service after init."""
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = SearchService(context)

        assert service.embedding_service is None

        service.set_embedding_service(mock_embedding_service)

        assert service.embedding_service is mock_embedding_service
