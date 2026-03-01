"""Tests for API authentication and authorization.

These tests verify:
- API key authentication
- Local access without auth
- Rate limiting
- Auth endpoints
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestAuthModule:
    """Tests for auth module functions."""

    def test_configure_auth_with_key(self):
        """Test configuring auth with API key."""
        from repo_ctx.api.auth import configure_auth, get_auth_config

        configure_auth(api_key="test-key-123")
        config = get_auth_config()

        assert config.api_key == "test-key-123"
        assert config.api_key_hash is not None

    def test_configure_auth_without_key(self):
        """Test configuring auth without API key."""
        from repo_ctx.api.auth import configure_auth, get_auth_config

        configure_auth(api_key=None)
        config = get_auth_config()

        assert config.api_key is None
        assert config.api_key_hash is None

    def test_hash_key(self):
        """Test API key hashing."""
        from repo_ctx.api.auth import _hash_key

        hash1 = _hash_key("test-key")
        hash2 = _hash_key("test-key")
        hash3 = _hash_key("different-key")

        assert hash1 == hash2
        assert hash1 != hash3
        assert len(hash1) == 64  # SHA-256 hex

    def test_generate_api_key(self):
        """Test API key generation."""
        from repo_ctx.api.auth import generate_api_key

        key1 = generate_api_key()
        key2 = generate_api_key()

        assert key1.startswith("rctx_")
        assert key2.startswith("rctx_")
        assert key1 != key2
        assert len(key1) > 20

    def test_rate_limit_tracking(self):
        """Test rate limit tracking."""
        from repo_ctx.api.auth import (
            configure_auth,
            _check_rate_limit,
            reset_rate_limits,
        )

        configure_auth(rate_limit_enabled=True, rate_limit_requests=5, rate_limit_window=60)
        reset_rate_limits()

        # Should allow first 5 requests
        for i in range(5):
            allowed, remaining = _check_rate_limit("test-ip")
            assert allowed is True
            assert remaining == 4 - i

        # 6th request should be blocked
        allowed, remaining = _check_rate_limit("test-ip")
        assert allowed is False
        assert remaining == 0

    def test_rate_limit_disabled(self):
        """Test rate limiting when disabled."""
        from repo_ctx.api.auth import configure_auth, _check_rate_limit, reset_rate_limits

        configure_auth(rate_limit_enabled=False)
        reset_rate_limits()

        # Should always allow
        for _ in range(100):
            allowed, remaining = _check_rate_limit("test-ip")
            assert allowed is True


class TestAuthEndpoints:
    """Tests for auth endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        # Reset auth state
        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    @pytest.fixture
    def client_with_auth(self):
        """Create test client with auth enabled."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key="test-api-key", rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_auth_status_endpoint_in_openapi(self, client):
        """Test that /v1/auth/status is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/auth/status" in data["paths"]

    def test_auth_config_endpoint_in_openapi(self, client):
        """Test that /v1/auth/config is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/auth/config" in data["paths"]

    def test_auth_verify_endpoint_in_openapi(self, client):
        """Test that /v1/auth/verify is in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()
        assert "/v1/auth/verify" in data["paths"]

    def test_auth_status_no_auth(self, client):
        """Test auth status when auth is not configured."""
        response = client.get("/v1/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert "authenticated" in data
        assert "is_local" in data
        assert "auth_required" in data
        assert data["auth_required"] is False

    def test_auth_config_no_auth(self, client):
        """Test auth config when auth is not configured."""
        response = client.get("/v1/auth/config")
        assert response.status_code == 200
        data = response.json()
        assert data["auth_enabled"] is False

    def test_auth_config_with_auth(self, client_with_auth):
        """Test auth config when auth is configured."""
        response = client_with_auth.get("/v1/auth/config")
        assert response.status_code == 200
        data = response.json()
        assert data["auth_enabled"] is True

    def test_auth_verify_requires_key_from_non_local(self, client_with_auth):
        """Test verify endpoint requires key from non-local (TestClient uses 'testclient' host)."""
        # TestClient uses "testclient" as host, which is not in local_origins
        # So it should require API key
        response = client_with_auth.get("/v1/auth/verify")
        assert response.status_code == 401  # Requires API key

    def test_auth_verify_with_valid_key(self, client_with_auth):
        """Test verify endpoint with valid API key."""
        response = client_with_auth.get(
            "/v1/auth/verify",
            headers={"X-API-Key": "test-api-key"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"

    def test_auth_verify_with_invalid_key(self):
        """Test verify endpoint with invalid API key from remote."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(api_key="correct-key", require_auth_always=True, rate_limit_enabled=False)
        reset_rate_limits()

        client = TestClient(app)
        response = client.get(
            "/v1/auth/verify",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401

    def test_generate_key_local(self, client):
        """Test generate key endpoint from local."""
        response = client.post("/v1/auth/generate-key")
        assert response.status_code == 200
        data = response.json()
        assert "api_key" in data
        assert data["api_key"].startswith("rctx_")


class TestRateLimitingMiddleware:
    """Tests for rate limiting middleware."""

    @pytest.fixture
    def client_rate_limited(self):
        """Create test client with rate limiting."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits

        configure_auth(
            api_key=None,
            rate_limit_enabled=True,
            rate_limit_requests=3,
            rate_limit_window=60,
        )
        reset_rate_limits()

        return TestClient(app)

    def test_rate_limit_headers(self, client_rate_limited):
        """Test that rate limit headers are included."""
        response = client_rate_limited.get("/health")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Window" in response.headers


class TestSecurityMiddleware:
    """Tests for security middleware."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth

        configure_auth(api_key=None, rate_limit_enabled=False)
        return TestClient(app)

    def test_security_headers(self, client):
        """Test that security headers are included."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers

    def test_response_time_header(self, client):
        """Test that response time header is included."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Response-Time" in response.headers
        assert "ms" in response.headers["X-Response-Time"]


class TestLocalVsRemoteAccess:
    """Tests for local vs remote access detection."""

    def test_is_local_request_localhost(self):
        """Test local detection for localhost."""
        from repo_ctx.api.auth import _is_local_request

        mock_request = MagicMock()
        mock_request.client.host = "127.0.0.1"

        result = _is_local_request(mock_request)
        assert result is True

    def test_is_local_request_ipv6_localhost(self):
        """Test local detection for IPv6 localhost."""
        from repo_ctx.api.auth import _is_local_request

        mock_request = MagicMock()
        mock_request.client.host = "::1"

        result = _is_local_request(mock_request)
        assert result is True

    def test_is_local_request_remote(self):
        """Test local detection for remote IP."""
        from repo_ctx.api.auth import _is_local_request

        mock_request = MagicMock()
        mock_request.client.host = "192.168.1.100"

        result = _is_local_request(mock_request)
        assert result is False

    def test_is_local_request_no_client(self):
        """Test local detection when no client."""
        from repo_ctx.api.auth import _is_local_request

        mock_request = MagicMock()
        mock_request.client = None

        result = _is_local_request(mock_request)
        assert result is False
