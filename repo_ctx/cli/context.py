"""CLI Context using the unified RepoCtxClient.

This module provides CLIContext which wraps RepoCtxClient to provide
a consistent interface for CLI commands. Supports legacy mode fallback.
"""

from typing import Any, Optional

from repo_ctx.config import Config
from repo_ctx.core import GitLabContext
from repo_ctx.client import RepoCtxClient


class CLIContext:
    """Context for CLI operations.

    Uses the unified RepoCtxClient by default, with fallback to legacy
    GitLabContext when legacy_mode=True.

    Attributes:
        use_legacy: Whether to use legacy mode.
        legacy: The GitLabContext for backwards compatibility.
        client: The unified RepoCtxClient (when not in legacy mode).
    """

    def __init__(
        self,
        config: Config,
        legacy_mode: bool = False,
        legacy_context: Optional[GitLabContext] = None,
    ) -> None:
        """Initialize the CLI context.

        Args:
            config: Configuration object.
            legacy_mode: If True, use legacy GitLabContext directly.
            legacy_context: Optional pre-initialized GitLabContext.
        """
        self._config = config
        self._use_legacy = legacy_mode

        # Legacy context (used in legacy mode)
        self._legacy = legacy_context or GitLabContext(config) if legacy_mode else None

        # Unified client (used in normal mode)
        self._client: Optional[RepoCtxClient] = None if legacy_mode else RepoCtxClient(config=config)

        self._initialized = False

    @property
    def use_legacy(self) -> bool:
        """Whether using legacy mode."""
        return self._use_legacy

    @property
    def legacy(self) -> Optional[GitLabContext]:
        """Get the legacy GitLabContext (None if not in legacy mode)."""
        return self._legacy

    @property
    def storage(self):
        """Get storage from context."""
        if self._use_legacy and self._legacy:
            return self._legacy.storage
        elif self._client and self._client._legacy_context:
            return self._client._legacy_context.storage
        return None

    @property
    def client(self) -> Optional[RepoCtxClient]:
        """Get the unified client (None in legacy mode)."""
        return self._client

    async def init(self) -> None:
        """Initialize the CLI context."""
        if self._initialized:
            return

        if self._use_legacy and self._legacy:
            await self._legacy.init()
        elif self._client:
            await self._client.connect()

        self._initialized = True

    async def close(self) -> None:
        """Close the CLI context and release resources."""
        if self._client:
            await self._client.close()
        self._initialized = False

    # ==========================================================================
    # Indexing Operations
    # ==========================================================================

    async def index_repository(
        self,
        group: str,
        project: str,
        provider_type: Optional[str] = None,
        progress: Any = None,
        analyze_code: bool = True,
    ) -> dict[str, Any]:
        """Index a repository.

        Args:
            group: Repository group/owner.
            project: Repository/project name.
            provider_type: Optional provider type override.
            progress: Optional progress callback.
            analyze_code: Whether to analyze code (default True).

        Returns:
            Indexing result dictionary.
        """
        if self._use_legacy and self._legacy:
            await self._legacy.index_repository(
                group, project,
                provider_type=provider_type,
                progress=progress,
                analyze_code=analyze_code,
            )
            return {"status": "completed", "repository": f"{group}/{project}"}

        # Use unified client
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        repository = f"{group}/{project}" if project else group
        result = await self._client.index_repository(
            repository=repository,
            provider=provider_type,
            analyze_code=analyze_code,
            progress_callback=progress,
        )
        return {
            "status": result.status,
            "repository": result.repository,
            "error": result.error,
        }

    async def index_group(
        self,
        group: str,
        include_subgroups: bool = True,
        provider_type: Optional[str] = None,
        progress: Any = None,
    ) -> dict[str, Any]:
        """Index all repositories in a group.

        Args:
            group: Group/organization name.
            include_subgroups: Include subgroups (GitLab only).
            provider_type: Optional provider type override.
            progress: Optional progress callback.

        Returns:
            Result with indexed and failed lists.
        """
        if self._use_legacy and self._legacy:
            return await self._legacy.index_group(
                group,
                include_subgroups=include_subgroups,
                provider_type=provider_type,
                progress=progress,
            )

        # Use unified client
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        results = await self._client.index_group(
            group=group,
            provider=provider_type,
            include_subgroups=include_subgroups,
            progress_callback=progress,
        )

        indexed = [r.repository for r in results if r.status == "success"]
        failed = [r.repository for r in results if r.status == "failed"]
        return {"indexed": indexed, "failed": failed}

    # ==========================================================================
    # Search Operations
    # ==========================================================================

    async def search_libraries(self, query: str) -> list[Any]:
        """Search for libraries by exact name match.

        Args:
            query: Search query.

        Returns:
            List of matching libraries.
        """
        if self._use_legacy and self._legacy:
            return await self._legacy.search_libraries(query)

        # Use unified client (non-fuzzy search)
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        results = await self._client.search_libraries(query, fuzzy=False)
        return [r.name for r in results]

    async def fuzzy_search_libraries(self, query: str, limit: int = 10) -> list[Any]:
        """Fuzzy search for libraries.

        Args:
            query: Search query.
            limit: Maximum results.

        Returns:
            List of matching libraries with scores.
        """
        if self._use_legacy and self._legacy:
            return await self._legacy.fuzzy_search_libraries(query, limit)

        # Use unified client
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        results = await self._client.search_libraries(query, limit=limit, fuzzy=True)
        return [(r.name, r.score) for r in results]

    async def list_all_libraries(self, provider_filter: Optional[str] = None) -> list[Any]:
        """List all indexed libraries.

        Args:
            provider_filter: Optional provider filter.

        Returns:
            List of all libraries.
        """
        if self._use_legacy and self._legacy:
            return await self._legacy.list_all_libraries(provider_filter)

        # Use unified client
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        libraries = await self._client.list_libraries(provider=provider_filter)
        # Return as objects with expected attributes for CLI compatibility
        return [_LibraryAdapter(lib) for lib in libraries]

    # ==========================================================================
    # Documentation Operations
    # ==========================================================================

    async def get_documentation(
        self,
        library_id: str,
        topic: Optional[str] = None,
        page: int = 1,
        **kwargs,
    ) -> dict[str, Any]:
        """Get documentation for a library.

        Args:
            library_id: Library identifier.
            topic: Optional topic filter.
            page: Page number.
            **kwargs: Additional options.

        Returns:
            Documentation content.
        """
        if self._use_legacy and self._legacy:
            return await self._legacy.get_documentation(library_id, topic, page, **kwargs)

        # Use unified client
        if self._client is None:
            raise RuntimeError("Client not initialized. Call init() first.")

        return await self._client.get_documentation(
            library_id=library_id,
            topic=topic,
            **kwargs,
        )

    # ==========================================================================
    # Analysis Operations
    # ==========================================================================

    def analyze_code(
        self,
        code: str,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze source code synchronously.

        Args:
            code: Source code content.
            file_path: Path to the file.
            language: Optional language override.

        Returns:
            Analysis results with symbols and dependencies.
        """
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer()
        symbols, deps = analyzer.analyze_file(code, file_path)
        return {
            "file_path": file_path,
            "language": language or analyzer.detect_language(file_path),
            "symbols": [
                {
                    "name": s.name,
                    "qualified_name": s.qualified_name,
                    "symbol_type": s.symbol_type.value,
                    "file_path": s.file_path,
                    "line_start": s.line_start,
                    "line_end": s.line_end,
                    "signature": s.signature,
                    "visibility": s.visibility,
                }
                for s in symbols
            ],
            "dependencies": deps,
        }

    def get_supported_languages(self) -> list[str]:
        """Get list of supported programming languages.

        Returns:
            List of language names.
        """
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer()
        return sorted(set(analyzer.language_map.values()))

    def generate_dependency_graph(
        self,
        symbols: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
        graph_type: str = "class",
        output_format: str = "json",
    ) -> Any:
        """Generate dependency graph.

        Args:
            symbols: List of symbol dictionaries.
            dependencies: List of dependency dictionaries.
            graph_type: Type of graph.
            output_format: Output format.

        Returns:
            Graph in requested format.
        """
        from repo_ctx.analysis.dependency_graph import DependencyGraph, GraphType
        from repo_ctx.analysis.models import Symbol, SymbolType

        # Convert to Symbol objects
        symbol_objects = []
        for s in symbols:
            sym_type = s.get("symbol_type", "function")
            if isinstance(sym_type, str):
                try:
                    sym_type = SymbolType(sym_type)
                except ValueError:
                    sym_type = SymbolType.FUNCTION

            symbol_objects.append(Symbol(
                name=s.get("name", ""),
                qualified_name=s.get("qualified_name", s.get("name", "")),
                symbol_type=sym_type,
                file_path=s.get("file_path", ""),
                line_start=s.get("line_start", 0),
                line_end=s.get("line_end", 0),
            ))

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
            "symbol": GraphType.SYMBOL,
        }

        builder = DependencyGraph()
        graph = builder.build(
            symbols=symbol_objects,
            dependencies=dependencies,
            graph_type=graph_type_map.get(graph_type, GraphType.CLASS),
        )

        if output_format == "dot":
            return builder.to_dot(graph)
        elif output_format == "graphml":
            return builder.to_graphml(graph)
        else:
            import json
            return json.loads(builder.to_json(graph))

    # ==========================================================================
    # Utility Methods
    # ==========================================================================

    def _get_repository_url(self, lib: Any) -> str:
        """Get repository URL for a library."""
        if self._use_legacy and self._legacy:
            return self._legacy._get_repository_url(lib)

        # Extract from library
        if hasattr(lib, 'metadata'):
            return lib.metadata.get('url', '')
        return ''


class _LibraryAdapter:
    """Adapter to make Library models work with existing CLI code.

    Provides backward-compatible attributes expected by CLI commands.
    """

    def __init__(self, library):
        """Initialize adapter.

        Args:
            library: Library model from client.
        """
        self._lib = library

    @property
    def group_name(self) -> str:
        """Get group name."""
        return self._lib.group

    @property
    def project_name(self) -> str:
        """Get project name."""
        return self._lib.name

    @property
    def name(self) -> str:
        """Get full name."""
        return f"{self._lib.group}/{self._lib.name}"

    @property
    def provider(self) -> str:
        """Get provider."""
        return self._lib.provider

    @property
    def description(self) -> str:
        """Get description."""
        return self._lib.description

    @property
    def id(self) -> str:
        """Get library ID."""
        return self._lib.id

    @property
    def last_indexed(self):
        """Get last indexed time."""
        return self._lib.last_indexed

    @property
    def versions(self) -> list[str]:
        """Get versions."""
        return self._lib.versions

    def __getattr__(self, name):
        """Forward unknown attributes to underlying library."""
        return getattr(self._lib, name)
