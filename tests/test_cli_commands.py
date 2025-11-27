"""Tests for CLI commands."""
import pytest
import os
import tempfile
from pathlib import Path


class TestCLIAnalyzeCommand:
    """Test the analyze CLI command."""

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file for testing."""
        code = '''
class Calculator:
    """A simple calculator class."""

    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    def subtract(self, a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b


def main():
    """Main function."""
    calc = Calculator()
    print(calc.add(1, 2))
'''
        file_path = tmp_path / "calculator.py"
        file_path.write_text(code)
        return file_path

    @pytest.fixture
    def sample_js_file(self, tmp_path):
        """Create a sample JavaScript file for testing."""
        code = '''
import { Component } from 'react';

/**
 * A simple component.
 */
class MyComponent extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return null;
    }
}

function helperFunction() {
    return 42;
}

export default MyComponent;
'''
        file_path = tmp_path / "component.js"
        file_path.write_text(code)
        return file_path


class TestSearchSymbolCommand:
    """Test the search-symbol CLI command."""

    def test_search_symbol_finds_class(self, tmp_path):
        """Test that search-symbol finds a class."""
        from repo_ctx.__main__ import search_symbol_command
        import asyncio

        code = '''
class UserService:
    def get_user(self, id):
        pass

class ProductService:
    def get_product(self, id):
        pass
'''
        file_path = tmp_path / "services.py"
        file_path.write_text(code)

        # The command prints to stdout, so we just verify it doesn't crash
        asyncio.run(search_symbol_command(
            path=str(tmp_path),
            query="Service",
            output="text"
        ))

    def test_search_symbol_with_filter(self, tmp_path):
        """Test search-symbol with type filter."""
        from repo_ctx.__main__ import search_symbol_command
        import asyncio

        code = '''
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass
'''
        file_path = tmp_path / "example.py"
        file_path.write_text(code)

        asyncio.run(search_symbol_command(
            path=str(tmp_path),
            query="my",
            output="text",
            filter_type="class"
        ))

    def test_search_symbol_json_output(self, tmp_path, capsys):
        """Test search-symbol with JSON output."""
        from repo_ctx.__main__ import search_symbol_command
        import asyncio
        import json

        code = '''
class TestClass:
    pass
'''
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        asyncio.run(search_symbol_command(
            path=str(tmp_path),
            query="Test",
            output="json"
        ))

        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "query" in data
        assert "matches_found" in data
        assert "symbols" in data


class TestSymbolDetailCommand:
    """Test the symbol-detail CLI command."""

    def test_symbol_detail_finds_class(self, tmp_path, capsys):
        """Test that symbol-detail finds a class."""
        from repo_ctx.__main__ import symbol_detail_command
        import asyncio

        code = '''
class UserManager:
    """Manages user operations."""

    def create_user(self, name: str):
        """Create a new user."""
        pass
'''
        file_path = tmp_path / "user_manager.py"
        file_path.write_text(code)

        asyncio.run(symbol_detail_command(
            path=str(tmp_path),
            symbol_name="UserManager",
            output="text"
        ))

        captured = capsys.readouterr()
        assert "UserManager" in captured.out
        assert "class" in captured.out

    def test_symbol_detail_not_found(self, tmp_path, capsys):
        """Test symbol-detail when symbol not found."""
        from repo_ctx.__main__ import symbol_detail_command
        import asyncio

        code = '''
class SomeClass:
    pass
'''
        file_path = tmp_path / "some.py"
        file_path.write_text(code)

        asyncio.run(symbol_detail_command(
            path=str(tmp_path),
            symbol_name="NonExistent",
            output="text"
        ))

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_symbol_detail_json_output(self, tmp_path, capsys):
        """Test symbol-detail with JSON output."""
        from repo_ctx.__main__ import symbol_detail_command
        import asyncio
        import json

        code = '''
def my_function():
    """A test function."""
    pass
'''
        file_path = tmp_path / "funcs.py"
        file_path.write_text(code)

        asyncio.run(symbol_detail_command(
            path=str(tmp_path),
            symbol_name="my_function",
            output="json"
        ))

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "my_function"
        assert "type" in data


class TestFileSymbolsCommand:
    """Test the file-symbols CLI command."""

    def test_file_symbols_lists_all(self, tmp_path, capsys):
        """Test that file-symbols lists all symbols."""
        from repo_ctx.__main__ import file_symbols_command
        import asyncio

        code = '''
class First:
    def method_a(self):
        pass

class Second:
    def method_b(self):
        pass

def standalone():
    pass
'''
        file_path = tmp_path / "multiple.py"
        file_path.write_text(code)

        asyncio.run(file_symbols_command(
            file_path=str(file_path),
            output="text"
        ))

        captured = capsys.readouterr()
        assert "First" in captured.out
        assert "Second" in captured.out
        assert "method_a" in captured.out
        assert "method_b" in captured.out

    def test_file_symbols_json_output(self, tmp_path, capsys):
        """Test file-symbols with JSON output."""
        from repo_ctx.__main__ import file_symbols_command
        import asyncio
        import json

        code = '''
class MyClass:
    pass
'''
        file_path = tmp_path / "simple.py"
        file_path.write_text(code)

        asyncio.run(file_symbols_command(
            file_path=str(file_path),
            output="json"
        ))

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "file" in data
        assert "symbols" in data
        assert len(data["symbols"]) >= 1

    def test_file_symbols_nonexistent_file(self, tmp_path, capsys):
        """Test file-symbols with non-existent file."""
        from repo_ctx.__main__ import file_symbols_command
        import asyncio

        asyncio.run(file_symbols_command(
            file_path=str(tmp_path / "nonexistent.py"),
            output="text"
        ))

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_file_symbols_unsupported_type(self, tmp_path, capsys):
        """Test file-symbols with unsupported file type."""
        from repo_ctx.__main__ import file_symbols_command
        import asyncio

        file_path = tmp_path / "readme.txt"
        file_path.write_text("Just some text")

        asyncio.run(file_symbols_command(
            file_path=str(file_path),
            output="text"
        ))

        captured = capsys.readouterr()
        assert "Unsupported" in captured.out


class TestAnalyzeDependencies:
    """Test the analyze --show-dependencies functionality."""

    def test_analyze_shows_dependencies(self, tmp_path, capsys):
        """Test that analyze --show-dependencies shows import dependencies."""
        from repo_ctx.__main__ import analyze_command
        import asyncio

        code = '''
import os
from pathlib import Path
from typing import List

class MyClass:
    pass
'''
        file_path = tmp_path / "with_imports.py"
        file_path.write_text(code)

        asyncio.run(analyze_command(
            path=str(tmp_path),
            output="text",
            show_dependencies=True,
            show_callgraph=False,
            filter_type=None,
            language=None,
            provider_type=None,
            config=None
        ))

        captured = capsys.readouterr()
        assert "Dependencies" in captured.out
        assert "os" in captured.out
        assert "pathlib" in captured.out


class TestAnalyzeCallgraph:
    """Test the analyze --show-callgraph functionality."""

    def test_analyze_shows_callgraph(self, tmp_path, capsys):
        """Test that analyze --show-callgraph shows class/method structure."""
        from repo_ctx.__main__ import analyze_command
        import asyncio

        code = '''
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
'''
        file_path = tmp_path / "calc.py"
        file_path.write_text(code)

        asyncio.run(analyze_command(
            path=str(tmp_path),
            output="text",
            show_dependencies=False,
            show_callgraph=True,
            filter_type=None,
            language=None,
            provider_type=None,
            config=None
        ))

        captured = capsys.readouterr()
        assert "Call Graph" in captured.out
        assert "Calculator" in captured.out


class TestLibraryAPI:
    """Test the library API exports."""

    def test_imports(self):
        """Test that all expected exports are available."""
        from repo_ctx import (
            __version__,
            GitLabContext,
            RepositoryContext,
            Config,
            Storage,
            CodeAnalyzer,
            Symbol,
            SymbolType,
            Dependency,
            PythonExtractor,
            JavaScriptExtractor,
            JavaExtractor,
            KotlinExtractor,
            Library,
            Document,
        )

        assert __version__ is not None
        assert CodeAnalyzer is not None
        assert SymbolType is not None

    def test_code_analyzer_usage(self):
        """Test basic CodeAnalyzer usage through library API."""
        from repo_ctx import CodeAnalyzer, SymbolType

        analyzer = CodeAnalyzer()

        code = '''
class Test:
    def method(self):
        pass
'''
        symbols = analyzer.analyze_file(code, "test.py")
        assert len(symbols) >= 1

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "Test"
