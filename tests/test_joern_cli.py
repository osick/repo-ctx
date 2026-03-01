"""
Unit tests for Joern CLI wrapper.

These tests use mocking to test the CLI wrapper without requiring
Joern to be installed.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from repo_ctx.joern.cli import (
    JoernCLI,
    JoernError,
    JoernNotFoundError,
    JoernParseError,
    JoernQueryError,
    JoernExportError,
    JoernResult,
    ParseResult,
    QueryResult,
    ExportResult,
)


class TestJoernCLI:
    """Test JoernCLI class."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        cli = JoernCLI()
        assert cli._joern_path is None
        assert cli._timeout == 300

    def test_init_custom_path(self):
        """Test initialization with custom path."""
        cli = JoernCLI(joern_path="/custom/path", timeout=600)
        assert cli._joern_path == "/custom/path"
        assert cli._timeout == 600

    @patch("shutil.which")
    def test_is_available_when_in_path(self, mock_which):
        """Test is_available returns True when joern-parse is in PATH."""
        mock_which.return_value = "/usr/bin/joern-parse"
        cli = JoernCLI()
        assert cli.is_available() is True

    @patch("shutil.which")
    def test_is_available_when_not_installed(self, mock_which):
        """Test is_available returns False when Joern is not found."""
        mock_which.return_value = None
        cli = JoernCLI()
        # Also mock the directory checks
        with patch("os.path.isdir", return_value=False):
            assert cli.is_available() is False

    @patch("shutil.which")
    @patch("os.path.isdir")
    @patch("os.path.isfile")
    @patch("os.access")
    def test_find_joern_path_custom(self, mock_access, mock_isfile, mock_isdir, mock_which):
        """Test finding Joern with custom path."""
        mock_which.return_value = None
        mock_isdir.return_value = True
        mock_isfile.return_value = True
        mock_access.return_value = True

        cli = JoernCLI(joern_path="/custom/joern")
        path = cli._find_joern_path()
        assert path == "/custom/joern"

    @patch("shutil.which")
    def test_get_command_path_in_path(self, mock_which):
        """Test getting command path when in PATH."""
        mock_which.return_value = "/usr/bin/joern-parse"
        cli = JoernCLI()
        path = cli._get_command_path("joern-parse")
        assert path == "/usr/bin/joern-parse"

    @patch("shutil.which")
    @patch("os.path.isdir")
    def test_get_command_path_not_found(self, mock_isdir, mock_which):
        """Test get_command_path raises error when not found."""
        mock_which.return_value = None
        mock_isdir.return_value = False

        cli = JoernCLI()
        with pytest.raises(JoernNotFoundError):
            cli._get_command_path("joern-parse")


class TestJoernCLIRunCommand:
    """Test JoernCLI._run_command method."""

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_command_success(self, mock_which, mock_run):
        """Test successful command execution."""
        mock_which.return_value = "/usr/bin/joern"
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="output",
            stderr="",
        )

        cli = JoernCLI()
        result = cli._run_command(["joern", "--version"])

        assert result.success is True
        assert result.stdout == "output"
        assert result.return_code == 0

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_run_command_failure(self, mock_which, mock_run):
        """Test command execution failure."""
        mock_which.return_value = "/usr/bin/joern"
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="error message",
        )

        cli = JoernCLI()
        result = cli._run_command(["joern", "--invalid"])

        assert result.success is False
        assert result.stderr == "error message"
        assert result.return_code == 1


class TestJoernCLIParse:
    """Test JoernCLI.parse method."""

    def test_parse_nonexistent_path(self):
        """Test parse raises error for non-existent path."""
        cli = JoernCLI()
        with pytest.raises(JoernParseError, match="does not exist"):
            cli.parse("/nonexistent/path")

    @patch.object(JoernCLI, "_run_command")
    @patch.object(JoernCLI, "_get_command_path")
    def test_parse_success(self, mock_get_cmd, mock_run_cmd):
        """Test successful parse."""
        mock_get_cmd.return_value = "/usr/bin/joern-parse"
        mock_run_cmd.return_value = JoernResult(
            success=True,
            stdout="Parsing complete",
            stderr="",
            return_code=0,
            command=["joern-parse"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy source file
            src_file = os.path.join(tmpdir, "test.py")
            with open(src_file, "w") as f:
                f.write("def test(): pass")

            cpg_file = os.path.join(tmpdir, "test.cpg")

            # Mock CPG file creation
            with patch("os.path.exists") as mock_exists:
                mock_exists.side_effect = lambda p: p == src_file or p == cpg_file

                cli = JoernCLI()
                result = cli.parse(src_file, cpg_file)

                assert result.success is True
                assert result.cpg_path == cpg_file

    @patch.object(JoernCLI, "_run_command")
    @patch.object(JoernCLI, "_get_command_path")
    def test_parse_with_language(self, mock_get_cmd, mock_run_cmd):
        """Test parse with explicit language."""
        mock_get_cmd.return_value = "/usr/bin/joern-parse"
        mock_run_cmd.return_value = JoernResult(
            success=True,
            stdout="",
            stderr="",
            return_code=0,
            command=["joern-parse"],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            src_file = os.path.join(tmpdir, "test.c")
            with open(src_file, "w") as f:
                f.write("int main() { return 0; }")

            cpg_file = os.path.join(tmpdir, "test.cpg")

            with patch("os.path.exists") as mock_exists:
                mock_exists.side_effect = lambda p: p == src_file or p == cpg_file

                cli = JoernCLI()
                cli.parse(src_file, cpg_file, language="c")

                # Verify language was passed
                call_args = mock_run_cmd.call_args[0][0]
                assert "--language" in call_args
                assert "C" in call_args


class TestJoernCLIRunQuery:
    """Test JoernCLI.run_query method."""

    def test_run_query_nonexistent_cpg(self):
        """Test run_query raises error for non-existent CPG."""
        cli = JoernCLI()
        with pytest.raises(JoernQueryError, match="does not exist"):
            cli.run_query("/nonexistent/cpg.bin", "cpg.method.name.l")


class TestJoernCLIExport:
    """Test JoernCLI.export method."""

    def test_export_nonexistent_cpg(self):
        """Test export raises error for non-existent CPG."""
        cli = JoernCLI()
        with pytest.raises(JoernExportError, match="does not exist"):
            cli.export("/nonexistent/cpg.bin", "/output")


class TestDataClasses:
    """Test dataclass structures."""

    def test_joern_result(self):
        """Test JoernResult dataclass."""
        result = JoernResult(
            success=True,
            stdout="output",
            stderr="",
            return_code=0,
            command=["joern", "--version"],
            duration_ms=100,
        )
        assert result.success is True
        assert result.duration_ms == 100

    def test_parse_result(self):
        """Test ParseResult dataclass."""
        result = ParseResult(
            cpg_path="/tmp/test.cpg",
            success=True,
            files_processed=5,
        )
        assert result.cpg_path == "/tmp/test.cpg"
        assert result.files_processed == 5

    def test_query_result(self):
        """Test QueryResult dataclass."""
        result = QueryResult(
            output="method1\nmethod2",
            success=True,
            query="cpg.method.name.l",
            execution_time_ms=500,
        )
        assert result.success is True
        assert result.execution_time_ms == 500

    def test_export_result(self):
        """Test ExportResult dataclass."""
        result = ExportResult(
            output_dir="/tmp/export",
            format="dot",
            representation="cfg",
            files_created=["file1.dot", "file2.dot"],
            success=True,
        )
        assert len(result.files_created) == 2
        assert result.format == "dot"
