"""Tests for graph search endpoints.

These tests verify:
- Graph query API endpoints
- Semantic symbol search
- Call graph traversal
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient


class TestGraphEndpoints:
    """Tests for graph API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_graph_call_graph_endpoint_in_openapi(self, client):
        """Test that call-graph endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        # Check for path pattern
        paths = list(data["paths"].keys())
        call_graph_paths = [p for p in paths if "call-graph" in p]
        assert len(call_graph_paths) > 0

    def test_graph_symbols_endpoint_in_openapi(self, client):
        """Test that /v1/graph/symbols is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/graph/symbols" in data["paths"]

    def test_graph_semantic_search_endpoint_in_openapi(self, client):
        """Test that /v1/graph/semantic-search is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/graph/semantic-search" in data["paths"]

    def test_analyze_persist_endpoint_in_openapi(self, client):
        """Test that /v1/analyze/persist is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/analyze/persist" in data["paths"]

    def test_graph_symbols_no_storage(self, client):
        """Test graph symbols returns empty when no graph storage."""
        response = client.get("/v1/graph/symbols", params={"symbol_type": "class"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["symbols"] == []

    def test_graph_semantic_search_no_storage(self, client):
        """Test semantic search returns empty when no embedding service."""
        response = client.get("/v1/graph/semantic-search", params={"q": "test"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    def test_graph_call_graph_no_storage(self, client):
        """Test call graph returns empty when no graph storage."""
        response = client.get("/v1/graph/call-graph/test_function")
        assert response.status_code == 200
        data = response.json()
        assert data["nodes"] == []
        assert data["relationships"] == []


class TestAnalysisServiceGraphMethods:
    """Tests for analysis service graph methods."""

    @pytest.fixture
    def mock_graph_storage(self):
        """Create mock graph storage."""
        storage = MagicMock()
        storage.create_nodes = AsyncMock()
        storage.create_relationships = AsyncMock()
        storage.get_call_graph = AsyncMock(return_value=MagicMock(nodes=[], relationships=[]))
        storage.find_nodes_by_label = AsyncMock(return_value=[])
        storage.get_node = AsyncMock(return_value=None)
        storage.delete_by_library = AsyncMock(return_value=0)
        return storage

    @pytest.fixture
    def mock_embedding_service(self):
        """Create mock embedding service."""
        service = MagicMock()
        service.embed_symbol = AsyncMock()
        service.search_similar_symbols = AsyncMock(return_value=[])
        service.delete_library_embeddings = AsyncMock(return_value={})
        return service

    @pytest.mark.asyncio
    async def test_persist_analysis_to_graph(self, mock_graph_storage, mock_embedding_service):
        """Test persisting analysis to graph storage."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            graph_storage=mock_graph_storage,
        )
        service = AnalysisService(context, embedding_service=mock_embedding_service)

        symbols = [
            {
                "name": "MyClass",
                "qualified_name": "module.MyClass",
                "symbol_type": "class",
                "file_path": "module.py",
                "visibility": "public",
            }
        ]
        dependencies = [
            {"source": "MyClass.method", "target": "helper", "dependency_type": "calls"}
        ]

        result = await service.persist_analysis_to_graph(
            library_id="/test/repo",
            symbols=symbols,
            dependencies=dependencies,
        )

        assert result["nodes"] == 1
        assert result["relationships"] == 1
        mock_graph_storage.create_nodes.assert_called_once()
        mock_graph_storage.create_relationships.assert_called_once()

    @pytest.mark.asyncio
    async def test_persist_analysis_no_graph_storage(self, mock_embedding_service):
        """Test persist returns zeros without graph storage."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = AnalysisService(context, embedding_service=mock_embedding_service)

        result = await service.persist_analysis_to_graph(
            library_id="/test",
            symbols=[{"name": "test"}],
            dependencies=[],
        )

        assert result == {"nodes": 0, "relationships": 0}

    @pytest.mark.asyncio
    async def test_query_call_graph(self, mock_graph_storage):
        """Test querying call graph."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage
        from repo_ctx.storage.protocols import GraphNode, GraphRelationship

        # Setup mock return value
        mock_graph_storage.get_call_graph = AsyncMock(
            return_value=MagicMock(
                nodes=[
                    GraphNode(id="sym1", labels=["Function"], properties={"name": "func1"}),
                    GraphNode(id="sym2", labels=["Function"], properties={"name": "func2"}),
                ],
                relationships=[
                    GraphRelationship(from_id="sym1", to_id="sym2", type="CALLS", properties={}),
                ],
            )
        )

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            graph_storage=mock_graph_storage,
        )
        service = AnalysisService(context)

        result = await service.query_call_graph("func1", depth=2)

        assert len(result["nodes"]) == 2
        assert len(result["relationships"]) == 1

    @pytest.mark.asyncio
    async def test_semantic_symbol_search(self, mock_graph_storage, mock_embedding_service):
        """Test semantic symbol search."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        mock_embedding_service.search_similar_symbols = AsyncMock(
            return_value=[
                {"id": "sym1", "name": "my_function", "score": 0.9}
            ]
        )

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            graph_storage=mock_graph_storage,
        )
        service = AnalysisService(context, embedding_service=mock_embedding_service)

        results = await service.semantic_symbol_search("function that processes data")

        assert len(results) == 1
        assert results[0]["name"] == "my_function"

    @pytest.mark.asyncio
    async def test_find_symbols_by_type(self, mock_graph_storage):
        """Test finding symbols by type."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage
        from repo_ctx.storage.protocols import GraphNode

        mock_graph_storage.find_nodes_by_label = AsyncMock(
            return_value=[
                GraphNode(
                    id="class1",
                    labels=["Symbol", "Class"],
                    properties={
                        "name": "MyClass",
                        "qualified_name": "module.MyClass",
                        "file_path": "module.py",
                    },
                )
            ]
        )

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            graph_storage=mock_graph_storage,
        )
        service = AnalysisService(context)

        results = await service.find_symbols_by_type("class")

        assert len(results) == 1
        assert results[0]["name"] == "MyClass"

    @pytest.mark.asyncio
    async def test_delete_library_analysis(self, mock_graph_storage, mock_embedding_service):
        """Test deleting library analysis data."""
        from repo_ctx.services.analysis import AnalysisService
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.storage import ContentStorage

        mock_graph_storage.delete_by_library = AsyncMock(return_value=5)
        mock_embedding_service.delete_library_embeddings = AsyncMock(
            return_value={"documents": 10, "symbols": 5}
        )

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            graph_storage=mock_graph_storage,
        )
        service = AnalysisService(context, embedding_service=mock_embedding_service)

        counts = await service.delete_library_analysis("/test/repo")

        assert counts["graph_nodes"] == 5
        assert counts["embeddings"] == 15
