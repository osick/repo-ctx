"""Embedding service for generating vector embeddings.

This module provides embedding generation using litellm for multi-provider support.
Supports OpenAI, Anthropic, Cohere, and other embedding models.
"""

import hashlib
import logging
from typing import Any, Optional

from repo_ctx.services.base import BaseService, ServiceContext

logger = logging.getLogger("repo_ctx.services.embedding")


class EmbeddingService(BaseService):
    """Service for generating and managing embeddings.

    Uses litellm for multi-provider embedding support.
    Supports caching to avoid redundant API calls.
    """

    # Default embedding dimensions for common models
    EMBEDDING_DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
        "voyage-code-2": 1536,
        "voyage-2": 1024,
        "cohere-embed-english-v3.0": 1024,
        "cohere-embed-multilingual-v3.0": 1024,
    }

    # Collection names
    DOCUMENTS_COLLECTION = "repo_ctx_documents"
    SYMBOLS_COLLECTION = "repo_ctx_symbols"
    CHUNKS_COLLECTION = "repo_ctx_chunks"

    def __init__(
        self,
        context: ServiceContext,
        model: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        cache_enabled: bool = True,
    ) -> None:
        """Initialize the embedding service.

        Args:
            context: ServiceContext with storage backends.
            model: Embedding model name (litellm format).
            api_key: API key for the embedding provider.
            base_url: Optional base URL for the API.
            cache_enabled: Whether to cache embeddings.
        """
        super().__init__(context)
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.cache_enabled = cache_enabled
        self._cache: dict[str, list[float]] = {}
        self._initialized = False

    def _get_vector_size(self) -> int:
        """Get the vector dimension for the current model."""
        return self.EMBEDDING_DIMENSIONS.get(self.model, 1536)

    def _content_hash(self, content: str) -> str:
        """Generate a hash for content to use as cache key."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    async def initialize(self) -> None:
        """Initialize the embedding service and create collections."""
        if self._initialized:
            return

        if self.vector_storage is None:
            logger.warning("No vector storage configured - embeddings will not be persisted")
            return

        vector_size = self._get_vector_size()

        # Create collections for different content types
        await self.vector_storage.create_collection(
            collection_name=self.DOCUMENTS_COLLECTION,
            vector_size=vector_size,
            distance="Cosine",
        )

        await self.vector_storage.create_collection(
            collection_name=self.SYMBOLS_COLLECTION,
            vector_size=vector_size,
            distance="Cosine",
        )

        await self.vector_storage.create_collection(
            collection_name=self.CHUNKS_COLLECTION,
            vector_size=vector_size,
            distance="Cosine",
        )

        # Create payload indexes for efficient filtering
        for collection in [self.DOCUMENTS_COLLECTION, self.SYMBOLS_COLLECTION, self.CHUNKS_COLLECTION]:
            await self.vector_storage.create_payload_index(
                collection_name=collection,
                field_name="library_id",
                field_type="keyword",
            )

        self._initialized = True
        logger.info(f"Embedding service initialized with model {self.model} (dim={vector_size})")

    async def generate_embedding(
        self,
        text: str,
        use_cache: bool = True,
    ) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed.
            use_cache: Whether to use cached embeddings.

        Returns:
            Embedding vector as list of floats.
        """
        if not text.strip():
            return [0.0] * self._get_vector_size()

        # Check cache
        cache_key = self._content_hash(text)
        if use_cache and self.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]

        try:
            import litellm

            # Set API key if provided
            if self.api_key:
                if "openai" in self.model.lower() or "text-embedding" in self.model:
                    litellm.openai_key = self.api_key
                elif "voyage" in self.model.lower():
                    litellm.voyage_key = self.api_key
                elif "cohere" in self.model.lower():
                    litellm.cohere_key = self.api_key

            response = await litellm.aembedding(
                model=self.model,
                input=[text],
                api_key=self.api_key,
                api_base=self.base_url,
            )

            embedding = response.data[0]["embedding"]

            # Cache the result
            if self.cache_enabled:
                self._cache[cache_key] = embedding

            return embedding

        except ImportError:
            logger.warning("litellm not installed - using placeholder embeddings")
            return self._generate_fallback_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return self._generate_fallback_embedding(text)

    async def generate_embeddings(
        self,
        texts: list[str],
        use_cache: bool = True,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.
            use_cache: Whether to use cached embeddings.

        Returns:
            List of embedding vectors.
        """
        if not texts:
            return []

        # Check cache for each text
        embeddings = []
        texts_to_embed = []
        text_indices = []

        for i, text in enumerate(texts):
            if not text.strip():
                embeddings.append([0.0] * self._get_vector_size())
                continue

            cache_key = self._content_hash(text)
            if use_cache and self.cache_enabled and cache_key in self._cache:
                embeddings.append(self._cache[cache_key])
            else:
                embeddings.append(None)  # Placeholder
                texts_to_embed.append(text)
                text_indices.append(i)

        # If all cached, return early
        if not texts_to_embed:
            return embeddings

        try:
            import litellm

            if self.api_key:
                if "openai" in self.model.lower() or "text-embedding" in self.model:
                    litellm.openai_key = self.api_key

            response = await litellm.aembedding(
                model=self.model,
                input=texts_to_embed,
                api_key=self.api_key,
                api_base=self.base_url,
            )

            # Fill in the embeddings
            for j, item in enumerate(response.data):
                idx = text_indices[j]
                embedding = item["embedding"]
                embeddings[idx] = embedding

                # Cache
                if self.cache_enabled:
                    cache_key = self._content_hash(texts_to_embed[j])
                    self._cache[cache_key] = embedding

        except ImportError:
            logger.warning("litellm not installed - using placeholder embeddings")
            for j, text in enumerate(texts_to_embed):
                idx = text_indices[j]
                embeddings[idx] = self._generate_fallback_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            for j, text in enumerate(texts_to_embed):
                idx = text_indices[j]
                embeddings[idx] = self._generate_fallback_embedding(text)

        return embeddings

    def _generate_fallback_embedding(self, text: str) -> list[float]:
        """Generate a simple hash-based fallback embedding.

        This is NOT suitable for production - only for testing without API.
        Uses character frequency and text statistics as features.
        """
        import math

        vector_size = self._get_vector_size()
        embedding = [0.0] * vector_size

        if not text:
            return embedding

        # Normalize text
        text = text.lower()

        # Use hash-based feature extraction
        for i, char in enumerate(text):
            # Distribute character influence across vector
            idx = (ord(char) * (i + 1)) % vector_size
            embedding[idx] += 1.0

        # Add text statistics
        words = text.split()
        if words:
            embedding[0] = len(words) / 100.0  # Word count
            embedding[1] = len(text) / 1000.0  # Char count
            embedding[2] = len(words) / max(len(text), 1)  # Density

        # Normalize to unit vector
        magnitude = math.sqrt(sum(x * x for x in embedding))
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]

        return embedding

    async def embed_document(
        self,
        document_id: str,
        content: str,
        library_id: str,
        file_path: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Generate and store embedding for a document.

        Args:
            document_id: Unique document identifier.
            content: Document content to embed.
            library_id: Library identifier for filtering.
            file_path: Document file path.
            metadata: Additional metadata to store.
        """
        if self.vector_storage is None:
            return

        await self.initialize()

        # Truncate content if too long (most embedding models have limits)
        max_chars = 8000  # Conservative limit
        if len(content) > max_chars:
            content = content[:max_chars]

        embedding = await self.generate_embedding(content)

        from repo_ctx.storage.protocols import Embedding

        payload = {
            "library_id": library_id,
            "file_path": file_path,
            "content_preview": content[:500] if len(content) > 500 else content,
            **(metadata or {}),
        }

        await self.vector_storage.upsert_embeddings(
            collection_name=self.DOCUMENTS_COLLECTION,
            embeddings=[
                Embedding(
                    id=document_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

    async def embed_symbol(
        self,
        symbol_id: str,
        name: str,
        qualified_name: str,
        library_id: str,
        file_path: str,
        signature: Optional[str] = None,
        documentation: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Generate and store embedding for a code symbol.

        Args:
            symbol_id: Unique symbol identifier.
            name: Symbol name.
            qualified_name: Fully qualified name.
            library_id: Library identifier.
            file_path: File containing the symbol.
            signature: Function/method signature.
            documentation: Docstring or comments.
            metadata: Additional metadata.
        """
        if self.vector_storage is None:
            return

        await self.initialize()

        # Create rich text for embedding
        parts = [name, qualified_name]
        if signature:
            parts.append(signature)
        if documentation:
            parts.append(documentation)

        text = " ".join(parts)
        embedding = await self.generate_embedding(text)

        from repo_ctx.storage.protocols import Embedding

        payload = {
            "library_id": library_id,
            "file_path": file_path,
            "name": name,
            "qualified_name": qualified_name,
            "signature": signature,
            **(metadata or {}),
        }

        await self.vector_storage.upsert_embeddings(
            collection_name=self.SYMBOLS_COLLECTION,
            embeddings=[
                Embedding(
                    id=symbol_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

    async def embed_chunk(
        self,
        chunk_id: str,
        content: str,
        library_id: str,
        chunk_type: str,
        source_id: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Generate and store embedding for a content chunk.

        Args:
            chunk_id: Unique chunk identifier.
            content: Chunk content.
            library_id: Library identifier.
            chunk_type: Type of chunk (code, documentation, mixed).
            source_id: Source document or symbol ID.
            metadata: Additional metadata.
        """
        if self.vector_storage is None:
            return

        await self.initialize()

        embedding = await self.generate_embedding(content)

        from repo_ctx.storage.protocols import Embedding

        payload = {
            "library_id": library_id,
            "chunk_type": chunk_type,
            "source_id": source_id,
            "content_preview": content[:500] if len(content) > 500 else content,
            **(metadata or {}),
        }

        await self.vector_storage.upsert_embeddings(
            collection_name=self.CHUNKS_COLLECTION,
            embeddings=[
                Embedding(
                    id=chunk_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

    async def search_similar_documents(
        self,
        query: str,
        library_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for semantically similar documents.

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            List of similar documents with scores.
        """
        if self.vector_storage is None:
            return []

        await self.initialize()

        query_embedding = await self.generate_embedding(query)

        filters = {}
        if library_id:
            filters["library_id"] = library_id

        results = await self.vector_storage.search_similar(
            collection_name=self.DOCUMENTS_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            filters=filters if filters else None,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "file_path": r.payload.get("file_path"),
                "library_id": r.payload.get("library_id"),
                "content_preview": r.payload.get("content_preview"),
            }
            for r in results
        ]

    async def search_similar_symbols(
        self,
        query: str,
        library_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for semantically similar code symbols.

        Args:
            query: Search query.
            library_id: Optional library filter.
            limit: Maximum results.

        Returns:
            List of similar symbols with scores.
        """
        if self.vector_storage is None:
            return []

        await self.initialize()

        query_embedding = await self.generate_embedding(query)

        filters = {}
        if library_id:
            filters["library_id"] = library_id

        results = await self.vector_storage.search_similar(
            collection_name=self.SYMBOLS_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            filters=filters if filters else None,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "name": r.payload.get("name"),
                "qualified_name": r.payload.get("qualified_name"),
                "file_path": r.payload.get("file_path"),
                "signature": r.payload.get("signature"),
                "library_id": r.payload.get("library_id"),
            }
            for r in results
        ]

    async def search_similar_chunks(
        self,
        query: str,
        library_id: Optional[str] = None,
        chunk_type: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for semantically similar content chunks.

        Args:
            query: Search query.
            library_id: Optional library filter.
            chunk_type: Optional chunk type filter.
            limit: Maximum results.

        Returns:
            List of similar chunks with scores.
        """
        if self.vector_storage is None:
            return []

        await self.initialize()

        query_embedding = await self.generate_embedding(query)

        filters = {}
        if library_id:
            filters["library_id"] = library_id
        if chunk_type:
            filters["chunk_type"] = chunk_type

        results = await self.vector_storage.search_similar(
            collection_name=self.CHUNKS_COLLECTION,
            query_vector=query_embedding,
            limit=limit,
            filters=filters if filters else None,
        )

        return [
            {
                "id": r.id,
                "score": r.score,
                "chunk_type": r.payload.get("chunk_type"),
                "source_id": r.payload.get("source_id"),
                "content_preview": r.payload.get("content_preview"),
                "library_id": r.payload.get("library_id"),
            }
            for r in results
        ]

    async def delete_library_embeddings(self, library_id: str) -> dict[str, int]:
        """Delete all embeddings for a library.

        Args:
            library_id: Library identifier.

        Returns:
            Dictionary with deletion counts per collection.
        """
        if self.vector_storage is None:
            return {}

        counts = {}
        for collection in [self.DOCUMENTS_COLLECTION, self.SYMBOLS_COLLECTION, self.CHUNKS_COLLECTION]:
            count = await self.vector_storage.delete_by_library(
                collection_name=collection,
                library_id=library_id,
            )
            counts[collection] = count

        return counts

    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self._cache.clear()
