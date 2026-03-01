"""GitHub provider implementation."""
import base64
import json
from typing import Optional, List
from github import Github, GithubException, UnknownObjectException, BadCredentialsException
from .base import GitProvider, ProviderProject, ProviderFile
from .exceptions import (
    ProviderNotFoundError,
    ProviderAuthError,
    ProviderFileNotFoundError,
    ProviderError,
    ProviderRateLimitError
)


class GitHubProvider(GitProvider):
    """GitHub repository provider using PyGithub."""

    def __init__(self, url: str = "https://api.github.com", token: Optional[str] = None):
        """
        Initialize GitHub provider.

        Args:
            url: GitHub API URL (default: public GitHub, or GitHub Enterprise URL)
            token: Personal access token (optional for public repos)

        Raises:
            ProviderAuthError: Authentication failed
        """
        self.url = url
        self.token = token

        try:
            if url == "https://api.github.com":
                # Public GitHub
                self.client = Github(token) if token else Github()
            else:
                # GitHub Enterprise
                base_url = url.replace("/api/v3", "").rstrip("/")
                self.client = Github(base_url=base_url, login_or_token=token)

            # Verify authentication
            if token:
                try:
                    self.client.get_user().login
                except BadCredentialsException as e:
                    raise ProviderAuthError(f"GitHub authentication failed: {e}")

        except Exception as e:
            if isinstance(e, ProviderAuthError):
                raise
            raise ProviderError(f"Failed to initialize GitHub client: {e}")

    async def get_project(self, path: str) -> ProviderProject:
        """
        Get project metadata from GitHub.

        Args:
            path: Repository path (format: owner/repo)

        Returns:
            ProviderProject with normalized metadata

        Raises:
            ProviderNotFoundError: Repository doesn't exist
            ProviderAuthError: Authentication failed
        """
        try:
            repo = self.client.get_repo(path)

            return ProviderProject(
                id=str(repo.id),
                name=repo.name,
                path=repo.full_name,
                description=repo.description,
                default_branch=repo.default_branch,
                web_url=repo.html_url
            )

        except UnknownObjectException:
            raise ProviderNotFoundError(f"GitHub repository not found: {path}")
        except BadCredentialsException:
            raise ProviderAuthError(f"Authentication failed for repository: {path}")
        except GithubException as e:
            if e.status == 404:
                raise ProviderNotFoundError(f"GitHub repository not found: {path}")
            elif e.status == 401:
                raise ProviderAuthError(f"Authentication failed for repository: {path}")
            elif e.status == 403:
                # Could be rate limit or permissions
                if "rate limit" in str(e).lower():
                    raise ProviderRateLimitError(f"GitHub rate limit exceeded")
                raise ProviderAuthError(f"Access denied to repository: {path}")
            else:
                raise ProviderError(f"Error getting GitHub repository {path}: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error getting repository {path}: {e}")

    async def get_default_branch(self, project: ProviderProject) -> str:
        """
        Get default branch name.

        Args:
            project: Project to query

        Returns:
            Default branch name (e.g., "main", "master")
        """
        # Already in ProviderProject
        if project.default_branch:
            return project.default_branch

        # Fallback: fetch from API
        try:
            repo = self.client.get_repo(project.path)
            return repo.default_branch
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
            repo = self.client.get_repo(project.path)

            # Get git tree
            tree = repo.get_git_tree(ref, recursive=recursive)

            # Extract file paths (blobs only, not trees)
            file_paths = []
            for item in tree.tree:
                if item.type == "blob":  # Files only, not directories
                    file_paths.append(item.path)

            return file_paths

        except GithubException as e:
            if e.status == 404:
                raise ProviderError(
                    f"Branch/tag '{ref}' not found in repository {project.path}"
                )
            elif e.status == 409:
                # Empty repository
                return []
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
        Read file contents from GitHub.

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
            repo = self.client.get_repo(project.path)
            file_content = repo.get_contents(path, ref=ref)

            # Handle file content (could be list if path is directory)
            if isinstance(file_content, list):
                raise ProviderError(f"Path '{path}' is a directory, not a file")

            # Decode content
            content = file_content.decoded_content.decode('utf-8')

            return ProviderFile(
                path=path,
                content=content,
                size=file_content.size
            )

        except UnknownObjectException:
            raise ProviderFileNotFoundError(
                f"File '{path}' not found in {project.path} at ref '{ref}'"
            )
        except GithubException as e:
            if e.status == 404:
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
        5. .github/repo-ctx.json (GitHub-specific)

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
            ".repo-ctx.json",
            ".github/repo-ctx.json"  # GitHub-specific location
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
            repo = self.client.get_repo(project.path)
            tags = repo.get_tags()

            # Safely iterate and collect tags (handles empty repos)
            tag_names = []
            for i, tag in enumerate(tags):
                if i >= limit:
                    break
                tag_names.append(tag.name)

            return tag_names

        except GithubException as e:
            raise ProviderError(f"Error getting tags: {e}")
        except Exception as e:
            raise ProviderError(f"Unexpected error getting tags: {e}")

    async def list_projects_in_group(
        self,
        group_path: str,
        include_subgroups: bool = True
    ) -> List[ProviderProject]:
        """
        List all projects in a GitHub organization.

        Args:
            group_path: Organization name (e.g., "fastapi")
            include_subgroups: Ignored for GitHub (no nested orgs)

        Returns:
            List of public repositories in the organization

        Raises:
            ProviderNotFoundError: Organization not found
            ProviderError: Error accessing organization

        Note:
            GitHub doesn't have nested organizations like GitLab,
            so include_subgroups parameter is ignored.
        """
        try:
            org = self.client.get_organization(group_path)
            repos = org.get_repos()

            result = []
            for repo in repos:
                result.append(ProviderProject(
                    id=str(repo.id),
                    name=repo.name,
                    path=repo.full_name,
                    description=repo.description,
                    default_branch=repo.default_branch,
                    web_url=repo.html_url
                ))

            return result

        except UnknownObjectException:
            raise ProviderNotFoundError(f"GitHub organization not found: {group_path}")
        except BadCredentialsException:
            raise ProviderAuthError(
                f"Authentication failed for organization: {group_path}"
            )
        except GithubException as e:
            if e.status == 404:
                raise ProviderNotFoundError(f"GitHub organization not found: {group_path}")
            elif e.status == 401:
                raise ProviderAuthError(
                    f"Authentication failed for organization: {group_path}"
                )
            elif e.status == 403:
                if "rate limit" in str(e).lower():
                    raise ProviderRateLimitError(
                        f"GitHub rate limit exceeded for organization: {group_path}"
                    )
                else:
                    raise ProviderAuthError(
                        f"Access denied to organization: {group_path}"
                    )
            else:
                raise ProviderError(f"Error getting organization {group_path}: {e}")
        except Exception as e:
            raise ProviderError(
                f"Unexpected error listing projects in organization {group_path}: {e}"
            )
