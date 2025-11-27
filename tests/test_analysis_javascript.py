"""Tests for JavaScript/TypeScript code analysis."""
import pytest
from repo_ctx.analysis.javascript_extractor import JavaScriptExtractor
from repo_ctx.analysis.models import Symbol, SymbolType


class TestJavaScriptSymbolExtraction:
    """Test JavaScript symbol extraction."""

    def setup_method(self):
        """Set up extractor for each test."""
        self.extractor = JavaScriptExtractor()

    def test_extract_function_simple(self):
        """Test extracting a simple function."""
        code = """
function helloWorld() {
    console.log("Hello, World!");
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "helloWorld"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.line_start == 2
        assert symbol.visibility == "public"

    def test_extract_arrow_function(self):
        """Test extracting arrow function."""
        code = """
const greet = (name) => {
    return `Hello ${name}`;
};
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "greet"
        assert symbol.symbol_type == SymbolType.FUNCTION
        assert symbol.metadata.get("is_arrow") is True

    def test_extract_class(self):
        """Test extracting a class definition."""
        code = """
class User {
    constructor(name) {
        this.name = name;
    }

    greet() {
        return `Hello, ${this.name}`;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        # Should find class and its methods
        class_symbols = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        method_symbols = [s for s in symbols if s.symbol_type == SymbolType.METHOD]

        assert len(class_symbols) == 1
        assert class_symbols[0].name == "User"

        assert len(method_symbols) == 2
        method_names = {s.name for s in method_symbols}
        assert "constructor" in method_names
        assert "greet" in method_names

    def test_extract_class_with_inheritance(self):
        """Test extracting class with inheritance."""
        code = """
class Animal {
    speak() {
        return "sound";
    }
}

class Dog extends Animal {
    bark() {
        return "Woof!";
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 2

        dog_class = [s for s in classes if s.name == "Dog"][0]
        assert dog_class.metadata.get("extends") == "Animal"

    def test_extract_private_members(self):
        """Test extracting private class members (ES2022)."""
        code = """
class MyClass {
    #privateField = 42;

    #privateMethod() {
        return this.#privateField;
    }

    publicMethod() {
        return this.#privateMethod();
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        private_methods = [m for m in methods if m.visibility == "private"]
        public_methods = [m for m in methods if m.visibility == "public"]

        assert len(private_methods) >= 1
        assert len(public_methods) >= 1

    def test_extract_imports_es6(self):
        """Test extracting ES6 import statements."""
        code = """
import React from 'react';
import { useState, useEffect } from 'react';
import * as utils from './utils';
"""
        imports = self.extractor.extract_imports(code, "test.js")

        assert len(imports) >= 3
        import_modules = {imp["module"] for imp in imports}
        assert "react" in import_modules
        assert "./utils" in import_modules

    def test_extract_imports_commonjs(self):
        """Test extracting CommonJS require statements."""
        code = """
const fs = require('fs');
const path = require('path');
const { parse } = require('./parser');
"""
        imports = self.extractor.extract_imports(code, "test.js")

        assert len(imports) >= 3
        import_modules = {imp["module"] for imp in imports}
        assert "fs" in import_modules
        assert "path" in import_modules
        assert "./parser" in import_modules

    def test_extract_function_calls(self):
        """Test extracting function calls."""
        code = """
function processData(data) {
    validate(data);
    const result = transform(data);
    save(result);
    return result;
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")
        func = symbols[0]

        calls = self.extractor.extract_calls(code, "test.js", func)

        call_names = {call["name"] for call in calls}
        assert "validate" in call_names
        assert "transform" in call_names
        assert "save" in call_names

    def test_extract_jsdoc(self):
        """Test extracting JSDoc documentation."""
        code = '''
/**
 * A well-documented function.
 *
 * @param {string} name - The name parameter
 * @returns {string} The greeting message
 */
function documentedFunction(name) {
    return `Hello ${name}`;
}
'''
        symbols = self.extractor.extract_symbols(code, "test.js")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.documentation is not None
        assert "well-documented function" in symbol.documentation

    def test_extract_async_function(self):
        """Test extracting async function."""
        code = """
async function fetchData(url) {
    const response = await fetch(url);
    return response.json();
}
"""
        symbols = self.extractor.extract_symbols(code, "test.js")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "fetchData"
        assert symbol.metadata.get("is_async") is True

    def test_qualified_names(self):
        """Test that qualified names are correctly generated."""
        code = """
class Outer {
    method() {
        class Inner {
            innerMethod() {
                console.log("nested");
            }
        }
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "module.js")

        # Find the inner method
        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        inner_methods = [m for m in methods if m.name == "innerMethod"]

        if inner_methods:
            assert "Inner" in inner_methods[0].qualified_name


class TestTypeScriptSymbolExtraction:
    """Test TypeScript-specific symbol extraction."""

    def setup_method(self):
        """Set up extractor for each test."""
        self.extractor = JavaScriptExtractor()

    def test_extract_interface(self):
        """Test extracting TypeScript interface."""
        code = """
interface User {
    name: string;
    age: number;
    greet(): string;
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        interfaces = [s for s in symbols if s.symbol_type == SymbolType.INTERFACE]
        assert len(interfaces) == 1
        assert interfaces[0].name == "User"

    def test_extract_type_alias(self):
        """Test extracting TypeScript type alias."""
        code = """
type Point = {
    x: number;
    y: number;
};

type StringOrNumber = string | number;
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        # Type aliases should be captured
        types = [s for s in symbols if "Point" in s.name or "StringOrNumber" in s.name]
        assert len(types) >= 1

    def test_extract_function_with_types(self):
        """Test extracting function with TypeScript types."""
        code = """
function greet(name: string, age: number): string {
    return `Hello ${name}, you are ${age}`;
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "greet"
        # Signature should include type annotations
        assert "string" in symbol.signature
        assert "number" in symbol.signature

    def test_extract_generic_function(self):
        """Test extracting generic function."""
        code = """
function identity<T>(arg: T): T {
    return arg;
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        assert len(symbols) == 1
        symbol = symbols[0]
        assert symbol.name == "identity"
        # Should capture generic type parameter
        assert "<T>" in symbol.signature or "T" in symbol.signature

    def test_extract_enum(self):
        """Test extracting TypeScript enum."""
        code = """
enum Color {
    Red = 'RED',
    Green = 'GREEN',
    Blue = 'BLUE'
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        enums = [s for s in symbols if s.symbol_type == SymbolType.ENUM]
        assert len(enums) == 1
        assert enums[0].name == "Color"

    def test_extract_class_with_access_modifiers(self):
        """Test extracting class with TypeScript access modifiers."""
        code = """
class Person {
    private name: string;
    protected age: number;
    public email: string;

    private validateEmail(): boolean {
        return true;
    }

    public greet(): string {
        return `Hello`;
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        methods = [s for s in symbols if s.symbol_type == SymbolType.METHOD]
        private_methods = [m for m in methods if m.visibility == "private"]
        public_methods = [m for m in methods if m.visibility == "public"]

        assert len(private_methods) >= 1
        assert len(public_methods) >= 1

    def test_extract_abstract_class(self):
        """Test extracting abstract class."""
        code = """
abstract class Shape {
    abstract getArea(): number;

    describe(): string {
        return "A shape";
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        classes = [s for s in symbols if s.symbol_type == SymbolType.CLASS]
        assert len(classes) == 1
        assert classes[0].metadata.get("is_abstract") is True

    def test_extract_namespace(self):
        """Test extracting TypeScript namespace."""
        code = """
namespace Utils {
    export function log(message: string): void {
        console.log(message);
    }
}
"""
        symbols = self.extractor.extract_symbols(code, "test.ts")

        # Namespace and its exported function
        namespaces = [s for s in symbols if "Utils" in s.qualified_name]
        assert len(namespaces) >= 1


class TestJavaScriptDependencyExtraction:
    """Test JavaScript dependency extraction."""

    def setup_method(self):
        """Set up extractor for each test."""
        self.extractor = JavaScriptExtractor()

    def test_extract_module_dependencies(self):
        """Test extracting module-level dependencies."""
        code = """
import React from 'react';
import { useState } from 'react';
const fs = require('fs');

function Component() {
    const [state, setState] = useState(0);
    fs.readFile('file.txt');
}
"""
        deps = self.extractor.extract_dependencies(code, "test.js")

        # Should find imports
        imports = [d for d in deps if d["type"] == "import"]
        assert len(imports) >= 2

        modules = {imp["target"] for imp in imports}
        assert "react" in modules
        assert "fs" in modules
