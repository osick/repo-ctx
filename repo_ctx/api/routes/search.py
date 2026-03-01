"""Search endpoints for the repo-ctx API.

This module provides endpoints for search operations.
"""

from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.search import SearchService
from repo_ctx.services.embedding import EmbeddingService
from repo_ctx.services.combined_search import CombinedSearchService


class DocumentSearchResult(BaseModel):
    """Document search result."""
    id: Optional[int] = None
    file_path: str
    content_type: str
    content_preview: str
    quality_score: float


class SymbolSearchResult(BaseModel):
    """Symbol search result."""
    name: str
    qualified_name: str
    symbol_type: str
    file_path: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None


class SemanticSearchResult(BaseModel):
    """Semantic search result with similarity score."""
    id: str
    score: float
    file_path: Optional[str] = None
    library_id: Optional[str] = None
    content_preview: Optional[str] = None
    name: Optional[str] = None
    qualified_name: Optional[str] = None
    signature: Optional[str] = None


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    total: int
    results: list[dict[str, Any]]


class SemanticSearchResponse(BaseModel):
    """Semantic search response with results grouped by type."""
    query: str
    documents: list[dict[str, Any]] = Field(default_factory=list)
    symbols: list[dict[str, Any]] = Field(default_factory=list)
    chunks: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0


class SymbolDetailResponse(BaseModel):
    """Symbol detail response."""
    found: bool
    symbol: Optional[dict[str, Any]] = None


class CombinedSearchResult(BaseModel):
    """Result from combined search."""
    id: str
    source: str = Field(..., description="Source: content, vector, or graph")
    score: float = Field(..., description="Relevance score")
    file_path: Optional[str] = None
    library_id: Optional[str] = None
    content_preview: Optional[str] = None
    name: Optional[str] = None
    qualified_name: Optional[str] = None
    symbol_type: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class CombinedSearchResponse(BaseModel):
    """Response from combined search across all databases."""
    query: str
    total: int
    results: list[dict[str, Any]]
    sources_used: list[str] = Field(
        ..., description="List of sources that returned results"
    )
    content_count: int = Field(0, description="Results from content storage")
    vector_count: int = Field(0, description="Results from vector storage")
    graph_count: int = Field(0, description="Results from graph storage")


def create_search_router(context: ServiceContext) -> APIRouter:
    """Create a search router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["search"])

    # Create embedding service if vector storage is available
    embedding_service = None
    if context.vector_storage is not None:
        embedding_service = EmbeddingService(context)

    # Create search service with embedding service
    service = SearchService(context, embedding_service=embedding_service)

    # Create combined search service
    combined_service = CombinedSearchService(context, embedding_service=embedding_service)

    @router.get("/search", response_model=SearchResponse)
    async def search_documents(
        q: str = Query(..., description="Search query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        topic: Optional[str] = Query(None, description="Topic filter"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Results per page"),
    ) -> SearchResponse:
        """Search documents.

        Args:
            q: Search query string.
            repository: Optional repository ID to scope search.
            topic: Optional topic filter.
            page: Page number.
            page_size: Results per page.

        Returns:
            SearchResponse with matching documents.
        """
        results = await service.search_documents(
            query=q,
            repository_id=repository,
            topic=topic,
            page=page,
            page_size=page_size,
        )

        return SearchResponse(
            query=q,
            total=len(results),
            results=results,
        )

    @router.get("/search/symbols", response_model=SearchResponse)
    async def search_symbols(
        q: str = Query(..., description="Symbol name pattern"),
        repository_id: int = Query(..., description="Repository ID"),
        symbol_type: Optional[str] = Query(None, description="Symbol type filter"),
        language: Optional[str] = Query(None, description="Language filter"),
        limit: int = Query(50, ge=1, le=200, description="Max results"),
    ) -> SearchResponse:
        """Search symbols by name.

        Args:
            q: Symbol name pattern.
            repository_id: Repository ID to search in.
            symbol_type: Optional symbol type filter.
            language: Optional language filter.
            limit: Maximum results.

        Returns:
            SearchResponse with matching symbols.
        """
        results = await service.search_symbols(
            query=q,
            repository_id=repository_id,
            symbol_type=symbol_type,
            language=language,
            limit=limit,
        )

        return SearchResponse(
            query=q,
            total=len(results),
            results=results,
        )

    @router.get("/search/semantic", response_model=SemanticSearchResponse)
    async def semantic_search(
        q: str = Query(..., description="Natural language query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        search_type: str = Query("all", description="Type: all, documents, symbols, chunks"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
    ) -> SemanticSearchResponse:
        """Semantic search using vector embeddings.

        Searches for semantically similar content using embeddings.
        Requires vector storage to be configured.

        Args:
            q: Natural language query.
            repository: Optional repository ID to scope search.
            search_type: Type of search - "all", "documents", "symbols", or "chunks".
            limit: Maximum results per type.

        Returns:
            SemanticSearchResponse with results grouped by type.
        """
        if embedding_service is None:
            return SemanticSearchResponse(
                query=q,
                documents=[],
                symbols=[],
                chunks=[],
                total=0,
            )

        results = await service.semantic_search(
            query=q,
            repository_id=repository,
            search_type=search_type,
            limit=limit,
        )

        total = (
            len(results.get("documents", []))
            + len(results.get("symbols", []))
            + len(results.get("chunks", []))
        )

        return SemanticSearchResponse(
            query=q,
            documents=results.get("documents", []),
            symbols=results.get("symbols", []),
            chunks=results.get("chunks", []),
            total=total,
        )

    @router.get("/search/semantic/documents", response_model=SearchResponse)
    async def semantic_search_documents(
        q: str = Query(..., description="Natural language query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
    ) -> SearchResponse:
        """Semantic search for documents only.

        Args:
            q: Natural language query.
            repository: Optional repository ID.
            limit: Maximum results.

        Returns:
            SearchResponse with semantically similar documents.
        """
        results = await service.semantic_search_documents(
            query=q,
            repository_id=repository,
            limit=limit,
        )

        return SearchResponse(
            query=q,
            total=len(results),
            results=results,
        )

    @router.get("/search/semantic/symbols", response_model=SearchResponse)
    async def semantic_search_symbols(
        q: str = Query(..., description="Natural language query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
    ) -> SearchResponse:
        """Semantic search for code symbols.

        Args:
            q: Natural language query.
            repository: Optional repository ID.
            limit: Maximum results.

        Returns:
            SearchResponse with semantically similar symbols.
        """
        results = await service.semantic_search_symbols(
            query=q,
            repository_id=repository,
            limit=limit,
        )

        return SearchResponse(
            query=q,
            total=len(results),
            results=results,
        )

    @router.get("/symbols/{qualified_name:path}", response_model=SymbolDetailResponse)
    async def get_symbol_detail(
        qualified_name: str,
        repository_id: int = Query(..., description="Repository ID"),
    ) -> SymbolDetailResponse:
        """Get detailed information about a symbol.

        Args:
            qualified_name: Fully qualified symbol name.
            repository_id: Repository ID.

        Returns:
            SymbolDetailResponse with symbol details.
        """
        result = await service.get_symbol_detail(
            repository_id=repository_id,
            qualified_name=qualified_name,
        )

        return SymbolDetailResponse(
            found=result is not None,
            symbol=result,
        )

    @router.get("/search/combined", response_model=CombinedSearchResponse)
    async def combined_search(
        q: str = Query(..., description="Search query"),
        repository: Optional[str] = Query(None, description="Repository ID filter"),
        sources: Optional[str] = Query(None, description="Comma-separated: content,vector,graph"),
        include_content: bool = Query(True, description="Include documents"),
        include_symbols: bool = Query(True, description="Include symbols"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
    ) -> CombinedSearchResponse:
        """Combined search across all storage backends.

        Searches content storage (text), vector storage (semantic),
        and graph storage (relationships) and merges results.

        Args:
            q: Search query string.
            repository: Optional repository ID to scope search.
            sources: Comma-separated list of sources (default: all).
            include_content: Include document results.
            include_symbols: Include symbol results.
            limit: Maximum results.

        Returns:
            CombinedSearchResponse with merged results from all sources.
        """
        # Parse sources
        search_sources = None
        if sources:
            search_sources = [s.strip() for s in sources.split(",")]

        result = await combined_service.search(
            query=q,
            library_id=repository,
            search_sources=search_sources,
            limit=limit,
            include_content=include_content,
            include_symbols=include_symbols,
        )

        # Convert SearchResult objects to dicts
        results_dicts = []
        for r in result.results:
            results_dicts.append({
                "id": r.id,
                "source": r.source,
                "score": r.score,
                "file_path": r.file_path,
                "library_id": r.library_id,
                "content_preview": r.content_preview,
                "name": r.name,
                "qualified_name": r.qualified_name,
                "symbol_type": r.symbol_type,
                "metadata": r.metadata,
            })

        return CombinedSearchResponse(
            query=result.query,
            total=result.total,
            results=results_dicts,
            sources_used=result.sources_used,
            content_count=result.content_count,
            vector_count=result.vector_count,
            graph_count=result.graph_count,
        )

    @router.get("/search/combined/documents", response_model=CombinedSearchResponse)
    async def combined_search_documents(
        q: str = Query(..., description="Search query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
    ) -> CombinedSearchResponse:
        """Combined search for documents only.

        Args:
            q: Search query.
            repository: Optional repository filter.
            limit: Maximum results.

        Returns:
            CombinedSearchResponse with document results.
        """
        result = await combined_service.search_documents(
            query=q,
            library_id=repository,
            limit=limit,
        )

        results_dicts = [
            {
                "id": r.id,
                "source": r.source,
                "score": r.score,
                "file_path": r.file_path,
                "library_id": r.library_id,
                "content_preview": r.content_preview,
                "metadata": r.metadata,
            }
            for r in result.results
        ]

        return CombinedSearchResponse(
            query=result.query,
            total=result.total,
            results=results_dicts,
            sources_used=result.sources_used,
            content_count=result.content_count,
            vector_count=result.vector_count,
            graph_count=result.graph_count,
        )

    @router.get("/search/combined/symbols", response_model=CombinedSearchResponse)
    async def combined_search_symbols(
        q: str = Query(..., description="Search query"),
        repository: Optional[str] = Query(None, description="Repository ID"),
        limit: int = Query(20, ge=1, le=100, description="Max results"),
    ) -> CombinedSearchResponse:
        """Combined search for symbols only.

        Args:
            q: Search query.
            repository: Optional repository filter.
            limit: Maximum results.

        Returns:
            CombinedSearchResponse with symbol results.
        """
        result = await combined_service.search_symbols(
            query=q,
            library_id=repository,
            limit=limit,
        )

        results_dicts = [
            {
                "id": r.id,
                "source": r.source,
                "score": r.score,
                "file_path": r.file_path,
                "library_id": r.library_id,
                "name": r.name,
                "qualified_name": r.qualified_name,
                "symbol_type": r.symbol_type,
                "metadata": r.metadata,
            }
            for r in result.results
        ]

        return CombinedSearchResponse(
            query=result.query,
            total=result.total,
            results=results_dicts,
            sources_used=result.sources_used,
            content_count=result.content_count,
            vector_count=result.vector_count,
            graph_count=result.graph_count,
        )

    return router
