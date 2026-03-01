"""Tests for FastAPI application.

These tests verify the API server skeleton and core endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestAPIApplication:
    """Tests for API application setup."""

    def test_app_exists(self):
        """API app should exist."""
        from repo_ctx.api import app

        assert app is not None

    def test_app_is_fastapi(self):
        """API app should be a FastAPI instance."""
        from fastapi import FastAPI
        from repo_ctx.api import app

        assert isinstance(app, FastAPI)

    def test_app_title(self):
        """API app should have a title."""
        from repo_ctx.api import app

        assert app.title == "repo-ctx API"

    def test_app_version(self):
        """API app should have a version."""
        from repo_ctx.api import app

        assert app.version is not None


class TestHealthEndpoints:
    """Tests for health check endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_health_endpoint_exists(self, client):
        """GET /health should exist."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """GET /health should return status."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_returns_version(self, client):
        """GET /health should return version."""
        response = client.get("/health")
        data = response.json()
        assert "version" in data

    def test_health_returns_components(self, client):
        """GET /health should return component status."""
        response = client.get("/health")
        data = response.json()
        assert "components" in data
        components = data["components"]
        assert "content_db" in components
        assert "vector_db" in components
        assert "graph_db" in components


class TestInfoEndpoint:
    """Tests for info endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_info_endpoint_exists(self, client):
        """GET /info should exist."""
        response = client.get("/info")
        assert response.status_code == 200

    def test_info_returns_name(self, client):
        """GET /info should return app name."""
        response = client.get("/info")
        data = response.json()
        assert "name" in data
        assert data["name"] == "repo-ctx"

    def test_info_returns_description(self, client):
        """GET /info should return description."""
        response = client.get("/info")
        data = response.json()
        assert "description" in data

    def test_info_returns_capabilities(self, client):
        """GET /info should return capabilities."""
        response = client.get("/info")
        data = response.json()
        assert "capabilities" in data
        capabilities = data["capabilities"]
        assert "indexing" in capabilities
        assert "search" in capabilities
        assert "analysis" in capabilities


class TestRootEndpoint:
    """Tests for root endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_root_endpoint_exists(self, client):
        """GET / should exist."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_welcome(self, client):
        """GET / should return welcome message."""
        response = client.get("/")
        data = response.json()
        assert "message" in data
        assert "docs_url" in data


class TestAPIVersioning:
    """Tests for API versioning."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_health_endpoint(self, client):
        """GET /v1/health should exist."""
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_v1_info_endpoint(self, client):
        """GET /v1/info should exist."""
        response = client.get("/v1/info")
        assert response.status_code == 200


class TestIndexingEndpointsWired:
    """Tests that indexing endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_index_endpoint_in_openapi(self, client):
        """Test that POST /v1/index endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/index" in data["paths"]
        assert "post" in data["paths"]["/v1/index"]

    def test_v1_index_status_endpoint_in_openapi(self, client):
        """Test that GET /v1/index/status endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/index/status" in data["paths"]
        assert "get" in data["paths"]["/v1/index/status"]


class TestSearchEndpointsWired:
    """Tests that search endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_search_endpoint_in_openapi(self, client):
        """Test that GET /v1/search endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search" in data["paths"]
        assert "get" in data["paths"]["/v1/search"]

    def test_v1_search_symbols_endpoint_in_openapi(self, client):
        """Test that GET /v1/search/symbols endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/search/symbols" in data["paths"]
        assert "get" in data["paths"]["/v1/search/symbols"]

    def test_v1_symbols_detail_endpoint_in_openapi(self, client):
        """Test that GET /v1/symbols/{name} endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        # Path parameter uses {qualified_name:path}
        assert "/v1/symbols/{qualified_name}" in data["paths"]
        assert "get" in data["paths"]["/v1/symbols/{qualified_name}"]


class TestAnalysisEndpointsWired:
    """Tests that analysis endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_analyze_endpoint_in_openapi(self, client):
        """Test that POST /v1/analyze endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/analyze" in data["paths"]
        assert "post" in data["paths"]["/v1/analyze"]

    def test_v1_analyze_languages_endpoint_in_openapi(self, client):
        """Test that GET /v1/analyze/languages endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/analyze/languages" in data["paths"]
        assert "get" in data["paths"]["/v1/analyze/languages"]

    def test_v1_analyze_graph_endpoint_in_openapi(self, client):
        """Test that POST /v1/analyze/graph endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/analyze/graph" in data["paths"]
        assert "post" in data["paths"]["/v1/analyze/graph"]


class TestOpenAPISchema:
    """Tests for OpenAPI schema."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_openapi_schema_exists(self, client):
        """GET /openapi.json should exist."""
        response = client.get("/openapi.json")
        assert response.status_code == 200

    def test_openapi_schema_valid(self, client):
        """OpenAPI schema should be valid JSON."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_endpoint_exists(self, client):
        """GET /docs should exist (Swagger UI)."""
        response = client.get("/docs")
        assert response.status_code == 200


class TestRepositoriesEndpointsWired:
    """Tests that repository endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_repositories_endpoint_in_openapi(self, client):
        """Test that GET /v1/repositories endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/repositories" in data["paths"]
        assert "get" in data["paths"]["/v1/repositories"]

    def test_v1_repository_detail_endpoint_in_openapi(self, client):
        """Test that GET /v1/repositories/{group}/{project} is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/repositories/{group}/{project}" in data["paths"]
        assert "get" in data["paths"]["/v1/repositories/{group}/{project}"]
        assert "delete" in data["paths"]["/v1/repositories/{group}/{project}"]

    def test_v1_repository_stats_endpoint_in_openapi(self, client):
        """Test that GET /v1/repositories/{group}/{project}/stats is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/repositories/{group}/{project}/stats" in data["paths"]
        assert "get" in data["paths"]["/v1/repositories/{group}/{project}/stats"]


class TestDocsEndpointsWired:
    """Tests that documentation endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_docs_endpoint_in_openapi(self, client):
        """Test that GET /v1/docs/{group}/{project} is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/docs/{group}/{project}" in data["paths"]
        assert "get" in data["paths"]["/v1/docs/{group}/{project}"]

    def test_v1_docs_list_endpoint_in_openapi(self, client):
        """Test that GET /v1/docs/{group}/{project}/list is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/docs/{group}/{project}/list" in data["paths"]
        assert "get" in data["paths"]["/v1/docs/{group}/{project}/list"]

    def test_v1_llmstxt_endpoint_in_openapi(self, client):
        """Test that GET /v1/llmstxt/{group}/{project} is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/llmstxt/{group}/{project}" in data["paths"]
        assert "get" in data["paths"]["/v1/llmstxt/{group}/{project}"]


class TestRepositoriesEndpointsBehavior:
    """Tests for repository endpoints behavior."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_list_repositories_returns_empty(self, client):
        """GET /v1/repositories returns empty list when no repos indexed."""
        response = client.get("/v1/repositories")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "repositories" in data
        assert isinstance(data["repositories"], list)

    def test_list_repositories_with_provider_filter(self, client):
        """GET /v1/repositories accepts provider filter."""
        response = client.get("/v1/repositories?provider=github")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data

    def test_get_repository_not_found(self, client):
        """GET /v1/repositories/{group}/{project} returns 404 for missing repo."""
        response = client.get("/v1/repositories/nonexistent/repo")
        assert response.status_code == 404

    def test_delete_repository_not_found(self, client):
        """DELETE /v1/repositories/{group}/{project} returns 404 for missing repo."""
        response = client.delete("/v1/repositories/nonexistent/repo")
        assert response.status_code == 404


class TestDocsEndpointsBehavior:
    """Tests for documentation endpoints behavior."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_get_docs_not_found(self, client):
        """GET /v1/docs/{group}/{project} returns 404 for missing repo."""
        response = client.get("/v1/docs/nonexistent/repo")
        assert response.status_code == 404

    def test_get_docs_list_not_found(self, client):
        """GET /v1/docs/{group}/{project}/list returns 404 for missing repo."""
        response = client.get("/v1/docs/nonexistent/repo/list")
        assert response.status_code == 404

    def test_get_llmstxt_not_found(self, client):
        """GET /v1/llmstxt/{group}/{project} returns 404 for missing repo."""
        response = client.get("/v1/llmstxt/nonexistent/repo")
        assert response.status_code == 404


class TestTasksEndpointsWired:
    """Tests that task endpoints are wired into the app."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_v1_tasks_endpoint_in_openapi(self, client):
        """Test that GET /v1/tasks endpoint is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/tasks" in data["paths"]
        assert "get" in data["paths"]["/v1/tasks"]

    def test_v1_task_detail_endpoint_in_openapi(self, client):
        """Test that GET /v1/tasks/{task_id} is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/tasks/{task_id}" in data["paths"]
        assert "get" in data["paths"]["/v1/tasks/{task_id}"]
        assert "delete" in data["paths"]["/v1/tasks/{task_id}"]

    def test_v1_task_stream_endpoint_in_openapi(self, client):
        """Test that GET /v1/tasks/{task_id}/stream is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/tasks/{task_id}/stream" in data["paths"]
        assert "get" in data["paths"]["/v1/tasks/{task_id}/stream"]


class TestTasksEndpointsBehavior:
    """Tests for task endpoints behavior."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app

        return TestClient(app)

    def test_list_tasks_returns_empty(self, client):
        """GET /v1/tasks returns empty list when no tasks."""
        response = client.get("/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_list_tasks_with_status_filter(self, client):
        """GET /v1/tasks accepts status filter."""
        response = client.get("/v1/tasks?status=running")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data

    def test_get_task_not_found(self, client):
        """GET /v1/tasks/{task_id} returns 404 for missing task."""
        response = client.get("/v1/tasks/nonexistent-task-id")
        assert response.status_code == 404

    def test_delete_task_not_found(self, client):
        """DELETE /v1/tasks/{task_id} returns 404 for missing task."""
        response = client.delete("/v1/tasks/nonexistent-task-id")
        assert response.status_code == 404

    def test_task_stream_not_found(self, client):
        """GET /v1/tasks/{task_id}/stream returns 404 for missing task."""
        response = client.get("/v1/tasks/nonexistent-task-id/stream")
        assert response.status_code == 404


class TestTaskHelperFunctions:
    """Tests for task helper functions."""

    def test_create_task(self):
        """Test create_task creates a task."""
        from repo_ctx.api.routes.tasks import create_task, get_task, _tasks

        # Clear any existing tasks
        _tasks.clear()

        task_id = create_task("test_type", {"key": "value"})

        assert task_id is not None
        task = get_task(task_id)
        assert task is not None
        assert task["type"] == "test_type"
        assert task["status"] == "pending"
        assert task["params"] == {"key": "value"}

    def test_update_task(self):
        """Test update_task updates task progress."""
        from repo_ctx.api.routes.tasks import create_task, update_task, get_task, _tasks

        _tasks.clear()
        task_id = create_task("test_type")

        success = update_task(task_id, status="running", progress=50.0, message="Halfway done")

        assert success is True
        task = get_task(task_id)
        assert task["status"] == "running"
        assert task["progress"] == 50.0
        assert task["message"] == "Halfway done"

    def test_update_nonexistent_task(self):
        """Test update_task returns False for missing task."""
        from repo_ctx.api.routes.tasks import update_task, _tasks

        _tasks.clear()
        success = update_task("nonexistent", status="running")
        assert success is False
