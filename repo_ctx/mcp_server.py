"""MCP server implementation - thin shell delegating to mcp_tools_ctx."""
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .config import Config
from .mcp_tools_ctx import get_ctx_tools, handle_ctx_tool
from .mcp import MCPServerContext


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
        sys.stderr.write(f"Configuration error: {e}\n")
        raise

    context = MCPServerContext(config)
    await context.init()

    server = Server("repo-ctx")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return get_ctx_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        result = await handle_ctx_tool(name, arguments, context)
        if result is not None:
            return result
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
