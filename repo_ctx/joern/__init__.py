"""
Joern Code Property Graph (CPG) integration for repo-ctx.

This module provides integration with Joern for advanced code analysis
including support for 12+ programming languages and CPGQL queries.

Usage:
    from repo_ctx.joern import JoernAdapter

    adapter = JoernAdapter()
    if adapter.is_available():
        result = adapter.analyze_directory("/path/to/code")
        symbols = result.symbols
"""

from repo_ctx.joern.adapter import JoernAdapter
from repo_ctx.joern.cli import JoernCLI, JoernError, JoernNotFoundError
from repo_ctx.joern.parser import CPGParser
from repo_ctx.joern.mapper import CPGMapper
from repo_ctx.joern.queries import (
    QUERY_ALL_METHODS,
    QUERY_ALL_TYPES,
    QUERY_CALL_GRAPH,
    QUERY_INHERITANCE,
    QUERY_COMPLEXITY,
    QUERY_PARAMETERS,
    # LLM-friendly queries
    QUERY_LLM_METHODS,
    QUERY_LLM_TYPES,
    QUERY_LLM_CALLS,
    QUERY_LLM_MEMBERS,
    QUERY_LLM_SUMMARY,
)
from repo_ctx.joern.formatter import CPGFormatter, format_simple_list

from repo_ctx.joern.languages import (
    JOERN_LANGUAGES,
    get_language_for_file,
    get_supported_extensions,
    get_joern_frontend,
    get_language_maturity,
    requires_directory,
)

__all__ = [
    # Main adapter
    "JoernAdapter",
    # CLI wrapper
    "JoernCLI",
    "JoernError",
    "JoernNotFoundError",
    # Parser and mapper
    "CPGParser",
    "CPGMapper",
    # Built-in queries
    "QUERY_ALL_METHODS",
    "QUERY_ALL_TYPES",
    "QUERY_CALL_GRAPH",
    "QUERY_INHERITANCE",
    "QUERY_COMPLEXITY",
    "QUERY_PARAMETERS",
    # LLM-friendly queries
    "QUERY_LLM_METHODS",
    "QUERY_LLM_TYPES",
    "QUERY_LLM_CALLS",
    "QUERY_LLM_MEMBERS",
    "QUERY_LLM_SUMMARY",
    # Formatter
    "CPGFormatter",
    "format_simple_list",
    # Language utilities
    "JOERN_LANGUAGES",
    "get_language_for_file",
    "get_supported_extensions",
    "get_joern_frontend",
    "get_language_maturity",
    "requires_directory",
]
