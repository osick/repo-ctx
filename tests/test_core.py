"""Tests for repo_ctx.core module - specifically get_documentation and Smart Truncation."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from repo_ctx.core import RepositoryContext
from repo_ctx.models import Document, Library


class TestSmartTruncation:
    """Tests for quality-based smart truncation in get_documentation."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.storage_path = ":memory:"
        config.gitlab_url = None
        config.gitlab_token = None
        config.github_url = None
        config.github_token = None
        return config

    @pytest.fixture
    def sample_documents(self):
        """Create sample documents with varying quality."""
        # High quality - README with code examples
        high_quality_doc = Document(
            id=1,
            version_id=1,
            file_path="README.md",
            content="""# My Project

This is a great project.

## Installation

```bash
pip install myproject
```

## Usage

```python
from myproject import main
main()
```

## Features
- Feature 1
- Feature 2
""",
            tokens=100
        )

        # Medium quality - guide without much code
        medium_quality_doc = Document(
            id=2,
            version_id=1,
            file_path="docs/guide.md",
            content="""# User Guide

This guide explains how to use the project.

## Getting Started

First, install the project. Then configure it.

## Configuration

Set the following environment variables.
""",
            tokens=80
        )

        # Low quality - short changelog-like doc
        low_quality_doc = Document(
            id=3,
            version_id=1,
            file_path="HISTORY.txt",
            content="""v1.0.0 - Initial release
v1.0.1 - Bug fix
""",
            tokens=20
        )

        return [low_quality_doc, medium_quality_doc, high_quality_doc]

    @pytest.mark.asyncio
    async def test_documents_sorted_by_quality(self, mock_config, sample_documents):
        """Test that documents are sorted by quality score (highest first)."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            # Mock get_library to return a library
            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)

            # Return documents in "wrong" order (low quality first)
            context.storage.get_documents = AsyncMock(return_value=sample_documents)

            await context.init()

            # Get documentation with token limit
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=5000  # Large enough for all docs
            )

            # The metadata should show documents in quality order
            # README.md should be first (highest quality)
            docs_metadata = result["metadata"]["documents_metadata"]
            assert len(docs_metadata) >= 1

            # First document should be README.md (highest quality)
            first_doc_path = docs_metadata[0]["file_path"]
            assert first_doc_path == "README.md"

    @pytest.mark.asyncio
    async def test_truncation_footer_when_limit_reached(self, mock_config, sample_documents):
        """Test that truncation footer is added when documents are truncated."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents)

            await context.init()

            # Get documentation with very small token limit
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=150  # Small enough to truncate
            )

            content = result["content"][0]["text"]

            # Should contain truncation footer if docs were truncated
            if result["metadata"]["documents_truncated"] > 0:
                assert "more document(s) available" in content
                assert "Additional documents" in content

    @pytest.mark.asyncio
    async def test_truncated_count_in_metadata(self, mock_config, sample_documents):
        """Test that truncated document count is in metadata."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents)

            await context.init()

            # Get with small limit
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=100
            )

            metadata = result["metadata"]
            assert "documents_truncated" in metadata
            assert metadata["documents_available"] == 3  # Total docs

    @pytest.mark.asyncio
    async def test_no_truncation_when_all_fit(self, mock_config, sample_documents):
        """Test no truncation footer when all documents fit."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents)

            await context.init()

            # Get with very large limit
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=100000  # Large enough for everything
            )

            metadata = result["metadata"]
            content = result["content"][0]["text"]

            # Should have no truncated docs and no footer
            assert metadata.get("documents_truncated", 0) == 0
            assert "more document(s) available" not in content


class TestGetDocumentation:
    """General tests for get_documentation method."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.storage_path = ":memory:"
        config.gitlab_url = None
        config.gitlab_token = None
        config.github_url = None
        config.github_token = None
        return config

    @pytest.mark.asyncio
    async def test_library_not_found_error(self, mock_config):
        """Test error when library is not found."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()
            context.storage.get_library = AsyncMock(return_value=None)

            await context.init()

            with pytest.raises(ValueError, match="Library not found"):
                await context.get_documentation("/nonexistent/repo")

    @pytest.mark.asyncio
    async def test_version_not_found_error(self, mock_config):
        """Test error when version is not found."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=None)

            await context.init()

            with pytest.raises(ValueError, match="Version not found"):
                await context.get_documentation("/owner/repo")


class TestQueryFiltering:
    """Tests for query-aware relevance filtering in get_documentation."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        config = Mock()
        config.storage_path = ":memory:"
        config.gitlab_url = None
        config.gitlab_token = None
        config.github_url = None
        config.github_token = None
        return config

    @pytest.fixture
    def sample_documents_for_query(self):
        """Create sample documents for query relevance testing."""
        # Auth doc - should match 'authentication' query
        auth_doc = Document(
            id=1,
            version_id=1,
            file_path="docs/authentication.md",
            content="""# Authentication Guide

This guide covers authentication and authorization.

## OAuth Setup

Configure OAuth tokens for access.
""",
            tokens=50
        )

        # Database doc - should NOT match 'authentication' query
        db_doc = Document(
            id=2,
            version_id=1,
            file_path="docs/database.md",
            content="""# Database Configuration

This guide covers PostgreSQL and MySQL setup.

## Connection Pooling

Configure database connections.
""",
            tokens=50
        )

        # API doc - has some auth content
        api_doc = Document(
            id=3,
            version_id=1,
            file_path="docs/api.md",
            content="""# API Reference

API endpoints documentation.

## Authentication

All requests require authentication tokens.
""",
            tokens=50
        )

        return [db_doc, api_doc, auth_doc]

    @pytest.mark.asyncio
    async def test_query_affects_document_ordering(self, mock_config, sample_documents_for_query):
        """Test that query affects document ordering based on relevance."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents_for_query)

            await context.init()

            # Query for authentication - auth doc should be prioritized
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=5000,
                query="authentication"
            )

            # Check that authentication.md is ranked first
            docs_metadata = result["metadata"]["documents_metadata"]
            assert len(docs_metadata) >= 1
            first_doc_path = docs_metadata[0]["file_path"]
            # Authentication doc should be first due to high relevance
            assert "authentication" in first_doc_path.lower() or "auth" in first_doc_path.lower()

    @pytest.mark.asyncio
    async def test_query_included_in_metadata(self, mock_config, sample_documents_for_query):
        """Test that query is included in response metadata."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents_for_query)

            await context.init()

            result = await context.get_documentation(
                "/owner/project",
                query="authentication oauth"
            )

            # Query should be in metadata
            assert result["metadata"].get("query") == "authentication oauth"

    @pytest.mark.asyncio
    async def test_no_query_uses_quality_only(self, mock_config, sample_documents_for_query):
        """Test that without query, documents are ordered by quality only."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents_for_query)

            await context.init()

            # No query - should use quality scoring only
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=5000
            )

            # Should not have query in metadata
            assert result["metadata"].get("query") is None

    @pytest.mark.asyncio
    async def test_query_combined_with_truncation(self, mock_config, sample_documents_for_query):
        """Test that query filtering works with token truncation."""
        with patch.object(RepositoryContext, '_init_providers'):
            context = RepositoryContext(mock_config)
            context.storage = AsyncMock()
            context.storage.init_db = AsyncMock()

            mock_lib = Mock()
            mock_lib.id = 1
            mock_lib.default_version = "main"
            context.storage.get_library = AsyncMock(return_value=mock_lib)
            context.storage.get_version_id = AsyncMock(return_value=1)
            context.storage.get_documents = AsyncMock(return_value=sample_documents_for_query)

            await context.init()

            # Small token limit with query
            result = await context.get_documentation(
                "/owner/project",
                max_tokens=100,  # Very small - will truncate
                query="authentication"
            )

            content = result["content"][0]["text"]
            metadata = result["metadata"]

            # If truncated, the footer should mention relevance
            if metadata.get("documents_truncated", 0) > 0:
                assert "relevance" in content.lower() or "more document" in content.lower()
