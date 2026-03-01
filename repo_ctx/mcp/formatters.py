"""MCP response formatters.

This module provides formatting utilities for MCP tool responses,
converting internal data structures to human-readable text or JSON.
"""

import json
from typing import Any, Optional


def format_search_results(
    results: list[Any],
    query: str,
) -> str:
    """Format search results for MCP output.

    Args:
        results: List of search result objects.
        query: The search query used.

    Returns:
        Formatted string for MCP response.
    """
    output = []
    output.append(f"Search results for '{query}':\n\n")

    for i, result in enumerate(results, 1):
        library_id = getattr(result, 'library_id', 'unknown')
        name = getattr(result, 'name', 'unknown')
        group = getattr(result, 'group', 'unknown')
        description = getattr(result, 'description', '')
        match_type = getattr(result, 'match_type', 'unknown')
        matched_field = getattr(result, 'matched_field', 'unknown')
        score = getattr(result, 'score', 0.0)

        output.append(f"{i}. {library_id}\n")
        output.append(f"   Name: {name}\n")
        output.append(f"   Group: {group}\n")
        output.append(f"   Description: {description}\n")
        output.append(f"   Match: {match_type} in {matched_field} (score: {score:.2f})\n")
        output.append("\n")

    if not results:
        output.append(f"No repositories found matching '{query}'.\n")
        output.append(
            "Try a different search term or index repositories first using "
            "repo-ctx-index or repo-ctx-index-group.\n"
        )
    else:
        output.append(
            "\nTo get documentation, use repo-ctx-docs with one of the "
            "Repository IDs above.\n"
        )

    return "".join(output)


def format_repository_list(
    repositories: list[Any],
    provider_filter: Optional[str] = None,
) -> str:
    """Format repository list for MCP output.

    Args:
        repositories: List of Library objects.
        provider_filter: Optional provider filter used.

    Returns:
        Formatted string for MCP response.
    """
    output = []

    if provider_filter:
        output.append(f"Indexed repositories ({provider_filter} provider):\n\n")
    else:
        output.append("Indexed repositories:\n\n")

    for repo in repositories:
        group = getattr(repo, 'group_name', 'unknown')
        project = getattr(repo, 'project_name', 'unknown')
        description = getattr(repo, 'description', '')

        output.append(f"- /{group}/{project}\n")
        if description:
            output.append(f"  {description}\n")
        output.append("\n")

    if not repositories:
        output.append("No repositories indexed yet.\n")
        output.append(
            "Use repo-ctx-index to index a repository.\n"
        )

    output.append(f"\nTotal: {len(repositories)} repositories\n")

    return "".join(output)


def format_analysis_results(
    analysis: dict[str, Any],
    output_format: str = "text",
) -> str:
    """Format analysis results for MCP output.

    Args:
        analysis: Analysis result dictionary.
        output_format: Output format ('text', 'json', 'yaml').

    Returns:
        Formatted string for MCP response.
    """
    if output_format == "json":
        return json.dumps(analysis, indent=2)

    if output_format == "yaml":
        import yaml
        return yaml.dump(analysis, default_flow_style=False)

    # Text format
    output = []
    file_path = analysis.get("file_path", "unknown")
    language = analysis.get("language", "unknown")
    symbols = analysis.get("symbols", [])
    dependencies = analysis.get("dependencies", [])

    output.append(f"Analysis Results for {file_path}\n")
    output.append(f"Language: {language}\n")
    output.append(f"Symbols: {len(symbols)}\n")
    output.append(f"Dependencies: {len(dependencies)}\n")
    output.append("\n")

    if symbols:
        output.append("Symbols:\n")
        for sym in symbols:
            name = sym.get("name", "unknown")
            sym_type = sym.get("symbol_type", "unknown")
            line_start = sym.get("line_start", 0)
            signature = sym.get("signature", "")

            if signature:
                output.append(f"  {sym_type} {name}: {signature} (line {line_start})\n")
            else:
                output.append(f"  {sym_type} {name} (line {line_start})\n")

    return "".join(output)


def format_index_result(
    result: dict[str, Any],
) -> str:
    """Format indexing result for MCP output.

    Args:
        result: Indexing result dictionary.

    Returns:
        Formatted string for MCP response.
    """
    output = []
    status = result.get("status", "unknown")
    repository = result.get("repository", "unknown")
    message = result.get("message", "")

    if status == "completed":
        output.append(f"Successfully indexed {repository}.\n")
        output.append(
            "You can now search for it using repo-ctx-search or repo-ctx-docs.\n"
        )
    elif status == "error":
        error = result.get("error", "Unknown error")
        output.append(f"Error indexing {repository}: {error}\n")
    else:
        output.append(f"Indexing {repository}: {status}\n")
        if message:
            output.append(f"{message}\n")

    return "".join(output)


def format_languages_list(
    languages: list[str],
) -> str:
    """Format supported languages list for MCP output.

    Args:
        languages: List of supported language names.

    Returns:
        Formatted string for MCP response.
    """
    output = []
    output.append("Supported languages for code analysis:\n\n")

    for lang in sorted(languages):
        output.append(f"  - {lang}\n")

    output.append(f"\nTotal: {len(languages)} languages\n")

    return "".join(output)


def format_error(
    error: str,
    tool_name: Optional[str] = None,
) -> str:
    """Format error message for MCP output.

    Args:
        error: Error message.
        tool_name: Optional tool name for context.

    Returns:
        Formatted error string.
    """
    if tool_name:
        return f"Error in {tool_name}: {error}"
    return f"Error: {error}"
