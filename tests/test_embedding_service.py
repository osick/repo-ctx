"""Tests for the embedding service.

These tests verify:
- Embedding generation (with fallback)
- Document/symbol/chunk embedding storage
- Semantic search functionality
- Cache behavior
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from repo_ctx.services.embedding import EmbeddingService
from repo_ctx.services.base import ServiceContext
from repo_ctx.storage import ContentStorage, VectorStorage
from repo_ctx.storage.protocols import Embedding, SimilarityResult


class TestEmbeddingServiceInit:
    """Tests for embedding service initialization."""

    def test_init_default_model(self):
        """Test initialization with default model."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)

        service = EmbeddingService(context)

        assert service.model == "text-embedding-3-small"
        assert service.cache_enabled is True
        assert service._initialized is False

    def test_init_custom_model(self):
        """Test initialization with custom model."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)

        service = EmbeddingService(
            context,
            model="voyage-code-2",
            api_key="test-key",
            cache_enabled=False,
        )

        assert service.model == "voyage-code-2"
        assert service.api_key == "test-key"
        assert service.cache_enabled is False

    def test_get_vector_size_known_model(self):
        """Test vector size for known models."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)

        service = EmbeddingService(context, model="text-embedding-3-large")
        assert service._get_vector_size() == 3072

        service = EmbeddingService(context, model="text-embedding-3-small")
        assert service._get_vector_size() == 1536

    def test_get_vector_size_unknown_model(self):
        """Test vector size defaults for unknown models."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)

        service = EmbeddingService(context, model="custom-model")
        assert service._get_vector_size() == 1536  # Default


class TestFallbackEmbedding:
    """Tests for fallback embedding generation."""

    def test_fallback_embedding_generates_vector(self):
        """Test fallback generates correct size vector."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding = service._generate_fallback_embedding("Hello world")

        assert len(embedding) == 1536
        assert all(isinstance(x, float) for x in embedding)

    def test_fallback_embedding_normalized(self):
        """Test fallback embedding is normalized."""
        import math

        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding = service._generate_fallback_embedding("Test content")

        magnitude = math.sqrt(sum(x * x for x in embedding))
        assert abs(magnitude - 1.0) < 0.01  # Should be unit vector

    def test_fallback_embedding_empty_text(self):
        """Test fallback for empty text."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding = service._generate_fallback_embedding("")

        assert len(embedding) == 1536
        assert all(x == 0.0 for x in embedding)

    def test_fallback_embedding_deterministic(self):
        """Test fallback is deterministic for same input."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        text = "Same input text"
        embedding1 = service._generate_fallback_embedding(text)
        embedding2 = service._generate_fallback_embedding(text)

        assert embedding1 == embedding2

    def test_fallback_embedding_different_texts(self):
        """Test fallback produces different embeddings for different texts."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding1 = service._generate_fallback_embedding("First text")
        embedding2 = service._generate_fallback_embedding("Second text")

        assert embedding1 != embedding2


class TestEmbeddingCache:
    """Tests for embedding cache functionality."""

    def test_content_hash_deterministic(self):
        """Test content hash is deterministic."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        hash1 = service._content_hash("Test content")
        hash2 = service._content_hash("Test content")

        assert hash1 == hash2
        assert len(hash1) == 16

    def test_content_hash_different_content(self):
        """Test different content produces different hashes."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        hash1 = service._content_hash("Content A")
        hash2 = service._content_hash("Content B")

        assert hash1 != hash2

    def test_clear_cache(self):
        """Test cache clearing."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        # Add something to cache
        service._cache["test_key"] = [0.1] * 1536

        service.clear_cache()

        assert len(service._cache) == 0


class TestGenerateEmbedding:
    """Tests for embedding generation."""

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text(self):
        """Test embedding generation for empty text."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding = await service.generate_embedding("")

        assert len(embedding) == 1536
        assert all(x == 0.0 for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_text(self):
        """Test embedding generation for whitespace text."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embedding = await service.generate_embedding("   \n\t  ")

        assert len(embedding) == 1536
        assert all(x == 0.0 for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embedding_fallback(self):
        """Test fallback embedding when litellm not available."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        # Should use fallback since we're not mocking litellm
        embedding = await service.generate_embedding("Test content")

        assert len(embedding) == 1536
        assert any(x != 0.0 for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embedding_caching(self):
        """Test embedding caching behavior."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context, cache_enabled=True)

        text = "Cache test content"

        # First call
        embedding1 = await service.generate_embedding(text)
        assert len(service._cache) == 1

        # Second call should use cache
        embedding2 = await service.generate_embedding(text)
        assert embedding1 == embedding2

    @pytest.mark.asyncio
    async def test_generate_embedding_no_cache(self):
        """Test embedding without caching."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context, cache_enabled=False)

        await service.generate_embedding("Test content")

        assert len(service._cache) == 0


class TestGenerateEmbeddings:
    """Tests for batch embedding generation."""

    @pytest.mark.asyncio
    async def test_generate_embeddings_empty_list(self):
        """Test batch embedding for empty list."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        embeddings = await service.generate_embeddings([])

        assert embeddings == []

    @pytest.mark.asyncio
    async def test_generate_embeddings_multiple_texts(self):
        """Test batch embedding for multiple texts."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        texts = ["First text", "Second text", "Third text"]
        embeddings = await service.generate_embeddings(texts)

        assert len(embeddings) == 3
        for emb in embeddings:
            assert len(emb) == 1536

    @pytest.mark.asyncio
    async def test_generate_embeddings_with_empty_texts(self):
        """Test batch embedding with some empty texts."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        texts = ["Text", "", "Another"]
        embeddings = await service.generate_embeddings(texts)

        assert len(embeddings) == 3
        assert all(x == 0.0 for x in embeddings[1])  # Empty text


class TestEmbeddingServiceWithVectorStorage:
    """Tests for embedding service with vector storage."""

    @pytest.fixture
    def mock_vector_storage(self):
        """Create mock vector storage."""
        storage = MagicMock(spec=VectorStorage)
        storage.create_collection = AsyncMock()
        storage.create_payload_index = AsyncMock()
        storage.collection_exists = AsyncMock(return_value=False)
        storage.upsert_embeddings = AsyncMock()
        storage.search_similar = AsyncMock(return_value=[])
        storage.delete_by_library = AsyncMock(return_value=0)
        return storage

    @pytest.fixture
    def service_with_vector(self, mock_vector_storage):
        """Create embedding service with vector storage."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(
            content_storage=content_storage,
            vector_storage=mock_vector_storage,
        )
        return EmbeddingService(context)

    @pytest.mark.asyncio
    async def test_initialize_creates_collections(self, service_with_vector, mock_vector_storage):
        """Test initialization creates vector collections."""
        await service_with_vector.initialize()

        # Should create 3 collections
        assert mock_vector_storage.create_collection.call_count == 3
        assert service_with_vector._initialized is True

    @pytest.mark.asyncio
    async def test_initialize_idempotent(self, service_with_vector, mock_vector_storage):
        """Test initialization is idempotent."""
        await service_with_vector.initialize()
        await service_with_vector.initialize()

        # Should only create collections once
        assert mock_vector_storage.create_collection.call_count == 3

    @pytest.mark.asyncio
    async def test_embed_document(self, service_with_vector, mock_vector_storage):
        """Test document embedding storage."""
        await service_with_vector.embed_document(
            document_id="doc-1",
            content="Test document content",
            library_id="/test/repo",
            file_path="README.md",
            metadata={"type": "markdown"},
        )

        mock_vector_storage.upsert_embeddings.assert_called_once()
        call_args = mock_vector_storage.upsert_embeddings.call_args
        assert call_args.kwargs["collection_name"] == "repo_ctx_documents"

    @pytest.mark.asyncio
    async def test_embed_symbol(self, service_with_vector, mock_vector_storage):
        """Test symbol embedding storage."""
        await service_with_vector.embed_symbol(
            symbol_id="sym-1",
            name="my_function",
            qualified_name="module.my_function",
            library_id="/test/repo",
            file_path="module.py",
            signature="def my_function(x: int) -> str",
            documentation="A test function",
        )

        mock_vector_storage.upsert_embeddings.assert_called_once()
        call_args = mock_vector_storage.upsert_embeddings.call_args
        assert call_args.kwargs["collection_name"] == "repo_ctx_symbols"

    @pytest.mark.asyncio
    async def test_embed_chunk(self, service_with_vector, mock_vector_storage):
        """Test chunk embedding storage."""
        await service_with_vector.embed_chunk(
            chunk_id="chunk-1",
            content="Code chunk content",
            library_id="/test/repo",
            chunk_type="code",
            source_id="doc-1",
        )

        mock_vector_storage.upsert_embeddings.assert_called_once()
        call_args = mock_vector_storage.upsert_embeddings.call_args
        assert call_args.kwargs["collection_name"] == "repo_ctx_chunks"

    @pytest.mark.asyncio
    async def test_search_similar_documents(self, service_with_vector, mock_vector_storage):
        """Test document similarity search."""
        mock_vector_storage.search_similar = AsyncMock(
            return_value=[
                SimilarityResult(
                    id="doc-1",
                    score=0.95,
                    payload={"file_path": "README.md", "library_id": "/test/repo"},
                )
            ]
        )

        results = await service_with_vector.search_similar_documents(
            query="test query",
            library_id="/test/repo",
            limit=5,
        )

        assert len(results) == 1
        assert results[0]["id"] == "doc-1"
        assert results[0]["score"] == 0.95

    @pytest.mark.asyncio
    async def test_search_similar_symbols(self, service_with_vector, mock_vector_storage):
        """Test symbol similarity search."""
        mock_vector_storage.search_similar = AsyncMock(
            return_value=[
                SimilarityResult(
                    id="sym-1",
                    score=0.90,
                    payload={
                        "name": "my_function",
                        "qualified_name": "module.my_function",
                        "file_path": "module.py",
                    },
                )
            ]
        )

        results = await service_with_vector.search_similar_symbols(
            query="function that does something",
            limit=10,
        )

        assert len(results) == 1
        assert results[0]["name"] == "my_function"

    @pytest.mark.asyncio
    async def test_delete_library_embeddings(self, service_with_vector, mock_vector_storage):
        """Test deleting library embeddings."""
        mock_vector_storage.delete_by_library = AsyncMock(return_value=5)

        counts = await service_with_vector.delete_library_embeddings("/test/repo")

        assert len(counts) == 3
        assert mock_vector_storage.delete_by_library.call_count == 3


class TestEmbeddingServiceNoVectorStorage:
    """Tests for embedding service without vector storage."""

    @pytest.mark.asyncio
    async def test_embed_document_no_storage(self):
        """Test embed_document is no-op without vector storage."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        # Should not raise
        await service.embed_document(
            document_id="doc-1",
            content="Test",
            library_id="/test",
            file_path="test.md",
        )

    @pytest.mark.asyncio
    async def test_search_no_storage(self):
        """Test search returns empty without vector storage."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        results = await service.search_similar_documents("query")

        assert results == []

    @pytest.mark.asyncio
    async def test_delete_library_no_storage(self):
        """Test delete returns empty without vector storage."""
        content_storage = MagicMock(spec=ContentStorage)
        context = ServiceContext(content_storage=content_storage)
        service = EmbeddingService(context)

        counts = await service.delete_library_embeddings("/test")

        assert counts == {}
