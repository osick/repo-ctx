"""Abstract base class for repository providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class ProviderProject:
    """Normalized project representation across providers."""
    id: str
    name: str
    path: str
    description: Optional[str]
    default_branch: str
    web_url: Optional[str]


@dataclass
class ProviderFile:
    """Normalized file representation."""
    path: str
    content: str
    size: int


class GitProvider(ABC):
    """Abstract base class for all repository providers."""

    @abstractmethod
    async def get_project(self, path: str) -> ProviderProject:
        """
        Get project metadata.

        Args:
            path: Provider-specific project identifier
                  GitLab: "group/project" or "group/subgroup/project"
                  GitHub: "owner/repo"
                  Local: "/absolute/path" or "./relative/path"

        Returns:
            ProviderProject with normalized metadata

        Raises:
            ProviderNotFoundError: Project doesn't exist
            ProviderAuthError: Authentication failed
        """
        pass

    @abstractmethod
    async def get_default_branch(self, project: ProviderProject) -> str:
        """
        Get default branch name (main, master, etc.).

        Args:
            project: Project to query

        Returns:
            Default branch name

        Raises:
            ProviderError: Error getting branch information
        """
        pass

    @abstractmethod
    async def get_file_tree(
        self,
        project: ProviderProject,
        ref: str,
        recursive: bool = True
    ) -> List[str]:
        """
        Get list of all file paths in repository.

        Args:
            project: Project to query
            ref: Branch, tag, or commit SHA
            recursive: Include subdirectories

        Returns:
            List of file paths relative to repo root

        Raises:
            ProviderError: Error accessing file tree
        """
        pass

    @abstractmethod
    async def read_file(
        self,
        project: ProviderProject,
        path: str,
        ref: str
    ) -> ProviderFile:
        """
        Read file contents.

        Args:
            project: Project to query
            path: File path relative to repo root
            ref: Branch, tag, or commit SHA

        Returns:
            ProviderFile with content and metadata

        Raises:
            ProviderFileNotFoundError: File doesn't exist at ref
        """
        pass

    @abstractmethod
    async def read_config(
        self,
        project: ProviderProject,
        ref: str
    ) -> Optional[dict]:
        """
        Read repo-ctx configuration file if it exists.

        Searches for configuration files in this order:
        1. git_context.json (current name)
        2. .git_context.json
        3. repo_context.json
        4. .repo-ctx.json

        Args:
            project: Project to query
            ref: Branch, tag, or commit SHA

        Returns:
            Parsed JSON config or None if not found

        Raises:
            ProviderError: Error reading configuration
        """
        pass

    @abstractmethod
    async def get_tags(
        self,
        project: ProviderProject,
        limit: int = 5
    ) -> List[str]:
        """
        Get repository tags (most recent first).

        Args:
            project: Project to query
            limit: Maximum number of tags to return

        Returns:
            List of tag names

        Raises:
            ProviderError: Error accessing tags
        """
        pass

    @abstractmethod
    async def list_projects_in_group(
        self,
        group_path: str,
        include_subgroups: bool = True
    ) -> List[ProviderProject]:
        """
        List all projects in a group/organization.

        Args:
            group_path: Group identifier
                       GitLab: "group" or "group/subgroup"
                       GitHub: "org"
                       Local: Not supported

        include_subgroups: Include nested groups (GitLab only)

        Returns:
            List of projects in the group

        Raises:
            ProviderNotFoundError: Group not found
            NotImplementedError: Provider doesn't support groups

        Note:
            Not all providers support groups (e.g., local repos)
        """
        pass
