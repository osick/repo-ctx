"""MCP server implementation."""
import json
from typing import Tuple, Optional, List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .core import GitLabContext
from .config import Config


def parse_repo_id(repo_id: str) -> Tuple[str, str]:
    """Parse repo_id into (group, project) tuple."""
    clean_id = repo_id.strip("/")
    parts = clean_id.split("/")
    if len(parts) >= 2:
        project = parts[-1]
        group = "/".join(parts[:-1])
        return (group, project)
    return (clean_id, "")


async def get_or_analyze_repo(context: GitLabContext, repo_id: str, force_refresh: bool = False):
    """Get stored analysis for a repo, or analyze and store it.

    Returns: (symbols, lib, error_message)
    """
    from .analysis import CodeAnalyzer, Symbol, SymbolType
    from .providers import ProviderFactory

    group, project = parse_repo_id(repo_id)
    lib = await context.storage.get_library(group, project)

    if not lib:
        return None, None, f"Repository {repo_id} not found in index. Use repo-ctx-index first."

    # Check if we have stored symbols
    stored_symbols = await context.storage.search_symbols(lib.id, "")

    if stored_symbols and not force_refresh:
        # Return stored symbols
        symbols = []
        for s in stored_symbols:
            symbols.append(Symbol(
                name=s['name'],
                symbol_type=SymbolType(s['symbol_type']),
                file_path=s['file_path'],
                line_start=s['line_start'],
                line_end=s['line_end'],
                signature=s.get('signature'),
                visibility=s.get('visibility', 'public'),
                language=s.get('language', 'unknown'),
                qualified_name=s.get('qualified_name'),
                documentation=s.get('documentation'),
                is_exported=s.get('is_exported', True),
                metadata={}
            ))
        return symbols, lib, None

    # Need to fetch and analyze
    try:
        config = context.config
        provider = ProviderFactory.from_config(config, lib.provider)
        project_path = f"{group}/{project}"
        project_info = await provider.get_project(project_path)
        ref = await provider.get_default_branch(project_info)
        file_paths = await provider.get_file_tree(project_info, ref)

        analyzer = CodeAnalyzer()
        files = {}
        for file_path in file_paths:
            if analyzer.detect_language(file_path):
                try:
                    file_content = await provider.read_file(project_info, file_path, ref)
                    files[file_path] = file_content.content
                except Exception:
                    continue

        if not files:
            return [], lib, None

        # Analyze
        results = analyzer.analyze_files(files)
        symbols = analyzer.aggregate_symbols(results)

        # Store symbols in database
        await context.storage.save_symbols(symbols, lib.id)

        return symbols, lib, None

    except Exception as e:
        return None, lib, str(e)


async def serve(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    github_url: str = None,
    github_token: str = None,
    storage_path: str = None
):
    """Run MCP server.

    Args:
        config_path: Optional path to config file
        gitlab_url: Optional GitLab URL (overrides config file)
        gitlab_token: Optional GitLab token (overrides config file)
        github_url: Optional GitHub URL (overrides config file)
        github_token: Optional GitHub token (overrides config file)
        storage_path: Optional storage path (overrides config file)
    """
    # Load config with priority: CLI args > env vars > config files
    try:
        config = Config.load(
            config_path=config_path,
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
            github_url=github_url,
            github_token=github_token,
            storage_path=storage_path
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        raise
    
    # Initialize core
    context = GitLabContext(config)
    await context.init()
    
    # Create server
    server = Server("repo-ctx")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="repo-ctx-search",
                description="Search for indexed repositories by exact name match. Returns matching repositories with their IDs and available versions. Works across all providers (local, GitHub, GitLab).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "libraryName": {
                            "type": "string",
                            "description": "Repository name to search for"
                        }
                    },
                    "required": ["libraryName"]
                }
            ),
            Tool(
                name="repo-ctx-fuzzy-search",
                description="Fuzzy search for repositories with typo tolerance. Returns top matches even with partial names or typos. Use this when you don't know the exact repository path. Works across all indexed repositories (local, GitHub, GitLab).",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term (can be partial or fuzzy)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum results to return (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="repo-ctx-index",
                description="Index a repository to make its documentation searchable. Supports local Git repositories (absolute/relative paths), GitHub (owner/repo), and GitLab (group/project). Auto-detects provider from path format.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repository": {
                            "type": "string",
                            "description": "Repository path: '/path/to/local/repo', 'owner/repo' (GitHub), or 'group/project' (GitLab)"
                        },
                        "provider": {
                            "type": "string",
                            "description": "Provider to use: 'local', 'gitlab', 'github', or 'auto' for auto-detection (default: auto)",
                            "enum": ["local", "gitlab", "github", "auto"],
                            "default": "auto"
                        }
                    },
                    "required": ["repository"]
                }
            ),
            Tool(
                name="repo-ctx-index-group",
                description="Index all repositories in a GitLab group or GitHub organization. Optionally include subgroups (GitLab only). Not supported for local provider.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "Group/organization path (e.g., 'groupname' or 'orgname')"
                        },
                        "includeSubgroups": {
                            "type": "boolean",
                            "description": "Include subgroups - only works with GitLab (default: true)",
                            "default": True
                        },
                        "provider": {
                            "type": "string",
                            "description": "Provider to use: 'gitlab', 'github', or 'auto' (default: auto)",
                            "enum": ["gitlab", "github", "auto"],
                            "default": "auto"
                        }
                    },
                    "required": ["group"]
                }
            ),
            Tool(
                name="repo-ctx-docs",
                description="Retrieve documentation for a specific indexed repository. Supports topic filtering and token-based limiting (recommended) or page-based pagination. Works with any indexed repository (local, GitHub, GitLab). Optionally include code analysis summary with class hierarchy and API overview.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "libraryId": {
                            "type": "string",
                            "description": "Library ID in format /group/project or /group/project/version"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Optional topic to filter documentation"
                        },
                        "maxTokens": {
                            "type": "integer",
                            "description": "Maximum tokens to return (recommended for LLM context management, e.g., 8000 for most models, 50000 for long-context models). If specified, page parameter is ignored."
                        },
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination (default: 1). Ignored if maxTokens is specified.",
                            "default": 1
                        },
                        "includeMetadata": {
                            "type": "boolean",
                            "description": "Include quality scores, document types, and metadata in response (default: false)",
                            "default": False
                        },
                        "includeCodeAnalysis": {
                            "type": "boolean",
                            "description": "Include code analysis summary with symbol statistics, class hierarchy (mermaid), and public API overview (default: false)",
                            "default": False
                        }
                    },
                    "required": ["libraryId"]
                }
            ),
            Tool(
                name="repo-ctx-list",
                description="List all indexed repositories with metadata (name, description, versions, last indexed date). Optionally filter by provider. Use this to see what's available in your index.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "provider": {
                            "type": "string",
                            "description": "Optional provider filter: 'local', 'github', 'gitlab', or omit for all",
                            "enum": ["local", "github", "gitlab"]
                        }
                    }
                }
            ),
            Tool(
                name="repo-ctx-analyze",
                description="Analyze source code to extract symbols (functions, classes, methods, etc.). Supports Python, JavaScript, TypeScript, Java, and Kotlin. Can analyze local paths OR indexed repositories. Returns detailed symbol information including signatures, visibility, documentation, and location.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to file or directory to analyze (absolute or relative). Not required if repoId is provided."
                        },
                        "repoId": {
                            "type": "string",
                            "description": "Optional: Repository ID of an indexed repo (e.g., /owner/repo). If provided, analyzes the indexed repository instead of a local path."
                        },
                        "refresh": {
                            "type": "boolean",
                            "description": "Force re-fetch and re-analyze for indexed repos (default: false)",
                            "default": False
                        },
                        "language": {
                            "type": "string",
                            "description": "Optional: Filter by language (python, javascript, typescript, java, kotlin)",
                            "enum": ["python", "javascript", "typescript", "java", "kotlin"]
                        },
                        "symbolType": {
                            "type": "string",
                            "description": "Optional: Filter by symbol type (function, class, method, interface, enum)",
                            "enum": ["function", "class", "method", "interface", "enum"]
                        },
                        "includePrivate": {
                            "type": "boolean",
                            "description": "Include private symbols (default: true)",
                            "default": True
                        },
                        "outputFormat": {
                            "type": "string",
                            "description": "Output format: text (human-readable with emojis), json (structured), yaml (structured)",
                            "enum": ["text", "json", "yaml"],
                            "default": "text"
                        }
                    }
                }
            ),
            Tool(
                name="repo-ctx-search-symbol",
                description="Search for symbols by name or pattern across analyzed code. Can search local paths OR indexed repositories. Use fuzzy matching to find functions, classes, methods even with partial names. Useful for code navigation and exploration.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to file or directory to search in. Not required if repoId is provided."
                        },
                        "repoId": {
                            "type": "string",
                            "description": "Optional: Repository ID of an indexed repo (e.g., /owner/repo). If provided, searches the indexed repository instead of a local path."
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query (symbol name or pattern)"
                        },
                        "symbolType": {
                            "type": "string",
                            "description": "Optional: Filter by symbol type",
                            "enum": ["function", "class", "method", "interface", "enum"]
                        },
                        "language": {
                            "type": "string",
                            "description": "Optional: Filter by language",
                            "enum": ["python", "javascript", "typescript", "java", "kotlin"]
                        },
                        "outputFormat": {
                            "type": "string",
                            "description": "Output format: text (human-readable), json (structured), yaml (structured)",
                            "enum": ["text", "json", "yaml"],
                            "default": "text"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="repo-ctx-get-symbol-detail",
                description="Get detailed information about a specific symbol including its full signature, documentation, metadata, and source location. Can search local paths OR indexed repositories. Use after finding a symbol with search-symbol.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to file or directory. Not required if repoId is provided."
                        },
                        "repoId": {
                            "type": "string",
                            "description": "Optional: Repository ID of an indexed repo (e.g., /owner/repo). If provided, searches the indexed repository instead of a local path."
                        },
                        "symbolName": {
                            "type": "string",
                            "description": "Exact symbol name or qualified name (e.g., 'MyClass.method')"
                        },
                        "outputFormat": {
                            "type": "string",
                            "description": "Output format: text (human-readable), json (structured), yaml (structured)",
                            "enum": ["text", "json", "yaml"],
                            "default": "text"
                        }
                    },
                    "required": ["symbolName"]
                }
            ),
            Tool(
                name="repo-ctx-get-file-symbols",
                description="Get all symbols defined in a specific file. Returns symbols organized by type with full details. Useful for understanding file structure.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filePath": {
                            "type": "string",
                            "description": "Path to the source file"
                        },
                        "groupByType": {
                            "type": "boolean",
                            "description": "Group symbols by type (default: true)",
                            "default": True
                        },
                        "outputFormat": {
                            "type": "string",
                            "description": "Output format: text (human-readable), json (structured), yaml (structured)",
                            "enum": ["text", "json", "yaml"],
                            "default": "text"
                        }
                    },
                    "required": ["filePath"]
                }
            ),
            Tool(
                name="repo-ctx-dependency-graph",
                description="Generate a dependency graph showing relationships between code elements. Supports multiple graph types (file, module, class, function) and output formats (JSON, DOT, GraphML). Essential for understanding code architecture and dependencies.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to file or directory to analyze. Not required if repoId is provided."
                        },
                        "repoId": {
                            "type": "string",
                            "description": "Optional: Repository ID of an indexed repo (e.g., /owner/repo). If provided, analyzes the indexed repository instead of a local path."
                        },
                        "graphType": {
                            "type": "string",
                            "description": "Type of dependency graph to generate",
                            "enum": ["file", "module", "class", "function", "symbol"],
                            "default": "class"
                        },
                        "depth": {
                            "type": "integer",
                            "description": "Maximum traversal depth (default: unlimited)"
                        },
                        "outputFormat": {
                            "type": "string",
                            "description": "Output format: json (JGF), dot (GraphViz), graphml (XML)",
                            "enum": ["json", "dot", "graphml"],
                            "default": "json"
                        }
                    }
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "repo-ctx-search":
            library_name = arguments["libraryName"]
            results = await context.search_libraries(library_name)

            output = []
            output.append("Available Repositories (search results):\n\n")

            for result in results:
                output.append(f"- Repository ID: {result.library_id}\n")
                output.append(f"  Name: {result.name}\n")
                output.append(f"  Description: {result.description}\n")
                output.append(f"  Versions: {', '.join(result.versions)}\n")
                output.append("\n")

            if not results:
                output.append(f"No repositories found matching '{library_name}'.\n")
                output.append("Make sure the repository has been indexed first using repo-ctx-index.\n")

            return [TextContent(type="text", text="".join(output))]

        elif name == "repo-ctx-fuzzy-search":
            query = arguments["query"]
            limit = arguments.get("limit", 10)
            results = await context.fuzzy_search_libraries(query, limit)

            output = []
            output.append(f"Fuzzy search results for '{query}':\n\n")

            for i, result in enumerate(results, 1):
                output.append(f"{i}. {result.library_id}\n")
                output.append(f"   Name: {result.name}\n")
                output.append(f"   Group: {result.group}\n")
                output.append(f"   Description: {result.description}\n")
                output.append(f"   Match: {result.match_type} in {result.matched_field} (score: {result.score:.2f})\n")
                output.append("\n")

            if not results:
                output.append(f"No repositories found matching '{query}'.\n")
                output.append("Try a different search term or index repositories first using repo-ctx-index or repo-ctx-index-group.\n")
            else:
                output.append(f"\nTo get documentation, use repo-ctx-docs with one of the Repository IDs above.\n")

            return [TextContent(type="text", text="".join(output))]

        elif name == "repo-ctx-index":
            repository = arguments["repository"]
            provider = arguments.get("provider", "auto")

            # Handle local paths (don't split them)
            from .providers.detector import ProviderDetector
            detected_provider = ProviderDetector.detect(repository)

            if detected_provider == "local" or provider == "local" or repository.startswith(("/", "./", "~/")):
                group = repository
                project = ""
            else:
                parts = repository.split("/")
                if len(parts) < 2:
                    return [TextContent(type="text", text=f"Error: Repository must be in format group/project, owner/repo, or /path/to/repo")]
                project = parts[-1]
                group = "/".join(parts[:-1])

            # Convert "auto" to None for auto-detection
            provider_type = None if provider == "auto" else provider

            try:
                await context.index_repository(group, project, provider_type=provider_type)
                provider_used = provider_type or "auto-detected"
                return [TextContent(type="text", text=f"Successfully indexed {repository} using {provider_used} provider. You can now search for it using repo-ctx-fuzzy-search or repo-ctx-docs.")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error indexing {repository}: {str(e)}")]

        elif name == "repo-ctx-index-group":
            group = arguments["group"]
            include_subgroups = arguments.get("includeSubgroups", True)
            provider = arguments.get("provider", "auto")

            # Convert "auto" to None for auto-detection
            provider_type = None if provider == "auto" else provider

            try:
                results = await context.index_group(group, include_subgroups, provider_type=provider_type)
                output = []
                provider_used = provider_type or "auto-detected"
                output.append(f"Indexed group '{group}' using {provider_used} provider:\n\n")
                output.append(f"Total projects: {results['total']}\n")
                output.append(f"Successfully indexed: {len(results['indexed'])}\n")
                output.append(f"Failed: {len(results['failed'])}\n\n")

                if results['indexed']:
                    output.append("Indexed repositories:\n")
                    for repo in results['indexed'][:10]:  # Show first 10
                        output.append(f"  - {repo}\n")
                    if len(results['indexed']) > 10:
                        output.append(f"  ... and {len(results['indexed']) - 10} more\n")

                if results['failed']:
                    output.append("\nFailed repositories:\n")
                    for fail in results['failed'][:5]:  # Show first 5 failures
                        output.append(f"  - {fail['path']}: {fail['error']}\n")

                return [TextContent(type="text", text="".join(output))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error indexing group {group}: {str(e)}")]

        elif name == "repo-ctx-docs":
            library_id = arguments["libraryId"]
            topic = arguments.get("topic")
            page = arguments.get("page", 1)
            max_tokens = arguments.get("maxTokens")
            include_metadata = arguments.get("includeMetadata", False)
            include_code_analysis = arguments.get("includeCodeAnalysis", False)

            try:
                result = await context.get_documentation(
                    library_id,
                    topic,
                    page,
                    max_tokens=max_tokens
                )

                # Build response text
                response_text = result["content"][0]["text"]

                # Optionally append metadata
                if include_metadata and "documents_metadata" in result.get("metadata", {}):
                    metadata = result["metadata"]
                    response_text += "\n\n---\n\n## Documentation Metadata\n\n"
                    response_text += f"**Library:** {metadata['library']}\n"
                    response_text += f"**Version:** {metadata['version']}\n"
                    response_text += f"**Documents:** {metadata['documents_count']}\n"
                    response_text += f"**Total tokens:** {metadata['tokens']}\n\n"

                    response_text += "### Document Quality & Classification\n\n"
                    for doc_meta in metadata["documents_metadata"]:
                        response_text += f"- **{doc_meta['file_path']}**\n"
                        response_text += f"  - Type: {doc_meta['document_type'].title()}\n"
                        response_text += f"  - Quality Score: {doc_meta['quality_score']}/100\n"
                        response_text += f"  - Reading Time: {doc_meta['reading_time']} min\n"
                        response_text += f"  - Code Examples: {doc_meta['snippet_count']}\n"

                # Optionally append code analysis
                if include_code_analysis:
                    from .analysis import CodeAnalysisReport

                    # Get symbols for the repository
                    symbols, lib, error = await get_or_analyze_repo(context, library_id)

                    if not error and symbols:
                        # Generate code analysis report
                        report = CodeAnalysisReport(symbols)
                        markdown_report = report.generate_markdown(include_mermaid=True)
                        response_text += f"\n\n---\n\n{markdown_report}"

                return [TextContent(type="text", text=response_text)]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        elif name == "repo-ctx-list":
            provider_filter = arguments.get("provider")

            try:
                libraries = await context.list_all_libraries(provider_filter)

                output = []
                if provider_filter:
                    output.append(f"Indexed repositories ({provider_filter} provider):\n\n")
                else:
                    output.append(f"All indexed repositories ({len(libraries)} total):\n\n")

                if not libraries:
                    if provider_filter:
                        output.append(f"No repositories found for provider '{provider_filter}'.\n")
                    else:
                        output.append("No repositories indexed yet.\n")
                        output.append("Use repo-ctx-index to index repositories.\n")
                    return [TextContent(type="text", text="".join(output))]

                for i, lib in enumerate(libraries, 1):
                    library_id = f"/{lib.group_name}/{lib.project_name}"
                    output.append(f"{i}. {library_id}\n")

                    # Show URL or file path
                    url = context._get_repository_url(lib)
                    output.append(f"   URL: {url}\n")

                    if lib.description:
                        output.append(f"   Description: {lib.description}\n")
                    if lib.default_version:
                        output.append(f"   Default version: {lib.default_version}\n")
                    if lib.last_indexed:
                        output.append(f"   Last indexed: {lib.last_indexed}\n")
                    output.append("\n")

                return [TextContent(type="text", text="".join(output))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error listing repositories: {str(e)}")]

        elif name == "repo-ctx-analyze":
            from pathlib import Path
            from .analysis import CodeAnalyzer, SymbolType
            import os

            path = arguments.get("path")
            repo_id = arguments.get("repoId")
            force_refresh = arguments.get("refresh", False)
            language_filter = arguments.get("language")
            symbol_type_filter = arguments.get("symbolType")
            include_private = arguments.get("includePrivate", True)
            output_format = arguments.get("outputFormat", "text")

            try:
                analyzer = CodeAnalyzer()
                all_symbols = []
                files = {}
                source_info = path or repo_id

                # Check if using indexed repo
                if repo_id:
                    symbols, lib, error = await get_or_analyze_repo(context, repo_id, force_refresh=force_refresh)

                    if error:
                        return [TextContent(type="text", text=f"Error: {error}")]

                    if not symbols:
                        return [TextContent(type="text", text=f"No symbols found in '{repo_id}'")]

                    all_symbols = symbols
                    source_info = f"{repo_id} (indexed)"

                elif path:
                    # Use local path
                    path_obj = Path(path)

                    if not path_obj.exists():
                        return [TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                    # Collect files to analyze
                    if path_obj.is_file():
                        if analyzer.detect_language(str(path_obj)):
                            with open(path_obj, 'r', encoding='utf-8') as f:
                                files[str(path_obj)] = f.read()
                    elif path_obj.is_dir():
                        for root, _, filenames in os.walk(path_obj):
                            for filename in filenames:
                                file_path = os.path.join(root, filename)
                                if analyzer.detect_language(filename):
                                    try:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            files[file_path] = f.read()
                                    except (UnicodeDecodeError, PermissionError):
                                        continue

                    if not files:
                        return [TextContent(type="text", text=f"No supported files found in '{path}'")]

                    # Analyze files
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                else:
                    return [TextContent(type="text", text="Error: Either 'path' or 'repoId' must be provided")]

                # Apply filters
                if language_filter:
                    all_symbols = [s for s in all_symbols if s.language == language_filter]
                if symbol_type_filter:
                    all_symbols = analyzer.filter_symbols_by_type(all_symbols, SymbolType(symbol_type_filter))
                if not include_private:
                    all_symbols = analyzer.filter_symbols_by_visibility(all_symbols, "public")

                # Get statistics
                stats = analyzer.get_statistics(all_symbols)

                # Format output based on outputFormat
                if output_format in ["json", "yaml"]:
                    import json
                    # Structured output
                    output_data = {
                        "source": source_info,
                        "files_analyzed": len(files) if files else "stored",
                        "statistics": stats,
                        "symbols": [
                            {
                                "name": s.name,
                                "type": s.symbol_type.value,
                                "file": s.file_path,
                                "line": s.line_start,
                                "signature": s.signature,
                                "visibility": s.visibility,
                                "language": s.language,
                                "qualified_name": s.qualified_name,
                                "documentation": s.documentation
                            }
                            for s in all_symbols
                        ]
                    }
                    if output_format == "json":
                        return [TextContent(type="text", text=json.dumps(output_data, indent=2))]
                    else:  # yaml
                        import yaml
                        return [TextContent(type="text", text=yaml.dump(output_data, default_flow_style=False, sort_keys=False))]
                else:
                    # Text output with emojis
                    output = []
                    output.append(f"📊 Code Analysis Results for '{source_info}':\n\n")

                    output.append(f"**Summary:**\n")
                    output.append(f"- Total symbols: {stats['total_symbols']}\n")
                    if files:
                        output.append(f"- Files analyzed: {len(files)}\n\n")
                    else:
                        output.append(f"- Source: indexed repository\n\n")

                    output.append("**Symbols by type:**\n")
                    for stype, count in stats['by_type'].items():
                        output.append(f"- {stype}: {count}\n")
                    output.append("\n")

                    # Group by file
                    by_file = {}
                    for symbol in all_symbols:
                        if symbol.file_path not in by_file:
                            by_file[symbol.file_path] = []
                        by_file[symbol.file_path].append(symbol)

                    output.append("**Symbols by file:**\n\n")
                    for file_path, symbols in sorted(by_file.items()):
                        output.append(f"### 📄 {file_path}\n")
                        for symbol in sorted(symbols, key=lambda s: s.line_start or 0):
                            visibility_marker = "🔒" if symbol.visibility == "private" else "🔓"
                            output.append(f"- {visibility_marker} `{symbol.name}` ({symbol.symbol_type.value})")
                            if symbol.signature:
                                output.append(f" - {symbol.signature}")
                            if symbol.line_start:
                                output.append(f" - Line {symbol.line_start}")
                            output.append("\n")
                        output.append("\n")

                    return [TextContent(type="text", text="".join(output))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error analyzing code: {str(e)}")]

        elif name == "repo-ctx-search-symbol":
            from pathlib import Path
            from .analysis import CodeAnalyzer, SymbolType
            import os

            path = arguments.get("path")
            repo_id = arguments.get("repoId")
            query = arguments["query"].lower()
            symbol_type_filter = arguments.get("symbolType")
            language_filter = arguments.get("language")
            output_format = arguments.get("outputFormat", "text")

            try:
                analyzer = CodeAnalyzer()
                all_symbols = []

                # Check if using indexed repo
                if repo_id:
                    symbols, lib, error = await get_or_analyze_repo(context, repo_id)

                    if error:
                        return [TextContent(type="text", text=f"Error: {error}")]

                    if not symbols:
                        return [TextContent(type="text", text=f"No symbols found in '{repo_id}'")]

                    all_symbols = symbols

                elif path:
                    # Use local path
                    path_obj = Path(path)

                    if not path_obj.exists():
                        return [TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                    # Collect and analyze files
                    files = {}
                    if path_obj.is_file():
                        if analyzer.detect_language(str(path_obj)):
                            with open(path_obj, 'r', encoding='utf-8') as f:
                                files[str(path_obj)] = f.read()
                    elif path_obj.is_dir():
                        for root, _, filenames in os.walk(path_obj):
                            for filename in filenames:
                                file_path = os.path.join(root, filename)
                                if analyzer.detect_language(filename):
                                    try:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            files[file_path] = f.read()
                                    except (UnicodeDecodeError, PermissionError):
                                        continue

                    if not files:
                        return [TextContent(type="text", text=f"No supported files found in '{path}'")]

                    # Analyze and filter
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                else:
                    return [TextContent(type="text", text="Error: Either 'path' or 'repoId' must be provided")]

                # Search by name (case-insensitive substring match)
                matching = [s for s in all_symbols if query in s.name.lower()]

                # Apply additional filters
                if symbol_type_filter:
                    matching = analyzer.filter_symbols_by_type(matching, SymbolType(symbol_type_filter))
                if language_filter:
                    matching = [s for s in matching if s.language == language_filter]

                # Format output based on outputFormat
                if output_format in ["json", "yaml"]:
                    import json
                    output_data = {
                        "query": query,
                        "matches_found": len(matching),
                        "symbols": [
                            {
                                "name": s.name,
                                "type": s.symbol_type.value,
                                "file": s.file_path,
                                "line": s.line_start,
                                "signature": s.signature,
                                "visibility": s.visibility,
                                "language": s.language,
                                "documentation": s.documentation
                            }
                            for s in sorted(matching, key=lambda s: (s.file_path, s.line_start or 0))
                        ]
                    }
                    if output_format == "json":
                        return [TextContent(type="text", text=json.dumps(output_data, indent=2))]
                    else:  # yaml
                        import yaml
                        return [TextContent(type="text", text=yaml.dump(output_data, default_flow_style=False, sort_keys=False))]
                else:
                    # Text output
                    output = []
                    output.append(f"🔍 Symbol search results for '{query}':\n\n")
                    output.append(f"Found {len(matching)} matching symbol(s)\n\n")

                    if matching:
                        for symbol in sorted(matching, key=lambda s: (s.file_path, s.line_start or 0)):
                            output.append(f"**{symbol.name}** ({symbol.symbol_type.value})\n")
                            output.append(f"- File: {symbol.file_path}")
                            if symbol.line_start:
                                output.append(f":{symbol.line_start}")
                            output.append("\n")
                            if symbol.signature:
                                output.append(f"- Signature: `{symbol.signature}`\n")
                            if symbol.documentation:
                                output.append(f"- Documentation: {symbol.documentation}\n")
                            output.append(f"- Visibility: {symbol.visibility}\n")
                            output.append("\n")
                    else:
                        output.append(f"No symbols found matching '{query}'\n")

                    return [TextContent(type="text", text="".join(output))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error searching symbols: {str(e)}")]

        elif name == "repo-ctx-get-symbol-detail":
            from pathlib import Path
            from .analysis import CodeAnalyzer
            import os
            import json

            path = arguments.get("path")
            repo_id = arguments.get("repoId")
            symbol_name = arguments["symbolName"]
            output_format = arguments.get("outputFormat", "text")

            try:
                analyzer = CodeAnalyzer()
                all_symbols = []

                # Check if using indexed repo
                if repo_id:
                    symbols, lib, error = await get_or_analyze_repo(context, repo_id)

                    if error:
                        return [TextContent(type="text", text=f"Error: {error}")]

                    if not symbols:
                        return [TextContent(type="text", text=f"No symbols found in '{repo_id}'")]

                    all_symbols = symbols

                elif path:
                    # Use local path
                    path_obj = Path(path)

                    if not path_obj.exists():
                        return [TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                    # Collect and analyze files
                    files = {}
                    if path_obj.is_file():
                        if analyzer.detect_language(str(path_obj)):
                            with open(path_obj, 'r', encoding='utf-8') as f:
                                files[str(path_obj)] = f.read()
                    elif path_obj.is_dir():
                        for root, _, filenames in os.walk(path_obj):
                            for filename in filenames:
                                file_path = os.path.join(root, filename)
                                if analyzer.detect_language(filename):
                                    try:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            files[file_path] = f.read()
                                    except (UnicodeDecodeError, PermissionError):
                                        continue

                    if not files:
                        return [TextContent(type="text", text=f"No supported files found in '{path}'")]

                    # Analyze and find symbol
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)
                else:
                    return [TextContent(type="text", text="Error: Either 'path' or 'repoId' must be provided")]

                # Find by exact name or qualified name
                matching = [s for s in all_symbols
                           if s.name == symbol_name or s.qualified_name == symbol_name]

                if not matching:
                    return [TextContent(type="text", text=f"Symbol '{symbol_name}' not found")]

                symbol = matching[0]

                # Format output based on outputFormat
                if output_format in ["json", "yaml"]:
                    output_data = {
                        "name": symbol.name,
                        "type": symbol.symbol_type.value,
                        "language": symbol.language,
                        "file": symbol.file_path,
                        "line_start": symbol.line_start,
                        "line_end": symbol.line_end,
                        "visibility": symbol.visibility,
                        "qualified_name": symbol.qualified_name,
                        "signature": symbol.signature,
                        "documentation": symbol.documentation,
                        "is_exported": symbol.is_exported,
                        "metadata": symbol.metadata
                    }
                    if len(matching) > 1:
                        output_data["other_matches"] = [
                            {"file": s.file_path, "line": s.line_start}
                            for s in matching[1:]
                        ]
                    if output_format == "json":
                        return [TextContent(type="text", text=json.dumps(output_data, indent=2))]
                    else:  # yaml
                        import yaml
                        return [TextContent(type="text", text=yaml.dump(output_data, default_flow_style=False, sort_keys=False))]
                else:
                    # Text output
                    output = []
                    output.append(f"# Symbol Detail: {symbol.name}\n\n")
                    output.append(f"**Type:** {symbol.symbol_type.value}\n")
                    output.append(f"**Language:** {symbol.language}\n")
                    output.append(f"**File:** {symbol.file_path}\n")
                    if symbol.line_start:
                        if symbol.line_end:
                            output.append(f"**Location:** Lines {symbol.line_start}-{symbol.line_end}\n")
                        else:
                            output.append(f"**Location:** Line {symbol.line_start}\n")
                    output.append(f"**Visibility:** {symbol.visibility}\n")

                    if symbol.qualified_name:
                        output.append(f"**Qualified Name:** {symbol.qualified_name}\n")

                    if symbol.signature:
                        output.append(f"\n**Signature:**\n```{symbol.language}\n{symbol.signature}\n```\n")

                    if symbol.documentation:
                        output.append(f"\n**Documentation:**\n{symbol.documentation}\n")

                    if symbol.is_exported:
                        output.append(f"\n**Exported:** Yes\n")

                    if symbol.metadata:
                        output.append(f"\n**Metadata:**\n")
                        for key, value in symbol.metadata.items():
                            output.append(f"- {key}: {value}\n")

                    # Show other matches if any
                    if len(matching) > 1:
                        output.append(f"\n---\n\n**Note:** Found {len(matching)} symbols with this name. Showing details for the first match.\n")
                        output.append("\nOther matches:\n")
                        for other in matching[1:]:
                            output.append(f"- {other.file_path}")
                            if other.line_start:
                                output.append(f":{other.line_start}")
                            output.append("\n")

                    return [TextContent(type="text", text="".join(output))]
            except Exception as e:
                return [TextContent(type="text", text=f"Error getting symbol details: {str(e)}")]

        elif name == "repo-ctx-get-file-symbols":
            from pathlib import Path
            from .analysis import CodeAnalyzer
            import json

            file_path = arguments["filePath"]
            group_by_type = arguments.get("groupByType", True)
            output_format = arguments.get("outputFormat", "text")

            try:
                path_obj = Path(file_path)

                if not path_obj.exists():
                    return [TextContent(type="text", text=f"Error: File '{file_path}' does not exist")]

                if not path_obj.is_file():
                    return [TextContent(type="text", text=f"Error: '{file_path}' is not a file")]

                analyzer = CodeAnalyzer()

                # Detect language
                language = analyzer.detect_language(str(path_obj))
                if not language:
                    return [TextContent(type="text", text=f"Error: Unsupported file type for '{file_path}'")]

                # Read and analyze
                with open(path_obj, 'r', encoding='utf-8') as f:
                    code = f.read()

                symbols = analyzer.analyze_file(code, str(path_obj))

                if not symbols:
                    return [TextContent(type="text", text=f"No symbols found in '{file_path}'")]

                # Format output based on outputFormat
                if output_format in ["json", "yaml"]:
                    output_data = {
                        "file": file_path,
                        "language": language,
                        "total_symbols": len(symbols),
                        "symbols": [
                            {
                                "name": s.name,
                                "type": s.symbol_type.value,
                                "line": s.line_start,
                                "line_end": s.line_end,
                                "signature": s.signature,
                                "visibility": s.visibility,
                                "qualified_name": s.qualified_name,
                                "documentation": s.documentation
                            }
                            for s in sorted(symbols, key=lambda s: s.line_start or 0)
                        ]
                    }
                    if group_by_type:
                        # Also include grouped view
                        by_type = {}
                        for s in symbols:
                            stype = s.symbol_type.value
                            if stype not in by_type:
                                by_type[stype] = []
                            by_type[stype].append(s.name)
                        output_data["symbols_by_type"] = by_type

                    if output_format == "json":
                        return [TextContent(type="text", text=json.dumps(output_data, indent=2))]
                    else:  # yaml
                        import yaml
                        return [TextContent(type="text", text=yaml.dump(output_data, default_flow_style=False, sort_keys=False))]
                else:
                    # Text output
                    output = []
                    output.append(f"# Symbols in {file_path}\n\n")
                    output.append(f"**Language:** {language}\n")
                    output.append(f"**Total symbols:** {len(symbols)}\n\n")

                    if group_by_type:
                        # Group by symbol type
                        by_type = {}
                        for symbol in symbols:
                            stype = symbol.symbol_type.value
                            if stype not in by_type:
                                by_type[stype] = []
                            by_type[stype].append(symbol)

                        for stype, type_symbols in sorted(by_type.items()):
                            output.append(f"## {stype.title()}s ({len(type_symbols)})\n\n")
                            for symbol in sorted(type_symbols, key=lambda s: s.line_start or 0):
                                visibility_marker = "🔒" if symbol.visibility == "private" else "🔓"
                                output.append(f"- {visibility_marker} **{symbol.name}**")
                                if symbol.line_start:
                                    output.append(f" (Line {symbol.line_start})")
                                output.append("\n")
                                if symbol.signature:
                                    output.append(f"  - Signature: `{symbol.signature}`\n")
                                if symbol.documentation:
                                    # Truncate long docs
                                    doc = symbol.documentation[:100] + "..." if len(symbol.documentation) > 100 else symbol.documentation
                                    output.append(f"  - {doc}\n")
                            output.append("\n")
                    else:
                        # Flat list
                        for symbol in sorted(symbols, key=lambda s: s.line_start or 0):
                            visibility_marker = "🔒" if symbol.visibility == "private" else "🔓"
                            output.append(f"- {visibility_marker} **{symbol.name}** ({symbol.symbol_type.value})")
                            if symbol.line_start:
                                output.append(f" - Line {symbol.line_start}")
                            if symbol.signature:
                                output.append(f" - `{symbol.signature}`")
                            output.append("\n")

                    return [TextContent(type="text", text="".join(output))]
            except UnicodeDecodeError:
                return [TextContent(type="text", text=f"Error: Cannot read '{file_path}' - not a text file")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error analyzing file: {str(e)}")]

        elif name == "repo-ctx-dependency-graph":
            from pathlib import Path
            from .analysis import CodeAnalyzer, DependencyGraph, GraphType
            import os

            path = arguments.get("path")
            repo_id = arguments.get("repoId")
            graph_type_str = arguments.get("graphType", "class")
            max_depth = arguments.get("depth")
            output_format = arguments.get("outputFormat", "json")

            try:
                analyzer = CodeAnalyzer()
                graph_builder = DependencyGraph()
                all_symbols = []
                all_dependencies = []
                source_info = path or repo_id or "unknown"
                repository_info = None

                # Determine graph type
                graph_type_map = {
                    "file": GraphType.FILE,
                    "module": GraphType.MODULE,
                    "class": GraphType.CLASS,
                    "function": GraphType.FUNCTION,
                    "symbol": GraphType.SYMBOL
                }
                graph_type = graph_type_map.get(graph_type_str, GraphType.CLASS)

                # Check if using indexed repo
                if repo_id:
                    symbols, lib, error = await get_or_analyze_repo(context, repo_id)

                    if error:
                        return [TextContent(type="text", text=f"Error: {error}")]

                    if not symbols:
                        # Return empty graph
                        empty_result = {"graph": {"nodes": {}, "edges": []}}
                        return [TextContent(type="text", text=json.dumps(empty_result, indent=2))]

                    all_symbols = symbols
                    source_info = f"{repo_id} (indexed)"

                    # Get repository info
                    group, project = parse_repo_id(repo_id)
                    lib_obj = await context.storage.get_library(group, project)
                    if lib_obj:
                        repository_info = {
                            "id": repo_id,
                            "provider": lib_obj.provider,
                            "group": group,
                            "project": project
                        }

                elif path:
                    # Use local path
                    path_obj = Path(path)

                    if not path_obj.exists():
                        return [TextContent(type="text", text=f"Error: Path '{path}' does not exist")]

                    # Collect files
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

                    if not files:
                        # Return empty graph
                        empty_result = {"graph": {"nodes": {}, "edges": []}}
                        return [TextContent(type="text", text=json.dumps(empty_result, indent=2))]

                    # Analyze files
                    results = analyzer.analyze_files(files)
                    all_symbols = analyzer.aggregate_symbols(results)

                    # Extract dependencies (pass symbols for call extraction)
                    for file_path, code in files.items():
                        file_symbols = results.get(file_path, [])
                        deps = analyzer.extract_dependencies(code, file_path, file_symbols)
                        all_dependencies.extend(deps)

                    source_info = path

                else:
                    return [TextContent(type="text", text="Error: Either 'path' or 'repoId' must be provided")]

                # Build the graph
                result = graph_builder.build(
                    symbols=all_symbols,
                    dependencies=all_dependencies,
                    graph_type=graph_type,
                    graph_id=source_info,
                    graph_label=f"Dependency Graph: {source_info}",
                    max_depth=max_depth,
                    repository_info=repository_info
                )

                # Output based on format
                if output_format == "dot":
                    return [TextContent(type="text", text=graph_builder.to_dot(result))]
                elif output_format == "graphml":
                    return [TextContent(type="text", text=graph_builder.to_graphml(result))]
                else:
                    return [TextContent(type="text", text=graph_builder.to_json(result))]

            except Exception as e:
                return [TextContent(type="text", text=f"Error generating dependency graph: {str(e)}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
