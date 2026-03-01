"""
Unit tests for Joern adapter.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from repo_ctx.joern.adapter import JoernAdapter, AnalysisResult, QueryResult
from repo_ctx.joern.cli import JoernCLI, JoernNotFoundError
from repo_ctx.joern.parser import CPGParseResult, CPGMethod, CPGType


class TestJoernAdapter:
    """Test JoernAdapter class."""

    def test_init_default(self):
        """Test initialization with defaults."""
        adapter = JoernAdapter()
        assert adapter._cache_dir == os.path.expanduser("~/.cache/repo-ctx/cpg")
        assert adapter._timeout == 300

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = JoernAdapter(
                joern_path="/custom/joern",
                cache_dir=tmpdir,
                timeout=600,
            )
            assert adapter._cache_dir == tmpdir
            assert adapter._timeout == 600

    @patch.object(JoernCLI, "is_available")
    def test_is_available_true(self, mock_available):
        """Test is_available returns True when Joern is installed."""
        mock_available.return_value = True
        adapter = JoernAdapter()
        assert adapter.is_available() is True

    @patch.object(JoernCLI, "is_available")
    def test_is_available_false(self, mock_available):
        """Test is_available returns False when Joern is not installed."""
        mock_available.return_value = False
        adapter = JoernAdapter()
        assert adapter.is_available() is False

    @patch.object(JoernCLI, "get_version")
    def test_get_version(self, mock_version):
        """Test getting Joern version."""
        mock_version.return_value = "1.2.3"
        adapter = JoernAdapter()
        assert adapter.get_version() == "1.2.3"

    def test_get_supported_languages(self):
        """Test getting supported languages."""
        adapter = JoernAdapter()
        languages = adapter.get_supported_languages()

        assert "python" in languages
        assert "java" in languages
        assert "c" in languages
        assert "cpp" in languages
        assert "go" in languages


class TestAnalyzeDirectory:
    """Test JoernAdapter.analyze_directory method."""

    @patch.object(JoernCLI, "is_available")
    def test_analyze_directory_nonexistent_path(self, mock_available):
        """Test analyzing non-existent path."""
        mock_available.return_value = True
        adapter = JoernAdapter()

        result = adapter.analyze_directory("/nonexistent/path")

        assert len(result.errors) > 0
        assert "does not exist" in result.errors[0]

    @patch.object(JoernCLI, "is_available")
    def test_analyze_directory_joern_not_available(self, mock_available):
        """Test analyzing when Joern is not available."""
        mock_available.return_value = False

        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = JoernAdapter()
            result = adapter.analyze_directory(tmpdir)

            assert len(result.errors) > 0
            assert "not installed" in result.errors[0]


class TestAnalyzeDirectoryWithComments:
    """Test that comments are correctly analyzed."""

    @patch("repo_ctx.joern.adapter.JoernCLI")
    @patch("repo_ctx.joern.adapter.os.path.exists")
    def test_analyze_directory_with_comments(self, mock_exists, MockJoernCLI):
        """Test that docstrings are correctly mapped to symbols."""
        mock_exists.return_value = True

        # Mock the CLI class
        mock_cli_instance = MockJoernCLI.return_value
        mock_cli_instance.is_available.return_value = True

        # Define mock outputs for different queries
        extract_all_output = 'METHOD|my_func|test.py.my_func|test.py|2|5|my_func()|'
        comments_output = 'test.py|1|"""This is a docstring."""'

        # Side effect function to return different output based on query
        def run_query_side_effect(cpg_path, query, timeout):
            if "METHOD" in query:  # A bit brittle, but works for QUERY_EXTRACT_ALL
                return MagicMock(output=extract_all_output, success=True)
            elif "comment" in query:  # For QUERY_COMMENTS
                return MagicMock(output=comments_output, success=True)
            return MagicMock(output="", success=True)

        mock_cli_instance.run_query.side_effect = run_query_side_effect

        with patch.object(JoernAdapter, "_get_or_create_cpg", return_value="/dummy/cpg.bin"):
            adapter = JoernAdapter()
            result = adapter.analyze_directory("/dummy/path")

            assert not result.errors
            assert len(result.symbols) == 1
            symbol = result.symbols[0]
            assert symbol.name == "my_func"
            assert symbol.documentation is not None
            assert "This is a docstring" in symbol.documentation


    @patch("repo_ctx.joern.adapter.os.path.exists")
    def test_analyze_directory_with_data_flow(self, mock_exists):
        """Test that data flow is correctly analyzed."""
        mock_exists.return_value = True

        # Mock the CLI class
        mock_cli_instance = MagicMock()
        with patch("repo_ctx.joern.adapter.JoernCLI", return_value=mock_cli_instance):
            mock_cli_instance.is_available.return_value = True

            # Define mock outputs for different queries
            extract_all_output = (
                "METHOD|source_func|test.py.source_func|test.py|1|2|source_func(arg)|arg:any\n"
                "METHOD|sink_func|test.py.sink_func|test.py|4|5|sink_func(data)|data:any"
            )
            comments_output = ""
            data_flow_output = "test.py|1|arg|test.py|5|data"

            # Side effect function to return different output based on query
            def run_query_side_effect(cpg_path, query, timeout):
                if "METHOD" in query:
                    return MagicMock(output=extract_all_output, success=True)
                elif "comment" in query:
                    return MagicMock(output=comments_output, success=True)
                elif "reachableBy" in query:
                    return MagicMock(output=data_flow_output, success=True)
                return MagicMock(output="", success=True)

            mock_cli_instance.run_query.side_effect = run_query_side_effect

            with patch.object(
                JoernAdapter, "_get_or_create_cpg", return_value="/dummy/cpg.bin"
            ):
                adapter = JoernAdapter()
                result = adapter.analyze_directory("/dummy/path")

                assert not result.errors
                assert len(result.dependencies) > 0
                data_flow_deps = [
                    d for d in result.dependencies if d.dependency_type == "data_flow"
                ]
                assert len(data_flow_deps) == 1
                dep = data_flow_deps[0]
                assert dep.source == "test.py:arg"
                assert dep.target == "test.py:data"
                assert dep.file_path == "test.py"
                assert dep.line == 1


class TestAnalyzeFile:
    """Test JoernAdapter.analyze_file method."""

    @patch.object(JoernAdapter, "analyze_directory")
    def test_analyze_file_with_code(self, mock_analyze):
        """Test analyzing file with provided code."""
        mock_result = AnalysisResult(
            symbols=[],
            files_analyzed=1,
        )
        mock_analyze.return_value = mock_result

        adapter = JoernAdapter()
        symbols = adapter.analyze_file(
            file_path="test.py",
            code="def hello(): pass",
        )

        # Should have called analyze_directory
        mock_analyze.assert_called_once()


class TestRunQuery:
    """Test JoernAdapter.run_query method."""

    @patch.object(JoernAdapter, "_get_or_create_cpg")
    @patch.object(JoernCLI, "run_query")
    def test_run_query_success(self, mock_run_query, mock_get_cpg):
        """Test successful query execution."""
        mock_get_cpg.return_value = "/tmp/test.cpg"
        mock_run_query.return_value = MagicMock(
            output="method1\nmethod2",
            success=True,
            execution_time_ms=100,
        )

        adapter = JoernAdapter()
        result = adapter.run_query("/path/to/code", "cpg.method.name.l")

        assert result.success is True
        assert "method1" in result.output


class TestExportGraph:
    """Test JoernAdapter.export_graph method."""

    @patch.object(JoernAdapter, "_get_or_create_cpg")
    @patch.object(JoernCLI, "export")
    def test_export_graph_success(self, mock_export, mock_get_cpg):
        """Test successful graph export."""
        mock_get_cpg.return_value = "/tmp/test.cpg"
        mock_export.return_value = MagicMock(
            output_dir="/tmp/export",
            format="dot",
            representation="cfg",
            files_created=["file1.dot"],
            success=True,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = JoernAdapter()
            result = adapter.export_graph(
                "/path/to/code",
                tmpdir,
                representation="cfg",
                format="dot",
            )

            assert result["success"] is True
            assert result["format"] == "dot"


class TestCPGCaching:
    """Test CPG caching functionality."""

    def test_cache_directory_created(self):
        """Test that cache directory is created on init."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = os.path.join(tmpdir, "cpg_cache")
            adapter = JoernAdapter(cache_dir=cache_dir)
            assert os.path.exists(cache_dir)

    @patch.object(JoernCLI, "parse")
    @patch.object(JoernCLI, "is_available")
    def test_cache_key_generation(self, mock_available, mock_parse):
        """Test that cache keys are generated consistently."""
        mock_available.return_value = True

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy source file
            src_dir = os.path.join(tmpdir, "src")
            os.makedirs(src_dir)
            src_file = os.path.join(src_dir, "test.py")
            with open(src_file, "w") as f:
                f.write("def test(): pass")

            # Calculate expected cache key
            import hashlib
            abs_path = os.path.abspath(src_dir)
            expected_key = hashlib.md5(abs_path.encode()).hexdigest()
            expected_cpg_path = os.path.join(tmpdir, f"{expected_key}.bin")

            # Set mock to return expected path
            mock_parse.return_value = MagicMock(cpg_path=expected_cpg_path)

            adapter = JoernAdapter(cache_dir=tmpdir)

            # Get CPG path for source
            with patch("os.path.exists", return_value=False):
                path1 = adapter._get_or_create_cpg(src_dir, None, True, False)

            # Verify parse was called with expected output path
            mock_parse.assert_called_once()
            call_kwargs = mock_parse.call_args[1]
            assert expected_key in call_kwargs["output_path"]
            assert path1 == expected_cpg_path

    def test_clear_cache_all(self):
        """Test clearing all cached CPGs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adapter = JoernAdapter(cache_dir=tmpdir)

            # Create some dummy cache files
            for i in range(3):
                path = os.path.join(tmpdir, f"cache{i}.bin")
                with open(path, "w") as f:
                    f.write("dummy")

            count = adapter.clear_cache()
            assert count == 3
            assert len(os.listdir(tmpdir)) == 0


class TestAnalysisResult:
    """Test AnalysisResult dataclass."""

    def test_defaults(self):
        """Test default values."""
        result = AnalysisResult()
        assert result.symbols == []
        assert result.dependencies == []
        assert result.files_analyzed == 0
        assert result.languages_detected == []
        assert result.cpg_path is None
        assert result.errors == []

    def test_with_values(self):
        """Test with provided values."""
        result = AnalysisResult(
            files_analyzed=5,
            languages_detected=["python", "java"],
            cpg_path="/tmp/test.cpg",
        )
        assert result.files_analyzed == 5
        assert len(result.languages_detected) == 2


class TestQueryResult:
    """Test QueryResult dataclass."""

    def test_defaults(self):
        """Test default values."""
        result = QueryResult(
            output="output",
            success=True,
            query="cpg.method.name.l",
        )
        assert result.execution_time_ms == 0
        assert result.parsed_result is None

    def test_with_parsed(self):
        """Test with parsed result."""
        result = QueryResult(
            output="item1\nitem2",
            success=True,
            query="cpg.method.name.l",
            parsed_result=["item1", "item2"],
        )
        assert len(result.parsed_result) == 2
