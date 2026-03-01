"""Flat command handlers for the new Unix-style CLI.

These commands provide a simpler, flatter command structure:
- repo-ctx index <target>      instead of  repo-ctx repo index <path>
- repo-ctx analyze <target>    instead of  repo-ctx code analyze <path> --repo
- repo-ctx search <query>      instead of  repo-ctx repo search <query>

Target auto-detection:
- /owner/repo  → indexed repository
- ./path       → local filesystem
- owner/repo   → remote repository (indexes if needed)

Service Layer Integration:
- By default, uses service layer for operations
- Use --legacy flag to bypass services and use core directly
"""

import os
import sys
import json
import asyncio
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

from .target import detect_target
from .context import CLIContext
from ..config import Config

console = Console()


def print_error(message: str):
    """Print an error message."""
    from rich.markup import escape as rich_escape
    console.print(f"[red]Error: {rich_escape(str(message))}[/red]")


def run_flat_command(args):
    """Route and execute flat commands."""
    cmd = args.command

    if cmd == "index":
        asyncio.run(cmd_index(args))
    elif cmd == "list":
        asyncio.run(cmd_list(args))
    elif cmd == "search":
        asyncio.run(cmd_search(args))
    elif cmd == "docs":
        asyncio.run(cmd_docs(args))
    elif cmd == "analyze":
        asyncio.run(cmd_analyze(args))
    elif cmd == "graph":
        asyncio.run(cmd_graph(args))
    elif cmd == "query":
        asyncio.run(cmd_query(args))
    elif cmd == "export":
        asyncio.run(cmd_export(args))
    elif cmd == "status":
        asyncio.run(cmd_status(args))
    elif cmd == "dsm":
        asyncio.run(cmd_dsm(args))
    elif cmd == "cycles":
        asyncio.run(cmd_cycles(args))
    elif cmd == "layers":
        asyncio.run(cmd_layers(args))
    elif cmd == "architecture":
        asyncio.run(cmd_architecture(args))
    elif cmd == "metrics":
        asyncio.run(cmd_metrics(args))
    elif cmd == "dump":
        asyncio.run(cmd_dump(args))
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        sys.exit(1)


# =============================================================================
# INDEX - Index a repository or group
# =============================================================================

async def cmd_index(args):
    """Index a repository or group."""
    from ..progress import PrintProgressCallback

    try:
        config = Config.load(config_path=args.config)
        legacy_mode = getattr(args, 'legacy', False)
        context = CLIContext(config, legacy_mode=legacy_mode)
        await context.init()

        # Check if indexing a group
        if getattr(args, 'group', False):
            await _index_group(context, args)
            return

        target = args.target
        provider = args.provider

        # Parse target
        if provider == "local" or target.startswith(("/", "./", "~/")):
            # Local path
            if not target.startswith("/"):
                target = os.path.abspath(os.path.expanduser(target))
            group = target
            project = ""
            provider_type = "local"
        else:
            # Remote repo: owner/repo
            parts = target.split("/")
            if len(parts) < 2:
                console.print("[red]Error: Repository must be in format owner/repo[/red]")
                sys.exit(1)
            project = parts[-1]
            group = "/".join(parts[:-1])
            provider_type = None if provider == "auto" else provider

        # Progress callback for text output
        progress = None if args.output == "json" else PrintProgressCallback()

        # analyze_code defaults to True, --no-analyze sets it to False
        analyze_code = not getattr(args, 'no_analyze', False)

        await context.index_repository(
            group,
            project,
            provider_type=provider_type,
            progress=progress,
            analyze_code=analyze_code
        )

        if args.output == "json":
            print(json.dumps({"status": "success", "repository": target, "analyze_code": analyze_code}))
        else:
            console.print(f"[green]Indexed: {target}[/green]")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def _index_group(context, args):
    """Index all repositories in a group."""
    from ..progress import PrintProgressCallback

    group = args.target
    include_subgroups = not getattr(args, 'no_subgroups', False)
    provider = args.provider
    provider_type = None if provider == "auto" else provider

    progress = None if args.output == "json" else PrintProgressCallback()

    result = await context.index_group(
        group,
        include_subgroups=include_subgroups,
        provider_type=provider_type,
        progress=progress
    )

    if args.output == "json":
        print(json.dumps({
            "status": "success",
            "group": group,
            "indexed": result.get("indexed", []),
            "failed": result.get("failed", [])
        }))
    else:
        indexed_count = len(result.get("indexed", []))
        failed_count = len(result.get("failed", []))
        console.print(f"[green]Indexed {indexed_count} repositories from '{group}'[/green]")
        if failed_count > 0:
            console.print(f"[yellow]Failed: {failed_count}[/yellow]")


# =============================================================================
# LIST - List indexed repositories
# =============================================================================

async def cmd_list(args):
    """List indexed repositories."""
    try:
        config = Config.load(config_path=args.config)
        legacy_mode = getattr(args, 'legacy', False)
        context = CLIContext(config, legacy_mode=legacy_mode)
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
                        "provider": lib.provider,
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
                    {"id": f"/{lib.group_name}/{lib.project_name}", "description": lib.description}
                    for lib in libraries
                ]
            }
            print(yaml.dump(output, default_flow_style=False))
        else:
            if not libraries:
                console.print("[yellow]No repositories indexed.[/yellow]")
                console.print("[dim]Use 'repo-ctx index <repo>' to index repositories.[/dim]")
                return

            table = Table(title=f"Indexed Repositories ({len(libraries)})", box=box.ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("Repository", style="green")
            table.add_column("Description", style="white")

            for i, lib in enumerate(libraries, 1):
                table.add_row(
                    str(i),
                    f"/{lib.group_name}/{lib.project_name}",
                    (lib.description or "")[:50]
                )

            console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# SEARCH - Unified search (repos and symbols)
# =============================================================================

async def cmd_search(args):
    """Unified search for repositories and symbols."""
    # Check if searching symbols
    if getattr(args, 'symbols', None):
        await _search_symbols(args)
    else:
        await _search_repos(args)


async def _search_repos(args):
    """Search repositories (fuzzy or exact)."""
    try:
        config = Config.load(config_path=args.config)
        legacy_mode = getattr(args, 'legacy', False)
        context = CLIContext(config, legacy_mode=legacy_mode)
        await context.init()

        query = args.query
        exact = getattr(args, 'exact', False)
        limit = getattr(args, 'limit', 10)

        if exact:
            results = await context.search_libraries(query)
        else:
            results = await context.fuzzy_search_libraries(query, limit=limit)

        if args.output == "json":
            output = {
                "query": query,
                "exact": exact,
                "count": len(results),
                "results": [
                    {
                        "id": r.library_id,
                        "name": r.name,
                        "description": r.description,
                        "score": getattr(r, 'score', 1.0)
                    }
                    for r in results
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not results:
                console.print(f"[yellow]No repositories found for '{query}'[/yellow]")
                return

            table = Table(box=box.ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("Repository", style="green")
            table.add_column("Description", style="white")
            if not exact:
                table.add_column("Score", style="cyan", width=8)

            for i, r in enumerate(results, 1):
                row = [str(i), r.library_id, (r.description or "")[:50]]
                if not exact:
                    row.append(f"{getattr(r, 'score', 1.0):.0%}")
                table.add_row(*row)

            console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def _search_symbols(args):
    """Search symbols in a target (local path or indexed repo)."""
    from ..analysis import CodeAnalyzer
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.symbols)
        query = args.query.lower()
        analyzer = CodeAnalyzer()
        all_symbols = []

        if target.is_repo:
            # Indexed repository
            symbols, lib, error = await get_or_analyze_repo_standalone(target.repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Search by name
        matching = [s for s in all_symbols if query in s.name.lower()]

        # Apply filters
        if getattr(args, 'type', None):
            matching = [s for s in matching if s.symbol_type.value == args.type]
        if getattr(args, 'lang', None):
            matching = [s for s in matching if s.language == args.lang]

        if args.output == "json":
            output = {
                "query": args.query,
                "target": args.symbols,
                "count": len(matching),
                "symbols": [
                    {
                        "name": s.name,
                        "type": s.symbol_type.value,
                        "file": s.file_path,
                        "line": s.line_start
                    }
                    for s in matching
                ]
            }
            print(json.dumps(output, indent=2))
        else:
            if not matching:
                console.print(f"[yellow]No symbols found for '{args.query}'[/yellow]")
                return

            console.print(f"[bold]Found {len(matching)} symbol(s):[/bold]\n")
            for s in sorted(matching, key=lambda x: (x.file_path, x.line_start or 0)):
                loc = f":{s.line_start}" if s.line_start else ""
                console.print(f"  [green]{s.name}[/green] ({s.symbol_type.value}) - {s.file_path}{loc}")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# DOCS - Get repository documentation
# =============================================================================

async def cmd_docs(args):
    """Get documentation for a repository."""
    from ..models import OutputMode
    from ..operations import parse_include_options, get_or_analyze_repo_standalone

    try:
        config = Config.load(config_path=args.config)
        legacy_mode = getattr(args, 'legacy', False)
        context = CLIContext(config, legacy_mode=legacy_mode)
        await context.init()

        repo_id = args.repository

        # Parse include options
        include_str = getattr(args, 'include', None)
        include_opts = parse_include_options(include_str)
        force_refresh = getattr(args, 'refresh', False)

        # Parse output mode
        output_mode_str = getattr(args, 'mode', 'standard')
        try:
            output_mode = OutputMode.from_string(output_mode_str)
        except ValueError:
            output_mode = OutputMode.STANDARD

        # Check for llmstxt format
        if getattr(args, 'format', None) == 'llmstxt':
            await _docs_llmstxt(context, args)
            return

        query = getattr(args, 'query', None)

        result = await context.get_documentation(
            repo_id,
            topic=getattr(args, 'topic', None),
            page=getattr(args, 'page', 1),
            max_tokens=getattr(args, 'max_tokens', None),
            include_examples=include_opts['include_examples'],
            output_mode=output_mode,
            query=query
        )

        # Add code analysis if requested
        needs_code = include_opts['include_code'] or include_opts['include_symbols'] or include_opts['include_diagrams']
        if needs_code:
            from ..analysis import CodeAnalysisReport
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id, force_refresh=force_refresh)
            if not error and symbols:
                report = CodeAnalysisReport(symbols, exclude_tests=not include_opts['include_tests'])
                markdown = report.generate_markdown(
                    include_code=include_opts['include_code'],
                    include_symbols=include_opts['include_symbols'],
                    include_mermaid=include_opts['include_diagrams']
                )
                result["content"][0]["text"] += f"\n\n---\n\n{markdown}"

        if args.output == "json":
            print(json.dumps(result, indent=2))
        elif args.output == "yaml":
            import yaml
            print(yaml.dump(result, default_flow_style=False))
        else:
            console.print(result["content"][0]["text"], markup=False)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


async def _docs_llmstxt(context, args):
    """Generate llms.txt format documentation."""
    from ..llmstxt import LlmsTxtGenerator
    from ..operations import parse_repo_id

    repo_id = args.repository
    group, project = parse_repo_id(repo_id)

    lib = await context.storage.get_library(group, project)
    if not lib:
        print_error(f"Repository not found: {repo_id}")
        sys.exit(1)

    version_id = await context.storage.get_version_id(lib.id, lib.default_version)
    if not version_id:
        print_error(f"No version found for {repo_id}")
        sys.exit(1)

    documents = await context.storage.get_documents(version_id)

    generator = LlmsTxtGenerator()
    llmstxt = generator.generate(
        documents,
        repo_id,
        description=lib.description,
        include_api=not getattr(args, 'no_api', False),
        include_quickstart=not getattr(args, 'no_quickstart', False)
    )

    if args.output == "json":
        print(json.dumps({"repository": repo_id, "content": llmstxt}))
    else:
        print(llmstxt)


# =============================================================================
# ANALYZE - Code analysis with auto-detection
# =============================================================================

async def cmd_analyze(args):
    """Analyze code with automatic target detection."""
    from ..analysis import CodeAnalyzer, SymbolType
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        # Pass Smalltalk dialect if specified
        dialect = getattr(args, 'dialect', None)
        analyzer = CodeAnalyzer(smalltalk_dialect=dialect)
        all_symbols = []
        files_count = 0
        source_info = args.target

        if target.is_repo:
            # Indexed or remote repository
            repo_id = target.repo_id
            force_refresh = getattr(args, 'refresh', False)

            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id, force_refresh=force_refresh)
            if error:
                if args.output == "json":
                    print(json.dumps({"status": "error", "message": error}))
                else:
                    print_error(error)
                sys.exit(1)

            all_symbols = symbols or []
            source_info = f"{repo_id} (indexed)"

        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

            files = {}
            lang_filter = getattr(args, 'lang', None)

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

            if not files:
                if args.output == "json":
                    print(json.dumps({"target": args.target, "symbols": [], "statistics": {}}))
                else:
                    console.print(f"[yellow]No supported files found in '{args.target}'[/yellow]")
                return

            files_count = len(files)
            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

        # Apply filters
        if getattr(args, 'type', None):
            all_symbols = analyzer.filter_symbols_by_type(all_symbols, SymbolType(args.type))
        if not getattr(args, 'private', True):
            all_symbols = analyzer.filter_symbols_by_visibility(all_symbols, "public")

        stats = analyzer.get_statistics(all_symbols)

        # Output
        if args.output == "json":
            output = {
                "target": args.target,
                "files_analyzed": files_count if files_count else "indexed",
                "statistics": stats,
                "symbols": [
                    {
                        "name": s.name,
                        "type": s.symbol_type.value,
                        "file": s.file_path,
                        "line": s.line_start,
                        "visibility": s.visibility,
                        "language": s.language
                    }
                    for s in all_symbols
                ]
            }
            print(json.dumps(output, indent=2))
        elif args.output == "yaml":
            import yaml
            output = {"target": args.target, "statistics": stats}
            print(yaml.dump(output, default_flow_style=False))
        else:
            console.print(f"[bold]Analysis: {source_info}[/bold]\n")
            if files_count:
                console.print(f"Files analyzed: {files_count}")
            console.print(f"Total symbols: {stats['total_symbols']}\n")

            if stats['by_type']:
                table = Table(title="Symbols by Type", box=box.SIMPLE)
                table.add_column("Type", style="cyan")
                table.add_column("Count", style="white", justify="right")
                for stype, count in sorted(stats['by_type'].items()):
                    table.add_row(stype, str(count))
                console.print(table)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# GRAPH - Dependency graph
# =============================================================================

async def cmd_graph(args):
    """Generate dependency graph."""
    from ..analysis import CodeAnalyzer, DependencyGraph, GraphType
    from ..operations import get_or_analyze_repo_standalone, parse_repo_id

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        all_symbols = []
        all_deps = []
        repository_info = None

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []

            # Get repo info for graph metadata
            config = Config.load(config_path=args.config)
            legacy_mode = getattr(args, 'legacy', False)
            context = CLIContext(config, legacy_mode=legacy_mode)
            await context.init()
            group, project = parse_repo_id(repo_id)
            lib_obj = await context.storage.get_library(group, project)
            if lib_obj:
                repository_info = {"id": repo_id, "provider": lib_obj.provider}

        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build graph
        result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"Dependencies: {args.target}",
            max_depth=getattr(args, 'depth', None),
            repository_info=repository_info
        )

        # Output
        fmt = getattr(args, 'format', 'json')
        if fmt == "dot":
            print(graph_builder.to_dot(result))
        elif fmt == "graphml":
            print(graph_builder.to_graphml(result))
        else:
            print(graph_builder.to_json(result))

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# QUERY - CPG query (Joern)
# =============================================================================

async def cmd_query(args):
    """Run CPGQL query."""
    from ..analysis import CodeAnalyzer

    try:
        analyzer = CodeAnalyzer()

        if not analyzer.is_joern_available():
            print_error("Joern is not installed. See: https://joern.io/")
            sys.exit(1)

        result = analyzer.run_cpg_query(args.path, args.query, args.output)

        if not result["success"]:
            print_error(result.get("error", "Query failed"))
            sys.exit(1)

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[bold]Query:[/bold] {result['query']}\n")
            console.print(result['output'])

    except Exception as e:
        print_error(e)
        sys.exit(1)


# =============================================================================
# EXPORT - CPG export (Joern)
# =============================================================================

async def cmd_export(args):
    """Export CPG to visualization format."""
    from ..analysis import CodeAnalyzer

    try:
        analyzer = CodeAnalyzer()

        if not analyzer.is_joern_available():
            print_error("Joern is not installed. See: https://joern.io/")
            sys.exit(1)

        result = analyzer.export_cpg_graph(
            args.path,
            args.output_dir,
            getattr(args, 'repr', 'all'),
            getattr(args, 'format', 'dot')
        )

        if not result["success"]:
            print_error(result.get("error", "Export failed"))
            sys.exit(1)

        if args.output == "json":
            print(json.dumps(result, indent=2))
        else:
            console.print(f"[green]Exported to: {result['output_dir']}[/green]")
            console.print(f"Files: {result.get('file_count', 0)}")

    except Exception as e:
        print_error(e)
        sys.exit(1)


# =============================================================================
# STATUS - System status
# =============================================================================

async def cmd_status(args):
    """Show system status and capabilities."""
    from ..analysis import CodeAnalyzer

    try:
        analyzer = CodeAnalyzer()

        status = {
            "joern": {
                "available": analyzer.is_joern_available(),
                "version": analyzer.get_joern_version() if analyzer.is_joern_available() else None,
                "languages": analyzer.get_joern_supported_languages() if analyzer.is_joern_available() else []
            },
            "treesitter": {
                "available": True,
                "languages": analyzer.get_treesitter_supported_languages()
            }
        }

        if args.output == "json":
            print(json.dumps(status, indent=2))
        else:
            console.print("[bold]repo-ctx Status[/bold]\n")

            # Joern
            if status["joern"]["available"]:
                console.print(f"[green]Joern:[/green] {status['joern']['version']}")
                console.print(f"  Languages: {', '.join(sorted(set(status['joern']['languages'])))}")
            else:
                console.print("[yellow]Joern:[/yellow] Not installed")

            # Tree-sitter
            console.print("\n[green]Tree-sitter:[/green] Available")
            console.print(f"  Languages: {', '.join(sorted(status['treesitter']['languages']))}")

    except Exception as e:
        print_error(e)
        sys.exit(1)


# =============================================================================
# DSM - Dependency Structure Matrix
# =============================================================================

async def cmd_dsm(args):
    """Generate Dependency Structure Matrix."""
    from ..analysis import CodeAnalyzer, DependencyGraph, GraphType, DSMBuilder
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        dsm_builder = DSMBuilder()
        all_symbols = []
        all_deps = []

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build dependency graph
        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"DSM: {args.target}"
        )

        # Build DSM
        dsm = dsm_builder.build(graph_result)

        # Output
        fmt = getattr(args, 'format', 'text')
        if fmt == "json":
            print(dsm.to_json())
        else:
            print(dsm.to_text())

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# CYCLES - Cycle detection
# =============================================================================

async def cmd_cycles(args):
    """Detect dependency cycles."""
    from ..analysis import CodeAnalyzer, DependencyGraph, GraphType, CycleDetector
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        cycle_detector = CycleDetector()
        all_symbols = []
        all_deps = []

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build dependency graph
        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"Cycles: {args.target}"
        )

        # Detect cycles
        cycles = cycle_detector.detect(graph_result)

        # Output
        fmt = getattr(args, 'format', 'text')
        if fmt == "json":
            output = {
                "target": args.target,
                "graph_type": graph_type.value,
                "cycle_count": len(cycles),
                "cycles": [c.to_dict() for c in cycles]
            }
            print(json.dumps(output, indent=2))
        else:
            if not cycles:
                console.print(f"[green]No cycles detected in {args.target}[/green]")
                console.print(f"Graph type: {graph_type.value}")
                console.print(f"Total nodes: {len(graph_result.nodes)}")
            else:
                console.print(f"[red]Found {len(cycles)} cycle(s) in {args.target}[/red]\n")
                console.print(f"Graph type: {graph_type.value}")
                console.print(f"Total nodes: {len(graph_result.nodes)}\n")

                for i, cycle in enumerate(cycles, 1):
                    console.print(f"[bold]Cycle {i}[/bold] (impact: {cycle.impact_score:.1f})")
                    console.print(f"  Nodes: {' -> '.join(cycle.nodes[:8])}")
                    if len(cycle.nodes) > 8:
                        console.print(f"         ... and {len(cycle.nodes) - 8} more")
                    console.print(f"  Edges: {len(cycle.edges)}")

                    if cycle.breakup_suggestions:
                        console.print("  [yellow]Breakup suggestions:[/yellow]")
                        for j, suggestion in enumerate(cycle.breakup_suggestions[:3], 1):
                            console.print(f"    {j}. {suggestion.reason}")
                    console.print()

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# LAYERS - Layer detection
# =============================================================================

async def cmd_layers(args):
    """Detect architectural layers from dependency structure."""
    from ..analysis import CodeAnalyzer, DependencyGraph, GraphType, LayerDetector
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        layer_detector = LayerDetector()
        all_symbols = []
        all_deps = []

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build dependency graph
        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"Layers: {args.target}"
        )

        # Detect layers
        layers = layer_detector.detect(graph_result)

        # Output
        fmt = getattr(args, 'format', 'text')
        if fmt == "json":
            output = {
                "target": args.target,
                "graph_type": graph_type.value,
                "layer_count": len(layers),
                "layers": [layer.to_dict() for layer in layers]
            }
            print(json.dumps(output, indent=2))
        else:
            if not layers:
                console.print(f"[yellow]No layers detected in {args.target}[/yellow]")
                console.print(f"Graph type: {graph_type.value}")
                console.print(f"Total nodes: {len(graph_result.nodes)}")
            else:
                console.print(f"[bold]Detected {len(layers)} layer(s) in {args.target}[/bold]\n")
                console.print(f"Graph type: {graph_type.value}")
                console.print(f"Total nodes: {len(graph_result.nodes)}\n")

                for layer in reversed(layers):  # Show from top to bottom
                    console.print(f"[cyan]Level {layer.level}:[/cyan] {layer.name}")
                    console.print(f"  Nodes ({len(layer.nodes)}): ", end="")
                    display_nodes = layer.nodes[:10]
                    console.print(", ".join(display_nodes), end="")
                    if len(layer.nodes) > 10:
                        console.print(f" ... and {len(layer.nodes) - 10} more")
                    else:
                        console.print()
                    console.print()

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# ARCHITECTURE - Architecture rule checking
# =============================================================================

async def cmd_architecture(args):
    """Check architecture rules and detect violations."""
    from ..analysis import (
        CodeAnalyzer, DependencyGraph, GraphType,
        analyze_with_rules
    )
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        all_symbols = []
        all_deps = []

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build dependency graph
        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"Architecture: {args.target}"
        )

        # Load rules if specified
        rules_file = getattr(args, 'rules', None)

        # Analyze with rules
        result = analyze_with_rules(
            graph_result,
            rules_file=rules_file
        )

        # Output
        fmt = getattr(args, 'format', 'text')
        if fmt == "json":
            output = {
                "target": args.target,
                "graph_type": graph_type.value,
                "rules_file": rules_file,
                **result
            }
            print(json.dumps(output, indent=2))
        else:
            console.print(f"[bold]Architecture Analysis: {args.target}[/bold]\n")
            console.print(f"Graph type: {graph_type.value}")
            console.print(f"Total nodes: {len(graph_result.nodes)}")
            if rules_file:
                console.print(f"Rules: {rules_file}")
            if result["summary"].get("rules_name"):
                console.print(f"Architecture: {result['summary']['rules_name']}")
            console.print()

            # Layers
            if result["layers"]:
                console.print(f"[cyan]Layers ({len(result['layers'])}):[/cyan]")
                for layer in reversed(result["layers"]):
                    node_count = layer.get("node_count", len(layer.get("nodes", [])))
                    console.print(f"  Level {layer['level']}: {layer['name']} ({node_count} nodes)")
                console.print()

            # Violations
            if result["violations"]:
                console.print(f"[red]Violations ({len(result['violations'])}):[/red]")
                for v in result["violations"]:
                    console.print(f"  [{v['severity'].upper()}] {v['rule_name']}: {v['message']}")
                    console.print(f"    {v['source']} -> {v['target']}")
                    if v.get("file_path"):
                        loc = f":{v['line']}" if v.get("line") else ""
                        console.print(f"    at {v['file_path']}{loc}")
                    console.print()
            else:
                console.print("[green]No architecture violations detected.[/green]")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# METRICS - Structural complexity metrics (XS)
# =============================================================================

async def cmd_metrics(args):
    """Calculate XS (eXcess Structural complexity) metrics."""
    from ..analysis import (
        CodeAnalyzer, DependencyGraph, GraphType,
        analyze_structure
    )
    from ..operations import get_or_analyze_repo_standalone

    try:
        target = detect_target(args.target)
        analyzer = CodeAnalyzer()
        graph_builder = DependencyGraph()
        all_symbols = []
        all_deps = []

        graph_type_map = {
            "file": GraphType.FILE,
            "module": GraphType.MODULE,
            "class": GraphType.CLASS,
            "function": GraphType.FUNCTION,
        }
        graph_type = graph_type_map.get(getattr(args, 'type', 'class'), GraphType.CLASS)

        if target.is_repo:
            repo_id = target.repo_id
            symbols, lib, error = await get_or_analyze_repo_standalone(repo_id)
            if error:
                print_error(error)
                sys.exit(1)
            all_symbols = symbols or []
        else:
            # Local path
            path_obj = Path(target.value)
            if not path_obj.exists():
                print_error(f"Path not found: {target.value}")
                sys.exit(1)

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

        # Build dependency graph
        graph_result = graph_builder.build(
            symbols=all_symbols,
            dependencies=all_deps,
            graph_type=graph_type,
            graph_id=args.target,
            graph_label=f"Metrics: {args.target}"
        )

        # Load rules and check violations if specified
        violations = []
        rules_file = getattr(args, 'rules', None)
        if rules_file:
            from ..analysis import analyze_with_rules
            result = analyze_with_rules(graph_result, rules_file=rules_file)
            # Convert violation dicts back to objects for XS calculation
            from ..analysis import ArchitectureViolation
            violations = [
                ArchitectureViolation(
                    rule_name=v["rule_name"],
                    source=v["source"],
                    target=v["target"],
                    message=v["message"],
                    file_path=v.get("file_path"),
                    line=v.get("line"),
                    severity=v.get("severity", "error")
                )
                for v in result.get("violations", [])
            ]

        # Calculate metrics
        report = analyze_structure(graph_result, violations=violations)

        # Output
        fmt = getattr(args, 'format', 'text')
        if fmt == "json":
            output = {
                "target": args.target,
                "graph_type": graph_type.value,
                "rules_file": rules_file,
                **report
            }
            print(json.dumps(output, indent=2))
        else:
            summary = report["summary"]
            metrics = report["metrics"]

            # Header with grade
            grade_colors = {"A": "green", "B": "cyan", "C": "yellow", "D": "red", "F": "red bold"}
            grade_color = grade_colors.get(summary["grade"], "white")
            console.print(f"[bold]Structural Metrics: {args.target}[/bold]\n")
            console.print(f"[{grade_color}]Grade: {summary['grade']}[/{grade_color}] - {summary['grade_description']}")
            console.print(f"[bold]XS Score: {summary['xs_score']}[/bold]\n")

            # Summary stats
            console.print(f"Nodes: {summary['total_nodes']} | Edges: {summary['total_edges']}")
            console.print(f"Cycles: {summary['cycles']} | Violations: {summary['violations']}")
            console.print()

            # Component breakdown
            components = metrics.get("components", {})
            console.print("[cyan]Score Breakdown:[/cyan]")
            console.print(f"  Cycles:     {components.get('cycle_contribution', 0):6.1f}")
            console.print(f"  Coupling:   {components.get('coupling_contribution', 0):6.1f}")
            console.print(f"  Size:       {components.get('size_contribution', 0):6.1f}")
            console.print(f"  Violations: {components.get('violation_contribution', 0):6.1f}")
            console.print()

            # Hotspots
            hotspots = report.get("hotspots", [])
            if hotspots:
                console.print(f"[yellow]Hotspots ({len(hotspots)}):[/yellow]")
                for h in hotspots[:5]:  # Top 5
                    console.print(f"  {h['node_label']} ({h['reason']}) - severity: {h['severity']:.1f}")

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)


# =============================================================================
# DUMP - Export repository analysis to .repo-ctx directory
# =============================================================================

async def cmd_dump(args):
    """Export repository analysis to .repo-ctx directory."""
    from ..services import create_service_context, DumpService, DumpLevel
    from ..progress import PrintProgressCallback

    try:
        target = args.target

        # Resolve target path
        if not target.startswith("/"):
            target = os.path.abspath(os.path.expanduser(target))

        source_path = Path(target)
        if not source_path.exists():
            print_error(f"Path not found: {target}")
            sys.exit(1)

        if not source_path.is_dir():
            print_error(f"Target must be a directory: {target}")
            sys.exit(1)

        # Parse level
        level_map = {
            "compact": DumpLevel.COMPACT,
            "medium": DumpLevel.MEDIUM,
            "full": DumpLevel.FULL,
        }
        level = level_map.get(getattr(args, 'level', 'medium'), DumpLevel.MEDIUM)

        # Output path
        output_path = None
        if getattr(args, 'output', None):
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = Path(os.getcwd()) / output_path

        # Create service context
        context = create_service_context()

        # Optionally create LLM service for business summary or enhancement
        llm_service = None
        use_llm = getattr(args, 'llm', False)
        llm_enhance = getattr(args, 'llm_enhance', False)
        if use_llm or llm_enhance:
            try:
                from ..services.llm import LLMService
                llm_model = getattr(args, 'llm_model', 'gpt-5-mini')
                llm_service = LLMService(context, model=llm_model)
                if args.output != "json":
                    console.print(f"[cyan]LLM provider: {llm_model}[/cyan]")
            except Exception as e:
                if args.output != "json":
                    console.print(f"[yellow]Warning: Could not initialize LLM service: {e}[/yellow]")

        # Create dump service with optional LLM
        service = DumpService(context, llm_service=llm_service)

        # Create progress callback for text output
        progress = None if args.output == "json" else PrintProgressCallback()

        # Show progress header
        if args.output != "json":
            console.print("[bold]Dumping repository analysis...[/bold]")
            console.print(f"  Source: {source_path}")
            console.print(f"  Level: {level.value}")
            if output_path:
                console.print(f"  Output: {output_path}")
            if use_llm and llm_service:
                console.print("  LLM Summary: enabled")
            console.print()

        # Check if persist_to_graph is requested
        persist_to_graph = getattr(args, 'persist_graph', False)
        if persist_to_graph and args.output != "json":
            console.print("  Persist to graph: enabled")

        # Check if llm_enhance is requested
        if llm_enhance and args.output != "json":
            console.print("  LLM Enhancement: enabled")

        # Check for skip_joern flag
        skip_joern = getattr(args, 'skip_joern', False)
        if skip_joern and args.output != "json":
            console.print("  Skip Joern: enabled (tree-sitter only)")

        # Run dump with progress callback
        result = await service.dump(
            source_path=source_path,
            output_path=output_path,
            level=level,
            force=getattr(args, 'force', False),
            include_private=getattr(args, 'include_private', False),
            progress=progress,
            exclude_patterns=getattr(args, 'exclude_patterns', None),
            persist_to_graph=persist_to_graph,
            skip_joern=skip_joern,
        )

        # Run LLM enhancement if requested
        enhance_result = None
        if llm_enhance and result.success:
            try:
                from ..analysis.file_enhancer import FileEnhancer
                import json as json_lib

                if args.output != "json":
                    console.print("\n[cyan]Enhancing documentation with LLM...[/cyan]")

                # Check for by-file directory (requires --level full)
                by_file_dir = result.output_path / "symbols" / "by-file"
                enhanced_files = []

                if by_file_dir.exists():
                    # Create enhancer with LLM service and source path
                    enhancer = FileEnhancer(
                        llm_service=llm_service,
                        source_root=source_path,
                    )

                    # Get configuration
                    include_private = getattr(args, 'include_private', False)
                    max_concurrency = getattr(args, 'llm_concurrency', 5)

                    # Load all file data
                    json_files = list(by_file_dir.glob("*.json"))
                    total_files = len(json_files)

                    if args.output != "json":
                        console.print(f"  Processing {total_files} files (concurrency: {max_concurrency})...")

                    # Load file data from JSON files
                    files_data = []
                    json_file_paths = []  # Keep track of paths for writing back
                    for json_file in json_files:
                        with open(json_file) as f:
                            file_data = json_lib.load(f)
                        files_data.append(file_data)
                        json_file_paths.append(json_file)

                    # Progress callback for parallel processing
                    def progress_callback(file_path: str, completed: int, total: int):
                        if args.output != "json":
                            short_path = file_path.split("/")[-1] if "/" in file_path else file_path
                            console.print(f"  [{completed}/{total}] Enhanced {short_path}...", end="\r")

                    # Process files in parallel with controlled concurrency
                    enhanced_results = await enhancer.enhance_files_parallel(
                        files_data=files_data,
                        max_concurrency=max_concurrency,
                        progress_callback=progress_callback,
                        include_private=include_private,
                    )

                    # Write enhanced files back
                    for json_file, enhanced in zip(json_file_paths, enhanced_results):
                        with open(json_file, "w") as f:
                            json_lib.dump(enhanced, f, indent=2)
                        enhanced_files.append(enhanced.get("file", ""))

                    if args.output != "json":
                        # Clear progress line and show summary
                        console.print(" " * 80, end="\r")
                        console.print(f"[green]Enhanced {len(enhanced_files)} files with LLM documentation[/green]")
                else:
                    if args.output != "json":
                        console.print("[yellow]Note: symbols/by-file not found. Using index.json for summary (use --level full for per-file enhancement).[/yellow]")

                enhance_result = {
                    "files_enhanced": len(enhanced_files),
                    "files": enhanced_files,
                }

                # Generate business summary and add it to llms.txt (not as separate file)
                if args.output != "json":
                    console.print("[cyan]Generating business summary for llms.txt...[/cyan]")

                from ..analysis.codebase_summarizer import CodebaseSummarizer
                summarizer = CodebaseSummarizer(llm_service=llm_service)
                raw_summary = await summarizer.generate_raw_summary(
                    repo_ctx_path=result.output_path,
                    project_name=source_path.name,
                )

                if raw_summary:
                    llms_txt_path = result.output_path / "llms.txt"
                    if summarizer.update_llms_txt(llms_txt_path, raw_summary):
                        enhance_result["llms_txt_updated"] = True
                        if args.output != "json":
                            console.print("[green]Updated llms.txt with business summary[/green]")
                    else:
                        if args.output != "json":
                            console.print("[yellow]Warning: Could not update llms.txt with business summary[/yellow]")
                else:
                    if args.output != "json":
                        console.print("[yellow]Warning: Business summary not generated (LLM returned empty response - check your API key and model name)[/yellow]")

            except Exception as e:
                if args.output != "json":
                    console.print(f"[yellow]Warning: LLM enhancement failed: {e}[/yellow]")

        # Output
        if args.output == "json":
            output_dict = result.to_dict()
            if enhance_result:
                output_dict["enhancement"] = enhance_result
            print(json.dumps(output_dict, indent=2))
        else:
            if result.success:
                console.print(f"[green]Successfully created {result.output_path}[/green]")
                console.print(f"\nFiles created ({len(result.files_created)}):")
                for f in result.files_created[:15]:
                    console.print(f"  • {f}")
                if len(result.files_created) > 15:
                    console.print(f"  ... and {len(result.files_created) - 15} more")

                # Show stats from metadata
                if result.metadata:
                    stats = result.metadata.stats
                    console.print("\nAnalysis summary:")
                    console.print(f"  Symbols: {stats.get('symbols_extracted', 0)}")
                    console.print(f"  Files: {stats.get('files_analyzed', 0)}")
                    if result.metadata.git and result.metadata.git.commit:
                        console.print(f"  Git commit: {result.metadata.git.short_commit}")
                    # Show graph stats if graph was persisted
                    graph_nodes = stats.get('graph_nodes', 0)
                    graph_rels = stats.get('graph_relationships', 0)
                    if graph_nodes > 0 or graph_rels > 0:
                        console.print("\nGraph storage:")
                        console.print(f"  Nodes: {graph_nodes}")
                        console.print(f"  Relationships: {graph_rels}")
            else:
                console.print("[red]Dump failed[/red]")
                for error in result.errors:
                    console.print(f"  • {error}")
                sys.exit(1)

    except Exception as e:
        if args.output == "json":
            print(json.dumps({"status": "error", "message": str(e)}))
        else:
            print_error(e)
        sys.exit(1)
    finally:
        # Clean up litellm async clients to avoid warning
        if use_llm:
            try:
                import asyncio
                from litellm.llms.custom_httpx.async_client_cleanup import close_litellm_async_clients
                asyncio.get_event_loop().run_until_complete(close_litellm_async_clients())
            except Exception:
                pass  # Ignore cleanup errors