"""JavaScript/TypeScript code symbol extractor using Tree-sitter."""
import tree_sitter_javascript as tsjavascript
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType, Dependency


class JavaScriptExtractor:
    """Extract symbols and dependencies from JavaScript/TypeScript code."""

    def __init__(self, language: str = "javascript"):
        """
        Initialize JavaScript/TypeScript extractor with Tree-sitter parser.

        Args:
            language: "javascript" or "typescript"
        """
        self.language_name = language

        if language == "typescript":
            self.language = Language(tstypescript.language_typescript())
        else:
            self.language = Language(tsjavascript.language())

        self.parser = Parser(self.language)
        self.current_file = ""
        self.current_code = ""

    def extract_symbols(self, code: str, file_path: str) -> List[Symbol]:
        """
        Extract all symbols from JavaScript/TypeScript code.

        Args:
            code: Source code
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        # Detect language from file extension and reinitialize if needed
        if file_path.endswith('.ts') or file_path.endswith('.tsx'):
            if self.language_name != "typescript":
                self.__init__("typescript")
        elif self.language_name != "javascript":
            self.__init__("javascript")

        # Set current file and code AFTER initialization
        self.current_file = file_path
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        symbols = []

        # Extract top-level symbols
        symbols.extend(self._extract_functions(root, file_path))
        symbols.extend(self._extract_classes(root, file_path))
        symbols.extend(self._extract_interfaces(root, file_path))
        symbols.extend(self._extract_enums(root, file_path))
        symbols.extend(self._extract_type_aliases(root, file_path))
        symbols.extend(self._extract_namespaces(root, file_path))

        return symbols

    def _extract_functions(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract function definitions."""
        functions = []

        for child in node.children:
            if child.type in ["function_declaration", "function", "method_definition"]:
                func = self._parse_function(child, file_path, parent_class)
                if func:
                    functions.append(func)
            elif child.type == "lexical_declaration":
                # const/let arrow functions
                func = self._parse_arrow_function(child, file_path, parent_class)
                if func:
                    functions.append(func)
            elif child.type == "variable_declaration":
                # var arrow functions
                func = self._parse_arrow_function(child, file_path, parent_class)
                if func:
                    functions.append(func)
            elif child.type in ["class_declaration", "class"]:
                # Recurse into classes to find methods
                functions.extend(self._extract_functions(child, file_path, parent_class))

        return functions

    def _parse_function(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Optional[Symbol]:
        """Parse a function definition node."""
        # Try different field/child types for name
        name_node = node.child_by_field_name("name")
        if not name_node:
            # For methods, might need to look for property_identifier
            for child in node.children:
                if child.type in ["identifier", "property_identifier", "type_identifier"]:
                    name_node = child
                    break

        if not name_node:
            return None

        name = self._get_node_text(name_node)

        # Get type parameters for generics (TypeScript)
        type_params = ""
        type_params_node = node.child_by_field_name("type_parameters")
        if type_params_node:
            type_params = self._get_node_text(type_params_node)

        parameters_node = node.child_by_field_name("parameters")
        return_type_node = node.child_by_field_name("return_type")
        body_node = node.child_by_field_name("body")

        # Build signature
        params = self._get_node_text(parameters_node) if parameters_node else "()"
        return_type = self._get_node_text(return_type_node) if return_type_node else ""

        signature = f"{name}{type_params}{params}"
        if return_type:
            signature += f": {return_type}"

        # Determine visibility
        visibility = self._determine_visibility(node, name)

        # Extract JSDoc
        documentation = self._extract_jsdoc(node)

        # Check if async
        is_async = self._is_async(node)

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
            language=self.language_name,
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_async": is_async,
                "parent_class": parent_class,
                "is_arrow": False
            }
        )

    def _parse_arrow_function(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Optional[Symbol]:
        """Parse arrow function assigned to variable."""
        # Look for variable declarator with arrow function
        for child in node.children:
            if child.type == "variable_declarator":
                name_node = child.child_by_field_name("name")
                value_node = child.child_by_field_name("value")

                if not name_node or not value_node:
                    continue

                if value_node.type == "arrow_function":
                    name = self._get_node_text(name_node)
                    params_node = value_node.child_by_field_name("parameters") or value_node.child_by_field_name("parameter")
                    return_type_node = value_node.child_by_field_name("return_type")

                    params = self._get_node_text(params_node) if params_node else "()"
                    return_type = self._get_node_text(return_type_node) if return_type_node else ""

                    signature = f"{name} = {params} =>"
                    if return_type:
                        signature += f" {return_type}"

                    qualified_name = f"{parent_class}.{name}" if parent_class else name

                    return Symbol(
                        name=name,
                        symbol_type=SymbolType.METHOD if parent_class else SymbolType.FUNCTION,
                        file_path=file_path,
                        line_start=node.start_point[0] + 1,
                        line_end=node.end_point[0] + 1,
                        column_start=node.start_point[1],
                        signature=signature,
                        visibility="public",
                        language=self.language_name,
                        qualified_name=qualified_name,
                        metadata={
                            "is_arrow": True,
                            "is_async": self._is_async(value_node),
                            "parent_class": parent_class
                        }
                    )

        return None

    def _extract_classes(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract class definitions and their methods."""
        classes = []

        for child in node.children:
            if child.type in ["class_declaration", "class", "abstract_class_declaration"]:
                class_symbol, methods = self._parse_class(child, file_path, parent_class)
                if class_symbol:
                    classes.append(class_symbol)
                    classes.extend(methods)

        return classes

    def _parse_class(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Optional[Symbol], List[Symbol]]:
        """Parse a class definition node."""
        # Try to find name node (can be identifier or type_identifier in TypeScript)
        name_node = node.child_by_field_name("name")
        if not name_node:
            # For some nodes, name might be a direct child
            for child in node.children:
                if child.type in ["identifier", "type_identifier", "property_identifier"]:
                    name_node = child
                    break

        if not name_node:
            return None, []

        name = self._get_node_text(name_node)

        # Check for inheritance - look for class_heritage node
        extends = None
        for child in node.children:
            if child.type == "class_heritage":
                # TypeScript: has extends_clause child
                has_extends_clause = False
                for heritage_child in child.children:
                    if heritage_child.type == "extends_clause":
                        has_extends_clause = True
                        # Get the identifier/type after "extends"
                        for extends_child in heritage_child.children:
                            if extends_child.type in ["identifier", "type_identifier", "member_expression"]:
                                extends = self._get_node_text(extends_child)
                                break
                        break

                # JavaScript: class_heritage contains identifier directly
                if not has_extends_clause:
                    for heritage_child in child.children:
                        if heritage_child.type in ["identifier", "type_identifier", "member_expression"]:
                            extends = self._get_node_text(heritage_child)
                            break
                break

        body_node = node.child_by_field_name("body")
        documentation = self._extract_jsdoc(node)

        # Check if abstract (TypeScript) - node type is abstract_class_declaration
        is_abstract = node.type == "abstract_class_declaration"

        # Qualified name
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        metadata = {}
        if extends:
            metadata["extends"] = extends
        if is_abstract:
            metadata["is_abstract"] = True

        class_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.CLASS,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=f"class {name}",
            visibility="public" if not name.startswith("_") else "private",
            language=self.language_name,
            documentation=documentation,
            qualified_name=qualified_name,
            metadata=metadata
        )

        # Extract methods and nested classes from the class body
        all_symbols = []
        if body_node:
            all_symbols.extend(self._extract_functions(body_node, file_path, parent_class=qualified_name))
            all_symbols.extend(self._extract_classes(body_node, file_path, parent_class=qualified_name))

        return class_symbol, all_symbols

    def _extract_interfaces(self, node: Node, file_path: str) -> List[Symbol]:
        """Extract TypeScript interface definitions."""
        interfaces = []

        for child in node.children:
            if child.type == "interface_declaration":
                # TypeScript interfaces use type_identifier for the name
                name_node = None
                for subchild in child.children:
                    if subchild.type in ["type_identifier", "identifier"]:
                        name_node = subchild
                        break

                if not name_node:
                    continue

                name = self._get_node_text(name_node)

                interface_symbol = Symbol(
                    name=name,
                    symbol_type=SymbolType.INTERFACE,
                    file_path=file_path,
                    line_start=child.start_point[0] + 1,
                    line_end=child.end_point[0] + 1,
                    column_start=child.start_point[1],
                    signature=f"interface {name}",
                    visibility="public",
                    language="typescript",
                    qualified_name=name
                )
                interfaces.append(interface_symbol)

        return interfaces

    def _extract_enums(self, node: Node, file_path: str) -> List[Symbol]:
        """Extract TypeScript enum definitions."""
        enums = []

        for child in node.children:
            if child.type == "enum_declaration":
                # Enum uses regular identifier for the name
                name_node = None
                for subchild in child.children:
                    if subchild.type in ["identifier", "type_identifier"]:
                        name_node = subchild
                        break

                if not name_node:
                    continue

                name = self._get_node_text(name_node)

                enum_symbol = Symbol(
                    name=name,
                    symbol_type=SymbolType.ENUM,
                    file_path=file_path,
                    line_start=child.start_point[0] + 1,
                    line_end=child.end_point[0] + 1,
                    column_start=child.start_point[1],
                    signature=f"enum {name}",
                    visibility="public",
                    language="typescript",
                    qualified_name=name
                )
                enums.append(enum_symbol)

        return enums

    def _extract_type_aliases(self, node: Node, file_path: str) -> List[Symbol]:
        """Extract TypeScript type alias definitions."""
        types = []

        for child in node.children:
            if child.type == "type_alias_declaration":
                # Type alias uses type_identifier for the name
                name_node = None
                for subchild in child.children:
                    if subchild.type in ["type_identifier", "identifier"]:
                        name_node = subchild
                        break

                if not name_node:
                    continue

                name = self._get_node_text(name_node)

                # Get the value/type definition
                value = ""
                for subchild in child.children:
                    if subchild.type not in ["type", "type_identifier", "identifier", "=", ";"]:
                        value = self._get_node_text(subchild)
                        break

                type_symbol = Symbol(
                    name=name,
                    symbol_type=SymbolType.VARIABLE,  # Use VARIABLE for type aliases
                    file_path=file_path,
                    line_start=child.start_point[0] + 1,
                    line_end=child.end_point[0] + 1,
                    column_start=child.start_point[1],
                    signature=f"type {name} = {value[:50]}..." if len(value) > 50 else f"type {name} = {value}",
                    visibility="public",
                    language="typescript",
                    qualified_name=name,
                    metadata={"is_type_alias": True}
                )
                types.append(type_symbol)

        return types

    def _extract_namespaces(self, node: Node, file_path: str, parent_namespace: Optional[str] = None) -> List[Symbol]:
        """Extract TypeScript namespace definitions."""
        namespaces = []

        for child in node.children:
            # Namespaces appear as internal_module inside expression_statement
            if child.type == "expression_statement":
                for subchild in child.children:
                    if subchild.type == "internal_module":
                        namespace_symbol, nested = self._parse_namespace(subchild, file_path, parent_namespace)
                        if namespace_symbol:
                            namespaces.append(namespace_symbol)
                            namespaces.extend(nested)
            elif child.type == "internal_module":
                namespace_symbol, nested = self._parse_namespace(child, file_path, parent_namespace)
                if namespace_symbol:
                    namespaces.append(namespace_symbol)
                    namespaces.extend(nested)

        return namespaces

    def _parse_namespace(self, node: Node, file_path: str, parent_namespace: Optional[str] = None) -> tuple[Optional[Symbol], List[Symbol]]:
        """Parse a namespace (internal_module) definition."""
        # Find namespace name
        name_node = None
        for child in node.children:
            if child.type in ["identifier", "type_identifier"]:
                name_node = child
                break

        if not name_node:
            return None, []

        name = self._get_node_text(name_node)
        qualified_name = f"{parent_namespace}.{name}" if parent_namespace else name

        namespace_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.MODULE,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=f"namespace {name}",
            visibility="public",
            language="typescript",
            qualified_name=qualified_name
        )

        # Extract members from namespace body
        all_symbols = []
        body_node = None
        for child in node.children:
            if child.type == "statement_block":
                body_node = child
                break

        if body_node:
            # Extract functions, classes, and nested namespaces
            all_symbols.extend(self._extract_functions(body_node, file_path, parent_class=qualified_name))
            all_symbols.extend(self._extract_classes(body_node, file_path))
            all_symbols.extend(self._extract_namespaces(body_node, file_path, parent_namespace=qualified_name))

        return namespace_symbol, all_symbols

    def _determine_visibility(self, node: Node, name: str) -> str:
        """Determine visibility of a symbol."""
        # Check for TypeScript access modifiers in direct children
        for child in node.children:
            modifier_text = self._get_node_text(child).strip()
            if modifier_text == "private":
                return "private"
            elif modifier_text == "protected":
                return "protected"
            elif modifier_text == "public":
                return "public"

        # Check parent for access modifiers (some nodes wrap the modifiers)
        if node.parent:
            for sibling in node.parent.children:
                modifier_text = self._get_node_text(sibling).strip()
                if modifier_text in ["private", "protected", "public"]:
                    if sibling.start_point[0] == node.start_point[0]:  # Same line
                        return modifier_text

        # Check for JavaScript private fields (#)
        if name.startswith("#"):
            return "private"

        # Check for convention (_prefix)
        if name.startswith("_"):
            return "private"

        return "public"

    def _has_modifier(self, node: Node, modifier: str) -> bool:
        """Check if node has a specific modifier."""
        for child in node.children:
            if child.type == modifier or self._get_node_text(child).strip() == modifier:
                return True
        return False

    def _is_async(self, node: Node) -> bool:
        """Check if function is async."""
        for child in node.children:
            if child.type == "async" or self._get_node_text(child) == "async":
                return True
        return False

    def _extract_jsdoc(self, node: Node) -> Optional[str]:
        """Extract JSDoc comment for a node."""
        # Look for comment node before this node
        if node.prev_sibling and node.prev_sibling.type == "comment":
            comment = self._get_node_text(node.prev_sibling)
            # Clean up JSDoc format
            if comment.startswith("/**") and comment.endswith("*/"):
                # Remove /** */ and clean up
                lines = comment[3:-2].split("\n")
                cleaned = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("*"):
                        line = line[1:].strip()
                    if line and not line.startswith("@"):
                        cleaned.append(line)
                return " ".join(cleaned).strip()

        return None

    def extract_imports(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract import statements."""
        self.current_file = file_path
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        imports = []

        for child in root.children:
            # ES6 imports
            if child.type == "import_statement":
                source_node = child.child_by_field_name("source")
                if source_node:
                    module = self._get_node_text(source_node).strip("'\"")
                    imports.append({
                        "type": "import",
                        "module": module,
                        "symbols": [],
                        "line": child.start_point[0] + 1
                    })

            # CommonJS require
            elif child.type == "variable_declaration" or child.type == "lexical_declaration":
                for declarator in child.children:
                    if declarator.type == "variable_declarator":
                        value_node = declarator.child_by_field_name("value")
                        if value_node and value_node.type == "call_expression":
                            func_node = value_node.child_by_field_name("function")
                            if func_node and self._get_node_text(func_node) == "require":
                                args_node = value_node.child_by_field_name("arguments")
                                if args_node and len(args_node.children) > 0:
                                    for arg in args_node.children:
                                        if arg.type == "string":
                                            module = self._get_node_text(arg).strip("'\"")
                                            imports.append({
                                                "type": "require",
                                                "module": module,
                                                "symbols": [],
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
        if node.type == "call_expression":
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
        """Extract all dependencies (imports, requires, etc.)."""
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
        for child in root.children:
            if child.type in ["function_declaration", "function", "class_declaration", "class", "method_definition"]:
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
