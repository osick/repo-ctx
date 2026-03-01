"""New ctx- prefixed MCP tools implementation.

This module implements the consolidated, simplified MCP tools:
- ctx-index, ctx-list, ctx-search, ctx-docs
- ctx-analyze, ctx-symbol, ctx-symbols, ctx-graph
- ctx-query, ctx-export, ctx-status

These tools use unified parameters and auto-detection of targets
(local paths vs indexed repositories).
"""

import json
import os
from pathlib import Path
from typing import List, Optional

from mcp.types import Tool, TextContent

from .cli.target import detect_target


def _collect_files(analyzer, path_obj: Path) -> dict:
    """Collect analyzable files from a path."""
    files = {}
    if path_obj.is_file():
        if analyzer.detect_language(str(path_obj)):
            with open(path_obj, 'r', encoding='utf-8') as f:
                files[str(path_obj)] = f.read()
    else:
        for root, _, filenames in os.walk(path_obj):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if analyzer.detect_language(filename):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files[file_path] = f.read()
                    except (UnicodeDecodeError, PermissionError):
                        continue
    return files


def get_ctx_tools() -> List[Tool]:
    """Return the list of new ctx- prefixed tools."""
    return [
        # =====================================================================
        # ctx-index: Index repository or group
        # =====================================================================
        Tool(
            name="ctx-index",
            description="Index a repository or group for documentation search and code analysis. Auto-detects provider from path format. Use `group: true` to index all repositories in a group/organization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository path: 'owner/repo' (GitHub), 'group/project' (GitLab), '/local/path', or group name when group=true"
                    },
                    "provider": {
                        "type": "string",
                        "enum": ["auto", "github", "gitlab", "local"],
                        "default": "auto",
                        "description": "Provider: 'auto' (default), 'github', 'gitlab', or 'local'"
                    },
                    "group": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, treat repository as a group/organization and index all repos within it"
                    },
                    "include_subgroups": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include subgroups when indexing a group (GitLab only)"
                    }
                },
                "required": ["repository"]
            }
        ),

        # =====================================================================
        # ctx-list: List indexed repositories
        # =====================================================================
        Tool(
            name="ctx-list",
            description="List all indexed repositories with metadata. Optionally filter by provider.",
            inputSchema={
                "type": "object",
                "properties": {
                    "provider": {
                        "type": "string",
                        "enum": ["github", "gitlab", "local"],
                        "description": "Filter by provider (optional)"
                    }
                }
            }
        ),

        # =====================================================================
        # ctx-search: Unified search (repos and symbols)
        # =====================================================================
        Tool(
            name="ctx-search",
            description="Unified search for repositories or symbols. By default searches repositories with fuzzy matching. Use `mode: 'symbols'` to search for code symbols in a specific target.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (fuzzy matching for repos, substring for symbols)"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["repos", "symbols"],
                        "default": "repos",
                        "description": "Search mode: 'repos' (default) or 'symbols'"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target for symbol search: local path or /repo-id (required when mode='symbols')"
                    },
                    "exact": {
                        "type": "boolean",
                        "default": False,
                        "description": "Use exact matching instead of fuzzy (for repos mode)"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum results (default: 10)"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["function", "class", "method", "interface", "enum"],
                        "description": "Filter symbols by type (only for mode='symbols')"
                    },
                    "lang": {
                        "type": "string",
                        "description": "Filter symbols by language (only for mode='symbols')"
                    }
                },
                "required": ["query"]
            }
        ),

        # =====================================================================
        # ctx-docs: Get repository documentation
        # =====================================================================
        Tool(
            name="ctx-docs",
            description="Get documentation for an indexed repository. Supports topic filtering, code analysis inclusion, and multiple output formats including compact llms.txt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Repository ID (e.g., /owner/repo)"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Filter by topic"
                    },
                    "include": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Include extras: ['code', 'symbols', 'diagrams', 'tests', 'examples', 'all']"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Maximum tokens to return"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["summary", "standard", "full"],
                        "default": "standard",
                        "description": "Output detail level"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["standard", "llmstxt"],
                        "default": "standard",
                        "description": "Output format: 'standard' or 'llmstxt' (compact)"
                    },
                    "query": {
                        "type": "string",
                        "description": "Relevance filter query"
                    },
                    "refresh": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force re-analysis of code"
                    }
                },
                "required": ["repository"]
            }
        ),

        # =====================================================================
        # ctx-analyze: Analyze code
        # =====================================================================
        Tool(
            name="ctx-analyze",
            description="Analyze code and extract symbols. Auto-detects whether target is a local path or indexed repository (use /owner/repo format for indexed repos).",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target: local path (./src) or indexed repo (/owner/repo)"
                    },
                    "lang": {
                        "type": "string",
                        "description": "Filter by language"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["function", "class", "method", "interface", "enum"],
                        "description": "Filter by symbol type"
                    },
                    "include_private": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include private symbols"
                    },
                    "refresh": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force re-analysis for indexed repos"
                    },
                    "smalltalk_dialect": {
                        "type": "string",
                        "enum": ["standard", "squeak", "pharo", "visualworks", "cincom"],
                        "description": "Smalltalk dialect for .st files (auto-detected if not specified)"
                    }
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-symbol: Get symbol details
        # =====================================================================
        Tool(
            name="ctx-symbol",
            description="Get detailed information about a specific symbol including signature, documentation, location, and dependencies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Symbol name or qualified name (e.g., 'MyClass.method')"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target: local path or /repo-id"
                    }
                },
                "required": ["name"]
            }
        ),

        # =====================================================================
        # ctx-symbols: List file symbols
        # =====================================================================
        Tool(
            name="ctx-symbols",
            description="List all symbols defined in a specific file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "Path to the source file"
                    },
                    "group_by_type": {
                        "type": "boolean",
                        "default": True,
                        "description": "Group symbols by type"
                    }
                },
                "required": ["file"]
            }
        ),

        # =====================================================================
        # ctx-graph: Dependency graph
        # =====================================================================
        Tool(
            name="ctx-graph",
            description="Generate dependency graph showing relationships between code elements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Target: local path or /repo-id"
                    },
                    "type": {
                        "type": "string",
                        "enum": ["file", "module", "class", "function"],
                        "default": "class",
                        "description": "Graph type"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "dot", "graphml"],
                        "default": "json",
                        "description": "Output format"
                    },
                    "depth": {
                        "type": "integer",
                        "description": "Maximum traversal depth"
                    }
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-query: CPG query (Joern)
        # =====================================================================
        Tool(
            name="ctx-query",
            description="Run a CPGQL (Code Property Graph Query Language) query on source code. Requires Joern installation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to source directory"
                    },
                    "query": {
                        "type": "string",
                        "description": "CPGQL query string (e.g., 'cpg.method.name.l')"
                    }
                },
                "required": ["path", "query"]
            }
        ),

        # =====================================================================
        # ctx-export: CPG export (Joern)
        # =====================================================================
        Tool(
            name="ctx-export",
            description="Export Code Property Graph to a visualization format. Requires Joern installation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to source directory"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory for exported files"
                    },
                    "representation": {
                        "type": "string",
                        "enum": ["all", "ast", "cfg", "cdg", "ddg", "pdg", "cpg14"],
                        "default": "all",
                        "description": "Graph representation to export"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["dot", "graphml", "graphson", "neo4jcsv"],
                        "default": "dot",
                        "description": "Export format"
                    }
                },
                "required": ["path", "output_dir"]
            }
        ),

        # =====================================================================
        # ctx-status: System status
        # =====================================================================
        Tool(
            name="ctx-status",
            description="Show system status including Joern availability and supported languages.",
            inputSchema={
                "type": "object",
                "properties": {
                    "component": {
                        "type": "string",
                        "enum": ["all", "joern", "languages"],
                        "default": "all",
                        "description": "Component to check"
                    }
                }
            }
        ),

        # =====================================================================
        # ctx-dsm: Design Structure Matrix
        # =====================================================================
        Tool(
            name="ctx-dsm",
            description="Generate a Design Structure Matrix (DSM) for architecture analysis. DSM provides a compact matrix visualization of dependencies — triangular matrix indicates clean layered architecture, cells above diagonal indicate cycles.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Local path or repository ID (owner/repo format)"},
                    "type": {"type": "string", "enum": ["file", "module", "class", "function"], "default": "class", "description": "Graph granularity level"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text", "description": "Output format"}
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-cycles: Dependency cycle detection
        # =====================================================================
        Tool(
            name="ctx-cycles",
            description="Detect dependency cycles in code using Tarjan's algorithm. Returns detailed cycle information including involved nodes, edges, impact scores, and breakup suggestions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Local path or repository ID"},
                    "type": {"type": "string", "enum": ["file", "module", "class", "function"], "default": "class"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text"}
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-layers: Architectural layer detection
        # =====================================================================
        Tool(
            name="ctx-layers",
            description="Detect architectural layers from dependency structure using topological analysis. Automatically identifies natural layers in code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Local path or repository ID"},
                    "type": {"type": "string", "enum": ["file", "module", "class", "function"], "default": "class"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text"}
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-architecture: Architecture analysis with rules
        # =====================================================================
        Tool(
            name="ctx-architecture",
            description="Analyze architecture with layer detection and optional rule enforcement. Supports YAML-based architecture rules for defining layer ordering and forbidden dependencies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Local path or repository ID"},
                    "type": {"type": "string", "enum": ["file", "module", "class", "function"], "default": "class"},
                    "rules_file": {"type": "string", "description": "Path to architecture rules YAML file"},
                    "rules_yaml": {"type": "string", "description": "Inline architecture rules as YAML string"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text"}
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-metrics: Structural complexity metrics
        # =====================================================================
        Tool(
            name="ctx-metrics",
            description="Calculate XS (eXcess Structural complexity) metrics for code. Returns grade (A-F), XS score, component breakdown, and complexity hotspots.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Local path or repository ID"},
                    "type": {"type": "string", "enum": ["file", "module", "class", "function"], "default": "class"},
                    "rules_file": {"type": "string", "description": "Path to architecture rules YAML"},
                    "rules_yaml": {"type": "string", "description": "Inline architecture rules YAML"},
                    "format": {"type": "string", "enum": ["text", "json"], "default": "text"}
                },
                "required": ["target"]
            }
        ),

        # =====================================================================
        # ctx-llmstxt: Generate llms.txt summary
        # =====================================================================
        Tool(
            name="ctx-llmstxt",
            description="Generate a compact llms.txt summary for a repository (<2000 tokens). Returns project overview, key files, quickstart guide, and documentation links.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {"type": "string", "description": "Repository ID (owner/repo or group/project)"},
                    "include_api": {"type": "boolean", "default": True, "description": "Include API overview"},
                    "include_quickstart": {"type": "boolean", "default": True, "description": "Include quickstart guide"}
                },
                "required": ["repository"]
            }
        ),

        # =====================================================================
        # ctx-dump: Export repository analysis
        # =====================================================================
        Tool(
            name="ctx-dump",
            description="Export repository analysis to a .repo-ctx directory. Creates a static snapshot including metadata, symbols, and architecture analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to local repository to dump"},
                    "level": {"type": "string", "enum": ["compact", "medium", "full"], "default": "medium", "description": "Dump completeness level"},
                    "output_path": {"type": "string", "description": "Custom output directory"},
                    "force": {"type": "boolean", "default": False, "description": "Overwrite existing dump"},
                    "include_private": {"type": "boolean", "default": False, "description": "Include private symbols"},
                    "use_llm": {"type": "boolean", "default": False, "description": "Use LLM for business summary"},
                    "llm_model": {"type": "string", "description": "LLM model to use for summary"}
                },
                "required": ["path"]
            }
        ),
    ]


async def handle_ctx_tool(name: str, arguments: dict, context) -> Optional[List[TextContent]]:
    """
    Handle a ctx- prefixed tool call.

    Args:
        name: Tool name (must start with 'ctx-')
        arguments: Tool arguments
        context: GitLabContext instance

    Returns:
        List of TextContent results, or None if tool not found
    """
    if not name.startswith("ctx-"):
        return None

    # =========================================================================
    # ctx-index
    # =========================================================================
    if name == "ctx-index":

        repository = arguments["repository"]
        provider = arguments.get("provider", "auto")
        is_group = arguments.get("group", False)
        include_subgroups = arguments.get("include_subgroups", True)

        try:
            if is_group:
                # Index group
                provider_type = None if provider == "auto" else provider
                result = await context.index_group(
                    repository,
                    include_subgroups=include_subgroups,
                    provider_type=provider_type
                )
                indexed = result.get("indexed", [])
                failed = result.get("failed", [])
                return [TextContent(
                    type="text",
                    text=f"Indexed {len(indexed)} repositories from '{repository}'\n"
                         f"Failed: {len(failed)}"
                )]
            else:
                # Index single repo
                target = detect_target(repository)
                if target.is_local:
                    group = repository
                    project = ""
                    provider_type = "local"
                else:
                    parts = repository.split("/")
                    project = parts[-1]
                    group = "/".join(parts[:-1])
                    provider_type = None if provider == "auto" else provider

                await context.index_repository(group, project, provider_type=provider_type)
                return [TextContent(type="text", text=f"Successfully indexed: {repository}")]

        except Exception as e:
            return [TextContent(type="text", text=f"Error indexing {repository}: {e}")]

    # =========================================================================
    # ctx-list
    # =========================================================================
    elif name == "ctx-list":
        provider_filter = arguments.get("provider")
        libraries = await context.list_all_libraries(provider_filter)

        if not libraries:
            return [TextContent(type="text", text="No repositories indexed.")]

        output = f"Indexed Repositories ({len(libraries)}):\n\n"
        for lib in libraries:
            output += f"  /{lib.group_name}/{lib.project_name}"
            if lib.description:
                output += f" - {lib.description[:40]}"
            output += "\n"

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-search
    # =========================================================================
    elif name == "ctx-search":
        query = arguments["query"]
        mode = arguments.get("mode", "repos")
        exact = arguments.get("exact", False)
        limit = arguments.get("limit", 10)

        if mode == "symbols":
            # Symbol search
            target_str = arguments.get("target")
            if not target_str:
                return [TextContent(type="text", text="Error: 'target' is required for symbol search")]

            from .operations import get_or_analyze_repo
            from .analysis import CodeAnalyzer, SymbolType

            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            all_symbols = []

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                # Local path
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = {}
                if path_obj.is_file():
                    if analyzer.detect_language(str(path_obj)):
                        with open(path_obj, 'r', encoding='utf-8') as f:
                            files[str(path_obj)] = f.read()
                else:
                    for root, _, filenames in os.walk(path_obj):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if analyzer.detect_language(filename):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        files[file_path] = f.read()
                                except (UnicodeDecodeError, PermissionError):
                                    continue

                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)

            # Filter by query
            query_lower = query.lower()
            matching = [s for s in all_symbols if query_lower in s.name.lower()]

            # Apply type filter
            if arguments.get("type"):
                matching = [s for s in matching if s.symbol_type.value == arguments["type"]]

            # Apply language filter
            if arguments.get("lang"):
                matching = [s for s in matching if s.language == arguments["lang"]]

            if not matching:
                return [TextContent(type="text", text=f"No symbols found for '{query}'")]

            output = f"Found {len(matching)} symbol(s) for '{query}':\n\n"
            for s in matching[:limit]:
                loc = f":{s.line_start}" if s.line_start else ""
                output += f"  {s.name} ({s.symbol_type.value}) - {s.file_path}{loc}\n"

            return [TextContent(type="text", text=output)]

        else:
            # Repository search
            if exact:
                results = await context.search_libraries(query)
            else:
                results = await context.fuzzy_search_libraries(query, limit=limit)

            if not results:
                return [TextContent(type="text", text=f"No repositories found for '{query}'")]

            output = f"Search results for '{query}':\n\n"
            for r in results:
                score = f" ({getattr(r, 'score', 1.0):.0%})" if not exact else ""
                output += f"  {r.library_id}{score}"
                if r.description:
                    output += f" - {r.description[:40]}"
                output += "\n"

            return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-docs
    # =========================================================================
    elif name == "ctx-docs":
        from .models import OutputMode
        from .operations import parse_include_options, get_or_analyze_repo, parse_repo_id
        from .llmstxt import LlmsTxtGenerator

        repository = arguments["repository"]
        format_type = arguments.get("format", "standard")

        if format_type == "llmstxt":
            # Generate llms.txt format
            group, project = parse_repo_id(repository)
            lib = await context.storage.get_library(group, project)
            if not lib:
                return [TextContent(type="text", text=f"Repository not found: {repository}")]

            version_id = await context.storage.get_version_id(lib.id, lib.default_version)
            if not version_id:
                return [TextContent(type="text", text=f"No version found for {repository}")]

            documents = await context.storage.get_documents(version_id)
            generator = LlmsTxtGenerator()
            llmstxt = generator.generate(documents, repository, description=lib.description)
            return [TextContent(type="text", text=llmstxt)]

        # Standard documentation
        include_list = arguments.get("include", [])
        include_str = ",".join(include_list) if include_list else None
        include_opts = parse_include_options(include_str)

        output_mode_str = arguments.get("mode", "standard")
        try:
            output_mode = OutputMode.from_string(output_mode_str)
        except ValueError:
            output_mode = OutputMode.STANDARD

        result = await context.get_documentation(
            repository,
            topic=arguments.get("topic"),
            max_tokens=arguments.get("max_tokens"),
            include_examples=include_opts['include_examples'],
            output_mode=output_mode,
            query=arguments.get("query")
        )

        # Add code analysis if requested
        needs_code = include_opts['include_code'] or include_opts['include_symbols'] or include_opts['include_diagrams']
        if needs_code:
            from .analysis import CodeAnalysisReport
            force_refresh = arguments.get("refresh", False)
            symbols, lib, error = await get_or_analyze_repo(context, repository, force_refresh=force_refresh)
            if not error and symbols:
                report = CodeAnalysisReport(symbols, exclude_tests=not include_opts['include_tests'])
                markdown = report.generate_markdown(
                    include_code=include_opts['include_code'],
                    include_symbols=include_opts['include_symbols'],
                    include_mermaid=include_opts['include_diagrams']
                )
                result["content"][0]["text"] += f"\n\n---\n\n{markdown}"

        return [TextContent(type="text", text=result["content"][0]["text"])]

    # =========================================================================
    # ctx-analyze
    # =========================================================================
    elif name == "ctx-analyze":
        from .analysis import CodeAnalyzer, SymbolType
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        target = detect_target(target_str)
        # Pass Smalltalk dialect if specified
        dialect = arguments.get("smalltalk_dialect")
        analyzer = CodeAnalyzer(smalltalk_dialect=dialect)
        all_symbols = []

        if target.is_repo:
            force_refresh = arguments.get("refresh", False)
            symbols, lib, error = await get_or_analyze_repo(context, target.repo_id, force_refresh=force_refresh)
            if error:
                return [TextContent(type="text", text=f"Error: {error}")]
            all_symbols = symbols or []
        else:
            path_obj = Path(target.value)
            if not path_obj.exists():
                return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

            files = {}
            lang_filter = arguments.get("lang")
            if path_obj.is_file():
                lang = analyzer.detect_language(str(path_obj))
                if lang and (not lang_filter or lang == lang_filter):
                    with open(path_obj, 'r', encoding='utf-8') as f:
                        files[str(path_obj)] = f.read()
            else:
                for root, _, filenames in os.walk(path_obj):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        lang = analyzer.detect_language(filename)
                        if lang and (not lang_filter or lang == lang_filter):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    files[file_path] = f.read()
                            except (UnicodeDecodeError, PermissionError):
                                continue

            if files:
                results = analyzer.analyze_files(files)
                all_symbols = analyzer.aggregate_symbols(results)

        # Apply filters
        if arguments.get("type"):
            all_symbols = analyzer.filter_symbols_by_type(all_symbols, SymbolType(arguments["type"]))
        if not arguments.get("include_private", True):
            all_symbols = analyzer.filter_symbols_by_visibility(all_symbols, "public")

        stats = analyzer.get_statistics(all_symbols)

        output = f"Analysis: {target_str}\n\n"
        output += f"Total symbols: {stats['total_symbols']}\n\n"
        if stats['by_type']:
            output += "By type:\n"
            for stype, count in sorted(stats['by_type'].items()):
                output += f"  {stype}: {count}\n"

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-symbol
    # =========================================================================
    elif name == "ctx-symbol":
        from .analysis import CodeAnalyzer
        from .operations import get_or_analyze_repo

        symbol_name = arguments["name"]
        target_str = arguments.get("target", ".")
        target = detect_target(target_str)
        analyzer = CodeAnalyzer()
        all_symbols = []

        if target.is_repo:
            symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
            if error:
                return [TextContent(type="text", text=f"Error: {error}")]
            all_symbols = symbols or []
        else:
            path_obj = Path(target.value)
            if path_obj.exists():
                files = {}
                if path_obj.is_file():
                    if analyzer.detect_language(str(path_obj)):
                        with open(path_obj, 'r', encoding='utf-8') as f:
                            files[str(path_obj)] = f.read()
                else:
                    for root, _, filenames in os.walk(path_obj):
                        for filename in filenames:
                            file_path = os.path.join(root, filename)
                            if analyzer.detect_language(filename):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        files[file_path] = f.read()
                                except (UnicodeDecodeError, PermissionError):
                                    continue
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

        # Find the symbol
        symbol = analyzer.find_symbol(all_symbols, symbol_name)
        if not symbol:
            return [TextContent(type="text", text=f"Symbol not found: {symbol_name}")]

        # Find dependencies of the symbol
        dependencies = analyzer.get_dependencies(all_dependencies, symbol.qualified_name)

        output = f"Symbol: {symbol.name}\n\n"
        output += f"Type: {symbol.symbol_type.value}\n"
        output += f"File: {symbol.file_path}"
        if symbol.line_start:
            output += f":{symbol.line_start}"
        output += "\n"
        output += f"Visibility: {symbol.visibility}\n"
        output += f"Language: {symbol.language}\n"
        if symbol.signature:
            output += f"\nSignature: {symbol.signature}\n"
        if symbol.documentation:
            output += f"\nDocumentation:\n{symbol.documentation}\n"
        
        if dependencies:
            output += "\nDependencies:\n"
            for dep in dependencies:
                output += f"- {dep.dependency_type}: {dep.target}\n"

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-symbols
    # =========================================================================
    elif name == "ctx-symbols":
        from .analysis import CodeAnalyzer

        file_path = arguments["file"]
        group_by_type = arguments.get("group_by_type", True)

        if not Path(file_path).exists():
            return [TextContent(type="text", text=f"File not found: {file_path}")]

        analyzer = CodeAnalyzer()
        if not analyzer.detect_language(file_path):
            return [TextContent(type="text", text=f"Unsupported file type: {file_path}")]

        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        result = analyzer.analyze_file(code, file_path)
        symbols = result[0] if isinstance(result, tuple) else result

        if not symbols:
            return [TextContent(type="text", text=f"No symbols found in {file_path}")]

        output = f"Symbols in {file_path}:\n\n"

        if group_by_type:
            by_type = {}
            for s in symbols:
                stype = s.symbol_type.value
                if stype not in by_type:
                    by_type[stype] = []
                by_type[stype].append(s)

            for stype, syms in sorted(by_type.items()):
                output += f"{stype.upper()}S ({len(syms)}):\n"
                for s in syms:
                    loc = f":{s.line_start}" if s.line_start else ""
                    output += f"  {s.name}{loc}\n"
                output += "\n"
        else:
            for s in symbols:
                loc = f":{s.line_start}" if s.line_start else ""
                output += f"  {s.name} ({s.symbol_type.value}){loc}\n"

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-graph
    # =========================================================================
    elif name == "ctx-graph":
        from .analysis import CodeAnalyzer, DependencyGraph, GraphType
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        target = detect_target(target_str)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(arguments.get("type", "class"), GraphType.CLASS)
        output_format = arguments.get("format", "json")

        all_symbols = []
        all_deps = []

        if target.is_repo:
            symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
            if error:
                return [TextContent(type="text", text=f"Error: {error}")]
            all_symbols = symbols or []
        else:
            path_obj = Path(target.value)
            if not path_obj.exists():
                return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

            files = {}
            if path_obj.is_file():
                if analyzer.detect_language(str(path_obj)):
                    with open(path_obj, 'r', encoding='utf-8') as f:
                        files[str(path_obj)] = f.read()
            else:
                for root, _, filenames in os.walk(path_obj):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        if analyzer.detect_language(filename):
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    files[file_path] = f.read()
                            except (UnicodeDecodeError, PermissionError):
                                continue

            if files:
                results = analyzer.analyze_files(files)
                all_symbols = analyzer.aggregate_symbols(results)
                all_deps = analyzer.aggregate_dependencies(results)

        result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=target_str,
            max_depth=arguments.get("depth")
        )

        if output_format == "dot":
            output = graph_builder.to_dot(result)
        elif output_format == "graphml":
            output = graph_builder.to_graphml(result)
        else:
            output = graph_builder.to_json(result)

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-query
    # =========================================================================
    elif name == "ctx-query":
        from .analysis import CodeAnalyzer

        path = arguments["path"]
        query = arguments["query"]

        analyzer = CodeAnalyzer()
        if not analyzer.is_joern_available():
            return [TextContent(type="text", text="Error: Joern is not installed. See: https://joern.io/")]

        result = analyzer.run_cpg_query(path, query)
        if not result["success"]:
            return [TextContent(type="text", text=f"Query failed: {result.get('error', 'Unknown error')}")]

        return [TextContent(type="text", text=result["output"])]

    # =========================================================================
    # ctx-export
    # =========================================================================
    elif name == "ctx-export":
        from .analysis import CodeAnalyzer

        path = arguments["path"]
        output_dir = arguments["output_dir"]
        representation = arguments.get("representation", "all")
        fmt = arguments.get("format", "dot")

        analyzer = CodeAnalyzer()
        if not analyzer.is_joern_available():
            return [TextContent(type="text", text="Error: Joern is not installed. See: https://joern.io/")]

        result = analyzer.export_cpg_graph(path, output_dir, representation, fmt)
        if not result["success"]:
            return [TextContent(type="text", text=f"Export failed: {result.get('error', 'Unknown error')}")]

        return [TextContent(type="text", text=f"Exported to: {result['output_dir']}")]

    # =========================================================================
    # ctx-status
    # =========================================================================
    elif name == "ctx-status":
        from .analysis import CodeAnalyzer

        component = arguments.get("component", "all")
        analyzer = CodeAnalyzer()

        output = "repo-ctx Status\n\n"

        if component in ("all", "joern"):
            if analyzer.is_joern_available():
                version = analyzer.get_joern_version()
                output += f"Joern: {version}\n"
                languages = analyzer.get_joern_supported_languages()
                output += f"  Languages: {', '.join(sorted(set(languages)))}\n"
            else:
                output += "Joern: Not installed\n"
            output += "\n"

        if component in ("all", "languages"):
            output += "Tree-sitter: Available\n"
            languages = analyzer.get_treesitter_supported_languages()
            output += f"  Languages: {', '.join(sorted(languages))}\n"

        return [TextContent(type="text", text=output)]

    # =========================================================================
    # ctx-dsm
    # =========================================================================
    elif name == "ctx-dsm":
        from .analysis import CodeAnalyzer, DependencyGraph, GraphType, DSMBuilder
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        graph_type_str = arguments.get("type", "class")
        output_format = arguments.get("format", "text")

        try:
            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            graph_builder = DependencyGraph()
            dsm_builder = DSMBuilder()
            all_symbols = []
            all_dependencies = []

            graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }
            graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = _collect_files(analyzer, path_obj)
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

            graph_result = graph_builder.build(
                symbols=all_symbols,
                dependencies=all_dependencies,
                graph_type=graph_type,
                graph_id=target_str,
                graph_label=f"DSM: {target_str}"
            )

            dsm = dsm_builder.build(graph_result)

            if output_format == "json":
                return [TextContent(type="text", text=dsm.to_json())]
            else:
                return [TextContent(type="text", text=dsm.to_text())]

        except Exception as e:
            return [TextContent(type="text", text=f"Error generating DSM: {str(e)}")]

    # =========================================================================
    # ctx-cycles
    # =========================================================================
    elif name == "ctx-cycles":
        from .analysis import CodeAnalyzer, DependencyGraph, GraphType, CycleDetector
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        graph_type_str = arguments.get("type", "class")
        output_format = arguments.get("format", "text")

        try:
            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            graph_builder = DependencyGraph()
            cycle_detector = CycleDetector()
            all_symbols = []
            all_dependencies = []

            graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }
            graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = _collect_files(analyzer, path_obj)
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

            graph_result = graph_builder.build(
                symbols=all_symbols,
                dependencies=all_dependencies,
                graph_type=graph_type,
                graph_id=target_str,
                graph_label=f"Cycles: {target_str}"
            )

            cycles = cycle_detector.detect(graph_result)

            if output_format == "json":
                output = {
                    "source": target_str,
                    "graph_type": graph_type.value,
                    "total_nodes": len(graph_result.nodes),
                    "cycle_count": len(cycles),
                    "cycles": [c.to_dict() for c in cycles]
                }
                return [TextContent(type="text", text=json.dumps(output, indent=2))]
            else:
                if not cycles:
                    text = f"No cycles detected in {target_str}\n"
                    text += f"Graph type: {graph_type.value}\n"
                    text += f"Total nodes: {len(graph_result.nodes)}"
                else:
                    text = f"Found {len(cycles)} cycle(s) in {target_str}\n"
                    text += f"Graph type: {graph_type.value}\n"
                    text += f"Total nodes: {len(graph_result.nodes)}\n\n"

                    for i, cycle in enumerate(cycles, 1):
                        text += f"Cycle {i} (impact: {cycle.impact_score:.1f})\n"
                        text += f"  Nodes: {' -> '.join(cycle.nodes[:8])}\n"
                        if len(cycle.nodes) > 8:
                            text += f"         ... and {len(cycle.nodes) - 8} more\n"
                        text += f"  Edges: {len(cycle.edges)}\n"

                        if cycle.breakup_suggestions:
                            text += "  Breakup suggestions:\n"
                            for j, suggestion in enumerate(cycle.breakup_suggestions[:3], 1):
                                text += f"    {j}. {suggestion.reason}\n"
                        text += "\n"

                return [TextContent(type="text", text=text)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error detecting cycles: {str(e)}")]

    # =========================================================================
    # ctx-layers
    # =========================================================================
    elif name == "ctx-layers":
        from .analysis import CodeAnalyzer, DependencyGraph, GraphType, LayerDetector
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        graph_type_str = arguments.get("type", "class")
        output_format = arguments.get("format", "text")

        try:
            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            graph_builder = DependencyGraph()
            layer_detector = LayerDetector()
            all_symbols = []
            all_dependencies = []

            graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }
            graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = _collect_files(analyzer, path_obj)
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

            graph_result = graph_builder.build(
                symbols=all_symbols,
                dependencies=all_dependencies,
                graph_type=graph_type,
                graph_id=target_str,
                graph_label=f"Layers: {target_str}"
            )

            layers = layer_detector.detect(graph_result)

            if output_format == "json":
                output = {
                    "source": target_str,
                    "graph_type": graph_type_str,
                    "layer_count": len(layers),
                    "layers": [layer.to_dict() for layer in layers]
                }
                return [TextContent(type="text", text=json.dumps(output, indent=2))]
            else:
                if not layers:
                    text = f"No layers detected in {target_str}\n"
                    text += f"Graph type: {graph_type_str}\n"
                    text += f"Total nodes: {len(graph_result.nodes)}\n"
                else:
                    text = f"Detected {len(layers)} layer(s) in {target_str}\n\n"
                    text += f"Graph type: {graph_type_str}\n"
                    text += f"Total nodes: {len(graph_result.nodes)}\n\n"

                    for layer in reversed(layers):
                        text += f"Level {layer.level}: {layer.name}\n"
                        display_nodes = layer.nodes[:10]
                        text += f"  Nodes ({len(layer.nodes)}): {', '.join(display_nodes)}"
                        if len(layer.nodes) > 10:
                            text += f" ... and {len(layer.nodes) - 10} more"
                        text += "\n\n"

                return [TextContent(type="text", text=text)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error detecting layers: {str(e)}")]

    # =========================================================================
    # ctx-architecture
    # =========================================================================
    elif name == "ctx-architecture":
        from .analysis import CodeAnalyzer, DependencyGraph, GraphType, RuleParser, analyze_with_rules
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        graph_type_str = arguments.get("type", "class")
        rules_file = arguments.get("rules_file")
        rules_yaml = arguments.get("rules_yaml")
        output_format = arguments.get("format", "text")

        try:
            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            graph_builder = DependencyGraph()
            all_symbols = []
            all_dependencies = []

            graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }
            graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = _collect_files(analyzer, path_obj)
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

            graph_result = graph_builder.build(
                symbols=all_symbols,
                dependencies=all_dependencies,
                graph_type=graph_type,
                graph_id=target_str,
                graph_label=f"Architecture: {target_str}"
            )

            # Load rules if provided
            rules = None
            if rules_yaml:
                parser = RuleParser()
                rules = parser.parse_yaml(rules_yaml)
            elif rules_file:
                parser = RuleParser()
                rules = parser.parse_file(rules_file)

            # Analyze with rules
            result = analyze_with_rules(graph_result, rules=rules)

            if output_format == "json":
                output = {
                    "source": target_str,
                    "graph_type": graph_type_str,
                    "rules_file": rules_file,
                    **result
                }
                return [TextContent(type="text", text=json.dumps(output, indent=2))]
            else:
                text = f"Architecture Analysis: {target_str}\n\n"
                text += f"Graph type: {graph_type_str}\n"
                text += f"Total nodes: {len(graph_result.nodes)}\n"
                if rules_file:
                    text += f"Rules: {rules_file}\n"
                if result["summary"].get("rules_name"):
                    text += f"Architecture: {result['summary']['rules_name']}\n"
                text += "\n"

                # Layers
                if result["layers"]:
                    text += f"Layers ({len(result['layers'])}):\n"
                    for layer in reversed(result["layers"]):
                        node_count = layer.get("node_count", len(layer.get("nodes", [])))
                        text += f"  Level {layer['level']}: {layer['name']} ({node_count} nodes)\n"
                    text += "\n"

                # Violations
                if result["violations"]:
                    text += f"Violations ({len(result['violations'])}):\n"
                    for v in result["violations"]:
                        text += f"  [{v['severity'].upper()}] {v['rule_name']}: {v['message']}\n"
                        text += f"    {v['source']} -> {v['target']}\n"
                        if v.get("file_path"):
                            loc = f":{v['line']}" if v.get("line") else ""
                            text += f"    at {v['file_path']}{loc}\n"
                        text += "\n"
                else:
                    text += "No architecture violations detected.\n"

                return [TextContent(type="text", text=text)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error analyzing architecture: {str(e)}")]

    # =========================================================================
    # ctx-metrics
    # =========================================================================
    elif name == "ctx-metrics":
        from .analysis import (
            CodeAnalyzer, DependencyGraph, GraphType,
            RuleParser, analyze_structure
        )
        from .operations import get_or_analyze_repo

        target_str = arguments["target"]
        graph_type_str = arguments.get("type", "class")
        rules_file = arguments.get("rules_file")
        rules_yaml = arguments.get("rules_yaml")
        output_format = arguments.get("format", "text")

        try:
            target = detect_target(target_str)
            analyzer = CodeAnalyzer()
            graph_builder = DependencyGraph()
            all_symbols = []
            all_dependencies = []

            graph_type_map = {
                "file": GraphType.FILE,
                "module": GraphType.MODULE,
                "class": GraphType.CLASS,
                "function": GraphType.FUNCTION,
            }
            graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

            if target.is_repo:
                symbols, lib, error = await get_or_analyze_repo(context, target.repo_id)
                if error:
                    return [TextContent(type="text", text=f"Error: {error}")]
                all_symbols = symbols or []
            else:
                path_obj = Path(target.value)
                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: Path not found: {target.value}")]

                files = _collect_files(analyzer, path_obj)
                if files:
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                    all_dependencies = analyzer.aggregate_dependencies(results)

            graph_result = graph_builder.build(
                symbols=all_symbols,
                dependencies=all_dependencies,
                graph_type=graph_type,
                graph_id=target_str,
                graph_label=f"Metrics: {target_str}"
            )

            # Load rules and check violations if specified
            violations = []
            rules = None
            if rules_yaml:
                parser = RuleParser()
                rules = parser.parse_yaml(rules_yaml)
            elif rules_file:
                parser = RuleParser()
                rules = parser.parse_file(rules_file)

            if rules:
                arch_violations = rules.check(graph_result)
                violations = arch_violations

            # Calculate metrics
            report = analyze_structure(graph_result, violations=violations)

            if output_format == "json":
                output = {
                    "source": target_str,
                    "graph_type": graph_type_str,
                    "rules_file": rules_file,
                    **report
                }
                return [TextContent(type="text", text=json.dumps(output, indent=2))]
            else:
                summary = report["summary"]
                metrics = report["metrics"]

                text = f"Structural Metrics: {target_str}\n\n"
                text += f"Grade: {summary['grade']} - {summary['grade_description']}\n"
                text += f"XS Score: {summary['xs_score']}\n\n"

                text += f"Nodes: {summary['total_nodes']} | Edges: {summary['total_edges']}\n"
                text += f"Cycles: {summary['cycles']} | Violations: {summary['violations']}\n\n"

                components = metrics.get("components", {})
                text += "Score Breakdown:\n"
                text += f"  Cycles:     {components.get('cycle_contribution', 0):6.1f}\n"
                text += f"  Coupling:   {components.get('coupling_contribution', 0):6.1f}\n"
                text += f"  Size:       {components.get('size_contribution', 0):6.1f}\n"
                text += f"  Violations: {components.get('violation_contribution', 0):6.1f}\n\n"

                hotspots = report.get("hotspots", [])
                if hotspots:
                    text += f"Hotspots ({len(hotspots)}):\n"
                    for h in hotspots[:5]:
                        text += f"  {h['node_label']} ({h['reason']}) - severity: {h['severity']:.1f}\n"

                return [TextContent(type="text", text=text)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error calculating metrics: {str(e)}")]

    # =========================================================================
    # ctx-llmstxt
    # =========================================================================
    elif name == "ctx-llmstxt":
        from .llmstxt import LlmsTxtGenerator
        from .operations import parse_repo_id

        repository = arguments["repository"]
        include_api = arguments.get("include_api", True)
        include_quickstart = arguments.get("include_quickstart", True)

        try:
            group, project = parse_repo_id(repository)

            lib = await context.storage.get_library(group, project)
            if not lib:
                return [TextContent(type="text", text=f"Error: Library not found: {repository}")]

            version_id = await context.storage.get_version_id(lib.id, lib.default_version)
            if not version_id:
                return [TextContent(type="text", text=f"Error: No version found for {repository}")]

            documents = await context.storage.get_documents(version_id)

            generator = LlmsTxtGenerator()
            llmstxt = generator.generate(
                documents,
                repository,
                description=lib.description,
                include_api=include_api,
                include_quickstart=include_quickstart
            )

            return [TextContent(type="text", text=llmstxt)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error generating llms.txt: {str(e)}")]

    # =========================================================================
    # ctx-dump
    # =========================================================================
    elif name == "ctx-dump":
        import logging
        from .services import create_service_context, DumpService, DumpLevel

        logger = logging.getLogger(__name__)

        try:
            path = arguments.get("path")
            if not path:
                return [TextContent(type="text", text="Error: 'path' parameter is required")]

            source_path = Path(path).expanduser().resolve()
            if not source_path.exists():
                return [TextContent(type="text", text=f"Error: Path not found: {path}")]
            if not source_path.is_dir():
                return [TextContent(type="text", text=f"Error: Path must be a directory: {path}")]

            level_str = arguments.get("level", "medium")
            level_map = {
                "compact": DumpLevel.COMPACT,
                "medium": DumpLevel.MEDIUM,
                "full": DumpLevel.FULL,
            }
            level = level_map.get(level_str, DumpLevel.MEDIUM)

            output_path = None
            if arguments.get("output_path"):
                output_path = Path(arguments["output_path"]).expanduser().resolve()

            service_context = create_service_context()

            llm_service = None
            use_llm = arguments.get("use_llm", False)
            if use_llm:
                try:
                    from .services.llm import LLMService
                    llm_model = arguments.get("llm_model", "gpt-5-mini")
                    llm_service = LLMService(service_context, model=llm_model)
                except Exception as e:
                    logger.warning(f"Could not initialize LLM service: {e}")

            service = DumpService(service_context, llm_service=llm_service)

            result = await service.dump(
                source_path=source_path,
                output_path=output_path,
                level=level,
                force=arguments.get("force", False),
                include_private=arguments.get("include_private", False),
            )

            output = []
            if result.success:
                output.append("Repository Context Dump Created\n\n")
                output.append(f"Output: {result.output_path}\n")
                output.append(f"Level: {result.level.value}\n\n")

                output.append(f"Files Created ({len(result.files_created)})\n\n")
                for f in result.files_created[:20]:
                    output.append(f"- {f}\n")
                if len(result.files_created) > 20:
                    output.append(f"- ... and {len(result.files_created) - 20} more\n")

                if result.metadata:
                    output.append("\nAnalysis Summary\n\n")
                    stats = result.metadata.stats
                    output.append(f"- Symbols extracted: {stats.get('symbols_extracted', 0)}\n")
                    output.append(f"- Files analyzed: {stats.get('files_analyzed', 0)}\n")
                    if result.metadata.git and result.metadata.git.commit:
                        output.append(f"- Git commit: {result.metadata.git.short_commit}\n")
                        if result.metadata.git.branch:
                            output.append(f"- Branch: {result.metadata.git.branch}\n")
                        if result.metadata.git.tag:
                            output.append(f"- Tag: {result.metadata.git.tag}\n")
            else:
                output.append("Dump Failed\n\n")
                for error in result.errors:
                    output.append(f"- {error}\n")

            return [TextContent(type="text", text="".join(output))]

        except Exception as e:
            return [TextContent(type="text", text=f"Error during dump: {str(e)}")]

    return None
