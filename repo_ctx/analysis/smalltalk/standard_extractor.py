"""
Standard Smalltalk extractor for Squeak/Pharo file-out format.

This module provides symbol extraction for standard Smalltalk file-out
format as used by Squeak, Pharo, and similar open-source implementations.

Standard format characteristics:
- Class definition: `Superclass subclass: #ClassName instanceVariableNames: 'vars'...`
- Method header: `!ClassName methodsFor: 'category' stamp: 'author date'!`
- Chunk delimiter: `!` with `! !` for method end
- Categories for organization
"""

from repo_ctx.analysis.models import Symbol, SymbolType
from repo_ctx.analysis.smalltalk.base import BaseSmalltalkExtractor
from repo_ctx.analysis.smalltalk.fileout_parser import ClassDefinition


class StandardSmalltalkExtractor(BaseSmalltalkExtractor):
    """
    Extract symbols from standard Smalltalk (Squeak/Pharo) file-out format.

    Supports:
    - Squeak file-out format
    - Pharo file-out format
    - Generic standard Smalltalk file-out
    """

    DIALECT = "standard"

    # Also support squeak and pharo as aliases
    SUPPORTED_DIALECTS = {"standard", "squeak", "pharo"}

    def _class_to_symbol(self, class_def: ClassDefinition, file_path: str) -> Symbol:
        """
        Convert a ClassDefinition to a Symbol for standard Smalltalk.

        Args:
            class_def: Parsed class definition
            file_path: Path to the file

        Returns:
            Symbol object representing the class
        """
        # Build qualified name with category if available
        qualified_name = class_def.name
        if class_def.category:
            qualified_name = f"{class_def.category}.{class_def.name}"

        return Symbol(
            name=class_def.name,
            symbol_type=SymbolType.CLASS,
            file_path=file_path,
            line_start=class_def.line_number,
            qualified_name=qualified_name,
            language="smalltalk",
            documentation=class_def.comment or None,
            visibility="public",  # Standard Smalltalk doesn't have private classes
            metadata={
                "superclass": class_def.superclass,
                "instance_variables": class_def.instance_variables,
                "class_variables": class_def.class_variables,
                "pool_dictionaries": class_def.pool_dictionaries,
                "category": class_def.category,
                "dialect": self.DIALECT,
            },
        )

    @classmethod
    def supports_dialect(cls, dialect: str) -> bool:
        """
        Check if this extractor supports the given dialect.

        Supports standard, squeak, and pharo dialects.

        Args:
            dialect: Dialect identifier

        Returns:
            True if this extractor supports the dialect
        """
        return dialect.lower() in cls.SUPPORTED_DIALECTS
