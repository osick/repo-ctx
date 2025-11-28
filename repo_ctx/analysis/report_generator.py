"""Generate code analysis reports in various formats (markdown, mermaid)."""
from typing import List, Dict, Any, Optional
from .models import Symbol, SymbolType


class CodeAnalysisReport:
    """Generate code analysis reports for documentation output."""

    def __init__(self, symbols: List[Symbol], dependencies: Optional[List[Dict[str, Any]]] = None):
        """Initialize report generator.

        Args:
            symbols: List of Symbol objects from code analysis
            dependencies: Optional list of dependency dictionaries
        """
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
        sections.append("## Code Analysis Summary\n")

        # Symbol statistics
        sections.append(self._generate_statistics_section())

        # Class hierarchy (mermaid)
        if include_mermaid:
            hierarchy = self._generate_class_hierarchy_mermaid()
            if hierarchy:
                sections.append(hierarchy)

        # Top-level API
        sections.append(self._generate_api_section())

        # Dependencies overview
        if self.dependencies:
            sections.append(self._generate_dependencies_section())

        return "\n".join(sections)

    def _generate_statistics_section(self) -> str:
        """Generate symbol statistics section."""
        lines = ["### Symbol Statistics\n"]

        # Count by type
        by_type: Dict[str, int] = {}
        by_language: Dict[str, int] = {}
        by_visibility: Dict[str, int] = {}

        for s in self.symbols:
            # By type
            type_key = s.symbol_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # By language
            lang_key = s.language or "unknown"
            by_language[lang_key] = by_language.get(lang_key, 0) + 1

            # By visibility
            vis_key = s.visibility or "public"
            by_visibility[vis_key] = by_visibility.get(vis_key, 0) + 1

        lines.append(f"**Total symbols:** {len(self.symbols)}\n")

        # By type table
        lines.append("| Type | Count |")
        lines.append("|------|-------|")
        for stype, count in sorted(by_type.items(), key=lambda x: -x[1]):
            lines.append(f"| {stype} | {count} |")
        lines.append("")

        # By language (if multiple)
        if len(by_language) > 1:
            lines.append("**By language:**")
            for lang, count in sorted(by_language.items(), key=lambda x: -x[1]):
                lines.append(f"- {lang}: {count}")
            lines.append("")

        # Visibility summary
        public_count = by_visibility.get("public", 0)
        private_count = by_visibility.get("private", 0) + by_visibility.get("protected", 0)
        if private_count > 0:
            lines.append(f"**Visibility:** {public_count} public, {private_count} private/protected\n")

        return "\n".join(lines)

    def _generate_class_hierarchy_mermaid(self) -> Optional[str]:
        """Generate mermaid class diagram for inheritance hierarchy."""
        # Get all classes and interfaces
        class_types = {SymbolType.CLASS, SymbolType.INTERFACE, SymbolType.ENUM}
        classes = [s for s in self.symbols if s.symbol_type in class_types]

        if not classes:
            return None

        lines = ["### Class Hierarchy\n"]
        lines.append("```mermaid")
        lines.append("classDiagram")

        # Track classes we've defined
        defined_classes = set()
        relationships = []

        for cls in classes:
            class_name = cls.name
            defined_classes.add(class_name)

            # Get base classes from metadata
            bases = cls.metadata.get("bases", [])
            implements = cls.metadata.get("implements", [])

            # Add class definition with type annotation
            if cls.symbol_type == SymbolType.INTERFACE:
                lines.append(f"    class {class_name} {{")
                lines.append(f"        <<interface>>")
                lines.append(f"    }}")
            elif cls.symbol_type == SymbolType.ENUM:
                lines.append(f"    class {class_name} {{")
                lines.append(f"        <<enumeration>>")
                lines.append(f"    }}")
            else:
                # Add methods for the class
                methods = [s for s in self.symbols
                          if s.symbol_type == SymbolType.METHOD
                          and s.metadata.get("parent_class") == class_name
                          and s.visibility == "public"]

                if methods:
                    lines.append(f"    class {class_name} {{")
                    for method in methods[:5]:  # Limit to 5 methods
                        lines.append(f"        +{method.name}()")
                    if len(methods) > 5:
                        lines.append(f"        +... {len(methods) - 5} more")
                    lines.append(f"    }}")

            # Add inheritance relationships
            for base in bases:
                # Clean base name (remove module prefix if present)
                base_name = base.split(".")[-1]
                relationships.append(f"    {base_name} <|-- {class_name}")

            # Add implementation relationships
            for iface in implements:
                iface_name = iface.split(".")[-1]
                relationships.append(f"    {iface_name} <|.. {class_name}")

        # Add relationships
        for rel in relationships:
            lines.append(rel)

        lines.append("```\n")

        # Only return if we have meaningful content
        if len(relationships) == 0 and len(classes) < 2:
            return None

        return "\n".join(lines)

    def _generate_api_section(self) -> str:
        """Generate top-level API section."""
        lines = ["### Public API\n"]

        # Get public classes
        public_classes = [s for s in self.symbols
                        if s.symbol_type == SymbolType.CLASS
                        and s.visibility == "public"]

        if public_classes:
            lines.append("**Classes:**\n")
            for cls in sorted(public_classes, key=lambda x: x.name)[:15]:
                signature = cls.signature or f"class {cls.name}"
                doc_preview = ""
                if cls.documentation:
                    doc_preview = f" - {cls.documentation[:60]}..." if len(cls.documentation) > 60 else f" - {cls.documentation}"
                lines.append(f"- `{signature}`{doc_preview}")
            if len(public_classes) > 15:
                lines.append(f"- ... and {len(public_classes) - 15} more classes")
            lines.append("")

        # Get public functions (not methods)
        public_functions = [s for s in self.symbols
                          if s.symbol_type == SymbolType.FUNCTION
                          and s.visibility == "public"]

        if public_functions:
            lines.append("**Functions:**\n")
            for func in sorted(public_functions, key=lambda x: x.name)[:15]:
                signature = func.signature or func.name
                # Truncate long signatures
                if len(signature) > 80:
                    signature = signature[:77] + "..."
                lines.append(f"- `{signature}`")
            if len(public_functions) > 15:
                lines.append(f"- ... and {len(public_functions) - 15} more functions")
            lines.append("")

        # Get interfaces
        interfaces = [s for s in self.symbols
                     if s.symbol_type == SymbolType.INTERFACE]

        if interfaces:
            lines.append("**Interfaces:**\n")
            for iface in sorted(interfaces, key=lambda x: x.name)[:10]:
                lines.append(f"- `{iface.name}`")
            if len(interfaces) > 10:
                lines.append(f"- ... and {len(interfaces) - 10} more interfaces")
            lines.append("")

        # Get enums
        enums = [s for s in self.symbols
                if s.symbol_type == SymbolType.ENUM]

        if enums:
            lines.append("**Enums:**\n")
            for enum in sorted(enums, key=lambda x: x.name)[:10]:
                lines.append(f"- `{enum.name}`")
            if len(enums) > 10:
                lines.append(f"- ... and {len(enums) - 10} more enums")
            lines.append("")

        return "\n".join(lines)

    def _generate_dependencies_section(self) -> str:
        """Generate dependencies overview section."""
        lines = ["### Dependencies\n"]

        # Separate imports from calls
        imports = [d for d in self.dependencies if d.get("type") == "import"]
        calls = [d for d in self.dependencies if d.get("type") == "call"]

        if imports:
            # Group by target module
            import_targets: Dict[str, int] = {}
            for imp in imports:
                target = imp.get("target", "unknown")
                import_targets[target] = import_targets.get(target, 0) + 1

            # Separate internal vs external
            external = [(t, c) for t, c in import_targets.items()
                       if imp.get("is_external", True)]
            internal = [(t, c) for t, c in import_targets.items()
                       if not imp.get("is_external", True)]

            lines.append("**External imports:**\n")
            for target, count in sorted(external, key=lambda x: -x[1])[:15]:
                lines.append(f"- `{target}`" + (f" ({count} files)" if count > 1 else ""))
            if len(external) > 15:
                lines.append(f"- ... and {len(external) - 15} more")
            lines.append("")

        if calls:
            # Count internal calls
            internal_calls = [c for c in calls if c.get("is_internal", False)]
            if internal_calls:
                lines.append(f"**Internal function calls:** {len(internal_calls)} calls detected\n")

        return "\n".join(lines)

    def generate_json(self) -> Dict[str, Any]:
        """Generate JSON report data.

        Returns:
            Dictionary with analysis data
        """
        # Count by type
        by_type: Dict[str, int] = {}
        by_language: Dict[str, int] = {}

        for s in self.symbols:
            type_key = s.symbol_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            lang_key = s.language or "unknown"
            by_language[lang_key] = by_language.get(lang_key, 0) + 1

        # Get public API
        public_classes = [
            {"name": s.name, "signature": s.signature, "file": s.file_path}
            for s in self.symbols
            if s.symbol_type == SymbolType.CLASS and s.visibility == "public"
        ]

        public_functions = [
            {"name": s.name, "signature": s.signature, "file": s.file_path}
            for s in self.symbols
            if s.symbol_type == SymbolType.FUNCTION and s.visibility == "public"
        ]

        # Get class hierarchy
        hierarchy = []
        for s in self.symbols:
            if s.symbol_type == SymbolType.CLASS:
                bases = s.metadata.get("bases", [])
                if bases:
                    hierarchy.append({
                        "class": s.name,
                        "inherits": bases,
                        "file": s.file_path
                    })

        return {
            "statistics": {
                "total_symbols": len(self.symbols),
                "by_type": by_type,
                "by_language": by_language
            },
            "public_api": {
                "classes": public_classes,
                "functions": public_functions
            },
            "class_hierarchy": hierarchy,
            "dependencies": {
                "imports": [d for d in self.dependencies if d.get("type") == "import"],
                "calls_count": len([d for d in self.dependencies if d.get("type") == "call"])
            }
        }
