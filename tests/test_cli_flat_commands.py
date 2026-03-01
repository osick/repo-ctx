"""Tests for flat CLI commands."""

import json
import pytest
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from repo_ctx.cli import create_parser


class TestCLIParser:
    """Tests for CLI argument parsing."""

    @pytest.fixture
    def parser(self):
        """Create CLI parser."""
        return create_parser()

    def test_flat_commands_registered(self, parser):
        """All flat commands should be registered."""
        # Check that subparsers are registered by checking _subparsers
        flat_commands = ["index", "list", "search", "docs", "analyze", "graph", "query", "export", "status"]

        # Find the subparsers action
        subparsers_action = None
        for action in parser._actions:
            if hasattr(action, 'choices') and isinstance(action.choices, dict):
                subparsers_action = action
                break

        assert subparsers_action is not None, "Parser should have subparsers"

        for cmd in flat_commands:
            assert cmd in subparsers_action.choices, f"Command '{cmd}' should be registered"

    def test_index_command_args(self, parser):
        """Index command should parse correctly."""
        args = parser.parse_args(["index", "owner/repo"])
        assert args.command == "index"
        assert args.target == "owner/repo"
        assert args.group is False

    def test_index_with_group_flag(self, parser):
        """Index with --group should work."""
        args = parser.parse_args(["index", "--group", "myorg"])
        assert args.command == "index"
        assert args.target == "myorg"
        assert args.group is True

    def test_index_with_provider_shortcut(self, parser):
        """Index with --gitlab/--github should work."""
        args = parser.parse_args(["index", "group/project", "--gitlab"])
        assert args.command == "index"
        assert args.provider_shortcut == "gitlab"

    def test_list_command(self, parser):
        """List command should parse correctly."""
        args = parser.parse_args(["list"])
        assert args.command == "list"

    def test_search_command_basic(self, parser):
        """Search command should parse correctly."""
        args = parser.parse_args(["search", "fastapi"])
        assert args.command == "search"
        assert args.query == "fastapi"
        assert args.symbols is None
        assert args.exact is False

    def test_search_with_symbols(self, parser):
        """Search with --symbols should work."""
        args = parser.parse_args(["search", "User", "--symbols", "./src"])
        assert args.command == "search"
        assert args.query == "User"
        assert args.symbols == "./src"

    def test_search_with_exact(self, parser):
        """Search with --exact should work."""
        args = parser.parse_args(["search", "flask", "--exact"])
        assert args.command == "search"
        assert args.exact is True

    def test_search_with_limit(self, parser):
        """Search with --limit should work."""
        args = parser.parse_args(["search", "test", "-n", "5"])
        assert args.command == "search"
        assert args.limit == 5

    def test_docs_command(self, parser):
        """Docs command should parse correctly."""
        args = parser.parse_args(["docs", "/owner/repo"])
        assert args.command == "docs"
        assert args.repository == "/owner/repo"

    def test_docs_with_include(self, parser):
        """Docs with --include should work."""
        args = parser.parse_args(["docs", "/owner/repo", "--include", "code,symbols"])
        assert args.command == "docs"
        assert args.include == "code,symbols"

    def test_docs_with_format(self, parser):
        """Docs with --format should work."""
        args = parser.parse_args(["docs", "/owner/repo", "--format", "llmstxt"])
        assert args.command == "docs"
        assert args.format == "llmstxt"

    def test_analyze_command(self, parser):
        """Analyze command should parse correctly."""
        args = parser.parse_args(["analyze", "./src"])
        assert args.command == "analyze"
        assert args.target == "./src"

    def test_analyze_with_filters(self, parser):
        """Analyze with filters should work."""
        args = parser.parse_args(["analyze", "./src", "--lang", "python", "--type", "class"])
        assert args.command == "analyze"
        assert args.lang == "python"
        assert args.type == "class"

    def test_analyze_no_private(self, parser):
        """Analyze with --no-private should work."""
        args = parser.parse_args(["analyze", "./src", "--no-private"])
        assert args.command == "analyze"
        assert args.private is False

    def test_graph_command(self, parser):
        """Graph command should parse correctly."""
        args = parser.parse_args(["graph", "./src"])
        assert args.command == "graph"
        assert args.target == "./src"

    def test_graph_with_options(self, parser):
        """Graph with options should work."""
        args = parser.parse_args(["graph", "./src", "--type", "file", "--format", "dot"])
        assert args.command == "graph"
        assert args.type == "file"
        assert args.format == "dot"

    def test_query_command(self, parser):
        """Query command should parse correctly."""
        args = parser.parse_args(["query", "./src", "cpg.method.l"])
        assert args.command == "query"
        assert args.path == "./src"
        assert args.query == "cpg.method.l"

    def test_export_command(self, parser):
        """Export command should parse correctly."""
        args = parser.parse_args(["export", "./src", "./output"])
        assert args.command == "export"
        assert args.path == "./src"
        assert args.output_dir == "./output"

    def test_export_with_options(self, parser):
        """Export with options should work."""
        args = parser.parse_args(["export", "./src", "./out", "--repr", "cfg", "--format", "graphml"])
        assert args.command == "export"
        assert args.repr == "cfg"
        assert args.format == "graphml"

    def test_status_command(self, parser):
        """Status command should parse correctly."""
        args = parser.parse_args(["status"])
        assert args.command == "status"


class TestCLIHelp:
    """Tests for CLI help output."""

    def test_main_help_shows_flat_commands(self):
        """Main help should show new flat commands."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "index" in result.stdout
        assert "analyze" in result.stdout
        assert "search" in result.stdout
        assert "docs" in result.stdout

    def test_analyze_help(self):
        """Analyze --help should work."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "analyze", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "target" in result.stdout.lower()
        assert "--lang" in result.stdout or "-l" in result.stdout

    def test_search_help(self):
        """Search --help should work."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "search", "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "--symbols" in result.stdout or "-s" in result.stdout
        assert "--exact" in result.stdout or "-e" in result.stdout


class TestAnalyzeCommandExecution:
    """Tests for analyze command execution."""

    def test_analyze_local_file(self, tmp_path):
        """Analyze should work on local Python file."""
        # Create a test Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello():
    return "Hello"

class MyClass:
    pass
""")
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "analyze", str(test_file)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["statistics"]["total_symbols"] > 0
        assert "function" in output["statistics"]["by_type"] or "class" in output["statistics"]["by_type"]

    def test_analyze_local_directory(self, tmp_path):
        """Analyze should work on local directory."""
        # Create test files
        (tmp_path / "a.py").write_text("def func_a(): pass")
        (tmp_path / "b.py").write_text("class ClassB: pass")

        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "analyze", str(tmp_path)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["files_analyzed"] == 2

    def test_analyze_with_language_filter(self, tmp_path):
        """Analyze with --lang filter should work."""
        (tmp_path / "test.py").write_text("def func(): pass")
        (tmp_path / "test.js").write_text("function jsFunc() {}")

        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "analyze", str(tmp_path), "--lang", "python"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        # Should only have Python symbols (symbols might not all have language field)
        symbols = output.get("symbols", [])
        # No JavaScript symbols should be present (filter should exclude .js files)
        assert not any(s.get("language") == "javascript" for s in symbols)

    def test_analyze_nonexistent_path(self):
        """Analyze should error on nonexistent path."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "analyze", "/nonexistent/path/xyz"],
            capture_output=True,
            text=True
        )
        assert result.returncode != 0
        # Error message may be in stdout or stderr depending on implementation
        combined = result.stdout.lower() + result.stderr.lower()
        assert "not found" in combined or "error" in combined


class TestStatusCommand:
    """Tests for status command."""

    def test_status_runs(self):
        """Status command should run without errors."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "status"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        assert "tree-sitter" in result.stdout.lower() or "Tree-sitter" in result.stdout

    def test_status_json_output(self):
        """Status with JSON output should work."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "status"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert "treesitter" in output
        assert "joern" in output


class TestListCommand:
    """Tests for list command."""

    def test_list_empty(self):
        """List should work even with no indexed repos."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "list"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "REPO_CTX_STORAGE_PATH": ":memory:"}
        )
        # Should not crash, may show "no repositories"
        assert result.returncode == 0 or "no repositories" in result.stdout.lower()


class TestLegacyCommandsStillWork:
    """Tests that legacy nested commands still work."""

    def test_legacy_code_analyze(self, tmp_path):
        """Legacy 'code analyze' should still work."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def hello(): pass")

        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "code", "analyze", str(test_file)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["statistics"]["total_symbols"] > 0

    def test_legacy_repo_list(self):
        """Legacy 'repo list' should still work."""
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "repo", "list"],
            capture_output=True,
            text=True,
            env={**subprocess.os.environ, "REPO_CTX_STORAGE_PATH": ":memory:"}
        )
        # Should not crash
        assert result.returncode == 0 or "no repositories" in result.stdout.lower()


class TestSearchCommand:
    """Tests for search command."""

    def test_search_symbols_in_file(self, tmp_path):
        """Search --symbols should work on local file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class UserService:
    def get_user(self):
        pass

class AdminService:
    pass
""")
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "search", "User", "-s", str(test_file)],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        assert output["count"] > 0
        # Should find UserService
        names = [s["name"] for s in output["symbols"]]
        assert any("User" in name for name in names)

    def test_search_symbols_with_type_filter(self, tmp_path):
        """Search --symbols with --type should filter correctly."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def user_func(): pass
class UserClass: pass
""")
        result = subprocess.run(
            [sys.executable, "-m", "repo_ctx", "-o", "json", "search", "user", "-s", str(test_file), "--type", "class"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0
        output = json.loads(result.stdout)
        # Should only find class, not function
        for s in output["symbols"]:
            assert s["type"] == "class"
