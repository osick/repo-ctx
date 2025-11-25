"""MCP server implementation."""
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .core import GitLabContext
from .config import Config


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
                description="Retrieve documentation for a specific indexed repository. Supports topic filtering and pagination. Works with any indexed repository (local, GitHub, GitLab).",
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
                        "page": {
                            "type": "integer",
                            "description": "Page number for pagination (default: 1)",
                            "default": 1
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

            try:
                result = await context.get_documentation(library_id, topic, page)
                return [TextContent(type="text", text=result["content"][0]["text"])]
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

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
