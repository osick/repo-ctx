"""Tests for v2 configuration enhancements.

These tests verify the new configuration options for:
- Vector DB (Qdrant)
- Graph DB (Neo4j)
- GenAI (LLM settings)
"""

import os
import pytest
import tempfile
from pathlib import Path


class TestQdrantConfig:
    """Tests for Qdrant vector DB configuration."""

    def test_qdrant_config_exists(self):
        """QdrantConfig class should exist."""
        from repo_ctx.config import QdrantConfig

        assert QdrantConfig is not None

    def test_qdrant_config_defaults(self):
        """QdrantConfig should have sensible defaults."""
        from repo_ctx.config import QdrantConfig

        config = QdrantConfig()
        assert config.url == ":memory:"
        assert config.api_key is None
        assert config.collection_prefix == "repo_ctx"

    def test_qdrant_config_custom_values(self):
        """QdrantConfig should accept custom values."""
        from repo_ctx.config import QdrantConfig

        config = QdrantConfig(
            url="http://localhost:6333",
            api_key="test-key",
            collection_prefix="myapp",
        )
        assert config.url == "http://localhost:6333"
        assert config.api_key == "test-key"
        assert config.collection_prefix == "myapp"


class TestNeo4jConfig:
    """Tests for Neo4j graph DB configuration."""

    def test_neo4j_config_exists(self):
        """Neo4jConfig class should exist."""
        from repo_ctx.config import Neo4jConfig

        assert Neo4jConfig is not None

    def test_neo4j_config_defaults(self):
        """Neo4jConfig should have sensible defaults."""
        from repo_ctx.config import Neo4jConfig

        config = Neo4jConfig()
        assert config.uri == "bolt://localhost:7687"
        assert config.username == "neo4j"
        assert config.password is None
        assert config.database == "neo4j"
        assert config.in_memory is True  # Default to in-memory for safety

    def test_neo4j_config_custom_values(self):
        """Neo4jConfig should accept custom values."""
        from repo_ctx.config import Neo4jConfig

        config = Neo4jConfig(
            uri="bolt://graph.example.com:7687",
            username="admin",
            password="secret123",
            database="mydb",
            in_memory=False,
        )
        assert config.uri == "bolt://graph.example.com:7687"
        assert config.username == "admin"
        assert config.password == "secret123"
        assert config.database == "mydb"
        assert config.in_memory is False


class TestGenAIConfig:
    """Tests for GenAI/LLM configuration."""

    def test_genai_config_exists(self):
        """GenAIConfig class should exist."""
        from repo_ctx.config import GenAIConfig

        assert GenAIConfig is not None

    def test_genai_config_defaults(self):
        """GenAIConfig should have sensible defaults."""
        from repo_ctx.config import GenAIConfig

        config = GenAIConfig()
        assert config.model is None  # No default model
        assert config.embedding_model is None
        assert config.api_key is None
        assert config.base_url is None
        assert config.enabled is False  # Disabled by default

    def test_genai_config_custom_values(self):
        """GenAIConfig should accept custom values."""
        from repo_ctx.config import GenAIConfig

        config = GenAIConfig(
            model="gpt-5-mini",
            embedding_model="text-embedding-ada-002",
            api_key="sk-test123",
            base_url="https://api.openai.com/v1",
            enabled=True,
        )
        assert config.model == "gpt-5-mini"
        assert config.embedding_model == "text-embedding-ada-002"
        assert config.api_key == "sk-test123"
        assert config.base_url == "https://api.openai.com/v1"
        assert config.enabled is True


class TestStorageConfig:
    """Tests for unified StorageConfig."""

    def test_storage_config_exists(self):
        """StorageConfig class should exist."""
        from repo_ctx.config import StorageConfig

        assert StorageConfig is not None

    def test_storage_config_defaults(self):
        """StorageConfig should have defaults for all DBs."""
        from repo_ctx.config import StorageConfig

        config = StorageConfig()
        assert config.content_db_path is not None
        assert config.qdrant is not None
        assert config.neo4j is not None

    def test_storage_config_content_db_path(self):
        """StorageConfig should have content_db_path."""
        from repo_ctx.config import StorageConfig

        config = StorageConfig(content_db_path="/custom/path/context.db")
        assert config.content_db_path == "/custom/path/context.db"


class TestConfigV2Integration:
    """Tests for Config class v2 integration."""

    def test_config_has_storage(self):
        """Config should have storage attribute."""
        from repo_ctx.config import Config

        config = Config()
        assert hasattr(config, "storage") or hasattr(config, "storage_path")

    def test_config_has_genai(self):
        """Config should have genai attribute."""
        from repo_ctx.config import Config

        config = Config()
        assert hasattr(config, "genai")

    def test_config_genai_defaults(self):
        """Config genai should have defaults."""
        from repo_ctx.config import Config

        config = Config()
        if hasattr(config, "genai") and config.genai is not None:
            assert config.genai.enabled is False


class TestConfigFromEnvV2:
    """Tests for loading v2 config from environment."""

    def test_qdrant_from_env(self):
        """QdrantConfig should load from environment variables."""
        from repo_ctx.config import QdrantConfig

        os.environ["QDRANT_URL"] = "http://qdrant.example.com:6333"
        os.environ["QDRANT_API_KEY"] = "env-api-key"
        try:
            config = QdrantConfig.from_env()
            assert config.url == "http://qdrant.example.com:6333"
            assert config.api_key == "env-api-key"
        finally:
            os.environ.pop("QDRANT_URL", None)
            os.environ.pop("QDRANT_API_KEY", None)

    def test_neo4j_from_env(self):
        """Neo4jConfig should load from environment variables."""
        from repo_ctx.config import Neo4jConfig

        os.environ["NEO4J_URI"] = "bolt://neo4j.example.com:7687"
        os.environ["NEO4J_USERNAME"] = "testuser"
        os.environ["NEO4J_PASSWORD"] = "testpass"
        try:
            config = Neo4jConfig.from_env()
            assert config.uri == "bolt://neo4j.example.com:7687"
            assert config.username == "testuser"
            assert config.password == "testpass"
        finally:
            os.environ.pop("NEO4J_URI", None)
            os.environ.pop("NEO4J_USERNAME", None)
            os.environ.pop("NEO4J_PASSWORD", None)

    def test_genai_from_env(self):
        """GenAIConfig should load from environment variables."""
        from repo_ctx.config import GenAIConfig

        os.environ["GENAI_MODEL"] = "claude-3-opus"
        os.environ["GENAI_API_KEY"] = "sk-test"
        os.environ["GENAI_ENABLED"] = "true"
        try:
            config = GenAIConfig.from_env()
            assert config.model == "claude-3-opus"
            assert config.api_key == "sk-test"
            assert config.enabled is True
        finally:
            os.environ.pop("GENAI_MODEL", None)
            os.environ.pop("GENAI_API_KEY", None)
            os.environ.pop("GENAI_ENABLED", None)


class TestConfigFromYamlV2:
    """Tests for loading v2 config from YAML."""

    def test_full_config_from_yaml(self):
        """Full v2 config should load from YAML."""
        from repo_ctx.config import Config

        yaml_content = """
gitlab:
  url: "https://gitlab.example.com"
  token: "test-token"

storage:
  content_db: "~/.repo-ctx/context.db"
  qdrant:
    url: "http://localhost:6333"
    api_key: null
    collection_prefix: "repo_ctx"
  neo4j:
    uri: "bolt://localhost:7687"
    username: "neo4j"
    password: null
    database: "neo4j"
    in_memory: true

genai:
  enabled: false
  model: null
  embedding_model: null
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                config = Config.from_yaml(f.name)
                assert config.gitlab_url == "https://gitlab.example.com"
                assert config.gitlab_token == "test-token"
                # Check storage config if implemented
                if hasattr(config, "storage") and config.storage is not None:
                    assert config.storage.qdrant is not None
            finally:
                os.unlink(f.name)
