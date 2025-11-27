"""Kotlin code symbol extractor using Tree-sitter."""
import tree_sitter_kotlin as tskotlin
from tree_sitter import Language, Parser, Node
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType, Dependency


class KotlinExtractor:
    """Extract symbols and dependencies from Kotlin code."""

    def __init__(self):
        """Initialize Kotlin extractor with Tree-sitter parser."""
        self.language = Language(tskotlin.language())
        self.parser = Parser(self.language)
        self.current_file = ""
        self.current_code = ""

    def extract_symbols(self, code: str, file_path: str) -> List[Symbol]:
        """
        Extract all symbols from Kotlin code.

        Args:
            code: Kotlin source code
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
        # Note: interfaces are handled within _extract_classes
        symbols.extend(self._extract_classes(root, file_path))
        symbols.extend(self._extract_enums(root, file_path))
        symbols.extend(self._extract_functions(root, file_path))

        return symbols

    def _extract_classes(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract class declarations and their members."""
        classes = []

        for child in node.children:
            if child.type == "class_declaration":
                # Check if this is an interface or a class by looking at child keywords
                is_interface = any(c.type == "interface" for c in child.children)
                if is_interface:
                    interface_symbol, methods = self._parse_interface(child, file_path, parent_class)
                    classes.append(interface_symbol)
                    classes.extend(methods)
                else:
                    class_symbol, members = self._parse_class(child, file_path, parent_class)
                    classes.append(class_symbol)
                    classes.extend(members)
            elif child.type == "object_declaration":
                obj_symbol, members = self._parse_object(child, file_path, parent_class)
                classes.append(obj_symbol)
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

        # Get modifiers
        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)
        is_data = "data" in modifiers
        is_sealed = "sealed" in modifiers
        is_abstract = "abstract" in modifiers
        is_open = "open" in modifiers
        is_inner = "inner" in modifiers

        # Get type parameters (generics)
        type_params = ""
        for child in node.children:
            if child.type == "type_parameters":
                type_params = self._get_node_text(child)
                break

        # Get primary constructor parameters
        primary_constructor = ""
        for child in node.children:
            if child.type == "primary_constructor":
                primary_constructor = self._get_node_text(child)
                break

        # Get superclass and interfaces
        superclass = None
        interfaces = []
        for child in node.children:
            if child.type == "delegation_specifiers":
                for spec_child in child.children:
                    if spec_child.type == "user_type":
                        # Could be superclass or interface
                        spec_text = self._get_node_text(spec_child)
                        if superclass is None:
                            superclass = spec_text
                        else:
                            interfaces.append(spec_text)

        # Build signature
        signature = ""
        if is_data:
            signature += "data "
        if is_sealed:
            signature += "sealed "
        if is_abstract:
            signature += "abstract "
        if is_open:
            signature += "open "

        signature += f"class {name}"
        if type_params:
            signature += type_params
        if primary_constructor:
            signature += primary_constructor

        # Extract KDoc
        documentation = self._extract_kdoc(node)

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
            language="kotlin",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_data_class": is_data,
                "is_sealed": is_sealed,
                "is_abstract": is_abstract,
                "is_open": is_open,
                "is_inner": is_inner,
                "modifiers": modifiers,
                "superclass": superclass,
                "interfaces": interfaces
            }
        )

        # Extract methods and nested classes from class body
        # Note: tree-sitter-kotlin uses 'class_body' not a 'body' field
        body_node = None
        for child in node.children:
            if child.type == "class_body":
                body_node = child
                break

        members = []
        if body_node:
            members.extend(self._extract_functions(body_node, file_path, qualified_name))
            members.extend(self._extract_classes(body_node, file_path, qualified_name))

        return class_symbol, members

    def _parse_object(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Symbol, List[Symbol]]:
        """Parse an object declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "companion"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)
        is_companion = "companion" in modifiers

        signature = ""
        if is_companion:
            signature += "companion "
        signature += f"object {name}"

        documentation = self._extract_kdoc(node)
        qualified_name = f"{parent_class}.{name}" if parent_class else name

        object_symbol = Symbol(
            name=name,
            symbol_type=SymbolType.CLASS,  # Objects are treated as classes
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="kotlin",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_object": True,
                "is_companion": is_companion,
                "modifiers": modifiers
            }
        )

        # Extract members from object body
        body_node = None
        for child in node.children:
            if child.type == "class_body":
                body_node = child
                break

        members = []
        if body_node:
            members.extend(self._extract_functions(body_node, file_path, qualified_name))

        return object_symbol, members

    def _parse_interface(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> tuple[Symbol, List[Symbol]]:
        """Parse an interface declaration."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        signature = f"interface {name}"
        documentation = self._extract_kdoc(node)
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
            language="kotlin",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "modifiers": modifiers
            }
        )

        # Extract methods from interface body
        body_node = None
        for child in node.children:
            if child.type == "class_body":
                body_node = child
                break

        methods = []
        if body_node:
            methods = self._extract_functions(body_node, file_path, qualified_name)

        return interface_symbol, methods

    def _extract_enums(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract enum class declarations."""
        enums = []

        for child in node.children:
            if child.type == "class_declaration":
                # Check if it's an enum
                for subchild in child.children:
                    if subchild.type == "modifiers":
                        mod_text = self._get_node_text(subchild)
                        if "enum" in mod_text:
                            enum_symbol = self._parse_enum(child, file_path, parent_class)
                            enums.append(enum_symbol)
                            break
            else:
                enums.extend(self._extract_enums(child, file_path, parent_class))

        return enums

    def _parse_enum(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse an enum class declaration."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        signature = f"enum class {name}"
        documentation = self._extract_kdoc(node)
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
            language="kotlin",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "modifiers": modifiers
            }
        )

    def _extract_functions(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> List[Symbol]:
        """Extract function declarations."""
        functions = []

        for child in node.children:
            if child.type == "function_declaration":
                func = self._parse_function(child, file_path, parent_class)
                functions.append(func)
            elif child.type == "secondary_constructor":
                constructor = self._parse_secondary_constructor(child, file_path, parent_class)
                functions.append(constructor)
            # Note: Don't recurse here - the parent methods already handle recursion

        return functions

    def _parse_function(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse a function declaration node."""
        name_node = node.child_by_field_name("name")
        name = self._get_node_text(name_node) if name_node else "unknown"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)
        is_suspend = "suspend" in modifiers
        is_inline = "inline" in modifiers
        is_abstract = "abstract" in modifiers
        is_override = "override" in modifiers
        is_open = "open" in modifiers

        # Check for extension function (receiver type)
        receiver_type = None
        for child in node.children:
            if child.type == "function_value_parameters":
                # Look for receiver before parameters
                prev = child.prev_sibling
                while prev:
                    if prev.type == "user_type":
                        receiver_type = self._get_node_text(prev)
                        break
                    prev = prev.prev_sibling

        # Get type parameters
        type_params_node = node.child_by_field_name("type_parameters")
        type_params = self._get_node_text(type_params_node) if type_params_node else ""

        # Get parameters
        params = ""
        for child in node.children:
            if child.type == "function_value_parameters":
                params = self._get_node_text(child)
                break

        # Get return type
        return_type = ""
        for child in node.children:
            if child.type == "user_type" or child.type == "nullable_type":
                # This might be return type (appears after parameters)
                return_type = self._get_node_text(child)

        # Build signature
        signature = ""
        if is_suspend:
            signature += "suspend "
        if is_inline:
            signature += "inline "
        if type_params:
            signature += f"{type_params} "

        signature += "fun "
        if receiver_type:
            signature += f"{receiver_type}."
        signature += f"{name}{params}"
        if return_type:
            signature += f": {return_type}"

        documentation = self._extract_kdoc(node)

        # Determine symbol type
        symbol_type = SymbolType.METHOD if parent_class else SymbolType.FUNCTION
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
            language="kotlin",
            documentation=documentation,
            qualified_name=qualified_name,
            is_exported=visibility == "public",
            metadata={
                "is_suspend": is_suspend,
                "is_inline": is_inline,
                "is_abstract": is_abstract,
                "is_override": is_override,
                "is_open": is_open,
                "is_extension": receiver_type is not None,
                "receiver_type": receiver_type,
                "modifiers": modifiers,
                "parent_class": parent_class
            }
        )

    def _parse_secondary_constructor(self, node: Node, file_path: str, parent_class: Optional[str] = None) -> Symbol:
        """Parse a secondary constructor."""
        name = parent_class.split(".")[-1] if parent_class else "constructor"

        modifiers = self._extract_modifiers(node)
        visibility = self._determine_visibility(modifiers)

        # Get parameters
        params = ""
        for child in node.children:
            if child.type == "function_value_parameters":
                params = self._get_node_text(child)
                break

        signature = f"constructor{params}"
        documentation = self._extract_kdoc(node)
        qualified_name = f"{parent_class}.constructor" if parent_class else "constructor"

        return Symbol(
            name=name,
            symbol_type=SymbolType.METHOD,
            file_path=file_path,
            line_start=node.start_point[0] + 1,
            line_end=node.end_point[0] + 1,
            column_start=node.start_point[1],
            signature=signature,
            visibility=visibility,
            language="kotlin",
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
        Extract import dependencies from Kotlin code.

        Args:
            code: Kotlin source code
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
            # tree-sitter-kotlin uses "import" node type
            if child.type == "import":
                dep = self._parse_import(child, file_path)
                if dep:
                    dependencies.append(dep)

        return dependencies

    def _parse_import(self, node: Node, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse an import statement."""
        import_path = None
        alias = None
        found_as = False

        for child in node.children:
            if child.type == "qualified_identifier":
                # Full qualified import path (e.g., java.util.List)
                import_path = self._get_node_text(child)
            elif child.type == "as":
                # Mark that we're looking for alias next
                found_as = True
            elif child.type == "identifier":
                if found_as:
                    # This is the alias
                    alias = self._get_node_text(child)
                elif import_path is None:
                    # Simple import (no qualified_identifier)
                    import_path = self._get_node_text(child)

        # Check for wildcard
        import_text = self._get_node_text(node)
        if ".*" in import_text:
            if import_path and not import_path.endswith(".*"):
                import_path += ".*"
            elif not import_path:
                # Try to extract from full text
                import_text = import_text.replace("import", "").strip()
                import_path = import_text

        # Try to extract from full text if needed
        if not import_path:
            import_text = import_text.replace("import", "").strip()
            parts = import_text.split(" as ")
            if len(parts) == 2:
                import_path = parts[0].strip()
                alias = parts[1].strip()
            else:
                import_path = import_text

        if not import_path:
            return None

        return {
            "source": file_path,
            "target": import_path,
            "dependency_type": "import",
            "line": node.start_point[0] + 1,
            "alias": alias
        }

    def _extract_modifiers(self, node: Node) -> List[str]:
        """Extract modifiers from a declaration node."""
        modifiers = []

        for child in node.children:
            if child.type == "modifiers":
                # Get the text and split by whitespace to extract all modifiers
                mod_text = self._get_node_text(child)
                # Split and filter keywords
                keywords = ["public", "private", "protected", "internal",
                           "open", "final", "abstract", "sealed",
                           "data", "inline", "suspend", "override",
                           "companion", "inner", "enum", "interface"]
                for keyword in keywords:
                    if keyword in mod_text:
                        modifiers.append(keyword)
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
        elif "internal" in modifiers:
            return "internal"
        else:
            # Default visibility in Kotlin is public
            return "public"

    def _extract_kdoc(self, node: Node) -> Optional[str]:
        """Extract KDoc comment preceding a node."""
        # Look for comment before the node
        prev_sibling = node.prev_sibling

        while prev_sibling:
            if prev_sibling.type in ["comment", "block_comment", "multiline_comment"]:
                text = self._get_node_text(prev_sibling)
                # Check if it's a KDoc comment (starts with /**)
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
                        # Skip @param, @return, etc. lines for now
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
