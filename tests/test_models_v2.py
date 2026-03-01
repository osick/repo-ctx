"""Tests for v2 model enhancements.

These tests verify the new fields and models added for the v2 architecture.
"""

import pytest
from datetime import datetime


class TestProviderType:
    """Tests for ProviderType enum."""

    def test_provider_type_exists(self):
        """ProviderType enum should exist."""
        from repo_ctx.models import ProviderType

        assert ProviderType is not None

    def test_provider_type_values(self):
        """ProviderType should have github, gitlab, local values."""
        from repo_ctx.models import ProviderType

        assert ProviderType.GITHUB.value == "github"
        assert ProviderType.GITLAB.value == "gitlab"
        assert ProviderType.LOCAL.value == "local"

    def test_provider_type_from_string(self):
        """ProviderType should be creatable from string."""
        from repo_ctx.models import ProviderType

        assert ProviderType.from_string("github") == ProviderType.GITHUB
        assert ProviderType.from_string("gitlab") == ProviderType.GITLAB
        assert ProviderType.from_string("local") == ProviderType.LOCAL
        assert ProviderType.from_string("GITHUB") == ProviderType.GITHUB

    def test_provider_type_auto(self):
        """ProviderType should have AUTO value for auto-detection."""
        from repo_ctx.models import ProviderType

        assert ProviderType.AUTO.value == "auto"


class TestSymbolType:
    """Tests for SymbolType enum."""

    def test_symbol_type_exists(self):
        """SymbolType enum should exist."""
        from repo_ctx.models import SymbolType

        assert SymbolType is not None

    def test_symbol_type_values(self):
        """SymbolType should have common symbol types."""
        from repo_ctx.models import SymbolType

        assert SymbolType.FUNCTION.value == "function"
        assert SymbolType.CLASS.value == "class"
        assert SymbolType.METHOD.value == "method"
        assert SymbolType.INTERFACE.value == "interface"
        assert SymbolType.ENUM.value == "enum"
        assert SymbolType.VARIABLE.value == "variable"
        assert SymbolType.CONSTANT.value == "constant"
        assert SymbolType.MODULE.value == "module"

    def test_symbol_type_from_string(self):
        """SymbolType should be creatable from string."""
        from repo_ctx.models import SymbolType

        assert SymbolType.from_string("function") == SymbolType.FUNCTION
        assert SymbolType.from_string("CLASS") == SymbolType.CLASS


class TestChunkType:
    """Tests for ChunkType enum."""

    def test_chunk_type_exists(self):
        """ChunkType enum should exist."""
        from repo_ctx.models import ChunkType

        assert ChunkType is not None

    def test_chunk_type_values(self):
        """ChunkType should have code, documentation, mixed values."""
        from repo_ctx.models import ChunkType

        assert ChunkType.CODE.value == "code"
        assert ChunkType.DOCUMENTATION.value == "documentation"
        assert ChunkType.MIXED.value == "mixed"


class TestDocumentEnhancements:
    """Tests for Document model enhancements."""

    def test_document_has_quality_score(self):
        """Document should have quality_score field."""
        from repo_ctx.models import Document

        doc = Document(
            version_id=1,
            file_path="README.md",
            content="# Hello",
            quality_score=0.85,
        )
        assert doc.quality_score == 0.85

    def test_document_quality_score_default(self):
        """Document quality_score should default to 0.5."""
        from repo_ctx.models import Document

        doc = Document(version_id=1, file_path="test.md", content="test")
        assert doc.quality_score == 0.5

    def test_document_has_classification(self):
        """Document should have classification field."""
        from repo_ctx.models import Document

        doc = Document(
            version_id=1,
            file_path="tutorial.md",
            content="# Tutorial",
            classification="tutorial",
        )
        assert doc.classification == "tutorial"

    def test_document_classification_default(self):
        """Document classification should default to None."""
        from repo_ctx.models import Document

        doc = Document(version_id=1, file_path="test.md", content="test")
        assert doc.classification is None

    def test_document_has_metadata(self):
        """Document should have metadata field."""
        from repo_ctx.models import Document

        doc = Document(
            version_id=1,
            file_path="api.md",
            content="# API",
            metadata={"author": "test", "tags": ["api", "reference"]},
        )
        assert doc.metadata == {"author": "test", "tags": ["api", "reference"]}

    def test_document_metadata_default(self):
        """Document metadata should default to None."""
        from repo_ctx.models import Document

        doc = Document(version_id=1, file_path="test.md", content="test")
        assert doc.metadata is None


class TestSymbol:
    """Tests for Symbol model."""

    def test_symbol_exists(self):
        """Symbol class should exist."""
        from repo_ctx.models import Symbol

        assert Symbol is not None

    def test_symbol_basic_fields(self):
        """Symbol should have basic fields."""
        from repo_ctx.models import Symbol, SymbolType

        symbol = Symbol(
            library_id=1,
            name="my_function",
            qualified_name="module.my_function",
            symbol_type=SymbolType.FUNCTION,
            file_path="module.py",
            line_start=10,
            line_end=20,
        )
        assert symbol.library_id == 1
        assert symbol.name == "my_function"
        assert symbol.qualified_name == "module.my_function"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.file_path == "module.py"
        assert symbol.line_start == 10
        assert symbol.line_end == 20

    def test_symbol_optional_fields(self):
        """Symbol should have optional fields."""
        from repo_ctx.models import Symbol, SymbolType

        symbol = Symbol(
            library_id=1,
            name="MyClass",
            qualified_name="module.MyClass",
            symbol_type=SymbolType.CLASS,
            file_path="module.py",
            line_start=1,
            line_end=100,
            signature="class MyClass(BaseClass)",
            documentation="A class that does things.",
            visibility="public",
            language="python",
            parent_symbol="module",
            metadata={"decorators": ["dataclass"]},
        )
        assert symbol.signature == "class MyClass(BaseClass)"
        assert symbol.documentation == "A class that does things."
        assert symbol.visibility == "public"
        assert symbol.language == "python"
        assert symbol.parent_symbol == "module"
        assert symbol.metadata == {"decorators": ["dataclass"]}

    def test_symbol_id_optional(self):
        """Symbol id should be optional (None before DB insert)."""
        from repo_ctx.models import Symbol, SymbolType

        symbol = Symbol(
            library_id=1,
            name="test",
            qualified_name="test",
            symbol_type=SymbolType.FUNCTION,
            file_path="test.py",
            line_start=1,
            line_end=5,
        )
        assert symbol.id is None


class TestChunk:
    """Tests for Chunk model."""

    def test_chunk_exists(self):
        """Chunk class should exist."""
        from repo_ctx.models import Chunk

        assert Chunk is not None

    def test_chunk_from_document(self):
        """Chunk should support document source."""
        from repo_ctx.models import Chunk, ChunkType

        chunk = Chunk(
            content="This is a chunk of text.",
            chunk_type=ChunkType.DOCUMENTATION,
            document_id=42,
            start_line=1,
            end_line=10,
            tokens=15,
        )
        assert chunk.document_id == 42
        assert chunk.symbol_id is None
        assert chunk.chunk_type == ChunkType.DOCUMENTATION

    def test_chunk_from_symbol(self):
        """Chunk should support symbol source."""
        from repo_ctx.models import Chunk, ChunkType

        chunk = Chunk(
            content="def my_function(): pass",
            chunk_type=ChunkType.CODE,
            symbol_id=123,
            start_line=10,
            end_line=12,
            tokens=8,
        )
        assert chunk.symbol_id == 123
        assert chunk.document_id is None
        assert chunk.chunk_type == ChunkType.CODE

    def test_chunk_embedding_id(self):
        """Chunk should have optional embedding_id field."""
        from repo_ctx.models import Chunk, ChunkType

        chunk = Chunk(
            content="test",
            chunk_type=ChunkType.MIXED,
            embedding_id="emb_abc123",
        )
        assert chunk.embedding_id == "emb_abc123"

    def test_chunk_metadata(self):
        """Chunk should have optional metadata field."""
        from repo_ctx.models import Chunk, ChunkType

        chunk = Chunk(
            content="test",
            chunk_type=ChunkType.CODE,
            metadata={"language": "python", "complexity": "low"},
        )
        assert chunk.metadata == {"language": "python", "complexity": "low"}


class TestClassification:
    """Tests for Classification model."""

    def test_classification_exists(self):
        """Classification class should exist."""
        from repo_ctx.models import Classification

        assert Classification is not None

    def test_classification_fields(self):
        """Classification should have required fields."""
        from repo_ctx.models import Classification

        classification = Classification(
            entity_type="document",
            entity_id=42,
            classification="tutorial",
            confidence=0.95,
            model="gpt-5-mini",
        )
        assert classification.entity_type == "document"
        assert classification.entity_id == 42
        assert classification.classification == "tutorial"
        assert classification.confidence == 0.95
        assert classification.model == "gpt-5-mini"

    def test_classification_created_at(self):
        """Classification should have created_at timestamp."""
        from repo_ctx.models import Classification

        classification = Classification(
            entity_type="symbol",
            entity_id=1,
            classification="utility",
        )
        assert classification.created_at is not None
        assert isinstance(classification.created_at, datetime)


class TestDependency:
    """Tests for Dependency model."""

    def test_dependency_exists(self):
        """Dependency class should exist."""
        from repo_ctx.models import Dependency

        assert Dependency is not None

    def test_dependency_fields(self):
        """Dependency should have required fields."""
        from repo_ctx.models import Dependency

        dep = Dependency(
            library_id=1,
            source_name="module_a",
            target_name="module_b",
            dependency_type="imports",
        )
        assert dep.library_id == 1
        assert dep.source_name == "module_a"
        assert dep.target_name == "module_b"
        assert dep.dependency_type == "imports"

    def test_dependency_optional_fields(self):
        """Dependency should have optional source_file and target_file."""
        from repo_ctx.models import Dependency

        dep = Dependency(
            library_id=1,
            source_name="MyClass",
            target_name="BaseClass",
            dependency_type="extends",
            source_file="child.py",
            target_file="parent.py",
        )
        assert dep.source_file == "child.py"
        assert dep.target_file == "parent.py"


class TestLibraryEnhancements:
    """Tests for Library model enhancements."""

    def test_library_provider_type(self):
        """Library should support ProviderType enum."""
        from repo_ctx.models import Library, ProviderType

        lib = Library(
            group_name="owner",
            project_name="repo",
            description="A test repo",
            default_version="main",
            provider=ProviderType.GITHUB,
        )
        assert lib.provider == ProviderType.GITHUB

    def test_library_provider_string_compatibility(self):
        """Library should still work with string provider for backward compatibility."""
        from repo_ctx.models import Library

        lib = Library(
            group_name="owner",
            project_name="repo",
            description="A test repo",
            default_version="main",
            provider="github",
        )
        # Should still work with string
        assert lib.provider == "github"
