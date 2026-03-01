"""
Cincom VisualWorks Smalltalk extractor.

This module provides symbol extraction for Cincom VisualWorks file-out format,
which has several differences from standard Smalltalk:

VisualWorks format characteristics:
- Class definition: `Smalltalk defineClass: #Name superclass: #{Namespace.Class}...`
- Namespace references: `#{Namespace.ClassName}`
- Class instance variables: `classInstanceVariableNames: 'vars'`
- Privacy flags: `private: true/false`
- Imports: `imports: ''`
- Indexed type: `indexedType: #none`
- Class extensions: `ClassName class\n\tinstanceVariableNames: 'vars'`
- Method headers without stamps (simpler format)
"""

import re
from typing import Optional

from repo_ctx.analysis.models import Symbol, SymbolType
from repo_ctx.analysis.smalltalk.base import BaseSmalltalkExtractor
from repo_ctx.analysis.smalltalk.fileout_parser import (
    ClassDefinition,
    MethodDefinition,
)


class CincomSmalltalkExtractor(BaseSmalltalkExtractor):
    """
    Extract symbols from Cincom VisualWorks file-out format.

    Provides enhanced extraction for VisualWorks-specific features:
    - Namespace-qualified class references
    - Class instance variables
    - Privacy modifiers
    - Import declarations
    - Class extensions
    """

    DIALECT = "visualworks"

    # Pattern for namespace reference: #{Namespace.ClassName}
    NAMESPACE_REF_PATTERN = re.compile(r"#\{([^}]+)\}")

    # Pattern for class extension: ClassName class\n\tinstanceVariableNames:
    CLASS_EXTENSION_PATTERN = re.compile(
        r"^(\w+)\s+class\s*\n\s*instanceVariableNames:\s*'([^']*)'",
        re.MULTILINE
    )

    def __init__(self):
        """Initialize the Cincom extractor."""
        super().__init__()
        # Track class extensions for merging
        self._class_extensions: dict[str, dict] = {}

    def extract_symbols(self, code: str, file_path: str) -> list[Symbol]:
        """
        Extract all symbols from VisualWorks code.

        Overrides base to handle class extensions.

        Args:
            code: VisualWorks source code (file-out format)
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        # First, extract class extensions from the code
        self._extract_class_extensions(code)

        # Then call base implementation
        return super().extract_symbols(code, file_path)

    def _extract_class_extensions(self, code: str) -> None:
        """
        Extract class extension blocks from code.

        VisualWorks uses separate blocks like:
        ```
        ClassName class
            instanceVariableNames: 'var1 var2'
        ```

        Args:
            code: Source code
        """
        self._class_extensions = {}

        for match in self.CLASS_EXTENSION_PATTERN.finditer(code):
            class_name = match.group(1)
            vars_str = match.group(2)
            vars_list = [v.strip() for v in vars_str.split() if v.strip()]

            self._class_extensions[class_name] = {
                "class_instance_variables": vars_list,
            }

    def _class_to_symbol(self, class_def: ClassDefinition, file_path: str) -> Symbol:
        """
        Convert a ClassDefinition to a Symbol for VisualWorks.

        Handles VisualWorks-specific features:
        - Namespace-qualified names
        - Class instance variables (including from extensions)
        - Privacy flags
        - Imports

        Args:
            class_def: Parsed class definition
            file_path: Path to the file

        Returns:
            Symbol object representing the class
        """
        # Build qualified name with namespace if available
        qualified_name = class_def.name
        if class_def.namespace:
            qualified_name = f"{class_def.namespace}.{class_def.name}"
        elif class_def.category:
            qualified_name = f"{class_def.category}.{class_def.name}"

        # Merge class instance variables from extensions
        class_inst_vars = list(class_def.class_instance_variables)
        if class_def.name in self._class_extensions:
            ext_vars = self._class_extensions[class_def.name].get(
                "class_instance_variables", []
            )
            for var in ext_vars:
                if var not in class_inst_vars:
                    class_inst_vars.append(var)

        # Determine visibility from privacy flag
        visibility = "private" if class_def.is_private else "public"

        # The namespace field from parser contains the superclass namespace
        # (extracted from #{Namespace.Class} format)
        superclass_namespace = class_def.namespace if class_def.namespace else None

        return Symbol(
            name=class_def.name,
            symbol_type=SymbolType.CLASS,
            file_path=file_path,
            line_start=class_def.line_number,
            qualified_name=qualified_name,
            language="smalltalk",
            documentation=class_def.comment or None,
            visibility=visibility,
            metadata={
                "superclass": class_def.superclass,
                "superclass_namespace": superclass_namespace,
                "instance_variables": class_def.instance_variables,
                "class_variables": class_def.class_variables,
                "class_instance_variables": class_inst_vars,
                "pool_dictionaries": class_def.pool_dictionaries,
                "category": class_def.category,
                "namespace": class_def.namespace,
                "is_private": class_def.is_private,
                "dialect": self.DIALECT,
            },
        )

    def _method_to_symbol(self, method_def: MethodDefinition, file_path: str) -> Symbol:
        """
        Convert a MethodDefinition to a Symbol for VisualWorks.

        Adds VisualWorks-specific metadata.

        Args:
            method_def: Parsed method definition
            file_path: Path to the file

        Returns:
            Symbol object representing the method
        """
        # Get base symbol from parent
        symbol = super()._method_to_symbol(method_def, file_path)

        # Add VisualWorks-specific metadata
        symbol.metadata["dialect"] = self.DIALECT

        # Extract any namespace references from method body
        namespace_refs = self._extract_namespace_references(method_def.source)
        if namespace_refs:
            symbol.metadata["namespace_references"] = namespace_refs

        return symbol

    def _extract_namespace(self, class_ref: str) -> Optional[str]:
        """
        Extract namespace from a class reference.

        For VisualWorks references like "Core.Object", extracts "Core".

        Args:
            class_ref: Class reference string

        Returns:
            Namespace string or None
        """
        if not class_ref:
            return None

        if "." in class_ref:
            parts = class_ref.rsplit(".", 1)
            return parts[0] if len(parts) > 1 else None

        return None

    def _extract_namespace_references(self, code: str) -> list[str]:
        """
        Extract namespace references from code.

        Finds patterns like #{Namespace.ClassName}.

        Args:
            code: Source code

        Returns:
            List of namespace references found
        """
        refs = []
        for match in self.NAMESPACE_REF_PATTERN.finditer(code):
            ref = match.group(1)
            if ref not in refs:
                refs.append(ref)
        return refs

    def extract_dependencies(
        self, code: str, file_path: str, symbols: Optional[list[Symbol]] = None
    ) -> list[dict]:
        """
        Extract dependencies from VisualWorks code.

        Extends base to include namespace-qualified dependencies.

        Args:
            code: VisualWorks source code
            file_path: Path to the file
            symbols: Optional list of symbols

        Returns:
            List of dependency dictionaries
        """
        # Get base dependencies
        dependencies = super().extract_dependencies(code, file_path, symbols)

        # Add namespace references as imports
        chunks = self.fileout_parser.parse(code)
        methods = self.fileout_parser.get_methods(chunks)

        for method_def in methods:
            namespace_refs = self._extract_namespace_references(method_def.source)
            for ref in namespace_refs:
                # Skip if it's a known class reference
                _class_name = ref.split(".")[-1] if "." in ref else ref
                dependencies.append({
                    "from": f"{method_def.class_name}>>{method_def.selector}",
                    "to": ref,
                    "type": "references",
                    "namespace": self._extract_namespace(ref),
                })

        return dependencies

    @classmethod
    def supports_dialect(cls, dialect: str) -> bool:
        """
        Check if this extractor supports the given dialect.

        Args:
            dialect: Dialect identifier

        Returns:
            True if this is VisualWorks/Cincom dialect
        """
        return dialect.lower() in {"visualworks", "cincom", "vw"}
