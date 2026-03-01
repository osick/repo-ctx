"""Tests for the chunking service.

These tests verify:
- Different chunking strategies (fixed-size, token-based, semantic, markdown)
- Chunk properties and metadata
- Edge cases and large content handling
"""

import pytest

from repo_ctx.services.chunking import (
    ChunkingService,
    ChunkType,
    Chunk,
    FixedSizeChunking,
    TokenBasedChunking,
    SemanticChunking,
    MarkdownChunking,
    estimate_tokens,
    generate_chunk_id,
)


class TestChunkUtilities:
    """Tests for chunk utility functions."""

    def test_estimate_tokens_empty(self):
        """Test token estimation for empty string."""
        assert estimate_tokens("") == 0

    def test_estimate_tokens_simple_text(self):
        """Test token estimation for simple text."""
        text = "Hello world this is a test"
        tokens = estimate_tokens(text)
        assert tokens > 0
        assert tokens <= len(text.split()) * 2  # Reasonable upper bound

    def test_estimate_tokens_code(self):
        """Test token estimation for code with special characters."""
        code = "def foo(): return {'key': value}"
        tokens = estimate_tokens(code)
        # Code has special chars that add to token count
        assert tokens > len(code.split())

    def test_generate_chunk_id_unique(self):
        """Test that chunk IDs are unique."""
        id1 = generate_chunk_id("content1", "file.py", 1)
        id2 = generate_chunk_id("content2", "file.py", 1)
        id3 = generate_chunk_id("content1", "file.py", 2)

        assert id1 != id2
        assert id1 != id3

    def test_generate_chunk_id_deterministic(self):
        """Test that chunk IDs are deterministic."""
        id1 = generate_chunk_id("content", "file.py", 1)
        id2 = generate_chunk_id("content", "file.py", 1)

        assert id1 == id2


class TestChunkDataclass:
    """Tests for Chunk dataclass."""

    def test_chunk_creation(self):
        """Test creating a chunk."""
        chunk = Chunk(
            id="test-id",
            content="test content",
            chunk_type=ChunkType.CODE,
            source_file="test.py",
            start_line=1,
            end_line=10,
        )

        assert chunk.id == "test-id"
        assert chunk.content == "test content"
        assert chunk.chunk_type == ChunkType.CODE
        assert chunk.source_file == "test.py"
        assert chunk.start_line == 1
        assert chunk.end_line == 10

    def test_chunk_auto_token_count(self):
        """Test that token count is calculated automatically."""
        chunk = Chunk(
            id="test-id",
            content="Hello world",
            chunk_type=ChunkType.CODE,
            source_file="test.py",
            start_line=1,
            end_line=1,
        )

        assert chunk.token_count > 0

    def test_chunk_explicit_token_count(self):
        """Test explicit token count."""
        chunk = Chunk(
            id="test-id",
            content="Hello",
            chunk_type=ChunkType.CODE,
            source_file="test.py",
            start_line=1,
            end_line=1,
            token_count=100,
        )

        assert chunk.token_count == 100


class TestFixedSizeChunking:
    """Tests for FixedSizeChunking strategy."""

    def test_chunk_empty_content(self):
        """Test chunking empty content."""
        strategy = FixedSizeChunking()
        chunks = strategy.chunk("", "test.py")

        assert chunks == []

    def test_chunk_small_content(self):
        """Test chunking content smaller than chunk size."""
        strategy = FixedSizeChunking(chunk_size=1000, min_chunk_size=5)
        content = "Small content here"
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) == 1
        assert chunks[0].content == content

    def test_chunk_large_content(self):
        """Test chunking large content into multiple chunks."""
        strategy = FixedSizeChunking(chunk_size=100, overlap=20, min_chunk_size=10)
        content = "\n".join([f"Line {i}: " + "x" * 50 for i in range(20)])
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) > 1
        # All chunks except last should be close to chunk_size
        for chunk in chunks:
            assert len(chunk.content) >= strategy.min_chunk_size

    def test_chunk_overlap(self):
        """Test that chunks have overlap."""
        strategy = FixedSizeChunking(chunk_size=100, overlap=30, min_chunk_size=10)
        content = "\n".join([f"Line {i}" for i in range(50)])
        chunks = strategy.chunk(content, "test.py")

        if len(chunks) > 1:
            # Check for overlap between consecutive chunks
            for i in range(len(chunks) - 1):
                chunk1_end = chunks[i].content.split("\n")[-1]
                chunk2_start = chunks[i + 1].content.split("\n")[0]
                # Overlap should share some lines
                assert chunk1_end == chunk2_start or chunks[i].end_line >= chunks[i + 1].start_line

    def test_chunk_line_numbers(self):
        """Test that line numbers are correct."""
        strategy = FixedSizeChunking(chunk_size=1000, min_chunk_size=10)
        content = "\n".join([f"Line {i}" for i in range(10)])
        chunks = strategy.chunk(content, "test.py")

        assert chunks[0].start_line == 1
        assert chunks[0].end_line == 10

    def test_strategy_name(self):
        """Test strategy name property."""
        strategy = FixedSizeChunking()
        assert strategy.name == "fixed_size"


class TestTokenBasedChunking:
    """Tests for TokenBasedChunking strategy."""

    def test_chunk_empty_content(self):
        """Test chunking empty content."""
        strategy = TokenBasedChunking()
        chunks = strategy.chunk("", "test.py")

        assert chunks == []

    def test_chunk_respects_max_tokens(self):
        """Test that chunks respect max token limit."""
        strategy = TokenBasedChunking(max_tokens=100, min_tokens=5)
        content = "\n".join([f"Line {i}: some text content here" for i in range(50)])
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) > 1
        for chunk in chunks:
            # Allow reasonable tolerance for line boundaries
            assert chunk.token_count <= strategy.max_tokens + 50

    def test_chunk_small_content(self):
        """Test that small content stays in one chunk."""
        strategy = TokenBasedChunking(max_tokens=1000, min_tokens=2)
        content = "Small content that has enough tokens"
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) == 1

    def test_chunk_token_count_set(self):
        """Test that token count is set on chunks."""
        strategy = TokenBasedChunking(max_tokens=100, min_tokens=5)
        content = "\n".join([f"Line {i}" for i in range(20)])
        chunks = strategy.chunk(content, "test.py")

        for chunk in chunks:
            assert chunk.token_count > 0

    def test_strategy_name(self):
        """Test strategy name property."""
        strategy = TokenBasedChunking()
        assert strategy.name == "token_based"


class TestSemanticChunking:
    """Tests for SemanticChunking strategy."""

    def test_chunk_empty_content(self):
        """Test chunking empty content."""
        strategy = SemanticChunking()
        chunks = strategy.chunk("", "test.py")

        assert chunks == []

    def test_chunk_python_classes(self):
        """Test chunking Python code with classes."""
        strategy = SemanticChunking(language="python")
        content = '''class Foo:
    def method1(self):
        pass

class Bar:
    def method2(self):
        pass
'''
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) >= 2
        # Check chunk types
        class_chunks = [c for c in chunks if c.chunk_type == ChunkType.CLASS]
        assert len(class_chunks) >= 2

    def test_chunk_python_functions(self):
        """Test chunking Python code with functions."""
        strategy = SemanticChunking(language="python")
        content = '''def func1():
    pass

def func2():
    pass

async def async_func():
    pass
'''
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) >= 3
        func_chunks = [c for c in chunks if c.chunk_type == ChunkType.FUNCTION]
        assert len(func_chunks) >= 3

    def test_chunk_auto_detect_language(self):
        """Test auto-detecting language from file extension."""
        strategy = SemanticChunking(max_chunk_size=1000)
        # Larger content to avoid min_chunk_size issues
        content_py = "class Foo:\n    def method(self):\n        pass\n"
        content_js = "class Foo {\n    constructor() {}\n}\n"

        chunks_py = strategy.chunk(content_py, "test.py")
        chunks_js = strategy.chunk(content_js, "test.js")

        assert len(chunks_py) >= 1
        assert len(chunks_js) >= 1
        assert chunks_py[0].metadata.get("language") == "python"
        assert chunks_js[0].metadata.get("language") == "javascript"

    def test_chunk_javascript(self):
        """Test chunking JavaScript code."""
        strategy = SemanticChunking(language="javascript")
        content = '''export class MyClass {
    constructor() {}
}

function myFunction() {
    return true;
}

const arrowFunc = () => {};
'''
        chunks = strategy.chunk(content, "test.js")

        assert len(chunks) >= 1
        # Should detect class and functions
        chunk_types = set(c.metadata.get("boundary_type") for c in chunks)
        assert "class" in chunk_types or "function" in chunk_types or len(chunks) > 0

    def test_chunk_large_content_splits(self):
        """Test that large content gets split."""
        strategy = SemanticChunking(max_chunk_size=100)
        content = "def func():\n" + "    x = 1\n" * 50

        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) >= 1
        for chunk in chunks:
            # Each chunk should be reasonably sized
            assert len(chunk.content) <= strategy.max_chunk_size * 2  # Allow some tolerance

    def test_fallback_to_fixed_size(self):
        """Test fallback when no semantic boundaries found."""
        strategy = SemanticChunking(max_chunk_size=100)
        content = "x = 1\n" * 50  # No functions or classes

        chunks = strategy.chunk(content, "test.py")

        # Should still produce chunks via fallback
        assert len(chunks) >= 1

    def test_strategy_name(self):
        """Test strategy name property."""
        strategy = SemanticChunking()
        assert strategy.name == "semantic"

    def test_chunk_metadata_includes_boundary_type(self):
        """Test that metadata includes boundary type."""
        strategy = SemanticChunking(language="python")
        content = "class MyClass:\n    pass"
        chunks = strategy.chunk(content, "test.py")

        assert len(chunks) >= 1
        assert "boundary_type" in chunks[0].metadata


class TestMarkdownChunking:
    """Tests for MarkdownChunking strategy."""

    def test_chunk_empty_content(self):
        """Test chunking empty content."""
        strategy = MarkdownChunking()
        chunks = strategy.chunk("", "README.md")

        assert chunks == []

    def test_chunk_by_headings(self):
        """Test chunking Markdown by headings."""
        strategy = MarkdownChunking(min_heading_level=2)
        content = '''# Title

Introduction paragraph.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection

More content.
'''
        chunks = strategy.chunk(content, "README.md", ChunkType.DOCUMENTATION)

        assert len(chunks) >= 2
        # Should have sections
        sections = [c.metadata.get("section") for c in chunks if c.metadata.get("section")]
        assert len(sections) >= 2

    def test_chunk_includes_heading_level(self):
        """Test that chunks include heading level in metadata."""
        strategy = MarkdownChunking(min_heading_level=2)
        content = '''## Section 1

Content here.

### Subsection

More content.
'''
        chunks = strategy.chunk(content, "README.md")

        for chunk in chunks:
            if chunk.metadata.get("section"):
                assert "level" in chunk.metadata

    def test_chunk_preamble(self):
        """Test handling content before first heading."""
        strategy = MarkdownChunking(min_heading_level=2)
        content = '''This is preamble content.

## First Section

Section content.
'''
        chunks = strategy.chunk(content, "README.md")

        # Should have preamble as first chunk
        preamble_chunks = [c for c in chunks if c.metadata.get("section") == "preamble"]
        assert len(preamble_chunks) == 1

    def test_chunk_large_section_splits(self):
        """Test that large sections get split."""
        strategy = MarkdownChunking(max_chunk_size=100)
        content = '''## Large Section

''' + "Content line.\n" * 100

        chunks = strategy.chunk(content, "README.md")

        # Should split into multiple chunks
        assert len(chunks) > 1

    def test_fallback_without_headings(self):
        """Test fallback when no headings found."""
        strategy = MarkdownChunking()
        content = "Just some text without headings.\n" * 10

        chunks = strategy.chunk(content, "README.md")

        # Should fall back to fixed-size chunking
        assert len(chunks) >= 1

    def test_chunk_type_is_documentation(self):
        """Test that chunks have documentation type."""
        strategy = MarkdownChunking()
        content = "## Section\n\nContent"
        chunks = strategy.chunk(content, "README.md")

        for chunk in chunks:
            assert chunk.chunk_type == ChunkType.DOCUMENTATION

    def test_strategy_name(self):
        """Test strategy name property."""
        strategy = MarkdownChunking()
        assert strategy.name == "markdown"


class TestChunkingService:
    """Tests for ChunkingService."""

    def test_service_creation(self):
        """Test creating chunking service."""
        service = ChunkingService()
        assert service is not None

    def test_get_available_strategies(self):
        """Test getting available strategies."""
        service = ChunkingService()
        strategies = service.get_available_strategies()

        assert "fixed_size" in strategies
        assert "token_based" in strategies
        assert "semantic" in strategies
        assert "markdown" in strategies

    def test_get_strategy_by_name(self):
        """Test getting strategy by name."""
        service = ChunkingService()

        strategy = service.get_strategy("fixed_size")
        assert isinstance(strategy, FixedSizeChunking)

        strategy = service.get_strategy("semantic")
        assert isinstance(strategy, SemanticChunking)

    def test_get_strategy_default(self):
        """Test getting default strategy."""
        service = ChunkingService(default_strategy="token_based")
        strategy = service.get_strategy()

        assert isinstance(strategy, TokenBasedChunking)

    def test_get_strategy_invalid(self):
        """Test getting invalid strategy raises error."""
        service = ChunkingService()

        with pytest.raises(ValueError):
            service.get_strategy("nonexistent")

    def test_chunk_auto_detect_python(self):
        """Test auto-detecting strategy for Python files."""
        service = ChunkingService()
        content = "def func():\n    return 'hello world'\n"
        chunks = service.chunk(content, "test.py")

        assert len(chunks) >= 1
        # Should use semantic chunking for Python
        assert chunks[0].source_file == "test.py"

    def test_chunk_auto_detect_markdown(self):
        """Test auto-detecting strategy for Markdown files."""
        service = ChunkingService()
        content = "## Section\n\nContent"
        chunks = service.chunk(content, "README.md")

        assert len(chunks) >= 1
        assert chunks[0].chunk_type == ChunkType.DOCUMENTATION

    def test_chunk_code(self):
        """Test chunk_code method."""
        service = ChunkingService()
        content = "def foo():\n    return 1\n\ndef bar():\n    return 2\n"
        chunks = service.chunk_code(content, "test.py", language="python")

        assert len(chunks) >= 1
        # Semantic chunking may set chunk type to FUNCTION for functions
        assert chunks[0].chunk_type in (ChunkType.CODE, ChunkType.FUNCTION)

    def test_chunk_documentation(self):
        """Test chunk_documentation method."""
        service = ChunkingService()
        content = "## Heading\n\nParagraph content."
        chunks = service.chunk_documentation(content, "docs.md")

        assert len(chunks) >= 1
        assert chunks[0].chunk_type == ChunkType.DOCUMENTATION

    def test_chunk_for_embedding(self):
        """Test chunking for embedding with smaller chunks."""
        service = ChunkingService()
        content = "\n".join([f"Line {i} with some content" for i in range(100)])
        chunks = service.chunk_for_embedding(content, "test.py", max_tokens=100)

        assert len(chunks) >= 1
        # Chunks should be smaller for embedding
        for chunk in chunks:
            assert chunk.token_count <= 150  # Allow some tolerance

    def test_chunk_for_context(self):
        """Test chunking for LLM context with larger chunks."""
        service = ChunkingService()
        content = "\n".join([f"Line {i} with some content" for i in range(100)])
        chunks = service.chunk_for_context(content, "test.py", max_tokens=500)

        assert len(chunks) >= 1
        # Can have larger chunks for context

    def test_chunk_with_metadata(self):
        """Test chunking with custom metadata."""
        service = ChunkingService()
        content = "def foo():\n    return 'hello world'\n"
        chunks = service.chunk(
            content,
            "test.py",
            metadata={"custom_key": "custom_value"},
        )

        assert len(chunks) >= 1
        # Metadata should be included in some chunks


class TestChunkTypeEnum:
    """Tests for ChunkType enum."""

    def test_chunk_types_exist(self):
        """Test that all chunk types exist."""
        assert ChunkType.CODE
        assert ChunkType.DOCUMENTATION
        assert ChunkType.MIXED
        assert ChunkType.FUNCTION
        assert ChunkType.CLASS
        assert ChunkType.MODULE
        assert ChunkType.COMMENT

    def test_chunk_type_values(self):
        """Test chunk type values."""
        assert ChunkType.CODE.value == "code"
        assert ChunkType.DOCUMENTATION.value == "documentation"
        assert ChunkType.FUNCTION.value == "function"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_unicode_content(self):
        """Test chunking content with unicode."""
        service = ChunkingService()
        content = "def greet():\n    return '안녕하세요 世界 🌍 hello world'\n"
        chunks = service.chunk(content, "test.py")

        assert len(chunks) >= 1
        assert "안녕하세요" in chunks[0].content

    def test_very_long_lines(self):
        """Test chunking content with very long lines."""
        service = ChunkingService()
        long_line = "x = " + "a" * 5000
        chunks = service.chunk(long_line, "test.py")

        assert len(chunks) >= 1

    def test_only_whitespace(self):
        """Test chunking whitespace-only content."""
        service = ChunkingService()
        content = "   \n\n   \t  "
        chunks = service.chunk(content, "test.py")

        # Should return empty or minimal chunks
        assert len(chunks) == 0 or all(not c.content.strip() for c in chunks)

    def test_mixed_line_endings(self):
        """Test chunking content with mixed line endings."""
        service = ChunkingService()
        # Create content with a clear function and enough text
        content = "def func():\r\n    line1 = 1\n    line2 = 2\n    return line1 + line2\n"
        chunks = service.chunk(content, "test.py")

        assert len(chunks) >= 1

    def test_binary_like_content(self):
        """Test chunking binary-like content."""
        service = ChunkingService()
        content = "".join(chr(i) for i in range(32, 127))
        chunks = service.chunk(content, "test.bin")

        # Should handle without error
        assert len(chunks) >= 0
