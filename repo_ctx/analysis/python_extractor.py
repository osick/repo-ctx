"""Python code symbol extractor using Tree-sitter."""
import tree_sitter_python as tspython
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType, Dependency


class PythonExtractor:
    """Extract symbols and dependencies from Python code."""

    def __init__(self):
        """Initialize Python extractor with Tree-sitter parser."""
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
        self.current_file = ""
        self.current_code = ""

    def extract_symbols(self, code: str, file_path: str) -> List[Symbol]:
        """
        Extract all symbols from Python code.

        Args:
            code: Python source code
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        self.current_file = file_path
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        symbols = []

        # Extract top-level symbols
        symbols.extend(self._extract_functions(root, file_path))
        symbols.extend(self._extract_classes(root, file_path))

        return symbols

    def _extract_functions(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract function definitions."""
        functions = []

        for child in node.children:
            if child.type == "function_definition":
                func = self._parse_function(child, file_path, parent_class)
                functions.append(func)
            elif child.type in ["class_definition", "decorated_definition"]:
                # Recurse into classes to find methods
                functions.extend(self._extract_functions(child, file_path, parent_class))

        return functions

    def _parse_function(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse a function definition node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        parameters_node = node.child_by_field_name("parameters")
        return_type_node = node.child_by_field_name("return_type")
        body_node = node.child_by_field_name("body")

        # Build signature
        params = self._get_node_text(parameters_node) if parameters_node else "()"
        return_type = self._get_node_text(return_type_node) if return_type_node else ""

        signature = f"{name}{params}"
        if return_type:
            signature += f" -> {return_type}"

        # Determine visibility
        visibility = "public"
        if name.startswith("__") and not name.endswith("__"):
            visibility = "private"
        elif name.startswith("_"):
            visibility = "private"

        # Extract docstring
        documentation = self._extract_docstring(body_node) if body_node else None

        # Check for decorators
        decorators = []
        if node.parent and node.parent.type == "decorated_definition":
            decorators = self._extract_decorators(node.parent)

        # Check if async
        is_async = any(child.type == "async" for child in node.children)

        # Determine symbol type (function vs method)
        symbol_type = SymbolType.METHOD if parent_class else SymbolType.FUNCTION

        # Qualified name
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        return Symbol(
            name=name,
            symbol_type=symbol_type,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="python",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_async": is_async,
                "decorators": decorators,
                "parent_class": parent_class
            }
        )

    def _extract_classes(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract class definitions and their methods."""
        classes = []

        for child in node.children:
            if child.type == "class_definition":
                class_symbol, methods = self._parse_class(child, file_path, parent_class)
                classes.append(class_symbol)
                classes.extend(methods)
            elif child.type == "decorated_definition":
                # Check if decorator wraps a class
                classes.extend(self._extract_classes(child, file_path, parent_class))

        return classes

    def _parse_class(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Symbol, List[Symbol]]:
        """Parse a class definition node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        superclasses_node = node.child_by_field_name("superclasses")
        bases = []
        if superclasses_node:
            for child in superclasses_node.children:
                if child.type == "identifier":
                    bases.append(self._get_node_text(child))
                elif child.type == "attribute":
                    bases.append(self._get_node_text(child))

        body_node = node.child_by_field_name("body")
        documentation = self._extract_docstring(body_node) if body_node else None

        # Qualified name
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        class_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.CLASS,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=f"class {name}",
            visibility="public" if not name.startswith("_") else "private",
            language="python",
            documentation=documentation,
            qualified_name=qualified_name,
            metadata={"bases": bases}
        )

        # Extract methods and nested classes from the class body
        all_symbols = []
        if body_node:
            # Extract methods
            all_symbols.extend(self._extract_functions(body_node, file_path, parent_class=qualified_name))
            # Extract nested classes
            all_symbols.extend(self._extract_classes(body_node, file_path, parent_class=qualified_name))

        return class_symbol, all_symbols

    def _extract_docstring(self, body_node: Node) -> Optional[str]:
        """Extract docstring from function/class body."""
        if not body_node:
            return None

        for child in body_node.children:
            if child.type == "expression_statement":
                for subchild in child.children:
                    if subchild.type == "string":
                        # Remove quotes and clean up
                        docstring = self._get_node_text(subchild)
                        # Remove triple quotes
                        docstring = docstring.strip('"""').strip("'''").strip()
                        return docstring

        return None

    def _extract_decorators(self, decorated_node: Node) -> List[str]:
        """Extract decorator names from decorated definition."""
        decorators = []

        for child in decorated_node.children:
            if child.type == "decorator":
                # Get decorator name (skip @ symbol)
                for subchild in child.children:
                    if subchild.type in ["identifier", "attribute", "call"]:
                        decorators.append(self._get_node_text(subchild))

        return decorators

    def extract_imports(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        self.current_file = file_path
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        imports = []

        for child in root.children:
            if child.type == "import_statement":
                # import os, sys
                for subchild in child.children:
                    if subchild.type == "dotted_name":
                        imports.append({
                            "type": "import",
                            "module": self._get_node_text(subchild),
                            "symbols": [],
                            "line": child.start_point[0] + 1
                        })
                    elif subchild.type == "aliased_import":
                        name_node = subchild.child_by_field_name("name")
                        if name_node:
                            imports.append({
                                "type": "import",
                                "module": self._get_node_text(name_node),
                                "symbols": [],
                                "line": child.start_point[0] + 1
                            })

            elif child.type == "import_from_statement":
                # from module import symbol
                module_node = child.child_by_field_name("module_name")
                module = self._get_node_text(module_node) if module_node else None

                # Find imported symbols
                symbols = []
                for subchild in child.children:
                    if subchild.type == "dotted_name" and subchild != module_node:
                        symbols.append(self._get_node_text(subchild))
                    elif subchild.type == "aliased_import":
                        name_node = subchild.child_by_field_name("name")
                        if name_node:
                            symbols.append(self._get_node_text(name_node))

                if module:
                    imports.append({
                        "type": "import_from",
                        "module": module,
                        "symbols": symbols,
                        "line": child.start_point[0] + 1
                    })

        return imports

    def extract_calls(self, code: str, file_path: str, symbol: Symbol) -> List[Dict[str, Any]]:
        """Extract function calls within a symbol."""
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        # Find the function node for this symbol
        func_node = self._find_symbol_node(root, symbol)
        if not func_node:
            return []

        calls = []
        self._extract_calls_from_node(func_node, calls)

        return calls

    def _extract_calls_from_node(self, node: Node, calls: List[Dict[str, Any]]):
        """Recursively extract call expressions from a node."""
        if node.type == "call":
            function_node = node.child_by_field_name("function")
            if function_node:
                name = self._get_node_text(function_node)
                calls.append({
                    "name": name,
                    "line": node.start_point[0] + 1,
                    "type": "call"
                })

        for child in node.children:
            self._extract_calls_from_node(child, calls)

    def extract_dependencies(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract all dependencies (imports, calls, etc.)."""
        imports = self.extract_imports(code, file_path)

        dependencies = []
        for imp in imports:
            dependencies.append({
                "type": "import",
                "source": file_path,
                "target": imp["module"],
                "line": imp.get("line"),
                "is_external": True  # Assume external for now
            })

        return dependencies

    def _find_symbol_node(self, root: Node, symbol: Symbol) -> Optional[Node]:
        """Find the AST node corresponding to a symbol."""
        # Simple approach: find by line number and name
        for child in root.children:
            if child.type in ["function_definition", "class_definition"]:
                if child.start_point[0] + 1 == symbol.line_start:
                    name_node = child.child_by_field_name("name")
                    if name_node and self._get_node_text(name_node) == symbol.name:
                        return child

            # Recurse
            found = self._find_symbol_node(child, symbol)
            if found:
                return found

        return None

    def _get_node_text(self, node: Node) -> str:
        """Get text content of a node."""
        if not node:
            return ""

        start_byte = node.start_byte
        end_byte = node.end_byte
        return self.current_code[start_byte:end_byte]
