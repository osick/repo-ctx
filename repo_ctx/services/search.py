"""Search service for repository search operations.

This module provides the SearchService which handles
searching documents, symbols, and semantic queries.
"""

from typing import Any, Optional, TYPE_CHECKING

from repo_ctx.services.base import BaseService, ServiceContext

if TYPE_CHECKING:
    from repo_ctx.services.embedding import EmbeddingService


class SearchService(BaseService):
    """Service for search operations.

    Handles document search, symbol search, and semantic search.
    """

    def __init__(
        self,
        context: ServiceContext,
        embedding_service: Optional["EmbeddingService"] = None,
    ) -> None:
        """Initialize the search service.

        Args:
            context: ServiceContext with storage backends.
            embedding_service: Optional embedding service for semantic search.
        """
        super().__init__(context)
        self._embedding_service = embedding_service

    @property
    def embedding_service(self) -> Optional["EmbeddingService"]:
        """Get the embedding service."""
        return self._embedding_service

    def set_embedding_service(self, service: "EmbeddingService") -> None:
        """Set the embedding service.

        Args:
            service: EmbeddingService instance.
        """
        self._embedding_service = service

    async def search_documents(
        self,
        query: str,
        repository_id: Optional[str] = None,
        topic: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> list[dict[str, Any]]:
        """Search documents by query.

        Args:
            query: Search query string.
            repository_id: Optional repository ID to scope search.
            topic: Optional topic filter.
            page: Page number (1-indexed).
            page_size: Number of results per page.

        Returns:
            List of matching documents.
        """
        # Get library if repository specified
        version_id = None
        if repository_id:
            library = await self.content_storage.get_library(repository_id)
            if library:
                version_id = library.id

        if version_id is None:
            # Search across all documents (get from first library)
            all_libs = await self.content_storage.get_all_libraries()
            if not all_libs:
                return []
            version_id = all_libs[0].id

        # Get documents
        documents = await self.content_storage.get_documents(
            version_id=version_id,
            topic=topic,
            page=page,
            page_size=page_size * 2,  # Get more to filter
        )

        # Filter by query (simple text match)
        query_lower = query.lower()
        matching_docs = []
        for doc in documents:
            if query_lower in doc.content.lower() or query_lower in doc.file_path.lower():
                matching_docs.append({
                    "id": doc.id,
                    "file_path": doc.file_path,
                    "content_type": doc.content_type,
                    "content_preview": doc.content[:200] + "..." if len(doc.content) > 200 else doc.content,
                    "quality_score": doc.quality_score,
                })
                if len(matching_docs) >= page_size:
                    break

        return matching_docs

    async def search_symbols(
        self,
        query: str,
        repository_id: int,
        symbol_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search symbols by query.

        Args:
            query: Search query (symbol name pattern).
            repository_id: Repository ID to search in.
            symbol_type: Optional filter by symbol type.
            language: Optional filter by language.
            limit: Maximum results to return.

        Returns:
            List of matching symbols.
        """
        return await self.content_storage.search_symbols(
            repository_id=repository_id,
            query=query,
            symbol_type=symbol_type,
            language=language,
            limit=limit,
        )

    async def semantic_search(
        self,
        query: str,
        repository_id: Optional[str] = None,
        limit: int = 10,
        search_type: str = "all",
    ) -> dict[str, Any]:
        """Semantic search using vector embeddings.

        Args:
            query: Natural language query.
            repository_id: Optional repository ID to scope search.
            limit: Maximum results to return.
            search_type: Type of search - "documents", "symbols", "chunks", or "all".

        Returns:
            Dictionary with search results grouped by type.
        """
        results: dict[str, Any] = {
            "query": query,
            "documents": [],
            "symbols": [],
            "chunks": [],
        }

        # Use embedding service if available
        if self._embedding_service is not None:
            if search_type in ("documents", "all"):
                results["documents"] = await self._embedding_service.search_similar_documents(
                    query=query,
                    library_id=repository_id,
                    limit=limit,
                )

            if search_type in ("symbols", "all"):
                results["symbols"] = await self._embedding_service.search_similar_symbols(
                    query=query,
                    library_id=repository_id,
                    limit=limit,
                )

            if search_type in ("chunks", "all"):
                results["chunks"] = await self._embedding_service.search_similar_chunks(
                    query=query,
                    library_id=repository_id,
                    limit=limit,
                )

        return results

    async def semantic_search_documents(
        self,
        query: str,
        repository_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Semantic search for documents only.

        Args:
            query: Natural language query.
            repository_id: Optional repository ID to scope search.
            limit: Maximum results to return.

        Returns:
            List of semantically similar documents.
        """
        if self._embedding_service is None:
            return []

        return await self._embedding_service.search_similar_documents(
            query=query,
            library_id=repository_id,
            limit=limit,
        )

    async def semantic_search_symbols(
        self,
        query: str,
        repository_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Semantic search for code symbols.

        Args:
            query: Natural language query.
            repository_id: Optional repository ID to scope search.
            limit: Maximum results to return.

        Returns:
            List of semantically similar symbols.
        """
        if self._embedding_service is None:
            return []

        return await self._embedding_service.search_similar_symbols(
            query=query,
            library_id=repository_id,
            limit=limit,
        )

    async def get_symbol_detail(
        self,
        repository_id: int,
        qualified_name: str,
    ) -> Optional[dict[str, Any]]:
        """Get detailed information about a symbol.

        Args:
            repository_id: Repository ID.
            qualified_name: Fully qualified symbol name.

        Returns:
            Symbol details if found, None otherwise.
        """
        return await self.content_storage.get_symbol_by_name(
            repository_id=repository_id,
            qualified_name=qualified_name,
        )

    async def get_call_graph(
        self,
        symbol_name: str,
        depth: int = 2,
        direction: str = "both",
    ) -> dict[str, Any]:
        """Get call graph for a symbol.

        Args:
            symbol_name: Symbol name to get graph for.
            depth: Maximum traversal depth.
            direction: "incoming", "outgoing", or "both".

        Returns:
            Graph data with nodes and relationships.
        """
        if self.graph_storage is None:
            return {"nodes": [], "relationships": []}

        result = await self.graph_storage.get_call_graph(
            symbol_name=symbol_name,
            depth=depth,
            direction=direction,
        )

        return {
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
