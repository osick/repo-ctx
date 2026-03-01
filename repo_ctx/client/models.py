"""Data models for the repo-ctx client.

These models provide a clean, typed interface for client operations,
abstracting away the differences between direct and HTTP modes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class SymbolType(Enum):
    """Types of code symbols."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    INTERFACE = "interface"
    ENUM = "enum"
    VARIABLE = "variable"
    CONSTANT = "constant"
    TYPE = "type"
    MODULE = "module"
    NAMESPACE = "namespace"


class Visibility(Enum):
    """Symbol visibility."""

    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    INTERNAL = "internal"


@dataclass
class Library:
    """Repository/library information.

    Attributes:
        id: Unique identifier (format: /owner/repo).
        name: Repository name.
        group: Owner/organization.
        provider: Provider type (github, gitlab, local).
        description: Repository description.
        versions: Available versions.
        last_indexed: Last indexing timestamp.
        metadata: Additional metadata.
    """

    id: str
    name: str
    group: str
    provider: str = "github"
    description: str = ""
    versions: list[str] = field(default_factory=list)
    last_indexed: Optional[datetime] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Library":
        """Create from dictionary."""
        last_indexed = data.get("last_indexed")
        if isinstance(last_indexed, str):
            last_indexed = datetime.fromisoformat(last_indexed)

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            group=data.get("group", ""),
            provider=data.get("provider", "github"),
            description=data.get("description", ""),
            versions=data.get("versions", []),
            last_indexed=last_indexed,
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "group": self.group,
            "provider": self.provider,
            "description": self.description,
            "versions": self.versions,
            "last_indexed": self.last_indexed.isoformat() if self.last_indexed else None,
            "metadata": self.metadata,
        }


@dataclass
class Document:
    """Documentation content.

    Attributes:
        id: Document identifier.
        path: File path.
        title: Document title.
        content: Document content.
        library_id: Parent library ID.
        doc_type: Document type (readme, api, guide, etc.).
        metadata: Additional metadata.
    """

    id: str
    path: str
    title: str
    content: str
    library_id: str = ""
    doc_type: str = "documentation"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            path=data.get("path", ""),
            title=data.get("title", ""),
            content=data.get("content", ""),
            library_id=data.get("library_id", ""),
            doc_type=data.get("doc_type", "documentation"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "path": self.path,
            "title": self.title,
            "content": self.content,
            "library_id": self.library_id,
            "doc_type": self.doc_type,
            "metadata": self.metadata,
        }


@dataclass
class Symbol:
    """Code symbol information.

    Attributes:
        name: Symbol name.
        qualified_name: Fully qualified name.
        symbol_type: Type of symbol.
        file_path: File containing the symbol.
        line_start: Starting line number.
        line_end: Ending line number.
        signature: Function/method signature.
        visibility: Symbol visibility.
        documentation: Docstring or comments.
        language: Programming language.
        metadata: Additional metadata.
    """

    name: str
    qualified_name: str
    symbol_type: SymbolType
    file_path: str
    line_start: int = 0
    line_end: int = 0
    signature: Optional[str] = None
    visibility: Visibility = Visibility.PUBLIC
    documentation: Optional[str] = None
    language: str = "python"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Symbol":
        """Create from dictionary."""
        symbol_type = data.get("symbol_type", "function")
        if isinstance(symbol_type, str):
            try:
                symbol_type = SymbolType(symbol_type)
            except ValueError:
                symbol_type = SymbolType.FUNCTION

        visibility = data.get("visibility", "public")
        if isinstance(visibility, str):
            try:
                visibility = Visibility(visibility)
            except ValueError:
                visibility = Visibility.PUBLIC

        return cls(
            name=data.get("name", ""),
            qualified_name=data.get("qualified_name", data.get("name", "")),
            symbol_type=symbol_type,
            file_path=data.get("file_path", ""),
            line_start=data.get("line_start", 0),
            line_end=data.get("line_end", 0),
            signature=data.get("signature"),
            visibility=visibility,
            documentation=data.get("documentation"),
            language=data.get("language", "python"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "qualified_name": self.qualified_name,
            "symbol_type": self.symbol_type.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "signature": self.signature,
            "visibility": self.visibility.value,
            "documentation": self.documentation,
            "language": self.language,
            "metadata": self.metadata,
        }


@dataclass
class SearchResult:
    """Search result item.

    Attributes:
        id: Result identifier.
        name: Result name.
        result_type: Type of result (library, document, symbol).
        score: Relevance score (0-1).
        snippet: Content snippet.
        metadata: Additional metadata.
    """

    id: str
    name: str
    result_type: str
    score: float = 1.0
    snippet: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SearchResult":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            result_type=data.get("result_type", "library"),
            score=data.get("score", 1.0),
            snippet=data.get("snippet", ""),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "result_type": self.result_type,
            "score": self.score,
            "snippet": self.snippet,
            "metadata": self.metadata,
        }


@dataclass
class IndexResult:
    """Result of an indexing operation.

    Attributes:
        status: Status (success, failed, skipped).
        repository: Repository identifier.
        documents: Number of documents indexed.
        symbols: Number of symbols extracted.
        duration_ms: Indexing duration in milliseconds.
        error: Error message if failed.
        metadata: Additional metadata.
    """

    status: str
    repository: str
    documents: int = 0
    symbols: int = 0
    duration_ms: int = 0
    error: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndexResult":
        """Create from dictionary."""
        return cls(
            status=data.get("status", "unknown"),
            repository=data.get("repository", ""),
            documents=data.get("documents", 0),
            symbols=data.get("symbols", 0),
            duration_ms=data.get("duration_ms", 0),
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status,
            "repository": self.repository,
            "documents": self.documents,
            "symbols": self.symbols,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class AnalysisResult:
    """Result of code analysis.

    Attributes:
        file_path: Analyzed file path.
        language: Detected language.
        symbols: Extracted symbols.
        dependencies: Detected dependencies.
        metrics: Code metrics.
        errors: Analysis errors.
    """

    file_path: str
    language: str
    symbols: list[Symbol] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisResult":
        """Create from dictionary."""
        symbols = [
            Symbol.from_dict(s) if isinstance(s, dict) else s
            for s in data.get("symbols", [])
        ]
        return cls(
            file_path=data.get("file_path", ""),
            language=data.get("language", ""),
            symbols=symbols,
            dependencies=data.get("dependencies", []),
            metrics=data.get("metrics", {}),
            errors=data.get("errors", []),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "language": self.language,
            "symbols": [s.to_dict() for s in self.symbols],
            "dependencies": self.dependencies,
            "metrics": self.metrics,
            "errors": self.errors,
        }
