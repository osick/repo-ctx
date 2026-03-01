"""Tests for the generic code extractor supporting multiple languages."""
import pytest
from repo_ctx.analysis.generic_extractor import GenericExtractor, create_generic_extractor
from repo_ctx.analysis.models import SymbolType


class TestGenericExtractorFactory:
    """Tests for the create_generic_extractor factory function."""

    def test_create_c_extractor(self):
        """Test creating C extractor."""
        extractor = create_generic_extractor("c")
        assert extractor is not None
        assert extractor.language_name == "c"

    def test_create_cpp_extractor(self):
        """Test creating C++ extractor."""
        extractor = create_generic_extractor("cpp")
        assert extractor is not None
        assert extractor.language_name == "cpp"

    def test_create_go_extractor(self):
        """Test creating Go extractor."""
        extractor = create_generic_extractor("go")
        assert extractor is not None
        assert extractor.language_name == "go"

    def test_create_rust_extractor(self):
        """Test creating Rust extractor."""
        extractor = create_generic_extractor("rust")
        assert extractor is not None
        assert extractor.language_name == "rust"

    def test_create_ruby_extractor(self):
        """Test creating Ruby extractor."""
        extractor = create_generic_extractor("ruby")
        assert extractor is not None
        assert extractor.language_name == "ruby"

    def test_create_php_extractor(self):
        """Test creating PHP extractor."""
        extractor = create_generic_extractor("php")
        assert extractor is not None
        assert extractor.language_name == "php"

    def test_create_csharp_extractor(self):
        """Test creating C# extractor."""
        extractor = create_generic_extractor("c_sharp")
        assert extractor is not None
        assert extractor.language_name == "c_sharp"

    def test_create_bash_extractor(self):
        """Test creating Bash extractor."""
        extractor = create_generic_extractor("bash")
        assert extractor is not None
        assert extractor.language_name == "bash"

    def test_unsupported_language_raises_error(self):
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError):
            create_generic_extractor("fortran")


class TestCExtractor:
    """Tests for C language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("c")

    def test_extract_function(self, extractor):
        """Test extracting C function."""
        code = """
int add(int a, int b) {
    return a + b;
}
"""
        symbols = extractor.extract_symbols(code, "test.c")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "add" for s in functions)

    def test_extract_struct(self, extractor):
        """Test extracting C struct."""
        code = """
struct Point {
    int x;
    int y;
};
"""
        symbols = extractor.extract_symbols(code, "test.c")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Point" for s in classes)

    def test_extract_include_dependency(self, extractor, tmp_path):
        """Test extracting #include dependency."""
        # Create a header file so local include can be resolved
        header = tmp_path / "myheader.h"
        header.write_text("int foo();")

        main_file = tmp_path / "test.c"
        code = """
#include <stdio.h>
#include "myheader.h"

int main() { return 0; }
"""
        # System includes (<stdio.h>) are skipped, only local includes are extracted
        deps = extractor.extract_dependencies(code, str(main_file))
        assert len(deps) == 1  # Only myheader.h, not stdio.h
        assert str(header) in deps[0].target  # Resolved to actual path


class TestCppExtractor:
    """Tests for C++ language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("cpp")

    def test_extract_class(self, extractor):
        """Test extracting C++ class."""
        code = """
class Calculator {
public:
    int add(int a, int b);
    int subtract(int a, int b);
};
"""
        symbols = extractor.extract_symbols(code, "test.cpp")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Calculator" for s in classes)

    def test_extract_function(self, extractor):
        """Test extracting C++ function."""
        code = """
int main() {
    return 0;
}
"""
        symbols = extractor.extract_symbols(code, "test.cpp")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "main" for s in functions)


class TestGoExtractor:
    """Tests for Go language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("go")

    def test_extract_function(self, extractor):
        """Test extracting Go function."""
        code = """
package main

func Add(a, b int) int {
    return a + b
}
"""
        symbols = extractor.extract_symbols(code, "test.go")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "Add" for s in functions)

    def test_extract_struct_type(self, extractor):
        """Test extracting Go struct type."""
        code = """
package main

type Point struct {
    X int
    Y int
}
"""
        symbols = extractor.extract_symbols(code, "test.go")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Point" for s in classes)

    def test_visibility_detection(self, extractor):
        """Test Go visibility detection (uppercase = public)."""
        code = """
package main

func PublicFunc() {}
func privateFunc() {}
"""
        symbols = extractor.extract_symbols(code, "test.go")
        public_funcs = [s for s in symbols if s.visibility == "public"]
        private_funcs = [s for s in symbols if s.visibility == "private"]
        assert any(s.name == "PublicFunc" for s in public_funcs)
        assert any(s.name == "privateFunc" for s in private_funcs)


class TestRustExtractor:
    """Tests for Rust language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("rust")

    def test_extract_function(self, extractor):
        """Test extracting Rust function."""
        code = """
fn add(a: i32, b: i32) -> i32 {
    a + b
}
"""
        symbols = extractor.extract_symbols(code, "test.rs")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "add" for s in functions)

    def test_extract_struct(self, extractor):
        """Test extracting Rust struct."""
        code = """
struct Point {
    x: i32,
    y: i32,
}
"""
        symbols = extractor.extract_symbols(code, "test.rs")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Point" for s in classes)

    def test_extract_enum(self, extractor):
        """Test extracting Rust enum."""
        code = """
enum Color {
    Red,
    Green,
    Blue,
}
"""
        symbols = extractor.extract_symbols(code, "test.rs")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Color" for s in classes)


class TestRubyExtractor:
    """Tests for Ruby language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("ruby")

    def test_extract_class(self, extractor):
        """Test extracting Ruby class."""
        code = """
class Calculator
  def add(a, b)
    a + b
  end
end
"""
        symbols = extractor.extract_symbols(code, "test.rb")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Calculator" for s in classes)

    def test_extract_method(self, extractor):
        """Test extracting Ruby method."""
        code = """
def greet(name)
  puts "Hello, #{name}!"
end
"""
        symbols = extractor.extract_symbols(code, "test.rb")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "greet" for s in functions)


class TestPhpExtractor:
    """Tests for PHP language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("php")

    def test_extract_class(self, extractor):
        """Test extracting PHP class."""
        code = """<?php
class Calculator {
    public function add($a, $b) {
        return $a + $b;
    }
}
"""
        symbols = extractor.extract_symbols(code, "test.php")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Calculator" for s in classes)

    def test_extract_function(self, extractor):
        """Test extracting PHP function."""
        code = """<?php
function greet($name) {
    echo "Hello, $name!";
}
"""
        symbols = extractor.extract_symbols(code, "test.php")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "greet" for s in functions)


class TestCSharpExtractor:
    """Tests for C# language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("c_sharp")

    def test_extract_class(self, extractor):
        """Test extracting C# class."""
        code = """
public class Calculator {
    public int Add(int a, int b) {
        return a + b;
    }
}
"""
        symbols = extractor.extract_symbols(code, "test.cs")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Calculator" for s in classes)

    def test_extract_interface(self, extractor):
        """Test extracting C# interface."""
        code = """
public interface ICalculator {
    int Add(int a, int b);
}
"""
        symbols = extractor.extract_symbols(code, "test.cs")
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "ICalculator" for s in classes)


class TestBashExtractor:
    """Tests for Bash language extraction."""

    @pytest.fixture
    def extractor(self):
        return create_generic_extractor("bash")

    def test_extract_function(self, extractor):
        """Test extracting Bash function."""
        code = """
#!/bin/bash

greet() {
    echo "Hello, $1!"
}
"""
        symbols = extractor.extract_symbols(code, "test.sh")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert any(s.name == "greet" for s in functions)


class TestCodeAnalyzerIntegration:
    """Tests for CodeAnalyzer integration with generic extractor."""

    def test_analyze_c_file(self):
        """Test analyzing C file via CodeAnalyzer."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer(use_treesitter=True)
        code = "int main() { return 0; }"
        symbols, deps = analyzer.analyze_file(code, "test.c")

        assert len(symbols) >= 1
        assert any(s.name == "main" for s in symbols)

    def test_analyze_cpp_file(self):
        """Test analyzing C++ file via CodeAnalyzer."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer(use_treesitter=True)
        code = "class Foo { void bar() {} };"
        symbols, deps = analyzer.analyze_file(code, "test.cpp")

        # Should find the class
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) >= 1
        assert any(s.name == "Foo" for s in classes)

    def test_analyze_go_file(self):
        """Test analyzing Go file via CodeAnalyzer."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer(use_treesitter=True)
        code = """
package main

func Hello() string {
    return "Hello"
}
"""
        symbols, deps = analyzer.analyze_file(code, "test.go")
        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert any(s.name == "Hello" for s in functions)

    def test_analyze_rust_file(self):
        """Test analyzing Rust file via CodeAnalyzer."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer(use_treesitter=True)
        code = "fn main() { println!(\"Hello\"); }"
        symbols, deps = analyzer.analyze_file(code, "test.rs")

        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert any(s.name == "main" for s in functions)

    def test_supported_extensions_includes_new_languages(self):
        """Test that supported_extensions includes the new languages."""
        from repo_ctx.analysis import CodeAnalyzer

        analyzer = CodeAnalyzer(use_treesitter=True)
        extensions = analyzer.supported_extensions

        # Check new extensions are included
        assert ".c" in extensions
        assert ".cpp" in extensions
        assert ".go" in extensions
        assert ".rs" in extensions
        assert ".rb" in extensions
        assert ".php" in extensions
        assert ".cs" in extensions
        assert ".sh" in extensions
