"""MCP Server Context using the unified RepoCtxClient.

This module provides MCPServerContext which wraps the unified RepoCtxClient
to provide a consistent interface for MCP tool handlers.
"""

from typing import Any, Optional

from repo_ctx.config import Config
from repo_ctx.core import GitLabContext
from repo_ctx.client import RepoCtxClient


class MCPServerContext:
    """Bridge context for MCP server using unified client.

    Provides access to the unified RepoCtxClient while maintaining
    backward compatibility with existing tool handlers.

    Attributes:
        client: The unified RepoCtxClient.
        legacy: Access to legacy GitLabContext (via client).
        storage: Content storage (via client).
    """

    def __init__(
        self,
        config: Config,
        legacy_context: Optional[GitLabContext] = None,
    ) -> None:
        """Initialize the MCP server context.

        Args:
            config: Configuration object.
            legacy_context: Optional pre-initialized GitLabContext (unused, for API compat).
        """
        self._config = config

        # Use unified client
        self._client = RepoCtxClient(config=config)
        self._initialized = False

    @property
    def client(self) -> RepoCtxClient:
        """Get the unified client."""
        return self._client

    @property
    def legacy(self) -> Optional[GitLabContext]:
        """Get the legacy GitLabContext for backwards compatibility."""
        if self._client and self._client._legacy_context:
            return self._client._legacy_context
        return None

    @property
    def storage(self):
        """Get the storage from client (for backwards compatibility)."""
        if self._client and self._client._legacy_context:
            return self._client._legacy_context.storage
        return None

    @property
    def services(self):
        """Get the ServiceContext (for backwards compatibility)."""
        if self._client:
            return self._client._service_context
        return None

    @property
    def repository(self):
        """Get the RepositoryService (for backwards compatibility)."""
        if self._client:
            return self._client._repository_service
        return None

    @property
    def indexing(self):
        """Get the IndexingService (for backwards compatibility)."""
        if self._client:
            return self._client._indexing_service
        return None

    @property
    def search(self):
        """Get the SearchService (for backwards compatibility)."""
        if self._client:
            return self._client._search_service
        return None

    @property
    def analysis(self):
        """Get the AnalysisService (for backwards compatibility)."""
        if self._client:
            return self._client._analysis_service
        return None

    async def init(self) -> None:
        """Initialize the MCP server context."""
        if self._initialized:
            return

        await self._client.connect()
        self._initialized = True

    async def close(self) -> None:
        """Close the context and release resources."""
        if self._client:
            await self._client.close()
        self._initialized = False

    # ==========================================================================
    # Legacy method proxies (for backwards compatibility)
    # These delegate to the unified client
    # ==========================================================================

    async def search_libraries(self, query: str):
        """Search for libraries by name (legacy method)."""
        if self.legacy:
            return await self.legacy.search_libraries(query)
        results = await self._client.search_libraries(query, fuzzy=False)
        return [r.name for r in results]

    async def fuzzy_search_libraries(self, query: str, limit: int = 10):
        """Fuzzy search for libraries (legacy method)."""
        if self.legacy:
            return await self.legacy.fuzzy_search_libraries(query, limit)
        results = await self._client.search_libraries(query, limit=limit, fuzzy=True)
        return [(r.name, r.score) for r in results]

    async def index_repository(self, group: str, project: str, **kwargs):
        """Index a repository (legacy method)."""
        if self.legacy:
            return await self.legacy.index_repository(group, project, **kwargs)
        repository = f"{group}/{project}" if project else group
        provider = kwargs.get('provider_type')
        analyze_code = kwargs.get('analyze_code', True)
        progress = kwargs.get('progress')
        result = await self._client.index_repository(
            repository=repository,
            provider=provider,
            analyze_code=analyze_code,
            progress_callback=progress,
        )
        return {"status": result.status, "repository": result.repository}

    async def index_group(self, group: str, include_subgroups: bool = True, **kwargs):
        """Index a group of repositories (legacy method)."""
        if self.legacy:
            return await self.legacy.index_group(group, include_subgroups, **kwargs)
        provider = kwargs.get('provider_type')
        progress = kwargs.get('progress')
        results = await self._client.index_group(
            group=group,
            provider=provider,
            include_subgroups=include_subgroups,
            progress_callback=progress,
        )
        indexed = [r.repository for r in results if r.status == "success"]
        failed = [r.repository for r in results if r.status == "failed"]
        return {"indexed": indexed, "failed": failed}

    async def get_documentation(self, library_id: str, topic: Optional[str] = None, page: int = 1, **kwargs):
        """Get documentation for a library (legacy method)."""
        if self.legacy:
            return await self.legacy.get_documentation(library_id, topic, page, **kwargs)
        return await self._client.get_documentation(
            library_id=library_id,
            topic=topic,
            **kwargs,
        )

    async def list_all_libraries(self, provider_filter: Optional[str] = None):
        """List all indexed libraries (legacy method)."""
        if self.legacy:
            return await self.legacy.list_all_libraries(provider_filter)
        libraries = await self._client.list_libraries(provider=provider_filter)
        return libraries

    def _get_repository_url(self, lib):
        """Get repository URL (legacy method)."""
        if self.legacy:
            return self.legacy._get_repository_url(lib)
        if hasattr(lib, 'metadata'):
            return lib.metadata.get('url', '')
        return ''

    # ==========================================================================
    # Service-based methods (analysis operations)
    # ==========================================================================

    def analyze_code(
        self,
        code: str,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze source code.

        Args:
            code: Source code content.
            file_path: Path to the file.
            language: Optional language override.

        Returns:
            Analysis results dictionary.
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
        """Get list of supported languages.

        Returns:
            List of supported language names.
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

    async def health_check(self) -> dict[str, Any]:
        """Check health of all components.

        Returns:
            Health status dictionary.
        """
        result = {
            "client": "healthy" if self._client and self._client.is_initialized else "not initialized",
            "overall": "healthy",
        }

        # Check storage
        if self.storage:
            try:
                result["content_storage"] = {"status": "healthy"}
            except Exception as e:
                result["content_storage"] = {"status": "unhealthy", "error": str(e)}
                result["overall"] = "unhealthy"

        return result
