"""Tests for search service and API endpoints.

This module tests the search service which handles repository
search operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from repo_ctx.models import Library, Document
from repo_ctx.services.base import ServiceContext
from repo_ctx.services.search import SearchService
from repo_ctx.storage.protocols import SimilarityResult


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_content_storage():
    """Create a mock content storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.get_library = AsyncMock(return_value=None)
    storage.get_documents = AsyncMock(return_value=[])
    storage.search_symbols = AsyncMock(return_value=[])
    storage.get_symbol_by_name = AsyncMock(return_value=None)
    return storage


@pytest.fixture
def mock_vector_storage():
    """Create a mock vector storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.search_similar = AsyncMock(return_value=[])
    return storage


@pytest.fixture
def mock_graph_storage():
    """Create a mock graph storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.get_call_graph = AsyncMock(return_value=MagicMock(nodes=[], relationships=[]))
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
# SearchService Tests
# =============================================================================


class TestSearchService:
    """Tests for SearchService."""

    def test_search_service_creation(self, service_context):
        """Test creating a search service."""
        service = SearchService(service_context)
        assert service is not None

    @pytest.mark.asyncio
    async def test_search_documents_empty(self, service_context, mock_content_storage):
        """Test searching when no documents match."""
        mock_content_storage.get_documents = AsyncMock(return_value=[])

        service = SearchService(service_context)
        results = await service.search_documents(
            query="test query",
            repository_id="/test/repo",
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_search_documents_with_results(
        self, service_context, mock_content_storage
    ):
        """Test searching with matching documents."""
        mock_documents = [
            Document(
                version_id=1,
                file_path="README.md",
                content="Test content with query term",
            ),
            Document(
                version_id=1,
                file_path="docs/guide.md",
                content="Another document with query",
            ),
        ]
        mock_content_storage.get_documents = AsyncMock(return_value=mock_documents)

        service = SearchService(service_context)
        results = await service.search_documents(
            query="query",
            repository_id="/test/repo",
        )

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_search_symbols_empty(self, service_context, mock_content_storage):
        """Test searching symbols when none match."""
        mock_content_storage.search_symbols = AsyncMock(return_value=[])

        service = SearchService(service_context)
        results = await service.search_symbols(
            query="test_function",
            repository_id=1,
        )

        assert results == []

    @pytest.mark.asyncio
    async def test_search_symbols_with_results(
        self, service_context, mock_content_storage
    ):
        """Test searching symbols with matches."""
        mock_symbols = [
            {
                "name": "test_function",
                "qualified_name": "module.test_function",
                "symbol_type": "function",
                "file_path": "module.py",
            },
        ]
        mock_content_storage.search_symbols = AsyncMock(return_value=mock_symbols)

        service = SearchService(service_context)
        results = await service.search_symbols(
            query="test",
            repository_id=1,
        )

        assert len(results) == 1
        assert results[0]["name"] == "test_function"

    @pytest.mark.asyncio
    async def test_semantic_search_without_vector_storage(self, mock_content_storage):
        """Test semantic search when vector storage not configured."""
        ctx = ServiceContext(content_storage=mock_content_storage)
        service = SearchService(ctx)

        results = await service.semantic_search(
            query="test query",
            repository_id="/test/repo",
        )

        # semantic_search returns a dict with query, documents, symbols, chunks
        assert isinstance(results, dict)
        assert results["query"] == "test query"
        assert results["documents"] == []
        assert results["symbols"] == []
        assert results["chunks"] == []

    @pytest.mark.asyncio
    async def test_semantic_search_with_vector_storage(
        self, service_context, mock_vector_storage
    ):
        """Test semantic search with vector storage and embedding service."""
        mock_embedding_service = AsyncMock()
        mock_embedding_service.search_similar_documents = AsyncMock(return_value=[
            {
                "id": "doc_1",
                "score": 0.95,
                "file_path": "README.md",
                "library_id": "/test/repo",
            },
        ])
        mock_embedding_service.search_similar_symbols = AsyncMock(return_value=[])
        mock_embedding_service.search_similar_chunks = AsyncMock(return_value=[])

        service = SearchService(service_context, embedding_service=mock_embedding_service)
        results = await service.semantic_search(
            query="test query",
            repository_id="/test/repo",
        )

        # semantic_search returns a dict with query, documents, symbols, chunks
        assert isinstance(results, dict)
        assert results["query"] == "test query"
        assert len(results["documents"]) == 1
        assert results["documents"][0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_get_symbol_detail(self, service_context, mock_content_storage):
        """Test getting symbol detail."""
        mock_symbol = {
            "name": "MyClass",
            "qualified_name": "module.MyClass",
            "symbol_type": "class",
            "file_path": "module.py",
            "line_start": 10,
            "line_end": 50,
        }
        mock_content_storage.get_symbol_by_name = AsyncMock(return_value=mock_symbol)

        service = SearchService(service_context)
        result = await service.get_symbol_detail(
            repository_id=1,
            qualified_name="module.MyClass",
        )

        assert result is not None
        assert result["name"] == "MyClass"

    @pytest.mark.asyncio
    async def test_get_symbol_detail_not_found(
        self, service_context, mock_content_storage
    ):
        """Test getting symbol detail when not found."""
        mock_content_storage.get_symbol_by_name = AsyncMock(return_value=None)

        service = SearchService(service_context)
        result = await service.get_symbol_detail(
            repository_id=1,
            qualified_name="nonexistent.Symbol",
        )

        assert result is None


# =============================================================================
# Search API Endpoint Tests
# =============================================================================


class TestSearchEndpoints:
    """Tests for search API endpoints."""

    @pytest.fixture
    def app(self, service_context):
        """Create FastAPI app with search routes."""
        from repo_ctx.api.routes.search import create_search_router

        app = FastAPI()
        router = create_search_router(service_context)
        app.include_router(router, prefix="/v1")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_search_endpoint_exists(self, client):
        """Test that GET /v1/search endpoint exists."""
        response = client.get("/v1/search", params={"q": "test"})
        assert response.status_code != 404

    def test_search_endpoint_requires_query(self, client):
        """Test that search endpoint requires query parameter."""
        response = client.get("/v1/search")
        assert response.status_code == 422  # Validation error

    def test_symbols_search_endpoint_exists(self, client):
        """Test that GET /v1/search/symbols endpoint exists."""
        response = client.get(
            "/v1/search/symbols",
            params={"q": "test", "repository_id": 1}
        )
        assert response.status_code != 404

    def test_symbol_detail_endpoint_exists(self, client):
        """Test that GET /v1/symbols/{name} endpoint exists."""
        response = client.get(
            "/v1/symbols/module.Class",
            params={"repository_id": 1}
        )
        assert response.status_code != 404
