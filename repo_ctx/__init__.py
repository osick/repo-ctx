"""GitLab Context - MCP server for GitLab repository documentation."""

__version__ = "0.3.1"

# Core classes
from .core import GitLabContext, RepositoryContext
from .config import Config
from .storage import Storage

# Code analysis
from .analysis import (
    CodeAnalyzer,
    Symbol,
    SymbolType,
    Dependency,
    PythonExtractor,
    JavaScriptExtractor,
    JavaExtractor,
    KotlinExtractor,
)

# Models
from .models import Library, Document

__all__ = [
    # Version
    "__version__",
    # Core
    "GitLabContext",
    "RepositoryContext",
    "Config",
    "Storage",
    # Code analysis
    "CodeAnalyzer",
    "Symbol",
    "SymbolType",
    "Dependency",
    "PythonExtractor",
    "JavaScriptExtractor",
    "JavaExtractor",
    "KotlinExtractor",
    # Models
    "Library",
    "Document",
]
