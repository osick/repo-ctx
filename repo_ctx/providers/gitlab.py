"""GitLab provider implementation."""
import gitlab
import base64
import json
from typing import Optional, List
from .base import GitProvider, ProviderProject, ProviderFile
from .exceptions import (
    ProviderNotFoundError,
    ProviderAuthError,
    ProviderFileNotFoundError,
    ProviderError,
    ProviderRateLimitError
)


class GitLabProvider(GitProvider):
    """GitLab repository provider using python-gitlab."""

    def __init__(self, url: str, token: str):
        """
        Initialize GitLab provider.

        Args:
            url: GitLab instance URL
            token: Personal access token with read_api scope

        Raises:
            ProviderAuthError: Authentication failed
        """
        self.url = url
        self.token = token
        try:
            self.client = gitlab.Gitlab(url, private_token=token)
            self.client.auth()
        except gitlab.exceptions.GitlabAuthenticationError as e:
            raise ProviderAuthError(f"GitLab authentication failed: {e}")
        except Exception as e:
            raise ProviderError(f"Failed to initialize GitLab client: {e}")

    async def get_project(self, path: str) -> ProviderProject:
        """
        Get project metadata from GitLab.

        Args:
            path: Project path (format: group/project or group/subgroup/project)

        Returns:
            ProviderProject with normalized metadata

        Raises:
            ProviderNotFoundError: Project doesn't exist
            ProviderAuthError: Authentication failed
        """
        try:
            project = self.client.projects.get(path)

            return ProviderProject(
                id=str(project.id),
                name=project.name,
                path=project.path_with_namespace,
                description=project.description,
                default_branch=project.default_branch,
                web_url=project.web_url
            )
        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                raise ProviderNotFoundError(f"GitLab project not found: {path}")
            elif e.response_code == 401:
                raise ProviderAuthError(f"Authentication failed for project: {path}")
            else:
                raise ProviderError(f"Error getting GitLab project {path}: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error getting project {path}: {e}")

    async def get_default_branch(self, project: ProviderProject) -> str:
        """
        Get default branch name.

        Args:
            project: Project to query

        Returns:
            Default branch name (e.g., "main", "master")
        """
        # Already in ProviderProject, but fetch fresh if needed
        if project.default_branch:
            return project.default_branch

        # Fallback: fetch from API
        try:
            gitlab_project = self.client.projects.get(project.id)
            return gitlab_project.default_branch
        except Exception as e:
            raise ProviderError(f"Error getting default branch: {e}")

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
        try:
            gitlab_project = self.client.projects.get(project.id)
            tree = gitlab_project.repository_tree(
                ref=ref,
                recursive=recursive,
                all=True
            )

            # Extract file paths from tree objects
            file_paths = []
            for item in tree:
                if item['type'] == 'blob':  # Files only, not directories
                    file_paths.append(item['path'])

            return file_paths

        except gitlab.exceptions.GitlabGetError as e:
            # If ref not found, try with default branch
            if e.response_code == 404:
                raise ProviderError(
                    f"Branch/tag '{ref}' not found in project {project.path}"
                )
            else:
                raise ProviderError(f"Error getting file tree: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error getting file tree: {e}")

    async def read_file(
        self,
        project: ProviderProject,
        path: str,
        ref: str
    ) -> ProviderFile:
        """
        Read file contents from GitLab.

        Args:
            project: Project to query
            path: File path relative to repo root
            ref: Branch, tag, or commit SHA

        Returns:
            ProviderFile with content and metadata

        Raises:
            ProviderFileNotFoundError: File doesn't exist at ref
        """
        try:
            gitlab_project = self.client.projects.get(project.id)
            file_data = gitlab_project.files.get(file_path=path, ref=ref)

            # Decode content if base64 encoded
            content = file_data.content
            if file_data.encoding == 'base64':
                content = base64.b64decode(content).decode('utf-8')

            return ProviderFile(
                path=path,
                content=content,
                size=file_data.size if hasattr(file_data, 'size') else len(content)
            )

        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                raise ProviderFileNotFoundError(
                    f"File '{path}' not found in {project.path} at ref '{ref}'"
                )
            else:
                raise ProviderError(f"Error reading file {path}: {e}")
        except UnicodeDecodeError:
            raise ProviderError(
                f"File '{path}' is not valid UTF-8 (binary file?)"
            )
        except Exception as e:
            raise ProviderError(f"Unexpected error reading file {path}: {e}")

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
        """
        config_filenames = [
            "git_context.json",
            ".git_context.json",
            "repo_context.json",
            ".repo-ctx.json"
        ]

        for filename in config_filenames:
            try:
                file = await self.read_file(project, filename, ref)
                return json.loads(file.content)
            except ProviderFileNotFoundError:
                # Try next filename
                continue
            except json.JSONDecodeError as e:
                raise ProviderError(
                    f"Invalid JSON in config file {filename}: {e}"
                )
            except Exception:
                # Try next filename
                continue

        # No config file found
        return None

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
        try:
            gitlab_project = self.client.projects.get(project.id)
            tags = gitlab_project.tags.list(all=True)

            # GitLab returns tags in reverse chronological order by default
            tag_names = [tag.name for tag in tags[:limit]]

            return tag_names

        except gitlab.exceptions.GitlabError as e:
            raise ProviderError(f"Error getting tags: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error getting tags: {e}")

    async def list_projects_in_group(
        self,
        group_path: str,
        include_subgroups: bool = True
    ) -> List[ProviderProject]:
        """
        List all projects in a GitLab group.

        Args:
            group_path: Group path (e.g., "mygroup" or "mygroup/subgroup")
            include_subgroups: Include projects from nested subgroups

        Returns:
            List of projects in the group

        Raises:
            ProviderNotFoundError: Group not found
            ProviderError: Error accessing group
        """
        try:
            group = self.client.groups.get(group_path)
            projects = group.projects.list(
                all=True,
                include_subgroups=include_subgroups
            )

            result = []
            for proj in projects:
                result.append(ProviderProject(
                    id=str(proj.id),
                    name=proj.name,
                    path=proj.path_with_namespace,
                    description=getattr(proj, 'description', None),
                    default_branch=getattr(proj, 'default_branch', 'main'),
                    web_url=getattr(proj, 'web_url', None)
                ))

            return result

        except gitlab.exceptions.GitlabGetError as e:
            if e.response_code == 404:
                raise ProviderNotFoundError(f"GitLab group not found: {group_path}")
            elif e.response_code == 401:
                raise ProviderAuthError(
                    f"Authentication failed for group: {group_path}"
                )
            else:
                raise ProviderError(f"Error getting group {group_path}: {e}")
        except gitlab.exceptions.GitlabHttpError as e:
            if e.response_code == 429:
                raise ProviderRateLimitError(
                    f"GitLab rate limit exceeded for group: {group_path}"
                )
            else:
                raise ProviderError(f"HTTP error accessing group {group_path}: {e}")
        except Exception as e:
            raise ProviderError(
                f"Unexpected error listing projects in group {group_path}: {e}"
            )
