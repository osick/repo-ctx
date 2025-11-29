"""CLI module for repo-ctx."""

import sys
import argparse
import asyncio
from typing import Optional

from rich.console import Console

from .. import __version__

console = Console()


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        prog="repo-ctx",
        description="Repository Context Manager - Index, search, and analyze repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  (default)        Interactive mode when no command given
  -i, --interactive  Interactive command palette
  -m, --mcp          Start MCP server for AI assistants

Examples:
  repo-ctx                          # Interactive mode
  repo-ctx repo index owner/repo    # Index a GitHub repo
  repo-ctx repo search python       # Search repositories
  repo-ctx code analyze ./src       # Analyze code
  repo-ctx code find ./src User     # Find symbols

Run 'repo-ctx <command> --help' for command details.
"""
    )

    # Version
    parser.add_argument(
        "--version", "-V",
        action="version",
        version=f"repo-ctx {__version__}"
    )

    # Mode flags
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive command palette"
    )
    parser.add_argument(
        "-m", "--mcp",
        action="store_true",
        help="Start MCP server for AI assistants"
    )

    # Global options
    parser.add_argument(
        "-c", "--config",
        metavar="PATH",
        help="Config file path"
    )
    parser.add_argument(
        "-p", "--provider",
        choices=["auto", "github", "gitlab", "local"],
        default="auto",
        help="Provider override (default: auto)"
    )
    parser.add_argument(
        "-o", "--output",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # === REPO commands ===
    repo_parser = subparsers.add_parser(
        "repo",
        help="Repository management (index, search, list, docs)",
        description="Repository Management Commands"
    )
    repo_subparsers = repo_parser.add_subparsers(dest="repo_command", metavar="<subcommand>")

    # repo index
    repo_index = repo_subparsers.add_parser(
        "index",
        help="Index a repository",
        description="Index a repository for documentation search"
    )
    repo_index.add_argument("path", help="Repository path (owner/repo, group/project, or local path)")

    # repo search
    repo_search = repo_subparsers.add_parser(
        "search",
        help="Search indexed repositories",
        description="Search for repositories by name"
    )
    repo_search.add_argument("query", help="Search query")
    repo_search.add_argument("--limit", "-l", type=int, default=10, help="Max results (default: 10)")

    # repo list
    repo_list = repo_subparsers.add_parser(
        "list",
        help="List all indexed repositories",
        description="List all indexed repositories"
    )

    # repo docs
    repo_docs = repo_subparsers.add_parser(
        "docs",
        help="Get documentation for a repository",
        description="Retrieve documentation content"
    )
    repo_docs.add_argument("id", help="Repository ID (e.g., /owner/repo)")
    repo_docs.add_argument("--topic", "-t", help="Filter by topic")
    repo_docs.add_argument("--max-tokens", type=int, help="Maximum tokens to return")
    repo_docs.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    repo_docs.add_argument("--include", "-I",
                          help="Include additional content (comma-separated): "
                               "code (structure), symbols (detailed info), diagrams (mermaid), "
                               "tests (include test code), examples (all doc snippets), all")
    repo_docs.add_argument("--refresh", action="store_true",
                          help="Force re-analysis of code (ignore cached symbols)")

    # === CODE commands ===
    code_parser = subparsers.add_parser(
        "code",
        help="Code analysis (analyze, find, info, symbols)",
        description="Code Analysis Commands"
    )
    code_subparsers = code_parser.add_subparsers(dest="code_command", metavar="<subcommand>")

    # code analyze
    code_analyze = code_subparsers.add_parser(
        "analyze",
        help="Analyze code structure",
        description="Extract symbols from source code (local path or indexed repo)"
    )
    code_analyze.add_argument("path", help="Path to file/directory OR repo ID (e.g., /owner/repo)")
    code_analyze.add_argument("--repo", "-r", action="store_true", help="Treat path as indexed repository ID")
    code_analyze.add_argument("--refresh", action="store_true", help="Force re-fetch and re-analyze for repos")
    code_analyze.add_argument("--lang", "-l", choices=["python", "javascript", "typescript", "java", "kotlin"],
                              help="Filter by language")
    code_analyze.add_argument("--type", "-t", choices=["function", "class", "method", "interface", "enum"],
                              help="Filter by symbol type")
    code_analyze.add_argument("--deps", action="store_true", help="Show dependencies")

    # code find
    code_find = code_subparsers.add_parser(
        "find",
        help="Find symbols by pattern",
        description="Search for symbols by name pattern (local path or indexed repo)"
    )
    code_find.add_argument("path", help="Path to search in OR repo ID (e.g., /owner/repo)")
    code_find.add_argument("query", help="Symbol name or pattern")
    code_find.add_argument("--repo", "-r", action="store_true", help="Treat path as indexed repository ID")
    code_find.add_argument("--type", "-t", choices=["function", "class", "method", "interface", "enum"],
                           help="Filter by symbol type")
    code_find.add_argument("--lang", "-l", choices=["python", "javascript", "typescript", "java", "kotlin"],
                           help="Filter by language")

    # code info
    code_info = code_subparsers.add_parser(
        "info",
        help="Get symbol details",
        description="Get detailed information about a symbol (local path or indexed repo)"
    )
    code_info.add_argument("path", help="Path to search in OR repo ID (e.g., /owner/repo)")
    code_info.add_argument("name", help="Symbol name or qualified name")
    code_info.add_argument("--repo", "-r", action="store_true", help="Treat path as indexed repository ID")

    # code symbols
    code_symbols = code_subparsers.add_parser(
        "symbols",
        help="List symbols in a file",
        description="List all symbols in a specific file"
    )
    code_symbols.add_argument("file", help="Source file path")
    code_symbols.add_argument("--group", "-g", action="store_true", help="Group by type")

    # code dep (dependency graph)
    code_dep = code_subparsers.add_parser(
        "dep",
        help="Generate dependency graph",
        description="Generate dependency graph in JSON, DOT, or GraphML format"
    )
    code_dep.add_argument("path", nargs="?", help="Path to file/directory OR repo ID (e.g., /owner/repo)")
    code_dep.add_argument("--repo", "-r", action="store_true", help="Treat path as indexed repository ID")
    code_dep.add_argument("--type", "-t",
                          choices=["file", "module", "class", "function", "symbol"],
                          default="class",
                          help="Graph type (default: class)")
    code_dep.add_argument("--depth", "-d", type=int, help="Maximum traversal depth")
    code_dep.add_argument("--format", "-f",
                          choices=["json", "dot", "graphml"],
                          default="json",
                          help="Output format (default: json)")

    # === CONFIG commands ===
    config_parser = subparsers.add_parser(
        "config",
        help="Configuration management",
        description="Configuration Commands"
    )
    config_subparsers = config_parser.add_subparsers(dest="config_command", metavar="<subcommand>")

    # config show
    config_subparsers.add_parser(
        "show",
        help="Show current configuration",
        description="Display current configuration settings"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()

    # Handle no arguments - default to interactive
    if len(sys.argv) == 1:
        from .interactive import run_interactive
        run_interactive()
        return

    args = parser.parse_args()

    # Mode: Interactive
    if args.interactive:
        from .interactive import run_interactive
        run_interactive()
        return

    # Mode: MCP Server
    if args.mcp:
        from ..mcp_server import serve
        asyncio.run(serve(
            config_path=args.config
        ))
        return

    # Mode: Batch (command provided)
    if args.command:
        from .commands import run_command
        run_command(args)
        return

    # No command and no mode flag - show help
    parser.print_help()
