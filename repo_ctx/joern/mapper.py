"""
Mapper for converting CPG data to repo-ctx Symbol objects.

This module maps Joern's CPG nodes to the repo-ctx Symbol model,
enabling integration with the existing analysis infrastructure.
"""

import logging
import os
import re
from typing import Any

from repo_ctx.analysis.models import Symbol, SymbolType, Dependency
from repo_ctx.joern.parser import (
    CPGMethod,
    CPGType,
    CPGMember,
    CPGCall,
    CPGParseResult,
)

logger = logging.getLogger(__name__)


class CPGMapper:
    """
    Mapper for converting CPG data structures to repo-ctx symbols.

    Maps:
    - CPGMethod → Symbol (FUNCTION or METHOD)
    - CPGType → Symbol (CLASS or INTERFACE)
    - CPGMember → Symbol (VARIABLE)
    - CPGCall → Dependency
    """

    # Language detection from file extension
    EXTENSION_TO_LANGUAGE = {
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        ".java": "java",
        ".js": "javascript",
        ".jsx": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".py": "python",
        ".kt": "kotlin",
        ".kts": "kotlin",
        ".go": "go",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".cs": "csharp",
    }

    # Visibility detection patterns by language
    VISIBILITY_PATTERNS = {
        "python": {
            "private": lambda name: name.startswith("__") and not name.endswith("__"),
            "protected": lambda name: name.startswith("_") and not name.startswith("__"),
            "public": lambda name: not name.startswith("_"),
        },
        "javascript": {
            "private": lambda name: name.startswith("#"),
            "public": lambda name: not name.startswith("#"),
        },
        "ruby": {
            "private": lambda name: False,  # Determined by method, not name
            "public": lambda name: True,
        },
        "default": {
            "private": lambda name: name.startswith("_"),
            "public": lambda name: not name.startswith("_"),
        },
    }

    # Pattern to detect temp files created by Joern frontends (e.g., jssrc2cpg)
    # Matches: tmp<random>.js, /tmp/tmp<random>.js, etc.
    TEMP_FILE_PATTERN = re.compile(r'^(.*[/\\])?tmp[a-z0-9_]+\.(js|ts|jsx|tsx|mjs)$', re.IGNORECASE)

    # Internal artifact names that should be filtered out
    # These are Joern CPG internal constructs, not real code symbols
    INTERNAL_ARTIFACT_NAMES = {
        "ANY",           # Joern's root type in type hierarchy
        "<module>",      # Python module namespace
        "<init>",        # Constructor placeholder
        "<clinit>",      # Static initializer
        "<global>",      # Global scope
        "<lambda>",      # Anonymous function
        "<listcomp>",    # List comprehension
        "<dictcomp>",    # Dict comprehension
        "<setcomp>",     # Set comprehension
        "<genexpr>",     # Generator expression
    }

    def __init__(self):
        """Initialize the mapper."""
        pass

    def _is_internal_artifact(self, name: str) -> bool:
        """Check if a symbol name is a Joern internal artifact.

        These are CPG internal constructs that should not appear in
        code analysis output as they are not real code symbols.

        Args:
            name: Symbol name to check.

        Returns:
            True if the name is an internal artifact.
        """
        if not name:
            return True

        # Check exact matches
        if name in self.INTERNAL_ARTIFACT_NAMES:
            return True

        # Check patterns: names starting with < are typically internal
        if name.startswith("<"):
            return True

        # Check for metaClass patterns
        if "metaClass" in name or "meta" in name.lower() and name != name.lower():
            return True

        return False

    def map_parse_result(self, result: CPGParseResult) -> tuple[list[Symbol], list[Dependency]]:
        """
        Map a complete CPGParseResult to symbols and dependencies.

        Args:
            result: Parsed CPG data.

        Returns:
            Tuple of (symbols, dependencies).
        """
        symbols = []
        dependencies = []

        # Pre-process comments for quick lookup
        # Key: (filename, line_number)
        # We assume a comment on line N is for a symbol starting on line N+1
        comment_map = {
            (c.file_path, c.line_number + 1): c.code for c in result.comments
        }

        # Map types first (to establish parent context)
        type_map = {}  # full_name -> CPGType
        for cpg_type in result.types:
            symbol = self.map_type(cpg_type, comment_map)
            if symbol:
                symbols.append(symbol)
                type_map[cpg_type.full_name] = cpg_type

        # Map methods
        for cpg_method in result.methods:
            symbol = self.map_method(cpg_method, comment_map, type_map)
            if symbol:
                symbols.append(symbol)

        # Map members
        for cpg_member in result.members:
            symbol = self.map_member(cpg_member)
            if symbol:
                symbols.append(symbol)

        # Map calls to dependencies
        for cpg_call in result.calls:
            dep = self.map_call(cpg_call)
            if dep:
                dependencies.append(dep)

        # Map data flows to dependencies
        for cpg_flow in result.data_flows:
            dep = self.map_data_flow(cpg_flow)
            if dep:
                dependencies.append(dep)

        # Add inheritance dependencies
        for cpg_type in result.types:
            for dep in self.map_inheritance(cpg_type):
                dependencies.append(dep)

        return symbols, dependencies

    def map_data_flow(self, cpg_flow: Any) -> Dependency | None:
        """
        Map a CPGDataFlow to a Dependency.

        Args:
            cpg_flow: Parsed data flow from CPG.

        Returns:
            Dependency or None if mapping fails.
        """
        # This is a placeholder implementation.
        # The actual source and target need to be resolved to symbol qualified names.
        return Dependency(
            source=f"{cpg_flow.source_file}:{cpg_flow.source_code}",
            target=f"{cpg_flow.sink_file}:{cpg_flow.sink_code}",
            dependency_type="data_flow",
            file_path=cpg_flow.source_file,
            line=cpg_flow.source_line,
            is_external=False,
            external_module=None,
            metadata={"source": "joern"},
        )

    def map_method(
        self,
        cpg_method: CPGMethod,
        comment_map: dict[tuple[str, int], str],
        type_map: dict[str, CPGType] | None = None
    ) -> Symbol | None:
        """
        Map a CPGMethod to a Symbol.

        Args:
            cpg_method: Parsed method from CPG.
            comment_map: Lookup for finding associated comments.
            type_map: Optional mapping of type names for context.

        Returns:
            Symbol or None if mapping fails.
        """
        if not cpg_method.name:
            return None

        # Filter out internal Joern artifacts
        if self._is_internal_artifact(cpg_method.name):
            return None

        # Detect language from filename
        language = self._detect_language(cpg_method.filename)

        # Determine if it's a method (has parent class) or function
        parent_class = self._extract_parent_class(cpg_method.full_name)
        symbol_type = SymbolType.METHOD if parent_class else SymbolType.FUNCTION

        # Detect visibility
        visibility = self._detect_visibility(cpg_method.name, language)

        # Build signature
        signature = cpg_method.signature
        if not signature or signature == cpg_method.name:
            # Build signature from parameters
            params = ", ".join(
                f"{pname}: {ptype}" for pname, ptype in cpg_method.parameters
            )
            signature = f"{cpg_method.name}({params})"

        # Extract return type from signature if present
        return_type = self._extract_return_type(cpg_method.signature)

        # Find associated comment
        documentation = comment_map.get(
            (cpg_method.filename, cpg_method.line_start)
        )

        return Symbol(
            name=cpg_method.name,
            symbol_type=symbol_type,
            file_path=self._normalize_filepath(cpg_method.filename),
            line_start=cpg_method.line_start,
            line_end=cpg_method.line_end if cpg_method.line_end > 0 else None,
            column_start=None,
            signature=signature,
            visibility=visibility,
            language=language,
            documentation=documentation,
            qualified_name=cpg_method.full_name,
            is_exported=visibility == "public",
            metadata={
                "parameters": [
                    {"name": pname, "type": ptype}
                    for pname, ptype in cpg_method.parameters
                ],
                "return_type": return_type,
                "parent_class": parent_class,
                "is_external": cpg_method.is_external,
                "source": "joern",
            },
        )

    def map_type(self, cpg_type: CPGType, comment_map: dict[tuple[str, int], str]) -> Symbol | None:
        """
        Map a CPGType to a Symbol.

        Args:
            cpg_type: Parsed type declaration from CPG.
            comment_map: Lookup for finding associated comments.

        Returns:
            Symbol or None if mapping fails.
        """
        if not cpg_type.name:
            return None

        # Filter out internal Joern artifacts
        if self._is_internal_artifact(cpg_type.name):
            return None

        # Detect language
        language = self._detect_language(cpg_type.filename)

        # Determine if it's a class or interface
        # This is a heuristic - interfaces often have "Interface" in name
        # or specific patterns in inheritance
        symbol_type = self._determine_type_kind(cpg_type, language)

        # Type visibility is usually public unless nested
        visibility = "public"
        if cpg_type.name.startswith("_"):
            visibility = "private" if language == "python" else "internal"

        # Clean up inheritance - extract just class names from full qualified names
        # Joern returns things like ":<module>.py:<module>.BaseService"
        # We want just "BaseService"
        seen_bases = set()
        clean_bases = []
        for base in cpg_type.inherits_from:
            # Extract the last component (class name) first
            class_name = base.split(".")[-1]
            if not class_name:
                continue
            # Now filter based on the extracted class name, not the full path
            if class_name == "ANY":
                continue
            if class_name.startswith("<"):
                continue
            if "meta" in class_name.lower():
                continue
            # Deduplicate while preserving order
            if class_name not in seen_bases:
                seen_bases.add(class_name)
                clean_bases.append(class_name)

        # Find associated comment
        documentation = comment_map.get(
            (cpg_type.filename, cpg_type.line_start)
        )

        return Symbol(
            name=cpg_type.name,
            symbol_type=symbol_type,
            file_path=self._normalize_filepath(cpg_type.filename),
            line_start=cpg_type.line_start,
            line_end=None,
            column_start=None,
            signature=cpg_type.name,
            visibility=visibility,
            language=language,
            documentation=documentation,
            qualified_name=cpg_type.full_name,
            is_exported=visibility == "public",
            metadata={
                "bases": clean_bases,
                "is_external": cpg_type.is_external,
                "source": "joern",
            },
        )

    def map_member(self, cpg_member: CPGMember) -> Symbol | None:
        """
        Map a CPGMember to a Symbol.

        Args:
            cpg_member: Parsed class member from CPG.

        Returns:
            Symbol or None if mapping fails.
        """
        if not cpg_member.name:
            return None

        # Filter out internal Joern artifacts
        if self._is_internal_artifact(cpg_member.name):
            return None

        # Also filter members belonging to internal artifact types
        if cpg_member.parent_type and self._is_internal_artifact(cpg_member.parent_type.split(".")[-1]):
            return None

        # Members don't have filename in our output format
        # We'll use the parent type to infer context

        # Detect visibility from name pattern
        visibility = "public"
        if cpg_member.name.startswith("_"):
            visibility = "private"

        return Symbol(
            name=cpg_member.name,
            symbol_type=SymbolType.VARIABLE,
            file_path="",  # Not available from member query
            line_start=0,
            line_end=None,
            column_start=None,
            signature=f"{cpg_member.name}: {cpg_member.type_name}",
            visibility=visibility,
            language="",  # Unknown without file
            documentation=None,
            qualified_name=f"{cpg_member.parent_type}.{cpg_member.name}",
            is_exported=visibility == "public",
            metadata={
                "type": cpg_member.type_name,
                "parent_class": cpg_member.parent_type,
                "source": "joern",
            },
        )

    def map_call(self, cpg_call: CPGCall) -> Dependency | None:
        """
        Map a CPGCall to a Dependency.

        Args:
            cpg_call: Parsed call site from CPG.

        Returns:
            Dependency or None if mapping fails.
        """
        if not cpg_call.caller or not cpg_call.callee:
            return None

        return Dependency(
            source=cpg_call.caller,
            target=cpg_call.callee,
            dependency_type="call",
            file_path="",  # Not directly available
            line=cpg_call.line_number if cpg_call.line_number > 0 else None,
            is_external=False,  # Determined later
            external_module=None,
            metadata={"source": "joern"},
        )

    def map_inheritance(self, cpg_type: CPGType) -> list[Dependency]:
        """
        Map inheritance relationships to dependencies.

        Args:
            cpg_type: Parsed type declaration.

        Returns:
            List of inheritance dependencies.
        """
        dependencies = []

        for base_type in cpg_type.inherits_from:
            dependencies.append(
                Dependency(
                    source=cpg_type.full_name or cpg_type.name,
                    target=base_type,
                    dependency_type="inherits",
                    file_path=self._normalize_filepath(cpg_type.filename),
                    line=cpg_type.line_start if cpg_type.line_start > 0 else None,
                    is_external=False,
                    external_module=None,
                    metadata={"source": "joern"},
                )
            )

        return dependencies

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        if not filename:
            return ""

        ext = os.path.splitext(filename)[1].lower()
        return self.EXTENSION_TO_LANGUAGE.get(ext, "")

    def _normalize_filepath(self, filepath: str) -> str:
        """
        Normalize file path, handling temp files from Joern frontends.

        Some Joern frontends (especially jssrc2cpg for JavaScript/TypeScript)
        create temporary files during transpilation. These temp file names
        leak into the CPG and appear in the output.

        This method detects temp file patterns and replaces them with a
        meaningful placeholder.

        Args:
            filepath: Original file path from CPG.

        Returns:
            Normalized file path.
        """
        if not filepath:
            return filepath

        # Check if it's a temp file
        if self.TEMP_FILE_PATTERN.match(filepath):
            # Extract just the extension for a cleaner placeholder
            ext = os.path.splitext(filepath)[1]
            return f"<transpiled>{ext}"

        # Check for /tmp/ paths that aren't temp patterns
        # (e.g., analysis of a temp directory)
        basename = os.path.basename(filepath)
        if filepath.startswith('/tmp/') and basename.startswith('tmp'):
            ext = os.path.splitext(filepath)[1]
            return f"<transpiled>{ext}"

        return filepath

    def _detect_visibility(self, name: str, language: str) -> str:
        """
        Detect symbol visibility based on naming conventions.

        Args:
            name: Symbol name.
            language: Programming language.

        Returns:
            Visibility string: "public", "private", "protected", or "internal".
        """
        patterns = self.VISIBILITY_PATTERNS.get(
            language, self.VISIBILITY_PATTERNS["default"]
        )

        if "private" in patterns and patterns["private"](name):
            return "private"
        if "protected" in patterns and patterns["protected"](name):
            return "protected"
        return "public"

    def _extract_parent_class(self, full_name: str) -> str | None:
        """
        Extract parent class name from fully qualified name.

        Examples:
            "MyClass.myMethod" -> "MyClass"
            "module.MyClass.myMethod" -> "MyClass"
            "myFunction" -> None
        """
        if not full_name:
            return None

        parts = full_name.split(".")
        if len(parts) >= 2:
            # The second-to-last part is likely the class name
            # unless it looks like a module name (lowercase)
            potential_class = parts[-2]
            if potential_class and potential_class[0].isupper():
                return potential_class

        return None

    def _extract_return_type(self, signature: str) -> str | None:
        """
        Extract return type from method signature.

        Handles various formats:
            "method(args): ReturnType"
            "method(args) -> ReturnType"
            "ReturnType method(args)"
        """
        if not signature:
            return None

        # Python/TypeScript style: -> ReturnType
        if "->" in signature:
            parts = signature.split("->")
            if len(parts) >= 2:
                return parts[-1].strip()

        # Type annotation style: method(): ReturnType
        if "):" in signature:
            parts = signature.split("):")
            if len(parts) >= 2:
                return parts[-1].strip()

        return None

    def _determine_type_kind(self, cpg_type: CPGType, language: str) -> SymbolType:
        """
        Determine if a type is a class, interface, enum, etc.

        Uses heuristics based on naming patterns and language conventions.
        """
        name = cpg_type.name
        full_name = cpg_type.full_name or name

        # Interface detection
        if language in ("java", "kotlin", "typescript", "csharp"):
            if name.startswith("I") and len(name) > 1 and name[1].isupper():
                return SymbolType.INTERFACE
            if "Interface" in name:
                return SymbolType.INTERFACE

        # Protocol detection (Swift, Python)
        if language in ("swift", "python"):
            if "Protocol" in name:
                return SymbolType.INTERFACE

        # Enum detection
        if "Enum" in name or name.endswith("Enum"):
            return SymbolType.ENUM

        # Default to CLASS
        return SymbolType.CLASS
