"""Tests for Kotlin code analysis."""
import pytest
from repo_ctx.analysis.models import SymbolType


class TestKotlinSymbolExtraction:
    """Test Kotlin symbol extraction."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis.kotlin_extractor import KotlinExtractor
        self.extractor = KotlinExtractor()

    def test_extract_simple_class(self):
        """Test extracting a simple class."""
        code = """
class User {
    var name: String = ""

    fun getName(): String {
        return name
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.kt")

        # Should find class and method
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "User"

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) >= 1
        assert any(m.name == "getName" for m in methods)

    def test_extract_data_class(self):
        """Test extracting a data class."""
        code = """
data class User(
    val id: Long,
    val name: String,
    val email: String
)
"""
        symbols = self.extractor.extract_symbols(code, "User.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "User"
        assert classes[0].metadata.get("is_data_class") == True

    def test_extract_interface(self):
        """Test extracting an interface."""
        code = """
interface Repository {
    fun save(entity: Any)
    fun findById(id: String): Any?
}
"""
        symbols = self.extractor.extract_symbols(code, "Repository.kt")

        interfaces = [s for s in symbols if s.symbol_type == SymbolType.INTERFACE]
        assert len(interfaces) == 1
        assert interfaces[0].name == "Repository"

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 2
        method_names = {m.name for m in methods}
        assert "save" in method_names
        assert "findById" in method_names

    def test_extract_object(self):
        """Test extracting an object declaration."""
        code = """
object DatabaseConfig {
    const val DB_NAME = "mydb"

    fun connect() {
        // implementation
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "DatabaseConfig.kt")

        # Object declarations are like classes
        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].name == "DatabaseConfig"
        assert classes[0].metadata.get("is_object") == True

    def test_extract_companion_object(self):
        """Test extracting companion objects."""
        code = """
class Factory {
    companion object {
        fun create(): Factory {
            return Factory()
        }
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "Factory.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        # Should find Factory class and companion object
        assert len(classes) >= 1
        assert any(c.name == "Factory" for c in classes)

    def test_extract_sealed_class(self):
        """Test extracting sealed classes."""
        code = """
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
}
"""
        symbols = self.extractor.extract_symbols(code, "Result.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        # Should find Result and nested classes
        assert len(classes) >= 3

        result_class = [c for c in classes if c.name == "Result"][0]
        assert result_class.metadata.get("is_sealed") == True

    def test_extract_enum_class(self):
        """Test extracting enum classes."""
        code = """
enum class Status {
    ACTIVE,
    INACTIVE,
    PENDING
}
"""
        symbols = self.extractor.extract_symbols(code, "Status.kt")

        enums = [s for s in symbols if s.symbol_type == SymbolType.ENUM]
        assert len(enums) == 1
        assert enums[0].name == "Status"

    def test_extract_function_visibility(self):
        """Test extracting functions with different visibility modifiers."""
        code = """
class MyClass {
    public fun publicFunc() {}
    private fun privateFunc() {}
    protected fun protectedFunc() {}
    internal fun internalFunc() {}
}
"""
        symbols = self.extractor.extract_symbols(code, "MyClass.kt")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) == 4

        visibilities = {m.name: m.visibility for m in methods}
        assert visibilities["publicFunc"] == "public"
        assert visibilities["privateFunc"] == "private"
        assert visibilities["protectedFunc"] == "protected"
        assert visibilities["internalFunc"] == "internal"

    def test_extract_suspend_function(self):
        """Test extracting suspend functions (coroutines)."""
        code = """
class UserService {
    suspend fun fetchUser(id: Long): User {
        // async implementation
        return User()
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "UserService.kt")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        suspend_methods = [m for m in methods if m.metadata.get("is_suspend")]
        assert len(suspend_methods) == 1
        assert suspend_methods[0].name == "fetchUser"

    def test_extract_extension_function(self):
        """Test extracting extension functions."""
        code = """
fun String.isValidEmail(): Boolean {
    return this.contains("@")
}
"""
        symbols = self.extractor.extract_symbols(code, "Extensions.kt")

        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1

        ext_func = functions[0]
        assert ext_func.name == "isValidEmail"
        assert ext_func.metadata.get("is_extension") == True
        assert ext_func.metadata.get("receiver_type") == "String"

    def test_extract_nullable_types(self):
        """Test extracting functions with nullable types."""
        code = """
fun findUser(id: Long): User? {
    return null
}
"""
        symbols = self.extractor.extract_symbols(code, "UserRepository.kt")

        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) == 1
        assert "User?" in functions[0].signature

    def test_extract_inline_function(self):
        """Test extracting inline functions."""
        code = """
inline fun <T> measureTime(block: () -> T): T {
    return block()
}
"""
        symbols = self.extractor.extract_symbols(code, "Utils.kt")

        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 1
        assert functions[0].metadata.get("is_inline") == True

    def test_extract_primary_constructor(self):
        """Test extracting primary constructor."""
        code = """
class User(val name: String, val age: Int)
"""
        symbols = self.extractor.extract_symbols(code, "User.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        # Primary constructor parameters should be in signature
        assert "name" in classes[0].signature
        assert "age" in classes[0].signature

    def test_extract_secondary_constructor(self):
        """Test extracting secondary constructors."""
        code = """
class User {
    constructor(name: String) {
        // init
    }

    constructor(name: String, age: Int) {
        // init
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.kt")

        # Secondary constructors are treated as methods
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        constructors = [m for m in methods if m.metadata.get("is_constructor")]
        assert len(constructors) >= 1

    def test_extract_kdoc(self):
        """Test extracting KDoc comments."""
        code = """
/**
 * Represents a user in the system.
 * @property name The user's name
 */
class User(val name: String) {
    /**
     * Gets the user's display name.
     * @return The formatted name
     */
    fun getDisplayName(): String {
        return name
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "User.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].documentation is not None
        assert "Represents a user" in classes[0].documentation

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        display_methods = [m for m in methods if m.name == "getDisplayName"]
        assert len(display_methods) >= 1
        assert display_methods[0].documentation is not None

    def test_extract_generic_class(self):
        """Test extracting generic classes."""
        code = """
class Container<T> {
    private var value: T? = null

    fun getValue(): T? = value
}
"""
        symbols = self.extractor.extract_symbols(code, "Container.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert "T" in classes[0].signature

    def test_extract_abstract_class(self):
        """Test extracting abstract classes."""
        code = """
abstract class AbstractService {
    abstract fun execute()

    fun common() {
        // common implementation
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "AbstractService.kt")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].metadata.get("is_abstract") == True

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        abstract_methods = [m for m in methods if m.metadata.get("is_abstract")]
        assert len(abstract_methods) >= 1


class TestKotlinDependencyExtraction:
    """Test Kotlin dependency extraction."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis.kotlin_extractor import KotlinExtractor
        self.extractor = KotlinExtractor()

    def test_extract_imports(self):
        """Test extracting import statements."""
        code = """
import java.util.List
import java.util.ArrayList
import com.example.User

class UserService {
}
"""
        deps = self.extractor.extract_dependencies(code, "UserService.kt")

        assert len(deps) >= 3

        targets = {d["target"] for d in deps}
        assert "java.util.List" in targets
        assert "java.util.ArrayList" in targets
        assert "com.example.User" in targets

    def test_extract_wildcard_imports(self):
        """Test extracting wildcard imports."""
        code = """
import java.util.*
import com.example.models.*

class Service {
}
"""
        deps = self.extractor.extract_dependencies(code, "Service.kt")

        assert len(deps) >= 2

        targets = {d["target"] for d in deps}
        assert "java.util.*" in targets
        assert "com.example.models.*" in targets

    def test_extract_aliased_imports(self):
        """Test extracting imports with aliases."""
        code = """
import java.util.ArrayList as JavaList
import com.example.User as AppUser

class Service {
}
"""
        deps = self.extractor.extract_dependencies(code, "Service.kt")

        assert len(deps) >= 2

        # Should track both the original import and alias
        targets = {d["target"] for d in deps}
        assert "java.util.ArrayList" in targets


class TestKotlinIntegration:
    """Integration tests for Kotlin analysis."""

    def setup_method(self):
        """Set up for each test."""
        from repo_ctx.analysis import CodeAnalyzer
        self.analyzer = CodeAnalyzer()

    def test_detect_kotlin_language(self):
        """Test detecting Kotlin language from file extension."""
        assert self.analyzer.detect_language("Test.kt") == "kotlin"
        assert self.analyzer.detect_language("/path/to/File.kt") == "kotlin"
        assert self.analyzer.detect_language("MainActivity.kt") == "kotlin"

    def test_analyze_complete_kotlin_file(self):
        """Test analyzing a complete Kotlin file."""
        code = """
package com.example.service

import java.util.List
import java.util.ArrayList

/**
 * User management service.
 */
class UserService {
    private val users: MutableList<User> = ArrayList()

    /**
     * Adds a user to the service.
     */
    fun addUser(user: User) {
        users.add(user)
    }

    fun getUsers(): List<User> {
        return users
    }

    suspend fun fetchUserAsync(id: Long): User? {
        return null
    }
}
"""
        symbols = self.analyzer.analyze_file(code, "UserService.kt")

        # Should find class and methods
        assert len(symbols) >= 3

        class_symbols = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(class_symbols) == 1
        assert class_symbols[0].name == "UserService"

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        assert len(methods) >= 3

        method_names = {m.name for m in methods}
        assert "addUser" in method_names
        assert "getUsers" in method_names
        assert "fetchUserAsync" in method_names

    def test_kotlin_in_supported_languages(self):
        """Test that Kotlin is in supported languages list."""
        languages = self.analyzer.get_supported_languages()
        assert "kotlin" in languages

    def test_analyze_kotlin_with_extensions(self):
        """Test analyzing Kotlin file with extension functions."""
        code = """
fun String.isEmail(): Boolean {
    return this.contains("@")
}

fun List<Int>.sum(): Int {
    return this.reduce { acc, i -> acc + i }
}
"""
        symbols = self.analyzer.analyze_file(code, "Extensions.kt")

        functions = [s for s in symbols if s.symbol_type == SymbolType.FUNCTION]
        assert len(functions) >= 2

        ext_functions = [f for f in functions if f.metadata.get("is_extension")]
        assert len(ext_functions) == 2
