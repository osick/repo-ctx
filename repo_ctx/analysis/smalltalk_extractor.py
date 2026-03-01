"""
Smalltalk code symbol extractor.

Extracts symbols from Smalltalk file-out format, supporting:
- Standard Squeak/Pharo file-out format
- Cincom VisualWorks file-out format

This module provides a unified interface that automatically selects
the appropriate dialect-specific extractor based on the source code.

For direct access to dialect-specific extractors, use:
    from repo_ctx.analysis.smalltalk import (
        StandardSmalltalkExtractor,
        CincomSmalltalkExtractor,
        create_extractor,
    )
"""

from typing import Optional

from repo_ctx.analysis.models import Symbol
from repo_ctx.analysis.smalltalk import (
    create_extractor,
    BaseSmalltalkExtractor,
    FileOutParser,
)


class SmalltalkExtractor:
    """
    Unified Smalltalk symbol extractor with automatic dialect detection.

    This class provides backward compatibility and acts as a facade that
    delegates to the appropriate dialect-specific extractor.

    For explicit dialect control, use:
    - StandardSmalltalkExtractor for Squeak/Pharo format
    - CincomSmalltalkExtractor for VisualWorks format
    - create_extractor() factory function

    Attributes:
        dialect: The currently active dialect ("standard", "visualworks", etc.)
    """

    def __init__(self, dialect: Optional[str] = None):
        """
        Initialize Smalltalk extractor.

        Args:
            dialect: Optional dialect to use. If not specified, dialect will
                    be auto-detected from source code on first use.
        """
        self._dialect = dialect
        self._extractor: Optional[BaseSmalltalkExtractor] = None
        self._fileout_parser = FileOutParser()

        # If dialect is specified, create extractor now
        if dialect:
            self._extractor = create_extractor(dialect=dialect)

    @property
    def dialect(self) -> str:
        """Get the current dialect."""
        if self._extractor:
            return self._extractor.DIALECT
        return self._dialect or "unknown"

    def _get_extractor(self, code: str) -> BaseSmalltalkExtractor:
        """
        Get the appropriate extractor for the given code.

        Creates and caches the extractor on first use.

        Args:
            code: Source code for dialect detection

        Returns:
            Appropriate extractor instance
        """
        if self._extractor is None:
            self._extractor = create_extractor(code=code, dialect=self._dialect)
        return self._extractor

    def extract_symbols(self, code: str, file_path: str) -> list[Symbol]:
        """
        Extract all symbols from Smalltalk code.

        Automatically detects the dialect and uses the appropriate extractor.

        Args:
            code: Smalltalk source code (file-out format)
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        extractor = self._get_extractor(code)
        return extractor.extract_symbols(code, file_path)

    def detect_dialect(self, code: str) -> str:
        """
        Detect the Smalltalk dialect from source code.

        Args:
            code: Smalltalk source code

        Returns:
            Dialect identifier: "visualworks", "squeak", "pharo", or "standard"
        """
        return self._fileout_parser.detect_dialect(code)

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
        extractor = self._get_extractor(code)
        return extractor.extract_dependencies(code, file_path, symbols)

    # Convenience methods for creating dialect-specific extractors

    @staticmethod
    def for_standard() -> "SmalltalkExtractor":
        """
        Create an extractor for standard Smalltalk (Squeak/Pharo).

        Returns:
            SmalltalkExtractor configured for standard dialect
        """
        return SmalltalkExtractor(dialect="standard")

    @staticmethod
    def for_visualworks() -> "SmalltalkExtractor":
        """
        Create an extractor for Cincom VisualWorks.

        Returns:
            SmalltalkExtractor configured for VisualWorks dialect
        """
        return SmalltalkExtractor(dialect="visualworks")

    @staticmethod
    def for_cincom() -> "SmalltalkExtractor":
        """
        Create an extractor for Cincom VisualWorks (alias).

        Returns:
            SmalltalkExtractor configured for VisualWorks dialect
        """
        return SmalltalkExtractor(dialect="visualworks")
