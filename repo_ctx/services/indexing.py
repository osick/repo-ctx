"""Indexing service for repository indexing operations.

This module provides the IndexingService which handles
indexing repositories from various providers.
"""

import logging
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from repo_ctx.models import Library, Document
from repo_ctx.services.base import BaseService, ServiceContext

if TYPE_CHECKING:
    from repo_ctx.services.embedding import EmbeddingService

logger = logging.getLogger("repo_ctx.services.indexing")


class IndexingService(BaseService):
    """Service for repository indexing operations.

    Handles indexing repositories from GitHub, GitLab, and local providers.
    Optionally generates embeddings for semantic search.
    """

    def __init__(
        self,
        context: ServiceContext,
        embedding_service: Optional["EmbeddingService"] = None,
    ) -> None:
        """Initialize the indexing service.

        Args:
            context: ServiceContext with storage backends.
            embedding_service: Optional embedding service for vector indexing.
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

    def _create_provider(
        self,
        provider_type: str,
        repository: str,
    ) -> Any:
        """Create a git provider for the given repository.

        Args:
            provider_type: Type of provider (github, gitlab, local).
            repository: Repository identifier.

        Returns:
            Git provider instance.
        """
        from repo_ctx.providers import create_provider

        return create_provider(provider_type, repository)

    async def index_repository(
        self,
        repository: str,
        provider_type: str = "auto",
        version: Optional[str] = None,
        refresh: bool = False,
    ) -> dict[str, Any]:
        """Index a repository.

        Args:
            repository: Repository identifier (e.g., "owner/repo" or "/path/to/repo").
            provider_type: Provider type (github, gitlab, local, auto).
            version: Optional version/branch/tag to index.
            refresh: Whether to re-index if already indexed.

        Returns:
            Dictionary with indexing result.
        """
        # Parse repository path
        parts = repository.strip("/").split("/")
        if len(parts) >= 2:
            group_name = "/".join(parts[:-1])
            project_name = parts[-1]
        else:
            group_name = ""
            project_name = repository

        library_id = f"/{group_name}/{project_name}" if group_name else f"/{project_name}"

        # Check if already indexed
        existing = await self.content_storage.get_library(library_id)
        updated = existing is not None

        # Create provider
        provider = self._create_provider(provider_type, repository)

        # Get repository info
        repo_info = provider.get_repository_info()
        default_branch = repo_info.get("default_branch", "main")
        description = repo_info.get("description", "")

        # Determine version to index
        index_version = version or default_branch

        # Get documentation files
        doc_files = provider.get_documentation_files()

        # Create library entry
        library = Library(
            id=existing.id if existing else None,
            group_name=group_name,
            project_name=project_name,
            description=description or f"Repository: {repository}",
            default_version=index_version,
            provider=provider_type if provider_type != "auto" else "github",
            last_indexed=datetime.now(),
        )

        # Save library
        library_db_id = await self.content_storage.save_library(library)

        # Create documents
        documents = []
        for doc_file in doc_files:
            doc = Document(
                version_id=library_db_id,
                file_path=doc_file["path"],
                content=doc_file["content"],
                content_type=self._detect_content_type(doc_file["path"]),
            )
            documents.append(doc)

        # Save documents
        if documents:
            await self.content_storage.save_documents(documents)

        # Generate embeddings if embedding service is available
        embeddings_generated = 0
        if self._embedding_service is not None and documents:
            logger.info(f"Generating embeddings for {len(documents)} documents")
            embeddings_generated = await self._generate_document_embeddings(
                documents=documents,
                library_id=library_id,
            )

        return {
            "status": "success",
            "repository": library_id,
            "version": index_version,
            "document_count": len(documents),
            "embeddings_generated": embeddings_generated,
            "updated": updated,
        }

    async def _generate_document_embeddings(
        self,
        documents: list[Document],
        library_id: str,
    ) -> int:
        """Generate embeddings for documents.

        Args:
            documents: List of documents to embed.
            library_id: Library identifier.

        Returns:
            Number of embeddings generated.
        """
        if self._embedding_service is None:
            return 0

        count = 0
        for doc in documents:
            try:
                await self._embedding_service.embed_document(
                    document_id=f"{library_id}:{doc.file_path}",
                    content=doc.content,
                    library_id=library_id,
                    file_path=doc.file_path,
                    metadata={
                        "content_type": doc.content_type,
                        "tokens": doc.tokens,
                    },
                )
                count += 1
            except Exception as e:
                logger.warning(f"Failed to embed document {doc.file_path}: {e}")

        return count

    def _detect_content_type(self, file_path: str) -> str:
        """Detect content type from file extension.

        Args:
            file_path: Path to the file.

        Returns:
            Content type string.
        """
        path_lower = file_path.lower()
        if path_lower.endswith(".md"):
            return "markdown"
        elif path_lower.endswith(".rst"):
            return "restructuredtext"
        elif path_lower.endswith(".txt"):
            return "text"
        elif path_lower.endswith(".html") or path_lower.endswith(".htm"):
            return "html"
        else:
            return "text"

    async def get_indexing_status(
        self, repository_id: str
    ) -> dict[str, Any]:
        """Get indexing status for a repository.

        Args:
            repository_id: Repository identifier.

        Returns:
            Dictionary with indexing status.
        """
        library = await self.content_storage.get_library(repository_id)

        if library is None:
            return {
                "indexed": False,
                "repository": repository_id,
            }

        return {
            "indexed": True,
            "repository": repository_id,
            "group_name": library.group_name,
            "project_name": library.project_name,
            "default_version": library.default_version,
            "last_indexed": library.last_indexed.isoformat() if library.last_indexed else None,
        }

    async def reindex_repository(
        self, repository_id: str, provider_type: str = "auto"
    ) -> dict[str, Any]:
        """Re-index an existing repository.

        Args:
            repository_id: Repository identifier.
            provider_type: Provider type.

        Returns:
            Dictionary with re-indexing result.
        """
        # Parse repository ID to get the repository path
        parts = repository_id.strip("/").split("/")
        repository = "/".join(parts)

        return await self.index_repository(
            repository=repository,
            provider_type=provider_type,
            refresh=True,
        )
