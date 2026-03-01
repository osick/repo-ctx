"""Combined search service across all storage backends.

This module provides unified search across:
- Content storage (SQLite) - text search
- Vector storage (Qdrant) - semantic similarity
- Graph storage (Neo4j/NetworkX) - relationship queries

Results are merged, deduplicated, and ranked.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from repo_ctx.services.base import BaseService, ServiceContext

logger = logging.getLogger("repo_ctx.services.combined_search")


@dataclass
class SearchResult:
    """Unified search result."""

    id: str
    source: str  # "content", "vector", or "graph"
    score: float = 0.0
    file_path: Optional[str] = None
    library_id: Optional[str] = None
    content_preview: Optional[str] = None
    name: Optional[str] = None
    qualified_name: Optional[str] = None
    symbol_type: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CombinedSearchResponse:
    """Response from combined search."""

    query: str
    total: int
    results: list[SearchResult]
    sources_used: list[str]
    content_count: int = 0
    vector_count: int = 0
    graph_count: int = 0


class CombinedSearchService(BaseService):
    """Service for combined search across all storage backends.

    Provides unified search with result merging and ranking.
    """

    def __init__(
        self,
        context: ServiceContext,
        embedding_service: Optional[Any] = None,
    ) -> None:
        """Initialize the combined search service.

        Args:
            context: ServiceContext with storage backends.
            embedding_service: Optional embedding service for semantic search.
        """
        super().__init__(context)
        self._embedding_service = embedding_service

    @property
    def embedding_service(self) -> Optional[Any]:
        """Get the embedding service."""
        return self._embedding_service

    def set_embedding_service(self, service: Any) -> None:
        """Set the embedding service."""
        self._embedding_service = service

    async def search(
        self,
        query: str,
        library_id: Optional[str] = None,
        search_sources: Optional[list[str]] = None,
        limit: int = 20,
        include_content: bool = True,
        include_symbols: bool = True,
        boost_exact_match: float = 2.0,
        boost_semantic: float = 1.5,
        boost_graph: float = 1.2,
    ) -> CombinedSearchResponse:
        """Perform combined search across all storage backends.

        Args:
            query: Search query string.
            library_id: Optional library ID to scope search.
            search_sources: List of sources to search ("content", "vector", "graph").
                           Defaults to all available.
            limit: Maximum results per source.
            include_content: Include document content results.
            include_symbols: Include symbol results.
            boost_exact_match: Score boost for exact text matches.
            boost_semantic: Score boost for semantic matches.
            boost_graph: Score boost for graph matches.

        Returns:
            CombinedSearchResponse with merged results.
        """
        if search_sources is None:
            search_sources = ["content", "vector", "graph"]

        results: list[SearchResult] = []
        sources_used = []
        content_count = 0
        vector_count = 0
        graph_count = 0

        # Search content storage
        if "content" in search_sources:
            content_results = await self._search_content(
                query=query,
                library_id=library_id,
                limit=limit,
                include_content=include_content,
                include_symbols=include_symbols,
            )
            for r in content_results:
                r.score *= boost_exact_match
            results.extend(content_results)
            content_count = len(content_results)
            if content_results:
                sources_used.append("content")

        # Search vector storage
        if "vector" in search_sources and self._embedding_service is not None:
            vector_results = await self._search_vector(
                query=query,
                library_id=library_id,
                limit=limit,
                include_content=include_content,
                include_symbols=include_symbols,
            )
            for r in vector_results:
                r.score *= boost_semantic
            results.extend(vector_results)
            vector_count = len(vector_results)
            if vector_results:
                sources_used.append("vector")

        # Search graph storage
        if "graph" in search_sources and self.graph_storage is not None:
            graph_results = await self._search_graph(
                query=query,
                library_id=library_id,
                limit=limit,
            )
            for r in graph_results:
                r.score *= boost_graph
            results.extend(graph_results)
            graph_count = len(graph_results)
            if graph_results:
                sources_used.append("graph")

        # Merge and deduplicate results
        merged = self._merge_results(results)

        # Sort by score and limit
        merged.sort(key=lambda x: x.score, reverse=True)
        merged = merged[:limit]

        return CombinedSearchResponse(
            query=query,
            total=len(merged),
            results=merged,
            sources_used=sources_used,
            content_count=content_count,
            vector_count=vector_count,
            graph_count=graph_count,
        )

    async def _search_content(
        self,
        query: str,
        library_id: Optional[str],
        limit: int,
        include_content: bool,
        include_symbols: bool,
    ) -> list[SearchResult]:
        """Search content storage (SQLite).

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.
            include_content: Include documents.
            include_symbols: Include symbols.

        Returns:
            List of SearchResult from content storage.
        """
        results = []
        query_lower = query.lower()

        if include_content:
            # Search documents
            try:
                # Get library ID for filtering
                version_id = None
                if library_id:
                    library = await self.content_storage.get_library(library_id)
                    if library:
                        version_id = library.id

                # Get all libraries if not filtering
                if version_id is None:
                    all_libs = await self.content_storage.get_all_libraries()
                    if all_libs:
                        version_id = all_libs[0].id

                if version_id:
                    documents = await self.content_storage.get_documents(
                        version_id=version_id,
                        page=1,
                        page_size=limit * 2,
                    )

                    for doc in documents:
                        content_lower = doc.content.lower()
                        path_lower = doc.file_path.lower()

                        if query_lower in content_lower or query_lower in path_lower:
                            # Calculate simple score based on match count
                            match_count = content_lower.count(query_lower)
                            score = min(1.0, 0.5 + match_count * 0.1)

                            results.append(SearchResult(
                                id=f"doc:{doc.id or doc.file_path}",
                                source="content",
                                score=score,
                                file_path=doc.file_path,
                                library_id=library_id,
                                content_preview=doc.content[:200] if len(doc.content) > 200 else doc.content,
                                metadata={
                                    "content_type": doc.content_type,
                                    "quality_score": doc.quality_score,
                                },
                            ))

                            if len(results) >= limit:
                                break

            except Exception as e:
                logger.warning(f"Error searching content storage: {e}")

        if include_symbols:
            # Search symbols
            try:
                if library_id:
                    library = await self.content_storage.get_library(library_id)
                    if library and library.id:
                        symbols = await self.content_storage.search_symbols(
                            repository_id=library.id,
                            query=query,
                            limit=limit,
                        )

                        for sym in symbols:
                            results.append(SearchResult(
                                id=f"sym:{sym.get('qualified_name', sym.get('name'))}",
                                source="content",
                                score=0.8,  # Base score for symbol matches
                                file_path=sym.get("file_path"),
                                library_id=library_id,
                                name=sym.get("name"),
                                qualified_name=sym.get("qualified_name"),
                                symbol_type=sym.get("symbol_type"),
                                metadata={
                                    "line_start": sym.get("line_start"),
                                    "line_end": sym.get("line_end"),
                                },
                            ))

            except Exception as e:
                logger.warning(f"Error searching symbols: {e}")

        return results[:limit]

    async def _search_vector(
        self,
        query: str,
        library_id: Optional[str],
        limit: int,
        include_content: bool,
        include_symbols: bool,
    ) -> list[SearchResult]:
        """Search vector storage (semantic similarity).

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.
            include_content: Include document embeddings.
            include_symbols: Include symbol embeddings.

        Returns:
            List of SearchResult from vector storage.
        """
        if self._embedding_service is None:
            return []

        results = []

        try:
            if include_content:
                doc_results = await self._embedding_service.search_similar_documents(
                    query=query,
                    library_id=library_id,
                    limit=limit,
                )

                for doc in doc_results:
                    results.append(SearchResult(
                        id=doc.get("id", ""),
                        source="vector",
                        score=doc.get("score", 0.0),
                        file_path=doc.get("file_path"),
                        library_id=doc.get("library_id"),
                        content_preview=doc.get("content_preview"),
                        metadata={"semantic_match": True},
                    ))

            if include_symbols:
                sym_results = await self._embedding_service.search_similar_symbols(
                    query=query,
                    library_id=library_id,
                    limit=limit,
                )

                for sym in sym_results:
                    results.append(SearchResult(
                        id=sym.get("id", ""),
                        source="vector",
                        score=sym.get("score", 0.0),
                        file_path=sym.get("file_path"),
                        library_id=sym.get("library_id"),
                        name=sym.get("name"),
                        qualified_name=sym.get("qualified_name"),
                        metadata={
                            "semantic_match": True,
                            "signature": sym.get("signature"),
                        },
                    ))

        except Exception as e:
            logger.warning(f"Error searching vector storage: {e}")

        return results[:limit]

    async def _search_graph(
        self,
        query: str,
        library_id: Optional[str],
        limit: int,
    ) -> list[SearchResult]:
        """Search graph storage for symbols.

        Args:
            query: Search query (symbol name pattern).
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            List of SearchResult from graph storage.
        """
        if self.graph_storage is None:
            return []

        results = []

        try:
            # Search by symbol name in properties
            properties = {"name": query}
            if library_id:
                properties["library_id"] = library_id

            # Try to find nodes with matching name
            nodes = await self.graph_storage.find_nodes_by_label(
                label="Symbol",
                properties=properties if library_id else None,
                limit=limit,
            )

            for node in nodes:
                name = node.properties.get("name", "")
                if query.lower() in name.lower():
                    results.append(SearchResult(
                        id=node.id,
                        source="graph",
                        score=0.9 if query.lower() == name.lower() else 0.7,
                        file_path=node.properties.get("file_path"),
                        library_id=node.properties.get("library_id"),
                        name=name,
                        qualified_name=node.properties.get("qualified_name"),
                        symbol_type=node.labels[1] if len(node.labels) > 1 else None,
                        metadata={
                            "labels": node.labels,
                            "graph_source": True,
                        },
                    ))

        except Exception as e:
            logger.warning(f"Error searching graph storage: {e}")

        return results[:limit]

    def _merge_results(self, results: list[SearchResult]) -> list[SearchResult]:
        """Merge and deduplicate results from multiple sources.

        For duplicate results (same ID), keep the highest score and
        combine metadata from all sources.

        Args:
            results: List of results from all sources.

        Returns:
            Merged and deduplicated results.
        """
        seen: dict[str, SearchResult] = {}

        for result in results:
            # Normalize ID for comparison
            key = result.id.lower()

            if key in seen:
                existing = seen[key]
                # Keep highest score
                if result.score > existing.score:
                    existing.score = result.score
                    existing.source = result.source
                # Merge metadata
                existing.metadata.update(result.metadata)
                existing.metadata["sources"] = existing.metadata.get("sources", [existing.source])
                if result.source not in existing.metadata["sources"]:
                    existing.metadata["sources"].append(result.source)
            else:
                result.metadata["sources"] = [result.source]
                seen[key] = result

        return list(seen.values())

    async def search_documents(
        self,
        query: str,
        library_id: Optional[str] = None,
        limit: int = 20,
    ) -> CombinedSearchResponse:
        """Search only documents (not symbols).

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            CombinedSearchResponse with document results.
        """
        return await self.search(
            query=query,
            library_id=library_id,
            limit=limit,
            include_content=True,
            include_symbols=False,
        )

    async def search_symbols(
        self,
        query: str,
        library_id: Optional[str] = None,
        limit: int = 20,
    ) -> CombinedSearchResponse:
        """Search only symbols (not documents).

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            CombinedSearchResponse with symbol results.
        """
        return await self.search(
            query=query,
            library_id=library_id,
            limit=limit,
            include_content=False,
            include_symbols=True,
        )
