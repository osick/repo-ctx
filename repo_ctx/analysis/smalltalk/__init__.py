"""
Smalltalk code analysis module.

This module provides parsers and extractors for Smalltalk source code,
supporting multiple dialects including:
- Standard Smalltalk (Squeak/Pharo file-out format)
- Cincom VisualWorks file-out format

Usage:
    from repo_ctx.analysis.smalltalk import (
        create_extractor,
        StandardSmalltalkExtractor,
        CincomSmalltalkExtractor,
    )

    # Auto-detect dialect
    extractor = create_extractor(code)
    symbols = extractor.extract_symbols(code, "sample.st")

    # Or specify dialect explicitly
    extractor = create_extractor(dialect="visualworks")
    symbols = extractor.extract_symbols(code, "sample.st")
"""

from repo_ctx.analysis.smalltalk.fileout_parser import (
    FileOutParser,
    Chunk,
    ChunkType,
    ClassDefinition,
    MethodDefinition,
)
from repo_ctx.analysis.smalltalk.method_parser import MethodParser
from repo_ctx.analysis.smalltalk.base import BaseSmalltalkExtractor
from repo_ctx.analysis.smalltalk.standard_extractor import StandardSmalltalkExtractor
from repo_ctx.analysis.smalltalk.cincom_extractor import CincomSmalltalkExtractor


def create_extractor(
    code: str | None = None,
    dialect: str | None = None,
) -> BaseSmalltalkExtractor:
    """
    Create an appropriate Smalltalk extractor.

    If dialect is specified, creates that specific extractor.
    If code is provided without dialect, auto-detects the dialect.
    If neither is provided, returns a StandardSmalltalkExtractor.

    Args:
        code: Optional source code for dialect detection
        dialect: Optional dialect identifier ("standard", "squeak", "pharo",
                "visualworks", "cincom", "vw")

    Returns:
        Appropriate BaseSmalltalkExtractor subclass instance

    Examples:
        # Auto-detect from code
        extractor = create_extractor(code=source_code)

        # Specify dialect explicitly
        extractor = create_extractor(dialect="visualworks")
    """
    # If dialect is specified, use it
    if dialect:
        if CincomSmalltalkExtractor.supports_dialect(dialect):
            return CincomSmalltalkExtractor()
        elif StandardSmalltalkExtractor.supports_dialect(dialect):
            return StandardSmalltalkExtractor()
        else:
            # Unknown dialect, default to standard
            return StandardSmalltalkExtractor()

    # If code is provided, auto-detect
    if code:
        parser = FileOutParser()
        detected = parser.detect_dialect(code)

        if detected == "visualworks":
            return CincomSmalltalkExtractor()
        else:
            return StandardSmalltalkExtractor()

    # Default to standard
    return StandardSmalltalkExtractor()


__all__ = [
    # Parsers
    "FileOutParser",
    "MethodParser",
    "Chunk",
    "ChunkType",
    "ClassDefinition",
    "MethodDefinition",
    # Extractors
    "BaseSmalltalkExtractor",
    "StandardSmalltalkExtractor",
    "CincomSmalltalkExtractor",
    # Factory
    "create_extractor",
]
