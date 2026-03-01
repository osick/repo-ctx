"""Tests for CodebaseSummarizer module."""
import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import tempfile

from repo_ctx.analysis.codebase_summarizer import CodebaseSummarizer


class TestCodebaseSummarizer:
    """Tests for CodebaseSummarizer class."""

    def test_init_without_llm(self):
        """Initializes without LLM service."""
        summarizer = CodebaseSummarizer()
        assert summarizer.llm_service is None

    def test_init_with_llm(self):
        """Initializes with LLM service."""
        mock_llm = MagicMock()
        summarizer = CodebaseSummarizer(llm_service=mock_llm)
        assert summarizer.llm_service == mock_llm

    @pytest.mark.asyncio
    async def test_generate_summary_no_llm(self):
        """Returns None without LLM service."""
        summarizer = CodebaseSummarizer()
        result = await summarizer.generate_summary(Path("/tmp"))
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_no_symbol_data(self):
        """Returns None when neither by-file dir nor index.json exist."""
        mock_llm = MagicMock()
        summarizer = CodebaseSummarizer(llm_service=mock_llm)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create symbols directory but no by-file or index.json
            (Path(tmpdir) / "symbols").mkdir()
            result = await summarizer.generate_summary(Path(tmpdir))
            assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_from_index_json_fallback(self):
        """Uses index.json when by-file directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create symbols directory with index.json only
            repo_ctx = Path(tmpdir)
            symbols_dir = repo_ctx / "symbols"
            symbols_dir.mkdir(parents=True)

            # Create index.json
            index_data = {
                "total": 2,
                "symbols": [
                    {
                        "name": "MyClass",
                        "type": "class",
                        "file": "mymodule/service.py",
                        "line": 10
                    },
                    {
                        "name": "process_data",
                        "type": "function",
                        "file": "mymodule/service.py",
                        "line": 20
                    }
                ]
            }
            (symbols_dir / "index.json").write_text(json.dumps(index_data))

            # Mock LLM response
            mock_response = MagicMock()
            mock_response.content = "## Architecture\n\nFallback summary."

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            result = await summarizer.generate_summary(repo_ctx, project_name="FallbackTest")

            # Verify LLM was called
            assert mock_llm._complete.called

            # Verify result
            assert result is not None
            assert "FallbackTest" in result
            assert "Architecture" in result

    @pytest.mark.asyncio
    async def test_generate_summary_with_data(self):
        """Generates summary from by-file data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create by-file directory with test data
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            # Create test file data
            test_data = {
                "file": "mymodule/service.py",
                "documentation": "Service layer for business logic.",
                "symbols": [
                    {
                        "name": "MyService",
                        "type": "class",
                        "documentation": "Main service class."
                    },
                    {
                        "name": "process_data",
                        "type": "function",
                        "documentation": "Processes input data."
                    }
                ]
            }
            (by_file / "mymodule_service.py.json").write_text(json.dumps(test_data))

            # Mock LLM response
            mock_response = MagicMock()
            mock_response.content = "## Architecture Overview\n\nThis is a test summary."

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            result = await summarizer.generate_summary(repo_ctx, project_name="TestProject")

            # Verify LLM was called
            assert mock_llm._complete.called

            # Verify result
            assert result is not None
            assert "TestProject" in result
            assert "Architecture Overview" in result

    @pytest.mark.asyncio
    async def test_generate_and_save(self):
        """Saves summary to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create by-file directory with test data
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "main.py",
                "documentation": "Main entry point.",
                "symbols": []
            }
            (by_file / "main.py.json").write_text(json.dumps(test_data))

            # Mock LLM
            mock_response = MagicMock()
            mock_response.content = "# Summary\n\nTest content."

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            output_path = await summarizer.generate_and_save(
                repo_ctx,
                project_name="Test",
                output_filename="SUMMARY.md"
            )

            assert output_path is not None
            assert output_path.exists()
            assert output_path.name == "SUMMARY.md"

            content = output_path.read_text()
            assert "Test" in content


class TestBusinessSummary:
    """Tests for business summary generation."""

    @pytest.mark.asyncio
    async def test_generate_business_summary(self):
        """Should generate business-focused summary by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir) / ".repo-ctx"
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            # Create a README.md in the repo root
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("# Test Project\n\nA tool for testing things.")

            test_data = {
                "file": "src/service.py",
                "documentation": "Handles business logic.",
                "symbols": [{"name": "ServiceClass", "type": "class"}]
            }
            (by_file / "src_service.py.json").write_text(json.dumps(test_data))

            mock_response = MagicMock()
            mock_response.content = "## Executive Summary\n\nThis is a test tool."
            mock_response.prompt_tokens = 100
            mock_response.completion_tokens = 50

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)
            mock_llm.model = "test-model"

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            result = await summarizer.generate_summary(repo_ctx, project_name="TestProject")

            assert result is not None
            assert "Business overview" in result
            assert "Executive Summary" in result

    @pytest.mark.asyncio
    async def test_generate_technical_summary(self):
        """Should generate technical summary when type is 'technical'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/core.py",
                "documentation": "Core implementation.",
                "symbols": [{"name": "CoreClass", "type": "class"}]
            }
            (by_file / "src_core.py.json").write_text(json.dumps(test_data))

            mock_response = MagicMock()
            mock_response.content = "## Architecture Overview\n\nLayered architecture."
            mock_response.prompt_tokens = 100
            mock_response.completion_tokens = 50

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)
            mock_llm.model = "test-model"

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            result = await summarizer.generate_summary(
                repo_ctx,
                project_name="TestProject",
                summary_type="technical"
            )

            assert result is not None
            assert "Technical summary" in result

    def test_read_readme(self):
        """Should read README from repo root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir) / ".repo-ctx"
            repo_ctx.mkdir()

            # Create README in parent (repo root)
            readme = Path(tmpdir) / "README.md"
            readme.write_text("# My Project\n\nDescription here.")

            summarizer = CodebaseSummarizer()
            content = summarizer._read_readme(repo_ctx)

            assert "My Project" in content
            assert "Description" in content

    def test_format_modules_for_business_skips_tests(self):
        """Should skip test modules in business summary."""
        summarizer = CodebaseSummarizer()

        modules_data = {
            "src": [{"file": "src/main.py", "documentation": "Main entry point."}],
            "tests": [{"file": "tests/test_main.py", "documentation": "Tests."}],
            "examples": [{"file": "examples/demo.py", "documentation": "Demo."}],
        }

        result = summarizer._format_modules_for_business(modules_data)

        assert "src" in result
        assert "tests" not in result
        assert "examples" not in result


class TestCodebaseSummarizerEmptyLLMResponse:
    """Tests for handling empty LLM responses."""

    @pytest.mark.asyncio
    async def test_generate_summary_returns_none_on_empty_llm_response(self):
        """Should return None when LLM returns empty content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "mymodule/service.py",
                "documentation": "Service layer.",
                "symbols": [{"name": "MyClass", "type": "class"}]
            }
            (by_file / "mymodule_service.py.json").write_text(json.dumps(test_data))

            # Mock LLM that returns empty content (simulates API failure)
            mock_response = MagicMock()
            mock_response.content = ""  # Empty content
            mock_response.metadata = None

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="TestProject")

            # Should return None when LLM fails (after all retries)
            assert result is None

    @pytest.mark.asyncio
    async def test_generate_summary_logs_error_from_llm_metadata(self):
        """Should log error message from LLM response metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "mymodule/service.py",
                "documentation": "Service layer.",
                "symbols": [{"name": "MyClass", "type": "class"}]
            }
            (by_file / "mymodule_service.py.json").write_text(json.dumps(test_data))

            # Mock LLM that returns empty content with error in metadata
            mock_response = MagicMock()
            mock_response.content = ""
            mock_response.metadata = {"error": "Invalid model: gpt-5-mini"}

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            # Capture log output
            with patch("repo_ctx.analysis.codebase_summarizer.logger") as mock_logger:
                result = await summarizer.generate_summary(repo_ctx, project_name="TestProject")

                # Should return None
                assert result is None
                # Should log warning with error message (3 times due to retries)
                assert mock_logger.warning.call_count == 3
                # All calls should include the error message
                for call in mock_logger.warning.call_args_list:
                    assert "gpt-5-mini" in call[0][0]

    @pytest.mark.asyncio
    async def test_generate_and_save_returns_none_on_empty_llm_response(self):
        """Should return None (not create file) when LLM returns empty content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "main.py",
                "documentation": "Main entry point.",
                "symbols": []
            }
            (by_file / "main.py.json").write_text(json.dumps(test_data))

            # Mock LLM that returns empty content
            mock_response = MagicMock()
            mock_response.content = ""
            mock_response.metadata = None

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            output_path = await summarizer.generate_and_save(
                repo_ctx,
                project_name="Test",
                output_filename="CODEBASE_SUMMARY.md"
            )

            # Should return None (after all retries)
            assert output_path is None
            # File should NOT exist
            assert not (repo_ctx / "CODEBASE_SUMMARY.md").exists()


class TestModuleDataCollection:
    """Tests for module data collection."""

    def test_collect_groups_by_module(self):
        """Groups files by module correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            # Create files in different modules
            for module, filename in [
                ("repo_ctx", "core.py"),
                ("repo_ctx", "config.py"),
                ("repo_ctx/services", "llm.py"),
                ("tests", "test_core.py"),
            ]:
                data = {
                    "file": f"{module}/{filename}" if module != "(root)" else filename,
                    "documentation": f"Doc for {filename}",
                    "symbols": []
                }
                safe_name = f"{module}_{filename}".replace("/", "_")
                (by_file / f"{safe_name}.json").write_text(json.dumps(data))

            summarizer = CodebaseSummarizer()
            modules = summarizer._collect_module_data(by_file)

            # Should have grouped by first directory
            assert len(modules) >= 2  # At least repo_ctx and tests

    def test_format_modules_info(self):
        """Formats module info for prompt."""
        summarizer = CodebaseSummarizer()

        modules_data = {
            "mymodule": [
                {
                    "file": "mymodule/service.py",
                    "documentation": "Service implementation.",
                    "classes": [{"name": "MyService", "documentation": "Main service."}],
                    "functions": [{"name": "process", "documentation": "Process data."}]
                }
            ]
        }

        result = summarizer._format_modules_info(modules_data)

        assert "### Module: mymodule" in result
        assert "mymodule/service.py" in result
        assert "MyService" in result
        assert "process" in result


class TestSummaryRetryLogic:
    """Tests for retry logic on empty LLM responses in codebase summary."""

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self):
        """Retries and succeeds on second attempt after empty response."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            if call_count == 1:
                response.content = ""  # Empty on first attempt
                response.metadata = None
            else:
                response.content = "## Summary\n\nThis is a test summary."
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete
        mock_llm.model = "test-model"

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/main.py",
                "documentation": "Main entry.",
                "symbols": []
            }
            (by_file / "src_main.py.json").write_text(json.dumps(test_data))

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="Test")

            assert call_count == 2
            assert result is not None
            assert "Summary" in result

    @pytest.mark.asyncio
    async def test_retry_succeeds_on_third_attempt(self):
        """Retries and succeeds on third attempt after two empty responses."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            if call_count < 3:
                response.content = ""  # Empty on first two attempts
                response.metadata = None
            else:
                response.content = "## Architecture\n\nThird time success."
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete
        mock_llm.model = "test-model"

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/main.py",
                "documentation": "Main entry.",
                "symbols": []
            }
            (by_file / "src_main.py.json").write_text(json.dumps(test_data))

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="Test")

            assert call_count == 3
            assert result is not None
            assert "Architecture" in result

    @pytest.mark.asyncio
    async def test_all_retries_fail(self):
        """Returns None when all retries fail with empty responses."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            response = MagicMock()
            response.content = ""  # Always empty
            response.metadata = {"error": "Rate limited"}
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete
        mock_llm.model = "test-model"

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/main.py",
                "documentation": "Main entry.",
                "symbols": []
            }
            (by_file / "src_main.py.json").write_text(json.dumps(test_data))

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="Test")

            assert call_count == 3  # MAX_RETRIES
            assert result is None

    @pytest.mark.asyncio
    async def test_retry_after_exception(self):
        """Retries and succeeds after exception on first attempt."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network error")
            response = MagicMock()
            response.content = "## Recovered\n\nSuccess after retry."
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete
        mock_llm.model = "test-model"

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/main.py",
                "documentation": "Main entry.",
                "symbols": []
            }
            (by_file / "src_main.py.json").write_text(json.dumps(test_data))

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="Test")

            assert call_count == 2
            assert result is not None
            assert "Recovered" in result

    @pytest.mark.asyncio
    async def test_all_retries_fail_with_exceptions(self):
        """Returns None when all retries fail with exceptions."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            raise TimeoutError("API timeout")

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete
        mock_llm.model = "test-model"

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_ctx = Path(tmpdir)
            by_file = repo_ctx / "symbols" / "by-file"
            by_file.mkdir(parents=True)

            test_data = {
                "file": "src/main.py",
                "documentation": "Main entry.",
                "symbols": []
            }
            (by_file / "src_main.py.json").write_text(json.dumps(test_data))

            summarizer = CodebaseSummarizer(llm_service=mock_llm)
            summarizer.RETRY_DELAY = 0.01  # Speed up test

            result = await summarizer.generate_summary(repo_ctx, project_name="Test")

            assert call_count == 3  # MAX_RETRIES
            assert result is None
