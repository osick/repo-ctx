"""Analysis endpoints for the repo-ctx API.

This module provides endpoints for code analysis operations.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.analysis import AnalysisService
from repo_ctx.services.embedding import EmbeddingService
from repo_ctx.services.llm import LLMService


class AnalyzeRequest(BaseModel):
    """Request body for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    file_path: str = Field(..., description="File path (for language detection)")
    language: Optional[str] = Field(None, description="Language override")


class SymbolResponse(BaseModel):
    """Symbol in analysis response."""
    name: str
    qualified_name: str
    symbol_type: str
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    visibility: Optional[str] = None
    parent_name: Optional[str] = None


class DependencyResponse(BaseModel):
    """Dependency in analysis response."""
    source: Optional[str] = None
    target: Optional[str] = None
    dependency_type: Optional[str] = None
    file_path: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response from code analysis."""
    file_path: str
    language: Optional[str]
    symbols: list[dict[str, Any]]
    dependencies: list[dict[str, Any]]


class LanguagesResponse(BaseModel):
    """Response with supported languages."""
    languages: list[str]


class GraphRequest(BaseModel):
    """Request body for dependency graph generation."""
    symbols: list[dict[str, Any]] = Field(..., description="List of symbols")
    dependencies: list[dict[str, Any]] = Field(default=[], description="List of dependencies")
    graph_type: str = Field(default="class", description="Graph type (file, module, class, function, symbol)")
    output_format: str = Field(default="json", description="Output format (json, dot, graphml)")


class GraphResponse(BaseModel):
    """Response with dependency graph."""
    graph_type: str
    output_format: str
    nodes: list[dict[str, Any]]
    edges: list[dict[str, Any]]


class CallGraphResponse(BaseModel):
    """Response with call graph for a symbol."""
    symbol: str
    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]


class SymbolListResponse(BaseModel):
    """Response with list of symbols."""
    total: int
    symbols: list[dict[str, Any]]


class PersistAnalysisRequest(BaseModel):
    """Request to persist analysis to graph storage."""
    library_id: str = Field(..., description="Library identifier")
    symbols: list[dict[str, Any]] = Field(..., description="Symbols to persist")
    dependencies: list[dict[str, Any]] = Field(default=[], description="Dependencies to persist")


class PersistAnalysisResponse(BaseModel):
    """Response from persisting analysis."""
    library_id: str
    nodes_created: int
    relationships_created: int
    embeddings_generated: int


# LLM Analysis Models
class SummarizeRequest(BaseModel):
    """Request for code summarization."""
    code: str = Field(..., description="Source code to summarize")
    language: str = Field(..., description="Programming language")
    file_path: Optional[str] = Field(None, description="File path for context")
    context: Optional[str] = Field(None, description="Additional context")


class SummarizeResponse(BaseModel):
    """Response from code summarization."""
    summary: str
    language: str
    file_path: Optional[str] = None
    key_components: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)


class ExplainRequest(BaseModel):
    """Request for code explanation."""
    code: str = Field(..., description="Source code to explain")
    language: str = Field(..., description="Programming language")
    detail_level: str = Field(default="standard", description="Detail level: brief, standard, detailed")
    audience: str = Field(default="developer", description="Audience: beginner, developer, expert")


class ExplainResponse(BaseModel):
    """Response from code explanation."""
    explanation: str
    language: str
    detail_level: str
    audience: str
    concepts: list[str] = Field(default_factory=list)


class ClassifyRequest(BaseModel):
    """Request for code classification."""
    code: str = Field(..., description="Source code to classify")
    language: str = Field(..., description="Programming language")


class ClassifyResponse(BaseModel):
    """Response from code classification."""
    primary_category: str
    categories: list[str] = Field(default_factory=list)
    confidence: float
    tags: list[str] = Field(default_factory=list)


class ImproveRequest(BaseModel):
    """Request for code improvement suggestions."""
    code: str = Field(..., description="Source code to analyze")
    language: str = Field(..., description="Programming language")


class QualitySuggestionResponse(BaseModel):
    """Single code quality suggestion."""
    suggestion: str
    category: str
    severity: str
    original_code: Optional[str] = None
    suggested_code: Optional[str] = None


class ImproveResponse(BaseModel):
    """Response with code improvement suggestions."""
    suggestions: list[QualitySuggestionResponse]


class DocstringRequest(BaseModel):
    """Request for docstring generation."""
    code: str = Field(..., description="Source code (function or class)")
    language: str = Field(..., description="Programming language")
    style: str = Field(default="google", description="Docstring style: google, numpy, sphinx, jsdoc")


class DocstringResponse(BaseModel):
    """Response with generated docstring."""
    docstring: str
    style: str
    parameters: list[dict[str, str]] = Field(default_factory=list)
    returns: Optional[str] = None
    raises: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


def create_analysis_router(context: ServiceContext) -> APIRouter:
    """Create an analysis router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["analysis"])

    # Create embedding service if vector storage is available
    embedding_service = None
    if context.vector_storage is not None:
        embedding_service = EmbeddingService(context)

    # Create analysis service with embedding service
    service = AnalysisService(context, embedding_service=embedding_service)

    # Create LLM service
    llm_service = LLMService(context, enabled=True, use_fallback=True)

    @router.post("/analyze", response_model=AnalyzeResponse)
    async def analyze_code(request: AnalyzeRequest) -> AnalyzeResponse:
        """Analyze source code and extract symbols.

        Args:
            request: Analysis request with code and file path.

        Returns:
            AnalyzeResponse with extracted symbols and dependencies.
        """
        try:
            result = service.analyze_code(
                code=request.code,
                file_path=request.file_path,
                language=request.language,
            )
            return AnalyzeResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/analyze/languages", response_model=LanguagesResponse)
    async def get_supported_languages() -> LanguagesResponse:
        """Get list of supported programming languages.

        Returns:
            LanguagesResponse with list of languages.
        """
        languages = service.get_supported_languages()
        return LanguagesResponse(languages=languages)

    @router.post("/analyze/graph")
    async def generate_graph(request: GraphRequest):
        """Generate dependency graph from symbols.

        Args:
            request: Graph request with symbols and dependencies.

        Returns:
            Graph in requested format.
        """
        try:
            result = service.generate_dependency_graph(
                symbols=request.symbols,
                dependencies=request.dependencies,
                graph_type=request.graph_type,
                output_format=request.output_format,
            )

            # Return DOT/GraphML as plain text
            if request.output_format in ("dot", "graphml"):
                return PlainTextResponse(
                    content=result,
                    media_type="text/plain",
                )

            # JSON format - return the graph structure
            if isinstance(result, dict):
                return {
                    "graph_type": request.graph_type,
                    "output_format": request.output_format,
                    "nodes": result.get("graph", {}).get("nodes", []),
                    "edges": result.get("graph", {}).get("edges", []),
                }
            else:
                return {
                    "graph_type": request.graph_type,
                    "output_format": request.output_format,
                    "nodes": [],
                    "edges": [],
                }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/analyze/persist", response_model=PersistAnalysisResponse)
    async def persist_analysis(request: PersistAnalysisRequest) -> PersistAnalysisResponse:
        """Persist analysis results to graph storage.

        Creates nodes for symbols and relationships for dependencies
        in the graph database for later querying.

        Args:
            request: Analysis results to persist.

        Returns:
            PersistAnalysisResponse with counts of created items.
        """
        try:
            result = await service.persist_analysis_to_graph(
                library_id=request.library_id,
                symbols=request.symbols,
                dependencies=request.dependencies,
            )
            return PersistAnalysisResponse(
                library_id=request.library_id,
                nodes_created=result.get("nodes", 0),
                relationships_created=result.get("relationships", 0),
                embeddings_generated=result.get("embeddings", 0),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/graph/call-graph/{symbol_name:path}", response_model=CallGraphResponse)
    async def get_call_graph(
        symbol_name: str,
        library_id: Optional[str] = Query(None, description="Library filter"),
        depth: int = Query(2, ge=1, le=10, description="Traversal depth"),
        direction: str = Query("both", description="Direction: incoming, outgoing, both"),
    ) -> CallGraphResponse:
        """Get the call graph for a symbol.

        Traverses the graph to find all related symbols.

        Args:
            symbol_name: Symbol name to query.
            library_id: Optional library filter.
            depth: Maximum traversal depth.
            direction: Traversal direction.

        Returns:
            CallGraphResponse with nodes and relationships.
        """
        try:
            result = await service.query_call_graph(
                symbol_name=symbol_name,
                library_id=library_id,
                depth=depth,
                direction=direction,
            )
            return CallGraphResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/graph/symbols", response_model=SymbolListResponse)
    async def find_symbols_by_type(
        symbol_type: str = Query(..., description="Symbol type (class, function, method)"),
        library_id: Optional[str] = Query(None, description="Library filter"),
        limit: int = Query(100, ge=1, le=500, description="Max results"),
    ) -> SymbolListResponse:
        """Find symbols by type from graph storage.

        Args:
            symbol_type: Type of symbol to find.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            SymbolListResponse with matching symbols.
        """
        try:
            symbols = await service.find_symbols_by_type(
                symbol_type=symbol_type,
                library_id=library_id,
                limit=limit,
            )
            return SymbolListResponse(total=len(symbols), symbols=symbols)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/graph/public-api/{library_id:path}", response_model=SymbolListResponse)
    async def find_public_api(
        library_id: str,
        limit: int = Query(100, ge=1, le=500, description="Max results"),
    ) -> SymbolListResponse:
        """Find public API symbols in a library.

        Args:
            library_id: Library identifier.
            limit: Maximum results.

        Returns:
            SymbolListResponse with public API symbols.
        """
        try:
            symbols = await service.find_public_api(
                library_id=library_id,
                limit=limit,
            )
            return SymbolListResponse(total=len(symbols), symbols=symbols)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/graph/semantic-search", response_model=SymbolListResponse)
    async def semantic_symbol_search(
        q: str = Query(..., description="Natural language query"),
        library_id: Optional[str] = Query(None, description="Library filter"),
        limit: int = Query(10, ge=1, le=50, description="Max results"),
    ) -> SymbolListResponse:
        """Search symbols using semantic similarity.

        Uses vector embeddings for semantic search, then enriches
        results with graph data.

        Args:
            q: Natural language query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            SymbolListResponse with semantically similar symbols.
        """
        try:
            symbols = await service.semantic_symbol_search(
                query=q,
                library_id=library_id,
                limit=limit,
            )
            return SymbolListResponse(total=len(symbols), symbols=symbols)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/graph/{library_id:path}")
    async def delete_library_analysis(library_id: str) -> dict[str, Any]:
        """Delete all analysis data for a library.

        Removes nodes from graph storage and embeddings from vector storage.

        Args:
            library_id: Library identifier.

        Returns:
            Dictionary with deletion counts.
        """
        try:
            counts = await service.delete_library_analysis(library_id)
            return {
                "library_id": library_id,
                "deleted": counts,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # LLM-enhanced code analysis endpoints
    @router.post("/llm/summarize", response_model=SummarizeResponse)
    async def summarize_code(request: SummarizeRequest) -> SummarizeResponse:
        """Summarize source code using LLM.

        Generates a concise summary of code including key components
        and dependencies.

        Args:
            request: Summarization request with code and language.

        Returns:
            SummarizeResponse with code summary.
        """
        try:
            result = await llm_service.summarize_code(
                code=request.code,
                language=request.language,
                file_path=request.file_path,
                context=request.context,
            )
            return SummarizeResponse(
                summary=result.summary,
                language=result.language,
                file_path=result.file_path,
                key_components=result.key_components,
                dependencies=result.dependencies,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/llm/explain", response_model=ExplainResponse)
    async def explain_code(request: ExplainRequest) -> ExplainResponse:
        """Explain source code using LLM.

        Generates a detailed explanation of code, suitable for
        different audiences and detail levels.

        Args:
            request: Explanation request with code and preferences.

        Returns:
            ExplainResponse with code explanation.
        """
        try:
            result = await llm_service.explain_code(
                code=request.code,
                language=request.language,
                detail_level=request.detail_level,
                audience=request.audience,
            )
            return ExplainResponse(
                explanation=result.explanation,
                language=result.language,
                detail_level=result.detail_level,
                audience=result.audience,
                concepts=result.concepts,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/llm/classify", response_model=ClassifyResponse)
    async def classify_code(request: ClassifyRequest) -> ClassifyResponse:
        """Classify source code into categories using LLM.

        Categorizes code (e.g., controller, service, repository, etc.)
        with confidence scores.

        Args:
            request: Classification request with code.

        Returns:
            ClassifyResponse with categories and confidence.
        """
        try:
            result = await llm_service.classify_code(
                code=request.code,
                language=request.language,
            )
            return ClassifyResponse(
                primary_category=result.primary_category,
                categories=result.categories,
                confidence=result.confidence,
                tags=result.tags,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/llm/improve", response_model=ImproveResponse)
    async def suggest_improvements(request: ImproveRequest) -> ImproveResponse:
        """Suggest code improvements using LLM.

        Analyzes code for readability, performance, maintainability,
        and other quality aspects.

        Args:
            request: Improvement request with code.

        Returns:
            ImproveResponse with quality suggestions.
        """
        try:
            result = await llm_service.suggest_improvements(
                code=request.code,
                language=request.language,
            )
            return ImproveResponse(
                suggestions=[
                    QualitySuggestionResponse(
                        suggestion=s.suggestion,
                        category=s.category,
                        severity=s.severity,
                        original_code=s.original_code,
                        suggested_code=s.suggested_code,
                    )
                    for s in result
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/llm/docstring", response_model=DocstringResponse)
    async def generate_docstring(request: DocstringRequest) -> DocstringResponse:
        """Generate docstring for code using LLM.

        Creates properly formatted docstrings in various styles
        (Google, NumPy, Sphinx, JSDoc).

        Args:
            request: Docstring request with code and style.

        Returns:
            DocstringResponse with generated docstring.
        """
        try:
            result = await llm_service.generate_docstring(
                code=request.code,
                language=request.language,
                style=request.style,
            )
            return DocstringResponse(
                docstring=result.docstring,
                style=result.style,
                parameters=result.parameters,
                returns=result.returns,
                raises=result.raises,
                examples=result.examples,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
