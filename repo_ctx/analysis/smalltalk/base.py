"""
Base Smalltalk extractor with shared logic.

This module provides the abstract base class for Smalltalk symbol extractors,
containing common functionality shared between Standard and Cincom implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional

from repo_ctx.analysis.models import Symbol, SymbolType
from repo_ctx.analysis.smalltalk.fileout_parser import (
    FileOutParser,
    ClassDefinition,
    MethodDefinition,
)
from repo_ctx.analysis.smalltalk.method_parser import MethodParser


class BaseSmalltalkExtractor(ABC):
    """
    Abstract base class for Smalltalk symbol extraction.

    Provides common functionality for extracting symbols from Smalltalk
    file-out format, with dialect-specific behavior in subclasses.
    """

    # Dialect identifier for this extractor
    DIALECT: str = "unknown"

    def __init__(self):
        """Initialize the extractor with shared parsers."""
        self.fileout_parser = FileOutParser()
        self.method_parser = MethodParser()

    def extract_symbols(self, code: str, file_path: str) -> list[Symbol]:
        """
        Extract all symbols from Smalltalk code.

        Args:
            code: Smalltalk source code (file-out format)
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        symbols = []

        # Parse the file-out into chunks
        chunks = self.fileout_parser.parse(code)

        # Extract classes
        classes = self.fileout_parser.get_classes(chunks)
        for class_def in classes:
            symbol = self._class_to_symbol(class_def, file_path)
            symbols.append(symbol)

        # Extract methods
        methods = self.fileout_parser.get_methods(chunks)
        for method_def in methods:
            symbol = self._method_to_symbol(method_def, file_path)
            symbols.append(symbol)

        return symbols

    @abstractmethod
    def _class_to_symbol(self, class_def: ClassDefinition, file_path: str) -> Symbol:
        """
        Convert a ClassDefinition to a Symbol.

        Subclasses implement dialect-specific handling.

        Args:
            class_def: Parsed class definition
            file_path: Path to the file

        Returns:
            Symbol object representing the class
        """
        pass

    def _method_to_symbol(self, method_def: MethodDefinition, file_path: str) -> Symbol:
        """
        Convert a MethodDefinition to a Symbol.

        Args:
            method_def: Parsed method definition
            file_path: Path to the file

        Returns:
            Symbol object representing the method
        """
        # Parse the method body for additional info
        parsed = self.method_parser.parse(method_def.source)

        # Build qualified name: ClassName>>selector or ClassName class>>selector
        class_side = " class" if method_def.is_class_method else ""
        qualified_name = f"{method_def.class_name}{class_side}>>{method_def.selector}"

        # Build signature from selector and parameters
        signature = self._build_signature(parsed.selector, parsed.parameters)

        return Symbol(
            name=method_def.selector,
            symbol_type=SymbolType.METHOD,
            file_path=file_path,
            line_start=method_def.line_number,
            qualified_name=qualified_name,
            language="smalltalk",
            signature=signature,
            documentation=parsed.documentation or None,
            visibility="public",  # Smalltalk methods are always public
            metadata={
                "parent_class": method_def.class_name,
                "is_class_method": method_def.is_class_method,
                "category": method_def.category,
                "parameters": parsed.parameters,
                "temporaries": parsed.temporaries,
                "selector_type": parsed.selector_type,
                "stamp": method_def.stamp,
                "dialect": self.DIALECT,
            },
        )

    def _build_signature(self, selector: str, parameters: list[str]) -> str:
        """
        Build a method signature string.

        Args:
            selector: Method selector
            parameters: List of parameter names

        Returns:
            Signature string like "width: w height: h" or "area"
        """
        if not parameters:
            return selector

        # For keyword selectors, interleave keywords with parameters
        keywords = selector.split(":")
        keywords = [k for k in keywords if k]  # Remove empty strings

        if len(keywords) == len(parameters):
            parts = []
            for kw, param in zip(keywords, parameters):
                parts.append(f"{kw}: {param}")
            return " ".join(parts)

        # Fallback
        return selector

    def detect_dialect(self, code: str) -> str:
        """
        Detect the Smalltalk dialect from source code.

        Args:
            code: Smalltalk source code

        Returns:
            Dialect identifier: "visualworks", "squeak", "pharo", or "standard"
        """
        return self.fileout_parser.detect_dialect(code)

    def extract_dependencies(
        self, code: str, file_path: str, symbols: Optional[list[Symbol]] = None
    ) -> list[dict]:
        """
        Extract dependencies (message sends, class references) from code.

        Args:
            code: Smalltalk source code
            file_path: Path to the file
            symbols: Optional list of symbols (unused, for interface compatibility)

        Returns:
            List of dependency dictionaries
        """
        dependencies = []
        chunks = self.fileout_parser.parse(code)

        # Collect class references from inheritance
        classes = self.fileout_parser.get_classes(chunks)
        for class_def in classes:
            if class_def.superclass and class_def.superclass != "Object":
                dependencies.append({
                    "from": class_def.name,
                    "to": class_def.superclass,
                    "type": "inherits",
                })

        # Collect message sends from methods
        methods = self.fileout_parser.get_methods(chunks)
        for method_def in methods:
            parsed = self.method_parser.parse(method_def.source)
            messages = self.method_parser.extract_message_sends(parsed.body)

            for msg in messages:
                dependencies.append({
                    "from": f"{method_def.class_name}>>{method_def.selector}",
                    "to": msg,
                    "type": "calls",
                })

        return dependencies

    @classmethod
    def supports_dialect(cls, dialect: str) -> bool:
        """
        Check if this extractor supports the given dialect.

        Args:
            dialect: Dialect identifier

        Returns:
            True if this extractor supports the dialect
        """
        return dialect.lower() == cls.DIALECT.lower()
