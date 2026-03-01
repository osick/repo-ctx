"""Analysis service for code analysis operations.

This module provides the AnalysisService which handles
code analysis, symbol extraction, and dependency graph generation.
"""

import logging
from typing import Any, Optional, TYPE_CHECKING

from repo_ctx.services.base import BaseService, ServiceContext
from repo_ctx.analysis.code_analyzer import CodeAnalyzer
from repo_ctx.analysis.dependency_graph import DependencyGraph, GraphType
from repo_ctx.storage.protocols import GraphNode, GraphRelationship

if TYPE_CHECKING:
    from repo_ctx.services.embedding import EmbeddingService

logger = logging.getLogger("repo_ctx.services.analysis")


class AnalysisService(BaseService):
    """Service for code analysis operations.

    Handles symbol extraction, dependency analysis, and graph generation.
    Supports persisting analysis to graph storage for semantic queries.
    """

    def __init__(
        self,
        context: ServiceContext,
        embedding_service: Optional["EmbeddingService"] = None,
    ) -> None:
        """Initialize the analysis service.

        Args:
            context: ServiceContext with storage backends.
            embedding_service: Optional embedding service for symbol embeddings.
        """
        super().__init__(context)
        self._analyzer = CodeAnalyzer(use_treesitter=True)
        self._graph_builder = DependencyGraph()
        self._embedding_service = embedding_service

    @property
    def embedding_service(self) -> Optional["EmbeddingService"]:
        """Get the embedding service."""
        return self._embedding_service

    def set_embedding_service(self, service: "EmbeddingService") -> None:
        """Set the embedding service."""
        self._embedding_service = service

    def get_supported_languages(self) -> list[str]:
        """Get list of supported programming languages.

        Returns:
            List of language names.
        """
        # Get unique languages from the analyzer's language map
        languages = set(self._analyzer.language_map.values())
        return sorted(list(languages))

    def analyze_code(
        self,
        code: str,
        file_path: str,
        language: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze source code and extract symbols and dependencies.

        Args:
            code: Source code content.
            file_path: Path to the file (used for language detection).
            language: Optional language override.

        Returns:
            Dictionary with symbols, dependencies, and metadata.
        """
        # Detect language if not provided
        detected_language = language or self._analyzer.detect_language(file_path)

        if not detected_language:
            return {
                "file_path": file_path,
                "language": None,
                "symbols": [],
                "dependencies": [],
            }

        # Analyze the file
        symbols, dependencies = self._analyzer.analyze_file(code, file_path)

        # Convert symbols to dictionaries
        symbol_dicts = []
        for sym in symbols:
            symbol_dict = {
                "name": sym.name,
                "qualified_name": sym.qualified_name,
                "symbol_type": sym.symbol_type.value if hasattr(sym.symbol_type, 'value') else str(sym.symbol_type),
                "file_path": sym.file_path,
                "line_start": sym.line_start,
                "line_end": sym.line_end,
            }
            # Add optional fields if present
            if hasattr(sym, 'signature') and sym.signature:
                symbol_dict["signature"] = sym.signature
            if hasattr(sym, 'docstring') and sym.docstring:
                symbol_dict["docstring"] = sym.docstring
            if hasattr(sym, 'visibility') and sym.visibility:
                symbol_dict["visibility"] = sym.visibility
            if hasattr(sym, 'parent_name') and sym.parent_name:
                symbol_dict["parent_name"] = sym.parent_name

            symbol_dicts.append(symbol_dict)

        # Convert dependencies to dictionaries
        dep_dicts = []
        for dep in dependencies:
            if hasattr(dep, '__dict__'):
                dep_dict = {
                    "source": getattr(dep, 'source', None),
                    "target": getattr(dep, 'target', None),
                    "dependency_type": getattr(dep, 'dependency_type', None),
                }
                if hasattr(dep, 'file_path'):
                    dep_dict["file_path"] = dep.file_path
                dep_dicts.append(dep_dict)
            elif isinstance(dep, dict):
                dep_dicts.append(dep)

        return {
            "file_path": file_path,
            "language": detected_language,
            "symbols": symbol_dicts,
            "dependencies": dep_dicts,
        }

    def generate_dependency_graph(
        self,
        symbols: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
        graph_type: str = "class",
        output_format: str = "json",
    ) -> Any:
        """Generate a dependency graph from symbols and dependencies.

        Args:
            symbols: List of symbol dictionaries.
            dependencies: List of dependency dictionaries.
            graph_type: Type of graph (file, module, class, function, symbol).
            output_format: Output format (json, dot, graphml).

        Returns:
            Graph in requested format.
        """
        from repo_ctx.analysis.models import Symbol, SymbolType

        # Convert dictionaries back to Symbol objects
        symbol_objects = []
        for sym_dict in symbols:
            sym_type = sym_dict.get("symbol_type", "function")
            if isinstance(sym_type, str):
                try:
                    sym_type = SymbolType(sym_type)
                except ValueError:
                    sym_type = SymbolType.FUNCTION

            symbol = Symbol(
                name=sym_dict.get("name", ""),
                qualified_name=sym_dict.get("qualified_name", sym_dict.get("name", "")),
                symbol_type=sym_type,
                file_path=sym_dict.get("file_path", ""),
                line_start=sym_dict.get("line_start", 0),
                line_end=sym_dict.get("line_end", 0),
                signature=sym_dict.get("signature"),
                documentation=sym_dict.get("docstring"),
                visibility=sym_dict.get("visibility", "public"),
            )
            symbol_objects.append(symbol)

        # Map graph type string to enum
        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
            "symbol": GraphType.SYMBOL,
        }
        graph_type_enum = graph_type_map.get(graph_type, GraphType.CLASS)

        # Build the graph
        graph_result = self._graph_builder.build(
            symbols=symbol_objects,
            dependencies=dependencies,
            graph_type=graph_type_enum,
        )

        # Export in requested format
        if output_format == "dot":
            return self._graph_builder.to_dot(graph_result)
        elif output_format == "graphml":
            return self._graph_builder.to_graphml(graph_result)
        else:  # json
            # Return as dictionary structure
            json_str = self._graph_builder.to_json(graph_result)
            import json
            return json.loads(json_str)

    async def analyze_repository(
        self,
        repository_id: str,
        language: Optional[str] = None,
        save_results: bool = True,
    ) -> dict[str, Any]:
        """Analyze all code files in a repository.

        Args:
            repository_id: Repository identifier.
            language: Optional language filter.
            save_results: Whether to save results to storage.

        Returns:
            Dictionary with analysis summary.
        """
        # This would integrate with the indexing service to get files
        # For now, return a placeholder
        return {
            "repository_id": repository_id,
            "status": "not_implemented",
            "message": "Full repository analysis requires indexing first",
        }

    async def persist_analysis_to_graph(
        self,
        library_id: str,
        symbols: list[dict[str, Any]],
        dependencies: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Persist analysis results to graph storage.

        Creates nodes for symbols and relationships for dependencies.

        Args:
            library_id: Library identifier.
            symbols: List of symbol dictionaries.
            dependencies: List of dependency dictionaries.

        Returns:
            Dictionary with counts of nodes and relationships created.
        """
        if self.graph_storage is None:
            return {"nodes": 0, "relationships": 0}

        # Create nodes for symbols
        nodes = []
        for sym in symbols:
            symbol_type = sym.get("symbol_type", "function")
            labels = ["Symbol", symbol_type.capitalize()]

            # Add visibility label
            visibility = sym.get("visibility", "public")
            if visibility == "public":
                labels.append("PublicAPI")

            node = GraphNode(
                id=f"{library_id}:{sym.get('qualified_name', sym.get('name'))}",
                labels=labels,
                properties={
                    "name": sym.get("name"),
                    "qualified_name": sym.get("qualified_name"),
                    "file_path": sym.get("file_path"),
                    "line_start": sym.get("line_start"),
                    "line_end": sym.get("line_end"),
                    "signature": sym.get("signature"),
                    "docstring": sym.get("docstring"),
                    "visibility": visibility,
                    "library_id": library_id,
                    "language": sym.get("language"),
                },
            )
            nodes.append(node)

        await self.graph_storage.create_nodes(nodes)

        # Create relationships for dependencies
        relationships = []
        for dep in dependencies:
            source = dep.get("source")
            target = dep.get("target")
            dep_type = dep.get("dependency_type", "DEPENDS_ON")

            if source and target:
                rel = GraphRelationship(
                    from_id=f"{library_id}:{source}",
                    to_id=f"{library_id}:{target}",
                    type=dep_type.upper().replace(" ", "_"),
                    properties={
                        "file_path": dep.get("file_path"),
                        "library_id": library_id,
                    },
                )
                relationships.append(rel)

        await self.graph_storage.create_relationships(relationships)

        # Generate embeddings for symbols if embedding service available
        embeddings_count = 0
        if self._embedding_service is not None:
            for sym in symbols:
                try:
                    await self._embedding_service.embed_symbol(
                        symbol_id=f"{library_id}:{sym.get('qualified_name', sym.get('name'))}",
                        name=sym.get("name", ""),
                        qualified_name=sym.get("qualified_name", sym.get("name", "")),
                        library_id=library_id,
                        file_path=sym.get("file_path", ""),
                        signature=sym.get("signature"),
                        documentation=sym.get("docstring"),
                        metadata={
                            "symbol_type": sym.get("symbol_type"),
                            "visibility": sym.get("visibility"),
                            "language": sym.get("language"),
                        },
                    )
                    embeddings_count += 1
                except Exception as e:
                    logger.warning(f"Failed to embed symbol: {e}")

        return {
            "nodes": len(nodes),
            "relationships": len(relationships),
            "embeddings": embeddings_count,
        }

    async def query_call_graph(
        self,
        symbol_name: str,
        library_id: Optional[str] = None,
        depth: int = 2,
        direction: str = "both",
    ) -> dict[str, Any]:
        """Query the call graph for a symbol.

        Args:
            symbol_name: Symbol name to query.
            library_id: Optional library filter.
            depth: Maximum traversal depth.
            direction: "incoming", "outgoing", or "both".

        Returns:
            Graph result with nodes and relationships.
        """
        if self.graph_storage is None:
            return {"symbol": symbol_name, "nodes": [], "relationships": []}

        # Construct full symbol ID if library specified
        full_name = f"{library_id}:{symbol_name}" if library_id else symbol_name

        try:
            result = await self.graph_storage.get_call_graph(
                symbol_name=full_name,
                depth=depth,
                direction=direction,
            )

            return {
                "symbol": symbol_name,
                "nodes": [
                    {
                        "id": n.id,
                        "labels": n.labels,
                        "properties": n.properties,
                    }
                    for n in result.nodes
                ],
                "relationships": [
                    {
                        "from_id": r.from_id,
                        "to_id": r.to_id,
                        "type": r.type,
                        "properties": r.properties,
                    }
                    for r in result.relationships
                ],
            }
        except Exception as e:
            logger.warning(f"Error querying call graph: {e}")
            return {"symbol": symbol_name, "nodes": [], "relationships": []}

    async def find_symbols_by_type(
        self,
        symbol_type: str,
        library_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Find symbols by type using graph storage.

        Args:
            symbol_type: Type of symbol (class, function, method, etc.).
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            List of matching symbols.
        """
        if self.graph_storage is None:
            return []

        properties = {}
        if library_id:
            properties["library_id"] = library_id

        nodes = await self.graph_storage.find_nodes_by_label(
            label=symbol_type.capitalize(),
            properties=properties,
            limit=limit,
        )

        return [
            {
                "id": n.id,
                "name": n.properties.get("name"),
                "qualified_name": n.properties.get("qualified_name"),
                "file_path": n.properties.get("file_path"),
                "signature": n.properties.get("signature"),
                "visibility": n.properties.get("visibility"),
            }
            for n in nodes
        ]

    async def find_public_api(
        self,
        library_id: str,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Find public API symbols in a library.

        Args:
            library_id: Library identifier.
            limit: Maximum results.

        Returns:
            List of public API symbols.
        """
        if self.graph_storage is None:
            return []

        nodes = await self.graph_storage.find_nodes_by_label(
            label="PublicAPI",
            properties={"library_id": library_id},
            limit=limit,
        )

        return [
            {
                "id": n.id,
                "name": n.properties.get("name"),
                "qualified_name": n.properties.get("qualified_name"),
                "symbol_type": [l for l in n.labels if l not in ("Symbol", "PublicAPI")],
                "file_path": n.properties.get("file_path"),
                "signature": n.properties.get("signature"),
            }
            for n in nodes
        ]

    async def semantic_symbol_search(
        self,
        query: str,
        library_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search symbols using semantic similarity.

        Uses embedding service for vector search, then enriches
        results with graph data.

        Args:
            query: Natural language query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            List of semantically similar symbols with graph context.
        """
        if self._embedding_service is None:
            return []

        # Search for similar symbols
        results = await self._embedding_service.search_similar_symbols(
            query=query,
            library_id=library_id,
            limit=limit,
        )

        # Enrich with graph data if available
        if self.graph_storage is not None:
            for result in results:
                node = await self.graph_storage.get_node(result["id"])
                if node:
                    result["labels"] = node.labels
                    result["graph_properties"] = node.properties

        return results

    async def delete_library_analysis(self, library_id: str) -> dict[str, int]:
        """Delete all analysis data for a library.

        Args:
            library_id: Library identifier.

        Returns:
            Dictionary with deletion counts.
        """
        counts = {}

        # Delete from graph storage
        if self.graph_storage is not None:
            counts["graph_nodes"] = await self.graph_storage.delete_by_library(library_id)

        # Delete embeddings
        if self._embedding_service is not None:
            embedding_counts = await self._embedding_service.delete_library_embeddings(library_id)
            counts["embeddings"] = sum(embedding_counts.values())

        return counts
