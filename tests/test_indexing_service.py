"""Tests for indexing service and API endpoints.

This module tests the indexing service which handles repository
indexing operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from repo_ctx.models import Library
from repo_ctx.services.base import ServiceContext
from repo_ctx.services.indexing import IndexingService


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_content_storage():
    """Create a mock content storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.init_db = AsyncMock()
    storage.get_library = AsyncMock(return_value=None)
    storage.save_library = AsyncMock(return_value=1)
    storage.save_documents = AsyncMock()
    storage.save_symbols = AsyncMock()
    return storage


@pytest.fixture
def mock_vector_storage():
    """Create a mock vector storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.create_collection = AsyncMock()
    storage.upsert_embeddings = AsyncMock()
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


@pytest.fixture
def mock_git_provider():
    """Create a mock git provider."""
    provider = MagicMock()
    provider.get_documentation_files = MagicMock(return_value=[
        {"path": "README.md", "content": "# Test Repo\n\nThis is a test."},
        {"path": "docs/guide.md", "content": "# Guide\n\nUser guide content."},
    ])
    provider.get_repository_info = MagicMock(return_value={
        "name": "test-repo",
        "description": "A test repository",
        "default_branch": "main",
    })
    return provider


# =============================================================================
# IndexingService Tests
# =============================================================================


class TestIndexingService:
    """Tests for IndexingService."""

    def test_indexing_service_creation(self, service_context):
        """Test creating an indexing service."""
        service = IndexingService(service_context)
        assert service is not None

    @pytest.mark.asyncio
    async def test_index_repository_basic(
        self, service_context, mock_content_storage, mock_git_provider
    ):
        """Test basic repository indexing."""
        service = IndexingService(service_context)

        with patch.object(service, '_create_provider', return_value=mock_git_provider):
            result = await service.index_repository(
                repository="test/repo",
                provider_type="github",
            )

        assert result is not None
        assert result["status"] == "success"
        mock_content_storage.save_library.assert_called_once()

    @pytest.mark.asyncio
    async def test_index_repository_saves_documents(
        self, service_context, mock_content_storage, mock_git_provider
    ):
        """Test that indexing saves documents."""
        service = IndexingService(service_context)

        with patch.object(service, '_create_provider', return_value=mock_git_provider):
            result = await service.index_repository(
                repository="test/repo",
                provider_type="github",
            )

        mock_content_storage.save_documents.assert_called_once()
        call_args = mock_content_storage.save_documents.call_args
        documents = call_args[0][0]
        assert len(documents) == 2

    @pytest.mark.asyncio
    async def test_index_repository_with_version(
        self, service_context, mock_content_storage, mock_git_provider
    ):
        """Test indexing with specific version."""
        service = IndexingService(service_context)

        with patch.object(service, '_create_provider', return_value=mock_git_provider):
            result = await service.index_repository(
                repository="test/repo",
                provider_type="github",
                version="v1.0.0",
            )

        assert result["version"] == "v1.0.0"

    @pytest.mark.asyncio
    async def test_index_repository_already_indexed(
        self, service_context, mock_content_storage, mock_git_provider
    ):
        """Test indexing when repository already exists (should update)."""
        mock_content_storage.get_library = AsyncMock(return_value=Library(
            id=1,
            group_name="test",
            project_name="repo",
            description="Existing",
            default_version="main",
        ))

        service = IndexingService(service_context)

        with patch.object(service, '_create_provider', return_value=mock_git_provider):
            result = await service.index_repository(
                repository="test/repo",
                provider_type="github",
            )

        assert result["status"] == "success"
        assert result["updated"] is True

    @pytest.mark.asyncio
    async def test_get_indexing_status(self, service_context, mock_content_storage):
        """Test getting indexing status."""
        mock_content_storage.get_library = AsyncMock(return_value=Library(
            id=1,
            group_name="test",
            project_name="repo",
            description="Test",
            default_version="main",
        ))

        service = IndexingService(service_context)
        status = await service.get_indexing_status("/test/repo")

        assert status is not None
        assert status["indexed"] is True

    @pytest.mark.asyncio
    async def test_get_indexing_status_not_found(self, service_context, mock_content_storage):
        """Test getting status for non-indexed repository."""
        mock_content_storage.get_library = AsyncMock(return_value=None)

        service = IndexingService(service_context)
        status = await service.get_indexing_status("/test/repo")

        assert status is not None
        assert status["indexed"] is False


# =============================================================================
# Indexing API Endpoint Tests
# =============================================================================


class TestIndexingEndpoints:
    """Tests for indexing API endpoints."""

    @pytest.fixture
    def app(self, service_context):
        """Create FastAPI app with indexing routes."""
        from repo_ctx.api.routes.indexing import create_indexing_router

        app = FastAPI()
        router = create_indexing_router(service_context)
        app.include_router(router, prefix="/v1")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_index_endpoint_exists(self, client, mock_git_provider):
        """Test that POST /v1/index endpoint exists."""
        with patch(
            'repo_ctx.services.indexing.IndexingService._create_provider',
            return_value=mock_git_provider
        ):
            response = client.post(
                "/v1/index",
                json={"repository": "test/repo", "provider": "github"}
            )
        # Should not be 404
        assert response.status_code != 404

    def test_index_endpoint_requires_repository(self, client):
        """Test that index endpoint requires repository field."""
        response = client.post("/v1/index", json={})
        assert response.status_code == 422  # Validation error

    def test_status_endpoint_exists(self, client):
        """Test that GET /v1/index/status endpoint exists."""
        response = client.get("/v1/index/status", params={"repository": "test/repo"})
        assert response.status_code != 404

    def test_status_endpoint_requires_repository(self, client):
        """Test that status endpoint requires repository parameter."""
        response = client.get("/v1/index/status")
        assert response.status_code == 422  # Validation error
