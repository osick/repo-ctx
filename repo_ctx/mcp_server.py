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
    storage_path: str = None
):
    """Run MCP server.

    Args:
        config_path: Optional path to config file
        gitlab_url: Optional GitLab URL (overrides config file)
        gitlab_token: Optional GitLab token (overrides config file)
        storage_path: Optional storage path (overrides config file)
    """
    # Load config with priority: CLI args > env vars > config files
    try:
        config = Config.load(
            config_path=config_path,
            gitlab_url=gitlab_url,
            gitlab_token=gitlab_token,
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
                name="gitlab-search-libraries",
                description="Search for GitLab libraries/projects by name. Returns matching libraries with their IDs and available versions.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "libraryName": {
                            "type": "string",
                            "description": "Library name to search for"
                        }
                    },
                    "required": ["libraryName"]
                }
            ),
            Tool(
                name="gitlab-fuzzy-search",
                description="Fuzzy search for GitLab repositories. Returns top matches even with typos or partial names. Use this when you don't know the exact repository path.",
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
                name="gitlab-index-repository",
                description="Index a GitLab repository to make its documentation searchable. Use format: group/project or group/subgroup/project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repository": {
                            "type": "string",
                            "description": "Repository path (e.g., 'group/repo' or 'group/subgroup/repository')"
                        }
                    },
                    "required": ["repository"]
                }
            ),
            Tool(
                name="gitlab-index-group",
                description="Index all repositories in a GitLab group. Optionally include subgroups.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": "Group path (e.g., 'groupname')"
                        },
                        "includeSubgroups": {
                            "type": "boolean",
                            "description": "Include subgroups (default: true)",
                            "default": True
                        }
                    },
                    "required": ["group"]
                }
            ),
            Tool(
                name="gitlab-get-docs",
                description="Retrieve documentation for a specific GitLab library. Supports topic filtering and pagination.",
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
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "gitlab-search-libraries":
            library_name = arguments["libraryName"]
            results = await context.search_libraries(library_name)
            
            output = []
            output.append("Available Libraries (search results):\n\n")
            
            for result in results:
                output.append(f"- Library ID: {result.library_id}\n")
                output.append(f"  Name: {result.name}\n")
                output.append(f"  Description: {result.description}\n")
                output.append(f"  Versions: {', '.join(result.versions)}\n")
                output.append("\n")
            
            if not results:
                output.append(f"No libraries found matching '{library_name}'.\n")
                output.append("Make sure the repository has been indexed first.\n")
            
            return [TextContent(type="text", text="".join(output))]
        
        elif name == "gitlab-fuzzy-search":
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
                output.append("Try a different search term or index repositories first using gitlab-index-repository or gitlab-index-group.\n")
            else:
                output.append(f"\nTo get documentation, use gitlab-get-docs with one of the Library IDs above.\n")
            
            return [TextContent(type="text", text="".join(output))]
        
        elif name == "gitlab-index-repository":
            repository = arguments["repository"]
            parts = repository.split("/")
            if len(parts) < 2:
                return [TextContent(type="text", text=f"Error: Repository must be in format group/project or group/subgroup/project")]
            
            project = parts[-1]
            group = "/".join(parts[:-1])
            
            try:
                await context.index_repository(group, project)
                return [TextContent(type="text", text=f"Successfully indexed {repository}. You can now search for it using gitlab-fuzzy-search or gitlab-get-docs.")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error indexing {repository}: {str(e)}")]
        
        elif name == "gitlab-index-group":
            group = arguments["group"]
            include_subgroups = arguments.get("includeSubgroups", True)
            
            try:
                results = await context.index_group(group, include_subgroups)
                output = []
                output.append(f"Indexed group '{group}':\n\n")
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
        
        elif name == "gitlab-get-docs":
            library_id = arguments["libraryId"]
            topic = arguments.get("topic")
            page = arguments.get("page", 1)
            
            try:
                result = await context.get_documentation(library_id, topic, page)
                return [TextContent(type="text", text=result["content"][0]["text"])]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
