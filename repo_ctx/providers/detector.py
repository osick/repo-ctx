"""Provider detection from repository paths."""
from typing import Optional


class ProviderDetector:
    """Detect provider type from repository path."""

    @staticmethod
    def detect(path: str, default: Optional[str] = None) -> str:
        """
        Detect provider from path format.

        Examples:
            "owner/repo" -> "github" (2 parts, typical GitHub format)
            "group/subgroup/project" -> "gitlab" (3+ parts)
            "/absolute/path" -> "local"
            "./relative/path" -> "local"
            "../path" -> "local"
            "~/path" -> "local"
            "pypi:package" -> "pypi" (future)

        Args:
            path: Repository path to analyze
            default: Default provider if detection is ambiguous

        Returns:
            Provider type: "gitlab", "github", "local", etc.

        Raises:
            ValueError: Cannot detect provider from path

        Note:
            For ambiguous cases (owner/repo could be GitLab or GitHub),
            the default provider is used if provided, otherwise "github" is assumed.
        """
        # Handle explicit protocol prefixes
        if "://" in path:
            protocol = path.split("://")[0]
            return protocol  # gitlab://, github://, local://, etc.

        # Local filesystem paths
        if path.startswith("/") or path.startswith("~"):
            return "local"
        if path.startswith("."):
            return "local"

        # Git-style paths
        parts = path.split("/")

        # Single part is invalid
        if len(parts) == 1:
            raise ValueError(
                f"Cannot detect provider from path: {path}. "
                f"Expected format: owner/repo, group/project, or /path/to/repo"
            )

        # Two parts: owner/repo (typically GitHub)
        if len(parts) == 2:
            # Could be GitLab or GitHub, use default or assume GitHub
            if default:
                return default
            return "github"

        # Three or more parts: group/subgroup/project (typically GitLab)
        if len(parts) >= 3:
            return "gitlab"

        # Fallback to default or error
        if default:
            return default

        raise ValueError(f"Cannot detect provider from path: {path}")

    @staticmethod
    def normalize_path(path: str, provider: str) -> str:
        """
        Normalize path for given provider.

        Removes protocol prefixes and ensures correct format.

        Args:
            path: Repository path (may include protocol)
            provider: Provider type

        Returns:
            Normalized path without protocol

        Examples:
            gitlab://group/project -> group/project
            github://owner/repo -> owner/repo
            local:///path/to/repo -> /path/to/repo
        """
        # Remove protocol if present
        if "://" in path:
            protocol, rest = path.split("://", 1)
            return rest

        return path

    @staticmethod
    def to_library_id(path: str, provider: str) -> str:
        """
        Convert path and provider to library_id URI format.

        Args:
            path: Repository path
            provider: Provider type

        Returns:
            Library ID in URI format

        Examples:
            ("group/project", "gitlab") -> "gitlab://group/project"
            ("owner/repo", "github") -> "github://owner/repo"
            ("/path/to/repo", "local") -> "local:///path/to/repo"
        """
        normalized = ProviderDetector.normalize_path(path, provider)

        if provider == "local":
            # Ensure absolute path starts with /
            if not normalized.startswith("/"):
                raise ValueError(f"Local paths must be absolute: {normalized}")
            return f"local://{normalized}"

        return f"{provider}://{normalized}"

    @staticmethod
    def from_library_id(library_id: str) -> tuple[str, str]:
        """
        Parse library_id URI into provider and path.

        Args:
            library_id: Library ID in URI format

        Returns:
            Tuple of (provider, path)

        Examples:
            "gitlab://group/project" -> ("gitlab", "group/project")
            "github://owner/repo" -> ("github", "owner/repo")
            "local:///path/to/repo" -> ("local", "/path/to/repo")

        Raises:
            ValueError: Invalid library_id format
        """
        if "://" not in library_id:
            raise ValueError(f"Invalid library_id format: {library_id}")

        provider, path = library_id.split("://", 1)

        return provider, path
