"""Entry point for repo-ctx."""
import asyncio
import argparse
from .mcp_server import serve
from .core import GitLabContext
from .config import Config


def main():
    parser = argparse.ArgumentParser(
        description="Repository Context - Repository documentation indexer (MCP server, CLI, library)",
        epilog="""
Configuration priority (highest to lowest):
  1. Command-line arguments (--gitlab-url, --gitlab-token, etc.)
  2. Specified config file (--config)
  3. Environment variables (GITLAB_URL, GITLAB_TOKEN)
  4. Standard config locations (~/.config/repo-ctx/config.yaml, ~/.repo-ctx/config.yaml, ./config.yaml)
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
        "--storage-path",
        help="Path to SQLite database file (default: ~/.repo-ctx/context.db)"
    )

    # Actions
    parser.add_argument(
        "--index",
        help="Index a repository (format: group/project or group/subgroup/project)"
    )

    args = parser.parse_args()

    if args.index:
        # Index mode
        asyncio.run(index_repository(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            storage_path=args.storage_path,
            repo=args.index
        ))
    else:
        # Server mode
        asyncio.run(serve(
            config_path=args.config,
            gitlab_url=args.gitlab_url,
            gitlab_token=args.gitlab_token,
            storage_path=args.storage_path
        ))


async def index_repository(
    config_path: str = None,
    gitlab_url: str = None,
    gitlab_token: str = None,
    storage_path: str = None,
    repo: str = None
):
    """Index a repository."""
    parts = repo.split("/")
    if len(parts) < 2:
        print("Error: Repository must be in format group/project or group/subgroup/project")
        return

    # Handle nested groups: everything except last part is the group
    project = parts[-1]
    group = "/".join(parts[:-1])

    try:
        config = Config.load(
            config_path=config_path,
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
            storage_path=storage_path
        )
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    context = GitLabContext(config)
    await context.init()

    print(f"Indexing {group}/{project}...")
    try:
        await context.index_repository(group, project)
        print(f"Successfully indexed {group}/{project}")
    except Exception as e:
        print(f"Error indexing repository: {e}")


if __name__ == "__main__":
    main()
