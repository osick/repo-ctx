"""Tests for storage layer."""
import pytest
import pytest_asyncio
import tempfile
from pathlib import Path
from repo_ctx.storage import Storage, levenshtein_distance
from repo_ctx.models import Library, Version, Document


class TestLevenshteinDistance:
    """Test Levenshtein distance calculation."""

    def test_identical_strings(self):
        """Test distance between identical strings is 0."""
        assert levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self):
        """Test distance with empty strings."""
        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "hello") == 5

    def test_single_character_difference(self):
        """Test distance with single character difference."""
        assert levenshtein_distance("cat", "bat") == 1  # Substitution
        assert levenshtein_distance("cat", "cats") == 1  # Insertion
        assert levenshtein_distance("cats", "cat") == 1  # Deletion

    def test_multiple_differences(self):
        """Test distance with multiple differences."""
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("saturday", "sunday") == 3

    def test_completely_different(self):
        """Test distance between completely different strings."""
        assert levenshtein_distance("abc", "xyz") == 3

    def test_case_sensitive(self):
        """Test that comparison is case-sensitive."""
        assert levenshtein_distance("Hello", "hello") == 1

    def test_order_independence(self):
        """Test that distance is symmetric."""
        assert levenshtein_distance("abc", "def") == levenshtein_distance("def", "abc")


class TestStorage:
    """Test Storage class with temporary file database."""

    @pytest_asyncio.fixture
    async def storage(self, tmp_path):
        """Create a storage instance with temporary file database."""
        db_path = str(tmp_path / "test.db")
        storage = Storage(db_path)
        await storage.init_db()
        return storage

    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self, storage):
        """Test that init_db creates all required tables."""
        # Query to check if tables exist
        import aiosqlite
        async with aiosqlite.connect(storage.db_path) as db:
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in await cursor.fetchall()]

        assert "libraries" in tables
        assert "versions" in tables
        assert "documents" in tables

    @pytest.mark.asyncio
    async def test_save_library_new(self, storage):
        """Test saving a new library."""
        library = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Test project",
            default_version="main"
        )

        library_id = await storage.save_library(library)
        assert library_id is not None
        assert library_id > 0

    @pytest.mark.asyncio
    async def test_save_library_update(self, storage):
        """Test updating an existing library."""
        library1 = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Original description",
            default_version="main"
        )
        await storage.save_library(library1)

        # Update with new description
        library2 = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Updated description",
            default_version="main"
        )
        library_id = await storage.save_library(library2)

        # Verify update
        retrieved = await storage.get_library("testgroup", "testproject")
        assert retrieved.description == "Updated description"

    @pytest.mark.asyncio
    async def test_get_library_exists(self, storage):
        """Test retrieving an existing library."""
        library = Library(
            group_name="mygroup",
            project_name="myproject",
            description="Test",
            default_version="v1.0"
        )
        await storage.save_library(library)

        retrieved = await storage.get_library("mygroup", "myproject")
        assert retrieved is not None
        assert retrieved.group_name == "mygroup"
        assert retrieved.project_name == "myproject"
        assert retrieved.description == "Test"
        assert retrieved.default_version == "v1.0"

    @pytest.mark.asyncio
    async def test_get_library_not_exists(self, storage):
        """Test retrieving a non-existent library returns None."""
        retrieved = await storage.get_library("nonexistent", "project")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_save_version(self, storage):
        """Test saving a version."""
        # First create a library
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)

        # Save version
        version = Version(
            library_id=library_id,
            version_tag="v1.0.0",
            commit_sha="abc123def456"
        )
        version_id = await storage.save_version(version)

        assert version_id is not None
        assert version_id > 0

    @pytest.mark.asyncio
    async def test_get_version_id_exists(self, storage):
        """Test retrieving version ID."""
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)

        version = Version(library_id, "v1.0.0", "abc123")
        await storage.save_version(version)

        version_id = await storage.get_version_id(library_id, "v1.0.0")
        assert version_id is not None
        assert version_id > 0

    @pytest.mark.asyncio
    async def test_get_version_id_not_exists(self, storage):
        """Test retrieving non-existent version returns None."""
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)

        version_id = await storage.get_version_id(library_id, "nonexistent")
        assert version_id is None

    @pytest.mark.asyncio
    async def test_save_document(self, storage):
        """Test saving a document."""
        # Setup library and version
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)
        version = Version(library_id, "v1.0", "abc123")
        version_id = await storage.save_version(version)

        # Save document
        doc = Document(
            version_id=version_id,
            file_path="docs/README.md",
            content="# Hello World",
            tokens=100
        )
        await storage.save_document(doc)

        # Verify by retrieving
        docs = await storage.get_documents(version_id)
        assert len(docs) == 1
        assert docs[0].file_path == "docs/README.md"
        assert docs[0].content == "# Hello World"
        assert docs[0].tokens == 100

    @pytest.mark.asyncio
    async def test_get_documents_pagination(self, storage):
        """Test document retrieval with pagination."""
        # Setup
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)
        version = Version(library_id, "v1.0", "abc123")
        version_id = await storage.save_version(version)

        # Save 15 documents
        for i in range(15):
            doc = Document(version_id, f"doc{i}.md", f"Content {i}")
            await storage.save_document(doc)

        # Get first page (default page_size=10)
        page1 = await storage.get_documents(version_id, page=1, page_size=10)
        assert len(page1) == 10

        # Get second page
        page2 = await storage.get_documents(version_id, page=2, page_size=10)
        assert len(page2) == 5

    @pytest.mark.asyncio
    async def test_get_documents_with_topic_filter(self, storage):
        """Test document retrieval with topic filtering."""
        # Setup
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)
        version = Version(library_id, "v1.0", "abc123")
        version_id = await storage.save_version(version)

        # Save documents with different topics
        await storage.save_document(Document(version_id, "api.md", "API documentation"))
        await storage.save_document(Document(version_id, "guide.md", "User guide"))
        await storage.save_document(Document(version_id, "api_reference.md", "API reference"))

        # Filter by topic
        api_docs = await storage.get_documents(version_id, topic="api")
        assert len(api_docs) == 2  # Should match api.md and api_reference.md

    @pytest.mark.asyncio
    async def test_search_by_project_name(self, storage):
        """Test searching libraries by project name."""
        await storage.save_library(Library("group1", "python-lib", "Python library", "main"))
        await storage.save_library(Library("group2", "java-lib", "Java library", "main"))
        await storage.save_library(Library("group3", "python-tools", "Python tools", "main"))

        results = await storage.search("python")
        assert len(results) == 2
        names = [r.name for r in results]
        assert "group1/python-lib" in names
        assert "group3/python-tools" in names

    @pytest.mark.asyncio
    async def test_search_by_description(self, storage):
        """Test searching libraries by description."""
        await storage.save_library(Library("group", "proj1", "REST API framework", "main"))
        await storage.save_library(Library("group", "proj2", "GraphQL server", "main"))

        results = await storage.search("API")
        assert len(results) >= 1
        assert any("proj1" in r.name for r in results)

    @pytest.mark.asyncio
    async def test_search_no_results(self, storage):
        """Test search with no matching results."""
        await storage.save_library(Library("group", "project", "description", "main"))

        results = await storage.search("nonexistent")
        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_fuzzy_search_exact_match(self, storage):
        """Test fuzzy search with exact match."""
        await storage.save_library(Library("group", "myproject", "Test project", "main"))

        results = await storage.fuzzy_search("myproject")
        assert len(results) == 1
        assert results[0].score == 1.0
        assert results[0].match_type == "exact"
        assert results[0].matched_field == "name"

    @pytest.mark.asyncio
    async def test_fuzzy_search_starts_with(self, storage):
        """Test fuzzy search with starts_with match."""
        await storage.save_library(Library("group", "myproject", "Test", "main"))

        results = await storage.fuzzy_search("mypro")
        assert len(results) == 1
        assert results[0].score == 0.9
        assert results[0].match_type == "starts_with"

    @pytest.mark.asyncio
    async def test_fuzzy_search_contains(self, storage):
        """Test fuzzy search with contains match."""
        await storage.save_library(Library("group", "my-awesome-project", "Test", "main"))

        results = await storage.fuzzy_search("awesome")
        assert len(results) == 1
        assert results[0].score == 0.8
        assert results[0].match_type == "contains"

    @pytest.mark.asyncio
    async def test_fuzzy_search_description_match(self, storage):
        """Test fuzzy search matching description."""
        await storage.save_library(Library("group", "project", "Python web framework", "main"))

        results = await storage.fuzzy_search("framework")
        assert len(results) == 1
        assert results[0].score == 0.6
        assert results[0].matched_field == "description"

    @pytest.mark.asyncio
    async def test_fuzzy_search_typo_tolerance(self, storage):
        """Test fuzzy search with typo (Levenshtein distance)."""
        await storage.save_library(Library("group", "project", "Test", "main"))

        # "projet" has 1 character difference from "project"
        results = await storage.fuzzy_search("projet")
        assert len(results) == 1
        assert results[0].match_type == "fuzzy"
        assert results[0].score > 0.4

    @pytest.mark.asyncio
    async def test_fuzzy_search_limit(self, storage):
        """Test fuzzy search result limiting."""
        # Create 20 projects
        for i in range(20):
            await storage.save_library(Library("group", f"project{i}", f"Test {i}", "main"))

        results = await storage.fuzzy_search("project", limit=5)
        assert len(results) == 5

    @pytest.mark.asyncio
    async def test_fuzzy_search_sorting_by_score(self, storage):
        """Test fuzzy search results are sorted by score descending."""
        await storage.save_library(Library("g1", "myproject", "Test", "main"))  # Exact: 1.0
        await storage.save_library(Library("g2", "myproject-tools", "Test", "main"))  # Starts: 0.9
        await storage.save_library(Library("g3", "awesome-myproject", "Test", "main"))  # Contains: 0.8

        results = await storage.fuzzy_search("myproject")
        assert len(results) == 3
        # Verify sorted by score descending
        assert results[0].score >= results[1].score
        assert results[1].score >= results[2].score
        # Verify expected match types
        assert results[0].match_type == "exact"
        assert results[1].match_type == "starts_with"
        assert results[2].match_type == "contains"

    @pytest.mark.asyncio
    async def test_fuzzy_search_case_insensitive(self, storage):
        """Test fuzzy search is case-insensitive."""
        await storage.save_library(Library("group", "MyProject", "Test", "main"))

        results = await storage.fuzzy_search("myproject")
        assert len(results) == 1
        assert results[0].score == 1.0

    @pytest.mark.asyncio
    async def test_storage_with_file_path(self, temp_db_path):
        """Test storage with actual file path."""
        storage = Storage(temp_db_path)
        await storage.init_db()

        # Verify database file was created
        assert Path(temp_db_path).exists()

        # Verify it works
        library = Library("group", "project", "desc", "main")
        library_id = await storage.save_library(library)
        assert library_id > 0

    @pytest.mark.asyncio
    async def test_storage_creates_parent_directories(self):
        """Test that Storage creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = f"{tmpdir}/subdir/nested/context.db"
            storage = Storage(db_path)

            # Parent directories should be created
            assert Path(db_path).parent.exists()
