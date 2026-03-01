"""Chunking service for splitting content into optimal segments.

This module provides various chunking strategies for code and documentation
to optimize for embedding, retrieval, and LLM context windows.
"""

import hashlib
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("repo_ctx.services.chunking")


class ChunkType(Enum):
    """Types of content chunks."""

    CODE = "code"
    DOCUMENTATION = "documentation"
    MIXED = "mixed"
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    COMMENT = "comment"


@dataclass
class Chunk:
    """A content chunk with metadata.

    Attributes:
        id: Unique chunk identifier.
        content: Chunk text content.
        chunk_type: Type of chunk.
        source_file: Source file path.
        start_line: Starting line number (1-indexed).
        end_line: Ending line number (1-indexed).
        token_count: Estimated token count.
        metadata: Additional metadata.
    """

    id: str
    content: str
    chunk_type: ChunkType
    source_file: str
    start_line: int
    end_line: int
    token_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate token count if not provided."""
        if self.token_count == 0:
            self.token_count = estimate_tokens(self.content)


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Uses a simple heuristic: ~4 characters per token for English,
    adjusted for code which tends to be more dense.

    Args:
        text: Text to estimate.

    Returns:
        Estimated token count.
    """
    if not text:
        return 0

    # Count words and special characters
    words = len(text.split())
    special_chars = sum(1 for c in text if c in "{}[]().,;:!?@#$%^&*+-=<>/\\|`~")

    # Code tends to have more tokens due to syntax
    return words + special_chars // 2


def generate_chunk_id(content: str, source_file: str, start_line: int) -> str:
    """Generate a unique chunk ID.

    Args:
        content: Chunk content.
        source_file: Source file path.
        start_line: Starting line number.

    Returns:
        Unique chunk ID.
    """
    data = f"{source_file}:{start_line}:{content[:100]}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


class ChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(
        self,
        content: str,
        source_file: str,
        chunk_type: ChunkType = ChunkType.CODE,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Split content into chunks.

        Args:
            content: Content to chunk.
            source_file: Source file path.
            chunk_type: Type of content.
            metadata: Additional metadata.

        Returns:
            List of chunks.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name."""
        pass


class FixedSizeChunking(ChunkingStrategy):
    """Fixed-size chunking with overlap.

    Splits content into fixed-size chunks with configurable overlap.
    Simple but effective for consistent chunk sizes.
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        overlap: int = 100,
        min_chunk_size: int = 50,
    ) -> None:
        """Initialize fixed-size chunking.

        Args:
            chunk_size: Target chunk size in characters.
            overlap: Overlap between chunks in characters.
            min_chunk_size: Minimum chunk size to keep.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size

    @property
    def name(self) -> str:
        return "fixed_size"

    def chunk(
        self,
        content: str,
        source_file: str,
        chunk_type: ChunkType = ChunkType.CODE,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Split content into fixed-size chunks."""
        if not content:
            return []

        chunks = []
        lines = content.split("\n")
        total_lines = len(lines)

        current_chunk = []
        current_size = 0
        chunk_start_line = 1

        for line_idx, line in enumerate(lines):
            line_len = len(line) + 1  # +1 for newline

            if current_size + line_len > self.chunk_size and current_chunk:
                # Create chunk
                chunk_content = "\n".join(current_chunk)
                if len(chunk_content) >= self.min_chunk_size:
                    chunk_id = generate_chunk_id(
                        chunk_content, source_file, chunk_start_line
                    )
                    chunks.append(
                        Chunk(
                            id=chunk_id,
                            content=chunk_content,
                            chunk_type=chunk_type,
                            source_file=source_file,
                            start_line=chunk_start_line,
                            end_line=chunk_start_line + len(current_chunk) - 1,
                            metadata=metadata or {},
                        )
                    )

                # Calculate overlap
                overlap_lines = []
                overlap_size = 0
                for prev_line in reversed(current_chunk):
                    if overlap_size + len(prev_line) + 1 > self.overlap:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_size += len(prev_line) + 1

                # Start new chunk with overlap
                current_chunk = overlap_lines
                current_size = overlap_size
                chunk_start_line = line_idx + 1 - len(overlap_lines)

            current_chunk.append(line)
            current_size += line_len

        # Handle remaining content
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            if len(chunk_content) >= self.min_chunk_size:
                chunk_id = generate_chunk_id(
                    chunk_content, source_file, chunk_start_line
                )
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        chunk_type=chunk_type,
                        source_file=source_file,
                        start_line=chunk_start_line,
                        end_line=total_lines,
                        metadata=metadata or {},
                    )
                )

        return chunks


class TokenBasedChunking(ChunkingStrategy):
    """Token-based chunking for LLM context limits.

    Splits content based on estimated token count, useful for
    staying within LLM context windows.
    """

    def __init__(
        self,
        max_tokens: int = 2000,
        overlap_tokens: int = 100,
        min_tokens: int = 50,
    ) -> None:
        """Initialize token-based chunking.

        Args:
            max_tokens: Maximum tokens per chunk.
            overlap_tokens: Overlap in tokens.
            min_tokens: Minimum tokens to keep.
        """
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.min_tokens = min_tokens

    @property
    def name(self) -> str:
        return "token_based"

    def chunk(
        self,
        content: str,
        source_file: str,
        chunk_type: ChunkType = ChunkType.CODE,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Split content based on token count."""
        if not content:
            return []

        chunks = []
        lines = content.split("\n")
        total_lines = len(lines)

        current_chunk = []
        current_tokens = 0
        chunk_start_line = 1

        for line_idx, line in enumerate(lines):
            line_tokens = estimate_tokens(line)

            if current_tokens + line_tokens > self.max_tokens and current_chunk:
                # Create chunk
                chunk_content = "\n".join(current_chunk)
                chunk_tokens = estimate_tokens(chunk_content)

                if chunk_tokens >= self.min_tokens:
                    chunk_id = generate_chunk_id(
                        chunk_content, source_file, chunk_start_line
                    )
                    chunks.append(
                        Chunk(
                            id=chunk_id,
                            content=chunk_content,
                            chunk_type=chunk_type,
                            source_file=source_file,
                            start_line=chunk_start_line,
                            end_line=chunk_start_line + len(current_chunk) - 1,
                            token_count=chunk_tokens,
                            metadata=metadata or {},
                        )
                    )

                # Calculate overlap
                overlap_lines = []
                overlap_tokens = 0
                for prev_line in reversed(current_chunk):
                    prev_tokens = estimate_tokens(prev_line)
                    if overlap_tokens + prev_tokens > self.overlap_tokens:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_tokens += prev_tokens

                # Start new chunk
                current_chunk = overlap_lines
                current_tokens = overlap_tokens
                chunk_start_line = line_idx + 1 - len(overlap_lines)

            current_chunk.append(line)
            current_tokens += line_tokens

        # Handle remaining
        if current_chunk:
            chunk_content = "\n".join(current_chunk)
            chunk_tokens = estimate_tokens(chunk_content)

            if chunk_tokens >= self.min_tokens:
                chunk_id = generate_chunk_id(
                    chunk_content, source_file, chunk_start_line
                )
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        chunk_type=chunk_type,
                        source_file=source_file,
                        start_line=chunk_start_line,
                        end_line=total_lines,
                        token_count=chunk_tokens,
                        metadata=metadata or {},
                    )
                )

        return chunks


class SemanticChunking(ChunkingStrategy):
    """Semantic chunking that respects code structure.

    Splits code at logical boundaries like functions, classes,
    and documentation sections. Produces more meaningful chunks.
    """

    # Patterns for detecting code boundaries
    PATTERNS = {
        "python": {
            "class": r"^class\s+\w+",
            "function": r"^(?:async\s+)?def\s+\w+",
            "decorator": r"^@\w+",
        },
        "javascript": {
            "class": r"^(?:export\s+)?class\s+\w+",
            "function": r"^(?:export\s+)?(?:async\s+)?function\s+\w+",
            "arrow_function": r"^(?:export\s+)?(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?\(",
            "method": r"^\s+(?:async\s+)?\w+\s*\(",
        },
        "typescript": {
            "class": r"^(?:export\s+)?(?:abstract\s+)?class\s+\w+",
            "interface": r"^(?:export\s+)?interface\s+\w+",
            "function": r"^(?:export\s+)?(?:async\s+)?function\s+\w+",
            "type": r"^(?:export\s+)?type\s+\w+\s*=",
        },
        "java": {
            "class": r"^(?:public|private|protected)?\s*(?:abstract|final)?\s*class\s+\w+",
            "interface": r"^(?:public)?\s*interface\s+\w+",
            "method": r"^\s+(?:public|private|protected)?\s*(?:static)?\s*\w+\s+\w+\s*\(",
        },
        "kotlin": {
            "class": r"^(?:open|data|sealed|abstract)?\s*class\s+\w+",
            "object": r"^object\s+\w+",
            "fun": r"^(?:suspend\s+)?fun\s+\w+",
            "interface": r"^interface\s+\w+",
        },
        "go": {
            "struct": r"^type\s+\w+\s+struct",
            "interface": r"^type\s+\w+\s+interface",
            "function": r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?\w+\s*\(",
        },
    }

    def __init__(
        self,
        max_chunk_size: int = 2000,
        include_context: bool = True,
        language: Optional[str] = None,
    ) -> None:
        """Initialize semantic chunking.

        Args:
            max_chunk_size: Maximum chunk size in characters.
            include_context: Include surrounding context.
            language: Programming language (auto-detect if None).
        """
        self.max_chunk_size = max_chunk_size
        self.include_context = include_context
        self.language = language

    @property
    def name(self) -> str:
        return "semantic"

    def _detect_language(self, source_file: str) -> str:
        """Detect language from file extension."""
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".kt": "kotlin",
            ".go": "go",
        }
        for ext, lang in ext_map.items():
            if source_file.endswith(ext):
                return lang
        return "python"  # Default

    def _find_boundaries(
        self, lines: list[str], language: str
    ) -> list[tuple[int, str]]:
        """Find semantic boundaries in code.

        Returns list of (line_index, boundary_type) tuples.
        """
        boundaries = []
        patterns = self.PATTERNS.get(language, self.PATTERNS["python"])

        for i, line in enumerate(lines):
            for boundary_type, pattern in patterns.items():
                if re.match(pattern, line):
                    boundaries.append((i, boundary_type))
                    break

        return boundaries

    def chunk(
        self,
        content: str,
        source_file: str,
        chunk_type: ChunkType = ChunkType.CODE,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Split content at semantic boundaries."""
        if not content:
            return []

        language = self.language or self._detect_language(source_file)
        lines = content.split("\n")
        total_lines = len(lines)

        # Find boundaries
        boundaries = self._find_boundaries(lines, language)

        if not boundaries:
            # No boundaries found, fall back to fixed-size
            fallback = FixedSizeChunking(
                chunk_size=self.max_chunk_size,
                overlap=100,
            )
            return fallback.chunk(content, source_file, chunk_type, metadata)

        # Add start and end boundaries
        if boundaries[0][0] != 0:
            boundaries.insert(0, (0, "module_header"))
        if boundaries[-1][0] != total_lines - 1:
            boundaries.append((total_lines, "module_end"))

        chunks = []

        for i in range(len(boundaries) - 1):
            start_idx, boundary_type = boundaries[i]
            end_idx = boundaries[i + 1][0]

            # Extract chunk content
            chunk_lines = lines[start_idx:end_idx]
            chunk_content = "\n".join(chunk_lines)

            # Skip empty chunks
            if not chunk_content.strip():
                continue

            # Split if too large
            if len(chunk_content) > self.max_chunk_size:
                sub_chunks = self._split_large_chunk(
                    chunk_lines, source_file, start_idx + 1, boundary_type, metadata
                )
                chunks.extend(sub_chunks)
            else:
                # Determine chunk type from boundary
                if boundary_type in ("class", "interface"):
                    ct = ChunkType.CLASS
                elif boundary_type in ("function", "fun", "method", "arrow_function"):
                    ct = ChunkType.FUNCTION
                else:
                    ct = chunk_type

                chunk_id = generate_chunk_id(chunk_content, source_file, start_idx + 1)
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        chunk_type=ct,
                        source_file=source_file,
                        start_line=start_idx + 1,
                        end_line=end_idx,
                        metadata={
                            "boundary_type": boundary_type,
                            "language": language,
                            **(metadata or {}),
                        },
                    )
                )

        return chunks

    def _split_large_chunk(
        self,
        lines: list[str],
        source_file: str,
        base_line: int,
        boundary_type: str,
        metadata: Optional[dict[str, Any]],
    ) -> list[Chunk]:
        """Split a large chunk into smaller pieces."""
        chunks = []
        current_lines = []
        current_size = 0
        chunk_start = 0

        for i, line in enumerate(lines):
            line_len = len(line) + 1

            if current_size + line_len > self.max_chunk_size and current_lines:
                chunk_content = "\n".join(current_lines)
                chunk_id = generate_chunk_id(
                    chunk_content, source_file, base_line + chunk_start
                )
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=chunk_content,
                        chunk_type=ChunkType.CODE,
                        source_file=source_file,
                        start_line=base_line + chunk_start,
                        end_line=base_line + chunk_start + len(current_lines) - 1,
                        metadata={
                            "boundary_type": boundary_type,
                            "split": True,
                            **(metadata or {}),
                        },
                    )
                )
                current_lines = []
                current_size = 0
                chunk_start = i

            current_lines.append(line)
            current_size += line_len

        # Handle remaining
        if current_lines:
            chunk_content = "\n".join(current_lines)
            chunk_id = generate_chunk_id(
                chunk_content, source_file, base_line + chunk_start
            )
            chunks.append(
                Chunk(
                    id=chunk_id,
                    content=chunk_content,
                    chunk_type=ChunkType.CODE,
                    source_file=source_file,
                    start_line=base_line + chunk_start,
                    end_line=base_line + len(lines) - 1,
                    metadata={
                        "boundary_type": boundary_type,
                        "split": True,
                        **(metadata or {}),
                    },
                )
            )

        return chunks


class MarkdownChunking(ChunkingStrategy):
    """Chunking strategy for Markdown documentation.

    Splits at headings and preserves document structure.
    """

    def __init__(
        self,
        max_chunk_size: int = 2000,
        min_heading_level: int = 2,
    ) -> None:
        """Initialize Markdown chunking.

        Args:
            max_chunk_size: Maximum chunk size.
            min_heading_level: Minimum heading level to split at.
        """
        self.max_chunk_size = max_chunk_size
        self.min_heading_level = min_heading_level

    @property
    def name(self) -> str:
        return "markdown"

    def _parse_headings(
        self, lines: list[str]
    ) -> list[tuple[int, int, str]]:
        """Parse heading positions.

        Returns list of (line_index, level, title) tuples.
        """
        headings = []
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$")

        for i, line in enumerate(lines):
            match = heading_pattern.match(line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                if level >= self.min_heading_level:
                    headings.append((i, level, title))

        return headings

    def chunk(
        self,
        content: str,
        source_file: str,
        chunk_type: ChunkType = ChunkType.DOCUMENTATION,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Split Markdown at headings."""
        if not content:
            return []

        lines = content.split("\n")
        total_lines = len(lines)

        headings = self._parse_headings(lines)

        if not headings:
            # No headings, use fixed-size
            fallback = FixedSizeChunking(chunk_size=self.max_chunk_size)
            return fallback.chunk(content, source_file, chunk_type, metadata)

        chunks = []

        # Handle content before first heading
        if headings[0][0] > 0:
            preamble = "\n".join(lines[: headings[0][0]])
            if preamble.strip():
                chunk_id = generate_chunk_id(preamble, source_file, 1)
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=preamble,
                        chunk_type=ChunkType.DOCUMENTATION,
                        source_file=source_file,
                        start_line=1,
                        end_line=headings[0][0],
                        metadata={"section": "preamble", **(metadata or {})},
                    )
                )

        # Process sections
        for i, (line_idx, level, title) in enumerate(headings):
            # Find end of section
            end_idx = total_lines
            if i + 1 < len(headings):
                end_idx = headings[i + 1][0]

            section_lines = lines[line_idx:end_idx]
            section_content = "\n".join(section_lines)

            if not section_content.strip():
                continue

            # Split if too large
            if len(section_content) > self.max_chunk_size:
                sub_strategy = FixedSizeChunking(
                    chunk_size=self.max_chunk_size,
                    overlap=50,
                )
                sub_chunks = sub_strategy.chunk(
                    section_content,
                    source_file,
                    ChunkType.DOCUMENTATION,
                    {"section": title, "level": level, **(metadata or {})},
                )
                # Adjust line numbers
                for sc in sub_chunks:
                    sc.start_line = line_idx + 1 + (sc.start_line - 1)
                    sc.end_line = line_idx + 1 + (sc.end_line - 1)
                chunks.extend(sub_chunks)
            else:
                chunk_id = generate_chunk_id(section_content, source_file, line_idx + 1)
                chunks.append(
                    Chunk(
                        id=chunk_id,
                        content=section_content,
                        chunk_type=ChunkType.DOCUMENTATION,
                        source_file=source_file,
                        start_line=line_idx + 1,
                        end_line=end_idx,
                        metadata={
                            "section": title,
                            "level": level,
                            **(metadata or {}),
                        },
                    )
                )

        return chunks


class ChunkingService:
    """Service for managing content chunking.

    Provides a unified interface for different chunking strategies.
    """

    STRATEGIES = {
        "fixed_size": FixedSizeChunking,
        "token_based": TokenBasedChunking,
        "semantic": SemanticChunking,
        "markdown": MarkdownChunking,
    }

    def __init__(
        self,
        default_strategy: str = "semantic",
        **strategy_kwargs: Any,
    ) -> None:
        """Initialize the chunking service.

        Args:
            default_strategy: Default strategy name.
            strategy_kwargs: Keyword arguments for strategy.
        """
        self.default_strategy_name = default_strategy
        self.strategy_kwargs = strategy_kwargs
        self._strategies: dict[str, ChunkingStrategy] = {}

    def get_strategy(self, name: Optional[str] = None) -> ChunkingStrategy:
        """Get a chunking strategy by name.

        Args:
            name: Strategy name (uses default if None).

        Returns:
            ChunkingStrategy instance.
        """
        name = name or self.default_strategy_name

        if name not in self._strategies:
            if name not in self.STRATEGIES:
                raise ValueError(f"Unknown chunking strategy: {name}")

            strategy_class = self.STRATEGIES[name]
            self._strategies[name] = strategy_class(**self.strategy_kwargs)

        return self._strategies[name]

    def chunk(
        self,
        content: str,
        source_file: str,
        strategy: Optional[str] = None,
        chunk_type: Optional[ChunkType] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Chunk content using specified strategy.

        Args:
            content: Content to chunk.
            source_file: Source file path.
            strategy: Strategy name (auto-detect if None).
            chunk_type: Content type.
            metadata: Additional metadata.

        Returns:
            List of chunks.
        """
        # Auto-detect strategy based on file extension
        if strategy is None:
            if source_file.endswith(".md"):
                strategy = "markdown"
            elif any(
                source_file.endswith(ext)
                for ext in [".py", ".js", ".ts", ".java", ".kt", ".go"]
            ):
                strategy = "semantic"
            else:
                strategy = self.default_strategy_name

        # Auto-detect chunk type
        if chunk_type is None:
            if source_file.endswith(".md"):
                chunk_type = ChunkType.DOCUMENTATION
            else:
                chunk_type = ChunkType.CODE

        chunking_strategy = self.get_strategy(strategy)
        return chunking_strategy.chunk(content, source_file, chunk_type, metadata)

    def chunk_code(
        self,
        content: str,
        source_file: str,
        language: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Chunk code with semantic awareness.

        Args:
            content: Code content.
            source_file: Source file path.
            language: Programming language.
            metadata: Additional metadata.

        Returns:
            List of code chunks.
        """
        strategy = SemanticChunking(language=language, **self.strategy_kwargs)
        return strategy.chunk(content, source_file, ChunkType.CODE, metadata)

    def chunk_documentation(
        self,
        content: str,
        source_file: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Chunk documentation (Markdown).

        Args:
            content: Documentation content.
            source_file: Source file path.
            metadata: Additional metadata.

        Returns:
            List of documentation chunks.
        """
        strategy = MarkdownChunking(**self.strategy_kwargs)
        return strategy.chunk(content, source_file, ChunkType.DOCUMENTATION, metadata)

    def chunk_for_embedding(
        self,
        content: str,
        source_file: str,
        max_tokens: int = 500,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Chunk content optimized for embedding.

        Uses smaller chunks with overlap for better retrieval.

        Args:
            content: Content to chunk.
            source_file: Source file path.
            max_tokens: Maximum tokens per chunk.
            metadata: Additional metadata.

        Returns:
            List of chunks optimized for embedding.
        """
        strategy = TokenBasedChunking(
            max_tokens=max_tokens,
            overlap_tokens=50,
            min_tokens=20,
        )

        chunk_type = (
            ChunkType.DOCUMENTATION
            if source_file.endswith(".md")
            else ChunkType.CODE
        )

        return strategy.chunk(content, source_file, chunk_type, metadata)

    def chunk_for_context(
        self,
        content: str,
        source_file: str,
        max_tokens: int = 2000,
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[Chunk]:
        """Chunk content for LLM context.

        Uses larger chunks to preserve context.

        Args:
            content: Content to chunk.
            source_file: Source file path.
            max_tokens: Maximum tokens per chunk.
            metadata: Additional metadata.

        Returns:
            List of chunks for LLM context.
        """
        strategy = TokenBasedChunking(
            max_tokens=max_tokens,
            overlap_tokens=100,
            min_tokens=100,
        )

        chunk_type = (
            ChunkType.DOCUMENTATION
            if source_file.endswith(".md")
            else ChunkType.CODE
        )

        return strategy.chunk(content, source_file, chunk_type, metadata)

    def get_available_strategies(self) -> list[str]:
        """Get list of available strategy names.

        Returns:
            List of strategy names.
        """
        return list(self.STRATEGIES.keys())
