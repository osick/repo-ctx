"""Entry point for repo-ctx."""
import asyncio
import argparse
import sys
from datetime import datetime
from .mcp_server import serve
from .core import GitLabContext
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
        choices=["gitlab", "github", "auto"],
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
        help="Page number (default: 1)"
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
            format_type=args.format
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
            page=args.page
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
        print(f"Configuration error: {e}")
        return

    context = GitLabContext(config)
    await context.init()

    # Show which provider will be used
    if provider:
        print(f"Using provider: {provider}")
    else:
        print(f"Auto-detecting provider from path format...")

    print(f"Indexing {group}/{project}...")
    try:
        await context.index_repository(group, project, provider_type=provider)
        print(f"✓ Successfully indexed {group}/{project}")
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
    format_type: str = "detailed"
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
        libraries = await context.storage.get_all_libraries()

        if not libraries:
            print("No indexed repositories found.")
            print("\nTo index a repository, run:")
            print("  repo-ctx --index group/project")
            return

        print(f"Indexed Repositories ({len(libraries)}):\n")

        if format_type == "simple":
            for lib in libraries:
                print(f"  - {lib.group_name}/{lib.project_name}")
        else:  # detailed
            for i, lib in enumerate(libraries, 1):
                print(f"{i}. {lib.group_name}/{lib.project_name}")
                if lib.description:
                    desc = lib.description[:100] + "..." if len(lib.description) > 100 else lib.description
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
    page: int = 1
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
        print()

        docs = await context.get_documentation(repository, topic=topic, page=page)

        metadata = docs["metadata"]
        content = docs["content"][0]["text"]

        print(f"Library: {metadata['library']}")
        print(f"Version: {metadata['version']}")
        print(f"Page: {metadata['page']}")
        print(f"Documents: {metadata['documents_count']}")
        print("=" * 80)
        print()
        print(content)

        if metadata['documents_count'] >= 10:
            print()
            print(f"More documents available. Use --page {page + 1} to see next page.")

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


if __name__ == "__main__":
    main()
