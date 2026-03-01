"""Documentation endpoints for the repo-ctx API.

This module provides endpoints for retrieving repository documentation.
"""

from typing import Any, Optional

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from repo_ctx.services.base import ServiceContext
from repo_ctx.services.search import SearchService


class DocumentInfo(BaseModel):
    """Document information."""
    id: int
    file_path: str
    content_type: str
    tokens: int
    preview: str = Field(default="", description="Content preview (first 200 chars)")


class DocsResponse(BaseModel):
    """Documentation response."""
    repository: str
    version: Optional[str] = None
    topic: Optional[str] = None
    total_documents: int
    total_tokens: int
    page: int
    page_size: int
    content: str = Field(..., description="Formatted documentation content")


class DocsListResponse(BaseModel):
    """List of documents response."""
    repository: str
    total: int
    documents: list[DocumentInfo]


def create_docs_router(context: ServiceContext) -> APIRouter:
    """Create a docs router with the given service context.

    Args:
        context: ServiceContext with storage backends.

    Returns:
        Configured APIRouter.
    """
    router = APIRouter(tags=["documentation"])
    _search_service = SearchService(context)

    @router.get("/docs/{group}/{project}")
    async def get_documentation(
        group: str,
        project: str,
        topic: Optional[str] = Query(None, description="Topic to filter (e.g., 'api', 'setup')"),
        query: Optional[str] = Query(None, description="Search query for relevance filtering"),
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Documents per page"),
        max_tokens: Optional[int] = Query(None, description="Maximum tokens to return"),
        output_mode: str = Query("standard", description="Output mode: summary, standard, full"),
        format: str = Query("markdown", description="Output format: markdown, json"),
    ) -> dict[str, Any]:
        """Get documentation for a repository.

        Args:
            group: Group/owner name.
            project: Project name.
            topic: Optional topic filter.
            query: Optional search query.
            page: Page number.
            page_size: Documents per page.
            max_tokens: Maximum tokens to return.
            output_mode: Output detail level.
            format: Output format.

        Returns:
            Documentation content in requested format.
        """
        try:
            repository_id = f"/{group}/{project}"

            # Get the library
            lib = await context.content_storage.get_library(repository_id)
            if not lib:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            # Get version
            version_id = await context.content_storage.get_version_id(
                lib.id, lib.default_version or "main"
            )
            if not version_id:
                raise HTTPException(status_code=404, detail=f"No version found for {repository_id}")

            # Get documents
            documents = await context.content_storage.get_documents(
                version_id=version_id,
                topic=topic,
                page=page,
                page_size=page_size,
            )

            # Filter by query if provided
            if query:
                query_lower = query.lower()
                documents = [
                    d for d in documents
                    if query_lower in d.content.lower() or query_lower in d.file_path.lower()
                ]

            # Calculate tokens
            total_tokens = sum(d.tokens or 0 for d in documents)

            # Format content
            if format == "json":
                return {
                    "repository": repository_id,
                    "version": lib.default_version,
                    "topic": topic,
                    "total_documents": len(documents),
                    "total_tokens": total_tokens,
                    "page": page,
                    "page_size": page_size,
                    "documents": [
                        {
                            "id": d.id,
                            "file_path": d.file_path,
                            "content_type": d.content_type,
                            "tokens": d.tokens or 0,
                            "content": d.content[:max_tokens] if max_tokens else d.content,
                        }
                        for d in documents
                    ],
                }

            # Markdown format
            content_parts = []
            current_tokens = 0

            for doc in documents:
                doc_tokens = doc.tokens or len(doc.content.split())

                if max_tokens and current_tokens + doc_tokens > max_tokens:
                    remaining = max_tokens - current_tokens
                    if remaining > 100:
                        content_parts.append(f"## {doc.file_path}\n\n{doc.content[:remaining*4]}...\n")
                    break

                content_parts.append(f"## {doc.file_path}\n\n{doc.content}\n")
                current_tokens += doc_tokens

            return {
                "repository": repository_id,
                "version": lib.default_version,
                "topic": topic,
                "total_documents": len(documents),
                "total_tokens": total_tokens,
                "page": page,
                "page_size": page_size,
                "content": "\n---\n\n".join(content_parts) if content_parts else "No documentation found.",
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/docs/{group}/{project}/list", response_model=DocsListResponse)
    async def list_documents(
        group: str,
        project: str,
        topic: Optional[str] = Query(None, description="Topic filter"),
        page: int = Query(1, ge=1),
        page_size: int = Query(50, ge=1, le=200),
    ) -> DocsListResponse:
        """List all documents in a repository.

        Args:
            group: Group/owner name.
            project: Project name.
            topic: Optional topic filter.
            page: Page number.
            page_size: Documents per page.

        Returns:
            DocsListResponse with list of documents.
        """
        try:
            repository_id = f"/{group}/{project}"

            lib = await context.content_storage.get_library(repository_id)
            if not lib:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            version_id = await context.content_storage.get_version_id(
                lib.id, lib.default_version or "main"
            )
            if not version_id:
                raise HTTPException(status_code=404, detail=f"No version found for {repository_id}")

            documents = await context.content_storage.get_documents(
                version_id=version_id,
                topic=topic,
                page=page,
                page_size=page_size,
            )

            return DocsListResponse(
                repository=repository_id,
                total=len(documents),
                documents=[
                    DocumentInfo(
                        id=d.id or 0,
                        file_path=d.file_path,
                        content_type=d.content_type,
                        tokens=d.tokens or 0,
                        preview=d.content[:200] if d.content else "",
                    )
                    for d in documents
                ],
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/llmstxt/{group}/{project}")
    async def get_llmstxt(
        group: str,
        project: str,
        include_api: bool = Query(True, description="Include API section"),
        include_quickstart: bool = Query(True, description="Include quickstart section"),
    ) -> PlainTextResponse:
        """Get llms.txt format documentation for a repository.

        Args:
            group: Group/owner name.
            project: Project name.
            include_api: Include API section.
            include_quickstart: Include quickstart section.

        Returns:
            Plain text llms.txt content.
        """
        try:
            from repo_ctx.llmstxt import LlmsTxtGenerator

            repository_id = f"/{group}/{project}"

            lib = await context.content_storage.get_library(repository_id)
            if not lib:
                raise HTTPException(status_code=404, detail=f"Repository not found: {repository_id}")

            version_id = await context.content_storage.get_version_id(
                lib.id, lib.default_version or "main"
            )
            if not version_id:
                raise HTTPException(status_code=404, detail=f"No version found for {repository_id}")

            documents = await context.content_storage.get_documents(version_id)

            generator = LlmsTxtGenerator()
            llmstxt = generator.generate(
                documents,
                repository_id,
                description=lib.description,
                include_api=include_api,
                include_quickstart=include_quickstart,
            )

            return PlainTextResponse(content=llmstxt, media_type="text/plain")

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router
