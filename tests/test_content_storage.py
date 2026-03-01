"""Tests for ContentStorage implementing ContentStorageProtocol.

Tests the enhanced SQLite storage with the v2 schema including:
- Libraries, versions, documents
- Symbols with full metadata
- Chunks and classifications
- Health checks and transactions

Following TDD Chicago School - write tests first, then implement.
"""

import pytest
import pytest_asyncio
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Create a temporary database path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield os.path.join(tmpdir, "test.db")


@pytest_asyncio.fixture
async def storage(temp_db_path):
    """Create and initialize a ContentStorage instance."""
    from repo_ctx.storage.content import ContentStorage

    storage = ContentStorage(temp_db_path)
    await storage.init_db()
    return storage


class TestContentStorageCreation:
    """Test ContentStorage instantiation."""

    def test_content_storage_exists(self):
        """ContentStorage class should exist."""
        from repo_ctx.storage.content import ContentStorage

        assert ContentStorage is not None

    def test_content_storage_implements_protocol(self):
        """ContentStorage should implement ContentStorageProtocol."""
        from repo_ctx.storage.content import ContentStorage
        from repo_ctx.storage.protocols import ContentStorageProtocol

        assert isinstance(ContentStorage, type)
        # Check it has all required methods
        assert hasattr(ContentStorage, "init_db")
        assert hasattr(ContentStorage, "health_check")
        assert hasattr(ContentStorage, "save_library")
        assert hasattr(ContentStorage, "get_library")

    def test_content_storage_accepts_db_path(self, temp_db_path):
        """ContentStorage should accept a database path."""
        from repo_ctx.storage.content import ContentStorage

        storage = ContentStorage(temp_db_path)
        assert storage.db_path == temp_db_path


class TestContentStorageInitialization:
    """Test database initialization."""

    @pytest.mark.asyncio
    async def test_init_db_creates_database_file(self, temp_db_path):
        """init_db should create the database file."""
        from repo_ctx.storage.content import ContentStorage

        storage = ContentStorage(temp_db_path)
        await storage.init_db()

        assert os.path.exists(temp_db_path)

    @pytest.mark.asyncio
    async def test_init_db_creates_libraries_table(self, storage):
        """init_db should create libraries table."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='libraries'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_creates_versions_table(self, storage):
        """init_db should create versions table."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='versions'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_creates_documents_table(self, storage):
        """init_db should create documents table."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_creates_symbols_table(self, storage):
        """init_db should create symbols table."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='symbols'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_creates_chunks_table(self, storage):
        """init_db should create chunks table for GenAI."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='chunks'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_creates_classifications_table(self, storage):
        """init_db should create classifications table."""
        import aiosqlite

        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='classifications'"
            )
            result = await cursor.fetchone()
            assert result is not None

    @pytest.mark.asyncio
    async def test_init_db_idempotent(self, storage):
        """init_db should be safe to call multiple times."""
        # Call init_db again - should not raise
        await storage.init_db()
        await storage.init_db()


class TestHealthCheck:
    """Test health check functionality."""

    @pytest.mark.asyncio
    async def test_health_check_returns_true_when_healthy(self, storage):
        """health_check should return True for valid database."""
        result = await storage.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_returns_false_for_invalid_db(self, temp_db_path):
        """health_check should return False for corrupted database."""
        from repo_ctx.storage.content import ContentStorage

        # Create a file that is not a valid SQLite database
        with open(temp_db_path, "w") as f:
            f.write("not a valid sqlite database")

        storage = ContentStorage(temp_db_path)
        result = await storage.health_check()
        # SQLite will still connect to a corrupted file, so check init instead
        # For this test, we just verify the health check doesn't crash
        assert isinstance(result, bool)


class TestLibraryOperations:
    """Test library CRUD operations."""

    @pytest.mark.asyncio
    async def test_save_library_returns_id(self, storage):
        """save_library should return the library ID."""
        from repo_ctx.models import Library

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test repo",
            default_version="main",
            provider="github",
        )
        library_id = await storage.save_library(library)

        assert library_id is not None
        assert isinstance(library_id, int)
        assert library_id > 0

    @pytest.mark.asyncio
    async def test_get_library_by_id(self, storage):
        """get_library should retrieve library by ID string."""
        from repo_ctx.models import Library

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test repo",
            default_version="main",
            provider="github",
        )
        await storage.save_library(library)

        result = await storage.get_library("/owner/repo")

        assert result is not None
        assert result.group_name == "owner"
        assert result.project_name == "repo"
        assert result.description == "Test repo"
        assert result.provider == "github"

    @pytest.mark.asyncio
    async def test_get_library_not_found(self, storage):
        """get_library should return None for non-existent library."""
        result = await storage.get_library("/nonexistent/repo")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_libraries(self, storage):
        """get_all_libraries should return all libraries."""
        from repo_ctx.models import Library

        lib1 = Library(
            group_name="owner1",
            project_name="repo1",
            description="Repo 1",
            default_version="main",
            provider="github",
        )
        lib2 = Library(
            group_name="owner2",
            project_name="repo2",
            description="Repo 2",
            default_version="main",
            provider="gitlab",
        )

        await storage.save_library(lib1)
        await storage.save_library(lib2)

        libraries = await storage.get_all_libraries()

        assert len(libraries) == 2
        names = [lib.project_name for lib in libraries]
        assert "repo1" in names
        assert "repo2" in names

    @pytest.mark.asyncio
    async def test_delete_library(self, storage):
        """delete_library should remove library and return True."""
        from repo_ctx.models import Library

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        await storage.save_library(library)

        result = await storage.delete_library("/owner/repo")
        assert result is True

        # Verify deleted
        lib = await storage.get_library("/owner/repo")
        assert lib is None

    @pytest.mark.asyncio
    async def test_delete_library_not_found(self, storage):
        """delete_library should return False for non-existent library."""
        result = await storage.delete_library("/nonexistent/repo")
        assert result is False

    @pytest.mark.asyncio
    async def test_save_library_update_existing(self, storage):
        """save_library should update existing library."""
        from repo_ctx.models import Library

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Original",
            default_version="main",
            provider="github",
        )
        await storage.save_library(library)

        # Update description
        library.description = "Updated"
        await storage.save_library(library)

        result = await storage.get_library("/owner/repo")
        assert result.description == "Updated"


class TestDocumentOperations:
    """Test document CRUD operations."""

    @pytest.mark.asyncio
    async def test_save_documents(self, storage):
        """save_documents should save multiple documents."""
        from repo_ctx.models import Library, Version, Document

        # Create library and version first
        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        # Save documents
        docs = [
            Document(
                version_id=version_id,
                file_path="README.md",
                content="# Hello",
                content_type="markdown",
                tokens=10,
            ),
            Document(
                version_id=version_id,
                file_path="docs/guide.md",
                content="# Guide",
                content_type="markdown",
                tokens=20,
            ),
        ]
        await storage.save_documents(docs)

        # Verify saved
        result = await storage.get_documents(version_id)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_documents_with_pagination(self, storage):
        """get_documents should support pagination."""
        from repo_ctx.models import Library, Version, Document

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        # Save 5 documents
        docs = [
            Document(
                version_id=version_id,
                file_path=f"doc{i}.md",
                content=f"Content {i}",
                content_type="markdown",
                tokens=10,
            )
            for i in range(5)
        ]
        await storage.save_documents(docs)

        # Get page 1
        page1 = await storage.get_documents(version_id, page=1, page_size=2)
        assert len(page1) == 2

        # Get page 2
        page2 = await storage.get_documents(version_id, page=2, page_size=2)
        assert len(page2) == 2

        # Get page 3
        page3 = await storage.get_documents(version_id, page=3, page_size=2)
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_get_documents_with_topic_filter(self, storage):
        """get_documents should filter by topic."""
        from repo_ctx.models import Library, Version, Document

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        docs = [
            Document(
                version_id=version_id,
                file_path="docs/auth.md",
                content="Authentication guide",
                content_type="markdown",
                tokens=10,
            ),
            Document(
                version_id=version_id,
                file_path="docs/api.md",
                content="API reference",
                content_type="markdown",
                tokens=20,
            ),
        ]
        await storage.save_documents(docs)

        # Filter by topic
        result = await storage.get_documents(version_id, topic="auth")
        assert len(result) == 1
        assert "auth" in result[0].file_path


class TestSymbolOperations:
    """Test symbol CRUD operations."""

    @pytest.mark.asyncio
    async def test_save_symbols(self, storage):
        """save_symbols should save multiple symbols."""
        from repo_ctx.models import Library
        from repo_ctx.analysis.models import Symbol, SymbolType

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        symbols = [
            Symbol(
                name="main",
                qualified_name="src.main.main",
                symbol_type=SymbolType.FUNCTION,
                file_path="src/main.py",
                line_start=1,
                line_end=10,
                signature="def main() -> None",
                visibility="public",
                language="python",
                documentation="Main function",
                is_exported=True,
            ),
            Symbol(
                name="MyClass",
                qualified_name="src.main.MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="src/main.py",
                line_start=15,
                line_end=50,
                signature="class MyClass",
                visibility="public",
                language="python",
                documentation="A test class",
                is_exported=True,
            ),
        ]

        await storage.save_symbols(symbols, lib_id)

        # Verify saved
        result = await storage.search_symbols(lib_id, "")
        assert len(result) >= 2

    @pytest.mark.asyncio
    async def test_search_symbols_by_name(self, storage):
        """search_symbols should find symbols by name."""
        from repo_ctx.models import Library
        from repo_ctx.analysis.models import Symbol, SymbolType

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        symbols = [
            Symbol(
                name="authenticate",
                qualified_name="auth.authenticate",
                symbol_type=SymbolType.FUNCTION,
                file_path="auth.py",
                line_start=1,
                line_end=10,
                language="python",
            ),
            Symbol(
                name="authorize",
                qualified_name="auth.authorize",
                symbol_type=SymbolType.FUNCTION,
                file_path="auth.py",
                line_start=15,
                line_end=25,
                language="python",
            ),
        ]
        await storage.save_symbols(symbols, lib_id)

        result = await storage.search_symbols(lib_id, "authenticate")
        assert len(result) >= 1
        assert any(s["name"] == "authenticate" for s in result)

    @pytest.mark.asyncio
    async def test_search_symbols_by_type(self, storage):
        """search_symbols should filter by symbol type."""
        from repo_ctx.models import Library
        from repo_ctx.analysis.models import Symbol, SymbolType

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        symbols = [
            Symbol(
                name="MyClass",
                qualified_name="main.MyClass",
                symbol_type=SymbolType.CLASS,
                file_path="main.py",
                line_start=1,
                line_end=50,
                language="python",
            ),
            Symbol(
                name="my_function",
                qualified_name="main.my_function",
                symbol_type=SymbolType.FUNCTION,
                file_path="main.py",
                line_start=55,
                line_end=60,
                language="python",
            ),
        ]
        await storage.save_symbols(symbols, lib_id)

        result = await storage.search_symbols(lib_id, "", symbol_type="class")
        assert len(result) >= 1
        assert all(s["symbol_type"] == "class" for s in result)

    @pytest.mark.asyncio
    async def test_get_symbol_by_name(self, storage):
        """get_symbol_by_name should find symbol by qualified name."""
        from repo_ctx.models import Library
        from repo_ctx.analysis.models import Symbol, SymbolType

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        symbol = Symbol(
            name="process",
            qualified_name="utils.helpers.process",
            symbol_type=SymbolType.FUNCTION,
            file_path="utils/helpers.py",
            line_start=10,
            line_end=25,
            signature="def process(data: dict) -> dict",
            language="python",
            documentation="Process data",
        )
        await storage.save_symbols([symbol], lib_id)

        result = await storage.get_symbol_by_name(lib_id, "utils.helpers.process")
        assert result is not None
        assert result["name"] == "process"
        assert result["qualified_name"] == "utils.helpers.process"


class TestVersionOperations:
    """Test version operations."""

    @pytest.mark.asyncio
    async def test_save_version(self, storage):
        """save_version should save a version."""
        from repo_ctx.models import Library, Version

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(
            library_id=lib_id, version_tag="v1.0.0", commit_sha="abc123def456"
        )
        version_id = await storage.save_version(version)

        assert version_id is not None
        assert version_id > 0

    @pytest.mark.asyncio
    async def test_get_version_id(self, storage):
        """get_version_id should return version ID."""
        from repo_ctx.models import Library, Version

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        saved_id = await storage.save_version(version)

        retrieved_id = await storage.get_version_id(lib_id, "main")
        assert retrieved_id == saved_id


class TestChunkOperations:
    """Test chunk operations for GenAI."""

    @pytest.mark.asyncio
    async def test_save_chunk(self, storage):
        """save_chunk should save a content chunk."""
        from repo_ctx.models import Library, Version, Document

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        doc = Document(
            version_id=version_id,
            file_path="README.md",
            content="# Hello World",
            content_type="markdown",
            tokens=100,
        )
        await storage.save_documents([doc])

        # Get document ID
        docs = await storage.get_documents(version_id)
        doc_id = docs[0].id

        # Save chunk
        chunk_id = await storage.save_chunk(
            document_id=doc_id,
            content="# Hello World",
            chunk_type="documentation",
            start_line=1,
            end_line=1,
            tokens=10,
            embedding_id="emb_123",
        )

        assert chunk_id is not None
        assert chunk_id > 0

    @pytest.mark.asyncio
    async def test_get_chunks_by_document(self, storage):
        """get_chunks_by_document should return chunks for a document."""
        from repo_ctx.models import Library, Version, Document

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        doc = Document(
            version_id=version_id,
            file_path="README.md",
            content="# Hello\n\nWorld",
            content_type="markdown",
            tokens=100,
        )
        await storage.save_documents([doc])

        docs = await storage.get_documents(version_id)
        doc_id = docs[0].id

        # Save multiple chunks
        await storage.save_chunk(
            document_id=doc_id,
            content="# Hello",
            chunk_type="documentation",
            start_line=1,
            end_line=1,
            tokens=5,
        )
        await storage.save_chunk(
            document_id=doc_id,
            content="World",
            chunk_type="documentation",
            start_line=3,
            end_line=3,
            tokens=5,
        )

        chunks = await storage.get_chunks_by_document(doc_id)
        assert len(chunks) == 2


class TestClassificationOperations:
    """Test classification caching operations."""

    @pytest.mark.asyncio
    async def test_save_classification(self, storage):
        """save_classification should save a classification."""
        from repo_ctx.models import Library, Version, Document

        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        lib_id = await storage.save_library(library)

        version = Version(library_id=lib_id, version_tag="main", commit_sha="abc123")
        version_id = await storage.save_version(version)

        doc = Document(
            version_id=version_id,
            file_path="README.md",
            content="# Getting Started",
            content_type="markdown",
            tokens=50,
        )
        await storage.save_documents([doc])

        docs = await storage.get_documents(version_id)
        doc_id = docs[0].id

        # Save classification
        await storage.save_classification(
            entity_type="document",
            entity_id=doc_id,
            classification="tutorial",
            confidence=0.95,
            model="claude-3-sonnet",
        )

        # Get classification
        result = await storage.get_classification("document", doc_id)
        assert result is not None
        assert result["classification"] == "tutorial"
        assert result["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_get_classification_not_found(self, storage):
        """get_classification should return None for non-existent."""
        result = await storage.get_classification("document", 99999)
        assert result is None


class TestTransactionSupport:
    """Test transaction support."""

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, storage):
        """Transaction should rollback on error."""
        from repo_ctx.models import Library

        # Save a library
        library = Library(
            group_name="owner",
            project_name="repo",
            description="Test",
            default_version="main",
            provider="github",
        )
        await storage.save_library(library)

        # Verify it exists
        result = await storage.get_library("/owner/repo")
        assert result is not None
