"""Interactive command palette mode."""

import sys
import os
import asyncio
from typing import Optional, List, Dict, Any

import questionary
from questionary import Style
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.markup import escape as rich_escape
from rich import box

from .. import __version__

console = Console()


def print_error(message: str):
    """Print an error message, escaping any rich markup in the message."""
    console.print(f"[red]Error: {rich_escape(str(message))}[/red]")


async def get_indexed_repos() -> List[str]:
    """Fetch list of indexed repository IDs."""
    try:
        from ..config import Config
        from ..core import GitLabContext

        config = Config.load()
        context = GitLabContext(config)
        await context.init()

        libraries = await context.list_all_libraries()
        return [f"/{lib.group_name}/{lib.project_name}" for lib in libraries]
    except Exception:
        return []


def parse_repo_id(repo_id: str) -> tuple:
    """Parse repo_id into (group, project) tuple."""
    # Remove leading slash if present
    clean_id = repo_id.strip("/")
    parts = clean_id.split("/")
    if len(parts) >= 2:
        project = parts[-1]
        group = "/".join(parts[:-1])
        return (group, project)
    return (clean_id, "")


async def get_library_info(repo_id: str):
    """Get library info for a repo_id."""
    from ..config import Config
    from ..core import GitLabContext

    config = Config.load()
    context = GitLabContext(config)
    await context.init()

    group, project = parse_repo_id(repo_id)
    lib = await context.storage.get_library(group, project)
    return lib, context, config


async def get_or_analyze_repo(repo_id: str, force_refresh: bool = False):
    """Get stored analysis for a repo, or analyze and store it."""
    from ..config import Config
    from ..core import GitLabContext
    from ..analysis import CodeAnalyzer
    from ..providers import ProviderFactory

    config = Config.load()
    context = GitLabContext(config)
    await context.init()

    group, project = parse_repo_id(repo_id)
    lib = await context.storage.get_library(group, project)

    if not lib:
        return None, None, f"Repository {repo_id} not found in index"

    # Check if we have stored symbols
    stored_symbols = await context.storage.search_symbols(lib.id, "")

    if stored_symbols and not force_refresh:
        # Return stored symbols
        from ..analysis import Symbol, SymbolType
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


def is_local_path(path: str) -> bool:
    """Check if the given path is a local filesystem path."""
    # Explicit local path indicators
    if path.startswith(("/", "./", "../", "~/")):
        return True
    # Check if it exists as a local path
    expanded = os.path.expanduser(path)
    return os.path.exists(expanded)

# Custom style for questionary
custom_style = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'fg:white bold'),
    ('answer', 'fg:green bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:green'),
    ('separator', 'fg:gray'),
    ('instruction', 'fg:gray'),
    ('text', 'fg:white'),
])

# All available commands with descriptions
COMMANDS = [
    # Repository commands
    {"name": "repo index", "desc": "Index a repository", "category": "Repository"},
    {"name": "repo search", "desc": "Search indexed repositories", "category": "Repository"},
    {"name": "repo list", "desc": "List all indexed repositories", "category": "Repository"},
    {"name": "repo docs", "desc": "Get documentation for a repository", "category": "Repository"},
    # Code commands
    {"name": "code analyze", "desc": "Analyze code structure and extract symbols", "category": "Code"},
    {"name": "code find", "desc": "Find symbols by name pattern", "category": "Code"},
    {"name": "code info", "desc": "Get detailed symbol information", "category": "Code"},
    {"name": "code symbols", "desc": "List all symbols in a file", "category": "Code"},
    # Config commands
    {"name": "config show", "desc": "Show current configuration", "category": "Config"},
    # Special
    {"name": "help", "desc": "Show help information", "category": "System"},
    {"name": "quit", "desc": "Exit interactive mode", "category": "System"},
]


def show_banner():
    """Display the welcome banner."""
    banner = Text()
    banner.append("repo-ctx", style="bold cyan")
    banner.append(f" v{__version__}\n", style="dim")
    banner.append("Repository Context Manager", style="white")

    console.print(Panel(
        banner,
        box=box.ROUNDED,
        padding=(0, 2),
        border_style="cyan"
    ))
    console.print()


def show_help():
    """Display help information."""
    table = Table(
        title="Available Commands",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan"
    )
    table.add_column("Command", style="green")
    table.add_column("Description", style="white")
    table.add_column("Category", style="dim")

    for cmd in COMMANDS:
        if cmd["name"] not in ["help", "quit"]:
            table.add_row(cmd["name"], cmd["desc"], cmd["category"])

    console.print(table)
    console.print()
    console.print("[dim]Type a command or use arrow keys to select. Press Ctrl+C to exit.[/dim]")
    console.print()


def command_selector() -> Optional[str]:
    """Show command palette for selection."""
    choices = []
    for cmd in COMMANDS:
        # Format: "command - description"
        label = f"{cmd['name']:<20} {cmd['desc']}"
        choices.append(questionary.Choice(title=label, value=cmd["name"]))

    try:
        result = questionary.select(
            "Select a command:",
            choices=choices,
            style=custom_style,
            use_shortcuts=False,
            use_arrow_keys=True,
            use_jk_keys=True,
        ).ask()
        return result
    except KeyboardInterrupt:
        return "quit"


async def execute_repo_index():
    """Execute repo index command."""
    path = await questionary.text(
        "Repository path (owner/repo or local path):",
        style=custom_style
    ).ask_async()

    if not path:
        console.print("[yellow]Cancelled[/yellow]")
        return

    provider = await questionary.select(
        "Provider:",
        choices=["auto", "github", "gitlab", "local"],
        default="auto",
        style=custom_style
    ).ask_async()

    console.print(f"\n[cyan]Indexing {path}...[/cyan]")

    try:
        from ..config import Config
        from ..core import GitLabContext

        config = Config.load()
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
                return
            project = parts[-1]
            group = "/".join(parts[:-1])
            provider_type = None if provider == "auto" else provider

        await context.index_repository(group, project, provider_type=provider_type)
        console.print(f"[green]Successfully indexed {path}[/green]")

    except Exception as e:
        print_error(e)


async def execute_repo_search():
    """Execute repo search command."""
    query = await questionary.text(
        "Search query:",
        style=custom_style
    ).ask_async()

    if not query:
        console.print("[yellow]Cancelled[/yellow]")
        return

    console.print(f"\n[cyan]Searching for '{query}'...[/cyan]\n")

    try:
        from ..config import Config
        from ..core import GitLabContext

        config = Config.load()
        context = GitLabContext(config)
        await context.init()

        results = await context.fuzzy_search_libraries(query, limit=10)

        if not results:
            console.print(f"[yellow]No repositories found matching '{query}'[/yellow]")
            return

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold")
        table.add_column("#", style="dim")
        table.add_column("Repository", style="green")
        table.add_column("Description", style="white")
        table.add_column("Match", style="cyan")

        for i, result in enumerate(results, 1):
            table.add_row(
                str(i),
                result.library_id,
                (result.description or "")[:50],
                f"{result.match_type} ({result.score:.0%})"
            )

        console.print(table)

    except Exception as e:
        print_error(e)


async def execute_repo_list():
    """Execute repo list command."""
    console.print("\n[cyan]Fetching indexed repositories...[/cyan]\n")

    try:
        from ..config import Config
        from ..core import GitLabContext

        config = Config.load()
        context = GitLabContext(config)
        await context.init()

        libraries = await context.list_all_libraries()

        if not libraries:
            console.print("[yellow]No repositories indexed yet.[/yellow]")
            console.print("[dim]Use 'repo index' to index repositories.[/dim]")
            return

        table = Table(
            title=f"Indexed Repositories ({len(libraries)} total)",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold"
        )
        table.add_column("#", style="dim")
        table.add_column("Repository", style="green")
        table.add_column("Description", style="white")
        table.add_column("Last Indexed", style="dim")

        for i, lib in enumerate(libraries, 1):
            lib_id = f"/{lib.group_name}/{lib.project_name}"
            table.add_row(
                str(i),
                lib_id,
                (lib.description or "")[:40],
                str(lib.last_indexed)[:10] if lib.last_indexed else "-"
            )

        console.print(table)

    except Exception as e:
        print_error(e)


async def execute_repo_docs():
    """Execute repo docs command."""
    # Fetch indexed repos for selection
    console.print("[dim]Fetching indexed repositories...[/dim]")
    indexed_repos = await get_indexed_repos()

    if not indexed_repos:
        console.print("[yellow]No repositories indexed yet.[/yellow]")
        console.print("[dim]Use 'repo index' to index a repository first.[/dim]")
        return

    # Let user select from indexed repos
    repo_id = await questionary.select(
        "Select repository:",
        choices=indexed_repos,
        style=custom_style
    ).ask_async()

    if not repo_id:
        console.print("[yellow]Cancelled[/yellow]")
        return

    topic = await questionary.text(
        "Topic filter (optional, press Enter to skip):",
        style=custom_style
    ).ask_async()

    console.print(f"\n[cyan]Fetching documentation for {repo_id}...[/cyan]\n")

    try:
        from ..config import Config
        from ..core import GitLabContext

        config = Config.load()
        context = GitLabContext(config)
        await context.init()

        result = await context.get_documentation(
            repo_id,
            topic=topic if topic else None,
            max_tokens=8000
        )

        content = result["content"][0]["text"]
        console.print(Panel(content[:2000] + "..." if len(content) > 2000 else content, title=repo_id))

    except Exception as e:
        print_error(e)


async def execute_code_analyze():
    """Execute code analyze command."""
    # Ask for source type
    source_type = await questionary.select(
        "Analyze from:",
        choices=[
            questionary.Choice("Local path", value="local"),
            questionary.Choice("Indexed repository", value="indexed"),
        ],
        style=custom_style
    ).ask_async()

    if not source_type:
        console.print("[yellow]Cancelled[/yellow]")
        return

    files = {}
    source_name = ""

    if source_type == "indexed":
        # Get indexed repos
        indexed_repos = await get_indexed_repos()
        if not indexed_repos:
            console.print("[yellow]No repositories indexed yet.[/yellow]")
            console.print("[dim]Use 'repo index' to index a repository first.[/dim]")
            return

        repo_id = await questionary.select(
            "Select repository:",
            choices=indexed_repos,
            style=custom_style
        ).ask_async()

        if not repo_id:
            console.print("[yellow]Cancelled[/yellow]")
            return

        source_name = repo_id
        console.print(f"\n[cyan]Analyzing {repo_id} (fetching if needed)...[/cyan]")

        symbols, lib, error = await get_or_analyze_repo(repo_id)

        if error:
            print_error(error)
            return

        if not symbols:
            console.print(f"[yellow]No symbols found in {repo_id}[/yellow]")
            return

        # Get statistics
        from ..analysis import CodeAnalyzer
        analyzer = CodeAnalyzer()
        stats = analyzer.get_statistics(symbols)

        console.print(f"\n[bold]Analysis: {source_name}[/bold]\n")
        console.print(f"[green]Total symbols:[/green] {stats['total_symbols']}")
        console.print()

        if stats['by_type']:
            table = Table(title="Symbols by Type", box=box.SIMPLE)
            table.add_column("Type", style="cyan")
            table.add_column("Count", style="white")
            for stype, count in stats['by_type'].items():
                table.add_row(stype, str(count))
            console.print(table)

        return  # Done for indexed repos

    else:  # local
        path = await questionary.text(
            "Path to analyze:",
            default=".",
            style=custom_style
        ).ask_async()

        if not path:
            console.print("[yellow]Cancelled[/yellow]")
            return

        source_name = path
        console.print(f"\n[cyan]Analyzing {path}...[/cyan]\n")

        try:
            from pathlib import Path
            from ..analysis import CodeAnalyzer

            analyzer = CodeAnalyzer()
            path_obj = Path(path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{path}' does not exist[/red]")
                return

            # Collect files
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

        except Exception as e:
            print_error(e)
            return

    if not files:
        console.print(f"[yellow]No supported source files found[/yellow]")
        return

    # Analyze
    try:
        from ..analysis import CodeAnalyzer
        analyzer = CodeAnalyzer()

        results = analyzer.analyze_files(files)
        all_symbols = analyzer.aggregate_symbols(results)
        stats = analyzer.get_statistics(all_symbols)

        # Summary
        console.print(f"[bold]Analysis: {source_name}[/bold]\n")
        console.print(f"[green]Files analyzed:[/green] {len(files)}")
        console.print(f"[green]Total symbols:[/green] {stats['total_symbols']}")
        console.print()

        # By type
        if stats['by_type']:
            table = Table(title="Symbols by Type", box=box.SIMPLE)
            table.add_column("Type", style="cyan")
            table.add_column("Count", style="white")
            for stype, count in stats['by_type'].items():
                table.add_row(stype, str(count))
            console.print(table)

    except Exception as e:
        print_error(e)


async def execute_code_find():
    """Execute code find command."""
    # Ask for source type
    source_type = await questionary.select(
        "Search in:",
        choices=[
            questionary.Choice("Local path", value="local"),
            questionary.Choice("Indexed repository", value="indexed"),
        ],
        style=custom_style
    ).ask_async()

    if not source_type:
        console.print("[yellow]Cancelled[/yellow]")
        return

    files = {}
    source_name = ""

    if source_type == "indexed":
        indexed_repos = await get_indexed_repos()
        if not indexed_repos:
            console.print("[yellow]No repositories indexed yet.[/yellow]")
            console.print("[dim]Use 'repo index' to index a repository first.[/dim]")
            return

        repo_id = await questionary.select(
            "Select repository:",
            choices=indexed_repos,
            style=custom_style
        ).ask_async()

        if not repo_id:
            console.print("[yellow]Cancelled[/yellow]")
            return

        source_name = repo_id

        query = await questionary.text(
            "Symbol name or pattern:",
            style=custom_style
        ).ask_async()

        if not query:
            console.print("[yellow]Cancelled[/yellow]")
            return

        console.print(f"\n[cyan]Searching in {repo_id}...[/cyan]")

        symbols, lib, error = await get_or_analyze_repo(repo_id)

        if error:
            print_error(error)
            return

        if not symbols:
            console.print(f"[yellow]No symbols in {repo_id}[/yellow]")
            return

        # Search
        query_lower = query.lower()
        matching = [s for s in symbols if query_lower in s.name.lower()]

        if not matching:
            console.print(f"[yellow]No symbols found matching '{query}'[/yellow]")
            return

        console.print(f"[green]Found {len(matching)} matching symbol(s) in {source_name}[/green]\n")

        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("Symbol", style="green")
        table.add_column("Type", style="cyan")
        table.add_column("File", style="dim")
        table.add_column("Line", style="dim")

        for symbol in matching[:20]:
            table.add_row(
                symbol.name,
                symbol.symbol_type.value,
                symbol.file_path.split("/")[-1],
                str(symbol.line_start or "-")
            )

        console.print(table)

        if len(matching) > 20:
            console.print(f"[dim]... and {len(matching) - 20} more[/dim]")

        return  # Done for indexed repos

    else:  # local
        path = await questionary.text(
            "Path to search:",
            default=".",
            style=custom_style
        ).ask_async()

        if not path:
            console.print("[yellow]Cancelled[/yellow]")
            return

        query = await questionary.text(
            "Symbol name or pattern:",
            style=custom_style
        ).ask_async()

        if not query:
            console.print("[yellow]Cancelled[/yellow]")
            return

        source_name = path
        console.print(f"\n[cyan]Searching in {path}...[/cyan]")

        try:
            from pathlib import Path
            from ..analysis import CodeAnalyzer

            analyzer = CodeAnalyzer()
            path_obj = Path(path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{path}' does not exist[/red]")
                return

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

        except Exception as e:
            print_error(e)
            return

        if not files:
            console.print(f"[yellow]No supported source files found[/yellow]")
            return

        # Analyze and search
        try:
            from ..analysis import CodeAnalyzer
            analyzer = CodeAnalyzer()

            console.print(f"[cyan]Searching for '{query}'...[/cyan]\n")

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            query_lower = query.lower()
            matching = [s for s in all_symbols if query_lower in s.name.lower()]

            if not matching:
                console.print(f"[yellow]No symbols found matching '{query}'[/yellow]")
                return

            console.print(f"[green]Found {len(matching)} matching symbol(s) in {source_name}[/green]\n")

            table = Table(box=box.ROUNDED, show_header=True)
            table.add_column("Symbol", style="green")
            table.add_column("Type", style="cyan")
            table.add_column("File", style="dim")
            table.add_column("Line", style="dim")

            for symbol in matching[:20]:
                table.add_row(
                    symbol.name,
                    symbol.symbol_type.value,
                    symbol.file_path.split("/")[-1],
                    str(symbol.line_start or "-")
                )

            console.print(table)

            if len(matching) > 20:
                console.print(f"[dim]... and {len(matching) - 20} more[/dim]")

        except Exception as e:
            print_error(e)


async def execute_code_info():
    """Execute code info command."""
    # Ask for source type
    source_type = await questionary.select(
        "Search in:",
        choices=[
            questionary.Choice("Local path", value="local"),
            questionary.Choice("Indexed repository", value="indexed"),
        ],
        style=custom_style
    ).ask_async()

    if not source_type:
        console.print("[yellow]Cancelled[/yellow]")
        return

    files = {}

    if source_type == "indexed":
        indexed_repos = await get_indexed_repos()
        if not indexed_repos:
            console.print("[yellow]No repositories indexed yet.[/yellow]")
            console.print("[dim]Use 'repo index' to index a repository first.[/dim]")
            return

        repo_id = await questionary.select(
            "Select repository:",
            choices=indexed_repos,
            style=custom_style
        ).ask_async()

        if not repo_id:
            console.print("[yellow]Cancelled[/yellow]")
            return

        name = await questionary.text(
            "Symbol name:",
            style=custom_style
        ).ask_async()

        if not name:
            console.print("[yellow]Cancelled[/yellow]")
            return

        console.print(f"\n[cyan]Looking up '{name}' in {repo_id}...[/cyan]")

        symbols, lib, error = await get_or_analyze_repo(repo_id)

        if error:
            print_error(error)
            return

        if not symbols:
            console.print(f"[yellow]No symbols in {repo_id}[/yellow]")
            return

        # Find exact match
        matching = [s for s in symbols if s.name == name or s.qualified_name == name]

        if not matching:
            console.print(f"[yellow]Symbol '{name}' not found[/yellow]")
            return

        symbol = matching[0]

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

        return  # Done for indexed repos

    else:  # local
        path = await questionary.text(
            "Path to search:",
            default=".",
            style=custom_style
        ).ask_async()

        if not path:
            console.print("[yellow]Cancelled[/yellow]")
            return

        name = await questionary.text(
            "Symbol name:",
            style=custom_style
        ).ask_async()

        if not name:
            console.print("[yellow]Cancelled[/yellow]")
            return

        console.print(f"\n[cyan]Looking up '{name}' in {path}...[/cyan]")

        try:
            from pathlib import Path
            from ..analysis import CodeAnalyzer

            analyzer = CodeAnalyzer()
            path_obj = Path(path)

            if not path_obj.exists():
                console.print(f"[red]Error: Path '{path}' does not exist[/red]")
                return

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
                console.print(f"[yellow]No supported source files found[/yellow]")
                return

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            matching = [s for s in all_symbols if s.name == name or s.qualified_name == name]

            if not matching:
                console.print(f"[yellow]Symbol '{name}' not found[/yellow]")
                return

            symbol = matching[0]

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
            print_error(e)


async def execute_code_symbols():
    """Execute code symbols command."""
    # Ask for source type
    source_type = await questionary.select(
        "List symbols from:",
        choices=[
            questionary.Choice("Local file", value="local"),
            questionary.Choice("File in indexed repository", value="indexed"),
        ],
        style=custom_style
    ).ask_async()

    if not source_type:
        console.print("[yellow]Cancelled[/yellow]")
        return

    code = ""
    file_path = ""
    language = ""

    if source_type == "indexed":
        indexed_repos = await get_indexed_repos()
        if not indexed_repos:
            console.print("[yellow]No repositories indexed yet.[/yellow]")
            console.print("[dim]Use 'repo index' to index a repository first.[/dim]")
            return

        repo_id = await questionary.select(
            "Select repository:",
            choices=indexed_repos,
            style=custom_style
        ).ask_async()

        if not repo_id:
            console.print("[yellow]Cancelled[/yellow]")
            return

        console.print(f"\n[cyan]Fetching file list from {repo_id}...[/cyan]")

        try:
            from ..config import Config
            from ..core import GitLabContext
            from ..analysis import CodeAnalyzer
            from ..providers import ProviderFactory

            config = Config.load()
            context = GitLabContext(config)
            await context.init()

            group, project = parse_repo_id(repo_id)
            lib = await context.storage.get_library(group, project)
            if not lib:
                console.print(f"[red]Error: Repository {repo_id} not found in index[/red]")
                return

            provider = ProviderFactory.from_config(config, lib.provider)
            project_path = f"{group}/{project}"
            project_info = await provider.get_project(project_path)
            ref = await provider.get_default_branch(project_info)
            all_files = await provider.get_file_tree(project_info, ref)

            # Filter to source files only
            analyzer = CodeAnalyzer()
            source_files = [f for f in all_files if analyzer.detect_language(f)]

            if not source_files:
                console.print(f"[yellow]No supported source files in {repo_id}[/yellow]")
                return

            # Let user select a file
            file_path = await questionary.select(
                "Select file:",
                choices=source_files[:50],  # Limit to 50 for UI
                style=custom_style
            ).ask_async()

            if not file_path:
                console.print("[yellow]Cancelled[/yellow]")
                return

            console.print(f"\n[cyan]Fetching {file_path}...[/cyan]")

            file_content = await provider.read_file(project_info, file_path, ref)
            code = file_content.content
            language = analyzer.detect_language(file_path)

        except Exception as e:
            print_error(e)
            return

    else:  # local
        file_path = await questionary.text(
            "Source file path:",
            style=custom_style
        ).ask_async()

        if not file_path:
            console.print("[yellow]Cancelled[/yellow]")
            return

        console.print(f"\n[cyan]Analyzing {file_path}...[/cyan]\n")

        try:
            from pathlib import Path
            from ..analysis import CodeAnalyzer

            path_obj = Path(file_path)

            if not path_obj.exists():
                console.print(f"[red]Error: File '{file_path}' does not exist[/red]")
                return

            if not path_obj.is_file():
                console.print(f"[red]Error: '{file_path}' is not a file[/red]")
                return

            analyzer = CodeAnalyzer()
            language = analyzer.detect_language(str(path_obj))

            if not language:
                console.print(f"[red]Error: Unsupported file type[/red]")
                return

            with open(path_obj, 'r', encoding='utf-8') as f:
                code = f.read()

        except Exception as e:
            print_error(e)
            return

    if not code:
        console.print(f"[yellow]No content to analyze[/yellow]")
        return

    # Analyze
    try:
        from ..analysis import CodeAnalyzer
        analyzer = CodeAnalyzer()

        symbols = analyzer.analyze_file(code, file_path)

        if not symbols:
            console.print(f"[yellow]No symbols found in '{file_path}'[/yellow]")
            return

        console.print(f"\n[bold]{file_path}[/bold]")
        console.print(f"[green]Language:[/green] {language}")
        console.print(f"[green]Symbols:[/green] {len(symbols)}\n")

        # Group by type
        by_type = {}
        for symbol in symbols:
            stype = symbol.symbol_type.value
            if stype not in by_type:
                by_type[stype] = []
            by_type[stype].append(symbol)

        for stype, type_symbols in sorted(by_type.items()):
            console.print(f"[bold cyan]{stype.title()}s ({len(type_symbols)})[/bold cyan]")
            for symbol in sorted(type_symbols, key=lambda s: s.line_start or 0):
                vis = "🔒" if symbol.visibility == "private" else "🔓"
                console.print(f"  {vis} {symbol.name}", end="")
                if symbol.line_start:
                    console.print(f" [dim](line {symbol.line_start})[/dim]", end="")
                console.print()
            console.print()

    except Exception as e:
        print_error(e)


async def execute_config_show():
    """Execute config show command."""
    console.print("\n[cyan]Current Configuration[/cyan]\n")

    try:
        import os
        from ..config import Config

        config = Config.load()

        table = Table(box=box.ROUNDED, show_header=True)
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Source", style="dim")

        # GitLab
        gitlab_url = config.gitlab_url or os.environ.get("GITLAB_URL", "")
        table.add_row("GitLab URL", gitlab_url or "[dim]not set[/dim]",
                      "env" if os.environ.get("GITLAB_URL") else "config")

        gitlab_token = config.gitlab_token or os.environ.get("GITLAB_TOKEN", "")
        table.add_row("GitLab Token", "***" if gitlab_token else "[dim]not set[/dim]",
                      "env" if os.environ.get("GITLAB_TOKEN") else "config")

        # GitHub
        github_url = config.github_url or "https://api.github.com"
        table.add_row("GitHub URL", github_url, "default")

        github_token = config.github_token or os.environ.get("GITHUB_TOKEN", "")
        table.add_row("GitHub Token", "***" if github_token else "[dim]not set[/dim]",
                      "env" if os.environ.get("GITHUB_TOKEN") else "config")

        # Storage
        storage_path = config.storage_path
        table.add_row("Storage Path", storage_path, "config")

        console.print(table)

        # Config file locations
        console.print("\n[dim]Config file locations (in priority order):[/dim]")
        locations = [
            "~/.config/repo-ctx/config.yaml",
            "~/.repo-ctx/config.yaml",
            "./config.yaml"
        ]
        for loc in locations:
            expanded = os.path.expanduser(loc)
            exists = os.path.exists(expanded)
            status = "[green]found[/green]" if exists else "[dim]not found[/dim]"
            console.print(f"  {loc} {status}")

    except Exception as e:
        print_error(e)


async def execute_command(cmd: str):
    """Execute the selected command."""
    commands = {
        "repo index": execute_repo_index,
        "repo search": execute_repo_search,
        "repo list": execute_repo_list,
        "repo docs": execute_repo_docs,
        "code analyze": execute_code_analyze,
        "code find": execute_code_find,
        "code info": execute_code_info,
        "code symbols": execute_code_symbols,
        "config show": execute_config_show,
    }

    if cmd in commands:
        await commands[cmd]()
    elif cmd == "help":
        show_help()
    elif cmd == "quit":
        return False

    return True


def run_interactive():
    """Run the interactive command palette."""
    show_banner()
    console.print("[dim]Type to filter commands, use arrows to navigate, Enter to select[/dim]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")

    try:
        while True:
            cmd = command_selector()

            if cmd is None or cmd == "quit":
                console.print("\n[cyan]Goodbye![/cyan]")
                break

            console.print()

            # Run async command
            should_continue = asyncio.run(execute_command(cmd))

            if not should_continue:
                console.print("\n[cyan]Goodbye![/cyan]")
                break

            console.print()

    except KeyboardInterrupt:
        console.print("\n\n[cyan]Goodbye![/cyan]")
    except EOFError:
        console.print("\n\n[cyan]Goodbye![/cyan]")
