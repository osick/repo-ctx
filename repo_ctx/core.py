"""Core business logic."""
from typing import Optional, Dict
from .config import Config
from .storage import Storage
from .parser import Parser
from .models import Library, Version, Document, SearchResult, OutputMode
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

        # Initialize GitHub provider (always available for public repos)
        # Token is optional - public repos work without authentication (with rate limits)
        try:
            github_url = self.config.github_url or "https://api.github.com"
            self.providers["github"] = ProviderFactory.create_github(
                url=github_url,
                token=self.config.github_token  # Can be None for public repos
            )
        except Exception as e:
            # If authentication fails with a token, try without token for public repos
            from .providers.exceptions import ProviderAuthError
            if isinstance(e, ProviderAuthError) and self.config.github_token:
                try:
                    print(f"Warning: GitHub token authentication failed, falling back to unauthenticated access")
                    print(f"         (Public repos only, with rate limits)")
                    github_url = self.config.github_url or "https://api.github.com"
                    self.providers["github"] = ProviderFactory.create_github(
                        url=github_url,
                        token=None  # No token for public repos
                    )
                except Exception:
                    # Still failed, give up on GitHub provider
                    pass
            # GitHub provider initialization failed, continue without it

        # Local provider is always available (no config needed)
        # It will be instantiated on-demand when indexing a specific path
        self.local_provider_available = True

        # Set default provider based on what's available
        if "gitlab" in self.providers:
            self.default_provider = "gitlab"
        elif "github" in self.providers:
            self.default_provider = "github"
        else:
            # If no remote providers configured, default to local
            self.default_provider = "local"

    def get_provider(self, provider_type: Optional[str] = None, repo_path: Optional[str] = None) -> GitProvider:
        """
        Get provider instance.

        Args:
            provider_type: Provider type, or None to use default
            repo_path: Repository path (required for local provider)

        Returns:
            Provider instance

        Raises:
            ValueError: Provider not configured
        """
        provider_type = provider_type or self.default_provider

        # Special handling for local provider (created on-demand)
        if provider_type == "local":
            if not repo_path:
                raise ValueError("Local provider requires repo_path parameter")
            from .providers.local import LocalGitProvider
            return LocalGitProvider(repo_path)

        if provider_type not in self.providers:
            raise ValueError(
                f"Provider '{provider_type}' not configured. "
                f"Available: {list(self.providers.keys()) + ['local']}"
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

    def _get_repository_url(self, lib: Library) -> str:
        """
        Get the URL or file path for a repository.

        Args:
            lib: Library object

        Returns:
            URL for remote repos, file path for local repos
        """
        # Detect provider from path format
        if lib.group_name.startswith("/") or lib.group_name.startswith("~"):
            # Local repository - return the file path
            if lib.project_name:
                return f"{lib.group_name}/{lib.project_name}"
            return lib.group_name

        # Check if it's GitHub (2 parts)
        library_id = f"/{lib.group_name}/{lib.project_name}"
        parts = library_id.strip("/").split("/")

        if len(parts) == 2:
            # Likely GitHub
            return f"https://github.com/{lib.group_name}/{lib.project_name}"
        else:
            # Likely GitLab - use configured URL if available
            if self.config.gitlab_url:
                return f"{self.config.gitlab_url}/{lib.group_name}/{lib.project_name}"
            # Otherwise just return the path
            return f"/{lib.group_name}/{lib.project_name}"

    async def list_all_libraries(self, provider_filter: Optional[str] = None) -> list[Library]:
        """
        List all indexed libraries.

        Args:
            provider_filter: Optional provider filter ('local', 'github', 'gitlab')

        Returns:
            List of Library objects with metadata
        """
        libraries = await self.storage.get_all_libraries()

        # Filter by provider if requested
        if provider_filter:
            filtered = []
            for lib in libraries:
                # Detect provider from library ID format
                library_id = f"/{lib.group_name}/{lib.project_name}"
                detected = ProviderDetector.detect(library_id)

                # For stored libraries, we need to check the path format
                # Local: starts with / and is a file path
                # GitHub: typically 2 parts (owner/repo)
                # GitLab: typically 3+ parts or configured domains

                if provider_filter == "local":
                    # Local repos have absolute paths as group_name
                    if lib.group_name.startswith("/") or lib.group_name.startswith("~"):
                        filtered.append(lib)
                elif provider_filter == "github":
                    # GitHub: 2-part names without / prefix (owner/repo)
                    parts = library_id.strip("/").split("/")
                    if len(parts) == 2 and not lib.group_name.startswith("/"):
                        filtered.append(lib)
                elif provider_filter == "gitlab":
                    # GitLab: 3+ parts or specific patterns
                    parts = library_id.strip("/").split("/")
                    if len(parts) >= 3 and not lib.group_name.startswith("/"):
                        filtered.append(lib)

            return filtered

        return libraries

    async def get_documentation(
        self,
        library_id: str,
        topic: Optional[str] = None,
        page: int = 1,
        max_tokens: Optional[int] = None,
        include_examples: bool = False,
        output_mode: OutputMode = OutputMode.STANDARD,
        query: Optional[str] = None
    ) -> dict:
        """
        Get documentation for a library.

        Args:
            library_id: Library identifier (format: /group/project or /group/project/version)
            topic: Optional topic filter
            page: Page number for pagination (ignored if max_tokens specified)
            max_tokens: Maximum tokens to return (preferred over page-based)
            include_examples: If True, include all code examples (override smart filtering)
            output_mode: Output detail level (SUMMARY, STANDARD, FULL)
            query: Optional search query for relevance-based filtering

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

        # Detect if this is a local path (absolute path like /home/... or /usr/...)
        # Local paths are stored with full path as group_name and empty project_name
        is_local_path = library_id.startswith("/") and (
            library_id.startswith("/home/") or
            library_id.startswith("/usr/") or
            library_id.startswith("/opt/") or
            library_id.startswith("/tmp/") or
            library_id.startswith("/var/") or
            library_id.startswith("/mnt/") or
            library_id.startswith("/media/") or
            # Check if it looks like a file path (has more than 3 parts starting with common dirs)
            (len(parts) > 3 and parts[0] in ('home', 'usr', 'opt', 'tmp', 'var', 'mnt', 'media', 'root'))
        )

        if is_local_path:
            # Local repository: stored with full path as group, empty project
            group = library_id.rstrip("/")
            project = ""
            version = None
            library = await self.storage.get_library(group, project)
        else:
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

        # If not found and we have 3+ parts, try treating last as version (not for local paths)
        if not library and not is_local_path and len(parts) >= 3:
            version = parts[-1]
            project = parts[-2]
            group = "/".join(parts[:-2])
            library = await self.storage.get_library(group, project)

        if not library:
            if is_local_path:
                raise ValueError(f"Library not found: {group} (local). Did you index it first with 'repo-ctx -p local repo index {group}'?")
            raise ValueError(f"Library not found: {group}/{project}")

        # Use default version if not specified
        if not version:
            version = library.default_version

        # Get version_id
        version_id = await self.storage.get_version_id(library.id, version)
        if not version_id:
            raise ValueError(f"Version not found: {version}")

        # Get documents (all if token-based, paginated if page-based)
        if max_tokens:
            # Get all documents for token-based limiting
            documents = await self.storage.get_documents(version_id, topic, page=1, page_size=9999)
        else:
            # Get all documents for page-based (page_size=9999 means get all)
            # Users can still use --page for manual pagination if needed
            documents = await self.storage.get_documents(version_id, topic, page, page_size=9999)

        # Token-based limiting: format incrementally if max_tokens specified
        if max_tokens:
            # Calculate quality scores and optionally relevance scores
            scored_docs = []
            for doc in documents:
                doc_metadata = self.parser.extract_metadata(doc.content, doc.file_path)
                quality_score = doc_metadata.get("quality_score", 0)

                # Calculate combined score (quality + relevance if query provided)
                if query:
                    relevance_score = self.parser.calculate_relevance_score(doc.content, doc.file_path, query)
                    # Combined: 50% quality + 50% relevance when query is provided
                    combined_score = (quality_score * 0.5) + (relevance_score * 0.5)
                    doc_metadata["relevance_score"] = round(relevance_score, 1)
                else:
                    combined_score = quality_score
                    relevance_score = None

                scored_docs.append({
                    "doc": doc,
                    "quality_score": quality_score,
                    "combined_score": combined_score,
                    "relevance_score": relevance_score,
                    "metadata": doc_metadata
                })

            # Sort by combined score (highest first)
            scored_docs.sort(key=lambda x: x["combined_score"], reverse=True)

            # Format documents one by one and accumulate until token limit
            formatted_docs = []
            docs_metadata = []
            total_tokens = 0
            truncated_docs = []  # Documents that didn't fit

            for scored_doc in scored_docs:
                doc = scored_doc["doc"]
                doc_metadata = scored_doc["metadata"]

                # Format this single document
                single_doc_content = self.parser.format_for_llm([doc], library_id, include_examples=include_examples)
                doc_tokens = self.parser.count_tokens(single_doc_content)

                # Check if adding this document would exceed limit
                if total_tokens + doc_tokens <= max_tokens:
                    formatted_docs.append(doc)
                    total_tokens += doc_tokens
                    doc_metadata["file_path"] = doc.file_path
                    docs_metadata.append(doc_metadata)
                else:
                    # Track truncated documents for the footer
                    truncated_info = {
                        "file_path": doc.file_path,
                        "quality_score": scored_doc["quality_score"],
                        "title": self.parser.extract_title(doc.content, doc.file_path)
                    }
                    if scored_doc["relevance_score"] is not None:
                        truncated_info["relevance_score"] = scored_doc["relevance_score"]
                    truncated_docs.append(truncated_info)

            # Format the selected documents based on output mode
            if output_mode == OutputMode.SUMMARY:
                content = self.parser.format_summary_for_llm(formatted_docs, library_id)
            elif output_mode == OutputMode.FULL:
                content = self.parser.format_full_for_llm(formatted_docs, library_id)
            else:  # STANDARD
                content = self.parser.format_for_llm(formatted_docs, library_id, include_examples=include_examples)

            # Add truncation footer if there are more documents
            if truncated_docs:
                remaining_tokens = max_tokens - total_tokens
                truncation_footer = f"\n\n---\n**... and {len(truncated_docs)} more document(s) available**\n"

                # Show headers of top truncated documents (up to 5)
                top_truncated = truncated_docs[:5]
                if top_truncated:
                    if query:
                        truncation_footer += "Additional documents (by relevance + quality):\n"
                        for td in top_truncated:
                            rel_info = f", relevance: {td.get('relevance_score', 0):.0f}" if 'relevance_score' in td else ""
                            truncation_footer += f"- {td['file_path']} (quality: {td['quality_score']:.0f}{rel_info})\n"
                    else:
                        truncation_footer += "Additional documents (by quality score):\n"
                        for td in top_truncated:
                            truncation_footer += f"- {td['file_path']} (score: {td['quality_score']:.0f})\n"
                    if len(truncated_docs) > 5:
                        truncation_footer += f"- ... and {len(truncated_docs) - 5} more\n"

                content += truncation_footer

            actual_tokens = self.parser.count_tokens(content)

            metadata = {
                "library": f"{group}/{project}",
                "version": version,
                "output_mode": output_mode.value,
                "query": query,
                "documents_count": len(formatted_docs),
                "tokens": actual_tokens,
                "max_tokens": max_tokens,
                "documents_available": len(documents),
                "documents_truncated": len(truncated_docs),
                "documents_metadata": docs_metadata
            }
        else:
            # Page-based: format all retrieved documents based on output mode
            if output_mode == OutputMode.SUMMARY:
                content = self.parser.format_summary_for_llm(documents, library_id)
            elif output_mode == OutputMode.FULL:
                content = self.parser.format_full_for_llm(documents, library_id)
            else:  # STANDARD
                content = self.parser.format_for_llm(documents, library_id, include_examples=include_examples)
            actual_tokens = self.parser.count_tokens(content)

            # Extract metadata for all documents
            docs_metadata = []
            for doc in documents:
                doc_metadata = self.parser.extract_metadata(doc.content, doc.file_path)
                doc_metadata["file_path"] = doc.file_path
                docs_metadata.append(doc_metadata)

            metadata = {
                "library": f"{group}/{project}",
                "version": version,
                "output_mode": output_mode.value,
                "query": query,
                "documents_count": len(documents),
                "tokens": actual_tokens,
                "page": page,
                "documents_metadata": docs_metadata
            }

        return {
            "content": [{"type": "text", "text": content}],
            "metadata": metadata
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
            group: Group/organization path (or full path for local repos)
            project: Project/repository name (or empty for local repos)
            provider_type: Provider type (gitlab, github, local) or None for auto-detect

        Raises:
            ValueError: Provider not configured
            ProviderNotFoundError: Repository not found
        """
        # Auto-detect provider if not specified
        if provider_type is None:
            path = f"{group}/{project}" if project else group
            provider_type = ProviderDetector.detect(path, default=self.default_provider)

        # For local provider, group contains the full path
        if provider_type == "local":
            repo_path = f"{group}/{project}" if project else group
            provider = self.get_provider(provider_type, repo_path=repo_path)
            project_path = repo_path
        else:
            provider = self.get_provider(provider_type)
            project_path = f"{group}/{project}"

        # Get project via provider interface
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
            default_version=default_branch,
            provider=provider_type or "github"
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
