"""Generic code symbol extractor for multiple languages using Tree-sitter.

Supports: C, C++, Go, Rust, Ruby, PHP, C#, Bash
Uses language-specific node type mappings to extract symbols uniformly.
"""
import logging
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional, Callable
from .models import Symbol, SymbolType, Dependency

logger = logging.getLogger(__name__)


# Language-specific configurations
LANGUAGE_CONFIGS = {
    "c": {
        "module": "tree_sitter_c",
        "class_types": ["struct_specifier"],
        "function_types": ["function_definition"],
        "variable_types": ["declaration"],
        "import_types": ["preproc_include"],
        "name_field": "declarator",
        "struct_name_field": "name",
    },
    "cpp": {
        "module": "tree_sitter_cpp",
        "class_types": ["class_specifier", "struct_specifier"],
        "function_types": ["function_definition"],
        "method_types": ["function_definition"],
        "variable_types": ["declaration"],
        "import_types": ["preproc_include"],
        "name_field": "declarator",
        "class_name_field": "name",
    },
    "go": {
        "module": "tree_sitter_go",
        "class_types": ["type_declaration"],  # struct types
        "function_types": ["function_declaration"],
        "method_types": ["method_declaration"],
        "variable_types": ["var_declaration", "const_declaration"],
        "import_types": ["import_declaration"],
        "name_field": "name",
    },
    "rust": {
        "module": "tree_sitter_rust",
        "class_types": ["struct_item", "enum_item", "trait_item"],
        "function_types": ["function_item"],
        "method_types": ["function_item"],  # impl methods
        "variable_types": ["let_declaration", "const_item", "static_item"],
        "import_types": ["use_declaration"],
        "name_field": "name",
    },
    "ruby": {
        "module": "tree_sitter_ruby",
        "class_types": ["class", "module"],
        "function_types": ["method", "singleton_method"],
        "variable_types": ["assignment"],
        "import_types": ["call"],  # require/include calls
        "name_field": "name",
    },
    "php": {
        "module": "tree_sitter_php",
        "language_func": "language_php",
        "class_types": ["class_declaration", "interface_declaration", "trait_declaration"],
        "function_types": ["function_definition"],
        "method_types": ["method_declaration"],
        "variable_types": ["property_declaration"],
        "import_types": ["namespace_use_declaration"],
        "name_field": "name",
    },
    "c_sharp": {
        "module": "tree_sitter_c_sharp",
        "class_types": ["class_declaration", "interface_declaration", "struct_declaration"],
        "function_types": ["local_function_statement"],
        "method_types": ["method_declaration"],
        "variable_types": ["field_declaration", "property_declaration"],
        "import_types": ["using_directive"],
        "name_field": "name",
    },
    "bash": {
        "module": "tree_sitter_bash",
        "function_types": ["function_definition"],
        "variable_types": ["variable_assignment"],
        "name_field": "name",
    },
}


class GenericExtractor:
    """Generic symbol extractor for multiple languages using Tree-sitter."""

    def __init__(self, language: str):
        """
        Initialize extractor for a specific language.

        Args:
            language: Language name (c, cpp, go, rust, ruby, php, c_sharp, bash)
        """
        self.language_name = language
        self.config = LANGUAGE_CONFIGS.get(language)
        if not self.config:
            raise ValueError(f"Unsupported language: {language}")

        # Dynamically import the language module
        try:
            module = __import__(self.config["module"], fromlist=["language"])
            # Some packages use language_xxx instead of language
            lang_func_name = self.config.get("language_func", "language")
            lang_func = getattr(module, lang_func_name)
            self.ts_language = Language(lang_func())
            self.parser = Parser(self.ts_language)
        except ImportError as e:
            raise ImportError(
                f"tree-sitter-{language.replace('_', '-')} package not installed: {e}"
            )

        self.current_file = ""
        self.current_code = ""
        self.current_code_bytes = b""

    def extract_symbols(self, code: str, file_path: str) -> List[Symbol]:
        """
        Extract all symbols from source code.

        Args:
            code: Source code content
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        self.current_file = file_path
        self.current_code = code
        self.current_code_bytes = bytes(code, "utf8")

        try:
            tree = self.parser.parse(self.current_code_bytes)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return []

        root = tree.root_node
        symbols = []

        # Extract classes/structs/types
        class_types = self.config.get("class_types", [])
        for class_type in class_types:
            symbols.extend(self._extract_node_type(root, class_type, SymbolType.CLASS))

        # Extract functions
        func_types = self.config.get("function_types", [])
        for func_type in func_types:
            symbols.extend(self._extract_node_type(root, func_type, SymbolType.FUNCTION))

        # Extract methods (if separate from functions)
        method_types = self.config.get("method_types", [])
        for method_type in method_types:
            # Avoid duplicates if method_types overlap with function_types
            if method_type not in func_types:
                symbols.extend(self._extract_node_type(root, method_type, SymbolType.METHOD))

        return symbols

    def _extract_node_type(
        self,
        root: Node,
        node_type: str,
        symbol_type: SymbolType,
        parent_class: Optional[str] = None,
    ) -> List[Symbol]:
        """Extract all nodes of a specific type."""
        symbols = []
        self._walk_tree(root, node_type, symbol_type, symbols, parent_class)
        return symbols

    def _walk_tree(
        self,
        node: Node,
        target_type: str,
        symbol_type: SymbolType,
        symbols: List[Symbol],
        parent_class: Optional[str] = None,
    ):
        """Recursively walk tree and extract matching nodes."""
        if node.type == target_type:
            symbol = self._parse_node(node, symbol_type, parent_class)
            if symbol:
                symbols.append(symbol)
                # If it's a class, extract methods inside
                if symbol_type == SymbolType.CLASS:
                    method_types = self.config.get("method_types", [])
                    for method_type in method_types:
                        for child in node.children:
                            self._walk_tree(
                                child, method_type, SymbolType.METHOD, symbols, symbol.name
                            )

        # Continue walking children
        for child in node.children:
            self._walk_tree(child, target_type, symbol_type, symbols, parent_class)

    def _parse_node(
        self,
        node: Node,
        symbol_type: SymbolType,
        parent_class: Optional[str] = None,
    ) -> Optional[Symbol]:
        """Parse a node into a Symbol."""
        name = self._extract_name(node, symbol_type)
        if not name:
            return None

        # Skip anonymous/unnamed symbols
        if name.startswith("anonymous_") or name == "unknown":
            return None

        # Determine visibility
        visibility = self._extract_visibility(node)

        # Build signature
        signature = self._build_signature(node, name, symbol_type)

        # Extract documentation
        documentation = self._extract_documentation(node)

        # Build qualified name
        if parent_class:
            qualified_name = f"{parent_class}.{name}"
        else:
            qualified_name = name

        return Symbol(
            name=name,
            qualified_name=qualified_name,
            symbol_type=symbol_type,
            file_path=self.current_file,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            signature=signature,
            visibility=visibility,
            language=self.language_name,
            documentation=documentation,
            metadata={"parent_class": parent_class} if parent_class else {},
        )

    def _extract_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name from a node based on language configuration."""
        name_field = self.config.get("name_field", "name")

        # Try language-specific name extraction
        if self.language_name == "c" or self.language_name == "cpp":
            return self._extract_c_family_name(node, symbol_type)
        elif self.language_name == "go":
            return self._extract_go_name(node, symbol_type)
        elif self.language_name == "rust":
            return self._extract_rust_name(node, symbol_type)
        elif self.language_name == "ruby":
            return self._extract_ruby_name(node, symbol_type)
        elif self.language_name == "php":
            return self._extract_php_name(node, symbol_type)
        elif self.language_name == "c_sharp":
            return self._extract_csharp_name(node, symbol_type)
        elif self.language_name == "bash":
            return self._extract_bash_name(node, symbol_type)

        # Generic fallback
        name_node = node.child_by_field_name(name_field)
        if name_node:
            return self._get_node_text(name_node)

        # Try first identifier child
        for child in node.children:
            if child.type == "identifier":
                return self._get_node_text(child)

        return ""

    def _extract_c_family_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for C/C++."""
        if symbol_type == SymbolType.CLASS:
            # struct/class name
            name_node = node.child_by_field_name("name")
            if name_node:
                return self._get_node_text(name_node)
        elif symbol_type == SymbolType.FUNCTION:
            # Function declarator
            declarator = node.child_by_field_name("declarator")
            if declarator:
                return self._extract_declarator_name(declarator)
        return ""

    def _extract_declarator_name(self, declarator: Node) -> str:
        """Recursively extract name from C/C++ declarator."""
        if declarator.type == "identifier":
            return self._get_node_text(declarator)
        elif declarator.type == "function_declarator":
            inner = declarator.child_by_field_name("declarator")
            if inner:
                return self._extract_declarator_name(inner)
        elif declarator.type == "pointer_declarator":
            inner = declarator.child_by_field_name("declarator")
            if inner:
                return self._extract_declarator_name(inner)
        # Try children
        for child in declarator.children:
            if child.type == "identifier":
                return self._get_node_text(child)
            name = self._extract_declarator_name(child)
            if name:
                return name
        return ""

    def _extract_go_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for Go."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_node_text(name_node)

        # For type declarations, look for type_spec
        if node.type == "type_declaration":
            for child in node.children:
                if child.type == "type_spec":
                    type_name = child.child_by_field_name("name")
                    if type_name:
                        return self._get_node_text(type_name)
        return ""

    def _extract_rust_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for Rust."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_node_text(name_node)

        # Try identifier child
        for child in node.children:
            if child.type == "identifier" or child.type == "type_identifier":
                return self._get_node_text(child)
        return ""

    def _extract_ruby_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for Ruby."""
        name_node = node.child_by_field_name("name")
        if name_node:
            text = self._get_node_text(name_node)
            # Handle constant paths (Module::Class)
            if "::" in text:
                return text.split("::")[-1]
            return text

        # For methods, look for identifier
        for child in node.children:
            if child.type == "identifier":
                return self._get_node_text(child)
            if child.type == "constant":
                return self._get_node_text(child)
        return ""

    def _extract_php_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for PHP."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_node_text(name_node)

        # Try identifier/name children
        for child in node.children:
            if child.type in ("name", "identifier"):
                return self._get_node_text(child)
        return ""

    def _extract_csharp_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for C#."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_node_text(name_node)

        # Try identifier
        for child in node.children:
            if child.type == "identifier":
                return self._get_node_text(child)
        return ""

    def _extract_bash_name(self, node: Node, symbol_type: SymbolType) -> str:
        """Extract name for Bash."""
        name_node = node.child_by_field_name("name")
        if name_node:
            return self._get_node_text(name_node)

        # For function definition, look for word
        for child in node.children:
            if child.type == "word":
                return self._get_node_text(child)
        return ""

    def _extract_visibility(self, node: Node) -> str:
        """Extract visibility from node (public, private, protected)."""
        # Check for visibility modifiers in children
        for child in node.children:
            text = self._get_node_text(child).lower()
            if text in ("public", "private", "protected", "internal"):
                return text
            if child.type in ("visibility_modifier", "access_modifier"):
                return self._get_node_text(child).lower()

        # Language-specific defaults
        if self.language_name == "go":
            # Go: uppercase = exported (public)
            name = self._extract_name(node, SymbolType.FUNCTION)
            if name and name[0].isupper():
                return "public"
            return "private"
        elif self.language_name == "ruby":
            # Ruby: methods are public by default
            return "public"
        elif self.language_name in ("c", "cpp"):
            # C/C++: everything is public unless in private section
            return "public"

        return "public"

    def _build_signature(self, node: Node, name: str, symbol_type: SymbolType) -> str:
        """Build a human-readable signature."""
        if symbol_type == SymbolType.CLASS:
            if self.language_name == "rust":
                return f"struct {name}"
            elif self.language_name in ("c", "cpp"):
                return f"struct {name}" if node.type == "struct_specifier" else f"class {name}"
            elif self.language_name == "go":
                return f"type {name} struct"
            elif self.language_name == "ruby":
                return f"class {name}"
            return f"class {name}"

        elif symbol_type in (SymbolType.FUNCTION, SymbolType.METHOD):
            # Try to extract parameters
            params = self._extract_parameters(node)
            return f"{name}({params})"

        return name

    def _extract_parameters(self, node: Node) -> str:
        """Extract function/method parameters."""
        # Look for parameter list
        params_node = node.child_by_field_name("parameters")
        if params_node:
            return self._get_node_text(params_node).strip("()")

        # Try finding parameter_list child
        for child in node.children:
            if child.type in ("parameter_list", "formal_parameters", "parameters"):
                return self._get_node_text(child).strip("()")

        return ""

    def _extract_documentation(self, node: Node) -> Optional[str]:
        """Extract documentation comment preceding the node."""
        # Look for preceding comment nodes
        if node.prev_sibling:
            sibling = node.prev_sibling
            if sibling.type in ("comment", "line_comment", "block_comment"):
                text = self._get_node_text(sibling)
                # Clean up comment markers
                text = text.strip("/*").strip("*/").strip("//").strip("#").strip()
                return text if text else None

        return None

    def _get_node_text(self, node: Node) -> str:
        """Get text content of a node."""
        if node is None:
            return ""
        return self.current_code_bytes[node.start_byte:node.end_byte].decode("utf8")

    def _resolve_local_include(self, include_path: str) -> str:
        """Resolve a local include to an actual file path.

        For C/C++ #include "file.h", tries to find the actual file:
        1. Relative to the current file's directory
        2. Relative to parent directories (project root detection)
        3. In common include directories

        Args:
            include_path: The include path (e.g., "myheader.h" or "utils/helper.h")

        Returns:
            Resolved file path if found, otherwise the original include path.
        """
        from pathlib import Path

        if not self.current_file:
            return include_path

        current_path = Path(self.current_file)
        current_dir = current_path.parent

        # Try to resolve relative to current file's directory
        candidate = current_dir / include_path
        if candidate.exists():
            try:
                return str(candidate.resolve())
            except Exception:
                return str(candidate)

        # Try parent directories (for project-root-relative includes like "debugging/assert.h")
        # Walk up to 10 levels to find the file
        search_dir = current_dir
        for _ in range(10):
            parent = search_dir.parent
            if parent == search_dir:  # Reached filesystem root
                break
            candidate = parent / include_path
            if candidate.exists():
                try:
                    return str(candidate.resolve())
                except Exception:
                    return str(candidate)
            search_dir = parent

        # Try common include directories relative to current file
        for include_dir in ["include", "src", "..", "../include", "../src"]:
            candidate = current_dir / include_dir / include_path
            if candidate.exists():
                try:
                    return str(candidate.resolve())
                except Exception:
                    return str(candidate)

        # Could not resolve - return the original include path
        # This will still create a dependency edge, just won't link to a file
        return include_path

    def extract_dependencies(
        self, code: str, file_path: str, symbols: Optional[List[Symbol]] = None
    ) -> List[Dependency]:
        """
        Extract dependencies (imports/includes) from source code.

        Args:
            code: Source code content
            file_path: Path to the file
            symbols: Optional list of symbols (not used currently)

        Returns:
            List of Dependency objects
        """
        self.current_file = file_path
        self.current_code = code
        self.current_code_bytes = bytes(code, "utf8")

        try:
            tree = self.parser.parse(self.current_code_bytes)
        except Exception as e:
            logger.warning(f"Failed to parse {file_path} for dependencies: {e}")
            return []

        root = tree.root_node
        dependencies = []

        import_types = self.config.get("import_types", [])
        for import_type in import_types:
            deps = self._extract_imports(root, import_type)
            dependencies.extend(deps)

        return dependencies

    def _extract_imports(self, root: Node, import_type: str) -> List[Dependency]:
        """Extract import/include statements."""
        dependencies = []

        def walk(node: Node):
            if node.type == import_type:
                dep = self._parse_import(node)
                if dep:
                    dependencies.append(dep)
            for child in node.children:
                walk(child)

        walk(root)
        return dependencies

    def _parse_import(self, node: Node) -> Optional[Dependency]:
        """Parse an import/include node into a Dependency."""
        target = ""
        is_system_include = False

        if self.language_name in ("c", "cpp"):
            # #include <file> or #include "file"
            for child in node.children:
                if child.type == "system_lib_string":
                    # System include like <iostream> - skip for dependency graph
                    is_system_include = True
                    target = self._get_node_text(child).strip('<>')
                    break
                elif child.type == "string_literal":
                    # Local include like "myheader.h" - resolve to file path
                    target = self._get_node_text(child).strip('"')
                    # Try to resolve to actual file path
                    target = self._resolve_local_include(target)
                    break

            # Skip system includes for dependency graph (they're external)
            if is_system_include:
                return None
        elif self.language_name == "go":
            # import "package" or import ( "package" )
            path_node = node.child_by_field_name("path")
            if path_node:
                target = self._get_node_text(path_node).strip('"')
        elif self.language_name == "rust":
            # use crate::module
            for child in node.children:
                if child.type == "use_clause":
                    target = self._get_node_text(child)
                    break
        elif self.language_name == "ruby":
            # require 'file' or require_relative 'file'
            for child in node.children:
                if child.type == "string":
                    target = self._get_node_text(child).strip("'\"")
                    break
        elif self.language_name == "php":
            # use Namespace\Class
            for child in node.children:
                if child.type == "namespace_use_clause":
                    target = self._get_node_text(child)
                    break
        elif self.language_name == "c_sharp":
            # using Namespace
            for child in node.children:
                if child.type == "qualified_name" or child.type == "identifier":
                    target = self._get_node_text(child)
                    break

        if target:
            return Dependency(
                source=self.current_file,
                target=target,
                dependency_type="import",
                file_path=self.current_file,
            )
        return None


# Factory function for creating extractors
def create_generic_extractor(language: str) -> GenericExtractor:
    """
    Create a GenericExtractor for the specified language.

    Args:
        language: Language name (c, cpp, go, rust, ruby, php, c_sharp, bash)

    Returns:
        GenericExtractor instance
    """
    return GenericExtractor(language)
