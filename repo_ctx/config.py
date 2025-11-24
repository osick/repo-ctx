"""Configuration management."""
import os
import re
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel


class Config(BaseModel):
    # GitLab (optional now - for multi-provider support)
    gitlab_url: Optional[str] = None
    gitlab_token: Optional[str] = None

    # GitHub (optional)
    github_url: Optional[str] = None
    github_token: Optional[str] = None

    # Storage
    storage_path: str = "./data/context.db"

    @classmethod
    def from_env(cls) -> "Config":
        """Load config from environment variables.

        Supported environment variables:
        GitLab:
        - GITLAB_URL or GIT_CONTEXT_GITLAB_URL
        - GITLAB_TOKEN or GIT_CONTEXT_GITLAB_TOKEN

        GitHub:
        - GITHUB_URL or GIT_CONTEXT_GITHUB_URL (default: https://api.github.com)
        - GITHUB_TOKEN or GIT_CONTEXT_GITHUB_TOKEN (optional for public repos)

        Storage:
        - STORAGE_PATH or GIT_CONTEXT_STORAGE_PATH (default: ~/.repo-ctx/context.db)

        At least one provider (GitLab or GitHub) must be configured.
        """
        # GitLab
        gitlab_url = os.getenv("GIT_CONTEXT_GITLAB_URL") or os.getenv("GITLAB_URL")
        gitlab_token = os.getenv("GIT_CONTEXT_GITLAB_TOKEN") or os.getenv("GITLAB_TOKEN")

        # GitHub
        github_url = os.getenv("GIT_CONTEXT_GITHUB_URL") or os.getenv("GITHUB_URL")
        github_token = os.getenv("GIT_CONTEXT_GITHUB_TOKEN") or os.getenv("GITHUB_TOKEN")

        # Default GitHub URL if token is provided but URL is not
        if github_token and not github_url:
            github_url = "https://api.github.com"

        # Storage
        storage_path = (
            os.getenv("GIT_CONTEXT_STORAGE_PATH")
            or os.getenv("STORAGE_PATH")
            or os.path.expanduser("~/.repo-ctx/context.db")
        )

        # Validate at least one provider is configured
        if not (gitlab_url and gitlab_token) and not github_url:
            raise ValueError(
                "At least one provider must be configured.\n"
                "GitLab: Set GITLAB_URL and GITLAB_TOKEN\n"
                "GitHub: Set GITHUB_URL (optional) and/or GITHUB_TOKEN\n"
                "Or set GIT_CONTEXT_* prefixed versions"
            )

        return cls(
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
            github_url=github_url,
            github_token=github_token,
            storage_path=storage_path
        )

    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "Config":
        """Load config from YAML file with environment variable substitution.

        Example config.yaml:
        ```yaml
        gitlab:
          url: "https://gitlab.company.com"
          token: "${GITLAB_TOKEN}"

        github:
          url: "https://api.github.com"  # Optional, defaults to public GitHub
          token: "${GITHUB_TOKEN}"        # Optional for public repos

        storage:
          path: "~/.repo-ctx/context.db"
        ```
        """
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

        # Extract GitLab config
        gitlab_url = None
        gitlab_token = None
        if "gitlab" in data:
            gitlab_url = data["gitlab"].get("url")
            gitlab_token = data["gitlab"].get("token")

        # Extract GitHub config
        github_url = None
        github_token = None
        if "github" in data:
            github_url = data["github"].get("url")
            github_token = data["github"].get("token")
            # Default GitHub URL
            if github_token and not github_url:
                github_url = "https://api.github.com"

        # Extract storage path
        storage_path = data.get("storage", {}).get("path", "./data/context.db")

        # Validate at least one provider
        if not (gitlab_url and gitlab_token) and not github_url:
            raise ValueError(
                "Config file must specify at least one provider (gitlab or github)"
            )

        return cls(
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
            github_url=github_url,
            github_token=github_token,
            storage_path=storage_path
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
        github_url: Optional[str] = None,
        github_token: Optional[str] = None,
        storage_path: Optional[str] = None,
    ) -> "Config":
        """Load configuration from multiple sources with priority.

        Priority (highest to lowest):
        1. Explicit arguments
        2. Specified config file (config_path)
        3. Environment variables
        4. Standard config file locations

        Args:
            config_path: Explicit path to config file
            gitlab_url: GitLab URL (overrides all other sources)
            gitlab_token: GitLab token (overrides all other sources)
            github_url: GitHub URL (overrides all other sources)
            github_token: GitHub token (overrides all other sources)
            storage_path: Storage path (overrides all other sources)

        Returns:
            Config instance

        Raises:
            ValueError: If no valid configuration source is found
        """
        # If any provider is explicitly configured, use explicit params
        has_gitlab = gitlab_url and gitlab_token
        has_github = github_url or github_token

        if has_gitlab or has_github:
            # Default GitHub URL if not provided
            if github_token and not github_url:
                github_url = "https://api.github.com"

            return cls(
                gitlab_url=gitlab_url,
                gitlab_token=gitlab_token,
                github_url=github_url,
                github_token=github_token,
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
                if github_url:
                    config.github_url = github_url
                if github_token:
                    config.github_token = github_token
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
            if github_url:
                config.github_url = github_url
            if github_token:
                config.github_token = github_token
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
                if github_url:
                    config.github_url = github_url
                if github_token:
                    config.github_token = github_token
                if storage_path:
                    config.storage_path = storage_path
                return config
            except Exception as e:
                raise ValueError(f"Error loading config from {config_file}: {e}")

        # No valid config found
        raise ValueError(
            "No configuration found. Please configure at least one provider:\n\n"
            "Option 1: Environment variables\n"
            "  GitLab: GITLAB_URL and GITLAB_TOKEN\n"
            "  GitHub: GITHUB_URL (optional) and GITHUB_TOKEN\n\n"
            "Option 2: Config file in:\n"
            "  - Current directory (config.yaml)\n"
            "  - ~/.config/repo-ctx/config.yaml\n"
            "  - ~/.repo-ctx/config.yaml\n\n"
            "Option 3: Command-line arguments\n"
            "  --gitlab-url --gitlab-token\n"
            "  --github-url --github-token\n\n"
            "Option 4: Use --config to specify config file path"
        )
