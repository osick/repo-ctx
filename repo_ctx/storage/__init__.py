"""Storage layer for repo-ctx v2.

This package provides storage backends for the three database types:
- ContentStorage (SQLite): Content and metadata
- VectorStorage (Qdrant): Semantic embeddings
- GraphStorage (Neo4j): Code relationships

All storage classes implement their respective protocols defined in
repo_ctx.storage.protocols.

For backward compatibility, the legacy Storage class is also exported.
"""

from repo_ctx.storage.protocols import (
    # Protocols
    ContentStorageProtocol,
    VectorStorageProtocol,
    GraphStorageProtocol,
    # DTOs
    Embedding,
    SimilarityResult,
    GraphNode,
    GraphRelationship,
    GraphResult,
)

# Legacy Storage class and utilities for backward compatibility
from repo_ctx.storage.legacy import Storage, levenshtein_distance

# v2 Storage implementations
from repo_ctx.storage.content import ContentStorage
from repo_ctx.storage.vector import VectorStorage
from repo_ctx.storage.graph import GraphStorage

__all__ = [
    # Legacy (v1 compatibility)
    "Storage",
    "levenshtein_distance",
    # v2 Implementations
    "ContentStorage",
    "VectorStorage",
    "GraphStorage",
    # Protocols
    "ContentStorageProtocol",
    "VectorStorageProtocol",
    "GraphStorageProtocol",
    # DTOs
    "Embedding",
    "SimilarityResult",
    "GraphNode",
    "GraphRelationship",
    "GraphResult",
]
