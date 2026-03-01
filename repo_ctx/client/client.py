"""Unified client for repo-ctx operations.

This module provides RepoCtxClient, a unified interface that can be used
by CLI, MCP, and other integrations. It supports both direct service
access and HTTP API access.
"""

import logging
from enum import Enum
from typing import Any, Callable, Optional

from repo_ctx.config import Config
from repo_ctx.client.models import (
    Library,
    Symbol,
    SearchResult,
    IndexResult,
    AnalysisResult,
)

logger = logging.getLogger("repo_ctx.client")


class ClientMode(Enum):
    """Client operation mode."""

    DIRECT = "direct"  # Use service layer directly
    HTTP = "http"  # Use HTTP API


class RepoCtxClient:
    """Unified client for repo-ctx operations.

    Provides a single interface for all repo-ctx operations that works
    in both direct mode (using services) and HTTP mode (using REST API).

    Example:
        # Direct mode (default)
        async with RepoCtxClient() as client:
            libraries = await client.list_libraries()

        # HTTP mode
        client = RepoCtxClient(api_url="http://localhost:8000")
        await client.connect()
        libraries = await client.list_libraries()
        await client.close()
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        mode: Optional[ClientMode] = None,
    ) -> None:
        """Initialize the client.

        Args:
            config: Configuration object (for direct mode).
            api_url: API URL (for HTTP mode).
            api_key: API key for authentication.
            mode: Operation mode (auto-detected if not specified).
        """
        self._config = config
        self._api_url = api_url
        self._api_key = api_key

        # Auto-detect mode
        if mode is not None:
            self._mode = mode
        elif api_url:
            self._mode = ClientMode.HTTP
        else:
            self._mode = ClientMode.DIRECT

        # Direct mode resources
        self._legacy_context = None
        self._service_context = None
        self._repository_service = None
        self._indexing_service = None
        self._search_service = None
        self._analysis_service = None

        # HTTP mode resources
        self._http_session = None

        self._initialized = False

    @property
    def mode(self) -> ClientMode:
        """Get the client mode."""
        return self._mode

    @property
    def is_initialized(self) -> bool:
        """Check if client is initialized."""
        return self._initialized

    async def connect(self) -> None:
        """Initialize and connect the client.

        For direct mode, initializes services and database.
        For HTTP mode, creates HTTP session.
        """
        if self._initialized:
            return

        if self._mode == ClientMode.DIRECT:
            await self._init_direct()
        else:
            await self._init_http()

        self._initialized = True

    async def close(self) -> None:
        """Close the client and release resources."""
        if not self._initialized:
            return

        if self._mode == ClientMode.HTTP and self._http_session:
            await self._http_session.close()
            self._http_session = None

        self._initialized = False

    async def __aenter__(self) -> "RepoCtxClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _init_direct(self) -> None:
        """Initialize direct mode with service layer."""
        from repo_ctx.core import GitLabContext
        from repo_ctx.services.base import ServiceContext
        from repo_ctx.services.repository import RepositoryService
        from repo_ctx.services.indexing import IndexingService
        from repo_ctx.services.search import SearchService
        from repo_ctx.services.analysis import AnalysisService

        # Load config if not provided
        if self._config is None:
            self._config = Config.load()

        # Initialize legacy context (handles database)
        self._legacy_context = GitLabContext(self._config)
        await self._legacy_context.init()

        # Create service context using legacy storage
        self._service_context = ServiceContext(
            content_storage=self._legacy_context.storage,
            vector_storage=None,
            graph_storage=None,
        )

        # Create service instances
        self._repository_service = RepositoryService(self._service_context)
        self._indexing_service = IndexingService(self._service_context)
        self._search_service = SearchService(self._service_context)
        self._analysis_service = AnalysisService(self._service_context)

        logger.info("Client initialized in direct mode")

    async def _init_http(self) -> None:
        """Initialize HTTP mode with API client."""
        try:
            import httpx

            self._http_session = httpx.AsyncClient(
                base_url=self._api_url,
                headers={"Authorization": f"Bearer {self._api_key}"} if self._api_key else {},
                timeout=30.0,
            )
            logger.info(f"Client initialized in HTTP mode: {self._api_url}")
        except ImportError:
            raise RuntimeError("httpx is required for HTTP mode. Install with: pip install httpx")

    # ==========================================================================
    # Repository Operations
    # ==========================================================================

    async def list_libraries(
        self,
        provider: Optional[str] = None,
    ) -> list[Library]:
        """List all indexed libraries.

        Args:
            provider: Optional provider filter (github, gitlab, local).

        Returns:
            List of Library objects.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            raw_libs = await self._legacy_context.list_all_libraries(provider)
            return [self._convert_library(lib) for lib in raw_libs]
        else:
            response = await self._http_session.get("/v1/repositories")
            response.raise_for_status()
            data = response.json()
            return [Library.from_dict(lib) for lib in data.get("repositories", [])]

    async def get_library(self, library_id: str) -> Optional[Library]:
        """Get a library by ID.

        Args:
            library_id: Library identifier (e.g., /owner/repo).

        Returns:
            Library object or None if not found.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            libs = await self._legacy_context.search_libraries(library_id)
            if libs:
                return self._convert_library(libs[0])
            return None
        else:
            response = await self._http_session.get(f"/v1/repositories/{library_id}")
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return Library.from_dict(response.json())

    async def search_libraries(
        self,
        query: str,
        limit: int = 10,
        fuzzy: bool = True,
    ) -> list[SearchResult]:
        """Search for libraries.

        Args:
            query: Search query.
            limit: Maximum results.
            fuzzy: Use fuzzy matching.

        Returns:
            List of SearchResult objects.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            if fuzzy:
                raw_results = await self._legacy_context.fuzzy_search_libraries(query, limit)
            else:
                raw_results = await self._legacy_context.search_libraries(query)
            return [self._convert_search_result(r, "library") for r in raw_results]
        else:
            params = {"query": query, "limit": limit, "fuzzy": fuzzy}
            response = await self._http_session.get("/v1/search", params=params)
            response.raise_for_status()
            data = response.json()
            return [SearchResult.from_dict(r) for r in data.get("results", [])]

    # ==========================================================================
    # Indexing Operations
    # ==========================================================================

    async def index_repository(
        self,
        repository: str,
        provider: Optional[str] = None,
        analyze_code: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> IndexResult:
        """Index a repository.

        Args:
            repository: Repository path (owner/repo or local path).
            provider: Provider type (github, gitlab, local, or auto).
            analyze_code: Whether to analyze code.
            progress_callback: Optional progress callback.

        Returns:
            IndexResult with indexing status.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            # Parse repository path
            if repository.startswith(("/", "./", "~/")):
                group = repository
                project = ""
                provider_type = "local"
            else:
                parts = repository.split("/")
                if len(parts) >= 2:
                    project = parts[-1]
                    group = "/".join(parts[:-1])
                else:
                    group = repository
                    project = ""
                provider_type = provider if provider and provider != "auto" else None

            try:
                await self._legacy_context.index_repository(
                    group, project,
                    provider_type=provider_type,
                    progress=progress_callback,
                    analyze_code=analyze_code,
                )
                return IndexResult(
                    status="success",
                    repository=repository,
                    metadata={"analyze_code": analyze_code},
                )
            except Exception as e:
                return IndexResult(
                    status="failed",
                    repository=repository,
                    error=str(e),
                )
        else:
            response = await self._http_session.post(
                "/v1/index",
                json={
                    "repository": repository,
                    "provider": provider,
                    "analyze_code": analyze_code,
                },
            )
            response.raise_for_status()
            return IndexResult.from_dict(response.json())

    async def index_group(
        self,
        group: str,
        provider: Optional[str] = None,
        include_subgroups: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> list[IndexResult]:
        """Index all repositories in a group/organization.

        Args:
            group: Group or organization name.
            provider: Provider type.
            include_subgroups: Include subgroups (GitLab only).
            progress_callback: Optional progress callback.

        Returns:
            List of IndexResult for each repository.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            provider_type = provider if provider and provider != "auto" else None
            result = await self._legacy_context.index_group(
                group,
                include_subgroups=include_subgroups,
                provider_type=provider_type,
                progress=progress_callback,
            )
            results = []
            for repo in result.get("indexed", []):
                results.append(IndexResult(status="success", repository=repo))
            for repo in result.get("failed", []):
                results.append(IndexResult(status="failed", repository=repo))
            return results
        else:
            response = await self._http_session.post(
                "/v1/index/group",
                json={
                    "group": group,
                    "provider": provider,
                    "include_subgroups": include_subgroups,
                },
            )
            response.raise_for_status()
            data = response.json()
            return [IndexResult.from_dict(r) for r in data.get("results", [])]

    # ==========================================================================
    # Documentation Operations
    # ==========================================================================

    async def get_documentation(
        self,
        library_id: str,
        topic: Optional[str] = None,
        max_tokens: Optional[int] = None,
        include: Optional[list[str]] = None,
        output_mode: str = "standard",
        query: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get documentation for a library.

        Args:
            library_id: Library identifier.
            topic: Optional topic filter.
            max_tokens: Maximum tokens to return.
            include: Additional content to include.
            output_mode: Output detail level.
            query: Relevance filter query.

        Returns:
            Documentation content dictionary.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            from repo_ctx.models import OutputMode

            mode_map = {
                "summary": OutputMode.SUMMARY,
                "standard": OutputMode.STANDARD,
                "full": OutputMode.FULL,
            }

            return await self._legacy_context.get_documentation(
                library_id,
                topic=topic,
                max_tokens=max_tokens,
                include_options=include,
                output_mode=mode_map.get(output_mode, OutputMode.STANDARD),
                query=query,
            )
        else:
            params = {
                "topic": topic,
                "max_tokens": max_tokens,
                "output_mode": output_mode,
                "query": query,
            }
            if include:
                params["include"] = ",".join(include)

            response = await self._http_session.get(
                f"/v1/docs/{library_id}",
                params={k: v for k, v in params.items() if v is not None},
            )
            response.raise_for_status()
            return response.json()

    # ==========================================================================
    # Analysis Operations
    # ==========================================================================

    async def analyze_code(
        self,
        code: str,
        file_path: str,
        language: Optional[str] = None,
    ) -> AnalysisResult:
        """Analyze source code.

        Args:
            code: Source code content.
            file_path: File path for language detection.
            language: Language override.

        Returns:
            AnalysisResult with symbols and dependencies.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            from repo_ctx.analysis import CodeAnalyzer

            analyzer = CodeAnalyzer()
            symbols, deps = analyzer.analyze_file(code, file_path)

            return AnalysisResult(
                file_path=file_path,
                language=language or analyzer.detect_language(file_path),
                symbols=[self._convert_symbol(s) for s in symbols],
                dependencies=deps,
            )
        else:
            response = await self._http_session.post(
                "/v1/analyze",
                json={
                    "code": code,
                    "file_path": file_path,
                    "language": language,
                },
            )
            response.raise_for_status()
            return AnalysisResult.from_dict(response.json())

    async def search_symbols(
        self,
        query: str,
        target: Optional[str] = None,
        symbol_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 10,
    ) -> list[Symbol]:
        """Search for code symbols.

        Args:
            query: Search query.
            target: Path or repository ID to search in.
            symbol_type: Filter by symbol type.
            language: Filter by language.
            limit: Maximum results.

        Returns:
            List of matching symbols.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            # Search in indexed repository or local path

            # This is a simplified implementation
            # Full implementation would search in storage
            return []
        else:
            params = {
                "query": query,
                "target": target,
                "symbol_type": symbol_type,
                "language": language,
                "limit": limit,
            }
            response = await self._http_session.get(
                "/v1/symbols/search",
                params={k: v for k, v in params.items() if v is not None},
            )
            response.raise_for_status()
            data = response.json()
            return [Symbol.from_dict(s) for s in data.get("symbols", [])]

    async def generate_dependency_graph(
        self,
        target: str,
        graph_type: str = "class",
        output_format: str = "json",
        depth: Optional[int] = None,
    ) -> Any:
        """Generate a dependency graph.

        Args:
            target: Path or repository ID.
            graph_type: Type of graph (file, module, class, function).
            output_format: Output format (json, dot, graphml).
            depth: Maximum traversal depth.

        Returns:
            Graph in requested format.
        """
        self._ensure_initialized()

        if self._mode == ClientMode.DIRECT:
            # Direct mode implementation
            from repo_ctx.analysis.dependency_graph import GraphType

            _graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }

            # Analyze code and build graph
            # Simplified - full implementation would handle paths/repos
            return {"nodes": [], "edges": []}
        else:
            params = {
                "target": target,
                "graph_type": graph_type,
                "output_format": output_format,
                "depth": depth,
            }
            response = await self._http_session.get(
                "/v1/graph",
                params={k: v for k, v in params.items() if v is not None},
            )
            response.raise_for_status()
            return response.json()

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    def _ensure_initialized(self) -> None:
        """Ensure client is initialized."""
        if not self._initialized:
            raise RuntimeError("Client not initialized. Call connect() first.")

    def _convert_library(self, raw: Any) -> Library:
        """Convert raw library data to Library model."""
        if isinstance(raw, dict):
            return Library.from_dict(raw)

        # Handle legacy Library model
        return Library(
            id=getattr(raw, "id", str(raw)),
            name=getattr(raw, "name", ""),
            group=getattr(raw, "group", ""),
            provider=getattr(raw, "provider", "github"),
            description=getattr(raw, "description", ""),
            versions=[],
            last_indexed=getattr(raw, "last_indexed", None),
        )

    def _convert_search_result(self, raw: Any, result_type: str) -> SearchResult:
        """Convert raw search result to SearchResult model."""
        if isinstance(raw, dict):
            return SearchResult.from_dict(raw)

        # Handle tuple (name, score) from fuzzy search
        if isinstance(raw, tuple) and len(raw) >= 2:
            return SearchResult(
                id=str(raw[0]),
                name=str(raw[0]),
                result_type=result_type,
                score=float(raw[1]) if len(raw) > 1 else 1.0,
            )

        return SearchResult(
            id=str(raw),
            name=str(raw),
            result_type=result_type,
        )

    def _convert_symbol(self, raw: Any) -> Symbol:
        """Convert raw symbol to Symbol model."""
        if isinstance(raw, dict):
            return Symbol.from_dict(raw)

        from repo_ctx.client.models import SymbolType, Visibility

        # Handle legacy Symbol model
        sym_type = getattr(raw, "symbol_type", "function")
        if hasattr(sym_type, "value"):
            sym_type = sym_type.value

        try:
            symbol_type = SymbolType(sym_type)
        except ValueError:
            symbol_type = SymbolType.FUNCTION

        vis = getattr(raw, "visibility", "public")
        try:
            visibility = Visibility(vis)
        except ValueError:
            visibility = Visibility.PUBLIC

        return Symbol(
            name=getattr(raw, "name", ""),
            qualified_name=getattr(raw, "qualified_name", ""),
            symbol_type=symbol_type,
            file_path=getattr(raw, "file_path", ""),
            line_start=getattr(raw, "line_start", 0),
            line_end=getattr(raw, "line_end", 0),
            signature=getattr(raw, "signature", None),
            visibility=visibility,
            documentation=getattr(raw, "docstring", None),
        )


def create_client(
    config: Optional[Config] = None,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> RepoCtxClient:
    """Create a new RepoCtxClient.

    Factory function for creating clients.

    Args:
        config: Configuration for direct mode.
        api_url: API URL for HTTP mode.
        api_key: API key for authentication.

    Returns:
        Configured RepoCtxClient.
    """
    return RepoCtxClient(config=config, api_url=api_url, api_key=api_key)
