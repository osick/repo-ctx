"""Tests for ctx- prefixed MCP tools."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from mcp.types import Tool, TextContent

from repo_ctx.mcp_tools_ctx import get_ctx_tools, handle_ctx_tool


class TestGetCtxTools:
    """Tests for get_ctx_tools function."""

    def test_returns_list_of_tools(self):
        """Should return a list of Tool objects."""
        tools = get_ctx_tools()
        assert isinstance(tools, list)
        assert all(isinstance(t, Tool) for t in tools)

    def test_expected_tool_count(self):
        """Should return 18 ctx- tools."""
        tools = get_ctx_tools()
        assert len(tools) == 18

    def test_all_tools_have_ctx_prefix(self):
        """All tools should have ctx- prefix."""
        tools = get_ctx_tools()
        for tool in tools:
            assert tool.name.startswith("ctx-"), f"Tool {tool.name} missing ctx- prefix"

    def test_expected_tool_names(self):
        """All expected tools should be present."""
        tools = get_ctx_tools()
        tool_names = {t.name for t in tools}
        expected = {
            "ctx-index", "ctx-list", "ctx-search", "ctx-docs",
            "ctx-analyze", "ctx-symbol", "ctx-symbols", "ctx-graph",
            "ctx-query", "ctx-export", "ctx-status",
            "ctx-dsm", "ctx-cycles", "ctx-layers", "ctx-architecture",
            "ctx-metrics", "ctx-llmstxt", "ctx-dump"
        }
        assert tool_names == expected

    def test_tools_have_descriptions(self):
        """All tools should have descriptions."""
        tools = get_ctx_tools()
        for tool in tools:
            assert tool.description, f"Tool {tool.name} missing description"
            assert len(tool.description) > 20, f"Tool {tool.name} description too short"

    def test_tools_have_input_schema(self):
        """All tools should have input schema."""
        tools = get_ctx_tools()
        for tool in tools:
            assert tool.inputSchema, f"Tool {tool.name} missing inputSchema"
            assert "type" in tool.inputSchema
            assert tool.inputSchema["type"] == "object"


class TestCtxIndexTool:
    """Tests for ctx-index tool schema."""

    def test_schema_properties(self):
        """ctx-index should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-index")
        props = tool.inputSchema["properties"]

        assert "repository" in props
        assert "provider" in props
        assert "group" in props
        assert "include_subgroups" in props

    def test_required_fields(self):
        """ctx-index should require repository."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-index")
        assert tool.inputSchema["required"] == ["repository"]

    def test_provider_enum(self):
        """Provider should have correct enum values."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-index")
        provider = tool.inputSchema["properties"]["provider"]
        assert set(provider["enum"]) == {"auto", "github", "gitlab", "local"}


class TestCtxListTool:
    """Tests for ctx-list tool schema."""

    def test_schema_properties(self):
        """ctx-list should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-list")
        props = tool.inputSchema["properties"]

        assert "provider" in props

    def test_no_required_fields(self):
        """ctx-list should not require any fields."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-list")
        assert "required" not in tool.inputSchema or tool.inputSchema.get("required", []) == []


class TestCtxSearchTool:
    """Tests for ctx-search tool schema."""

    def test_schema_properties(self):
        """ctx-search should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-search")
        props = tool.inputSchema["properties"]

        assert "query" in props
        assert "mode" in props
        assert "target" in props
        assert "exact" in props
        assert "limit" in props
        assert "type" in props
        assert "lang" in props

    def test_required_fields(self):
        """ctx-search should require query."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-search")
        assert tool.inputSchema["required"] == ["query"]

    def test_mode_enum(self):
        """Mode should have correct enum values."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-search")
        mode = tool.inputSchema["properties"]["mode"]
        assert set(mode["enum"]) == {"repos", "symbols"}


class TestCtxDocsTool:
    """Tests for ctx-docs tool schema."""

    def test_schema_properties(self):
        """ctx-docs should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-docs")
        props = tool.inputSchema["properties"]

        assert "repository" in props
        assert "topic" in props
        assert "include" in props
        assert "max_tokens" in props
        assert "mode" in props
        assert "format" in props
        assert "query" in props
        assert "refresh" in props

    def test_required_fields(self):
        """ctx-docs should require repository."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-docs")
        assert tool.inputSchema["required"] == ["repository"]

    def test_format_enum(self):
        """Format should have correct enum values."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-docs")
        fmt = tool.inputSchema["properties"]["format"]
        assert set(fmt["enum"]) == {"standard", "llmstxt"}


class TestCtxAnalyzeTool:
    """Tests for ctx-analyze tool schema."""

    def test_schema_properties(self):
        """ctx-analyze should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-analyze")
        props = tool.inputSchema["properties"]

        assert "target" in props
        assert "lang" in props
        assert "type" in props
        assert "include_private" in props
        assert "refresh" in props

    def test_required_fields(self):
        """ctx-analyze should require target."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-analyze")
        assert tool.inputSchema["required"] == ["target"]

    def test_type_enum(self):
        """Type should have correct enum values."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-analyze")
        sym_type = tool.inputSchema["properties"]["type"]
        assert set(sym_type["enum"]) == {"function", "class", "method", "interface", "enum"}


class TestCtxSymbolTool:
    """Tests for ctx-symbol tool schema."""

    def test_schema_properties(self):
        """ctx-symbol should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-symbol")
        props = tool.inputSchema["properties"]

        assert "name" in props
        assert "target" in props

    def test_required_fields(self):
        """ctx-symbol should require name."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-symbol")
        assert tool.inputSchema["required"] == ["name"]


class TestCtxSymbolsTool:
    """Tests for ctx-symbols tool schema."""

    def test_schema_properties(self):
        """ctx-symbols should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-symbols")
        props = tool.inputSchema["properties"]

        assert "file" in props
        assert "group_by_type" in props

    def test_required_fields(self):
        """ctx-symbols should require file."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-symbols")
        assert tool.inputSchema["required"] == ["file"]


class TestCtxGraphTool:
    """Tests for ctx-graph tool schema."""

    def test_schema_properties(self):
        """ctx-graph should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-graph")
        props = tool.inputSchema["properties"]

        assert "target" in props
        assert "type" in props
        assert "format" in props
        assert "depth" in props

    def test_required_fields(self):
        """ctx-graph should require target."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-graph")
        assert tool.inputSchema["required"] == ["target"]

    def test_type_enum(self):
        """Type should have correct enum values."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-graph")
        graph_type = tool.inputSchema["properties"]["type"]
        assert set(graph_type["enum"]) == {"file", "module", "class", "function"}


class TestCtxQueryTool:
    """Tests for ctx-query tool schema."""

    def test_schema_properties(self):
        """ctx-query should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-query")
        props = tool.inputSchema["properties"]

        assert "path" in props
        assert "query" in props

    def test_required_fields(self):
        """ctx-query should require path and query."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-query")
        assert set(tool.inputSchema["required"]) == {"path", "query"}


class TestCtxExportTool:
    """Tests for ctx-export tool schema."""

    def test_schema_properties(self):
        """ctx-export should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-export")
        props = tool.inputSchema["properties"]

        assert "path" in props
        assert "output_dir" in props
        assert "representation" in props
        assert "format" in props

    def test_required_fields(self):
        """ctx-export should require path and output_dir."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-export")
        assert set(tool.inputSchema["required"]) == {"path", "output_dir"}


class TestCtxStatusTool:
    """Tests for ctx-status tool schema."""

    def test_schema_properties(self):
        """ctx-status should have correct schema properties."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-status")
        props = tool.inputSchema["properties"]

        assert "component" in props

    def test_no_required_fields(self):
        """ctx-status should not require any fields."""
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-status")
        assert "required" not in tool.inputSchema or tool.inputSchema.get("required", []) == []


class TestHandleCtxToolRouting:
    """Tests for handle_ctx_tool routing logic."""

    @pytest.mark.asyncio
    async def test_non_ctx_tool_returns_none(self):
        """Non-ctx- tools should return None."""
        mock_context = MagicMock()
        result = await handle_ctx_tool("repo-ctx-list", {}, mock_context)
        assert result is None

    @pytest.mark.asyncio
    async def test_unknown_ctx_tool_returns_none(self):
        """Unknown ctx- tools should return None."""
        mock_context = MagicMock()
        result = await handle_ctx_tool("ctx-unknown", {}, mock_context)
        assert result is None


class TestHandleCtxListTool:
    """Tests for ctx-list handler."""

    @pytest.mark.asyncio
    async def test_list_empty(self):
        """ctx-list with no repos should show message."""
        mock_context = MagicMock()
        mock_context.list_all_libraries = AsyncMock(return_value=[])

        result = await handle_ctx_tool("ctx-list", {}, mock_context)

        assert result is not None
        assert len(result) == 1
        assert "No repositories" in result[0].text

    @pytest.mark.asyncio
    async def test_list_with_repos(self):
        """ctx-list with repos should show them."""
        mock_lib = MagicMock()
        mock_lib.group_name = "owner"
        mock_lib.project_name = "repo"
        mock_lib.description = "Test repo"

        mock_context = MagicMock()
        mock_context.list_all_libraries = AsyncMock(return_value=[mock_lib])

        result = await handle_ctx_tool("ctx-list", {}, mock_context)

        assert result is not None
        assert "/owner/repo" in result[0].text


class TestHandleCtxStatusTool:
    """Tests for ctx-status handler."""

    @pytest.mark.asyncio
    async def test_status_basic(self):
        """ctx-status should show status information."""
        mock_context = MagicMock()

        # Don't mock - use real CodeAnalyzer for integration test
        result = await handle_ctx_tool("ctx-status", {}, mock_context)

        assert result is not None
        assert "repo-ctx Status" in result[0].text
        assert "Tree-sitter" in result[0].text


class TestHandleCtxAnalyzeTool:
    """Tests for ctx-analyze handler."""

    @pytest.mark.asyncio
    async def test_analyze_local_file(self, tmp_path):
        """ctx-analyze should work on local Python file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    return "Hello"

class MyClass:
    pass
""")
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-analyze",
            {"target": str(test_file)},
            mock_context
        )

        assert result is not None
        assert "Analysis:" in result[0].text
        # Should find function and class
        assert "Total symbols" in result[0].text

    @pytest.mark.asyncio
    async def test_analyze_nonexistent_path(self):
        """ctx-analyze should error on nonexistent path."""
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-analyze",
            {"target": "/nonexistent/path/xyz"},
            mock_context
        )

        assert result is not None
        assert "Error" in result[0].text or "not found" in result[0].text.lower()


class TestHandleCtxSymbolsTool:
    """Tests for ctx-symbols handler."""

    @pytest.mark.asyncio
    async def test_symbols_local_file(self, tmp_path):
        """ctx-symbols should list symbols in a file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def func_a():
    pass

def func_b():
    pass

class MyClass:
    def method(self):
        pass
""")
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-symbols",
            {"file": str(test_file)},
            mock_context
        )

        assert result is not None
        assert "Symbols in" in result[0].text

    @pytest.mark.asyncio
    async def test_symbols_nonexistent_file(self):
        """ctx-symbols should error on nonexistent file."""
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-symbols",
            {"file": "/nonexistent/file.py"},
            mock_context
        )

        assert result is not None
        assert "not found" in result[0].text.lower()


class TestHandleCtxSearchTool:
    """Tests for ctx-search handler."""

    @pytest.mark.asyncio
    async def test_search_repos_fuzzy(self):
        """ctx-search in repos mode should use fuzzy search."""
        mock_result = MagicMock()
        mock_result.library_id = "/owner/repo"
        mock_result.description = "Test repo"
        mock_result.score = 0.9

        mock_context = MagicMock()
        mock_context.fuzzy_search_libraries = AsyncMock(return_value=[mock_result])

        result = await handle_ctx_tool(
            "ctx-search",
            {"query": "test"},
            mock_context
        )

        assert result is not None
        assert "/owner/repo" in result[0].text
        mock_context.fuzzy_search_libraries.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_repos_exact(self):
        """ctx-search with exact=true should use exact search."""
        mock_result = MagicMock()
        mock_result.library_id = "/owner/repo"
        mock_result.description = "Test repo"

        mock_context = MagicMock()
        mock_context.search_libraries = AsyncMock(return_value=[mock_result])

        result = await handle_ctx_tool(
            "ctx-search",
            {"query": "test", "exact": True},
            mock_context
        )

        assert result is not None
        mock_context.search_libraries.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_symbols_requires_target(self):
        """ctx-search in symbols mode should require target."""
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-search",
            {"query": "test", "mode": "symbols"},
            mock_context
        )

        assert result is not None
        assert "target" in result[0].text.lower() and "required" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_search_symbols_local(self, tmp_path):
        """ctx-search in symbols mode should work on local path."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class UserService:
    def get_user(self):
        pass

class AdminService:
    pass
""")
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-search",
            {"query": "User", "mode": "symbols", "target": str(test_file)},
            mock_context
        )

        assert result is not None
        assert "User" in result[0].text


class TestHandleCtxGraphTool:
    """Tests for ctx-graph handler."""

    @pytest.mark.asyncio
    async def test_graph_local_path(self, tmp_path):
        """ctx-graph should generate graph from local path."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class Parent:
    pass

class Child(Parent):
    pass
""")
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-graph",
            {"target": str(tmp_path)},
            mock_context
        )

        assert result is not None
        # Should return some graph output (JSON by default)
        assert result[0].text  # Non-empty

    @pytest.mark.asyncio
    async def test_graph_nonexistent_path(self):
        """ctx-graph should error on nonexistent path."""
        mock_context = MagicMock()

        # Use a path that starts with ./ to be detected as local (not indexed repo)
        result = await handle_ctx_tool(
            "ctx-graph",
            {"target": "./nonexistent_dir_xyz"},
            mock_context
        )

        assert result is not None
        assert "Error" in result[0].text or "not found" in result[0].text.lower()


class TestHandleCtxSymbolTool:
    """Tests for ctx-symbol handler."""

    @pytest.mark.asyncio
    async def test_symbol_found(self, tmp_path):
        """ctx-symbol should return symbol details."""
        test_file = tmp_path / "test.py"
        test_file.write_text('''
def my_function():
    """This is my function."""
    return 42
''')
        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-symbol",
            {"name": "my_function", "target": str(test_file)},
            mock_context
        )

        assert result is not None
        assert "my_function" in result[0].text

    @pytest.mark.asyncio
    async def test_symbol_not_found(self, tmp_path):
        """ctx-symbol should error when symbol not found."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def other_func(): pass")

        mock_context = MagicMock()

        result = await handle_ctx_tool(
            "ctx-symbol",
            {"name": "nonexistent", "target": str(test_file)},
            mock_context
        )

        assert result is not None
        assert "not found" in result[0].text.lower()


class TestHandleCtxQueryTool:
    """Tests for ctx-query handler."""

    @pytest.mark.asyncio
    async def test_query_without_joern(self, tmp_path):
        """ctx-query should error when Joern not installed or provide result."""
        mock_context = MagicMock()

        # Create a real directory so path exists
        test_dir = tmp_path / "src"
        test_dir.mkdir()
        (test_dir / "test.py").write_text("def hello(): pass")

        # Use real CodeAnalyzer - it will report if Joern is installed or not
        result = await handle_ctx_tool(
            "ctx-query",
            {"path": str(test_dir), "query": "cpg.method.l"},
            mock_context
        )

        assert result is not None
        # Either shows Joern not installed, or executes the query
        assert "Joern" in result[0].text or "cpg" in result[0].text.lower() or "method" in result[0].text.lower()


class TestHandleCtxExportTool:
    """Tests for ctx-export handler."""

    @pytest.mark.asyncio
    async def test_export_without_joern(self):
        """ctx-export should error when Joern not installed."""
        mock_context = MagicMock()

        # Use real CodeAnalyzer - it will report if Joern is installed or not
        result = await handle_ctx_tool(
            "ctx-export",
            {"path": "./src", "output_dir": "./out"},
            mock_context
        )

        assert result is not None
        # Either shows Joern not installed, or exports the graph
        assert "Joern" in result[0].text or "export" in result[0].text.lower()


class TestCtxDsmTool:
    """Tests for ctx-dsm tool schema."""

    def test_dsm_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-dsm" in {t.name for t in tools}

    def test_dsm_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dsm")
        assert "target" in tool.inputSchema["properties"]

    def test_dsm_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dsm")
        assert tool.inputSchema["required"] == ["target"]

    def test_dsm_type_enum(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dsm")
        assert set(tool.inputSchema["properties"]["type"]["enum"]) == {"file", "module", "class", "function"}

    def test_dsm_format_enum(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dsm")
        assert set(tool.inputSchema["properties"]["format"]["enum"]) == {"text", "json"}


class TestCtxCyclesTool:
    """Tests for ctx-cycles tool schema."""

    def test_cycles_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-cycles" in {t.name for t in tools}

    def test_cycles_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-cycles")
        assert "target" in tool.inputSchema["properties"]

    def test_cycles_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-cycles")
        assert tool.inputSchema["required"] == ["target"]

    def test_cycles_type_enum(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-cycles")
        assert set(tool.inputSchema["properties"]["type"]["enum"]) == {"file", "module", "class", "function"}


class TestCtxLayersTool:
    """Tests for ctx-layers tool schema."""

    def test_layers_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-layers" in {t.name for t in tools}

    def test_layers_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-layers")
        assert "target" in tool.inputSchema["properties"]

    def test_layers_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-layers")
        assert tool.inputSchema["required"] == ["target"]


class TestCtxArchitectureTool:
    """Tests for ctx-architecture tool schema."""

    def test_architecture_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-architecture" in {t.name for t in tools}

    def test_architecture_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-architecture")
        props = tool.inputSchema["properties"]
        assert "target" in props
        assert "rules_file" in props

    def test_architecture_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-architecture")
        assert tool.inputSchema["required"] == ["target"]

    def test_architecture_rules_yaml_property(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-architecture")
        assert "rules_yaml" in tool.inputSchema["properties"]


class TestCtxMetricsTool:
    """Tests for ctx-metrics tool schema."""

    def test_metrics_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-metrics" in {t.name for t in tools}

    def test_metrics_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-metrics")
        assert "target" in tool.inputSchema["properties"]

    def test_metrics_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-metrics")
        assert tool.inputSchema["required"] == ["target"]

    def test_metrics_rules_properties(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-metrics")
        props = tool.inputSchema["properties"]
        assert "rules_file" in props
        assert "rules_yaml" in props


class TestCtxLlmstxtTool:
    """Tests for ctx-llmstxt tool schema."""

    def test_llmstxt_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-llmstxt" in {t.name for t in tools}

    def test_llmstxt_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-llmstxt")
        assert "repository" in tool.inputSchema["properties"]

    def test_llmstxt_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-llmstxt")
        assert tool.inputSchema["required"] == ["repository"]

    def test_llmstxt_optional_properties(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-llmstxt")
        props = tool.inputSchema["properties"]
        assert "include_api" in props
        assert "include_quickstart" in props


class TestCtxDumpTool:
    """Tests for ctx-dump tool schema."""

    def test_dump_tool_exists(self):
        tools = get_ctx_tools()
        assert "ctx-dump" in {t.name for t in tools}

    def test_dump_tool_schema(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dump")
        assert "path" in tool.inputSchema["properties"]
        assert "level" in tool.inputSchema["properties"]

    def test_dump_required_fields(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dump")
        assert tool.inputSchema["required"] == ["path"]

    def test_dump_level_enum(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dump")
        assert set(tool.inputSchema["properties"]["level"]["enum"]) == {"compact", "medium", "full"}

    def test_dump_optional_properties(self):
        tools = get_ctx_tools()
        tool = next(t for t in tools if t.name == "ctx-dump")
        props = tool.inputSchema["properties"]
        assert "output_path" in props
        assert "force" in props
        assert "include_private" in props
        assert "use_llm" in props
        assert "llm_model" in props
