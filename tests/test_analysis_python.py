"""Tests for Python code analysis."""
import pytest
from repo_ctx.analysis.python_extractor import PythonExtractor
from repo_ctx.analysis.models import Symbol, SymbolType


class TestPythonSymbolExtraction:
    """Test Python symbol extraction."""

    def setup_method(self):
        """Set up extractor for each test."""
        self.extractor = PythonExtractor()

    def test_extract_function_simple(self):
        """Test extracting a simple function."""
        code = """
def hello_world():
    print("Hello, World!")
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "hello_world"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.line_start == 2
        assert symbol.visibility == "public"

    def test_extract_function_with_parameters(self):
        """Test extracting function with parameters and return type."""
        code = """
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age}"
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "greet"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert "name: str" in symbol.signature
        assert "age: int" in symbol.signature
        assert "-> str" in symbol.signature

    def test_extract_class(self):
        """Test extracting a class definition."""
        code = """
class User:
    def __init__(self, name):
        self.name = name

    def greet(self):
        return f"Hello, {self.name}"
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        # Should find class and its methods
        class_symbols = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        method_symbols = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(class_symbols) == 1
        assert class_symbols[0].name == "User"

        assert len(method_symbols) == 2
        method_names = {s.name for s in method_symbols}
        assert "__init__" in method_names
        assert "greet" in method_names

    def test_extract_class_with_inheritance(self):
        """Test extracting class with inheritance."""
        code = """
class Animal:
    pass

class Dog(Animal):
    def bark(self):
        return "Woof!"
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 2

        dog_class = [s for s in classes if s.name == "Dog"][0]
        assert dog_class.metadata.get("bases") == ["Animal"]

    def test_extract_private_function(self):
        """Test extracting private function (leading underscore)."""
        code = """
def _private_helper():
    pass

def __very_private():
    pass
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 2
        private = [s for s in symbols if s.name == "_private_helper"][0]
        very_private = [s for s in symbols if s.name == "__very_private"][0]

        assert private.visibility == "private"
        assert very_private.visibility == "private"

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = """
import os
import sys
from pathlib import Path
from typing import List, Dict
"""
        imports = self.extractor.extract_imports(code, "test.py")

        assert len(imports) >= 4
        import_modules = {imp["module"] for imp in imports}
        assert "os" in import_modules
        assert "sys" in import_modules
        assert "pathlib" in import_modules
        assert "typing" in import_modules

    def test_extract_function_calls(self):
        """Test extracting function calls."""
        code = """
def process_data(data):
    validate(data)
    result = transform(data)
    save(result)
    return result
"""
        symbols = self.extractor.extract_symbols(code, "test.py")
        func = symbols[0]

        calls = self.extractor.extract_calls(code, "test.py", func)

        call_names = {call["name"] for call in calls}
        assert "validate" in call_names
        assert "transform" in call_names
        assert "save" in call_names

    def test_extract_docstring(self):
        """Test extracting function docstring."""
        code = '''
def documented_function():
    """This is a well-documented function.

    It does important things.
    """
    pass
'''
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.documentation is not None
        assert "well-documented function" in symbol.documentation

    def test_extract_async_function(self):
        """Test extracting async function."""
        code = """
async def fetch_data(url):
    return await http.get(url)
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "fetch_data"
        assert symbol.metadata.get("is_async") is True

    def test_extract_decorated_function(self):
        """Test extracting decorated function."""
        code = """
@app.route("/")
@login_required
def index():
    return "Home"
"""
        symbols = self.extractor.extract_symbols(code, "test.py")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "index"
        decorators = symbol.metadata.get("decorators", [])
        assert len(decorators) >= 1

    def test_qualified_names(self):
        """Test that qualified names are correctly generated."""
        code = """
class Outer:
    class Inner:
        def method(self):
            pass
"""
        symbols = self.extractor.extract_symbols(code, "module.py")

        # Find the inner method
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) > 0

        method = [m for m in methods if m.name == "method"][0]
        # Qualified name should include class hierarchy
        assert "Inner" in method.qualified_name or "Outer" in method.qualified_name


class TestPythonDependencyExtraction:
    """Test Python dependency extraction."""

    def setup_method(self):
        """Set up extractor for each test."""
        self.extractor = PythonExtractor()

    def test_extract_module_dependencies(self):
        """Test extracting module-level dependencies."""
        code = """
import os
from pathlib import Path
import numpy as np

def process():
    os.path.join("a", "b")
    p = Path(".")
    arr = np.array([1, 2, 3])
"""
        deps = self.extractor.extract_dependencies(code, "test.py")

        # Should find imports
        imports = [d for d in deps if d["type"] == "import"]
        assert len(imports) >= 3

        modules = {imp["target"] for imp in imports}
        assert "os" in modules
        assert "pathlib" in modules or "Path" in modules
        assert "numpy" in modules or "np" in modules
