"""Tests for analysis service and API endpoints.

This module tests the analysis service which handles code
analysis operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from repo_ctx.models import Library
from repo_ctx.services.base import ServiceContext
from repo_ctx.services.analysis import AnalysisService


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_content_storage():
    """Create a mock content storage."""
    storage = AsyncMock()
    storage.health_check = AsyncMock(return_value=True)
    storage.get_library = AsyncMock(return_value=None)
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


@pytest.fixture
def sample_python_code():
    """Sample Python code for testing."""
    return '''
class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract b from a."""
        return a - b


def main():
    """Main function."""
    calc = Calculator()
    print(calc.add(1, 2))
'''


# =============================================================================
# AnalysisService Tests
# =============================================================================


class TestAnalysisService:
    """Tests for AnalysisService."""

    def test_analysis_service_creation(self, service_context):
        """Test creating an analysis service."""
        service = AnalysisService(service_context)
        assert service is not None

    def test_get_supported_languages(self, service_context):
        """Test getting supported languages."""
        service = AnalysisService(service_context)
        languages = service.get_supported_languages()

        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert "java" in languages

    def test_analyze_code_python(self, service_context, sample_python_code):
        """Test analyzing Python code."""
        service = AnalysisService(service_context)
        result = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
            language="python",
        )

        assert result is not None
        assert "symbols" in result
        assert "dependencies" in result
        assert len(result["symbols"]) > 0

    def test_analyze_code_detects_language(self, service_context, sample_python_code):
        """Test that analyze_code detects language from file path."""
        service = AnalysisService(service_context)
        result = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
        )

        assert result is not None
        assert result["language"] == "python"

    def test_analyze_code_unsupported_language(self, service_context):
        """Test analyzing code with unsupported language."""
        service = AnalysisService(service_context)
        result = service.analyze_code(
            code="some code",
            file_path="file.unknown",
        )

        assert result["symbols"] == []
        assert result["dependencies"] == []

    def test_analyze_code_extracts_classes(self, service_context, sample_python_code):
        """Test that classes are extracted."""
        service = AnalysisService(service_context)
        result = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
        )

        symbols = result["symbols"]
        class_symbols = [s for s in symbols if s["symbol_type"] == "class"]
        assert len(class_symbols) >= 1
        assert any(s["name"] == "Calculator" for s in class_symbols)

    def test_analyze_code_extracts_functions(self, service_context, sample_python_code):
        """Test that functions are extracted."""
        service = AnalysisService(service_context)
        result = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
        )

        symbols = result["symbols"]
        func_symbols = [s for s in symbols if s["symbol_type"] in ("function", "method")]
        assert len(func_symbols) >= 1

    def test_generate_dependency_graph(self, service_context, sample_python_code):
        """Test generating dependency graph."""
        service = AnalysisService(service_context)

        # First analyze code
        analysis = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
        )

        # Then generate graph
        graph = service.generate_dependency_graph(
            symbols=analysis["symbols"],
            dependencies=analysis["dependencies"],
            graph_type="class",
        )

        assert graph is not None
        # JGF format has nodes/edges nested under "graph"
        assert "graph" in graph
        assert "nodes" in graph["graph"]
        assert "edges" in graph["graph"]

    def test_generate_dependency_graph_formats(self, service_context, sample_python_code):
        """Test dependency graph output formats."""
        service = AnalysisService(service_context)

        analysis = service.analyze_code(
            code=sample_python_code,
            file_path="calculator.py",
        )

        # Test JSON format
        json_graph = service.generate_dependency_graph(
            symbols=analysis["symbols"],
            dependencies=analysis["dependencies"],
            output_format="json",
        )
        assert isinstance(json_graph, dict)

        # Test DOT format
        dot_graph = service.generate_dependency_graph(
            symbols=analysis["symbols"],
            dependencies=analysis["dependencies"],
            output_format="dot",
        )
        assert isinstance(dot_graph, str)
        assert "digraph" in dot_graph


# =============================================================================
# Analysis API Endpoint Tests
# =============================================================================


class TestAnalysisEndpoints:
    """Tests for analysis API endpoints."""

    @pytest.fixture
    def app(self, service_context):
        """Create FastAPI app with analysis routes."""
        from repo_ctx.api.routes.analysis import create_analysis_router

        app = FastAPI()
        router = create_analysis_router(service_context)
        app.include_router(router, prefix="/v1")
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return TestClient(app)

    def test_analyze_endpoint_exists(self, client, sample_python_code):
        """Test that POST /v1/analyze endpoint exists."""
        response = client.post(
            "/v1/analyze",
            json={"code": sample_python_code, "file_path": "test.py"}
        )
        assert response.status_code != 404

    def test_analyze_endpoint_requires_code(self, client):
        """Test that analyze endpoint requires code field."""
        response = client.post("/v1/analyze", json={"file_path": "test.py"})
        assert response.status_code == 422  # Validation error

    def test_analyze_endpoint_returns_symbols(self, client, sample_python_code):
        """Test that analyze endpoint returns symbols."""
        response = client.post(
            "/v1/analyze",
            json={"code": sample_python_code, "file_path": "test.py"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert "dependencies" in data

    def test_languages_endpoint_exists(self, client):
        """Test that GET /v1/analyze/languages endpoint exists."""
        response = client.get("/v1/analyze/languages")
        assert response.status_code == 200

    def test_languages_endpoint_returns_list(self, client):
        """Test that languages endpoint returns list."""
        response = client.get("/v1/analyze/languages")
        data = response.json()
        assert "languages" in data
        assert isinstance(data["languages"], list)

    def test_graph_endpoint_exists(self, client, sample_python_code):
        """Test that POST /v1/analyze/graph endpoint exists."""
        response = client.post(
            "/v1/analyze/graph",
            json={
                "symbols": [],
                "dependencies": [],
                "graph_type": "class",
            }
        )
        assert response.status_code != 404

    def test_graph_endpoint_returns_graph(self, client):
        """Test that graph endpoint returns graph structure."""
        response = client.post(
            "/v1/analyze/graph",
            json={
                "symbols": [
                    {
                        "name": "TestClass",
                        "qualified_name": "test.TestClass",
                        "symbol_type": "class",
                        "file_path": "test.py",
                        "line_start": 1,
                        "line_end": 10,
                    }
                ],
                "dependencies": [],
                "graph_type": "class",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "nodes" in data or "graph" in data
