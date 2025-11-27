"""Tests for MCP code analysis tools."""
import pytest
from pathlib import Path


class TestMCPToolSchemas:
    """Test MCP tool schema definitions."""

    @pytest.mark.asyncio
    async def test_mcp_server_imports(self):
        """Test that MCP server imports correctly."""
        from repo_ctx.mcp_server import serve
        assert serve is not None

    @pytest.mark.asyncio
    async def test_analyze_tool_handler_logic(self):
        """Test repo-ctx-analyze handler logic directly."""
        from repo_ctx.analysis import CodeAnalyzer, SymbolType
        import tempfile
        import os

        # Create test file
        test_code = """
def test_function():
    pass

class TestClass:
    def method(self):
        pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()
            path_obj = Path(test_file)

            # Simulate handler logic
            files = {}
            if analyzer.detect_language(str(path_obj)):
                with open(path_obj, 'r', encoding='utf-8') as f:
                    files[str(path_obj)] = f.read()

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Verify symbols were extracted
            assert len(all_symbols) >= 3  # function, class, method
            symbol_names = {s.name for s in all_symbols}
            assert "test_function" in symbol_names
            assert "TestClass" in symbol_names
            assert "method" in symbol_names

            # Test filtering by type
            filtered = analyzer.filter_symbols_by_type(all_symbols, SymbolType.FUNCTION)
            assert len(filtered) >= 1
            assert all(s.symbol_type == SymbolType.FUNCTION for s in filtered)

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_search_symbol_handler_logic(self):
        """Test repo-ctx-search-symbol handler logic."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        # Create test file
        test_code = """
def getUserById(id):
    pass

def getUserByEmail(email):
    pass

def createPost():
    pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()

            # Read and analyze
            files = {}
            with open(test_file, 'r', encoding='utf-8') as f:
                files[test_file] = f.read()

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Search for "user"
            query = "user"
            matching = [s for s in all_symbols if query in s.name.lower()]

            assert len(matching) == 2
            names = {s.name for s in matching}
            assert "getUserById" in names
            assert "getUserByEmail" in names
            assert "createPost" not in names

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_get_symbol_detail_handler_logic(self):
        """Test repo-ctx-get-symbol-detail handler logic."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        # Create test file
        test_code = '''
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()

            # Read and analyze
            files = {}
            with open(test_file, 'r', encoding='utf-8') as f:
                files[test_file] = f.read()

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Find specific symbol
            symbol_name = "calculate_sum"
            matching = [s for s in all_symbols if s.name == symbol_name]

            assert len(matching) == 1
            symbol = matching[0]
            assert symbol.name == "calculate_sum"
            assert symbol.documentation is not None
            assert "sum" in symbol.documentation.lower()

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_get_file_symbols_handler_logic(self):
        """Test repo-ctx-get-file-symbols handler logic."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        # Create test file
        test_code = """
class MyClass:
    def method1(self):
        pass
    def method2(self):
        pass

def function1():
    pass

def function2():
    pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()

            # Read and analyze
            with open(test_file, 'r', encoding='utf-8') as f:
                code = f.read()

            symbols = analyzer.analyze_file(code, test_file)

            # Group by type
            by_type = {}
            for symbol in symbols:
                stype = symbol.symbol_type.value
                if stype not in by_type:
                    by_type[stype] = []
                by_type[stype].append(symbol)

            # Verify grouping
            assert "class" in by_type
            assert "method" in by_type or "function" in by_type  # Methods might be classified differently
            assert len(symbols) >= 3  # class + methods + functions

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_directory_analysis(self):
        """Test analyzing a directory with multiple files."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        # Create temp directory with multiple files
        with tempfile.TemporaryDirectory() as tmpdir:
            # Python file
            py_file = os.path.join(tmpdir, "test.py")
            with open(py_file, 'w') as f:
                f.write("def py_func(): pass")

            # JavaScript file
            js_file = os.path.join(tmpdir, "test.js")
            with open(js_file, 'w') as f:
                f.write("function jsFunc() {}")

            # Analyze directory
            analyzer = CodeAnalyzer()
            files = {}

            for root, _, filenames in os.walk(tmpdir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if analyzer.detect_language(filename):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files[file_path] = f.read()

            assert len(files) == 2

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Should find symbols from both files
            assert len(all_symbols) >= 2
            names = {s.name for s in all_symbols}
            assert "py_func" in names
            assert "jsFunc" in names


class TestMCPToolErrorHandling:
    """Test error handling in MCP tools."""

    @pytest.mark.asyncio
    async def test_nonexistent_path(self):
        """Test handling of nonexistent paths."""
        from pathlib import Path

        path = "/nonexistent/path/to/file.py"
        path_obj = Path(path)

        assert not path_obj.exists()

    @pytest.mark.asyncio
    async def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        # Create non-code file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Some text content")
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()
            language = analyzer.detect_language(test_file)

            assert language is None

        finally:
            os.unlink(test_file)

    @pytest.mark.asyncio
    async def test_empty_directory(self):
        """Test handling of directory with no supported files."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create only non-code files
            txt_file = os.path.join(tmpdir, "readme.txt")
            with open(txt_file, 'w') as f:
                f.write("Not a code file")

            analyzer = CodeAnalyzer()
            files = {}

            for root, _, filenames in os.walk(tmpdir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if analyzer.detect_language(filename):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files[file_path] = f.read()

            assert len(files) == 0


class TestMCPToolFiltering:
    """Test filtering capabilities of MCP tools."""

    @pytest.mark.asyncio
    async def test_language_filtering(self):
        """Test filtering by language."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmpdir:
            # Python file
            py_file = os.path.join(tmpdir, "test.py")
            with open(py_file, 'w') as f:
                f.write("def py_func(): pass")

            # JavaScript file
            js_file = os.path.join(tmpdir, "test.js")
            with open(js_file, 'w') as f:
                f.write("function jsFunc() {}")

            analyzer = CodeAnalyzer()
            files = {}

            for root, _, filenames in os.walk(tmpdir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if analyzer.detect_language(filename):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            files[file_path] = f.read()

            results = analyzer.analyze_files(files)
            all_symbols = analyzer.aggregate_symbols(results)

            # Filter by language
            python_symbols = [s for s in all_symbols if s.language == "python"]
            js_symbols = [s for s in all_symbols if s.language == "javascript"]

            assert len(python_symbols) >= 1
            assert len(js_symbols) >= 1
            assert all(s.language == "python" for s in python_symbols)
            assert all(s.language == "javascript" for s in js_symbols)

    @pytest.mark.asyncio
    async def test_visibility_filtering(self):
        """Test filtering by visibility."""
        from repo_ctx.analysis import CodeAnalyzer
        import tempfile
        import os

        test_code = """
def public_func():
    pass

def _private_func():
    pass
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            analyzer = CodeAnalyzer()

            with open(test_file, 'r', encoding='utf-8') as f:
                code = f.read()

            symbols = analyzer.analyze_file(code, test_file)

            # Filter public vs private
            public = analyzer.filter_symbols_by_visibility(symbols, "public")
            private = analyzer.filter_symbols_by_visibility(symbols, "private")

            assert len(public) >= 1
            assert len(private) >= 1
            assert all(s.visibility == "public" for s in public)
            assert all(s.visibility == "private" for s in private)

        finally:
            os.unlink(test_file)


class TestMCPToolStructuredOutput:
    """Test structured output (JSON/YAML) for MCP analysis tools."""

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file."""
        code = '''
class Calculator:
    """A calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
'''
        file_path = tmp_path / "calc.py"
        file_path.write_text(code)
        return file_path

    def test_analyze_json_output(self, sample_python_file):
        """Test repo-ctx-analyze with JSON output."""
        from repo_ctx.analysis import CodeAnalyzer
        import json

        analyzer = CodeAnalyzer()
        with open(sample_python_file, 'r') as f:
            code = f.read()

        symbols = analyzer.analyze_file(code, str(sample_python_file))
        stats = analyzer.get_statistics(symbols)

        # Build output similar to MCP tool
        output_data = {
            "path": str(sample_python_file),
            "files_analyzed": 1,
            "statistics": stats,
            "symbols": [
                {
                    "name": s.name,
                    "type": s.symbol_type.value,
                    "file": s.file_path,
                    "line": s.line_start,
                    "signature": s.signature,
                    "visibility": s.visibility,
                    "language": s.language,
                    "qualified_name": s.qualified_name,
                    "documentation": s.documentation
                }
                for s in symbols
            ]
        }

        json_output = json.dumps(output_data, indent=2)
        parsed = json.loads(json_output)

        assert "path" in parsed
        assert "symbols" in parsed
        assert len(parsed["symbols"]) >= 2  # class + method

    def test_symbol_detail_json_output(self, sample_python_file):
        """Test symbol detail with JSON output structure."""
        from repo_ctx.analysis import CodeAnalyzer
        import json

        analyzer = CodeAnalyzer()
        with open(sample_python_file, 'r') as f:
            code = f.read()

        symbols = analyzer.analyze_file(code, str(sample_python_file))
        symbol = symbols[0]  # Calculator class

        output_data = {
            "name": symbol.name,
            "type": symbol.symbol_type.value,
            "language": symbol.language,
            "file": symbol.file_path,
            "line_start": symbol.line_start,
            "line_end": symbol.line_end,
            "visibility": symbol.visibility,
            "qualified_name": symbol.qualified_name,
            "signature": symbol.signature,
            "documentation": symbol.documentation,
            "is_exported": symbol.is_exported,
            "metadata": symbol.metadata
        }

        json_output = json.dumps(output_data, indent=2)
        parsed = json.loads(json_output)

        assert parsed["name"] == "Calculator"
        assert parsed["type"] == "class"
        assert "documentation" in parsed

    def test_file_symbols_json_output(self, sample_python_file):
        """Test file symbols with JSON output structure."""
        from repo_ctx.analysis import CodeAnalyzer
        import json

        analyzer = CodeAnalyzer()
        language = analyzer.detect_language(str(sample_python_file))

        with open(sample_python_file, 'r') as f:
            code = f.read()

        symbols = analyzer.analyze_file(code, str(sample_python_file))

        output_data = {
            "file": str(sample_python_file),
            "language": language,
            "total_symbols": len(symbols),
            "symbols": [
                {
                    "name": s.name,
                    "type": s.symbol_type.value,
                    "line": s.line_start,
                    "line_end": s.line_end,
                    "signature": s.signature,
                    "visibility": s.visibility,
                    "qualified_name": s.qualified_name,
                    "documentation": s.documentation
                }
                for s in sorted(symbols, key=lambda s: s.line_start or 0)
            ]
        }

        # Add grouped view
        by_type = {}
        for s in symbols:
            stype = s.symbol_type.value
            if stype not in by_type:
                by_type[stype] = []
            by_type[stype].append(s.name)
        output_data["symbols_by_type"] = by_type

        json_output = json.dumps(output_data, indent=2)
        parsed = json.loads(json_output)

        assert parsed["language"] == "python"
        assert "symbols" in parsed
        assert "symbols_by_type" in parsed
        assert "class" in parsed["symbols_by_type"]

    def test_yaml_output(self, sample_python_file):
        """Test YAML output format."""
        from repo_ctx.analysis import CodeAnalyzer
        import yaml

        analyzer = CodeAnalyzer()
        with open(sample_python_file, 'r') as f:
            code = f.read()

        symbols = analyzer.analyze_file(code, str(sample_python_file))

        output_data = {
            "file": str(sample_python_file),
            "total_symbols": len(symbols),
            "symbols": [{"name": s.name, "type": s.symbol_type.value} for s in symbols]
        }

        yaml_output = yaml.dump(output_data, default_flow_style=False, sort_keys=False)
        parsed = yaml.safe_load(yaml_output)

        assert "file" in parsed
        assert "symbols" in parsed

    def test_kotlin_language_support(self, tmp_path):
        """Test Kotlin language is supported in analysis."""
        from repo_ctx.analysis import CodeAnalyzer

        # Create Kotlin file
        kotlin_code = '''
class UserService {
    fun getUser(id: Int): User {
        return User(id)
    }
}
'''
        kt_file = tmp_path / "service.kt"
        kt_file.write_text(kotlin_code)

        analyzer = CodeAnalyzer()
        language = analyzer.detect_language(str(kt_file))
        assert language == "kotlin"

        symbols = analyzer.analyze_file(kotlin_code, str(kt_file))
        assert len(symbols) >= 2  # class + method

        symbol_names = {s.name for s in symbols}
        assert "UserService" in symbol_names
        assert "getUser" in symbol_names
