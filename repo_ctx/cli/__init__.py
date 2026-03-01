"""CLI module for repo-ctx."""

import sys
import argparse
import asyncio

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
Commands:
  index       Index a repository or group
  list        List indexed repositories
  search      Search repositories or symbols
  docs        Get repository documentation
  analyze     Analyze code (auto-detects local/indexed)
  graph       Generate dependency graph
  dump        Export analysis to .repo-ctx directory
  query       Run CPGQL query (requires Joern)
  export      Export CPG graph (requires Joern)
  status      Show system status

Modes:
  -i, --interactive   Interactive command palette
  -m, --mcp           Start MCP server for AI assistants

Examples:
  repo-ctx index owner/repo              # Index a GitHub repo
  repo-ctx index ./local/project         # Index local directory
  repo-ctx index --group myorg           # Index all repos in org
  repo-ctx list                          # List indexed repos
  repo-ctx search "fastapi"              # Fuzzy search repos
  repo-ctx search "User" -s ./src        # Search symbols in path
  repo-ctx search "User" -s /owner/repo  # Search symbols in indexed repo
  repo-ctx analyze ./src                 # Analyze local code
  repo-ctx analyze /owner/repo           # Analyze indexed repo
  repo-ctx docs /owner/repo              # Get documentation

Target auto-detection:
  /owner/repo  = indexed repository (note the leading /)
  ./path       = local filesystem
  owner/repo   = remote repo (auto-indexes if needed)

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
    parser.add_argument(
        "--legacy",
        action="store_true",
        help="Use legacy core directly instead of service layer"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    # ==========================================================================
    # NEW FLAT COMMANDS (Unix-style)
    # ==========================================================================

    # index - Index repository or group
    flat_index = subparsers.add_parser(
        "index",
        help="Index a repository or group",
        description="Index a repository for documentation search and code analysis"
    )
    flat_index.add_argument("target", help="Repository (owner/repo) or local path (./src)")
    flat_index.add_argument("--group", "-g", action="store_true",
                            help="Treat target as a group/organization to index all repos")
    flat_index.add_argument("--no-subgroups", action="store_true",
                            help="Exclude subgroups (GitLab only)")
    flat_index.add_argument("--gitlab", action="store_const", const="gitlab", dest="provider_shortcut",
                            help="Use GitLab provider")
    flat_index.add_argument("--github", action="store_const", const="github", dest="provider_shortcut",
                            help="Use GitHub provider")
    flat_index.add_argument("--no-analyze", action="store_true",
                            help="Skip code analysis (only index documentation)")

    # list - List indexed repositories
    _flat_list = subparsers.add_parser(
        "list",
        help="List indexed repositories",
        description="List all indexed repositories"
    )

    # search - Unified search (repos and symbols)
    flat_search = subparsers.add_parser(
        "search",
        help="Search repositories or symbols",
        description="Search indexed repositories (default) or symbols (with --symbols)"
    )
    flat_search.add_argument("query", help="Search query")
    flat_search.add_argument("--symbols", "-s", metavar="TARGET",
                             help="Search symbols in TARGET (path or /repo-id)")
    flat_search.add_argument("--exact", "-e", action="store_true",
                             help="Exact match instead of fuzzy search")
    flat_search.add_argument("--limit", "-n", type=int, default=10,
                             help="Maximum results (default: 10)")
    flat_search.add_argument("--type", "-t",
                             choices=["function", "class", "method", "interface", "enum"],
                             help="Filter symbols by type")
    flat_search.add_argument("--lang", "-l",
                             help="Filter symbols by language")

    # docs - Get documentation
    flat_docs = subparsers.add_parser(
        "docs",
        help="Get repository documentation",
        description="Retrieve documentation for an indexed repository"
    )
    flat_docs.add_argument("repository", help="Repository ID (e.g., /owner/repo)")
    flat_docs.add_argument("--topic", "-t", help="Filter by topic")
    flat_docs.add_argument("--include", "-I",
                           help="Include extras (comma-separated): code,symbols,diagrams,tests,examples,all")
    flat_docs.add_argument("--max-tokens", type=int, help="Maximum tokens")
    flat_docs.add_argument("--mode", choices=["summary", "standard", "full"], default="standard",
                           help="Output detail level (default: standard)")
    flat_docs.add_argument("--format", choices=["standard", "llmstxt"],
                           help="Output format (llmstxt for compact)")
    flat_docs.add_argument("--query", "-q", help="Relevance filter query")
    flat_docs.add_argument("--refresh", action="store_true", help="Force re-analysis")
    flat_docs.add_argument("--no-api", action="store_true", help="Exclude API section (llmstxt)")
    flat_docs.add_argument("--no-quickstart", action="store_true", help="Exclude quickstart (llmstxt)")

    # analyze - Code analysis with auto-detection
    flat_analyze = subparsers.add_parser(
        "analyze",
        help="Analyze code structure",
        description="Extract symbols, docstrings, and data flows from code (auto-detects local path or indexed repo)"
    )
    flat_analyze.add_argument("target", help="Path (./src) or repo-id (/owner/repo)")
    flat_analyze.add_argument("--lang", "-l", help="Filter by language")
    flat_analyze.add_argument("--type", "-t",
                              choices=["function", "class", "method", "interface", "enum"],
                              help="Filter by symbol type")
    flat_analyze.add_argument("--no-private", dest="private", action="store_false",
                              help="Exclude private symbols")
    flat_analyze.add_argument("--refresh", action="store_true",
                              help="Force re-analysis for indexed repos")
    flat_analyze.add_argument("--dialect",
                              choices=["standard", "squeak", "pharo", "visualworks", "cincom"],
                              help="Smalltalk dialect (auto-detected if not specified)")

    # graph - Dependency graph
    flat_graph = subparsers.add_parser(
        "graph",
        help="Generate dependency graph",
        description="Generate dependency graph to visualize call graphs and data flows (JSON, DOT, or GraphML)"
    )
    flat_graph.add_argument("target", help="Path or repo-id")
    flat_graph.add_argument("--type", "-t",
                            choices=["file", "module", "class", "function"],
                            default="class",
                            help="Graph type (default: class)")
    flat_graph.add_argument("--format", "-f",
                            choices=["json", "dot", "graphml"],
                            default="json",
                            help="Output format (default: json)")
    flat_graph.add_argument("--depth", "-d", type=int,
                            help="Maximum traversal depth")

    # query - CPG query (Joern)
    flat_query = subparsers.add_parser(
        "query",
        help="Run CPGQL query (requires Joern)",
        description="Execute a CPGQL query on source code"
    )
    flat_query.add_argument("path", help="Path to source directory")
    flat_query.add_argument("query", help="CPGQL query string")

    # export - CPG export (Joern)
    flat_export = subparsers.add_parser(
        "export",
        help="Export CPG graph (requires Joern)",
        description="Export Code Property Graph to visualization format"
    )
    flat_export.add_argument("path", help="Path to source directory")
    flat_export.add_argument("output_dir", help="Output directory")
    flat_export.add_argument("--repr", "-r",
                             choices=["all", "ast", "cfg", "cdg", "ddg", "pdg", "cpg14"],
                             default="all",
                             help="Graph representation (default: all)")
    flat_export.add_argument("--format", "-f",
                             choices=["dot", "graphml", "graphson", "neo4jcsv"],
                             default="dot",
                             help="Export format (default: dot)")

    # status - System status
    _flat_status = subparsers.add_parser(
        "status",
        help="Show system status and capabilities",
        description="Display Joern availability and supported languages"
    )

    # dsm - Dependency Structure Matrix
    flat_dsm = subparsers.add_parser(
        "dsm",
        help="Generate Dependency Structure Matrix",
        description="Generate DSM for architecture analysis (Structure101-style)"
    )
    flat_dsm.add_argument("target", help="Path or repo-id")
    flat_dsm.add_argument("--type", "-t",
                          choices=["file", "module", "class", "function"],
                          default="class",
                          help="Graph type (default: class)")
    flat_dsm.add_argument("--format", "-f",
                          choices=["text", "json"],
                          default="text",
                          help="Output format (default: text)")

    # cycles - Cycle detection
    flat_cycles = subparsers.add_parser(
        "cycles",
        help="Detect dependency cycles",
        description="Find cyclic dependencies with breakup suggestions"
    )
    flat_cycles.add_argument("target", help="Path or repo-id")
    flat_cycles.add_argument("--type", "-t",
                             choices=["file", "module", "class", "function"],
                             default="class",
                             help="Graph type (default: class)")
    flat_cycles.add_argument("--format", "-f",
                             choices=["text", "json"],
                             default="text",
                             help="Output format (default: text)")

    # layers - Layer detection
    flat_layers = subparsers.add_parser(
        "layers",
        help="Detect architectural layers",
        description="Automatically detect layers from dependency structure"
    )
    flat_layers.add_argument("target", help="Path or repo-id")
    flat_layers.add_argument("--type", "-t",
                             choices=["file", "module", "class", "function"],
                             default="class",
                             help="Graph type (default: class)")
    flat_layers.add_argument("--format", "-f",
                             choices=["text", "json"],
                             default="text",
                             help="Output format (default: text)")

    # architecture - Architecture rule checking
    flat_architecture = subparsers.add_parser(
        "architecture",
        help="Check architecture rules",
        description="Detect layers and check architecture rules (Structure101-style)"
    )
    flat_architecture.add_argument("target", help="Path or repo-id")
    flat_architecture.add_argument("--rules", "-r",
                                   help="Path to architecture rules YAML file")
    flat_architecture.add_argument("--type", "-t",
                                   choices=["file", "module", "class", "function"],
                                   default="class",
                                   help="Graph type (default: class)")
    flat_architecture.add_argument("--format", "-f",
                                   choices=["text", "json"],
                                   default="text",
                                   help="Output format (default: text)")

    # metrics - Structural complexity metrics (XS)
    flat_metrics = subparsers.add_parser(
        "metrics",
        help="Calculate structural complexity (XS) metrics",
        description="Calculate XS (eXcess Structural complexity) metrics including grade, hotspots, and component breakdown"
    )
    flat_metrics.add_argument("target", help="Path or repo-id")
    flat_metrics.add_argument("--rules", "-r",
                              help="Path to architecture rules YAML file (violations add to XS)")
    flat_metrics.add_argument("--type", "-t",
                              choices=["file", "module", "class", "function"],
                              default="class",
                              help="Graph type (default: class)")
    flat_metrics.add_argument("--format", "-f",
                              choices=["text", "json"],
                              default="text",
                              help="Output format (default: text)")

    # dump - Export repository analysis to .repo-ctx directory
    flat_dump = subparsers.add_parser(
        "dump",
        help="Export repository analysis to .repo-ctx directory",
        description="Dump repository analysis to a .repo-ctx subdirectory for offline access and versioning"
    )
    flat_dump.add_argument("target", help="Path to local repository")
    flat_dump.add_argument("--level", "-l",
                           choices=["compact", "medium", "full"],
                           default="medium",
                           help="Completeness level (default: medium)")
    flat_dump.add_argument("--output", "-O",
                           help="Custom output path (default: target/.repo-ctx)")
    flat_dump.add_argument("--force", "-f",
                           action="store_true",
                           help="Overwrite existing .repo-ctx directory")
    flat_dump.add_argument("--include-private",
                           action="store_true",
                           help="Include private symbols in output")
    flat_dump.add_argument("--llm",
                           action="store_true",
                           help="Generate LLM-powered business summary (requires OPENAI_API_KEY or similar)")
    flat_dump.add_argument("--llm-model",
                           default="gpt-5-mini",
                           help="LLM model to use for summary (default: gpt-5-mini)")
    flat_dump.add_argument("--exclude", "-x",
                           action="append",
                           dest="exclude_patterns",
                           metavar="PATTERN",
                           help="Glob patterns to exclude (can be used multiple times). Example: --exclude 'tests/*' --exclude '*.test.py'")
    flat_dump.add_argument("--persist-graph", "-g",
                           action="store_true",
                           help="Persist analysis to Neo4j graph database for querying and visualization")
    flat_dump.add_argument("--llm-enhance", "-e",
                           action="store_true",
                           help="Enhance symbol documentation with LLM explanations and create hierarchical aggregation")
    flat_dump.add_argument("--llm-concurrency",
                           type=int,
                           default=5,
                           metavar="N",
                           help="Number of concurrent LLM requests for --llm-enhance (default: 5)")
    flat_dump.add_argument("--skip-joern",
                           action="store_true",
                           help="Skip Joern analysis (use tree-sitter only). Use when Joern runs out of memory on large C/C++ codebases.")

    # ==========================================================================
    # LEGACY NESTED COMMANDS (backwards compatibility)
    # ==========================================================================

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

    # repo search (fuzzy search - default)
    repo_search = repo_subparsers.add_parser(
        "search",
        help="Search indexed repositories (fuzzy matching)",
        description="Search for repositories by name with fuzzy matching"
    )
    repo_search.add_argument("query", help="Search query (supports partial matching)")
    repo_search.add_argument("--limit", "-l", type=int, default=10, help="Max results (default: 10)")

    # repo find-exact (exact name match)
    repo_find_exact = repo_subparsers.add_parser(
        "find-exact",
        help="Find repository by exact name",
        description="Find repositories by exact name match"
    )
    repo_find_exact.add_argument("name", help="Exact repository name to find")

    # repo index-group
    repo_index_group = repo_subparsers.add_parser(
        "index-group",
        help="Index all repositories in a group/organization",
        description="Index all repositories in a GitLab group or GitHub organization"
    )
    repo_index_group.add_argument("group", help="Group or organization name (e.g., 'myorg')")
    repo_index_group.add_argument("--include-subgroups", action="store_true",
                                   help="Include subgroups (GitLab only, default: true)")
    repo_index_group.add_argument("--no-subgroups", action="store_true",
                                   help="Exclude subgroups (GitLab only)")

    # repo list
    _repo_list = repo_subparsers.add_parser(
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
    repo_docs.add_argument("--output-mode", choices=["summary", "standard", "full"],
                          default="standard",
                          help="Output detail level: summary (compact), standard (default), full (everything)")
    repo_docs.add_argument("--query", "-q",
                          help="Search query for relevance-based filtering (prioritizes matching docs)")

    # repo llmstxt
    repo_llmstxt = repo_subparsers.add_parser(
        "llmstxt",
        help="Generate llms.txt summary for a repository",
        description="Generate compact llms.txt summary (<2000 tokens) for quick LLM context"
    )
    repo_llmstxt.add_argument("id", help="Repository ID (e.g., /owner/repo)")
    repo_llmstxt.add_argument("--no-api", action="store_true",
                              help="Exclude API overview section")
    repo_llmstxt.add_argument("--no-quickstart", action="store_true",
                              help="Exclude getting started section")

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
    code_analyze.add_argument("--language", "--lang", "-l", dest="language",
                              choices=["python", "javascript", "typescript", "java", "kotlin",
                                       "c", "cpp", "go", "php", "ruby", "swift", "csharp"],
                              help="Filter by language")
    code_analyze.add_argument("--symbol-type", "--type", "-t", dest="symbol_type",
                              choices=["function", "class", "method", "interface", "enum"],
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
    code_find.add_argument("--symbol-type", "--type", "-t", dest="symbol_type",
                           choices=["function", "class", "method", "interface", "enum"],
                           help="Filter by symbol type")
    code_find.add_argument("--language", "--lang", "-l", dest="language",
                           choices=["python", "javascript", "typescript", "java", "kotlin",
                                    "c", "cpp", "go", "php", "ruby", "swift", "csharp"],
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
    code_dep.add_argument("--graph-type", "--type", "-t", dest="graph_type",
                          choices=["file", "module", "class", "function", "symbol"],
                          default="class",
                          help="Graph type (default: class)")
    code_dep.add_argument("--depth", "-d", type=int, help="Maximum traversal depth")
    code_dep.add_argument("--output-format", "--format", "-f", dest="output_format",
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

    # === CPG (Code Property Graph) commands ===
    cpg_parser = subparsers.add_parser(
        "cpg",
        help="Code Property Graph analysis (requires Joern)",
        description="CPG Analysis Commands (requires Joern installation)"
    )
    cpg_subparsers = cpg_parser.add_subparsers(dest="cpg_command", metavar="<subcommand>")

    # cpg status
    cpg_subparsers.add_parser(
        "status",
        help="Check Joern availability and status",
        description="Show Joern installation status and supported features"
    )

    # cpg query
    cpg_query = cpg_subparsers.add_parser(
        "query",
        help="Run CPGQL query on source code",
        description="Execute a CPGQL (Code Property Graph Query Language) query"
    )
    cpg_query.add_argument("path", help="Path to source directory or CPG file")
    cpg_query.add_argument("query", help='CPGQL query (e.g., "cpg.method.name.l")')

    # cpg export
    cpg_export = cpg_subparsers.add_parser(
        "export",
        help="Export CPG to visualization format",
        description="Export Code Property Graph to DOT, GraphML, or Neo4j CSV"
    )
    cpg_export.add_argument("path", help="Path to source directory or CPG file")
    cpg_export.add_argument("output_dir", help="Directory to write exported files")
    cpg_export.add_argument("--representation", "-r",
                            choices=["all", "ast", "cfg", "cdg", "ddg", "pdg", "cpg14"],
                            default="all",
                            help="Graph representation to export (default: all)")
    cpg_export.add_argument("--format", "-f",
                            choices=["dot", "graphml", "graphson", "neo4jcsv"],
                            default="dot",
                            help="Export format (default: dot)")

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
        # New flat commands
        flat_commands = {"index", "list", "search", "docs", "analyze", "graph", "query", "export", "status", "dsm", "cycles", "layers", "architecture", "metrics", "dump"}
        if args.command in flat_commands:
            # Handle provider shortcut for index
            if args.command == "index" and hasattr(args, 'provider_shortcut') and args.provider_shortcut:
                args.provider = args.provider_shortcut
            from .flat_commands import run_flat_command
            run_flat_command(args)
            return

        # Legacy nested commands (repo, code, config, cpg)
        from .commands import run_command
        run_command(args)
        return

    # No command and no mode flag - show help
    parser.print_help()
