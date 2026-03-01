"""Parameter naming conventions and normalization.

This module provides parameter name normalization to support both
old (camelCase) and new (snake_case) parameter names with backwards
compatibility.

Standard Parameter Names:
- repository: Repository identifier (was: libraryId, repoId, id)
- language: Language filter (was: lang)
- symbol_type: Symbol type filter (was: symbolType, type)
- output_format: Output format (was: outputFormat)
- include_subgroups: Include subgroups flag (was: includeSubgroups)
- max_tokens: Maximum tokens (was: maxTokens)
- group_by_type: Group by type flag (was: groupByType)
- include_api: Include API flag (was: includeApi)
- include_quickstart: Include quickstart flag (was: includeQuickstart)
"""

import warnings
from typing import Any, Dict, Optional

# Mapping from old parameter names to canonical names
PARAMETER_ALIASES = {
    # Repository identifier
    "libraryId": "repository",
    "repoId": "repository",
    "library_id": "repository",
    "repo_id": "repository",

    # Language
    "lang": "language",

    # Symbol type
    "symbolType": "symbol_type",
    "type": "symbol_type",  # Only in symbol context

    # Output format
    "outputFormat": "output_format",

    # Boolean flags
    "includeSubgroups": "include_subgroups",
    "maxTokens": "max_tokens",
    "groupByType": "group_by_type",
    "includeApi": "include_api",
    "includeQuickstart": "include_quickstart",
    "includePrivate": "include_private",
    "includeMetadata": "include_metadata",

    # File path variations
    "filePath": "file_path",
    "symbolName": "symbol_name",
    "libraryName": "library_name",
    "graphType": "graph_type",
}

# Canonical parameter names
CANONICAL_PARAMETERS = {
    "repository",
    "language",
    "symbol_type",
    "output_format",
    "include_subgroups",
    "max_tokens",
    "group_by_type",
    "include_api",
    "include_quickstart",
    "include_private",
    "include_metadata",
    "file_path",
    "symbol_name",
    "library_name",
    "graph_type",
    "query",
    "path",
    "topic",
    "page",
    "depth",
    "limit",
    "refresh",
    "include",
    "provider",
    "group",
}


def get_canonical_parameter(param_name: str) -> str:
    """Get the canonical name for a parameter.

    Args:
        param_name: The parameter name (can be old or new)

    Returns:
        The canonical parameter name
    """
    if param_name in CANONICAL_PARAMETERS:
        return param_name
    return PARAMETER_ALIASES.get(param_name, param_name)


def is_deprecated_parameter(param_name: str) -> bool:
    """Check if a parameter name is deprecated.

    Args:
        param_name: The parameter name to check

    Returns:
        True if the name is deprecated
    """
    return param_name in PARAMETER_ALIASES


def normalize_arguments(arguments: Dict[str, Any], warn: bool = True) -> Dict[str, Any]:
    """Normalize argument names to canonical form.

    Converts old-style parameter names to canonical names while
    preserving values. Optionally emits deprecation warnings.

    Args:
        arguments: Dictionary of arguments with potentially mixed naming
        warn: Whether to emit deprecation warnings

    Returns:
        Dictionary with normalized parameter names
    """
    normalized = {}
    deprecated_used = []

    for key, value in arguments.items():
        canonical = get_canonical_parameter(key)
        if canonical != key and warn:
            deprecated_used.append((key, canonical))
        normalized[canonical] = value

    if deprecated_used and warn:
        for old, new in deprecated_used:
            warnings.warn(
                f"Parameter '{old}' is deprecated, use '{new}' instead.",
                DeprecationWarning,
                stacklevel=3
            )

    return normalized


def get_repository_id(arguments: Dict[str, Any]) -> Optional[str]:
    """Extract repository ID from arguments, checking all variants.

    Args:
        arguments: Dictionary of arguments

    Returns:
        The repository ID if found, None otherwise
    """
    # Check in order of preference
    for key in ["repository", "libraryId", "repoId", "library_id", "repo_id", "id"]:
        if key in arguments and arguments[key]:
            return arguments[key]
    return None


def get_language(arguments: Dict[str, Any]) -> Optional[str]:
    """Extract language from arguments, checking all variants.

    Args:
        arguments: Dictionary of arguments

    Returns:
        The language if found, None otherwise
    """
    for key in ["language", "lang"]:
        if key in arguments and arguments[key]:
            return arguments[key]
    return None


def get_symbol_type(arguments: Dict[str, Any]) -> Optional[str]:
    """Extract symbol type from arguments, checking all variants.

    Args:
        arguments: Dictionary of arguments

    Returns:
        The symbol type if found, None otherwise
    """
    for key in ["symbol_type", "symbolType", "type"]:
        if key in arguments and arguments[key]:
            return arguments[key]
    return None


def get_output_format(arguments: Dict[str, Any], default: str = "text") -> str:
    """Extract output format from arguments, checking all variants.

    Args:
        arguments: Dictionary of arguments
        default: Default format if not specified

    Returns:
        The output format
    """
    for key in ["output_format", "outputFormat", "format"]:
        if key in arguments and arguments[key]:
            return arguments[key]
    return default
