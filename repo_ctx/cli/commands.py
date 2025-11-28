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
from rich import box

console = Console()


def parse_repo_id(repo_id: str) -> Tuple[str, str]:
    """Parse repo_id into (group, project) tuple."""
    clean_id = repo_id.strip("/")
    parts = clean_id.split("/")
    if len(parts) >= 2:
        project = parts[-1]
        group = "/".join(parts[:-1])
        return (group, project)
    return (clean_id, "")


async def get_or_analyze_repo(repo_id: str, force_refresh: bool = False):
    """Get stored analysis for a repo, or analyze and store it."""
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
            console.print(f"[red]Error: {e}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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

        if args.output == "json":
            print(json.dumps(result, indent=2))
        elif args.output == "yaml":
            import yaml
            print(yaml.dump(result, default_flow_style=False))
        else:
            content = result["content"][0]["text"]
            console.print(content)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


# ============================================================================
# CODE COMMANDS
# ============================================================================

async def handle_code_command(args):
    """Handle code subcommands."""
    if not args.code_command:
        console.print("[yellow]Usage: repo-ctx code <analyze|find|info|symbols>[/yellow]")
        return

    if args.code_command == "analyze":
        await code_analyze(args)
    elif args.code_command == "find":
        await code_find(args)
    elif args.code_command == "info":
        await code_info(args)
    elif args.code_command == "symbols":
        code_symbols(args)


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
                    console.print(f"[red]Error: {error}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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
                    console.print(f"[red]Error: {error}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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
                    console.print(f"[red]Error: {error}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
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
            console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
