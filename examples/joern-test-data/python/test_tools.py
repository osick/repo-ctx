"""
Tests for DocGen tools module.
"""

import pytest
from unittest.mock import patch, MagicMock
from docgen.tools import RepoCtxTools, ToolResult, tools


class TestToolResult:
    """Tests for ToolResult dataclass."""

    def test_success_result(self):
        """Test successful tool result."""
        result = ToolResult(success=True, data={"key": "value"})

        assert result.success
        assert result.data == {"key": "value"}
        assert result.error is None

    def test_error_result(self):
        """Test error tool result."""
        result = ToolResult(success=False, data=None, error="Command failed")

        assert not result.success
        assert result.data is None
        assert result.error == "Command failed"


class TestRepoCtxTools:
    """Tests for RepoCtxTools wrapper."""

    def test_init_default_path(self):
        """Test default repo-ctx path."""
        tools = RepoCtxTools()
        assert tools.repo_ctx_path == "repo-ctx"

    def test_init_custom_path(self):
        """Test custom repo-ctx path."""
        tools = RepoCtxTools("/custom/path/repo-ctx")
        assert tools.repo_ctx_path == "/custom/path/repo-ctx"

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"symbols": []}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools._run_command(["analyze", "./src"])

        assert result.success
        assert result.data == {"symbols": []}
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run):
        """Test failed command execution."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Error: path not found",
        )

        tools = RepoCtxTools()
        result = tools._run_command(["analyze", "./nonexistent"])

        assert not result.success
        assert "Error" in result.error

    @patch("subprocess.run")
    def test_run_command_timeout(self, mock_run):
        """Test command timeout."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=30)

        tools = RepoCtxTools()
        result = tools._run_command(["query", "./src", "cpg.method.l"], timeout=30)

        assert not result.success
        assert "timed out" in result.error

    @patch("subprocess.run")
    def test_run_command_not_found(self, mock_run):
        """Test repo-ctx not found."""
        mock_run.side_effect = FileNotFoundError()

        tools = RepoCtxTools("/nonexistent/repo-ctx")
        result = tools._run_command(["status"])

        assert not result.success
        assert "not found" in result.error

    @patch("subprocess.run")
    def test_analyze(self, mock_run):
        """Test analyze command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"symbols": [{"name": "Test"}]}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools.analyze("./src", language="python")

        assert result.success
        args = mock_run.call_args[0][0]
        assert "analyze" in args
        assert "--lang" in args
        assert "python" in args

    @patch("subprocess.run")
    def test_docs(self, mock_run):
        """Test docs command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"content": "# README"}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools.docs("/owner/repo", max_tokens=5000)

        assert result.success
        args = mock_run.call_args[0][0]
        assert "docs" in args
        assert "--max-tokens" in args

    @patch("subprocess.run")
    def test_graph(self, mock_run):
        """Test graph command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"nodes": [], "edges": []}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools.graph("./src", graph_type="function")

        assert result.success
        args = mock_run.call_args[0][0]
        assert "graph" in args
        assert "--type" in args
        assert "function" in args

    @patch("subprocess.run")
    def test_query(self, mock_run):
        """Test query command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"result": ["method1", "method2"]}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools.query("./src", "cpg.method.name.l")

        assert result.success
        args = mock_run.call_args[0][0]
        assert "query" in args
        assert "cpg.method.name.l" in args

    @patch("subprocess.run")
    def test_status(self, mock_run):
        """Test status command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"joern_available": true}',
            stderr="",
        )

        tools = RepoCtxTools()
        result = tools.status()

        assert result.success


class TestToolsSingleton:
    """Tests for the tools singleton instance."""

    def test_singleton_exists(self):
        """Test that singleton instance exists."""
        assert tools is not None
        assert isinstance(tools, RepoCtxTools)
