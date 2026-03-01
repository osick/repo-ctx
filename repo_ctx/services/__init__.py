"""Service layer for repo-ctx API.

This package provides the business logic layer between API endpoints
and storage backends.

Services:
- RepositoryService: Manage indexed repositories
- IndexingService: Handle repository indexing operations
- SearchService: Handle search operations
- AnalysisService: Handle code analysis operations
- ChunkingService: Content chunking strategies
- EnrichmentService: LLM-enhanced metadata enrichment
- DumpService: Export repository analysis to filesystem

Factory functions:
- create_service_context: Create a ServiceContext from Config
- create_repository_service: Create a RepositoryService instance
- create_indexing_service: Create an IndexingService instance
- create_search_service: Create a SearchService instance
- create_analysis_service: Create an AnalysisService instance
- create_chunking_service: Create a ChunkingService instance
- create_enrichment_service: Create an EnrichmentService instance
- create_dump_service: Create a DumpService instance
"""

from typing import Optional

from repo_ctx.config import Config
from repo_ctx.storage import ContentStorage, VectorStorage, GraphStorage
from repo_ctx.services.base import BaseService, ServiceContext
from repo_ctx.services.repository import RepositoryService
from repo_ctx.services.indexing import IndexingService
from repo_ctx.services.search import SearchService
from repo_ctx.services.analysis import AnalysisService
from repo_ctx.services.embedding import EmbeddingService
from repo_ctx.services.combined_search import CombinedSearchService, CombinedSearchResponse, SearchResult
from repo_ctx.services.llm import (
    LLMService,
    LLMResponse,
    CodeSummary,
    CodeExplanation,
    CodeClassification,
    QualitySuggestion,
    GeneratedDocstring,
)
from repo_ctx.services.progress import (
    ProgressTracker,
    ProgressRegistry,
    get_progress_registry,
    reset_progress_registry,
)
from repo_ctx.services.chunking import (
    ChunkingService,
    Chunk,
    ChunkType,
    ChunkingStrategy,
    FixedSizeChunking,
    TokenBasedChunking,
    SemanticChunking,
    MarkdownChunking,
)
from repo_ctx.services.enrichment import (
    EnrichmentService,
    EnrichedMetadata,
    EnrichedDocument,
    EnrichedSymbol,
)
from repo_ctx.services.dump import (
    DumpService,
    DumpLevel,
    DumpResult,
    DumpMetadata,
    GitInfo,
    create_dump_service,
)


def create_service_context(
    config: Optional[Config] = None,
    content_storage: Optional[ContentStorage] = None,
    vector_storage: Optional[VectorStorage] = None,
    graph_storage: Optional[GraphStorage] = None,
) -> ServiceContext:
    """Create a ServiceContext from configuration.

    Args:
        config: Configuration object. If not provided, uses defaults.
        content_storage: Pre-initialized content storage (overrides config).
        vector_storage: Pre-initialized vector storage (overrides config).
        graph_storage: Pre-initialized graph storage (overrides config).

    Returns:
        ServiceContext with initialized storage backends.
    """
    if config is None:
        config = Config()

    # Use provided storage or create from config
    if content_storage is None:
        # Get storage path from config
        storage_path = config.storage_path
        if config.storage:
            storage_path = config.storage.content_db_path

        content_storage = ContentStorage(storage_path)

    # Vector storage (optional)
    if vector_storage is None and config.storage and config.storage.qdrant:
        qdrant_config = config.storage.qdrant
        if qdrant_config.url:
            vector_storage = VectorStorage(
                url=qdrant_config.url,
                api_key=qdrant_config.api_key,
            )

    # Graph storage (optional)
    if graph_storage is None and config.storage and config.storage.neo4j:
        neo4j_config = config.storage.neo4j
        graph_storage = GraphStorage(
            uri=neo4j_config.uri,
            username=neo4j_config.username,
            password=neo4j_config.password,
            database=neo4j_config.database,
            in_memory=neo4j_config.in_memory,
        )

    return ServiceContext(
        content_storage=content_storage,
        vector_storage=vector_storage,
        graph_storage=graph_storage,
    )


def create_repository_service(context: ServiceContext) -> RepositoryService:
    """Create a RepositoryService instance.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured RepositoryService.
    """
    return RepositoryService(context)


def create_indexing_service(context: ServiceContext) -> IndexingService:
    """Create an IndexingService instance.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured IndexingService.
    """
    return IndexingService(context)


def create_search_service(context: ServiceContext) -> SearchService:
    """Create a SearchService instance.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured SearchService.
    """
    return SearchService(context)


def create_analysis_service(context: ServiceContext) -> AnalysisService:
    """Create an AnalysisService instance.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured AnalysisService.
    """
    return AnalysisService(context)


def create_embedding_service(
    context: ServiceContext,
    model: str = "text-embedding-3-small",
    api_key: Optional[str] = None,
) -> EmbeddingService:
    """Create an EmbeddingService instance.

    Args:
        context: ServiceContext with storage backends.
        model: Embedding model name (litellm format).
        api_key: API key for the embedding provider.

    Returns:
        Configured EmbeddingService.
    """
    return EmbeddingService(context, model=model, api_key=api_key)


def create_combined_search_service(
    context: ServiceContext,
    embedding_service: Optional[EmbeddingService] = None,
) -> CombinedSearchService:
    """Create a CombinedSearchService instance.

    Args:
        context: ServiceContext with storage backends.
        embedding_service: Optional embedding service for semantic search.

    Returns:
        Configured CombinedSearchService.
    """
    return CombinedSearchService(context, embedding_service=embedding_service)


def create_llm_service(
    context: ServiceContext,
    model: str = "gpt-5-mini",
    api_key: Optional[str] = None,
    enabled: bool = True,
) -> LLMService:
    """Create an LLMService instance.

    Args:
        context: ServiceContext with storage backends.
        model: LLM model name (litellm format).
        api_key: API key for the LLM provider.
        enabled: Whether LLM features are enabled.

    Returns:
        Configured LLMService.
    """
    return LLMService(context, model=model, api_key=api_key, enabled=enabled)


def create_chunking_service(
    default_strategy: str = "semantic",
    **strategy_kwargs,
) -> ChunkingService:
    """Create a ChunkingService instance.

    Args:
        default_strategy: Default chunking strategy name.
        strategy_kwargs: Additional arguments for strategy.

    Returns:
        Configured ChunkingService.
    """
    return ChunkingService(default_strategy=default_strategy, **strategy_kwargs)


def create_enrichment_service(
    context: ServiceContext,
    llm_service: Optional[LLMService] = None,
    chunking_service: Optional[ChunkingService] = None,
    use_llm: bool = True,
) -> EnrichmentService:
    """Create an EnrichmentService instance.

    Args:
        context: ServiceContext with storage backends.
        llm_service: Optional LLM service for AI-powered enrichment.
        chunking_service: Optional chunking service.
        use_llm: Whether to use LLM for enrichment.

    Returns:
        Configured EnrichmentService.
    """
    return EnrichmentService(
        context,
        llm_service=llm_service,
        chunking_service=chunking_service,
        use_llm=use_llm,
    )


__all__ = [
    # Base Classes
    "BaseService",
    "ServiceContext",
    # Core Services
    "RepositoryService",
    "IndexingService",
    "SearchService",
    "AnalysisService",
    "EmbeddingService",
    "CombinedSearchService",
    "CombinedSearchResponse",
    "SearchResult",
    # LLM Service
    "LLMService",
    "LLMResponse",
    "CodeSummary",
    "CodeExplanation",
    "CodeClassification",
    "QualitySuggestion",
    "GeneratedDocstring",
    # Progress Tracking
    "ProgressTracker",
    "ProgressRegistry",
    "get_progress_registry",
    "reset_progress_registry",
    # Chunking Service
    "ChunkingService",
    "Chunk",
    "ChunkType",
    "ChunkingStrategy",
    "FixedSizeChunking",
    "TokenBasedChunking",
    "SemanticChunking",
    "MarkdownChunking",
    # Enrichment Service
    "EnrichmentService",
    "EnrichedMetadata",
    "EnrichedDocument",
    "EnrichedSymbol",
    # Dump Service
    "DumpService",
    "DumpLevel",
    "DumpResult",
    "DumpMetadata",
    "GitInfo",
    # Factory functions
    "create_service_context",
    "create_repository_service",
    "create_indexing_service",
    "create_search_service",
    "create_analysis_service",
    "create_embedding_service",
    "create_combined_search_service",
    "create_llm_service",
    "create_chunking_service",
    "create_enrichment_service",
    "create_dump_service",
]
