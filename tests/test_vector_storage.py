"""Tests for VectorStorage implementing VectorStorageProtocol.

Tests the Qdrant-based vector storage for semantic search including:
- Collection management
- Embedding upsert and retrieval
- Similarity search
- Filtering and deletion

Uses mocking for unit tests to avoid requiring a running Qdrant instance.
Following TDD Chicago School - write tests first, then implement.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestVectorStorageCreation:
    """Test VectorStorage instantiation."""

    def test_vector_storage_exists(self):
        """VectorStorage class should exist."""
        from repo_ctx.storage.vector import VectorStorage

        assert VectorStorage is not None

    def test_vector_storage_implements_protocol(self):
        """VectorStorage should implement VectorStorageProtocol."""
        from repo_ctx.storage.vector import VectorStorage
        from repo_ctx.storage.protocols import VectorStorageProtocol

        assert isinstance(VectorStorage, type)
        # Check it has all required methods
        assert hasattr(VectorStorage, "health_check")
        assert hasattr(VectorStorage, "create_collection")
        assert hasattr(VectorStorage, "upsert_embeddings")
        assert hasattr(VectorStorage, "search_similar")
        assert hasattr(VectorStorage, "delete_by_library")

    def test_vector_storage_accepts_url(self):
        """VectorStorage should accept a Qdrant URL."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url="http://localhost:6333")
        assert storage.url == "http://localhost:6333"

    def test_vector_storage_accepts_api_key(self):
        """VectorStorage should accept an optional API key."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url="http://localhost:6333", api_key="test-key")
        assert storage.api_key == "test-key"

    def test_vector_storage_default_vector_size(self):
        """VectorStorage should have a default vector size."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url="http://localhost:6333")
        assert storage.default_vector_size == 1536  # OpenAI ada-002 default

    def test_vector_storage_custom_vector_size(self):
        """VectorStorage should accept custom vector size."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url="http://localhost:6333", default_vector_size=768)
        assert storage.default_vector_size == 768


class TestVectorStorageInMemory:
    """Test VectorStorage with in-memory Qdrant for integration tests."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        # Use in-memory mode (no URL = in-memory)
        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_health_check_in_memory(self, storage):
        """health_check should return True for in-memory storage."""
        result = await storage.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_create_collection(self, storage):
        """create_collection should create a new collection."""
        await storage.create_collection(
            collection_name="test_collection",
            vector_size=1536,
            distance="Cosine",
        )

        # Verify collection exists
        exists = await storage.collection_exists("test_collection")
        assert exists is True

    @pytest.mark.asyncio
    async def test_create_collection_idempotent(self, storage):
        """create_collection should be idempotent."""
        await storage.create_collection("test_collection", 1536)
        # Should not raise
        await storage.create_collection("test_collection", 1536)

    @pytest.mark.asyncio
    async def test_upsert_embeddings(self, storage):
        """upsert_embeddings should store embeddings."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embeddings = [
            Embedding(
                id="emb_1",
                vector=[0.1, 0.2, 0.3, 0.4],
                payload={"library_id": "test/repo", "chunk_type": "code"},
            ),
            Embedding(
                id="emb_2",
                vector=[0.5, 0.6, 0.7, 0.8],
                payload={"library_id": "test/repo", "chunk_type": "documentation"},
            ),
        ]

        await storage.upsert_embeddings("test_collection", embeddings)

        # Verify by searching
        results = await storage.search_similar(
            "test_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=10,
        )
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_upsert_embeddings_update_existing(self, storage):
        """upsert_embeddings should update existing embeddings."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        # Insert first
        embedding = Embedding(
            id="emb_1",
            vector=[0.1, 0.2, 0.3, 0.4],
            payload={"version": "v1"},
        )
        await storage.upsert_embeddings("test_collection", [embedding])

        # Update
        embedding.payload = {"version": "v2"}
        embedding.vector = [0.9, 0.8, 0.7, 0.6]
        await storage.upsert_embeddings("test_collection", [embedding])

        # Verify update
        result = await storage.get_embedding("test_collection", "emb_1")
        assert result is not None
        assert result.payload["version"] == "v2"

    @pytest.mark.asyncio
    async def test_search_similar_returns_results(self, storage):
        """search_similar should return ranked results."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embeddings = [
            Embedding(id="close", vector=[0.1, 0.2, 0.3, 0.4], payload={"name": "close"}),
            Embedding(id="far", vector=[0.9, 0.8, 0.7, 0.6], payload={"name": "far"}),
        ]
        await storage.upsert_embeddings("test_collection", embeddings)

        results = await storage.search_similar(
            "test_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=2,
        )

        assert len(results) == 2
        # Closest should be first
        assert results[0].id == "close"
        assert results[0].score > results[1].score

    @pytest.mark.asyncio
    async def test_search_similar_with_limit(self, storage):
        """search_similar should respect limit."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embeddings = [
            Embedding(id=f"emb_{i}", vector=[0.1 * i, 0.2, 0.3, 0.4], payload={})
            for i in range(10)
        ]
        await storage.upsert_embeddings("test_collection", embeddings)

        results = await storage.search_similar(
            "test_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=3,
        )

        assert len(results) == 3

    @pytest.mark.asyncio
    async def test_search_similar_with_filter(self, storage):
        """search_similar should filter by payload."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embeddings = [
            Embedding(
                id="code_1",
                vector=[0.1, 0.2, 0.3, 0.4],
                payload={"chunk_type": "code", "library_id": "test/repo"},
            ),
            Embedding(
                id="doc_1",
                vector=[0.15, 0.25, 0.35, 0.45],
                payload={"chunk_type": "documentation", "library_id": "test/repo"},
            ),
            Embedding(
                id="code_2",
                vector=[0.2, 0.3, 0.4, 0.5],
                payload={"chunk_type": "code", "library_id": "other/repo"},
            ),
        ]
        await storage.upsert_embeddings("test_collection", embeddings)

        # Filter by chunk_type
        results = await storage.search_similar(
            "test_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=10,
            filters={"chunk_type": "code"},
        )

        assert len(results) == 2
        assert all(r.payload["chunk_type"] == "code" for r in results)

    @pytest.mark.asyncio
    async def test_delete_by_library(self, storage):
        """delete_by_library should remove all embeddings for a library."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embeddings = [
            Embedding(
                id="lib1_1",
                vector=[0.1, 0.2, 0.3, 0.4],
                payload={"library_id": "lib1"},
            ),
            Embedding(
                id="lib1_2",
                vector=[0.2, 0.3, 0.4, 0.5],
                payload={"library_id": "lib1"},
            ),
            Embedding(
                id="lib2_1",
                vector=[0.3, 0.4, 0.5, 0.6],
                payload={"library_id": "lib2"},
            ),
        ]
        await storage.upsert_embeddings("test_collection", embeddings)

        # Delete lib1
        deleted = await storage.delete_by_library("test_collection", "lib1")
        assert deleted >= 2

        # Verify lib1 is gone
        results = await storage.search_similar(
            "test_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=10,
        )
        assert len(results) == 1
        assert results[0].payload["library_id"] == "lib2"

    @pytest.mark.asyncio
    async def test_get_embedding(self, storage):
        """get_embedding should retrieve a specific embedding."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("test_collection", 4)

        embedding = Embedding(
            id="test_emb",
            vector=[0.1, 0.2, 0.3, 0.4],
            payload={"name": "test", "value": 42},
        )
        await storage.upsert_embeddings("test_collection", [embedding])

        result = await storage.get_embedding("test_collection", "test_emb")

        assert result is not None
        assert result.id == "test_emb"
        assert result.payload["name"] == "test"
        assert result.payload["value"] == 42

    @pytest.mark.asyncio
    async def test_get_embedding_not_found(self, storage):
        """get_embedding should return None for non-existent embedding."""
        await storage.create_collection("test_collection", 4)

        result = await storage.get_embedding("test_collection", "nonexistent")
        assert result is None


class TestVectorStorageCollectionManagement:
    """Test collection management operations."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_collection_exists_false(self, storage):
        """collection_exists should return False for non-existent collection."""
        exists = await storage.collection_exists("nonexistent")
        assert exists is False

    @pytest.mark.asyncio
    async def test_collection_exists_true(self, storage):
        """collection_exists should return True for existing collection."""
        await storage.create_collection("test_collection", 4)
        exists = await storage.collection_exists("test_collection")
        assert exists is True

    @pytest.mark.asyncio
    async def test_delete_collection(self, storage):
        """delete_collection should remove a collection."""
        await storage.create_collection("test_collection", 4)
        await storage.delete_collection("test_collection")

        exists = await storage.collection_exists("test_collection")
        assert exists is False

    @pytest.mark.asyncio
    async def test_list_collections(self, storage):
        """list_collections should return all collection names."""
        await storage.create_collection("collection_1", 4)
        await storage.create_collection("collection_2", 4)

        collections = await storage.list_collections()

        assert "collection_1" in collections
        assert "collection_2" in collections


class TestVectorStorageDistanceMetrics:
    """Test different distance metrics."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_cosine_distance(self, storage):
        """Cosine distance should work correctly."""
        await storage.create_collection("cosine_test", 4, distance="Cosine")

        from repo_ctx.storage.protocols import Embedding

        embeddings = [
            Embedding(id="a", vector=[1.0, 0.0, 0.0, 0.0], payload={}),
            Embedding(id="b", vector=[0.0, 1.0, 0.0, 0.0], payload={}),
        ]
        await storage.upsert_embeddings("cosine_test", embeddings)

        results = await storage.search_similar(
            "cosine_test",
            query_vector=[1.0, 0.0, 0.0, 0.0],
            limit=2,
        )

        # Vector "a" should be most similar to query
        assert results[0].id == "a"

    @pytest.mark.asyncio
    async def test_euclidean_distance(self, storage):
        """Euclidean distance should work correctly."""
        await storage.create_collection("euclidean_test", 4, distance="Euclid")

        from repo_ctx.storage.protocols import Embedding

        embeddings = [
            Embedding(id="close", vector=[0.1, 0.1, 0.1, 0.1], payload={}),
            Embedding(id="far", vector=[1.0, 1.0, 1.0, 1.0], payload={}),
        ]
        await storage.upsert_embeddings("euclidean_test", embeddings)

        results = await storage.search_similar(
            "euclidean_test",
            query_vector=[0.0, 0.0, 0.0, 0.0],
            limit=2,
        )

        # "close" should have higher score (smaller distance)
        assert results[0].id == "close"


class TestVectorStorageErrorHandling:
    """Test error handling."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_search_nonexistent_collection(self, storage):
        """search_similar on non-existent collection should raise or return empty."""
        from repo_ctx.exceptions import StorageError

        # Should either raise StorageError or return empty list
        try:
            results = await storage.search_similar(
                "nonexistent",
                query_vector=[0.1, 0.2, 0.3, 0.4],
                limit=10,
            )
            # If it doesn't raise, should return empty
            assert results == []
        except StorageError:
            pass  # Expected

    @pytest.mark.asyncio
    async def test_upsert_wrong_vector_size(self, storage):
        """upsert_embeddings with wrong vector size should raise."""
        from repo_ctx.storage.protocols import Embedding
        from repo_ctx.exceptions import ValidationError

        await storage.create_collection("test_collection", 4)

        # Try to insert vector with wrong size
        embedding = Embedding(
            id="wrong_size",
            vector=[0.1, 0.2],  # Only 2 dimensions instead of 4
            payload={},
        )

        with pytest.raises((ValidationError, Exception)):
            await storage.upsert_embeddings("test_collection", [embedding])


class TestVectorStoragePayloadIndexing:
    """Test payload indexing for filtering."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_create_payload_index(self, storage):
        """Should be able to create payload indexes."""
        await storage.create_collection("indexed_collection", 4)

        # Create index on library_id field
        await storage.create_payload_index(
            "indexed_collection",
            field_name="library_id",
            field_type="keyword",
        )

        # Should not raise - index should be usable
        from repo_ctx.storage.protocols import Embedding

        embedding = Embedding(
            id="test",
            vector=[0.1, 0.2, 0.3, 0.4],
            payload={"library_id": "test/repo"},
        )
        await storage.upsert_embeddings("indexed_collection", [embedding])

        results = await storage.search_similar(
            "indexed_collection",
            query_vector=[0.1, 0.2, 0.3, 0.4],
            limit=10,
            filters={"library_id": "test/repo"},
        )
        assert len(results) == 1


class TestVectorStorageBatchOperations:
    """Test batch operations."""

    @pytest_asyncio.fixture
    async def storage(self):
        """Create a VectorStorage instance with in-memory Qdrant."""
        from repo_ctx.storage.vector import VectorStorage

        storage = VectorStorage(url=":memory:")
        return storage

    @pytest.mark.asyncio
    async def test_upsert_large_batch(self, storage):
        """upsert_embeddings should handle large batches."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("large_batch", 4)

        # Create 100 embeddings
        embeddings = [
            Embedding(
                id=f"emb_{i}",
                vector=[0.1 * (i % 10), 0.2, 0.3, 0.4],
                payload={"index": i},
            )
            for i in range(100)
        ]

        await storage.upsert_embeddings("large_batch", embeddings)

        # Verify all were inserted
        results = await storage.search_similar(
            "large_batch",
            query_vector=[0.0, 0.2, 0.3, 0.4],
            limit=100,
        )
        assert len(results) == 100

    @pytest.mark.asyncio
    async def test_count_embeddings(self, storage):
        """count should return number of embeddings in collection."""
        from repo_ctx.storage.protocols import Embedding

        await storage.create_collection("count_test", 4)

        embeddings = [
            Embedding(id=f"emb_{i}", vector=[0.1, 0.2, 0.3, 0.4], payload={})
            for i in range(25)
        ]
        await storage.upsert_embeddings("count_test", embeddings)

        count = await storage.count("count_test")
        assert count == 25
