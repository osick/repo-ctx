"""Tests for CLI commands."""
import pytest
import os
import tempfile
import json
from argparse import Namespace
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
    """Test the code find CLI command."""

    def test_search_symbol_finds_class(self, tmp_path):
        """Test that code find finds a class."""
        from repo_ctx.cli.commands import code_find

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

        args = Namespace(
            path=str(tmp_path),
            query="Service",
            output="text",
            type=None,
            lang=None
        )
        # The command prints to stdout, so we just verify it doesn't crash
        code_find(args)

    def test_search_symbol_with_filter(self, tmp_path):
        """Test code find with type filter."""
        from repo_ctx.cli.commands import code_find

        code = '''
class MyClass:
    def my_method(self):
        pass

def my_function():
    pass
'''
        file_path = tmp_path / "example.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            query="my",
            output="text",
            type="class",
            lang=None
        )
        code_find(args)

    def test_search_symbol_json_output(self, tmp_path, capsys):
        """Test code find with JSON output."""
        from repo_ctx.cli.commands import code_find

        code = '''
class TestClass:
    pass
'''
        file_path = tmp_path / "test.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            query="Test",
            output="json",
            type=None,
            lang=None
        )
        code_find(args)

        captured = capsys.readouterr()
        # Should be valid JSON
        data = json.loads(captured.out)
        assert "query" in data
        assert "count" in data
        assert "symbols" in data


class TestSymbolDetailCommand:
    """Test the code info CLI command."""

    def test_symbol_detail_finds_class(self, tmp_path, capsys):
        """Test that code info finds a class."""
        from repo_ctx.cli.commands import code_info

        code = '''
class UserManager:
    """Manages user operations."""

    def create_user(self, name: str):
        """Create a new user."""
        pass
'''
        file_path = tmp_path / "user_manager.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            name="UserManager",
            output="text"
        )
        code_info(args)

        captured = capsys.readouterr()
        assert "UserManager" in captured.out
        assert "class" in captured.out

    def test_symbol_detail_not_found(self, tmp_path, capsys):
        """Test code info when symbol not found."""
        from repo_ctx.cli.commands import code_info

        code = '''
class SomeClass:
    pass
'''
        file_path = tmp_path / "some.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            name="NonExistent",
            output="text"
        )
        code_info(args)

        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_symbol_detail_json_output(self, tmp_path, capsys):
        """Test code info with JSON output."""
        from repo_ctx.cli.commands import code_info

        code = '''
def my_function():
    """A test function."""
    pass
'''
        file_path = tmp_path / "funcs.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            name="my_function",
            output="json"
        )
        code_info(args)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "my_function"
        assert "type" in data


class TestFileSymbolsCommand:
    """Test the code symbols CLI command."""

    def test_file_symbols_lists_all(self, tmp_path, capsys):
        """Test that code symbols lists all symbols."""
        from repo_ctx.cli.commands import code_symbols

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

        args = Namespace(
            file=str(file_path),
            output="text",
            group=False
        )
        code_symbols(args)

        captured = capsys.readouterr()
        assert "First" in captured.out
        assert "Second" in captured.out
        assert "method_a" in captured.out
        assert "method_b" in captured.out

    def test_file_symbols_json_output(self, tmp_path, capsys):
        """Test code symbols with JSON output."""
        from repo_ctx.cli.commands import code_symbols

        code = '''
class MyClass:
    pass
'''
        file_path = tmp_path / "simple.py"
        file_path.write_text(code)

        args = Namespace(
            file=str(file_path),
            output="json",
            group=False
        )
        code_symbols(args)

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "file" in data
        assert "symbols" in data
        assert len(data["symbols"]) >= 1

    def test_file_symbols_nonexistent_file(self, tmp_path, capsys):
        """Test code symbols with non-existent file."""
        from repo_ctx.cli.commands import code_symbols

        args = Namespace(
            file=str(tmp_path / "nonexistent.py"),
            output="text",
            group=False
        )

        with pytest.raises(SystemExit):
            code_symbols(args)

        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_file_symbols_unsupported_type(self, tmp_path, capsys):
        """Test code symbols with unsupported file type."""
        from repo_ctx.cli.commands import code_symbols

        file_path = tmp_path / "readme.txt"
        file_path.write_text("Just some text")

        args = Namespace(
            file=str(file_path),
            output="text",
            group=False
        )

        with pytest.raises(SystemExit):
            code_symbols(args)

        captured = capsys.readouterr()
        assert "Unsupported" in captured.out


class TestAnalyzeDependencies:
    """Test the code analyze --deps functionality."""

    def test_analyze_shows_dependencies(self, tmp_path, capsys):
        """Test that code analyze --deps shows import dependencies."""
        from repo_ctx.cli.commands import code_analyze

        code = '''
import os
from pathlib import Path
from typing import List

class MyClass:
    pass
'''
        file_path = tmp_path / "with_imports.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            output="text",
            deps=True,
            callgraph=False,
            type=None,
            lang=None
        )
        code_analyze(args)

        captured = capsys.readouterr()
        assert "Dependencies" in captured.out
        assert "os" in captured.out
        assert "pathlib" in captured.out


class TestAnalyzeCallgraph:
    """Test the code analyze command with symbols."""

    def test_analyze_shows_symbols(self, tmp_path, capsys):
        """Test that code analyze shows class/method structure."""
        from repo_ctx.cli.commands import code_analyze

        code = '''
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
'''
        file_path = tmp_path / "calc.py"
        file_path.write_text(code)

        args = Namespace(
            path=str(tmp_path),
            output="text",
            deps=False,
            callgraph=False,
            type=None,
            lang=None
        )
        code_analyze(args)

        captured = capsys.readouterr()
        assert "Calculator" in captured.out or "class" in captured.out


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
