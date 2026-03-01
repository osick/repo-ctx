"""Data models for code analysis."""
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


class SymbolType(str, Enum):
    """Symbol types."""
    FUNCTION = "function"
    METHOD = "method"
    CLASS = "class"
    VARIABLE = "variable"
    MODULE = "module"
    INTERFACE = "interface"
    ENUM = "enum"
    CONSTANT = "constant"


class DocQuality(str, Enum):
    """Documentation quality assessment."""
    SUFFICIENT = "sufficient"  # Existing docs explain purpose, params, return
    ENHANCED = "enhanced"  # LLM added explanation to insufficient docs
    MISSING = "missing"  # No documentation found


@dataclass
class Symbol:
    """Represents a code symbol (function, class, variable, etc.)."""

    name: str
    symbol_type: SymbolType
    file_path: str
    line_start: int
    line_end: Optional[int] = None
    column_start: Optional[int] = None
    signature: Optional[str] = None
    visibility: str = "public"  # public, private, protected, internal
    language: str = "unknown"
    documentation: Optional[str] = None
    qualified_name: Optional[str] = None
    is_exported: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    # LLM-enhanced documentation fields
    explanation: Optional[str] = None  # LLM-generated explanation
    doc_quality: Optional[DocQuality] = None  # Quality assessment

    def __post_init__(self):
        """Set defaults after initialization."""
        if self.qualified_name is None:
            self.qualified_name = self.name


@dataclass
class Dependency:
    """Represents a dependency between code elements."""

    source: str  # Source symbol name
    target: str  # Target symbol name
    dependency_type: str  # import, call, inherit, compose
    file_path: str
    line: Optional[int] = None
    is_external: bool = False
    external_module: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallEdge:
    """Represents a function call edge in call graph."""

    caller: str
    callee: str
    file_path: str
    line: int
    metadata: Dict[str, Any] = field(default_factory=dict)
