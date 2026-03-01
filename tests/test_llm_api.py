"""Tests for LLM analysis API endpoints.

These tests verify:
- LLM summarization endpoint
- LLM explanation endpoint
- LLM classification endpoint
- LLM improvement suggestions endpoint
- LLM docstring generation endpoint
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestLLMEndpoints:
    """Tests for LLM API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_llm_endpoints_in_openapi(self, client):
        """Test that LLM endpoints are in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/v1/llm/summarize" in data["paths"]
        assert "/v1/llm/explain" in data["paths"]
        assert "/v1/llm/classify" in data["paths"]
        assert "/v1/llm/improve" in data["paths"]
        assert "/v1/llm/docstring" in data["paths"]

    def test_summarize_endpoint(self, client):
        """Test code summarization endpoint."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "code": "def add(a, b):\n    return a + b",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert data["language"] == "python"

    def test_summarize_endpoint_with_file_path(self, client):
        """Test summarization with file path."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "code": "class UserService:\n    pass",
                "language": "python",
                "file_path": "services/user.py",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["file_path"] == "services/user.py"

    def test_summarize_endpoint_with_context(self, client):
        """Test summarization with additional context."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "code": "def helper(): pass",
                "language": "python",
                "context": "Part of a data processing pipeline",
            },
        )

        assert response.status_code == 200

    def test_explain_endpoint(self, client):
        """Test code explanation endpoint."""
        response = client.post(
            "/v1/llm/explain",
            json={
                "code": "result = [x**2 for x in range(10)]",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "explanation" in data
        assert data["language"] == "python"
        assert data["detail_level"] == "standard"
        assert data["audience"] == "developer"

    def test_explain_endpoint_with_detail_level(self, client):
        """Test explanation with different detail levels."""
        response = client.post(
            "/v1/llm/explain",
            json={
                "code": "x = lambda a, b: a + b",
                "language": "python",
                "detail_level": "detailed",
                "audience": "beginner",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["detail_level"] == "detailed"
        assert data["audience"] == "beginner"

    def test_classify_endpoint(self, client):
        """Test code classification endpoint."""
        response = client.post(
            "/v1/llm/classify",
            json={
                "code": """
class UserRepository:
    def find_by_id(self, id):
        return self.session.query(User).get(id)
""",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "primary_category" in data
        assert "categories" in data
        assert "confidence" in data
        assert isinstance(data["confidence"], float)

    def test_classify_endpoint_returns_categories(self, client):
        """Test that classification returns category list."""
        response = client.post(
            "/v1/llm/classify",
            json={
                "code": "@app.route('/users')\ndef get_users(): pass",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["categories"], list)

    def test_improve_endpoint(self, client):
        """Test code improvement suggestions endpoint."""
        response = client.post(
            "/v1/llm/improve",
            json={
                "code": """
def f(x):
    y = []
    for i in x:
        y.append(i * 2)
    return y
""",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)

    def test_improve_endpoint_suggestion_structure(self, client):
        """Test that suggestions have proper structure."""
        response = client.post(
            "/v1/llm/improve",
            json={
                "code": "def process_data(d):\n    for k in d:\n        print(d[k])",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()

        for suggestion in data["suggestions"]:
            assert "suggestion" in suggestion
            assert "category" in suggestion
            assert "severity" in suggestion
            assert suggestion["category"] in [
                "readability", "performance", "maintainability",
                "security", "naming", "documentation", "best_practices"
            ]
            assert suggestion["severity"] in ["low", "medium", "high"]

    def test_docstring_endpoint(self, client):
        """Test docstring generation endpoint."""
        response = client.post(
            "/v1/llm/docstring",
            json={
                "code": "def calculate_distance(x1, y1, x2, y2):\n    return ((x2-x1)**2 + (y2-y1)**2)**0.5",
                "language": "python",
                "style": "google",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "docstring" in data
        assert data["style"] == "google"

    def test_docstring_endpoint_different_styles(self, client):
        """Test docstring generation with different styles."""
        code = "def add(a, b):\n    return a + b"

        for style in ["google", "numpy", "sphinx"]:
            response = client.post(
                "/v1/llm/docstring",
                json={
                    "code": code,
                    "language": "python",
                    "style": style,
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["style"] == style

    def test_docstring_endpoint_includes_parameters(self, client):
        """Test that docstring includes parameter information."""
        response = client.post(
            "/v1/llm/docstring",
            json={
                "code": "def greet(name, greeting='Hello'):\n    return f'{greeting}, {name}!'",
                "language": "python",
                "style": "google",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "parameters" in data
        assert isinstance(data["parameters"], list)


class TestLLMEndpointsEmptyInput:
    """Tests for LLM endpoints with empty input."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_summarize_empty_code(self, client):
        """Test summarization with empty code."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "code": "",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == ""

    def test_explain_empty_code(self, client):
        """Test explanation with empty code."""
        response = client.post(
            "/v1/llm/explain",
            json={
                "code": "",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["explanation"] == ""

    def test_classify_empty_code(self, client):
        """Test classification with empty code."""
        response = client.post(
            "/v1/llm/classify",
            json={
                "code": "",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["primary_category"] == "unknown"
        assert data["confidence"] == 0.0

    def test_improve_empty_code(self, client):
        """Test improvements with empty code."""
        response = client.post(
            "/v1/llm/improve",
            json={
                "code": "",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["suggestions"] == []

    def test_docstring_empty_code(self, client):
        """Test docstring generation with empty code."""
        response = client.post(
            "/v1/llm/docstring",
            json={
                "code": "",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["docstring"] == ""


class TestLLMEndpointsValidation:
    """Tests for LLM endpoint input validation."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_summarize_missing_code(self, client):
        """Test summarization with missing code field."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "language": "python",
            },
        )

        assert response.status_code == 422

    def test_summarize_missing_language(self, client):
        """Test summarization with missing language field."""
        response = client.post(
            "/v1/llm/summarize",
            json={
                "code": "def f(): pass",
            },
        )

        assert response.status_code == 422

    def test_explain_missing_code(self, client):
        """Test explanation with missing code field."""
        response = client.post(
            "/v1/llm/explain",
            json={
                "language": "python",
            },
        )

        assert response.status_code == 422

    def test_classify_missing_language(self, client):
        """Test classification with missing language field."""
        response = client.post(
            "/v1/llm/classify",
            json={
                "code": "def f(): pass",
            },
        )

        assert response.status_code == 422


class TestLLMFallbackBehavior:
    """Tests for LLM fallback behavior (using heuristics when API unavailable)."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_summarize_fallback_extracts_docstring(self, client):
        """Test that fallback extracts from docstring.

        Patches LITELLM_AVAILABLE to False so the heuristic fallback runs
        deterministically without requiring a real API key.
        """
        with patch("repo_ctx.services.llm.LITELLM_AVAILABLE", False):
            response = client.post(
                "/v1/llm/summarize",
                json={
                    "code": '''
def calculate(x, y):
    """Calculate the sum of two numbers."""
    return x + y
''',
                    "language": "python",
                },
            )

        assert response.status_code == 200
        data = response.json()
        # Fallback should extract docstring content
        assert len(data["summary"]) > 0

    def test_classify_fallback_detects_patterns(self, client):
        """Test that fallback detects code patterns.

        Patches LITELLM_AVAILABLE to False so the heuristic fallback runs
        deterministically without requiring a real API key.
        """
        with patch("repo_ctx.services.llm.LITELLM_AVAILABLE", False):
            response = client.post(
                "/v1/llm/classify",
                json={
                    "code": """
class UserController:
    @app.route('/users')
    def get_users(self):
        pass
""",
                    "language": "python",
                },
            )

        assert response.status_code == 200
        data = response.json()
        # Fallback should detect controller pattern
        assert "controller" in data["categories"] or data["primary_category"] == "controller"

    def test_improve_fallback_detects_issues(self, client):
        """Test that fallback detects common issues."""
        response = client.post(
            "/v1/llm/improve",
            json={
                "code": """
def f(x):
    y = []
    for i in x:
        y.append(i)
    return y
""",
                "language": "python",
            },
        )

        assert response.status_code == 200
        data = response.json()
        # Fallback should detect naming issue (single letter names)
        assert len(data["suggestions"]) > 0
