"""Tests for configuration management."""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
from repo_ctx.config import Config


class TestConfigFromEnv:
    """Test loading configuration from environment variables."""

    def test_from_env_success(self):
        """Test loading config from environment variables."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.example.com',
            'GITLAB_TOKEN': 'glpat-test-token-123'
        }):
            config = Config.from_env()
            assert config.gitlab_url == 'https://gitlab.example.com'
            assert config.gitlab_token == 'glpat-test-token-123'
            assert config.storage_path == os.path.expanduser("~/.repo-ctx/context.db")

    def test_from_env_with_git_context_prefix(self):
        """Test loading from GIT_CONTEXT_* prefixed variables."""
        with patch.dict(os.environ, {
            'GIT_CONTEXT_GITLAB_URL': 'https://gitlab.custom.com',
            'GIT_CONTEXT_GITLAB_TOKEN': 'custom-token'
        }, clear=True):
            config = Config.from_env()
            assert config.gitlab_url == 'https://gitlab.custom.com'
            assert config.gitlab_token == 'custom-token'

    def test_from_env_priority_git_context_over_plain(self):
        """Test GIT_CONTEXT_* variables take priority over plain ones."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://plain.example.com',
            'GITLAB_TOKEN': 'plain-token',
            'GIT_CONTEXT_GITLAB_URL': 'https://prefixed.example.com',
            'GIT_CONTEXT_GITLAB_TOKEN': 'prefixed-token'
        }):
            config = Config.from_env()
            assert config.gitlab_url == 'https://prefixed.example.com'
            assert config.gitlab_token == 'prefixed-token'

    def test_from_env_custom_storage_path(self):
        """Test loading custom storage path from environment."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.example.com',
            'GITLAB_TOKEN': 'token',
            'STORAGE_PATH': '/custom/path/context.db'
        }):
            config = Config.from_env()
            assert config.storage_path == '/custom/path/context.db'

    def test_from_env_git_context_storage_path_priority(self):
        """Test GIT_CONTEXT_STORAGE_PATH takes priority."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.example.com',
            'GITLAB_TOKEN': 'token',
            'STORAGE_PATH': '/plain/path.db',
            'GIT_CONTEXT_STORAGE_PATH': '/prefixed/path.db'
        }):
            config = Config.from_env()
            assert config.storage_path == '/prefixed/path.db'

    def test_from_env_missing_url(self):
        """Test error when no provider is configured (only GitLab token)."""
        with patch.dict(os.environ, {
            'GITLAB_TOKEN': 'token'
        }, clear=True):
            with pytest.raises(ValueError, match="At least one provider must be configured"):
                Config.from_env()

    def test_from_env_missing_token(self):
        """Test GitLab URL alone is not enough (need token too or GitHub)."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://gitlab.example.com'
        }, clear=True):
            with pytest.raises(ValueError, match="At least one provider must be configured"):
                Config.from_env()

    def test_from_env_both_missing(self):
        """Test error when both URL and token are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Config.from_env()


class TestConfigFromYaml:
    """Test loading configuration from YAML files."""

    def test_from_yaml_success(self, tmp_path):
        """Test loading config from YAML file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://gitlab.example.com"
  token: "yaml-token-123"
storage:
  path: "/data/context.db"
""")

        config = Config.from_yaml(str(config_file))
        assert config.gitlab_url == "https://gitlab.example.com"
        assert config.gitlab_token == "yaml-token-123"
        assert config.storage_path == "/data/context.db"

    def test_from_yaml_default_storage_path(self, tmp_path):
        """Test YAML with missing storage path uses default."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://gitlab.example.com"
  token: "token"
""")

        config = Config.from_yaml(str(config_file))
        assert config.storage_path == "./data/context.db"

    def test_from_yaml_env_var_substitution(self, tmp_path):
        """Test environment variable substitution in YAML."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://gitlab.example.com"
  token: "${GITLAB_TOKEN}"
""")

        with patch.dict(os.environ, {'GITLAB_TOKEN': 'env-token-456'}):
            config = Config.from_yaml(str(config_file))
            assert config.gitlab_token == "env-token-456"

    def test_from_yaml_env_var_substitution_dollar_var(self, tmp_path):
        """Test $VAR style environment variable substitution."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://gitlab.example.com"
  token: $GITLAB_TOKEN
""")

        with patch.dict(os.environ, {'GITLAB_TOKEN': 'dollar-var-token'}):
            config = Config.from_yaml(str(config_file))
            assert config.gitlab_token == "dollar-var-token"

    def test_from_yaml_env_var_not_set(self, tmp_path):
        """Test error when referenced environment variable is not set."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://gitlab.example.com"
  token: "${NONEXISTENT_VAR}"
""")

        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Environment variable NONEXISTENT_VAR not set"):
                Config.from_yaml(str(config_file))

    def test_from_yaml_file_not_found(self):
        """Test error when YAML file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("/nonexistent/config.yaml")

    def test_from_yaml_invalid_yaml(self, tmp_path):
        """Test error with invalid YAML syntax."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content: [")

        with pytest.raises(Exception):  # yaml.safe_load will raise an exception
            Config.from_yaml(str(config_file))


class TestConfigFindConfigFile:
    """Test finding configuration files in standard locations."""

    def test_find_config_file_current_directory(self, tmp_path, monkeypatch):
        """Test finding config.yaml in current directory."""
        monkeypatch.chdir(tmp_path)
        config_file = tmp_path / "config.yaml"
        config_file.write_text("test")

        found = Config.find_config_file()
        assert found == Path("config.yaml")

    def test_find_config_file_user_config(self, tmp_path, monkeypatch):
        """Test finding config in ~/.config/repo-ctx/."""
        # Mock Path.home() to return tmp_path
        with patch('repo_ctx.config.Path.home', return_value=tmp_path):
            config_dir = tmp_path / ".config" / "repo-ctx"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "config.yaml"
            config_file.write_text("test")

            found = Config.find_config_file()
            assert found == config_dir / "config.yaml"

    def test_find_config_file_user_repo_ctx(self, tmp_path):
        """Test finding config in ~/.repo-ctx/."""
        with patch('repo_ctx.config.Path.home', return_value=tmp_path):
            config_dir = tmp_path / ".repo-ctx"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "config.yaml"
            config_file.write_text("test")

            found = Config.find_config_file()
            assert found == config_dir / "config.yaml"

    def test_find_config_file_not_found(self):
        """Test return None when no config file found."""
        with patch('repo_ctx.config.Path.home', return_value=Path("/nonexistent")):
            with patch('pathlib.Path.exists', return_value=False):
                found = Config.find_config_file()
                assert found is None


class TestConfigLoad:
    """Test the unified load() method with priority handling."""

    def test_load_with_explicit_url_and_token(self):
        """Test explicit arguments have highest priority."""
        config = Config.load(
            gitlab_url="https://explicit.example.com",
            gitlab_token="explicit-token"
        )
        assert config.gitlab_url == "https://explicit.example.com"
        assert config.gitlab_token == "explicit-token"

    def test_load_with_explicit_storage_path(self):
        """Test explicit storage path."""
        config = Config.load(
            gitlab_url="https://example.com",
            gitlab_token="token",
            storage_path="/explicit/path.db"
        )
        assert config.storage_path == "/explicit/path.db"

    def test_load_from_explicit_config_file(self, tmp_path):
        """Test loading from explicitly specified config file."""
        config_file = tmp_path / "custom-config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://yaml.example.com"
  token: "yaml-token"
""")

        config = Config.load(config_path=str(config_file))
        assert config.gitlab_url == "https://yaml.example.com"
        assert config.gitlab_token == "yaml-token"

    def test_load_explicit_args_override_config_file(self, tmp_path):
        """Test explicit arguments override config file values."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
gitlab:
  url: "https://yaml.example.com"
  token: "yaml-token"
""")

        config = Config.load(
            config_path=str(config_file),
            gitlab_url="https://override.example.com"
        )
        assert config.gitlab_url == "https://override.example.com"
        assert config.gitlab_token == "yaml-token"  # From file

    def test_load_from_environment(self):
        """Test loading from environment variables when no explicit args."""
        with patch.dict(os.environ, {
            'GITLAB_URL': 'https://env.example.com',
            'GITLAB_TOKEN': 'env-token'
        }):
            config = Config.load()
            assert config.gitlab_url == 'https://env.example.com'
            assert config.gitlab_token == 'env-token'

    def test_load_from_standard_config_file(self, tmp_path):
        """Test loading from standard config file location."""
        with patch('repo_ctx.config.Path.home', return_value=tmp_path):
            config_dir = tmp_path / ".config" / "repo-ctx"
            config_dir.mkdir(parents=True)
            config_file = config_dir / "config.yaml"
            config_file.write_text("""
gitlab:
  url: "https://standard.example.com"
  token: "standard-token"
""")

            with patch.dict(os.environ, {}, clear=True):
                config = Config.load()
                assert config.gitlab_url == "https://standard.example.com"
                assert config.gitlab_token == "standard-token"

    def test_load_no_valid_config_found(self):
        """Test error when no configuration source is available."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('repo_ctx.config.Config.find_config_file', return_value=None):
                with pytest.raises(ValueError, match="No configuration found"):
                    Config.load()

    def test_load_config_file_not_found_error(self):
        """Test error when explicitly specified config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            Config.load(config_path="/nonexistent/config.yaml")

    def test_load_invalid_config_file_error(self, tmp_path):
        """Test error when config file is invalid."""
        config_file = tmp_path / "invalid.yaml"
        config_file.write_text("invalid yaml content [[[")

        with pytest.raises(ValueError, match="Error loading config"):
            Config.load(config_path=str(config_file))


class TestConfigModel:
    """Test the Config Pydantic model itself."""

    def test_config_creation_direct(self):
        """Test creating Config instance directly."""
        config = Config(
            gitlab_url="https://gitlab.com",
            gitlab_token="token",
            storage_path="/path/to/db"
        )
        assert config.gitlab_url == "https://gitlab.com"
        assert config.gitlab_token == "token"
        assert config.storage_path == "/path/to/db"

    def test_config_default_storage_path(self):
        """Test default storage path when not specified."""
        config = Config(
            gitlab_url="https://gitlab.com",
            gitlab_token="token"
        )
        assert config.storage_path == "./data/context.db"

    def test_config_validation(self):
        """Test Config can be created with partial provider config."""
        # Now that providers are optional, Config can be created with partial info
        # Provider initialization will fail, but Config object is valid
        config = Config(gitlab_url="url")  # This is now valid
        assert config.gitlab_url == "url"
        assert config.gitlab_token is None  # Optional field
