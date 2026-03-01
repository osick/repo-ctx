"""Storage protocol definitions for repo-ctx v2.

This module defines the abstract protocols (interfaces) for the three
storage backends:
- ContentStorageProtocol: SQLite for content and metadata
- VectorStorageProtocol: Qdrant for semantic embeddings
- GraphStorageProtocol: Neo4j for code relationships

All protocols use async methods for I/O operations.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Protocol, runtime_checkable

from repo_ctx.models import Library, Document


# =============================================================================
# Data Transfer Objects
# =============================================================================


@dataclass
class Embedding:
    """Data transfer object for vector embeddings.

    Attributes:
        id: Unique identifier for the embedding.
        vector: The embedding vector (list of floats).
        payload: Additional metadata stored with the embedding.
    """

    id: str
    vector: list[float]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class SimilarityResult:
    """Result from a similarity search.

    Attributes:
        id: Identifier of the matched embedding.
        score: Similarity score (0.0 to 1.0, higher is more similar).
        payload: Metadata associated with the embedding.
    """

    id: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphNode:
    """A node in the graph database.

    Attributes:
        id: Unique identifier for the node.
        labels: Node labels (e.g., ["Symbol", "Function"]).
        properties: Node properties as key-value pairs.
    """

    id: str
    labels: list[str]
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphRelationship:
    """A relationship between two nodes.

    Attributes:
        from_id: Source node ID.
        to_id: Target node ID.
        type: Relationship type (e.g., "CALLS", "IMPORTS").
        properties: Relationship properties.
    """

    from_id: str
    to_id: str
    type: str
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphResult:
    """Result from a graph query.

    Attributes:
        nodes: List of nodes in the result.
        relationships: List of relationships in the result.
    """

    nodes: list[GraphNode] = field(default_factory=list)
    relationships: list[GraphRelationship] = field(default_factory=list)


# =============================================================================
# Storage Protocols
# =============================================================================


@runtime_checkable
class ContentStorageProtocol(Protocol):
    """Protocol for content storage (SQLite).

    This protocol defines the interface for storing and retrieving
    content data including libraries, documents, symbols, and dependencies.
    """

    async def init_db(self) -> None:
        """Initialize the database schema.

        Creates all necessary tables, indexes, and migrations.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        ...

    # Library operations
    async def save_library(self, library: Library) -> int:
        """Save or update a library.

        Args:
            library: Library to save.

        Returns:
            The library ID.
        """
        ...

    async def get_library(self, library_id: str) -> Optional[Library]:
        """Get a library by its ID.

        Args:
            library_id: Library identifier (e.g., "/owner/repo").

        Returns:
            Library if found, None otherwise.
        """
        ...

    async def get_all_libraries(self) -> list[Library]:
        """Get all indexed libraries.

        Returns:
            List of all libraries.
        """
        ...

    async def delete_library(self, library_id: str) -> bool:
        """Delete a library and all its data.

        Args:
            library_id: Library identifier.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # Document operations
    async def save_documents(self, documents: list[Document]) -> None:
        """Save multiple documents.

        Args:
            documents: List of documents to save.
        """
        ...

    async def get_documents(
        self,
        version_id: int,
        topic: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[Document]:
        """Get documents for a version.

        Args:
            version_id: Version ID to get documents for.
            topic: Optional topic filter.
            page: Page number (1-indexed).
            page_size: Number of documents per page.

        Returns:
            List of documents.
        """
        ...

    # Symbol operations
    async def save_symbols(self, symbols: list[Any], repository_id: int) -> None:
        """Save multiple symbols.

        Args:
            symbols: List of Symbol objects.
            repository_id: Repository/library ID.
        """
        ...

    async def search_symbols(
        self,
        repository_id: int,
        query: str,
        symbol_type: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Search symbols by query.

        Args:
            repository_id: Repository/library ID.
            query: Search query.
            symbol_type: Optional filter by type.
            language: Optional filter by language.
            limit: Maximum results.

        Returns:
            List of matching symbols as dictionaries.
        """
        ...

    async def get_symbol_by_name(
        self, repository_id: int, qualified_name: str
    ) -> Optional[dict[str, Any]]:
        """Get a symbol by its qualified name.

        Args:
            repository_id: Repository/library ID.
            qualified_name: Full qualified name.

        Returns:
            Symbol as dictionary if found.
        """
        ...


@runtime_checkable
class VectorStorageProtocol(Protocol):
    """Protocol for vector storage (Qdrant).

    This protocol defines the interface for storing and searching
    vector embeddings for semantic search.
    """

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        ...

    async def create_collection(
        self,
        collection_name: str,
        vector_size: int,
        distance: str = "Cosine",
    ) -> None:
        """Create a new collection for embeddings.

        Args:
            collection_name: Name of the collection.
            vector_size: Dimension of the vectors.
            distance: Distance metric (Cosine, Euclidean, Dot).
        """
        ...

    async def upsert_embeddings(
        self,
        collection_name: str,
        embeddings: list[Embedding],
    ) -> None:
        """Insert or update embeddings.

        Args:
            collection_name: Target collection.
            embeddings: List of embeddings to upsert.
        """
        ...

    async def search_similar(
        self,
        collection_name: str,
        query_vector: list[float],
        limit: int = 10,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[SimilarityResult]:
        """Search for similar embeddings.

        Args:
            collection_name: Collection to search in.
            query_vector: Query embedding vector.
            limit: Maximum results to return.
            filters: Optional filters on payload fields.

        Returns:
            List of similarity results.
        """
        ...

    async def delete_by_library(
        self,
        collection_name: str,
        library_id: str,
    ) -> int:
        """Delete all embeddings for a library.

        Args:
            collection_name: Collection to delete from.
            library_id: Library identifier.

        Returns:
            Number of deleted embeddings.
        """
        ...

    async def get_embedding(
        self,
        collection_name: str,
        embedding_id: str,
    ) -> Optional[Embedding]:
        """Get a specific embedding by ID.

        Args:
            collection_name: Collection to search.
            embedding_id: Embedding identifier.

        Returns:
            Embedding if found.
        """
        ...


@runtime_checkable
class GraphStorageProtocol(Protocol):
    """Protocol for graph storage (Neo4j).

    This protocol defines the interface for storing and querying
    code relationships and semantic graphs.
    """

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        ...

    async def create_nodes(self, nodes: list[GraphNode]) -> None:
        """Create multiple nodes.

        Args:
            nodes: List of nodes to create.
        """
        ...

    async def create_relationships(
        self, relationships: list[GraphRelationship]
    ) -> None:
        """Create multiple relationships.

        Args:
            relationships: List of relationships to create.
        """
        ...

    async def query(
        self,
        cypher: str,
        params: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            cypher: Cypher query string.
            params: Query parameters.

        Returns:
            List of result records as dictionaries.
        """
        ...

    async def get_call_graph(
        self,
        symbol_name: str,
        depth: int = 2,
        direction: str = "both",
    ) -> GraphResult:
        """Get the call graph for a symbol.

        Args:
            symbol_name: Name or qualified name of the symbol.
            depth: Maximum traversal depth.
            direction: "incoming", "outgoing", or "both".

        Returns:
            Graph result with nodes and relationships.
        """
        ...

    async def delete_by_library(self, library_id: str) -> int:
        """Delete all nodes and relationships for a library.

        Args:
            library_id: Library identifier.

        Returns:
            Number of deleted nodes.
        """
        ...

    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a specific node by ID.

        Args:
            node_id: Node identifier.

        Returns:
            Node if found.
        """
        ...

    async def find_nodes_by_label(
        self,
        label: str,
        properties: Optional[dict[str, Any]] = None,
        limit: int = 100,
    ) -> list[GraphNode]:
        """Find nodes by label and optional properties.

        Args:
            label: Node label to search.
            properties: Optional property filters.
            limit: Maximum results.

        Returns:
            List of matching nodes.
        """
        ...
