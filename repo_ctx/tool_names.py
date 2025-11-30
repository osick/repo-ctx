"""Tool naming conventions and backwards compatibility.

This module defines the canonical tool names and provides backwards
compatibility for deprecated names during the transition period.

Tool Naming Convention:
- repo-ctx-<action>[-<target>]
- Actions: search, find, index, list, analyze, docs, llmstxt
- 'search' = fuzzy search (default, user-friendly)
- 'find' = exact match (precise, developer-focused)
"""

import warnings
from typing import Optional

# Canonical tool names (new naming scheme)
CANONICAL_TOOLS = {
    # Discovery
    "repo-ctx-search": "Fuzzy search for repositories (default search behavior)",
    "repo-ctx-find-repo": "Find repository by exact name match",
    "repo-ctx-list": "List all indexed repositories",

    # Indexing
    "repo-ctx-index": "Index a single repository",
    "repo-ctx-index-group": "Index all repositories in a group/organization",

    # Documentation
    "repo-ctx-docs": "Get repository documentation",
    "repo-ctx-llmstxt": "Generate compact llms.txt summary",

    # Code Analysis
    "repo-ctx-analyze": "Analyze code and extract symbols",
    "repo-ctx-find-symbol": "Find symbols by name pattern",
    "repo-ctx-symbol-detail": "Get detailed information about a symbol",
    "repo-ctx-file-symbols": "List all symbols in a file",
    "repo-ctx-dependency-graph": "Generate dependency graph",

    # Configuration
    "repo-ctx-config": "Get/set configuration",
}

# Mapping from deprecated names to canonical names
TOOL_ALIASES = {
    # Old name -> New canonical name
    "repo-ctx-fuzzy-search": "repo-ctx-search",
    "repo-ctx-search-symbol": "repo-ctx-find-symbol",
    "repo-ctx-get-symbol-detail": "repo-ctx-symbol-detail",
    "repo-ctx-get-file-symbols": "repo-ctx-file-symbols",

    # Note: old "repo-ctx-search" (exact) is now "repo-ctx-find-repo"
    # This is a special case handled separately since we're swapping meanings
}

# Special case: the old "repo-ctx-search" tool becomes "repo-ctx-find-repo"
# We need to track this separately to avoid confusion
OLD_EXACT_SEARCH_NAME = "repo-ctx-search"  # This was exact match
NEW_EXACT_SEARCH_NAME = "repo-ctx-find-repo"  # New name for exact match
NEW_FUZZY_SEARCH_NAME = "repo-ctx-search"  # Now means fuzzy search


def get_canonical_name(tool_name: str) -> str:
    """Get the canonical (new) name for a tool.

    Args:
        tool_name: The tool name (can be old or new)

    Returns:
        The canonical tool name
    """
    # Check if it's already canonical
    if tool_name in CANONICAL_TOOLS:
        return tool_name

    # Check aliases
    if tool_name in TOOL_ALIASES:
        return TOOL_ALIASES[tool_name]

    # Unknown tool
    return tool_name


def is_deprecated_name(tool_name: str) -> bool:
    """Check if a tool name is deprecated.

    Args:
        tool_name: The tool name to check

    Returns:
        True if the name is deprecated
    """
    return tool_name in TOOL_ALIASES


def get_deprecation_message(old_name: str) -> str:
    """Get the deprecation warning message for an old tool name.

    Args:
        old_name: The deprecated tool name

    Returns:
        A warning message explaining the deprecation
    """
    new_name = TOOL_ALIASES.get(old_name, old_name)
    return (
        f"Tool '{old_name}' is deprecated and will be removed in a future version. "
        f"Please use '{new_name}' instead."
    )


def warn_if_deprecated(tool_name: str) -> Optional[str]:
    """Emit a deprecation warning if the tool name is deprecated.

    Args:
        tool_name: The tool name being used

    Returns:
        The deprecation message if deprecated, None otherwise
    """
    if is_deprecated_name(tool_name):
        message = get_deprecation_message(tool_name)
        warnings.warn(message, DeprecationWarning, stacklevel=3)
        return message
    return None


# CLI command to MCP tool mapping
CLI_TO_MCP_MAPPING = {
    # repo commands
    ("repo", "search"): "repo-ctx-search",
    ("repo", "find-exact"): "repo-ctx-find-repo",
    ("repo", "index"): "repo-ctx-index",
    ("repo", "index-group"): "repo-ctx-index-group",
    ("repo", "list"): "repo-ctx-list",
    ("repo", "docs"): "repo-ctx-docs",
    ("repo", "llmstxt"): "repo-ctx-llmstxt",

    # code commands
    ("code", "analyze"): "repo-ctx-analyze",
    ("code", "find"): "repo-ctx-find-symbol",
    ("code", "info"): "repo-ctx-symbol-detail",
    ("code", "symbols"): "repo-ctx-file-symbols",
    ("code", "dep"): "repo-ctx-dependency-graph",

    # config commands
    ("config", "show"): "repo-ctx-config",
}

# MCP tool to CLI command mapping (reverse)
MCP_TO_CLI_MAPPING = {v: k for k, v in CLI_TO_MCP_MAPPING.items()}


def get_mcp_tool_for_cli(command: str, subcommand: str) -> Optional[str]:
    """Get the MCP tool name for a CLI command.

    Args:
        command: The CLI command (repo, code, config)
        subcommand: The subcommand (search, analyze, etc.)

    Returns:
        The corresponding MCP tool name, or None if not found
    """
    return CLI_TO_MCP_MAPPING.get((command, subcommand))


def get_cli_for_mcp_tool(tool_name: str) -> Optional[tuple]:
    """Get the CLI command for an MCP tool.

    Args:
        tool_name: The MCP tool name

    Returns:
        A tuple of (command, subcommand) or None if not found
    """
    canonical = get_canonical_name(tool_name)
    return MCP_TO_CLI_MAPPING.get(canonical)
