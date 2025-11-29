"""Batch command handlers."""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Any, Optional, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markup import escape as rich_escape
from rich import box

console = Console()


def print_error(message: str):
    """Print an error message, escaping any rich markup in the message."""
    console.print(f"[red]Error: {rich_escape(str(message))}[/red]")


def parse_repo_id(repo_id: str) -> Tuple[str, str]:
    """Parse repo_id into (group, project) tuple."""
    clean_id = repo_id.strip("/")
    parts = clean_id.split("/")
    if len(parts) >= 2:
        project = parts[-1]
        group = "/".join(parts[:-1])
        return (group, project)
    return (clean_id, "")


def clone_repo_to_temp(clone_url: str, ref: str = None) -> str:
    """Clone a repository to a temporary directory using shallow clone.

    Args:
        clone_url: Git clone URL (https or ssh)
        ref: Optional branch/tag to checkout

    Returns:
        Path to the cloned repository

    Raises:
        RuntimeError: If clone fails
    """
    import tempfile
    import subprocess

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix="repo_ctx_")

    try:
        # Build clone command - shallow clone for speed
        cmd = ["git", "clone", "--depth", "1"]
        if ref:
            cmd.extend(["--branch", ref])
        cmd.extend([clone_url, temp_dir])

        # Run clone
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )

        if result.returncode != 0:
            # Clean up on failure
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        return temp_dir

    except subprocess.TimeoutExpired:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError("Git clone timed out")


def analyze_local_directory(repo_path: str, analyzer) -> dict:
    """Analyze all code files in a local directory.

    Args:
        repo_path: Path to the repository
        analyzer: CodeAnalyzer instance

    Returns:
        Dictionary of {relative_path: content}
    """
    import os

    files = {}
    for root, dirs, filenames in os.walk(repo_path):
        # Skip .git directory
        if '.git' in dirs:
            dirs.remove('.git')

        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_path)

            # Check if it's a code file we can analyze
            if analyzer.detect_language(rel_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        files[rel_path] = f.read()
                except Exception:
                    continue

    return files


def get_clone_url(provider_type: str, group: str, project: str, config) -> str:
    """Get the clone URL for a repository.

    Args:
        provider_type: 'github', 'gitlab', or 'local'
        group: Repository group/owner
        project: Repository name
        config: Config object

    Returns:
        Clone URL string
    """
    if provider_type == "github":
        # Use HTTPS with token if available
        token = config.github_token if hasattr(config, 'github_token') else None
        if token:
            return f"https://{token}@github.com/{group}/{project}.git"
        return f"https://github.com/{group}/{project}.git"
    elif provider_type == "gitlab":
        base_url = config.gitlab_url if hasattr(config, 'gitlab_url') else "https://gitlab.com"
        base_url = base_url.rstrip('/')
        # Extract host from URL
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.netloc or parsed.path
        token = config.gitlab_token if hasattr(config, 'gitlab_token') else None
        if token:
            return f"https://oauth2:{token}@{host}/{group}/{project}.git"
        return f"https://{host}/{group}/{project}.git"
    else:
        raise ValueError(f"Unsupported provider for clone: {provider_type}")


async def get_or_analyze_repo(repo_id: str, force_refresh: bool = False):
    """Get stored analysis for a repo, or analyze and store it.

    Uses git clone for efficient bulk file loading instead of per-file API calls.
    """
    import shutil
    from ..config import Config
    from ..core import GitLabContext
    from ..analysis import CodeAnalyzer, Symbol, SymbolType
    from ..providers import ProviderFactory

    config = Config.load()
    context = GitLabContext(config)
    await context.init()

    group, project = parse_repo_id(repo_id)
    lib = await context.storage.get_library(group, project)

    if not lib:
        return None, None, f"Repository {repo_id} not found in index. Use 'repo-ctx repo index {repo_id}' first."

    # Check if we have stored symbols
    stored_symbols = await context.storage.search_symbols(lib.id, "")

    if stored_symbols and not force_refresh:
        # Return stored symbols
        symbols = []
        for s in stored_symbols:
            # Parse metadata from JSON string
            metadata = {}
            if s.get('metadata'):
                try:
                    metadata = json.loads(s['metadata']) if isinstance(s['metadata'], str) else s['metadata']
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

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
                metadata=metadata
            ))
        return symbols, lib, None

    # Need to fetch and analyze - use git clone for efficiency
    temp_dir = None
    try:
        analyzer = CodeAnalyzer()

        # For local provider, analyze directly
        if lib.provider == "local":
            repo_path = f"{group}/{project}" if project else group
            files = analyze_local_directory(repo_path, analyzer)
        else:
            # Clone repo to temp directory (single operation, no API rate limits)
            clone_url = get_clone_url(lib.provider, group, project, config)
            temp_dir = clone_repo_to_temp(clone_url)
            files = analyze_local_directory(temp_dir, analyzer)

        if not files:
            return [], lib, None

        # Analyze all files
        analysis_results = analyzer.analyze_files(files)
        symbols = analyzer.aggregate_symbols(analysis_results)

        # Store symbols in database
        await context.storage.save_symbols(symbols, lib.id)

        return symbols, lib, None

    except Exception as e:
        return None, lib, str(e)

    finally:
        # Clean up temp directory
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_command(args):
    """Route and execute the appropriate command."""
    if args.command == "repo":
        asyncio.run(handle_repo_command(args))
    elif args.command == "code":
        asyncio.run(handle_code_command(args))
    elif args.command == "config":
        asyncio.run(handle_config_command(args))
    else:
        console.print(f"[red]Unknown command: {args.command}[/red]")
        sys.exit(1)


# ============================================================================
# REPO COMMANDS
# ============================================================================

async def handle_repo_command(args):
    """Handle repo subcommands."""
    if not args.repo_command:
        console.print("[yellow]Usage: repo-ctx repo <index|search|list|docs>[/yellow]")
        return

    if args.repo_command == "index":
        await repo_index(args)
    elif args.repo_command == "search":
        await repo_search(args)
    elif args.repo_command == "list":
        await repo_list(args)
    elif args.repo_command == "docs":
        await repo_docs(args)


async def repo_index(args):
    """Index a repository."""
    from ..config import Config
    from ..core import GitLabContext

    path = args.path
    provider = args.provider

    try:
        config = Config.load(config_path=args.config)
        context = GitLabContext(config)
        await context.init()

        # Parse path
        if provider == "local" or path.startswith(("/", "./", "~/")):
            group = path
            project = ""
            provider_type = "local"
        else:
            parts = path.split("/")
            if len(parts) < 2:
                console.print("[red]Error: Repository must be in format owner/repo[/red]")
                sys.exit(1)
            project = parts[-1]
            group = "/".join(parts[:-1])
            provider_type = None if provider == "auto" else provider

        await context.index_repository(group, project, provider_type=provider_type)

        if args.output == "json":
            print(json.dumps({"status": "success", "repository": path}))
        else:
            console.print(f"[green]Successfully indexed {path}[/green]")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def repo_search(args):
    """Search for repositories."""
    from ..config import Config
    from ..core import GitLabContext

    try:
        config = Config.load(config_path=args.config)
        context = GitLabContext(config)
        await context.init()

        results = await context.fuzzy_search_libraries(args.query, limit=args.limit)

        if args.output == "json":
            output = {
                "query": args.query,
                "count": len(results),
                "results": [
                    {
                        "id": r.library_id,
                        "name": r.name,
                        "group": r.group,
                        "description": r.description,
                        "score": r.score,
                        "match_type": r.match_type
                    }
                    for r in results
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "query": args.query,
                "count": len(results),
                "results": [
                    {
                        "id": r.library_id,
                        "name": r.name,
                        "description": r.description,
                        "score": r.score
                    }
                    for r in results
                ]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            if not results:
                console.print(f"[yellow]No repositories found matching '{args.query}'[/yellow]")
                return

            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("#", style="dim")
            table.add_column("Repository", style="green")
            table.add_column("Description", style="white")
            table.add_column("Score", style="cyan")

            for i, r in enumerate(results, 1):
                table.add_row(
                    str(i),
                    r.library_id,
                    (r.description or "")[:50],
                    f"{r.score:.0%}"
                )

            console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def repo_list(args):
    """List indexed repositories."""
    from ..config import Config
    from ..core import GitLabContext

    try:
        config = Config.load(config_path=args.config)
        context = GitLabContext(config)
        await context.init()

        provider_filter = args.provider if args.provider != "auto" else None
        libraries = await context.list_all_libraries(provider_filter)

        if args.output == "json":
            output = {
                "count": len(libraries),
                "repositories": [
                    {
                        "id": f"/{lib.group_name}/{lib.project_name}",
                        "name": lib.project_name,
                        "group": lib.group_name,
                        "description": lib.description,
                        "last_indexed": str(lib.last_indexed) if lib.last_indexed else None
                    }
                    for lib in libraries
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "count": len(libraries),
                "repositories": [
                    {
                        "id": f"/{lib.group_name}/{lib.project_name}",
                        "description": lib.description
                    }
                    for lib in libraries
                ]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            if not libraries:
                console.print("[yellow]No repositories indexed yet.[/yellow]")
                console.print("[dim]Use 'repo-ctx repo index <path>' to index repositories.[/dim]")
                return

            table = Table(
                title=f"Indexed Repositories ({len(libraries)})",
                box=box.ROUNDED
            )
            table.add_column("#", style="dim")
            table.add_column("Repository", style="green")
            table.add_column("Description", style="white")
            table.add_column("Last Indexed", style="dim")

            for i, lib in enumerate(libraries, 1):
                table.add_row(
                    str(i),
                    f"/{lib.group_name}/{lib.project_name}",
                    (lib.description or "")[:40],
                    str(lib.last_indexed)[:10] if lib.last_indexed else "-"
                )

            console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def repo_docs(args):
    """Get documentation for a repository."""
    from ..config import Config
    from ..core import GitLabContext

    try:
        config = Config.load(config_path=args.config)
        context = GitLabContext(config)
        await context.init()

        result = await context.get_documentation(
            args.id,
            topic=args.topic,
            page=args.page,
            max_tokens=args.max_tokens
        )

        # If include-code flag is set, append code analysis
        include_code = getattr(args, 'include_code', False)
        force_refresh = getattr(args, 'refresh', False)
        exclude_tests = getattr(args, 'exclude_tests', False)
        code_analysis_data = None

        if include_code:
            from ..analysis import CodeAnalysisReport

            # Get symbols for the repository (force_refresh to re-analyze if requested)
            symbols, lib, error = await get_or_analyze_repo(args.id, force_refresh=force_refresh)

            if not error and symbols:
                # Generate code analysis report (optionally excluding tests)
                report = CodeAnalysisReport(symbols, exclude_tests=exclude_tests)
                code_analysis_data = report.generate_json()

                # Append markdown report to content
                markdown_report = report.generate_markdown(include_mermaid=True)
                result["content"][0]["text"] += f"\n\n---\n\n{markdown_report}"

                # Add to metadata
                if "metadata" not in result:
                    result["metadata"] = {}
                result["metadata"]["code_analysis"] = code_analysis_data

        if args.output == "json":
            print(json.dumps(result, indent=2))
        elif args.output == "yaml":
            import yaml
            print(yaml.dump(result, default_flow_style=False))
        else:
            content = result["content"][0]["text"]
            # Use markup=False to avoid interpreting brackets as Rich markup
            console.print(content, markup=False)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# ============================================================================
# CODE COMMANDS
# ============================================================================

async def handle_code_command(args):
    """Handle code subcommands."""
    if not args.code_command:
        console.print("[yellow]Usage: repo-ctx code <analyze|find|info|symbols|dep>[/yellow]")
        return

    if args.code_command == "analyze":
        await code_analyze(args)
    elif args.code_command == "find":
        await code_find(args)
    elif args.code_command == "info":
        await code_info(args)
    elif args.code_command == "symbols":
        code_symbols(args)
    elif args.code_command == "dep":
        await code_dep(args)


async def code_analyze(args):
    """Analyze code structure."""
    from ..analysis import CodeAnalyzer, SymbolType

    try:
        analyzer = CodeAnalyzer()
        all_symbols = []
        files = {}
        source_info = args.path

        # Check if using indexed repo
        if getattr(args, 'repo', False):
            # Use indexed repository
            force_refresh = getattr(args, 'refresh', False)
            symbols, lib, error = await get_or_analyze_repo(args.path, force_refresh=force_refresh)

            if error:
                if args.output == "json":
                    print(json.dumps({"status": "error", "message": error}))
                else:
                    print_error(error)
                sys.exit(1)

            if not symbols:
                if args.output == "json":
                    print(json.dumps({"path": args.path, "symbols": [], "statistics": {}}))
                else:
                    console.print(f"[yellow]No symbols found in '{args.path}'[/yellow]")
                return

            all_symbols = symbols
            source_info = f"{args.path} (indexed)"

        else:
            # Use local path
            path_obj = Path(args.path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{args.path}' does not exist[/red]")
                sys.exit(1)

            # Collect files
            if path_obj.is_file():
                if analyzer.detect_language(str(path_obj)):
                    with open(path_obj, 'r', encoding='utf-8') as f:
                        files[str(path_obj)] = f.read()
            else:
                for root, _, filenames in os.walk(path_obj):
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        lang = analyzer.detect_language(filename)
                        if lang:
                            if args.lang and lang != args.lang:
                                continue
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    files[file_path] = f.read()
                            except (UnicodeDecodeError, PermissionError):
                                continue

            if not files:
                console.print(f"[yellow]No supported files found in '{args.path}'[/yellow]")
                return

            # Analyze
            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

        # Filter by type
        if args.type:
            all_symbols = analyzer.filter_symbols_by_type(all_symbols, SymbolType(args.type))

        stats = analyzer.get_statistics(all_symbols)

        # Output
        if args.output == "json":
            output = {
                "path": args.path,
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
                        "language": s.language
                    }
                    for s in all_symbols
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "path": args.path,
                "statistics": stats,
                "symbols": [
                    {"name": s.name, "type": s.symbol_type.value, "file": s.file_path}
                    for s in all_symbols
                ]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            console.print(f"[bold]Analysis: {source_info}[/bold]\n")
            if files:
                console.print(f"Files analyzed: {len(files)}")
            console.print(f"Total symbols: {stats['total_symbols']}\n")

            if stats['by_type']:
                table = Table(title="Symbols by Type", box=box.SIMPLE)
                table.add_column("Type", style="cyan")
                table.add_column("Count")
                for stype, count in stats['by_type'].items():
                    table.add_row(stype, str(count))
                console.print(table)

            # Show dependencies if requested (only for local)
            if args.deps and files:
                console.print("\n[bold]Dependencies:[/bold]")
                for file_path, code in files.items():
                    deps = analyzer.extract_dependencies(code, file_path)
                    if deps:
                        console.print(f"\n[cyan]{file_path}[/cyan]")
                        for dep in deps:
                            console.print(f"  → {dep.get('target', 'unknown')}")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def code_find(args):
    """Find symbols by pattern."""
    from ..analysis import CodeAnalyzer, SymbolType

    try:
        analyzer = CodeAnalyzer()
        all_symbols = []
        source_info = args.path

        # Check if using indexed repo
        if getattr(args, 'repo', False):
            symbols, lib, error = await get_or_analyze_repo(args.path)

            if error:
                if args.output == "json":
                    print(json.dumps({"status": "error", "message": error}))
                else:
                    print_error(error)
                sys.exit(1)

            if not symbols:
                if args.output == "json":
                    print(json.dumps({"query": args.query, "count": 0, "symbols": []}))
                else:
                    console.print(f"[yellow]No symbols found in '{args.path}'[/yellow]")
                return

            all_symbols = symbols
            source_info = f"{args.path} (indexed)"

        else:
            # Use local path
            path_obj = Path(args.path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{args.path}' does not exist[/red]")
                sys.exit(1)

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
                        lang = analyzer.detect_language(filename)
                        if lang:
                            if args.lang and lang != args.lang:
                                continue
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    files[file_path] = f.read()
                            except (UnicodeDecodeError, PermissionError):
                                continue

            if not files:
                console.print(f"[yellow]No supported files found[/yellow]")
                return

            # Analyze and search
            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

        # Filter by query
        query_lower = args.query.lower()
        matching = [s for s in all_symbols if query_lower in s.name.lower()]

        if args.type:
            matching = analyzer.filter_symbols_by_type(matching, SymbolType(args.type))

        # Output
        if args.output == "json":
            output = {
                "query": args.query,
                "count": len(matching),
                "symbols": [
                    {
                        "name": s.name,
                        "type": s.symbol_type.value,
                        "file": s.file_path,
                        "line": s.line_start,
                        "signature": s.signature
                    }
                    for s in matching
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "query": args.query,
                "count": len(matching),
                "symbols": [{"name": s.name, "type": s.symbol_type.value, "file": s.file_path} for s in matching]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            if not matching:
                console.print(f"[yellow]No symbols found matching '{args.query}'[/yellow]")
                return

            console.print(f"[green]Found {len(matching)} matching symbol(s)[/green]\n")

            table = Table(box=box.ROUNDED)
            table.add_column("Symbol", style="green")
            table.add_column("Type", style="cyan")
            table.add_column("File", style="dim")
            table.add_column("Line", style="dim")

            for s in matching:
                table.add_row(s.name, s.symbol_type.value, s.file_path.split("/")[-1], str(s.line_start or "-"))

            console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def code_info(args):
    """Get symbol details."""
    from ..analysis import CodeAnalyzer

    try:
        analyzer = CodeAnalyzer()
        all_symbols = []

        # Check if using indexed repo
        if getattr(args, 'repo', False):
            symbols, lib, error = await get_or_analyze_repo(args.path)

            if error:
                if args.output == "json":
                    print(json.dumps({"status": "error", "message": error}))
                else:
                    print_error(error)
                sys.exit(1)

            if not symbols:
                if args.output == "json":
                    print(json.dumps({"status": "error", "message": f"No symbols found in '{args.path}'"}))
                else:
                    console.print(f"[yellow]No symbols found in '{args.path}'[/yellow]")
                return

            all_symbols = symbols

        else:
            # Use local path
            path_obj = Path(args.path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{args.path}' does not exist[/red]")
                sys.exit(1)

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
                console.print(f"[yellow]No supported files found[/yellow]")
                return

            # Analyze and find
            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

        matching = [s for s in all_symbols if s.name == args.name or s.qualified_name == args.name]

        if not matching:
            console.print(f"[yellow]Symbol '{args.name}' not found[/yellow]")
            return

        symbol = matching[0]

        # Output
        if args.output == "json":
            output = {
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
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "name": symbol.name,
                "type": symbol.symbol_type.value,
                "file": symbol.file_path,
                "signature": symbol.signature,
                "documentation": symbol.documentation
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            console.print(Panel(
                f"[bold]{symbol.name}[/bold] ({symbol.symbol_type.value})\n\n"
                f"[cyan]File:[/cyan] {symbol.file_path}\n"
                f"[cyan]Line:[/cyan] {symbol.line_start or '-'}"
                + (f" - {symbol.line_end}" if symbol.line_end else "") + "\n"
                f"[cyan]Visibility:[/cyan] {symbol.visibility}\n"
                f"[cyan]Language:[/cyan] {symbol.language}\n"
                + (f"\n[cyan]Signature:[/cyan]\n{symbol.signature}" if symbol.signature else "")
                + (f"\n\n[cyan]Documentation:[/cyan]\n{symbol.documentation}" if symbol.documentation else ""),
                title="Symbol Details",
                border_style="green"
            ))

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


def code_symbols(args):
    """List symbols in a file."""
    from ..analysis import CodeAnalyzer

    try:
        path_obj = Path(args.file)

        if not path_obj.exists():
            console.print(f"[red]Error: File '{args.file}' does not exist[/red]")
            sys.exit(1)

        if not path_obj.is_file():
            console.print(f"[red]Error: '{args.file}' is not a file[/red]")
            sys.exit(1)

        analyzer = CodeAnalyzer()
        language = analyzer.detect_language(str(path_obj))

        if not language:
            console.print(f"[red]Error: Unsupported file type[/red]")
            sys.exit(1)

        with open(path_obj, 'r', encoding='utf-8') as f:
            code = f.read()

        symbols = analyzer.analyze_file(code, str(path_obj))

        if not symbols:
            console.print(f"[yellow]No symbols found in '{args.file}'[/yellow]")
            return

        # Output
        if args.output == "json":
            output = {
                "file": args.file,
                "language": language,
                "count": len(symbols),
                "symbols": [
                    {
                        "name": s.name,
                        "type": s.symbol_type.value,
                        "line": s.line_start,
                        "signature": s.signature,
                        "visibility": s.visibility
                    }
                    for s in sorted(symbols, key=lambda s: s.line_start or 0)
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "file": args.file,
                "language": language,
                "symbols": [{"name": s.name, "type": s.symbol_type.value} for s in symbols]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            console.print(f"[bold]{args.file}[/bold]")
            console.print(f"Language: {language}")
            console.print(f"Symbols: {len(symbols)}\n")

            if args.group:
                # Group by type
                by_type = {}
                for s in symbols:
                    stype = s.symbol_type.value
                    if stype not in by_type:
                        by_type[stype] = []
                    by_type[stype].append(s)

                for stype, type_symbols in sorted(by_type.items()):
                    console.print(f"[bold cyan]{stype.title()}s ({len(type_symbols)})[/bold cyan]")
                    for s in sorted(type_symbols, key=lambda x: x.line_start or 0):
                        vis = "🔒" if s.visibility == "private" else "🔓"
                        console.print(f"  {vis} {s.name} [dim](line {s.line_start or '-'})[/dim]")
                    console.print()
            else:
                table = Table(box=box.ROUNDED)
                table.add_column("Symbol", style="green")
                table.add_column("Type", style="cyan")
                table.add_column("Line", style="dim")
                table.add_column("Visibility", style="dim")

                for s in sorted(symbols, key=lambda x: x.line_start or 0):
                    table.add_row(s.name, s.symbol_type.value, str(s.line_start or "-"), s.visibility)

                console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def code_dep(args):
    """Generate dependency graph."""
    from ..analysis import CodeAnalyzer, DependencyGraph, GraphType

    try:
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        all_symbols = []
        all_dependencies = []
        source_info = args.path or ""
        repository_info = None

        # Determine graph type
        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
            "symbol": GraphType.SYMBOL
        }
        graph_type = graph_type_map.get(args.type, GraphType.CLASS)

        # Determine output format (use --format if provided, else global -o)
        output_format = getattr(args, 'format', 'json')

        # Check if using indexed repo
        if getattr(args, 'repo', False):
            if not args.path:
                console.print("[red]Error: Path is required when using --repo[/red]")
                sys.exit(1)

            symbols, lib, error = await get_or_analyze_repo(args.path)

            if error:
                print(json.dumps({"status": "error", "message": error}))
                sys.exit(1)

            if not symbols:
                print(json.dumps({"graph": {"nodes": {}, "edges": []}}))
                return

            all_symbols = symbols
            source_info = f"{args.path} (indexed)"

            # Get dependencies from storage
            from ..config import Config
            from ..core import GitLabContext

            config = Config.load()
            context = GitLabContext(config)
            await context.init()

            group, project = parse_repo_id(args.path)
            lib_obj = await context.storage.get_library(group, project)
            if lib_obj:
                repository_info = {
                    "id": args.path,
                    "provider": lib_obj.provider,
                    "group": group,
                    "project": project
                }

        elif args.path:
            # Use local path
            path_obj = Path(args.path)

            if not path_obj.exists():
                print(json.dumps({"status": "error", "message": f"Path '{args.path}' does not exist"}))
                sys.exit(1)

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
                print(json.dumps({"graph": {"nodes": {}, "edges": []}}))
                return

            # Analyze files
            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Extract dependencies (pass symbols for call extraction)
            for file_path, code in files.items():
                file_symbols = results.get(file_path, [])
                deps = analyzer.extract_dependencies(code, file_path, file_symbols)
                all_dependencies.extend(deps)

            source_info = args.path

        else:
            print(json.dumps({"status": "error", "message": "Path is required"}))
            sys.exit(1)

        # Build the graph
        result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_dependencies,
            graph_type=graph_type,
            graph_id=source_info,
            graph_label=f"Dependency Graph: {source_info}",
            max_depth=args.depth,
            repository_info=repository_info
        )

        # Output based on format
        if output_format == "dot":
            print(graph_builder.to_dot(result))
        elif output_format == "graphml":
            print(graph_builder.to_graphml(result))
        else:
            print(graph_builder.to_json(result))

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))
        sys.exit(1)


# ============================================================================
# CONFIG COMMANDS
# ============================================================================

async def handle_config_command(args):
    """Handle config subcommands."""
    if not args.config_command:
        console.print("[yellow]Usage: repo-ctx config <show>[/yellow]")
        return

    if args.config_command == "show":
        await config_show(args)


async def config_show(args):
    """Show current configuration."""
    from ..config import Config

    try:
        config = Config.load(config_path=args.config)

        if args.output == "json":
            output = {
                "gitlab_url": config.gitlab_url,
                "gitlab_token": "***" if config.gitlab_token else None,
                "github_url": config.github_url,
                "github_token": "***" if config.github_token else None,
                "storage_path": config.storage_path
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {
                "gitlab_url": config.gitlab_url,
                "github_url": config.github_url,
                "storage_path": config.storage_path
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            table = Table(title="Current Configuration", box=box.ROUNDED)
            table.add_column("Setting", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("GitLab URL", config.gitlab_url or "[dim]not set[/dim]")
            table.add_row("GitLab Token", "***" if config.gitlab_token else "[dim]not set[/dim]")
            table.add_row("GitHub URL", config.github_url or "https://api.github.com")
            table.add_row("GitHub Token", "***" if config.github_token else "[dim]not set[/dim]")
            table.add_row("Storage Path", config.storage_path)

            console.print(table)

            # Config file locations
            console.print("\n[dim]Config file locations:[/dim]")
            locations = [
                "~/.config/repo-ctx/config.yaml",
                "~/.repo-ctx/config.yaml",
                "./config.yaml"
            ]
            for loc in locations:
                expanded = os.path.expanduser(loc)
                exists = os.path.exists(expanded)
                status = "[green]✓[/green]" if exists else "[dim]–[/dim]"
                console.print(f"  {status} {loc}")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)
