"""Tests for service layer foundation.

This module tests the service layer that provides business logic
between the API endpoints and storage backends.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from dataclasses import dataclass
from typing import Optional

# Import what we're going to build
from repo_ctx.services.base import BaseService, ServiceContext
from repo_ctx.services.repository import RepositoryService
from repo_ctx.models import Library, Document


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_content_storage():
    """Create a mock content storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.get_all_libraries = AsyncMock(return_value=[])
    storage.get_library = AsyncMock(return_value=None)
    storage.save_library = AsyncMock(return_value=1)
    storage.delete_library = AsyncMock(return_value=True)
    storage.save_documents = AsyncMock()
    storage.get_documents = AsyncMock(return_value=[])
    return storage


@pytest.fixture
def mock_vector_storage():
    """Create a mock vector storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.create_collection = AsyncMock()
    storage.upsert_embeddings = AsyncMock()
    storage.search_similar = AsyncMock(return_value=[])
    storage.delete_by_library = AsyncMock(return_value=0)
    return storage


@pytest.fixture
def mock_graph_storage():
    """Create a mock graph storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.create_nodes = AsyncMock()
    storage.create_relationships = AsyncMock()
    storage.delete_by_library = AsyncMock(return_value=0)
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
# ServiceContext Tests
# =============================================================================


class TestServiceContext:
    """Tests for ServiceContext."""

    def test_context_creation(self, mock_content_storage):
        """Test creating a context with minimal storage."""
        ctx = ServiceContext(content_storage=mock_content_storage)
        assert ctx.content_storage is mock_content_storage
        assert ctx.vector_storage is None
        assert ctx.graph_storage is None

    def test_context_with_all_storages(self, service_context):
        """Test creating a context with all storages."""
        assert service_context.content_storage is not None
        assert service_context.vector_storage is not None
        assert service_context.graph_storage is not None

    @pytest.mark.asyncio
    async def test_context_health_check_all_healthy(self, service_context):
        """Test health check when all storages are healthy."""
        health = await service_context.health_check()
        assert health["content_storage"]["status"] == "healthy"
        assert health["vector_storage"]["status"] == "healthy"
        assert health["graph_storage"]["status"] == "healthy"
        assert health["overall"] == "healthy"

    @pytest.mark.asyncio
    async def test_context_health_check_partial_failure(self, mock_content_storage):
        """Test health check when some storages fail."""
        mock_content_storage.health_check = AsyncMock(return_value=False)
        ctx = ServiceContext(content_storage=mock_content_storage)

        health = await ctx.health_check()
        assert health["content_storage"]["status"] == "unhealthy"
        # When only content storage is configured and it's unhealthy, overall is unhealthy
        assert health["overall"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_context_health_check_skips_none_storages(self, mock_content_storage):
        """Test health check only checks configured storages."""
        ctx = ServiceContext(content_storage=mock_content_storage)
        health = await ctx.health_check()

        assert "content_storage" in health
        assert health["vector_storage"]["status"] == "not_configured"
        assert health["graph_storage"]["status"] == "not_configured"


# =============================================================================
# BaseService Tests
# =============================================================================


class TestBaseService:
    """Tests for BaseService."""

    def test_service_creation(self, service_context):
        """Test creating a base service."""
        service = BaseService(service_context)
        assert service.context is service_context

    def test_service_access_to_storages(self, service_context):
        """Test service has access to all storages via context."""
        service = BaseService(service_context)
        assert service.content_storage is not None
        assert service.vector_storage is not None
        assert service.graph_storage is not None

    def test_service_with_minimal_context(self, mock_content_storage):
        """Test service works with minimal storage configuration."""
        ctx = ServiceContext(content_storage=mock_content_storage)
        service = BaseService(ctx)
        assert service.content_storage is not None
        assert service.vector_storage is None


# =============================================================================
# RepositoryService Tests
# =============================================================================


class TestRepositoryService:
    """Tests for RepositoryService."""

    def test_repository_service_creation(self, service_context):
        """Test creating a repository service."""
        service = RepositoryService(service_context)
        assert isinstance(service, BaseService)

    @pytest.mark.asyncio
    async def test_list_repositories_empty(self, service_context):
        """Test listing repositories when none exist."""
        service = RepositoryService(service_context)
        repos = await service.list_repositories()
        assert repos == []

    @pytest.mark.asyncio
    async def test_list_repositories_with_data(self, service_context, mock_content_storage):
        """Test listing repositories with existing data."""
        mock_libraries = [
            Library(
                id=1,
                group_name="test",
                project_name="repo1",
                description="Test 1",
                default_version="main",
            ),
            Library(
                id=2,
                group_name="test",
                project_name="repo2",
                description="Test 2",
                default_version="main",
            ),
        ]
        mock_content_storage.get_all_libraries = AsyncMock(return_value=mock_libraries)

        service = RepositoryService(service_context)
        repos = await service.list_repositories()

        assert len(repos) == 2
        assert repos[0].project_name == "repo1"
        assert repos[1].project_name == "repo2"

    @pytest.mark.asyncio
    async def test_get_repository_not_found(self, service_context):
        """Test getting a non-existent repository."""
        service = RepositoryService(service_context)
        repo = await service.get_repository("/nonexistent/repo")
        assert repo is None

    @pytest.mark.asyncio
    async def test_get_repository_found(self, service_context, mock_content_storage):
        """Test getting an existing repository."""
        mock_library = Library(
            id=1,
            group_name="test",
            project_name="repo",
            description="Test",
            default_version="main",
        )
        mock_content_storage.get_library = AsyncMock(return_value=mock_library)

        service = RepositoryService(service_context)
        repo = await service.get_repository("/test/repo")

        assert repo is not None
        assert repo.project_name == "repo"
        mock_content_storage.get_library.assert_called_once_with("/test/repo")

    @pytest.mark.asyncio
    async def test_delete_repository_not_found(self, service_context, mock_content_storage):
        """Test deleting a non-existent repository."""
        mock_content_storage.delete_library = AsyncMock(return_value=False)

        service = RepositoryService(service_context)
        result = await service.delete_repository("/nonexistent/repo")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_repository_success(self, service_context, mock_content_storage):
        """Test deleting an existing repository."""
        mock_content_storage.delete_library = AsyncMock(return_value=True)

        service = RepositoryService(service_context)
        result = await service.delete_repository("/test/repo")

        assert result is True
        mock_content_storage.delete_library.assert_called_once_with("/test/repo")

    @pytest.mark.asyncio
    async def test_delete_repository_cleans_all_storages(
        self, service_context, mock_content_storage, mock_vector_storage, mock_graph_storage
    ):
        """Test that deleting a repository cleans all storage backends."""
        mock_content_storage.delete_library = AsyncMock(return_value=True)
        mock_vector_storage.delete_by_library = AsyncMock(return_value=5)
        mock_graph_storage.delete_by_library = AsyncMock(return_value=10)

        service = RepositoryService(service_context)
        result = await service.delete_repository("/test/repo")

        assert result is True
        mock_content_storage.delete_library.assert_called_once()
        mock_vector_storage.delete_by_library.assert_called_once()
        mock_graph_storage.delete_by_library.assert_called_once()

    @pytest.mark.asyncio
    async def test_repository_exists_true(self, service_context, mock_content_storage):
        """Test checking if repository exists when it does."""
        mock_library = Library(
            id=1,
            group_name="test",
            project_name="repo",
            description="Test",
            default_version="main",
        )
        mock_content_storage.get_library = AsyncMock(return_value=mock_library)

        service = RepositoryService(service_context)
        exists = await service.repository_exists("/test/repo")

        assert exists is True

    @pytest.mark.asyncio
    async def test_repository_exists_false(self, service_context, mock_content_storage):
        """Test checking if repository exists when it doesn't."""
        mock_content_storage.get_library = AsyncMock(return_value=None)

        service = RepositoryService(service_context)
        exists = await service.repository_exists("/nonexistent/repo")

        assert exists is False

    @pytest.mark.asyncio
    async def test_get_repository_stats(self, service_context, mock_content_storage):
        """Test getting repository statistics."""
        mock_library = Library(
            id=1,
            group_name="test",
            project_name="repo",
            description="Test",
            default_version="main",
        )
        mock_content_storage.get_library = AsyncMock(return_value=mock_library)
        mock_content_storage.get_documents = AsyncMock(
            return_value=[
                Document(version_id=1, file_path="/doc1.md", content="test"),
                Document(version_id=1, file_path="/doc2.md", content="test"),
            ]
        )

        service = RepositoryService(service_context)
        stats = await service.get_repository_stats("/test/repo")

        assert stats is not None
        assert stats["project_name"] == "repo"
        assert stats["document_count"] == 2

    @pytest.mark.asyncio
    async def test_get_repository_stats_not_found(self, service_context, mock_content_storage):
        """Test getting stats for non-existent repository."""
        mock_content_storage.get_library = AsyncMock(return_value=None)

        service = RepositoryService(service_context)
        stats = await service.get_repository_stats("/nonexistent/repo")

        assert stats is None


# =============================================================================
# Service Factory Tests
# =============================================================================


class TestServiceFactory:
    """Tests for service factory functions."""

    def test_create_service_context_from_config(self):
        """Test creating a service context from configuration."""
        from repo_ctx.services import create_service_context
        from repo_ctx.config import Config

        # This should work with default in-memory configuration
        config = Config()
        ctx = create_service_context(config)

        assert ctx is not None
        assert ctx.content_storage is not None

    def test_create_repository_service(self, service_context):
        """Test creating a repository service instance."""
        from repo_ctx.services import create_repository_service

        service = create_repository_service(service_context)
        assert isinstance(service, RepositoryService)
