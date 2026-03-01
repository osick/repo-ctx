"""Vector storage implementation using Qdrant.

This module implements VectorStorageProtocol for storing and searching
vector embeddings for semantic search capabilities.
"""

from typing import Any, Optional
import uuid
import hashlib

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    PayloadSchemaType,
)

from repo_ctx.storage.protocols import (
    VectorStorageProtocol,
    Embedding,
    SimilarityResult,
)
from repo_ctx.exceptions import StorageError, ValidationError


class VectorStorage:
    """Qdrant-based vector storage implementing VectorStorageProtocol.

    This storage provides semantic search capabilities through vector
    embeddings. It supports:
    - Multiple collections for different embedding types
    - Payload filtering for efficient queries
    - Multiple distance metrics (Cosine, Euclidean, Dot)
    """

    # Distance metric mapping
    DISTANCE_METRICS = {
        "Cosine": Distance.COSINE,
        "Euclid": Distance.EUCLID,
        "Euclidean": Distance.EUCLID,
        "Dot": Distance.DOT,
    }

    def __init__(
        self,
        url: str = ":memory:",
        api_key: Optional[str] = None,
        default_vector_size: int = 1536,
        timeout: int = 30,
    ):
        """Initialize vector storage.

        Args:
            url: Qdrant server URL or ":memory:" for in-memory storage.
            api_key: Optional API key for Qdrant Cloud.
            default_vector_size: Default vector dimension (1536 for OpenAI ada-002).
            timeout: Request timeout in seconds.
        """
        self.url = url
        self.api_key = api_key
        self.default_vector_size = default_vector_size
        self.timeout = timeout

        # Initialize client
        if url == ":memory:":
            self._client = QdrantClient(":memory:")
        else:
            self._client = QdrantClient(
                url=url,
                api_key=api_key,
                timeout=timeout,
            )

        # ID mapping for in-memory storage (string -> UUID)
        self._id_to_uuid: dict[str, str] = {}
        self._uuid_to_id: dict[str, str] = {}

    def _string_to_uuid(self, string_id: str) -> str:
        """Convert a string ID to a valid UUID.

        Uses UUID5 with a namespace to ensure deterministic conversion.
        """
        # Check if already a valid UUID
        try:
            uuid.UUID(string_id)
            return string_id
        except ValueError:
            pass

        # Check cache
        if string_id in self._id_to_uuid:
            return self._id_to_uuid[string_id]

        # Generate deterministic UUID from string
        namespace = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # URL namespace
        generated = str(uuid.uuid5(namespace, string_id))

        # Cache the mapping
        self._id_to_uuid[string_id] = generated
        self._uuid_to_id[generated] = string_id

        return generated

    def _uuid_to_string(self, uuid_str: str) -> str:
        """Convert a UUID back to original string ID."""
        return self._uuid_to_id.get(uuid_str, uuid_str)

    async def health_check(self) -> bool:
        """Check if the storage is healthy and connected.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            # For in-memory, just check if client exists
            if self.url == ":memory:":
                return True
            # For remote, try to list collections
            self._client.get_collections()
            return True
        except Exception:
            return False

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
        # Check if collection already exists
        if await self.collection_exists(collection_name):
            return

        distance_metric = self.DISTANCE_METRICS.get(distance, Distance.COSINE)

        self._client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance_metric,
            ),
        )

    async def collection_exists(self, collection_name: str) -> bool:
        """Check if a collection exists.

        Args:
            collection_name: Name of the collection.

        Returns:
            True if exists, False otherwise.
        """
        try:
            collections = self._client.get_collections()
            return any(c.name == collection_name for c in collections.collections)
        except Exception:
            return False

    async def delete_collection(self, collection_name: str) -> None:
        """Delete a collection.

        Args:
            collection_name: Name of the collection to delete.
        """
        try:
            self._client.delete_collection(collection_name)
        except Exception:
            pass  # Collection may not exist

    async def list_collections(self) -> list[str]:
        """List all collection names.

        Returns:
            List of collection names.
        """
        collections = self._client.get_collections()
        return [c.name for c in collections.collections]

    async def upsert_embeddings(
        self,
        collection_name: str,
        embeddings: list[Embedding],
    ) -> None:
        """Insert or update embeddings.

        Args:
            collection_name: Target collection.
            embeddings: List of embeddings to upsert.

        Raises:
            ValidationError: If vector dimensions don't match.
            StorageError: If upsert fails.
        """
        if not embeddings:
            return

        # Convert to Qdrant points
        points = []
        for emb in embeddings:
            # Convert string ID to UUID for Qdrant compatibility
            qdrant_id = self._string_to_uuid(emb.id)
            # Store original ID in payload for retrieval
            payload = dict(emb.payload) if emb.payload else {}
            payload["_original_id"] = emb.id

            point = PointStruct(
                id=qdrant_id,
                vector=emb.vector,
                payload=payload,
            )
            points.append(point)

        try:
            self._client.upsert(
                collection_name=collection_name,
                points=points,
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "dimension" in error_msg or "size" in error_msg:
                raise ValidationError(
                    f"Vector dimension mismatch: {e}",
                    field="vector",
                    expected="matching collection vector size",
                )
            raise StorageError(
                f"Failed to upsert embeddings: {e}",
                storage_type="qdrant",
            )

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
            List of similarity results, sorted by score descending.
        """
        # Check if collection exists
        if not await self.collection_exists(collection_name):
            return []

        # Build filter
        query_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value),
                    )
                )
            query_filter = Filter(must=conditions)

        try:
            response = self._client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=limit,
                query_filter=query_filter,
                with_payload=True,
            )

            similarity_results = []
            for r in response.points:
                payload = dict(r.payload) if r.payload else {}
                # Extract original ID from payload
                original_id = payload.pop("_original_id", str(r.id))
                similarity_results.append(
                    SimilarityResult(
                        id=original_id,
                        score=r.score if r.score is not None else 0.0,
                        payload=payload,
                    )
                )
            return similarity_results
        except Exception as e:
            raise StorageError(
                f"Search failed: {e}",
                storage_type="qdrant",
            )

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
        if not await self.collection_exists(collection_name):
            return 0

        try:
            # Count before deletion
            count_before = await self.count(collection_name, {"library_id": library_id})

            # Delete by filter
            self._client.delete(
                collection_name=collection_name,
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="library_id",
                            match=MatchValue(value=library_id),
                        )
                    ]
                ),
            )

            return count_before
        except Exception as e:
            raise StorageError(
                f"Delete failed: {e}",
                storage_type="qdrant",
            )

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
            Embedding if found, None otherwise.
        """
        if not await self.collection_exists(collection_name):
            return None

        try:
            # Convert to UUID for lookup
            qdrant_id = self._string_to_uuid(embedding_id)

            results = self._client.retrieve(
                collection_name=collection_name,
                ids=[qdrant_id],
                with_vectors=True,
            )

            if not results:
                return None

            point = results[0]
            payload = dict(point.payload) if point.payload else {}
            # Extract original ID
            original_id = payload.pop("_original_id", embedding_id)

            return Embedding(
                id=original_id,
                vector=list(point.vector) if point.vector else [],
                payload=payload,
            )
        except Exception:
            return None

    async def count(
        self,
        collection_name: str,
        filters: Optional[dict[str, Any]] = None,
    ) -> int:
        """Count embeddings in a collection.

        Args:
            collection_name: Collection to count.
            filters: Optional filters.

        Returns:
            Number of embeddings.
        """
        if not await self.collection_exists(collection_name):
            return 0

        try:
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        )
                    )
                query_filter = Filter(must=conditions)

                result = self._client.count(
                    collection_name=collection_name,
                    count_filter=query_filter,
                )
            else:
                result = self._client.count(collection_name=collection_name)

            return result.count
        except Exception:
            return 0

    async def create_payload_index(
        self,
        collection_name: str,
        field_name: str,
        field_type: str = "keyword",
    ) -> None:
        """Create an index on a payload field for efficient filtering.

        Args:
            collection_name: Collection to index.
            field_name: Field name to index.
            field_type: Type of index (keyword, integer, float, bool).
        """
        schema_type_map = {
            "keyword": PayloadSchemaType.KEYWORD,
            "integer": PayloadSchemaType.INTEGER,
            "float": PayloadSchemaType.FLOAT,
            "bool": PayloadSchemaType.BOOL,
            "text": PayloadSchemaType.TEXT,
        }

        schema_type = schema_type_map.get(field_type, PayloadSchemaType.KEYWORD)

        try:
            self._client.create_payload_index(
                collection_name=collection_name,
                field_name=field_name,
                field_schema=schema_type,
            )
        except Exception:
            pass  # Index may already exist
