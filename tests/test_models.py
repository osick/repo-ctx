"""Tests for data models."""
import pytest
from datetime import datetime
from repo_ctx.models import Library, Version, Document, SearchResult, FuzzySearchResult


class TestLibrary:
    """Test Library dataclass."""

    def test_library_creation_minimal(self):
        """Test creating a library with minimal required fields."""
        lib = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Test description",
            default_version="main"
        )
        assert lib.group_name == "testgroup"
        assert lib.project_name == "testproject"
        assert lib.description == "Test description"
        assert lib.default_version == "main"
        assert lib.id is None
        assert lib.last_indexed is None

    def test_library_creation_with_id(self):
        """Test creating a library with ID."""
        lib = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Test description",
            default_version="main",
            id=123
        )
        assert lib.id == 123

    def test_library_creation_with_timestamp(self):
        """Test creating a library with last_indexed timestamp."""
        now = datetime.now()
        lib = Library(
            group_name="testgroup",
            project_name="testproject",
            description="Test description",
            default_version="main",
            last_indexed=now
        )
        assert lib.last_indexed == now

    def test_library_equality(self):
        """Test library equality comparison."""
        lib1 = Library("group", "project", "desc", "main")
        lib2 = Library("group", "project", "desc", "main")
        assert lib1 == lib2

    def test_library_inequality_different_group(self):
        """Test library inequality when group differs."""
        lib1 = Library("group1", "project", "desc", "main")
        lib2 = Library("group2", "project", "desc", "main")
        assert lib1 != lib2


class TestVersion:
    """Test Version dataclass."""

    def test_version_creation_minimal(self):
        """Test creating a version with minimal required fields."""
        ver = Version(
            library_id=1,
            version_tag="v1.0.0",
            commit_sha="abc123def456"
        )
        assert ver.library_id == 1
        assert ver.version_tag == "v1.0.0"
        assert ver.commit_sha == "abc123def456"
        assert ver.id is None

    def test_version_creation_with_id(self):
        """Test creating a version with ID."""
        ver = Version(
            library_id=1,
            version_tag="v1.0.0",
            commit_sha="abc123",
            id=42
        )
        assert ver.id == 42

    def test_version_equality(self):
        """Test version equality comparison."""
        ver1 = Version(1, "v1.0.0", "abc123")
        ver2 = Version(1, "v1.0.0", "abc123")
        assert ver1 == ver2


class TestDocument:
    """Test Document dataclass."""

    def test_document_creation_minimal(self):
        """Test creating a document with minimal required fields."""
        doc = Document(
            version_id=1,
            file_path="docs/README.md",
            content="# Hello World"
        )
        assert doc.version_id == 1
        assert doc.file_path == "docs/README.md"
        assert doc.content == "# Hello World"
        assert doc.content_type == "markdown"  # Default value
        assert doc.tokens == 0  # Default value
        assert doc.id is None

    def test_document_creation_with_all_fields(self):
        """Test creating a document with all fields."""
        doc = Document(
            version_id=1,
            file_path="docs/README.md",
            content="# Hello World",
            content_type="rst",
            tokens=1500,
            id=99
        )
        assert doc.content_type == "rst"
        assert doc.tokens == 1500
        assert doc.id == 99

    def test_document_empty_content(self):
        """Test creating a document with empty content."""
        doc = Document(
            version_id=1,
            file_path="empty.md",
            content=""
        )
        assert doc.content == ""
        assert doc.tokens == 0


class TestSearchResult:
    """Test SearchResult dataclass."""

    def test_search_result_creation_minimal(self):
        """Test creating a search result with minimal fields."""
        result = SearchResult(
            library_id="/group/project",
            name="project",
            description="A test project",
            versions=["v1.0.0", "v2.0.0"]
        )
        assert result.library_id == "/group/project"
        assert result.name == "project"
        assert result.description == "A test project"
        assert result.versions == ["v1.0.0", "v2.0.0"]
        assert result.score == 0.0  # Default value

    def test_search_result_with_score(self):
        """Test creating a search result with custom score."""
        result = SearchResult(
            library_id="/group/project",
            name="project",
            description="Test",
            versions=["main"],
            score=0.95
        )
        assert result.score == 0.95

    def test_search_result_empty_versions(self):
        """Test search result with no versions."""
        result = SearchResult(
            library_id="/group/project",
            name="project",
            description="Test",
            versions=[]
        )
        assert result.versions == []


class TestFuzzySearchResult:
    """Test FuzzySearchResult dataclass."""

    def test_fuzzy_search_result_creation(self):
        """Test creating a fuzzy search result."""
        result = FuzzySearchResult(
            library_id="/group/project",
            name="my-project",
            group="mygroup",
            description="A test project",
            score=0.85,
            match_type="contains",
            matched_field="name"
        )
        assert result.library_id == "/group/project"
        assert result.name == "my-project"
        assert result.group == "mygroup"
        assert result.description == "A test project"
        assert result.score == 0.85
        assert result.match_type == "contains"
        assert result.matched_field == "name"

    def test_fuzzy_search_result_exact_match(self):
        """Test fuzzy search result with exact match."""
        result = FuzzySearchResult(
            library_id="/group/project",
            name="project",
            group="group",
            description="",
            score=1.0,
            match_type="exact",
            matched_field="name"
        )
        assert result.score == 1.0
        assert result.match_type == "exact"

    def test_fuzzy_search_result_fuzzy_match(self):
        """Test fuzzy search result with fuzzy match."""
        result = FuzzySearchResult(
            library_id="/group/projet",  # typo in library_id
            name="projet",
            group="group",
            description="",
            score=0.4,
            match_type="fuzzy",
            matched_field="name"
        )
        assert result.match_type == "fuzzy"
        assert result.score < 1.0
