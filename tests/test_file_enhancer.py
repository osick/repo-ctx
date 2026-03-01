"""Tests for FileEnhancer module."""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import tempfile

from repo_ctx.analysis.file_enhancer import FileEnhancer
from repo_ctx.analysis.prompts import (
    format_file_enhancement_prompt,
    parse_file_enhancement_response,
)


class TestFileEnhancer:
    """Tests for FileEnhancer class."""

    def test_init_without_llm(self):
        """FileEnhancer initializes without LLM service."""
        enhancer = FileEnhancer()
        assert enhancer.llm_service is None
        assert enhancer.source_root is None

    def test_init_with_llm_and_source_root(self):
        """FileEnhancer initializes with LLM service and source root."""
        mock_llm = MagicMock()
        source_root = Path("/tmp/test")
        enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
        assert enhancer.llm_service == mock_llm
        assert enhancer.source_root == source_root

    @pytest.mark.asyncio
    async def test_enhance_file_without_llm(self):
        """enhance_file returns original data without LLM."""
        enhancer = FileEnhancer()
        symbols = [
            {"name": "my_func", "type": "function", "documentation": "Does something"},
            {"name": "MyClass", "type": "class", "documentation": None},
        ]

        result = await enhancer.enhance_file(
            file_path="src/test.py",
            symbols=symbols,
            language="python",
        )

        assert result["file"] == "src/test.py"
        assert result["documentation"] is None  # No LLM means no file doc
        assert len(result["symbols"]) == 2

    @pytest.mark.asyncio
    async def test_enhance_file_with_source_code(self):
        """enhance_file reads source file and calls LLM."""
        # Create a temp file with source code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def calculate(x):\n    """Calc."""\n    return x * 2\n')
            temp_path = Path(f.name)

        try:
            # Create mock LLM response
            mock_response = MagicMock()
            mock_response.content = '''{"file_documentation": "Math utilities.", "symbols": {"calculate": "Multiplies input by 2."}}'''

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            enhancer = FileEnhancer(
                llm_service=mock_llm,
                source_root=temp_path.parent,
            )

            symbols = [
                {"name": "calculate", "type": "function", "documentation": "Calc."},
            ]

            result = await enhancer.enhance_file(
                file_path=temp_path.name,
                symbols=symbols,
                language="python",
            )

            # Verify LLM was called
            assert mock_llm._complete.called
            # Check result
            assert result["file"] == temp_path.name
            assert result["documentation"] == "Math utilities."
            assert result["symbols"][0]["documentation"] == "Multiplies input by 2."

        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_file_filters_private(self):
        """enhance_file filters private symbols by default."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('def public(): pass\ndef _private(): pass\n')
            temp_path = Path(f.name)

        try:
            mock_response = MagicMock()
            mock_response.content = '''{"file_documentation": "Test.", "symbols": {"public": "Public func."}}'''

            mock_llm = MagicMock()
            mock_llm._complete = AsyncMock(return_value=mock_response)

            enhancer = FileEnhancer(
                llm_service=mock_llm,
                source_root=temp_path.parent,
            )

            symbols = [
                {"name": "public", "type": "function"},
                {"name": "_private", "type": "function"},
            ]

            result = await enhancer.enhance_file(
                file_path=temp_path.name,
                symbols=symbols,
                language="python",
                include_private=False,
            )

            # Both symbols should be in result but only public enhanced
            assert len(result["symbols"]) == 2

        finally:
            temp_path.unlink()

    @pytest.mark.asyncio
    async def test_enhance_file_source_not_found(self):
        """enhance_file handles missing source files gracefully."""
        mock_llm = MagicMock()
        enhancer = FileEnhancer(
            llm_service=mock_llm,
            source_root=Path("/nonexistent"),
        )

        symbols = [{"name": "test", "type": "function"}]

        result = await enhancer.enhance_file(
            file_path="missing.py",
            symbols=symbols,
            language="python",
        )

        # Should return original data
        assert result["documentation"] is None
        assert result["symbols"] == symbols


class TestFormatFileEnhancementPrompt:
    """Tests for format_file_enhancement_prompt."""

    def test_basic_prompt(self):
        """Generates basic prompt with source and symbols."""
        prompt = format_file_enhancement_prompt(
            file_path="test.py",
            language="python",
            source_code="def foo(): pass",
            symbols=[{"name": "foo", "type": "function"}],
        )

        assert "test.py" in prompt
        assert "python" in prompt
        assert "def foo(): pass" in prompt
        assert "foo (function)" in prompt

    def test_truncates_long_code(self):
        """Truncates source code exceeding max chars."""
        long_code = "x" * 20000
        prompt = format_file_enhancement_prompt(
            file_path="test.py",
            language="python",
            source_code=long_code,
            symbols=[],
            max_code_chars=1000,
        )

        assert "[truncated]" in prompt
        assert len(prompt) < 20000

    def test_includes_existing_docs(self):
        """Includes existing documentation in prompt."""
        prompt = format_file_enhancement_prompt(
            file_path="test.py",
            language="python",
            source_code="def foo(): pass",
            symbols=[
                {"name": "foo", "type": "function", "documentation": "Does foo things."}
            ],
        )

        assert "existing doc:" in prompt
        assert "Does foo things" in prompt


class TestParseFileEnhancementResponse:
    """Tests for parse_file_enhancement_response."""

    def test_parse_valid_json(self):
        """Parses valid JSON response."""
        response = '{"file_documentation": "Test file.", "symbols": {"foo": "A function."}}'
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] == "Test file."
        assert result["symbols"]["foo"] == "A function."

    def test_parse_json_in_markdown(self):
        """Parses JSON wrapped in markdown code blocks."""
        response = '''```json
{"file_documentation": "Test.", "symbols": {"bar": "Bar func."}}
```'''
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] == "Test."
        assert result["symbols"]["bar"] == "Bar func."

    def test_parse_invalid_json(self):
        """Returns default for invalid JSON."""
        response = "This is not JSON"
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] is None
        assert result["symbols"] == {}

    def test_parse_empty_response(self):
        """Returns default for empty response."""
        result = parse_file_enhancement_response("")

        assert result["file_documentation"] is None
        assert result["symbols"] == {}

    def test_parse_partial_json(self):
        """Handles JSON with missing fields."""
        response = '{"file_documentation": "Only file doc."}'
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] == "Only file doc."
        assert result["symbols"] == {}

    def test_parse_json_with_invalid_escapes(self):
        """Handles JSON with invalid escape sequences like \\U from file paths."""
        # This is a common LLM mistake - returning Windows paths or regex without proper escaping
        response = '{"file_documentation": "Uses path C:\\Users\\test", "symbols": {}}'
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] is not None
        assert "Users" in result["file_documentation"]

    def test_parse_json_with_trailing_comma(self):
        """Handles JSON with trailing commas."""
        response = '{"file_documentation": "Test.", "symbols": {"foo": "Bar",}}'
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] == "Test."

    def test_parse_json_with_regex_escapes(self):
        """Handles JSON containing regex patterns with escapes."""
        response = '{"file_documentation": "Matches pattern \\\\d+ for digits", "symbols": {}}'
        result = parse_file_enhancement_response(response)

        assert result["file_documentation"] is not None


class TestSanitizeJsonString:
    """Tests for JSON sanitization function."""

    def test_sanitize_invalid_unicode_escape(self):
        """Fixes invalid \\U escape sequences."""
        from repo_ctx.analysis.prompts import sanitize_json_string

        content = '{"path": "C:\\Users\\test"}'
        sanitized = sanitize_json_string(content)
        # Should escape the backslashes so JSON can parse
        assert "\\\\U" in sanitized or "\\\\u" in sanitized.lower()

    def test_sanitize_trailing_comma(self):
        """Removes trailing commas."""
        from repo_ctx.analysis.prompts import sanitize_json_string

        content = '{"a": 1, "b": 2,}'
        sanitized = sanitize_json_string(content)
        assert sanitized == '{"a": 1, "b": 2}'

    def test_sanitize_valid_escapes_preserved(self):
        """Preserves valid escape sequences."""
        from repo_ctx.analysis.prompts import sanitize_json_string

        content = '{"text": "line1\\nline2\\ttab"}'
        sanitized = sanitize_json_string(content)
        assert "\\n" in sanitized
        assert "\\t" in sanitized

    def test_sanitize_empty_string(self):
        """Handles empty string."""
        from repo_ctx.analysis.prompts import sanitize_json_string

        assert sanitize_json_string("") == ""
        assert sanitize_json_string(None) is None


class TestEnhanceFilesParallel:
    """Tests for parallel file enhancement."""

    @pytest.mark.asyncio
    async def test_parallel_enhancement_empty_list(self):
        """Returns empty list for empty input."""
        mock_llm = MagicMock()
        enhancer = FileEnhancer(llm_service=mock_llm)

        result = await enhancer.enhance_files_parallel(files_data=[])
        assert result == []

    @pytest.mark.asyncio
    async def test_parallel_enhancement_multiple_files(self):
        """Processes multiple files in parallel."""
        import asyncio

        # Track call order and timing
        call_times = []

        async def mock_complete(prompt):
            """Mock LLM that takes 0.1s per call."""
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)
            response = MagicMock()
            response.content = '{"file_documentation": "Enhanced.", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        # Create temp files
        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            for i in range(3):
                (source_root / f"file{i}.py").write_text(f"# file {i}")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)

            files_data = [
                {"file": f"file{i}.py", "symbols": [], "language": "python"}
                for i in range(3)
            ]

            start = asyncio.get_event_loop().time()
            results = await enhancer.enhance_files_parallel(
                files_data=files_data,
                max_concurrency=3,  # All 3 should run concurrently
            )
            elapsed = asyncio.get_event_loop().time() - start

            # Should complete in ~0.1s, not ~0.3s (if parallel)
            assert elapsed < 0.25, f"Expected parallel execution, took {elapsed}s"
            assert len(results) == 3
            for r in results:
                assert r["documentation"] == "Enhanced."

    @pytest.mark.asyncio
    async def test_parallel_enhancement_respects_concurrency_limit(self):
        """Respects max_concurrency setting."""
        import asyncio

        concurrent_count = 0
        max_concurrent = 0
        lock = asyncio.Lock()

        async def mock_complete(prompt):
            nonlocal concurrent_count, max_concurrent
            async with lock:
                concurrent_count += 1
                max_concurrent = max(max_concurrent, concurrent_count)
            await asyncio.sleep(0.05)
            async with lock:
                concurrent_count -= 1
            response = MagicMock()
            response.content = '{"file_documentation": "Done.", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            for i in range(10):
                (source_root / f"file{i}.py").write_text(f"# file {i}")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)

            files_data = [
                {"file": f"file{i}.py", "symbols": [], "language": "python"}
                for i in range(10)
            ]

            await enhancer.enhance_files_parallel(
                files_data=files_data,
                max_concurrency=3,  # Limit to 3 concurrent
            )

            # Should never exceed concurrency limit
            assert max_concurrent <= 3, f"Max concurrent was {max_concurrent}, expected <= 3"

    @pytest.mark.asyncio
    async def test_parallel_enhancement_preserves_order(self):
        """Results are in same order as input."""
        import asyncio

        async def mock_complete(prompt):
            # Random delays to mix up completion order
            await asyncio.sleep(0.01 * (hash(prompt) % 10))
            response = MagicMock()
            # Extract file number from prompt for identification
            import re
            match = re.search(r'file(\d+)\.py', prompt)
            file_num = match.group(1) if match else "?"
            response.content = f'{{"file_documentation": "File {file_num}", "symbols": {{}}}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            for i in range(5):
                (source_root / f"file{i}.py").write_text(f"# file {i}")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)

            files_data = [
                {"file": f"file{i}.py", "symbols": [], "language": "python"}
                for i in range(5)
            ]

            results = await enhancer.enhance_files_parallel(
                files_data=files_data,
                max_concurrency=5,
            )

            # Verify order is preserved
            for i, result in enumerate(results):
                assert result["file"] == f"file{i}.py"
                assert result["documentation"] == f"File {i}"

    @pytest.mark.asyncio
    async def test_parallel_enhancement_progress_callback(self):
        """Progress callback is called for each file."""
        progress_calls = []

        def progress_callback(file_path: str, completed: int, total: int):
            progress_calls.append((file_path, completed, total))

        async def mock_complete(prompt):
            response = MagicMock()
            response.content = '{"file_documentation": "Done.", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            for i in range(3):
                (source_root / f"file{i}.py").write_text(f"# file {i}")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)

            files_data = [
                {"file": f"file{i}.py", "symbols": [], "language": "python"}
                for i in range(3)
            ]

            await enhancer.enhance_files_parallel(
                files_data=files_data,
                max_concurrency=2,
                progress_callback=progress_callback,
            )

            # Should have been called 3 times (once per file)
            assert len(progress_calls) == 3
            # All should have total=3
            assert all(call[2] == 3 for call in progress_calls)
            # Completed counts should be 1, 2, 3 (not necessarily in order due to parallelism)
            completed_counts = sorted([call[1] for call in progress_calls])
            assert completed_counts == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_parallel_enhancement_handles_exceptions(self):
        """Handles individual file failures gracefully."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            if "file1.py" in prompt:
                raise ValueError("Simulated failure")
            response = MagicMock()
            response.content = '{"file_documentation": "OK.", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            for i in range(3):
                (source_root / f"file{i}.py").write_text(f"# file {i}")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)

            files_data = [
                {"file": f"file{i}.py", "symbols": [{"name": f"func{i}"}], "language": "python"}
                for i in range(3)
            ]

            results = await enhancer.enhance_files_parallel(
                files_data=files_data,
                max_concurrency=3,
            )

            # Should return all 3 results
            assert len(results) == 3
            # file0 and file2 should succeed
            assert results[0]["documentation"] == "OK."
            assert results[2]["documentation"] == "OK."
            # file1 should have fallback (original symbols preserved)
            assert results[1]["file"] == "file1.py"
            assert results[1]["symbols"] == [{"name": "func1"}]


class TestRetryLogic:
    """Tests for retry logic on empty LLM responses."""

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
                response.content = '{"file_documentation": "Success!", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            (source_root / "test.py").write_text("# test file")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
            enhancer.RETRY_DELAY = 0.01  # Speed up test

            result = await enhancer.enhance_file(
                file_path="test.py",
                symbols=[],
                language="python",
            )

            assert call_count == 2
            assert result["documentation"] == "Success!"

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
                response.content = '{"file_documentation": "Third time!", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            (source_root / "test.py").write_text("# test file")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
            enhancer.RETRY_DELAY = 0.01  # Speed up test

            result = await enhancer.enhance_file(
                file_path="test.py",
                symbols=[],
                language="python",
            )

            assert call_count == 3
            assert result["documentation"] == "Third time!"

    @pytest.mark.asyncio
    async def test_all_retries_fail(self):
        """Returns original symbols when all retries fail."""
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

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            (source_root / "test.py").write_text("# test file")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
            enhancer.RETRY_DELAY = 0.01  # Speed up test

            original_symbols = [{"name": "my_func", "type": "function"}]
            result = await enhancer.enhance_file(
                file_path="test.py",
                symbols=original_symbols,
                language="python",
            )

            assert call_count == 3  # MAX_RETRIES
            assert result["documentation"] is None
            assert result["symbols"] == original_symbols

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
            response.content = '{"file_documentation": "Recovered!", "symbols": {}}'
            return response

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            (source_root / "test.py").write_text("# test file")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
            enhancer.RETRY_DELAY = 0.01  # Speed up test

            result = await enhancer.enhance_file(
                file_path="test.py",
                symbols=[],
                language="python",
            )

            assert call_count == 2
            assert result["documentation"] == "Recovered!"

    @pytest.mark.asyncio
    async def test_all_retries_fail_with_exceptions(self):
        """Returns original symbols when all retries fail with exceptions."""
        call_count = 0

        async def mock_complete(prompt):
            nonlocal call_count
            call_count += 1
            raise TimeoutError("API timeout")

        mock_llm = MagicMock()
        mock_llm._complete = mock_complete

        with tempfile.TemporaryDirectory() as tmpdir:
            source_root = Path(tmpdir)
            (source_root / "test.py").write_text("# test file")

            enhancer = FileEnhancer(llm_service=mock_llm, source_root=source_root)
            enhancer.RETRY_DELAY = 0.01  # Speed up test

            original_symbols = [{"name": "test_func", "type": "function"}]
            result = await enhancer.enhance_file(
                file_path="test.py",
                symbols=original_symbols,
                language="python",
            )

            assert call_count == 3  # MAX_RETRIES
            assert result["documentation"] is None
            assert result["symbols"] == original_symbols
