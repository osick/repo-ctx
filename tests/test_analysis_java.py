"""Tests for Java code analysis."""
import pytest
from repo_ctx.analysis.models import SymbolType


class TestJavaSymbolExtraction:
    """Test Java symbol extraction."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis.java_extractor import JavaExtractor
        self.extractor = JavaExtractor()

    def test_extract_simple_class(self):
        """Test extracting a simple class."""
        code = """
public class User {
    private String name;

    public String getName() {
        return name;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.java")

        # Should find class and method
        assert len(symbols) >= 2

        # Check class
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "User"
        assert classes[0].visibility == "public"

        # Check method
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 1
        assert methods[0].name == "getName"
        assert methods[0].visibility == "public"

    def test_extract_interface(self):
        """Test extracting an interface."""
        code = """
public interface Repository {
    void save(Object entity);
    Object findById(String id);
}
"""
        symbols = self.extractor.extract_symbols(code, "Repository.java")

        # Should find interface and methods
        interfaces = [s for s in symbols if s.symbol_type == SymbolType.INTERFACE]
        assert len(interfaces) == 1
        assert interfaces[0].name == "Repository"

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 2
        method_names = {m.name for m in methods}
        assert "save" in method_names
        assert "findById" in method_names

    def test_extract_enum(self):
        """Test extracting an enum."""
        code = """
public enum Status {
    ACTIVE,
    INACTIVE,
    PENDING
}
"""
        symbols = self.extractor.extract_symbols(code, "Status.java")

        enums = [s for s in symbols if s.symbol_type == SymbolType.ENUM]
        assert len(enums) == 1
        assert enums[0].name == "Status"

    def test_extract_method_visibility(self):
        """Test extracting methods with different visibility modifiers."""
        code = """
public class MyClass {
    public void publicMethod() {}
    private void privateMethod() {}
    protected void protectedMethod() {}
    void packagePrivateMethod() {}
}
"""
        symbols = self.extractor.extract_symbols(code, "MyClass.java")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 4

        visibilities = {m.name: m.visibility for m in methods}
        assert visibilities["publicMethod"] == "public"
        assert visibilities["privateMethod"] == "private"
        assert visibilities["protectedMethod"] == "protected"
        assert visibilities["packagePrivateMethod"] == "package"

    def test_extract_static_method(self):
        """Test extracting static methods."""
        code = """
public class Utils {
    public static String format(String input) {
        return input.trim();
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "Utils.java")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 1
        assert methods[0].name == "format"
        assert methods[0].metadata.get("is_static") == True

    def test_extract_constructor(self):
        """Test extracting constructors."""
        code = """
public class User {
    private String name;

    public User(String name) {
        this.name = name;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.java")

        # Constructor should be extracted as a method
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        constructors = [m for m in methods if m.name == "User"]
        assert len(constructors) == 1
        assert constructors[0].visibility == "public"

    def test_extract_generic_class(self):
        """Test extracting a generic class."""
        code = """
public class Container<T> {
    private T value;

    public T getValue() {
        return value;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "Container.java")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "Container"
        # Signature should include generic type
        assert "T" in classes[0].signature

    def test_extract_abstract_class(self):
        """Test extracting an abstract class."""
        code = """
public abstract class AbstractService {
    public abstract void execute();

    public void common() {
        // common implementation
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "AbstractService.java")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "AbstractService"
        assert classes[0].metadata.get("is_abstract") == True

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 2

        abstract_methods = [m for m in methods if m.metadata.get("is_abstract")]
        assert len(abstract_methods) == 1
        assert abstract_methods[0].name == "execute"

    def test_extract_inner_class(self):
        """Test extracting inner classes."""
        code = """
public class Outer {
    private class Inner {
        void innerMethod() {}
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "Outer.java")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 2

        class_names = {c.name for c in classes}
        assert "Outer" in class_names
        assert "Inner" in class_names

        # Inner class should have qualified name
        inner = [c for c in classes if c.name == "Inner"][0]
        assert "Outer" in (inner.qualified_name or "")

    def test_extract_with_annotations(self):
        """Test extracting elements with annotations."""
        code = """
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue
    private Long id;

    @Override
    public String toString() {
        return "User";
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.java")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) >= 1

    def test_extract_javadoc(self):
        """Test extracting Javadoc comments."""
        code = """
/**
 * Represents a user in the system.
 */
public class User {
    /**
     * Gets the user's name.
     * @return the user's name
     */
    public String getName() {
        return name;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.java")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].documentation is not None
        assert "Represents a user" in classes[0].documentation

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 1
        assert methods[0].documentation is not None
        assert "Gets the user's name" in methods[0].documentation

    def test_extract_method_with_parameters(self):
        """Test extracting method signatures with parameters."""
        code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public double divide(double numerator, double denominator) {
        return numerator / denominator;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "Calculator.java")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 2

        add_method = [m for m in methods if m.name == "add"][0]
        assert "int a" in add_method.signature
        assert "int b" in add_method.signature

        divide_method = [m for m in methods if m.name == "divide"][0]
        assert "double" in divide_method.signature


class TestJavaDependencyExtraction:
    """Test Java dependency extraction."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis.java_extractor import JavaExtractor
        self.extractor = JavaExtractor()

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = """
import java.util.List;
import java.util.ArrayList;
import com.example.User;

public class UserService {
}
"""
        deps = self.extractor.extract_dependencies(code, "UserService.java")

        assert len(deps) >= 3

        targets = {d["target"] for d in deps}
        assert "java.util.List" in targets
        assert "java.util.ArrayList" in targets
        assert "com.example.User" in targets

    def test_extract_wildcard_imports(self):
        """Test extracting wildcard imports."""
        code = """
import java.util.*;
import com.example.models.*;

public class Service {
}
"""
        deps = self.extractor.extract_dependencies(code, "Service.java")

        assert len(deps) >= 2

        targets = {d["target"] for d in deps}
        assert "java.util.*" in targets
        assert "com.example.models.*" in targets

    def test_extract_static_imports(self):
        """Test extracting static imports."""
        code = """
import static java.lang.Math.PI;
import static java.lang.Math.sqrt;

public class Calculator {
}
"""
        deps = self.extractor.extract_dependencies(code, "Calculator.java")

        assert len(deps) >= 2

        # Static imports should be tracked
        static_imports = [d for d in deps if d.get("dependency_type") == "static_import"]
        assert len(static_imports) >= 2


class TestJavaIntegration:
    """Integration tests for Java analysis."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis import CodeAnalyzer
        self.analyzer = CodeAnalyzer()

    def test_detect_java_language(self):
        """Test detecting Java language from file extension."""
        assert self.analyzer.detect_language("Test.java") == "java"
        assert self.analyzer.detect_language("/path/to/File.java") == "java"

    def test_analyze_complete_java_file(self):
        """Test analyzing a complete Java file."""
        code = """
package com.example.service;

import java.util.List;
import java.util.ArrayList;

/**
 * User management service.
 */
public class UserService {
    private List<User> users;

    public UserService() {
        this.users = new ArrayList<>();
    }

    /**
     * Adds a user to the service.
     */
    public void addUser(User user) {
        users.add(user);
    }

    public List<User> getUsers() {
        return users;
    }
}
"""
        symbols = self.analyzer.analyze_file(code, "UserService.java")

        # Should find class, constructor, and methods
        assert len(symbols) >= 3

        class_symbols = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(class_symbols) == 1
        assert class_symbols[0].name == "UserService"

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) >= 3

        method_names = {m.name for m in methods}
        assert "UserService" in method_names  # constructor
        assert "addUser" in method_names
        assert "getUsers" in method_names

    def test_java_in_supported_languages(self):
        """Test that Java is in supported languages list."""
        languages = self.analyzer.get_supported_languages()
        assert "java" in languages
