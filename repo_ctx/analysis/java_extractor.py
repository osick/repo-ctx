"""Java code symbol extractor using Tree-sitter."""
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType, Dependency


class JavaExtractor:
    """Extract symbols and dependencies from Java code."""

    def __init__(self):
        """Initialize Java extractor with Tree-sitter parser."""
        self.language = Language(tsjava.language())
        self.parser = Parser(self.language)
        self.current_file = ""
        self.current_code = ""

    def extract_symbols(self, code: str, file_path: str) -> List[Symbol]:
        """
        Extract all symbols from Java code.

        Args:
            code: Java source code
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
        symbols.extend(self._extract_classes(root, file_path))
        symbols.extend(self._extract_interfaces(root, file_path))
        symbols.extend(self._extract_enums(root, file_path))

        return symbols

    def _extract_classes(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract class declarations and their members."""
        classes = []

        for child in node.children:
            if child.type == "class_declaration":
                class_symbol, members = self._parse_class(child, file_path, parent_class)
                classes.append(class_symbol)
                classes.extend(members)
            else:
                # Recurse into other nodes
                classes.extend(self._extract_classes(child, file_path, parent_class))

        return classes

    def _parse_class(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Symbol, List[Symbol]]:
        """Parse a class declaration node."""
        # Get class name
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        # Get modifiers (public, private, abstract, etc.)
        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)
        is_abstract = "abstract" in modifiers
        is_static = "static" in modifiers

        # Get type parameters (generics)
        type_params_node = node.child_by_field_name("type_parameters")
        type_params = self._get_node_text(type_params_node) if type_params_node else ""

        # Get superclass
        superclass_node = node.child_by_field_name("superclass")
        superclass = self._get_node_text(superclass_node) if superclass_node else None

        # Get interfaces
        interfaces_node = node.child_by_field_name("interfaces")
        interfaces = []
        if interfaces_node:
            for child in interfaces_node.children:
                if child.type == "type_identifier":
                    interfaces.append(self._get_node_text(child))

        # Build signature
        signature = f"class {name}"
        if type_params:
            signature += type_params
        if superclass:
            signature += f" extends {superclass}"
        if interfaces:
            signature += f" implements {', '.join(interfaces)}"

        # Extract Javadoc
        documentation = self._extract_javadoc(node)

        # Qualified name
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        class_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.CLASS,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="java",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_abstract": is_abstract,
                "is_static": is_static,
                "modifiers": modifiers,
                "superclass": superclass,
                "interfaces": interfaces
            }
        )

        # Extract methods and inner classes from class body
        body_node = node.child_by_field_name("body")
        members = []
        if body_node:
            members.extend(self._extract_methods(body_node, file_path, qualified_name))
            members.extend(self._extract_classes(body_node, file_path, qualified_name))
            members.extend(self._extract_interfaces(body_node, file_path, qualified_name))

        return class_symbol, members

    def _extract_interfaces(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract interface declarations."""
        interfaces = []

        for child in node.children:
            if child.type == "interface_declaration":
                interface_symbol, methods = self._parse_interface(child, file_path, parent_class)
                interfaces.append(interface_symbol)
                interfaces.extend(methods)
            else:
                interfaces.extend(self._extract_interfaces(child, file_path, parent_class))

        return interfaces

    def _parse_interface(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Symbol, List[Symbol]]:
        """Parse an interface declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        type_params_node = node.child_by_field_name("type_parameters")
        type_params = self._get_node_text(type_params_node) if type_params_node else ""

        # Get extends (interfaces can extend other interfaces)
        extends_node = node.child_by_field_name("extends")
        extends = []
        if extends_node:
            for child in extends_node.children:
                if child.type == "type_identifier":
                    extends.append(self._get_node_text(child))

        signature = f"interface {name}"
        if type_params:
            signature += type_params
        if extends:
            signature += f" extends {', '.join(extends)}"

        documentation = self._extract_javadoc(node)
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        interface_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.INTERFACE,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="java",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "modifiers": modifiers,
                "extends": extends
            }
        )

        # Extract methods from interface body
        body_node = node.child_by_field_name("body")
        methods = []
        if body_node:
            methods = self._extract_methods(body_node, file_path, qualified_name)

        return interface_symbol, methods

    def _extract_enums(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract enum declarations."""
        enums = []

        for child in node.children:
            if child.type == "enum_declaration":
                enum_symbol = self._parse_enum(child, file_path, parent_class)
                enums.append(enum_symbol)
            else:
                enums.extend(self._extract_enums(child, file_path, parent_class))

        return enums

    def _parse_enum(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse an enum declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        signature = f"enum {name}"
        documentation = self._extract_javadoc(node)
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        return Symbol(
            name=name,
            symbol_type=SymbolType.ENUM,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="java",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "modifiers": modifiers
            }
        )

    def _extract_methods(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract method declarations and constructors."""
        methods = []

        for child in node.children:
            if child.type == "method_declaration":
                method = self._parse_method(child, file_path, parent_class)
                methods.append(method)
            elif child.type == "constructor_declaration":
                constructor = self._parse_constructor(child, file_path, parent_class)
                methods.append(constructor)
            elif child.type in ["class_body", "interface_body"]:
                # Recurse into body
                methods.extend(self._extract_methods(child, file_path, parent_class))

        return methods

    def _parse_method(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse a method declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)
        is_static = "static" in modifiers
        is_abstract = "abstract" in modifiers

        # Get return type
        type_node = node.child_by_field_name("type")
        return_type = self._get_node_text(type_node) if type_node else "void"

        # Get type parameters
        type_params_node = node.child_by_field_name("type_parameters")
        type_params = self._get_node_text(type_params_node) if type_params_node else ""

        # Get parameters
        params_node = node.child_by_field_name("parameters")
        params = self._get_node_text(params_node) if params_node else "()"

        # Build signature
        signature = ""
        if type_params:
            signature += f"{type_params} "
        signature += f"{return_type} {name}{params}"

        documentation = self._extract_javadoc(node)
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        return Symbol(
            name=name,
            symbol_type=SymbolType.METHOD,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="java",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_static": is_static,
                "is_abstract": is_abstract,
                "modifiers": modifiers,
                "return_type": return_type,
                "parent_class": parent_class
            }
        )

    def _parse_constructor(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse a constructor declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        # Get parameters
        params_node = node.child_by_field_name("parameters")
        params = self._get_node_text(params_node) if params_node else "()"

        signature = f"{name}{params}"
        documentation = self._extract_javadoc(node)
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        return Symbol(
            name=name,
            symbol_type=SymbolType.METHOD,  # Constructors are treated as methods
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="java",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_constructor": True,
                "modifiers": modifiers,
                "parent_class": parent_class
            }
        )

    def extract_dependencies(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract import dependencies from Java code.

        Args:
            code: Java source code
            file_path: Path to the file

        Returns:
            List of dependency dictionaries
        """
        self.current_file = file_path
        self.current_code = code

        tree = self.parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        dependencies = []

        for child in root.children:
            if child.type == "import_declaration":
                dep = self._parse_import(child, file_path)
                if dep:
                    dependencies.append(dep)

        return dependencies

    def _parse_import(self, node: Node, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse an import declaration."""
        # Check if static import
        is_static = False
        for child in node.children:
            if child.type == "static":
                is_static = True
                break

        # Check if wildcard import
        has_wildcard = False
        for child in node.children:
            if child.type == "asterisk":
                has_wildcard = True
                break

        # Get the import path
        import_path = None
        for child in node.children:
            if child.type in ["scoped_identifier", "identifier"]:
                import_path = self._get_node_text(child)
                if has_wildcard:
                    import_path += ".*"
                break

        if not import_path:
            return None

        return {
            "source": file_path,
            "target": import_path,
            "dependency_type": "static_import" if is_static else "import",
            "line": node.start_point[0] + 1
        }

    def _extract_modifiers(self, node: Node) -> List[str]:
        """Extract modifiers from a declaration node."""
        modifiers = []

        # Find modifiers child
        for child in node.children:
            if child.type == "modifiers":
                for modifier_child in child.children:
                    if modifier_child.type in ["public", "private", "protected", "static",
                                               "final", "abstract", "synchronized", "native",
                                               "strictfp", "transient", "volatile"]:
                        modifiers.append(modifier_child.type)
                break

        return modifiers

    def _determine_visibility(self, modifiers: List[str]) -> str:
        """Determine visibility from modifiers."""
        if "public" in modifiers:
            return "public"
        elif "private" in modifiers:
            return "private"
        elif "protected" in modifiers:
            return "protected"
        else:
            # Package-private (default in Java)
            return "package"

    def _extract_javadoc(self, node: Node) -> Optional[str]:
        """Extract Javadoc comment preceding a node."""
        # Look for comment before the node
        prev_sibling = node.prev_sibling

        while prev_sibling:
            if prev_sibling.type == "block_comment":
                text = self._get_node_text(prev_sibling)
                # Check if it's a Javadoc comment (starts with /**)
                if text.startswith("/**"):
                    # Clean up the comment
                    lines = text.split("\n")
                    cleaned_lines = []
                    for line in lines:
                        line = line.strip()
                        # Remove /** and */
                        line = line.lstrip("/*").rstrip("*/").strip()
                        # Remove leading * from each line
                        if line.startswith("*"):
                            line = line[1:].strip()
                        if line and not line.startswith("@"):
                            cleaned_lines.append(line)
                    return " ".join(cleaned_lines)
            prev_sibling = prev_sibling.prev_sibling

        return None

    def _get_node_text(self, node: Optional[Node]) -> str:
        """Get text content of a node."""
        if node is None:
            return ""

        return self.current_code[node.start_byte:node.end_byte]
