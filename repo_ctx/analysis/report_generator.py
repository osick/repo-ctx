"""Generate code analysis reports in various formats (markdown, mermaid)."""
import re
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType


def is_test_symbol(symbol: Symbol) -> bool:
    """Check if a symbol is test-related using naming conventions.

    Heuristics:
    - File path contains /test/, /tests/, or starts with test_
    - Class name starts with Test
    - Function/method name starts with test_
    """
    # Check file path
    if symbol.file_path:
        path_lower = symbol.file_path.lower()
        if '/test/' in path_lower or '/tests/' in path_lower:
            return True
        if re.search(r'(^|/)test_[^/]*\.py$', path_lower):
            return True
        if path_lower.endswith('_test.py'):
            return True

    # Check name patterns
    name = symbol.name
    if symbol.symbol_type == SymbolType.CLASS and name.startswith('Test'):
        return True
    if symbol.symbol_type in (SymbolType.FUNCTION, SymbolType.METHOD) and name.startswith('test_'):
        return True

    return False


def is_valid_mermaid_identifier(name: str) -> bool:
    """Check if a name is a valid mermaid identifier.

    Valid identifiers:
    - Start with a letter or underscore
    - Contain only alphanumeric characters and underscores
    - Not empty
    - Reasonable length (avoid garbage strings)
    """
    if not name or len(name) > 100:
        return False
    # Must start with letter or underscore
    if not re.match(r'^[a-zA-Z_]', name):
        return False
    # Must contain only valid identifier characters
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
        return False
    return True


def sanitize_mermaid_identifier(name: str) -> Optional[str]:
    """Sanitize a name for use as a mermaid identifier.

    Returns the sanitized name or None if it cannot be made valid.
    """
    if not name:
        return None
    # Strip whitespace
    name = name.strip()
    if not name:
        return None
    # If already valid, return as-is
    if is_valid_mermaid_identifier(name):
        return name
    # Try to extract a valid identifier from the start
    match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)', name)
    if match:
        return match.group(1)
    return None


class CodeAnalysisReport:
    """Generate comprehensive code analysis reports for documentation output."""

    def __init__(self, symbols: List[Symbol], dependencies: Optional[List[Dict[str, Any]]] = None,
                 exclude_tests: bool = False):
        """Initialize report generator.

        Args:
            symbols: List of Symbol objects from code analysis
            dependencies: Optional list of dependency dictionaries
            exclude_tests: If True, filter out test classes/functions from output
        """
        if exclude_tests:
            self.symbols = [s for s in symbols if not is_test_symbol(s)]
            # Also filter dependencies involving test files
            self.dependencies = [
                d for d in (dependencies or [])
                if not any(t in d.get('source', '').lower() for t in ['/test/', '/tests/', 'test_'])
            ]
        else:
            self.symbols = symbols
            self.dependencies = dependencies or []

    def generate_markdown(self, include_mermaid: bool = True) -> str:
        """Generate a complete markdown report.

        Args:
            include_mermaid: Whether to include mermaid diagrams

        Returns:
            Markdown formatted report string
        """
        sections = []

        # Header
        sections.append("## Code Analysis\n")

        # Classes section
        classes_section = self._generate_classes_section()
        if classes_section:
            sections.append(classes_section)

        # Interfaces section
        interfaces_section = self._generate_interfaces_section()
        if interfaces_section:
            sections.append(interfaces_section)

        # Enums section
        enums_section = self._generate_enums_section()
        if enums_section:
            sections.append(enums_section)

        # Functions section
        functions_section = self._generate_functions_section()
        if functions_section:
            sections.append(functions_section)

        # Class hierarchy (mermaid)
        if include_mermaid:
            hierarchy = self._generate_class_hierarchy_mermaid()
            if hierarchy:
                sections.append(hierarchy)

        # Module/File structure
        modules_section = self._generate_modules_section()
        if modules_section:
            sections.append(modules_section)

        # Dependencies overview
        if self.dependencies:
            sections.append(self._generate_dependencies_section())

            # Call graph mermaid diagram
            if include_mermaid:
                call_graph = self._generate_call_graph_mermaid()
                if call_graph:
                    sections.append(call_graph)

                # Import dependencies mermaid diagram
                import_graph = self._generate_import_graph_mermaid()
                if import_graph:
                    sections.append(import_graph)

        return "\n".join(sections)

    def _generate_classes_section(self) -> Optional[str]:
        """Generate complete classes section with all classes listed."""
        classes = [s for s in self.symbols if s.symbol_type == SymbolType.CLASS]

        if not classes:
            return None

        lines = ["### Classes\n"]

        # Group by file for better organization
        by_file: Dict[str, List[Symbol]] = {}
        for cls in classes:
            file_key = cls.file_path or "unknown"
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(cls)

        for file_path, file_classes in sorted(by_file.items()):
            if len(by_file) > 1:
                lines.append(f"#### {file_path}\n")

            for cls in sorted(file_classes, key=lambda x: x.line_start or 0):
                # Class header with full signature
                visibility_marker = "" if cls.visibility == "public" else f"({cls.visibility}) "
                signature = cls.signature or f"class {cls.name}"
                lines.append(f"**{visibility_marker}`{signature}`**")

                # Location
                if cls.line_start:
                    lines.append(f"  - Location: line {cls.line_start}" + (f"-{cls.line_end}" if cls.line_end else ""))

                # Inheritance
                bases = cls.metadata.get("bases", [])
                if bases:
                    lines.append(f"  - Inherits: {', '.join(bases)}")

                implements = cls.metadata.get("implements", [])
                if implements:
                    lines.append(f"  - Implements: {', '.join(implements)}")

                # Documentation
                if cls.documentation:
                    doc = cls.documentation.strip()
                    # Show full documentation, just clean up whitespace
                    doc_lines = doc.split('\n')
                    if len(doc_lines) == 1:
                        lines.append(f"  - {doc}")
                    else:
                        lines.append(f"  - {doc_lines[0]}")
                        for doc_line in doc_lines[1:]:
                            if doc_line.strip():
                                lines.append(f"    {doc_line.strip()}")

                # Methods of this class
                methods = [s for s in self.symbols
                          if s.symbol_type == SymbolType.METHOD
                          and s.metadata.get("parent_class") == cls.name]

                if methods:
                    public_methods = [m for m in methods if m.visibility == "public"]
                    private_methods = [m for m in methods if m.visibility != "public"]

                    if public_methods:
                        lines.append(f"  - Public methods ({len(public_methods)}):")
                        for method in sorted(public_methods, key=lambda x: x.name):
                            sig = method.signature or method.name
                            # Clean up signature - remove class prefix if present
                            if sig.startswith(f"{cls.name}."):
                                sig = sig[len(cls.name) + 1:]
                            lines.append(f"    - `{sig}`")

                    if private_methods:
                        lines.append(f"  - Private methods ({len(private_methods)}):")
                        for method in sorted(private_methods, key=lambda x: x.name):
                            sig = method.signature or method.name
                            lines.append(f"    - `{sig}`")

                lines.append("")

        return "\n".join(lines)

    def _generate_interfaces_section(self) -> Optional[str]:
        """Generate complete interfaces section."""
        interfaces = [s for s in self.symbols if s.symbol_type == SymbolType.INTERFACE]

        if not interfaces:
            return None

        lines = ["### Interfaces\n"]

        for iface in sorted(interfaces, key=lambda x: x.name):
            visibility_marker = "" if iface.visibility == "public" else f"({iface.visibility}) "
            signature = iface.signature or f"interface {iface.name}"
            lines.append(f"**{visibility_marker}`{signature}`**")

            if iface.file_path:
                lines.append(f"  - File: {iface.file_path}")
            if iface.line_start:
                lines.append(f"  - Location: line {iface.line_start}")

            if iface.documentation:
                lines.append(f"  - {iface.documentation.strip()}")

            # Show interface members if available
            extends = iface.metadata.get("extends", [])
            if extends:
                lines.append(f"  - Extends: {', '.join(extends)}")

            lines.append("")

        return "\n".join(lines)

    def _generate_enums_section(self) -> Optional[str]:
        """Generate complete enums section."""
        enums = [s for s in self.symbols if s.symbol_type == SymbolType.ENUM]

        if not enums:
            return None

        lines = ["### Enumerations\n"]

        for enum in sorted(enums, key=lambda x: x.name):
            signature = enum.signature or f"enum {enum.name}"
            lines.append(f"**`{signature}`**")

            if enum.file_path:
                lines.append(f"  - File: {enum.file_path}")
            if enum.line_start:
                lines.append(f"  - Location: line {enum.line_start}")

            if enum.documentation:
                lines.append(f"  - {enum.documentation.strip()}")

            # Show enum values if available in metadata
            values = enum.metadata.get("values", [])
            if values:
                lines.append(f"  - Values: {', '.join(values)}")

            lines.append("")

        return "\n".join(lines)

    def _generate_functions_section(self) -> Optional[str]:
        """Generate complete functions section (top-level functions only)."""
        functions = [s for s in self.symbols
                    if s.symbol_type == SymbolType.FUNCTION
                    and s.visibility == "public"]

        if not functions:
            return None

        lines = ["### Functions\n"]

        # Group by file
        by_file: Dict[str, List[Symbol]] = {}
        for func in functions:
            file_key = func.file_path or "unknown"
            if file_key not in by_file:
                by_file[file_key] = []
            by_file[file_key].append(func)

        for file_path, file_funcs in sorted(by_file.items()):
            if len(by_file) > 1:
                lines.append(f"#### {file_path}\n")

            for func in sorted(file_funcs, key=lambda x: x.line_start or 0):
                signature = func.signature or func.name
                lines.append(f"**`{signature}`**")

                if func.line_start:
                    lines.append(f"  - Location: line {func.line_start}")

                if func.documentation:
                    doc = func.documentation.strip()
                    doc_lines = doc.split('\n')
                    if len(doc_lines) == 1:
                        lines.append(f"  - {doc}")
                    else:
                        lines.append(f"  - {doc_lines[0]}")
                        for doc_line in doc_lines[1:3]:  # Show first few lines of multiline docs
                            if doc_line.strip():
                                lines.append(f"    {doc_line.strip()}")
                        if len(doc_lines) > 3:
                            lines.append(f"    ...")

                lines.append("")

        return "\n".join(lines)

    def _generate_modules_section(self) -> Optional[str]:
        """Generate modules/files overview section."""
        # Collect unique files
        files: Dict[str, Dict[str, int]] = {}

        for s in self.symbols:
            file_path = s.file_path or "unknown"
            if file_path not in files:
                files[file_path] = {"classes": 0, "functions": 0, "methods": 0, "interfaces": 0, "enums": 0}

            if s.symbol_type == SymbolType.CLASS:
                files[file_path]["classes"] += 1
            elif s.symbol_type == SymbolType.FUNCTION:
                files[file_path]["functions"] += 1
            elif s.symbol_type == SymbolType.METHOD:
                files[file_path]["methods"] += 1
            elif s.symbol_type == SymbolType.INTERFACE:
                files[file_path]["interfaces"] += 1
            elif s.symbol_type == SymbolType.ENUM:
                files[file_path]["enums"] += 1

        if len(files) <= 1:
            return None

        lines = ["### File Structure\n"]
        lines.append("| File | Classes | Functions | Methods | Interfaces | Enums |")
        lines.append("|------|---------|-----------|---------|------------|-------|")

        for file_path, counts in sorted(files.items()):
            lines.append(f"| {file_path} | {counts['classes']} | {counts['functions']} | {counts['methods']} | {counts['interfaces']} | {counts['enums']} |")

        lines.append("")
        return "\n".join(lines)

    def _generate_class_hierarchy_mermaid(self) -> Optional[str]:
        """Generate mermaid class diagram for inheritance hierarchy."""
        # Get all classes and interfaces with valid names
        class_types = {SymbolType.CLASS, SymbolType.INTERFACE, SymbolType.ENUM}
        classes = [s for s in self.symbols
                   if s.symbol_type in class_types
                   and is_valid_mermaid_identifier(s.name)]

        if not classes:
            return None

        # Collect relationships and track all referenced classes
        relationships = set()  # Use set to avoid duplicates
        defined_classes = set()
        external_classes = set()  # Classes referenced but not defined in codebase

        for cls in classes:
            class_name = cls.name
            defined_classes.add(class_name)

            # Get base classes from metadata
            bases = cls.metadata.get("bases", [])
            implements = cls.metadata.get("implements", [])

            for base in bases:
                base_name = sanitize_mermaid_identifier(base.split(".")[-1])
                if base_name:
                    relationships.add((base_name, class_name, "inherits"))
                    if base_name not in defined_classes:
                        external_classes.add(base_name)

            for iface in implements:
                iface_name = sanitize_mermaid_identifier(iface.split(".")[-1])
                if iface_name:
                    relationships.add((iface_name, class_name, "implements"))
                    if iface_name not in defined_classes:
                        external_classes.add(iface_name)

        # Remove external classes that are actually defined
        external_classes -= defined_classes

        # Only generate diagram if there are relationships
        if not relationships:
            return None

        lines = ["### Class Hierarchy Diagram\n"]
        lines.append("```mermaid")
        lines.append("classDiagram")

        # Add external base class definitions first (as simple nodes)
        for ext_class in sorted(external_classes):
            lines.append(f"    class {ext_class}")

        # Add class definitions with type annotations
        for cls in classes:
            class_name = cls.name

            if cls.symbol_type == SymbolType.INTERFACE:
                lines.append(f"    class {class_name} {{")
                lines.append(f"        <<interface>>")
                lines.append(f"    }}")
            elif cls.symbol_type == SymbolType.ENUM:
                lines.append(f"    class {class_name} {{")
                lines.append(f"        <<enumeration>>")
                lines.append(f"    }}")
            else:
                # For regular classes, show key methods if any
                methods = [s for s in self.symbols
                          if s.symbol_type == SymbolType.METHOD
                          and s.metadata.get("parent_class") == class_name
                          and s.visibility == "public"
                          and not s.name.startswith("_")
                          and is_valid_mermaid_identifier(s.name)]

                if methods:
                    lines.append(f"    class {class_name} {{")
                    for method in methods[:5]:
                        lines.append(f"        +{method.name}()")
                    if len(methods) > 5:
                        lines.append(f"        +... {len(methods) - 5} more")
                    lines.append(f"    }}")
                else:
                    # Still define the class even without methods
                    lines.append(f"    class {class_name}")

        # Add relationships (sorted for consistent output)
        for parent, child, rel_type in sorted(relationships):
            if rel_type == "inherits":
                lines.append(f"    {parent} <|-- {child}")
            else:  # implements
                lines.append(f"    {parent} <|.. {child}")

        lines.append("```\n")

        return "\n".join(lines)

    def _generate_dependencies_section(self) -> str:
        """Generate dependencies overview section."""
        lines = ["### Dependencies\n"]

        # Separate imports from calls
        imports = [d for d in self.dependencies if d.get("type") == "import"]
        calls = [d for d in self.dependencies if d.get("type") == "call"]

        if imports:
            # Group by source file
            by_source: Dict[str, List[str]] = {}
            for imp in imports:
                source = imp.get("source", "unknown")
                target = imp.get("target", "unknown")
                if source not in by_source:
                    by_source[source] = []
                if target not in by_source[source]:
                    by_source[source].append(target)

            lines.append("**Import Dependencies:**\n")

            for source, targets in sorted(by_source.items()):
                lines.append(f"**{source}** imports:")
                for target in sorted(targets):
                    lines.append(f"  - `{target}`")
                lines.append("")

        if calls:
            # Show internal function calls
            internal_calls = [c for c in calls if c.get("is_internal", False)]
            if internal_calls:
                lines.append("**Internal Function Calls:**\n")

                # Group by caller
                by_caller: Dict[str, List[str]] = {}
                for call in internal_calls:
                    caller = call.get("caller", "unknown")
                    callee = call.get("callee", "unknown")
                    if caller not in by_caller:
                        by_caller[caller] = []
                    if callee not in by_caller[caller]:
                        by_caller[caller].append(callee)

                for caller, callees in sorted(by_caller.items()):
                    lines.append(f"**{caller}** calls:")
                    for callee in sorted(callees):
                        lines.append(f"  - `{callee}`")
                    lines.append("")

        return "\n".join(lines)

    def _generate_call_graph_mermaid(self) -> Optional[str]:
        """Generate mermaid flowchart for function/method call relationships."""
        calls = [d for d in self.dependencies if d.get("type") == "call"]
        internal_calls = [c for c in calls if c.get("is_internal", False)]

        if not internal_calls:
            return None

        lines = ["### Call Graph\n"]
        lines.append("```mermaid")
        lines.append("flowchart TD")

        # Collect unique nodes and edges
        nodes = set()
        edges = []

        for call in internal_calls:
            caller = call.get("caller", "unknown")
            callee = call.get("callee", "unknown")

            # Sanitize names for mermaid (replace dots with underscores for node IDs)
            caller_id = caller.replace(".", "_").replace("-", "_")
            callee_id = callee.replace(".", "_").replace("-", "_")

            nodes.add((caller_id, caller))
            nodes.add((callee_id, callee))
            edges.append((caller_id, callee_id))

        # Add nodes with labels
        for node_id, label in sorted(nodes):
            # Use quotes for labels with special characters
            lines.append(f"    {node_id}[\"{label}\"]")

        # Add edges
        for caller_id, callee_id in edges:
            lines.append(f"    {caller_id} --> {callee_id}")

        lines.append("```\n")

        return "\n".join(lines)

    def _generate_import_graph_mermaid(self) -> Optional[str]:
        """Generate mermaid flowchart for import dependencies."""
        imports = [d for d in self.dependencies if d.get("type") == "import"]

        if not imports:
            return None

        # Group by source file
        by_source: Dict[str, List[Dict[str, Any]]] = {}
        for imp in imports:
            source = imp.get("source", "unknown")
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(imp)

        lines = ["### Import Dependencies Graph\n"]
        lines.append("```mermaid")
        lines.append("flowchart LR")

        # Subgraph for each source file
        for source, source_imports in sorted(by_source.items()):
            source_id = source.replace(".", "_").replace("/", "_").replace("-", "_")

            # Separate external and internal imports
            external = [i for i in source_imports if i.get("is_external", True)]
            internal = [i for i in source_imports if not i.get("is_external", True)]

            # Source file node
            lines.append(f"    {source_id}[[\"{source}\"]]")

            # External imports (standard library / third party)
            if external:
                for imp in external:
                    target = imp.get("target", "unknown")
                    target_id = f"ext_{target.replace('.', '_').replace('-', '_')}"
                    lines.append(f"    {target_id}((\"{target}\"))")
                    lines.append(f"    {source_id} -.-> {target_id}")

            # Internal imports (local modules)
            if internal:
                for imp in internal:
                    target = imp.get("target", "unknown")
                    target_id = f"int_{target.replace('.', '_').replace('/', '_').replace('-', '_')}"
                    lines.append(f"    {target_id}[\"{target}\"]")
                    lines.append(f"    {source_id} --> {target_id}")

        lines.append("```\n")

        return "\n".join(lines)

    def generate_json(self) -> Dict[str, Any]:
        """Generate JSON report data.

        Returns:
            Dictionary with complete analysis data
        """
        # Organize by type
        classes = []
        for s in self.symbols:
            if s.symbol_type == SymbolType.CLASS:
                methods = [
                    {"name": m.name, "signature": m.signature, "visibility": m.visibility}
                    for m in self.symbols
                    if m.symbol_type == SymbolType.METHOD and m.metadata.get("parent_class") == s.name
                ]
                classes.append({
                    "name": s.name,
                    "signature": s.signature,
                    "file": s.file_path,
                    "line_start": s.line_start,
                    "line_end": s.line_end,
                    "visibility": s.visibility,
                    "documentation": s.documentation,
                    "inherits": s.metadata.get("bases", []),
                    "implements": s.metadata.get("implements", []),
                    "methods": methods
                })

        interfaces = [
            {
                "name": s.name,
                "signature": s.signature,
                "file": s.file_path,
                "line_start": s.line_start,
                "documentation": s.documentation,
                "extends": s.metadata.get("extends", [])
            }
            for s in self.symbols if s.symbol_type == SymbolType.INTERFACE
        ]

        enums = [
            {
                "name": s.name,
                "signature": s.signature,
                "file": s.file_path,
                "line_start": s.line_start,
                "documentation": s.documentation,
                "values": s.metadata.get("values", [])
            }
            for s in self.symbols if s.symbol_type == SymbolType.ENUM
        ]

        functions = [
            {
                "name": s.name,
                "signature": s.signature,
                "file": s.file_path,
                "line_start": s.line_start,
                "visibility": s.visibility,
                "documentation": s.documentation
            }
            for s in self.symbols if s.symbol_type == SymbolType.FUNCTION
        ]

        # Build hierarchy
        hierarchy = []
        for s in self.symbols:
            if s.symbol_type == SymbolType.CLASS:
                bases = s.metadata.get("bases", [])
                implements = s.metadata.get("implements", [])
                if bases or implements:
                    hierarchy.append({
                        "class": s.name,
                        "inherits": bases,
                        "implements": implements,
                        "file": s.file_path
                    })

        return {
            "classes": classes,
            "interfaces": interfaces,
            "enums": enums,
            "functions": functions,
            "hierarchy": hierarchy,
            "dependencies": {
                "imports": [d for d in self.dependencies if d.get("type") == "import"],
                "calls": [d for d in self.dependencies if d.get("type") == "call"]
            }
        }
