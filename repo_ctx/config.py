"""Configuration management."""
import os
import re
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel


class Config(BaseModel):
    gitlab_url: str
    gitlab_token: str
    storage_path: str = "./data/context.db"

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables.

        Required environment variables:
        - GITLAB_URL or GIT_CONTEXT_GITLAB_URL
        - GITLAB_TOKEN or GIT_CONTEXT_GITLAB_TOKEN

        Optional:
        - STORAGE_PATH or GIT_CONTEXT_STORAGE_PATH (default: ~/.repo-ctx/context.db)
        """
        gitlab_url = os.getenv("GIT_CONTEXT_GITLAB_URL") or os.getenv("GITLAB_URL")
        gitlab_token = os.getenv("GIT_CONTEXT_GITLAB_TOKEN") or os.getenv("GITLAB_TOKEN")
        storage_path = (
            os.getenv("GIT_CONTEXT_STORAGE_PATH")
            or os.getenv("STORAGE_PATH")
            or os.path.expanduser("~/.repo-ctx/context.db")
        )

        if not gitlab_url:
            raise ValueError("GITLAB_URL or GIT_CONTEXT_GITLAB_URL environment variable must be set")
        if not gitlab_token:
            raise ValueError("GITLAB_TOKEN or GIT_CONTEXT_GITLAB_TOKEN environment variable must be set")

        return cls(
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
            storage_path=storage_path
        )

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "Config":
        """Load config from YAML file with environment variable substitution."""
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(config_path) as f:
            content = f.read()

        # Substitute ${VAR} or $VAR with environment variables
        def replace_env_var(match):
            var_name = match.group(1) or match.group(2)
            value = os.getenv(var_name)
            if value is None:
                raise ValueError(f"Environment variable {var_name} not set")
            return value

        # Replace ${VAR} and $VAR patterns
        content = re.sub(r'\$\{([^}]+)\}|\$([A-Z_][A-Z0-9_]*)', replace_env_var, content)

        data = yaml.safe_load(content)

        return cls(
            gitlab_url=data["gitlab"]["url"],
            gitlab_token=data["gitlab"]["token"],
            storage_path=data.get("storage", {}).get("path", "./data/context.db")
        )

    @classmethod
    def find_config_file(cls) -> Optional[Path]:
        """Find config file in standard locations.

        Checks in order:
        1. ./config.yaml (current directory)
        2. ~/.config/repo-ctx/config.yaml
        3. ~/.repo-ctx/config.yaml

        Returns:
            Path to config file if found, None otherwise
        """
        locations = [
            Path("config.yaml"),
            Path.home() / ".config" / "repo-ctx" / "config.yaml",
            Path.home() / ".repo-ctx" / "config.yaml",
        ]

        for location in locations:
            if location.exists():
                return location

        return None

    @classmethod
    def load(
        cls,
        config_path: Optional[str] = None,
        gitlab_url: Optional[str] = None,
        gitlab_token: Optional[str] = None,
        storage_path: Optional[str] = None,
    ) -> "Config":
        """Load configuration from multiple sources with priority.

        Priority (highest to lowest):
        1. Explicit arguments (gitlab_url, gitlab_token, storage_path)
        2. Specified config file (config_path)
        3. Environment variables
        4. Standard config file locations

        Args:
            config_path: Explicit path to config file
            gitlab_url: GitLab URL (overrides all other sources)
            gitlab_token: GitLab token (overrides all other sources)
            storage_path: Storage path (overrides all other sources)

        Returns:
            Config instance

        Raises:
            ValueError: If no valid configuration source is found
        """
        # If all required params are provided explicitly, use them
        if gitlab_url and gitlab_token:
            return cls(
                gitlab_url=gitlab_url,
                gitlab_token=gitlab_token,
                storage_path=storage_path or os.path.expanduser("~/.repo-ctx/context.db")
            )

        # Try explicit config path
        if config_path:
            try:
                config = cls.from_yaml(config_path)
                # Override with explicit params if provided
                if gitlab_url:
                    config.gitlab_url = gitlab_url
                if gitlab_token:
                    config.gitlab_token = gitlab_token
                if storage_path:
                    config.storage_path = storage_path
                return config
            except FileNotFoundError:
                raise
            except Exception as e:
                raise ValueError(f"Error loading config from {config_path}: {e}")

        # Try environment variables
        try:
            config = cls.from_env()
            # Override with explicit params if provided
            if gitlab_url:
                config.gitlab_url = gitlab_url
            if gitlab_token:
                config.gitlab_token = gitlab_token
            if storage_path:
                config.storage_path = storage_path
            return config
        except ValueError:
            pass  # Environment variables not set, try config file

        # Try standard config file locations
        config_file = cls.find_config_file()
        if config_file:
            try:
                config = cls.from_yaml(str(config_file))
                # Override with explicit params if provided
                if gitlab_url:
                    config.gitlab_url = gitlab_url
                if gitlab_token:
                    config.gitlab_token = gitlab_token
                if storage_path:
                    config.storage_path = storage_path
                return config
            except Exception as e:
                raise ValueError(f"Error loading config from {config_file}: {e}")

        # No valid config found
        raise ValueError(
            "No configuration found. Please either:\n"
            "1. Set environment variables: GITLAB_URL and GITLAB_TOKEN\n"
            "2. Create a config.yaml file in:\n"
            "   - Current directory\n"
            "   - ~/.config/repo-ctx/config.yaml\n"
            "   - ~/.repo-ctx/config.yaml\n"
            "3. Use --config to specify config file path\n"
            "4. Use --gitlab-url and --gitlab-token arguments"
        )
