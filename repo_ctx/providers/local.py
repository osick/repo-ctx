"""Local Git repository provider."""

import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Optional, List

from git import Repo, InvalidGitRepositoryError

from .base import GitProvider, ProviderProject, ProviderFile


class LocalGitProvider(GitProvider):
    """Provider for local Git repositories.

    Indexes repositories from the local filesystem without network access.
    Provides faster indexing compared to remote providers.
    """

    def __init__(self, repo_path: str):
        """Initialize local Git provider.

        Args:
            repo_path: Path to Git repository (absolute, relative, or ~)

        Raises:
            FileNotFoundError: If path doesn't exist
            ValueError: If path is not a Git repository
        """
        self.repo_path = Path(repo_path).expanduser().resolve()

        if not self.repo_path.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        try:
            self.repo = Repo(str(self.repo_path))
        except InvalidGitRepositoryError:
            raise ValueError(f"Path is not a Git repository: {repo_path}")

    async def get_project(self, path: str) -> ProviderProject:
        """Get project metadata from local repository.

        Args:
            path: Repository path (same as __init__)

        Returns:
            ProviderProject with extracted metadata
        """
        # Run in thread pool to avoid blocking
        return await asyncio.to_thread(self._get_project_sync)

    def _get_project_sync(self) -> ProviderProject:
        """Synchronous implementation of get_project."""
        # Extract project name from directory name
        project_name = self.repo_path.name

        # Try to get description from git config or README
        description = self._get_description()

        # Get remote URL if available
        web_url = self._get_remote_url()

        # Generate stable project ID
        project_id = self._generate_project_id()

        # Get current branch
        current_branch = self._get_current_branch()

        return ProviderProject(
            id=project_id,
            name=project_name,
            path=str(self.repo_path),
            description=description,
            default_branch=current_branch,
            web_url=web_url
        )

    def _get_description(self) -> Optional[str]:
        """Extract repository description from git config or README."""
        import re

        # Try git config first
        try:
            config = self.repo.config_reader()
            if config.has_option("gitweb", "description"):
                return config.get("gitweb", "description")
        except Exception:
            pass

        # Fall back to first meaningful line of README
        for readme_name in ["README.md", "README.rst", "README.txt", "README"]:
            readme_path = self.repo_path / readme_name
            if readme_path.exists():
                try:
                    with open(readme_path) as f:
                        # Read up to 20 lines to find meaningful content
                        for _ in range(20):
                            line = f.readline()
                            if not line:  # EOF
                                break

                            line = line.strip()

                            # Skip empty lines
                            if not line:
                                continue

                            # Skip HTML tags (full line is just a tag)
                            if re.match(r'^<[^>]+>$', line):
                                continue

                            # Skip markdown images
                            if re.match(r'^\!\[.*\]\(.*\)$', line):
                                continue

                            # Skip lines that are only markdown markers
                            if re.match(r'^[\*\-_=]+$', line):
                                continue

                            # Found meaningful content - clean it up
                            # Remove markdown heading markers
                            text = re.sub(r'^#+\s*', '', line)
                            # Remove inline HTML tags
                            text = re.sub(r'<[^>]+>', '', text)
                            # Remove markdown formatting
                            text = re.sub(r'[\*_`]', '', text)

                            text = text.strip()
                            if text:  # Has content after cleaning
                                return text
                except Exception:
                    pass

        return None

    def _get_remote_url(self) -> Optional[str]:
        """Get remote URL if configured."""
        try:
            if 'origin' in self.repo.remotes:
                return self.repo.remotes.origin.url
        except Exception:
            pass
        return None

    def _get_current_branch(self) -> str:
        """Get current branch name."""
        try:
            return self.repo.active_branch.name
        except (TypeError, AttributeError):
            # Detached HEAD or empty repo
            # Try to get default branch from HEAD ref
            try:
                head_ref = self.repo.head.ref
                return head_ref.name if hasattr(head_ref, 'name') else "main"
            except Exception:
                return "main"

    def _generate_project_id(self) -> str:
        """Generate stable project identifier."""
        # Use remote URL if available
        remote_url = self._get_remote_url()
        if remote_url:
            # Parse GitHub/GitLab URL: https://github.com/owner/repo.git
            # Extract: github.com/owner/repo
            match = re.search(r'([^/:]+/[^/]+?)(\.git)?$', remote_url)
            if match:
                return match.group(1)

        # Fallback: use path hash
        path_hash = hashlib.sha256(str(self.repo_path).encode()).hexdigest()[:12]
        return f"local-{path_hash}"

    async def get_default_branch(self, project: ProviderProject) -> str:
        """Get default branch name."""
        return project.default_branch

    async def get_file_tree(
        self,
        project: ProviderProject,
        ref: str,
        recursive: bool = True
    ) -> List[str]:
        """Get file tree at specific ref.

        Args:
            project: Project to get files from
            ref: Branch, tag, or commit SHA
            recursive: If True, include subdirectories

        Returns:
            List of file paths relative to repo root
        """
        return await asyncio.to_thread(
            self._get_file_tree_sync, ref, recursive
        )

    def _get_file_tree_sync(self, ref: str, recursive: bool) -> List[str]:
        """Synchronous implementation of get_file_tree."""
        try:
            # Get tree object for ref
            commit = self.repo.commit(ref)
            tree = commit.tree

            files = []

            if recursive:
                # Recursive traversal
                for item in tree.traverse():
                    if item.type == 'blob':  # File, not directory
                        # Skip binary files
                        if not self._is_binary_file(item):
                            files.append(item.path)
            else:
                # Only root level files
                for item in tree:
                    if item.type == 'blob':
                        if not self._is_binary_file(item):
                            files.append(item.name)

            return files
        except Exception as e:
            raise ValueError(f"Failed to get file tree for ref '{ref}': {e}")

    def _is_binary_file(self, blob) -> bool:
        """Check if file is binary.

        Args:
            blob: Git blob object

        Returns:
            True if file appears to be binary
        """
        try:
            # Get the binary data directly
            data = blob.data_stream.read()

            # Check for null bytes in first 8KB (common in binary files)
            sample = data[:8192]
            return b'\x00' in sample
        except Exception:
            return False

    async def read_file(
        self,
        project: ProviderProject,
        path: str,
        ref: str
    ) -> ProviderFile:
        """Read file content at specific ref.

        Args:
            project: Project containing the file
            path: File path relative to repo root
            ref: Branch, tag, or commit SHA

        Returns:
            ProviderFile with content
        """
        return await asyncio.to_thread(
            self._read_file_sync, path, ref
        )

    def _read_file_sync(self, path: str, ref: str) -> ProviderFile:
        """Synchronous implementation of read_file."""
        try:
            commit = self.repo.commit(ref)
            blob = commit.tree / path

            content = blob.data_stream.read().decode('utf-8', errors='replace')

            return ProviderFile(
                path=path,
                content=content,
                size=blob.size
            )
        except KeyError:
            raise FileNotFoundError(f"File '{path}' not found at ref '{ref}'")
        except Exception as e:
            raise FileNotFoundError(f"File '{path}' not found at ref '{ref}': {e}")

    async def read_config(
        self,
        project: ProviderProject,
        ref: str
    ) -> Optional[dict]:
        """Read .repo-ctx.json or git_context.json configuration.

        Args:
            project: Project to read config from
            ref: Branch or tag to read config from

        Returns:
            Configuration dict or None if not found
        """
        for config_name in [".repo-ctx.json", "git_context.json", ".git_context.json", "repo_context.json"]:
            try:
                file = await self.read_file(project, config_name, ref)
                return json.loads(file.content)
            except FileNotFoundError:
                continue

        return None

    async def get_tags(
        self,
        project: ProviderProject,
        limit: int = 5
    ) -> List[str]:
        """Get repository tags sorted by creation date.

        Args:
            project: Project to get tags from
            limit: Maximum number of tags to return

        Returns:
            List of tag names, most recent first
        """
        return await asyncio.to_thread(self._get_tags_sync, limit)

    def _get_tags_sync(self, limit: int) -> List[str]:
        """Synchronous implementation of get_tags."""
        try:
            # Get all tags with their commit dates
            tags_with_dates = []
            for tag in self.repo.tags:
                try:
                    # Get commit date
                    commit = tag.commit
                    date = commit.committed_datetime
                    tags_with_dates.append((tag.name, date))
                except Exception:
                    # Skip tags that can't be resolved
                    continue

            # Sort by date (newest first)
            tags_with_dates.sort(key=lambda x: x[1], reverse=True)

            # Return tag names only
            return [name for name, _ in tags_with_dates[:limit]]
        except Exception:
            return []

    async def list_projects_in_group(
        self,
        group_path: str,
        include_subgroups: bool = True
    ) -> List[ProviderProject]:
        """List projects in a group.

        Not supported for local provider.

        Raises:
            NotImplementedError: Local provider doesn't support groups
        """
        raise NotImplementedError(
            "Local provider does not support listing projects in groups. "
            "Use a directory scanner instead."
        )
