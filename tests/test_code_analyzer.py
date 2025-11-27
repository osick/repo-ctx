"""Tests for CodeAnalyzer core class."""
import pytest
from pathlib import Path
from repo_ctx.analysis.code_analyzer import CodeAnalyzer
from repo_ctx.analysis.models import Symbol, SymbolType


class TestCodeAnalyzer:
    """Test CodeAnalyzer core functionality."""

    def setup_method(self):
        """Set up analyzer for each test."""
        self.analyzer = CodeAnalyzer()

    def test_detect_language_python(self):
        """Test language detection for Python files."""
        assert self.analyzer.detect_language("test.py") == "python"
        assert self.analyzer.detect_language("/path/to/file.py") == "python"

    def test_detect_language_javascript(self):
        """Test language detection for JavaScript files."""
        assert self.analyzer.detect_language("test.js") == "javascript"
        assert self.analyzer.detect_language("test.jsx") == "javascript"

    def test_detect_language_typescript(self):
        """Test language detection for TypeScript files."""
        assert self.analyzer.detect_language("test.ts") == "typescript"
        assert self.analyzer.detect_language("test.tsx") == "typescript"

    def test_detect_language_unknown(self):
        """Test language detection for unknown files."""
        assert self.analyzer.detect_language("test.txt") is None
        assert self.analyzer.detect_language("README.md") is None

    def test_analyze_python_file(self):
        """Test analyzing a Python file."""
        code = """
def hello():
    print("Hello")

class Greeter:
    def greet(self):
        return "Hi"
"""
        symbols = self.analyzer.analyze_file(code, "test.py")

        assert len(symbols) >= 3  # hello function, Greeter class, greet method
        symbol_names = {s.name for s in symbols}
        assert "hello" in symbol_names
        assert "Greeter" in symbol_names
        assert "greet" in symbol_names

    def test_analyze_javascript_file(self):
        """Test analyzing a JavaScript file."""
        code = """
function hello() {
    console.log("Hello");
}

class Greeter {
    greet() {
        return "Hi";
    }
}
"""
        symbols = self.analyzer.analyze_file(code, "test.js")

        assert len(symbols) >= 3
        symbol_names = {s.name for s in symbols}
        assert "hello" in symbol_names
        assert "Greeter" in symbol_names
        assert "greet" in symbol_names

    def test_analyze_typescript_file(self):
        """Test analyzing a TypeScript file."""
        code = """
interface User {
    name: string;
}

function getUser(): User {
    return { name: "Alice" };
}
"""
        symbols = self.analyzer.analyze_file(code, "test.ts")

        assert len(symbols) >= 2
        symbol_names = {s.name for s in symbols}
        assert "User" in symbol_names
        assert "getUser" in symbol_names

        # Check that interface is correctly typed
        interfaces = [s for s in symbols if s.symbol_type == SymbolType.INTERFACE]
        assert len(interfaces) == 1
        assert interfaces[0].name == "User"

    def test_analyze_unsupported_language(self):
        """Test analyzing unsupported file returns empty list."""
        code = "Some random text"
        symbols = self.analyzer.analyze_file(code, "test.txt")

        assert symbols == []

    def test_get_supported_languages(self):
        """Test getting list of supported languages."""
        languages = self.analyzer.get_supported_languages()

        assert "python" in languages
        assert "javascript" in languages
        assert "typescript" in languages
        assert len(languages) >= 3

    def test_extract_dependencies_from_file(self):
        """Test extracting dependencies from a file."""
        code = """
import os
from pathlib import Path

def process():
    os.path.join("a", "b")
"""
        deps = self.analyzer.extract_dependencies(code, "test.py")

        assert len(deps) >= 2
        modules = {d["target"] for d in deps}
        assert "os" in modules
        assert "pathlib" in modules

    def test_analyze_multiple_files(self):
        """Test analyzing multiple files at once."""
        files = {
            "module1.py": """
def func1():
    pass
""",
            "module2.py": """
class MyClass:
    pass
""",
            "utils.js": """
function helper() {}
"""
        }

        result = self.analyzer.analyze_files(files)

        assert "module1.py" in result
        assert "module2.py" in result
        assert "utils.js" in result

        assert len(result["module1.py"]) >= 1
        assert len(result["module2.py"]) >= 1
        assert len(result["utils.js"]) >= 1

    def test_get_symbols_by_type(self):
        """Test filtering symbols by type."""
        code = """
class MyClass:
    pass

def my_function():
    pass

MY_CONSTANT = 42
"""
        symbols = self.analyzer.analyze_file(code, "test.py")

        classes = self.analyzer.filter_symbols_by_type(symbols, SymbolType.CLASS)
        functions = self.analyzer.filter_symbols_by_type(symbols, SymbolType.FUNCTION)

        assert len(classes) == 1
        assert classes[0].name == "MyClass"

        assert len(functions) == 1
        assert functions[0].name == "my_function"

    def test_get_symbols_by_visibility(self):
        """Test filtering symbols by visibility."""
        code = """
def public_func():
    pass

def _private_func():
    pass
"""
        symbols = self.analyzer.analyze_file(code, "test.py")

        public = self.analyzer.filter_symbols_by_visibility(symbols, "public")
        private = self.analyzer.filter_symbols_by_visibility(symbols, "private")

        assert len(public) == 1
        assert public[0].name == "public_func"

        assert len(private) == 1
        assert private[0].name == "_private_func"

    def test_get_symbol_statistics(self):
        """Test getting symbol statistics."""
        code = """
class Class1:
    def method1(self):
        pass

class Class2:
    pass

def func1():
    pass

def func2():
    pass

def func3():
    pass
"""
        symbols = self.analyzer.analyze_file(code, "test.py")
        stats = self.analyzer.get_statistics(symbols)

        # 2 classes + 3 functions + 1 method = 6 symbols
        assert stats["total_symbols"] == 6
        assert stats["by_type"][SymbolType.CLASS.value] == 2
        assert stats["by_type"][SymbolType.FUNCTION.value] == 3
        assert stats["by_type"][SymbolType.METHOD.value] == 1


class TestCodeAnalyzerIntegration:
    """Integration tests for CodeAnalyzer."""

    def setup_method(self):
        """Set up analyzer for each test."""
        self.analyzer = CodeAnalyzer()

    def test_analyze_mixed_language_project(self):
        """Test analyzing a project with multiple languages."""
        files = {
            "backend.py": """
class UserService:
    def get_user(self, id):
        return {"id": id}
""",
            "frontend.ts": """
interface User {
    id: number;
}

function fetchUser(id: number): User {
    return { id };
}
""",
            "utils.js": """
function logMessage(msg) {
    console.log(msg);
}

class Logger {
    log(msg) {
        console.log(msg);
    }
}
"""
        }

        result = self.analyzer.analyze_files(files)

        # Verify all files analyzed
        assert len(result) == 3

        # Verify Python symbols
        py_symbols = result["backend.py"]
        py_names = {s.name for s in py_symbols}
        assert "UserService" in py_names
        assert "get_user" in py_names

        # Verify TypeScript symbols
        ts_symbols = result["frontend.ts"]
        ts_names = {s.name for s in ts_symbols}
        assert "User" in ts_names
        assert "fetchUser" in ts_names

        # Verify JavaScript symbols
        js_symbols = result["utils.js"]
        js_names = {s.name for s in js_symbols}
        assert "logMessage" in js_names
        assert "Logger" in js_names
