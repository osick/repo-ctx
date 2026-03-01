"""Data models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Union


class ProviderType(Enum):
    """Git provider types.

    Supported providers for repository access:
    - GITHUB: GitHub repositories
    - GITLAB: GitLab repositories
    - LOCAL: Local filesystem repositories
    - AUTO: Auto-detect from path format
    """
    GITHUB = "github"
    GITLAB = "gitlab"
    LOCAL = "local"
    AUTO = "auto"

    @classmethod
    def from_string(cls, value: str) -> "ProviderType":
        """Create ProviderType from string value."""
        if not value:
            return cls.AUTO
        normalized = value.lower().strip()
        for provider in cls:
            if provider.value == normalized:
                return provider
        raise ValueError(f"Invalid provider type: {value}. Valid types: {[p.value for p in cls]}")


class SymbolType(Enum):
    """Code symbol types.

    Types of symbols that can be extracted from source code.
    """
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    INTERFACE = "interface"
    ENUM = "enum"
    VARIABLE = "variable"
    CONSTANT = "constant"
    MODULE = "module"
    PROPERTY = "property"
    TYPE_ALIAS = "type_alias"
    NAMESPACE = "namespace"

    @classmethod
    def from_string(cls, value: str) -> "SymbolType":
        """Create SymbolType from string value."""
        if not value:
            raise ValueError("Symbol type cannot be empty")
        normalized = value.lower().strip()
        for symbol_type in cls:
            if symbol_type.value == normalized:
                return symbol_type
        raise ValueError(f"Invalid symbol type: {value}. Valid types: {[s.value for s in cls]}")


class ChunkType(Enum):
    """Types of content chunks for GenAI processing.

    - CODE: Source code chunks
    - DOCUMENTATION: Documentation/text chunks
    - MIXED: Chunks containing both code and documentation
    """
    CODE = "code"
    DOCUMENTATION = "documentation"
    MIXED = "mixed"

    @classmethod
    def from_string(cls, value: str) -> "ChunkType":
        """Create ChunkType from string value."""
        if not value:
            return cls.MIXED
        normalized = value.lower().strip()
        for chunk_type in cls:
            if chunk_type.value == normalized:
                return chunk_type
        raise ValueError(f"Invalid chunk type: {value}. Valid types: {[c.value for c in cls]}")


class OutputMode(Enum):
    """Output mode for documentation retrieval.

    - SUMMARY: Titles, descriptions, and key methods only (~500-2000 tokens)
              Optimized for LLM context efficiency
    - STANDARD: Current behavior with quality-based truncation
               Good balance of detail and size
    - FULL: Everything including tests and low-quality docs
            Complete documentation dump
    """
    SUMMARY = "summary"
    STANDARD = "standard"
    FULL = "full"

    @classmethod
    def from_string(cls, value: str) -> "OutputMode":
        """Create OutputMode from string value."""
        if not value:
            return cls.STANDARD
        normalized = value.lower().strip()
        for mode in cls:
            if mode.value == normalized:
                return mode
        raise ValueError(f"Invalid output mode: {value}. Valid modes: {[m.value for m in cls]}")


@dataclass
class Library:
    group_name: str
    project_name: str
    description: str
    default_version: str
    provider: str = "github"  # Provider type: github, gitlab, local
    id: Optional[int] = None
    last_indexed: Optional[datetime] = None


@dataclass
class Version:
    library_id: int
    version_tag: str
    commit_sha: str
    id: Optional[int] = None


@dataclass
class Document:
    """A document in the repository.

    Attributes:
        version_id: ID of the version this document belongs to.
        file_path: Path to the document file.
        content: Document content.
        content_type: Type of content (markdown, rst, txt).
        tokens: Estimated token count.
        quality_score: Quality score for ranking (0.0-1.0).
        classification: GenAI classification (tutorial, api, guide, etc.).
        metadata: Additional metadata as key-value pairs.
        id: Database ID (None until saved).
    """
    version_id: int
    file_path: str
    content: str
    content_type: str = "markdown"
    tokens: int = 0
    quality_score: float = 0.5
    classification: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    id: Optional[int] = None


@dataclass
class SearchResult:
    library_id: str  # /group/project
    name: str
    description: str
    versions: list[str]
    score: float = 0.0


@dataclass
class FuzzySearchResult:
    library_id: str  # /group/project
    name: str
    group: str
    description: str
    score: float
    match_type: str
    matched_field: str


@dataclass
class Symbol:
    """A code symbol (function, class, method, etc.).

    Attributes:
        library_id: ID of the library this symbol belongs to.
        name: Symbol name.
        qualified_name: Fully qualified name (e.g., module.class.method).
        symbol_type: Type of symbol (function, class, etc.).
        file_path: Path to the source file.
        line_start: Starting line number.
        line_end: Ending line number.
        signature: Function/method signature or class declaration.
        documentation: Docstring or documentation.
        visibility: Visibility (public, private, protected).
        language: Programming language.
        parent_symbol: Parent symbol's qualified name (for methods in classes).
        metadata: Additional metadata.
        id: Database ID (None until saved).
    """
    library_id: int
    name: str
    qualified_name: str
    symbol_type: Union[SymbolType, str]
    file_path: str
    line_start: int
    line_end: int
    signature: Optional[str] = None
    documentation: Optional[str] = None
    visibility: Optional[str] = None
    language: Optional[str] = None
    parent_symbol: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    id: Optional[int] = None


@dataclass
class Chunk:
    """A content chunk for GenAI processing.

    Chunks are segments of documents or code used for embedding
    and semantic search.

    Attributes:
        content: The chunk content.
        chunk_type: Type of chunk (code, documentation, mixed).
        document_id: Source document ID (if from document).
        symbol_id: Source symbol ID (if from symbol).
        start_line: Starting line number.
        end_line: Ending line number.
        tokens: Token count.
        embedding_id: Reference to vector DB embedding.
        metadata: Additional metadata.
        id: Database ID (None until saved).
    """
    content: str
    chunk_type: Union[ChunkType, str]
    document_id: Optional[int] = None
    symbol_id: Optional[int] = None
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    tokens: Optional[int] = None
    embedding_id: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    id: Optional[int] = None


@dataclass
class Classification:
    """A GenAI classification result.

    Caches LLM classification results for documents, symbols, or chunks.

    Attributes:
        entity_type: Type of entity (document, symbol, chunk).
        entity_id: ID of the classified entity.
        classification: Assigned classification category.
        confidence: Confidence score (0.0-1.0).
        model: Model used for classification.
        created_at: Timestamp when classification was created.
        id: Database ID (None until saved).
    """
    entity_type: str
    entity_id: int
    classification: str
    confidence: Optional[float] = None
    model: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    id: Optional[int] = None


@dataclass
class Dependency:
    """A dependency relationship between code elements.

    Represents relationships like imports, inheritance, function calls.

    Attributes:
        library_id: ID of the library this dependency belongs to.
        source_name: Name of the source symbol/module.
        target_name: Name of the target symbol/module.
        dependency_type: Type of dependency (imports, extends, implements, calls).
        source_file: Source file path.
        target_file: Target file path.
        id: Database ID (None until saved).
    """
    library_id: int
    source_name: str
    target_name: str
    dependency_type: str
    source_file: Optional[str] = None
    target_file: Optional[str] = None
    id: Optional[int] = None
