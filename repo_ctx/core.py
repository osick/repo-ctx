"""Core business logic."""
from typing import Optional, Dict
from .config import Config
from .storage import Storage
from .parser import Parser
from .models import Library, Version, Document, SearchResult
from .providers import (
    GitProvider,
    ProviderFactory,
    ProviderDetector,
    ProviderProject,
    ProviderNotFoundError
)


class RepositoryContext:
    """
    Core repository indexing and search functionality.

    Supports multiple repository providers (GitLab, GitHub, local, etc.)
    """

    def __init__(self, config: Config):
        """
        Initialize repository context with providers.

        Args:
            config: Configuration object with provider settings
        """
        self.config = config
        self.storage = Storage(config.storage_path)
        self.parser = Parser()

        # Initialize providers based on config
        self.providers: Dict[str, GitProvider] = {}
        self._init_providers()

        # Default provider (for backward compatibility)
        self.default_provider = "gitlab"

    def _init_providers(self):
        """Initialize configured providers."""
        # Initialize GitLab provider if configured
        if self.config.gitlab_url and self.config.gitlab_token:
            try:
                self.providers["gitlab"] = ProviderFactory.create_gitlab(
                    url=self.config.gitlab_url,
                    token=self.config.gitlab_token
                )
            except Exception:
                # GitLab provider initialization failed, continue without it
                pass

        # Initialize GitHub provider if configured
        if self.config.github_url or self.config.github_token:
            try:
                github_url = self.config.github_url or "https://api.github.com"
                self.providers["github"] = ProviderFactory.create_github(
                    url=github_url,
                    token=self.config.github_token
                )
            except Exception:
                # GitHub provider initialization failed, continue without it
                pass

        # Set default provider based on what's available
        if "gitlab" in self.providers:
            self.default_provider = "gitlab"
        elif "github" in self.providers:
            self.default_provider = "github"

        # Future: Local provider
        # self.providers["local"] = ProviderFactory.create_local()

    def get_provider(self, provider_type: Optional[str] = None) -> GitProvider:
        """
        Get provider instance.

        Args:
            provider_type: Provider type, or None to use default

        Returns:
            Provider instance

        Raises:
            ValueError: Provider not configured
        """
        provider_type = provider_type or self.default_provider

        if provider_type not in self.providers:
            raise ValueError(
                f"Provider '{provider_type}' not configured. "
                f"Available: {list(self.providers.keys())}"
            )

        return self.providers[provider_type]

    async def init(self):
        """Initialize storage."""
        await self.storage.init_db()

    async def search_libraries(self, query: str) -> list[SearchResult]:
        """Search for libraries by name."""
        results = await self.storage.search(query)
        # Simple ranking: exact matches first
        for result in results:
            if query.lower() in result.name.lower():
                result.score = 2.0
            if query.lower() == result.name.lower():
                result.score = 3.0
        results.sort(key=lambda x: x.score, reverse=True)
        return results

    async def fuzzy_search_libraries(self, query: str, limit: int = 10) -> list:
        """Fuzzy search for libraries."""
        return await self.storage.fuzzy_search(query, limit)

    async def get_documentation(
        self,
        library_id: str,
        topic: Optional[str] = None,
        page: int = 1
    ) -> dict:
        """
        Get documentation for a library.

        Args:
            library_id: Library identifier (format: /group/project or /group/project/version)
            topic: Optional topic filter
            page: Page number for pagination

        Returns:
            Documentation content and metadata
        """
        # Parse library_id: /group/project or /group/subgroup/project or /group/project/version
        # Or URI format: gitlab://group/project, github://owner/repo, local:///path

        # Handle URI format
        if "://" in library_id:
            provider_type, path = ProviderDetector.from_library_id(library_id)
            parts = path.strip("/").split("/")
        else:
            # Legacy format: /group/project
            parts = library_id.strip("/").split("/")

        if len(parts) < 2:
            raise ValueError(f"Invalid library_id: {library_id}")

        # Check if last part is a version (exists in versions table)
        # For now, assume last part is project, second-to-last might be version
        # Simple heuristic: if we have more than 2 parts, last could be version
        project = parts[-1]
        group = "/".join(parts[:-1])
        version = None

        # Try to get library with full path first
        library = await self.storage.get_library(group, project)

        # If not found and we have 3+ parts, try treating last as version
        if not library and len(parts) >= 3:
            version = parts[-1]
            project = parts[-2]
            group = "/".join(parts[:-2])
            library = await self.storage.get_library(group, project)

        if not library:
            raise ValueError(f"Library not found: {group}/{project}")

        # Use default version if not specified
        if not version:
            version = library.default_version

        # Get version_id
        version_id = await self.storage.get_version_id(library.id, version)
        if not version_id:
            raise ValueError(f"Version not found: {version}")

        # Get documents
        documents = await self.storage.get_documents(version_id, topic, page)

        # Format for LLM
        content = self.parser.format_for_llm(documents, library_id)

        return {
            "content": [{"type": "text", "text": content}],
            "metadata": {
                "library": f"{group}/{project}",
                "version": version,
                "page": page,
                "documents_count": len(documents)
            }
        }

    async def index_repository(
        self,
        group: str,
        project: str,
        provider_type: Optional[str] = None
    ):
        """
        Index a repository from any provider.

        Args:
            group: Group/organization path
            project: Project/repository name
            provider_type: Provider type (gitlab, github, local) or None for auto-detect

        Raises:
            ValueError: Provider not configured
            ProviderNotFoundError: Repository not found
        """
        # Auto-detect provider if not specified
        if provider_type is None:
            path = f"{group}/{project}"
            provider_type = ProviderDetector.detect(path, default=self.default_provider)

        provider = self.get_provider(provider_type)

        # Get project via provider interface
        project_path = f"{group}/{project}"
        proj = await provider.get_project(project_path)

        # Get default branch
        default_branch = await provider.get_default_branch(proj)

        # Read config file if exists
        config = await provider.read_config(proj, default_branch)

        # Get project description
        description = config.get("description", proj.description) if config else proj.description

        # Save library with provider URI format
        library_id_uri = ProviderDetector.to_library_id(project_path, provider_type)

        library = Library(
            group_name=group,
            project_name=project,
            description=description or "",
            default_version=default_branch
        )
        db_library_id = await self.storage.save_library(library)

        # Index default branch
        await self._index_version(
            provider,
            proj,
            db_library_id,
            default_branch,
            config
        )

        # Index tags
        tags = await provider.get_tags(proj, limit=5)
        for tag in tags:
            await self._index_version(
                provider,
                proj,
                db_library_id,
                tag,
                config
            )

    async def index_group(
        self,
        group_path: str,
        include_subgroups: bool = True,
        provider_type: Optional[str] = None
    ) -> dict:
        """
        Index all projects in a group/organization.

        Args:
            group_path: Group path
            include_subgroups: Include nested subgroups (GitLab only)
            provider_type: Provider type or None for default

        Returns:
            Summary of indexing results
        """
        provider_type = provider_type or self.default_provider
        provider = self.get_provider(provider_type)

        projects = await provider.list_projects_in_group(
            group_path,
            include_subgroups
        )

        results = {
            "total": len(projects),
            "indexed": [],
            "failed": []
        }

        for proj in projects:
            # Parse path to extract group and project
            parts = proj.path.split("/")
            if len(parts) < 2:
                continue

            project_name = parts[-1]
            group_name = "/".join(parts[:-1])

            try:
                await self.index_repository(
                    group_name,
                    project_name,
                    provider_type
                )
                results["indexed"].append(proj.path)
            except Exception as e:
                results["failed"].append({
                    "path": proj.path,
                    "error": str(e)
                })

        return results

    async def _index_version(
        self,
        provider: GitProvider,
        project: ProviderProject,
        library_id: int,
        ref: str,
        config: Optional[dict]
    ):
        """
        Index a specific version/branch/tag.

        Args:
            provider: Provider instance
            project: Project metadata
            library_id: Database library ID
            ref: Branch, tag, or commit SHA
            config: Optional repo-ctx configuration
        """
        # For commit SHA, we need to get it from the ref
        # For now, use ref as commit SHA (works for GitLab)
        # TODO: Get actual commit SHA for the ref
        commit_sha = ref  # Simplified for now

        # Save version
        version = Version(
            library_id=library_id,
            version_tag=ref,
            commit_sha=commit_sha
        )
        version_id = await self.storage.save_version(version)

        # Get file tree
        file_paths = await provider.get_file_tree(project, ref, recursive=True)

        # Filter and process files
        for path in file_paths:
            if not self.parser.should_include_file(path, config):
                continue

            # Read file content
            try:
                file = await provider.read_file(project, path, ref)
                parsed_content = self.parser.parse_markdown(file.content)
                tokens = self.parser.count_tokens(parsed_content)

                # Save document
                doc = Document(
                    version_id=version_id,
                    file_path=path,
                    content=parsed_content,
                    tokens=tokens
                )
                await self.storage.save_document(doc)
            except Exception as e:
                # Skip files that can't be read
                print(f"Warning: Could not read {path}: {e}")
                continue


# Backward compatibility alias
GitLabContext = RepositoryContext
