"""Entry point for repo-ctx."""
import asyncio
import argparse
import sys
from datetime import datetime
from .mcp_server import serve
from .core import GitLabContext, RepositoryContext
from .config import Config


def main():
    parser = argparse.ArgumentParser(
        description="Repository Context - Repository documentation indexer and search tool",
        epilog="""
Configuration priority (highest to lowest):
  1. Command-line arguments (--gitlab-url, --gitlab-token, etc.)
  2. Specified config file (--config)
  3. Environment variables (GITLAB_URL, GITLAB_TOKEN)
  4. Standard config locations (~/.config/repo-ctx/config.yaml, ~/.repo-ctx/config.yaml, ./config.yaml)

Examples:
  # Start MCP server
  repo-ctx

  # Index a repository
  repo-ctx --index mygroup/myproject

  # Search for repositories
  repo-ctx search "python"

  # List all indexed repositories
  repo-ctx list

  # Get documentation
  repo-ctx docs mygroup/myproject --topic api
        """
    )

    # Config file
    parser.add_argument(
        "--config",
        help="Path to config.yaml file (optional if using environment variables or CLI args)"
    )

    # Direct configuration arguments
    parser.add_argument(
        "--gitlab-url",
        help="GitLab instance URL (e.g., https://gitlab.com)"
    )
    parser.add_argument(
        "--gitlab-token",
        help="GitLab personal access token"
    )
    parser.add_argument(
        "--github-url",
        help="GitHub API URL (default: https://api.github.com)"
    )
    parser.add_argument(
        "--github-token",
        help="GitHub personal access token (optional for public repos)"
    )
    parser.add_argument(
        "--storage-path",
        help="Path to SQLite database file (default: ~/.repo-ctx/context.db)"
    )

    # Provider selection
    parser.add_argument(
        "--provider",
        choices=["gitlab", "github", "local", "auto"],
        default="auto",
        help="Provider to use (default: auto-detect from path format)"
    )

    # Legacy action (for backwards compatibility)
    parser.add_argument(
        "--index",
        help="Index a repository (format: group/project or owner/repo)"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser(
        "search",
        help="Search for repositories"
    )
    search_parser.add_argument(
        "query",
        help="Search query"
    )
    search_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)"
    )
    search_parser.add_argument(
        "--repo",
        help="Search only in specific repository (format: group/project)"
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all indexed repositories"
    )
    list_parser.add_argument(
        "--format",
        choices=["simple", "detailed"],
        default="detailed",
        help="Output format (default: detailed)"
    )
    list_parser.add_argument(
        "--provider",
        choices=["local", "github", "gitlab"],
        help="Filter by provider (local, github, or gitlab)"
    )

    # Docs command
    docs_parser = subparsers.add_parser(
        "docs",
        help="Get documentation for a repository"
    )
    docs_parser.add_argument(
        "repository",
        help="Repository path (format: group/project or group/project/version)"
    )
    docs_parser.add_argument(
        "--topic",
        help="Filter by topic"
    )
    docs_parser.add_argument(
        "--page",
        type=int,
        default=1,
        help="Page number (default: 1, ignored if --max-tokens used)"
    )
    docs_parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens to return (recommended for LLM context management)"
    )
    docs_parser.add_argument(
        "--show-metadata",
        action="store_true",
        help="Show per-document metadata (quality scores, types, reading time)"
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze code structure and extract symbols"
    )
    analyze_parser.add_argument(
        "path",
        help="Path to local directory/file or remote repository (e.g., owner/repo for GitHub)"
    )
    analyze_parser.add_argument(
        "--output",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format: text (human-readable), json (structured), yaml (structured)"
    )
    analyze_parser.add_argument(
        "--show-dependencies",
        action="store_true",
        help="Show dependency graph"
    )
    analyze_parser.add_argument(
        "--show-callgraph",
        action="store_true",
        help="Show call graph"
    )
    analyze_parser.add_argument(
        "--filter-type",
        choices=["function", "class", "method", "interface", "enum"],
        help="Filter by symbol type"
    )
    analyze_parser.add_argument(
        "--language",
        choices=["python", "javascript", "typescript", "java", "kotlin"],
        help="Filter by programming language"
    )

    # Search-symbol command
    search_symbol_parser = subparsers.add_parser(
        "search-symbol",
        help="Search for symbols by name pattern"
    )
    search_symbol_parser.add_argument(
        "path",
        help="Path to local directory/file to search"
    )
    search_symbol_parser.add_argument(
        "query",
        help="Symbol name or pattern to search for"
    )
    search_symbol_parser.add_argument(
        "--output",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format"
    )
    search_symbol_parser.add_argument(
        "--filter-type",
        choices=["function", "class", "method", "interface", "enum"],
        help="Filter by symbol type"
    )
    search_symbol_parser.add_argument(
        "--language",
        choices=["python", "javascript", "typescript", "java", "kotlin"],
        help="Filter by programming language"
    )

    # Symbol-detail command
    symbol_detail_parser = subparsers.add_parser(
        "symbol-detail",
        help="Get detailed information about a specific symbol"
    )
    symbol_detail_parser.add_argument(
        "path",
        help="Path to local directory/file"
    )
    symbol_detail_parser.add_argument(
        "symbol_name",
        help="Exact symbol name or qualified name (e.g., 'MyClass.method')"
    )
    symbol_detail_parser.add_argument(
        "--output",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format"
    )

    # File-symbols command
    file_symbols_parser = subparsers.add_parser(
        "file-symbols",
        help="List all symbols in a specific file"
    )
    file_symbols_parser.add_argument(
        "file_path",
        help="Path to the source file"
    )
    file_symbols_parser.add_argument(
        "--output",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format"
    )
    file_symbols_parser.add_argument(
        "--group-by-type",
        action="store_true",
        default=True,
        help="Group symbols by type (default: true)"
    )

    args = parser.parse_args()

    # Handle legacy --index argument
    if args.index:
        asyncio.run(index_repository(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path,
            repo=args.index,
            provider=args.provider if args.provider != "auto" else None
        ))
        return

    # Handle subcommands
    if args.command == "search":
        asyncio.run(search_command(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path,
            query=args.query,
            limit=args.limit,
            repo=args.repo
        ))
    elif args.command == "list":
        asyncio.run(list_command(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path,
            format_type=args.format,
            provider=args.provider
        ))
    elif args.command == "docs":
        asyncio.run(docs_command(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path,
            repository=args.repository,
            topic=args.topic,
            page=args.page,
            max_tokens=args.max_tokens,
            show_metadata=args.show_metadata
        ))
    elif args.command == "analyze":
        # Load config for potential remote repository access
        from .config import Config
        config = Config.load(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path
        )

        asyncio.run(analyze_command(
            path=args.path,
            output=args.output,
            show_dependencies=args.show_dependencies,
            show_callgraph=args.show_callgraph,
            filter_type=args.filter_type,
            language=args.language,
            provider_type=args.provider if args.provider != "auto" else None,
            config=config
        ))
    elif args.command == "search-symbol":
        asyncio.run(search_symbol_command(
            path=args.path,
            query=args.query,
            output=args.output,
            filter_type=args.filter_type,
            language=args.language
        ))
    elif args.command == "symbol-detail":
        asyncio.run(symbol_detail_command(
            path=args.path,
            symbol_name=args.symbol_name,
            output=args.output
        ))
    elif args.command == "file-symbols":
        asyncio.run(file_symbols_command(
            file_path=args.file_path,
            output=args.output,
            group_by_type=args.group_by_type
        ))
    else:
        # Server mode (default)
        asyncio.run(serve(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            github_url=args.github_url,
            github_token=args.github_token,
            storage_path=args.storage_path
        ))


async def index_repository(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    github_url: str = None,
    github_token: str = None,
    storage_path: str = None,
    repo: str = None,
    provider: str = None
):
    """Index a repository."""
    from .providers.detector import ProviderDetector

    # Auto-detect provider type to determine if it's a local path
    detected_provider = ProviderDetector.detect(repo)

    # For local paths, don't split - use the full path
    if detected_provider == "local" or provider == "local" or repo.startswith(("/", "./", "~/")):
        group = repo
        project = ""
    else:
        # For remote repos, split into group/project
        parts = repo.split("/")
        if len(parts) < 2:
            print("Error: Repository must be in format group/project or owner/repo")
            return
        # Handle nested groups: everything except last part is the group
        project = parts[-1]
        group = "/".join(parts[:-1])

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
        # For local provider, configuration error is OK (no URL/token needed)
        if provider == "local" or detected_provider == "local":
            config = Config(storage_path=storage_path or Config._default_storage_path())
        else:
            print(f"Configuration error: {e}")
            return

    context = RepositoryContext(config)
    await context.init()

    # Show which provider will be used
    if provider:
        print(f"Using provider: {provider}")
    else:
        print(f"Auto-detecting provider from path format...")

    print(f"Indexing {repo}...")
    try:
        await context.index_repository(group, project, provider_type=provider)
        print(f"✓ Successfully indexed {repo}")
    except Exception as e:
        print(f"✗ Error indexing repository: {e}")


async def search_command(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    github_url: str = None,
    github_token: str = None,
    storage_path: str = None,
    query: str = None,
    limit: int = 10,
    repo: str = None
):
    """Search for repositories."""
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
        return

    context = GitLabContext(config)
    await context.init()

    print(f"Searching for '{query}'...\n")

    try:
        results = await context.fuzzy_search_libraries(query, limit=limit)

        if not results:
            print("No results found.")
            return

        # Filter by repo if specified
        if repo:
            results = [r for r in results if repo.lower() in r.library_id.lower()]

        if not results:
            print(f"No results found matching repository '{repo}'.")
            return

        print(f"Found {len(results)} result(s):\n")

        for i, result in enumerate(results, 1):
            match_icon = {
                "exact": "🎯",
                "starts_with": "▶️",
                "contains": "📝",
                "fuzzy": "🔍"
            }.get(result.match_type, "")

            print(f"{i}. {match_icon} {result.name}")
            print(f"   Library: /{result.group}/{result.name}")
            print(f"   Score: {result.score:.2f} ({result.match_type} match in {result.matched_field})")
            if result.description:
                desc = result.description[:80] + "..." if len(result.description) > 80 else result.description
                print(f"   {desc}")
            print()

    except Exception as e:
        print(f"Search error: {e}")


async def list_command(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    github_url: str = None,
    github_token: str = None,
    storage_path: str = None,
    format_type: str = "detailed",
    provider: str = None
):
    """List all indexed repositories."""
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
        return

    context = GitLabContext(config)
    await context.init()

    try:
        # Use the new list_all_libraries method with provider filtering
        libraries = await context.list_all_libraries(provider_filter=provider)

        if not libraries:
            if provider:
                print(f"No indexed repositories found for provider '{provider}'.")
            else:
                print("No indexed repositories found.")
            print("\nTo index a repository, run:")
            print("  repo-ctx --index group/project")
            return

        if provider:
            print(f"Indexed Repositories ({provider} provider, {len(libraries)} total):\n")
        else:
            print(f"Indexed Repositories ({len(libraries)}):\n")

        if format_type == "simple":
            for lib in libraries:
                # Clean up path display
                path = _format_repo_path(lib.group_name, lib.project_name)
                print(f"  - {path}")
        else:  # detailed
            for i, lib in enumerate(libraries, 1):
                # Clean up path display
                path = _format_repo_path(lib.group_name, lib.project_name)
                print(f"{i}. {path}")

                # Show URL or file path
                url = context._get_repository_url(lib)
                print(f"   URL: {url}")

                if lib.description:
                    # Clean HTML/markdown tags and truncate
                    desc = _clean_description(lib.description)
                    if len(desc) > 100:
                        desc = desc[:97] + "..."
                    print(f"   Description: {desc}")
                print(f"   Default version: {lib.default_version}")

                # Format last indexed time
                if lib.last_indexed:
                    if isinstance(lib.last_indexed, str):
                        # Parse from database timestamp string
                        try:
                            dt = datetime.fromisoformat(lib.last_indexed.replace(' ', 'T'))
                            time_ago = format_time_ago(dt)
                            print(f"   Last indexed: {dt.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})")
                        except:
                            print(f"   Last indexed: {lib.last_indexed}")
                    else:
                        time_ago = format_time_ago(lib.last_indexed)
                        print(f"   Last indexed: {lib.last_indexed.strftime('%Y-%m-%d %H:%M:%S')} ({time_ago})")
                print()

    except Exception as e:
        print(f"List error: {e}")


async def docs_command(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    github_url: str = None,
    github_token: str = None,
    storage_path: str = None,
    repository: str = None,
    topic: str = None,
    page: int = 1,
    max_tokens: int = None,
    show_metadata: bool = False
):
    """Get documentation for a repository."""
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
        return

    context = GitLabContext(config)
    await context.init()

    # Ensure repository starts with /
    if not repository.startswith("/"):
        repository = f"/{repository}"

    try:
        print(f"Retrieving documentation for {repository}...")
        if topic:
            print(f"Filtering by topic: {topic}")
        if max_tokens:
            print(f"Limiting to {max_tokens:,} tokens")
        print()

        docs = await context.get_documentation(
            repository,
            topic=topic,
            page=page,
            max_tokens=max_tokens
        )

        metadata = docs["metadata"]
        content = docs["content"][0]["text"]

        print(f"Library: {metadata['library']}")
        print(f"Version: {metadata['version']}")
        print(f"Documents: {metadata['documents_count']}", end="")

        if max_tokens and 'documents_available' in metadata:
            print(f" (of {metadata['documents_available']} available)")
        else:
            print()

        print(f"Tokens: {metadata['tokens']:,}")

        if max_tokens:
            print(f"Limit: {metadata['max_tokens']:,} tokens")
        else:
            print(f"Page: {metadata['page']}")

        print("=" * 80)
        print()

        # Show per-document metadata if requested
        if show_metadata and 'documents_metadata' in metadata:
            print("Document Metadata:")
            print()
            for doc_meta in metadata['documents_metadata']:
                print(f"  📄 {doc_meta['file_path']}")
                print(f"     Type: {doc_meta['document_type'].title()} | "
                      f"Quality: {doc_meta['quality_score']}/100 | "
                      f"Reading time: {doc_meta['reading_time']} min | "
                      f"Code examples: {doc_meta['snippet_count']}")
            print()
            print("=" * 80)
            print()

        print(content)

        # Pagination hint
        if not max_tokens and metadata['documents_count'] >= 10:
            print()
            print(f"More documents available. Use --page {page + 1} to see next page.")
            print(f"Or use --max-tokens to control output size (e.g., --max-tokens 8000)")

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Documentation retrieval error: {e}")


def format_time_ago(dt: datetime) -> str:
    """Format datetime as human-readable time ago."""
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = int(seconds / 31536000)
        return f"{years} year{'s' if years != 1 else ''} ago"


def _format_repo_path(group_name: str, project_name: str) -> str:
    """Format repository path for display.

    Args:
        group_name: Group/organization or full path for local repos
        project_name: Project/repository name (empty for local repos)

    Returns:
        Cleaned path string
    """
    if project_name:
        # Remote repo: group/project
        path = f"{group_name}/{project_name}"
    else:
        # Local repo: group_name contains full path
        path = group_name

    # Remove trailing slashes
    path = path.rstrip('/')

    return path


def _clean_description(description: str) -> str:
    """Clean description by removing HTML/markdown tags and extra whitespace.

    Args:
        description: Raw description text

    Returns:
        Cleaned description
    """
    import re

    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', description)

    # Remove markdown links: [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove markdown bold/italic: **text** or *text* -> text
    text = re.sub(r'\*+([^\*]+)\*+', r'\1', text)

    # Remove markdown heading markers
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)

    # Collapse multiple whitespace into single space
    text = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text


async def analyze_command(
    path: str,
    output: str = "text",
    show_dependencies: bool = False,
    show_callgraph: bool = False,
    filter_type: str = None,
    language: str = None,
    provider_type: str = None,
    config: 'Config' = None
):
    """Analyze code structure and extract symbols."""
    import os
    import json
    from pathlib import Path
    from .analysis import CodeAnalyzer, SymbolType

    analyzer = CodeAnalyzer()
    path_obj = Path(path)

    # Collect files to analyze
    files = {}

    # Check if this is a local path or a repository identifier
    is_local_path = path_obj.exists() or path.startswith(('/', './', '~/', '../'))

    if is_local_path:
        # Local file/directory analysis
        if path_obj.is_file():
            # Single file
            if analyzer.detect_language(str(path_obj)):
                with open(path_obj, 'r') as f:
                    files[str(path_obj)] = f.read()
        elif path_obj.is_dir():
            # Directory - recursively collect source files
            for root, _, filenames in os.walk(path_obj):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if analyzer.detect_language(filename):
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                files[file_path] = f.read()
                        except (UnicodeDecodeError, PermissionError):
                            continue
        else:
            print(f"Error: Path '{path}' does not exist")
            return
    else:
        # Repository identifier (e.g., owner/repo or group/project)
        # Try to fetch from provider
        print(f"Fetching repository '{path}' from remote...")
        from .providers.detector import ProviderDetector
        from .providers import ProviderFactory

        # Detect provider if not specified
        if not provider_type:
            provider_type = ProviderDetector.detect(path)

        # Parse repository path
        if provider_type == "local":
            print(f"Error: Path '{path}' does not exist locally")
            return

        parts = path.split("/")
        if len(parts) < 2:
            print(f"Error: Invalid repository path '{path}'. Expected format: owner/repo or group/project")
            return

        # Load config for provider if not provided
        if not config:
            from .config import Config
            try:
                config = Config.load(provider_type=provider_type)
            except Exception as e:
                print(f"Error: Could not load configuration for {provider_type}: {e}")
                print(f"\nTo analyze a remote repository, you need to either:")
                print(f"1. Clone it locally first: git clone <url> && repo-ctx analyze <local-path>")
                print(f"2. Configure {provider_type} credentials (see documentation)")
                return

        # Get provider
        try:
            provider = ProviderFactory.from_config(config, provider_type)

            # Fetch repository project info
            project_info = await provider.get_project(path)

            # Get default branch
            ref = await provider.get_default_branch(project_info)

            # Fetch file tree
            file_paths = await provider.get_file_tree(project_info, ref)

            # Fetch source files
            for file_path in file_paths:
                if analyzer.detect_language(file_path):
                    try:
                        file_content = await provider.read_file(project_info, file_path, ref)
                        files[file_path] = file_content.content
                    except Exception as e:
                        if output != "json":
                            print(f"Warning: Could not read {file_path}: {e}")
                        continue

            if output != "json" and files:
                print(f"Fetched {len(files)} source file(s) from {path}")

        except Exception as e:
            print(f"Error fetching repository: {e}")
            print(f"\nTip: For local analysis, clone first: git clone <url> && repo-ctx analyze <path>")
            return

    if not files:
        print(f"No supported source files found in '{path}'")
        print(f"Supported languages: {', '.join(analyzer.get_supported_languages())}")
        return

    # Analyze all files
    if output == "text":
        print(f"Analyzing {len(files)} file(s)...")
    results = analyzer.analyze_files(files)

    # Aggregate all symbols
    all_symbols = analyzer.aggregate_symbols(results)

    # Apply filters
    if filter_type:
        all_symbols = analyzer.filter_symbols_by_type(all_symbols, SymbolType(filter_type))

    if language:
        all_symbols = [s for s in all_symbols if s.language == language]

    # Get statistics
    stats = analyzer.get_statistics(all_symbols)

    # Output results
    if output in ["json", "yaml"]:
        # Structured output (JSON or YAML)
        output_data = {
            "path": str(path),
            "files_analyzed": len(files),
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
        if output == "json":
            print(json.dumps(output_data, indent=2))
        else:  # yaml
            import yaml
            print(yaml.dump(output_data, default_flow_style=False, sort_keys=False))
    else:
        # Text output
        print(f"\n{'='*80}")
        print(f"Code Analysis Results: {path}")
        print(f"{'='*80}\n")

        print(f"Files analyzed: {len(files)}")
        print(f"Total symbols: {stats['total_symbols']}\n")

        print("Symbols by type:")
        for sym_type, count in stats['by_type'].items():
            print(f"  {sym_type:15} {count:5}")

        if stats['by_language']:
            print("\nSymbols by language:")
            for lang, count in stats['by_language'].items():
                print(f"  {lang:15} {count:5}")

        print(f"\n{'='*80}")
        print("Symbol Details:")
        print(f"{'='*80}\n")

        # Group symbols by file
        by_file = {}
        for symbol in all_symbols:
            if symbol.file_path not in by_file:
                by_file[symbol.file_path] = []
            by_file[symbol.file_path].append(symbol)

        for file_path, symbols in sorted(by_file.items()):
            print(f"\n📄 {file_path}")
            for symbol in sorted(symbols, key=lambda s: s.line_start):
                vis_icon = "🔒" if symbol.visibility == "private" else "🔓"
                type_icon = {
                    "function": "⚡",
                    "method": "🔧",
                    "class": "📦",
                    "interface": "📋",
                    "enum": "🔢"
                }.get(symbol.symbol_type.value, "•")

                print(f"  {type_icon} {vis_icon} {symbol.name} ({symbol.symbol_type.value})")
                print(f"     Line {symbol.line_start} | {symbol.signature or 'N/A'}")
                if symbol.documentation:
                    doc_preview = symbol.documentation[:60] + "..." if len(symbol.documentation) > 60 else symbol.documentation
                    print(f"     📖 {doc_preview}")

        if show_dependencies:
            print(f"\n{'='*80}")
            print("Dependencies (Imports):")
            print(f"{'='*80}\n")

            # Extract dependencies for all files
            all_deps = []
            for file_path, code in files.items():
                file_deps = analyzer.extract_dependencies(code, file_path)
                all_deps.extend(file_deps)

            if all_deps:
                # Group by source file
                by_source = {}
                for dep in all_deps:
                    src = dep.get('source', 'unknown')
                    if src not in by_source:
                        by_source[src] = []
                    by_source[src].append(dep)

                for source_file, deps in sorted(by_source.items()):
                    print(f"📄 {source_file}")
                    for dep in sorted(deps, key=lambda d: d.get('line', 0)):
                        target = dep.get('target', 'unknown')
                        line = dep.get('line', '')
                        is_external = dep.get('is_external', True)
                        icon = "📦" if is_external else "📂"
                        print(f"   {icon} → {target}", end="")
                        if line:
                            print(f" (line {line})", end="")
                        print()
                    print()
            else:
                print("No dependencies found.")

        if show_callgraph:
            print(f"\n{'='*80}")
            print("Call Graph:")
            print(f"{'='*80}\n")
            print("Note: Call graph extraction requires deeper static analysis.")
            print("Currently showing function/method call patterns from symbols.\n")

            # Basic call pattern display based on method relationships
            methods = [s for s in all_symbols if s.symbol_type.value in ('method', 'function')]
            classes = [s for s in all_symbols if s.symbol_type.value == 'class']

            if classes:
                for cls in classes:
                    class_methods = [s for s in methods
                                    if s.qualified_name and s.qualified_name.startswith(cls.name + ".")]
                    if class_methods:
                        print(f"📦 {cls.name}")
                        for method in sorted(class_methods, key=lambda s: s.line_start or 0):
                            visibility = "🔒" if method.visibility == "private" else "🔓"
                            print(f"   {visibility} {method.name}")
                        print()

            standalone_funcs = [s for s in methods
                               if not s.qualified_name or "." not in s.qualified_name]
            if standalone_funcs:
                print("⚡ Standalone Functions")
                for func in sorted(standalone_funcs, key=lambda s: s.line_start or 0):
                    print(f"   {func.name}")


async def search_symbol_command(
    path: str,
    query: str,
    output: str = "text",
    filter_type: str = None,
    language: str = None
):
    """Search for symbols by name pattern."""
    import os
    import json
    from pathlib import Path
    from .analysis import CodeAnalyzer, SymbolType

    analyzer = CodeAnalyzer()
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"Error: Path '{path}' does not exist")
        return

    # Collect files
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
        print(f"No supported source files found in '{path}'")
        return

    # Analyze and search
    results = analyzer.analyze_files(files)
    all_symbols = analyzer.aggregate_symbols(results)

    # Search by name (case-insensitive substring match)
    query_lower = query.lower()
    matching = [s for s in all_symbols if query_lower in s.name.lower()]

    # Apply filters
    if filter_type:
        matching = analyzer.filter_symbols_by_type(matching, SymbolType(filter_type))
    if language:
        matching = [s for s in matching if s.language == language]

    # Output results
    if output in ["json", "yaml"]:
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
        if output == "json":
            print(json.dumps(output_data, indent=2))
        else:
            import yaml
            print(yaml.dump(output_data, default_flow_style=False, sort_keys=False))
    else:
        print(f"Search results for '{query}':\n")
        print(f"Found {len(matching)} matching symbol(s)\n")

        if matching:
            for symbol in sorted(matching, key=lambda s: (s.file_path, s.line_start or 0)):
                vis_icon = "🔒" if symbol.visibility == "private" else "🔓"
                type_icon = {
                    "function": "⚡",
                    "method": "🔧",
                    "class": "📦",
                    "interface": "📋",
                    "enum": "🔢"
                }.get(symbol.symbol_type.value, "•")

                print(f"{type_icon} {vis_icon} {symbol.name} ({symbol.symbol_type.value})")
                print(f"   File: {symbol.file_path}:{symbol.line_start or 0}")
                if symbol.signature:
                    print(f"   Signature: {symbol.signature}")
                if symbol.documentation:
                    doc_preview = symbol.documentation[:60] + "..." if len(symbol.documentation) > 60 else symbol.documentation
                    print(f"   📖 {doc_preview}")
                print()
        else:
            print(f"No symbols found matching '{query}'")


async def symbol_detail_command(
    path: str,
    symbol_name: str,
    output: str = "text"
):
    """Get detailed information about a specific symbol."""
    import os
    import json
    from pathlib import Path
    from .analysis import CodeAnalyzer

    analyzer = CodeAnalyzer()
    path_obj = Path(path)

    if not path_obj.exists():
        print(f"Error: Path '{path}' does not exist")
        return

    # Collect files
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
        print(f"No supported source files found in '{path}'")
        return

    # Analyze and find symbol
    results = analyzer.analyze_files(files)
    all_symbols = analyzer.aggregate_symbols(results)

    # Find by exact name or qualified name
    matching = [s for s in all_symbols
                if s.name == symbol_name or s.qualified_name == symbol_name]

    if not matching:
        print(f"Symbol '{symbol_name}' not found")
        return

    symbol = matching[0]

    # Output results
    if output in ["json", "yaml"]:
        output_data = {
            "name": symbol.name,
            "type": symbol.symbol_type.value,
            "file": symbol.file_path,
            "line_start": symbol.line_start,
            "line_end": symbol.line_end,
            "signature": symbol.signature,
            "visibility": symbol.visibility,
            "language": symbol.language,
            "qualified_name": symbol.qualified_name,
            "documentation": symbol.documentation,
            "is_exported": symbol.is_exported,
            "metadata": symbol.metadata
        }
        if len(matching) > 1:
            output_data["other_matches"] = [
                {"file": s.file_path, "line": s.line_start}
                for s in matching[1:]
            ]
        if output == "json":
            print(json.dumps(output_data, indent=2))
        else:
            import yaml
            print(yaml.dump(output_data, default_flow_style=False, sort_keys=False))
    else:
        print(f"Symbol Detail: {symbol.name}\n")
        print(f"{'='*60}")
        print(f"Type:           {symbol.symbol_type.value}")
        print(f"Language:       {symbol.language}")
        print(f"File:           {symbol.file_path}")
        if symbol.line_start:
            if symbol.line_end:
                print(f"Location:       Lines {symbol.line_start}-{symbol.line_end}")
            else:
                print(f"Location:       Line {symbol.line_start}")
        print(f"Visibility:     {symbol.visibility}")
        if symbol.qualified_name:
            print(f"Qualified Name: {symbol.qualified_name}")
        if symbol.signature:
            print(f"\nSignature:\n  {symbol.signature}")
        if symbol.documentation:
            print(f"\nDocumentation:\n  {symbol.documentation}")
        if symbol.is_exported:
            print(f"\nExported: Yes")
        if symbol.metadata:
            print(f"\nMetadata:")
            for key, value in symbol.metadata.items():
                print(f"  {key}: {value}")

        if len(matching) > 1:
            print(f"\n{'='*60}")
            print(f"Note: Found {len(matching)} symbols with this name.")
            print("Other matches:")
            for other in matching[1:]:
                print(f"  - {other.file_path}:{other.line_start or 0}")


async def file_symbols_command(
    file_path: str,
    output: str = "text",
    group_by_type: bool = True
):
    """List all symbols in a specific file."""
    import json
    from pathlib import Path
    from .analysis import CodeAnalyzer

    path_obj = Path(file_path)

    if not path_obj.exists():
        print(f"Error: File '{file_path}' does not exist")
        return

    if not path_obj.is_file():
        print(f"Error: '{file_path}' is not a file")
        return

    analyzer = CodeAnalyzer()

    # Detect language
    language = analyzer.detect_language(str(path_obj))
    if not language:
        print(f"Error: Unsupported file type for '{file_path}'")
        print(f"Supported languages: {', '.join(analyzer.get_supported_languages())}")
        return

    # Read and analyze
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            code = f.read()
    except UnicodeDecodeError:
        print(f"Error: Cannot read '{file_path}' - not a text file")
        return

    symbols = analyzer.analyze_file(code, str(path_obj))

    if not symbols:
        print(f"No symbols found in '{file_path}'")
        return

    # Output results
    if output in ["json", "yaml"]:
        output_data = {
            "file": file_path,
            "language": language,
            "total_symbols": len(symbols),
            "symbols": [
                {
                    "name": s.name,
                    "type": s.symbol_type.value,
                    "line": s.line_start,
                    "signature": s.signature,
                    "visibility": s.visibility,
                    "documentation": s.documentation
                }
                for s in sorted(symbols, key=lambda s: s.line_start or 0)
            ]
        }
        if output == "json":
            print(json.dumps(output_data, indent=2))
        else:
            import yaml
            print(yaml.dump(output_data, default_flow_style=False, sort_keys=False))
    else:
        print(f"Symbols in {file_path}\n")
        print(f"Language: {language}")
        print(f"Total symbols: {len(symbols)}\n")
        print(f"{'='*60}")

        if group_by_type:
            # Group by symbol type
            by_type = {}
            for symbol in symbols:
                stype = symbol.symbol_type.value
                if stype not in by_type:
                    by_type[stype] = []
                by_type[stype].append(symbol)

            for stype, type_symbols in sorted(by_type.items()):
                type_icon = {
                    "function": "⚡",
                    "method": "🔧",
                    "class": "📦",
                    "interface": "📋",
                    "enum": "🔢"
                }.get(stype, "•")
                print(f"\n{type_icon} {stype.title()}s ({len(type_symbols)})")
                print("-" * 40)
                for symbol in sorted(type_symbols, key=lambda s: s.line_start or 0):
                    vis_icon = "🔒" if symbol.visibility == "private" else "🔓"
                    print(f"  {vis_icon} {symbol.name}", end="")
                    if symbol.line_start:
                        print(f" (Line {symbol.line_start})", end="")
                    print()
                    if symbol.signature:
                        print(f"      {symbol.signature}")
        else:
            # Flat list
            for symbol in sorted(symbols, key=lambda s: s.line_start or 0):
                vis_icon = "🔒" if symbol.visibility == "private" else "🔓"
                type_icon = {
                    "function": "⚡",
                    "method": "🔧",
                    "class": "📦",
                    "interface": "📋",
                    "enum": "🔢"
                }.get(symbol.symbol_type.value, "•")
                print(f"{type_icon} {vis_icon} {symbol.name} ({symbol.symbol_type.value})", end="")
                if symbol.line_start:
                    print(f" - Line {symbol.line_start}", end="")
                print()


if __name__ == "__main__":
    main()
