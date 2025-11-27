"""Core code analyzer orchestrating multiple language extractors."""
from typing import List, Dict, Optional, Any
from pathlib import Path
from .models import Symbol, SymbolType, Dependency
from .python_extractor import PythonExtractor
from .javascript_extractor import JavaScriptExtractor
from .java_extractor import JavaExtractor
from .kotlin_extractor import KotlinExtractor


class CodeAnalyzer:
    """Main code analyzer that coordinates language-specific extractors."""

    def __init__(self):
        """Initialize code analyzer with language extractors."""
        self.python_extractor = PythonExtractor()
        self.javascript_extractor = JavaScriptExtractor("javascript")
        self.typescript_extractor = JavaScriptExtractor("typescript")
        self.java_extractor = JavaExtractor()
        self.kotlin_extractor = KotlinExtractor()

        # Language detection mapping
        self.language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".kt": "kotlin",
        }

    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name or None if unsupported
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        return self.language_map.get(ext)

    def analyze_file(self, code: str, file_path: str) -> List[Symbol]:
        """
        Analyze a single file and extract symbols.

        Args:
            code: Source code content
            file_path: Path to the file

        Returns:
            List of Symbol objects
        """
        language = self.detect_language(file_path)

        if not language:
            return []

        if language == "python":
            return self.python_extractor.extract_symbols(code, file_path)
        elif language == "javascript":
            return self.javascript_extractor.extract_symbols(code, file_path)
        elif language == "typescript":
            return self.typescript_extractor.extract_symbols(code, file_path)
        elif language == "java":
            return self.java_extractor.extract_symbols(code, file_path)
        elif language == "kotlin":
            return self.kotlin_extractor.extract_symbols(code, file_path)

        return []

    def analyze_files(self, files: Dict[str, str]) -> Dict[str, List[Symbol]]:
        """
        Analyze multiple files.

        Args:
            files: Dictionary mapping file paths to code content

        Returns:
            Dictionary mapping file paths to lists of symbols
        """
        results = {}

        for file_path, code in files.items():
            symbols = self.analyze_file(code, file_path)
            results[file_path] = symbols

        return results

    def extract_dependencies(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Extract dependencies from a file.

        Args:
            code: Source code content
            file_path: Path to the file

        Returns:
            List of dependency dictionaries
        """
        language = self.detect_language(file_path)

        if not language:
            return []

        if language == "python":
            return self.python_extractor.extract_dependencies(code, file_path)
        elif language in ["javascript", "typescript"]:
            extractor = self.javascript_extractor if language == "javascript" else self.typescript_extractor
            return extractor.extract_dependencies(code, file_path)
        elif language == "java":
            return self.java_extractor.extract_dependencies(code, file_path)
        elif language == "kotlin":
            return self.kotlin_extractor.extract_dependencies(code, file_path)

        return []

    def filter_symbols_by_type(self, symbols: List[Symbol], symbol_type: SymbolType) -> List[Symbol]:
        """
        Filter symbols by type.

        Args:
            symbols: List of symbols to filter
            symbol_type: Type to filter by

        Returns:
            Filtered list of symbols
        """
        return [s for s in symbols if s.symbol_type == symbol_type]

    def filter_symbols_by_visibility(self, symbols: List[Symbol], visibility: str) -> List[Symbol]:
        """
        Filter symbols by visibility.

        Args:
            symbols: List of symbols to filter
            visibility: Visibility to filter by (public, private, protected)

        Returns:
            Filtered list of symbols
        """
        return [s for s in symbols if s.visibility == visibility]

    def get_statistics(self, symbols: List[Symbol]) -> Dict[str, Any]:
        """
        Get statistics about symbols.

        Args:
            symbols: List of symbols to analyze

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_symbols": len(symbols),
            "by_type": {},
            "by_visibility": {},
            "by_language": {},
        }

        # Count by type
        for symbol in symbols:
            type_key = symbol.symbol_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1

            # Count by visibility
            vis_key = symbol.visibility
            stats["by_visibility"][vis_key] = stats["by_visibility"].get(vis_key, 0) + 1

            # Count by language
            lang_key = symbol.language
            stats["by_language"][lang_key] = stats["by_language"].get(lang_key, 0) + 1

        return stats

    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported programming languages.

        Returns:
            List of language names
        """
        return list(set(self.language_map.values()))

    def find_symbol(self, symbols: List[Symbol], name: str) -> Optional[Symbol]:
        """
        Find a symbol by name.

        Args:
            symbols: List of symbols to search
            name: Symbol name to find

        Returns:
            Symbol object or None if not found
        """
        for symbol in symbols:
            if symbol.name == name or symbol.qualified_name == name:
                return symbol
        return None

    def find_symbols(self, symbols: List[Symbol], name_pattern: str) -> List[Symbol]:
        """
        Find symbols matching a name pattern.

        Args:
            symbols: List of symbols to search
            name_pattern: Pattern to match (substring match)

        Returns:
            List of matching symbols
        """
        pattern_lower = name_pattern.lower()
        return [s for s in symbols if pattern_lower in s.name.lower()]

    def get_class_methods(self, symbols: List[Symbol], class_name: str) -> List[Symbol]:
        """
        Get all methods of a specific class.

        Args:
            symbols: List of symbols to search
            class_name: Name of the class

        Returns:
            List of method symbols
        """
        return [
            s for s in symbols
            if s.symbol_type == SymbolType.METHOD and s.metadata.get("parent_class") == class_name
        ]

    def aggregate_symbols(self, file_results: Dict[str, List[Symbol]]) -> List[Symbol]:
        """
        Aggregate symbols from multiple files into a single list.

        Args:
            file_results: Dictionary mapping file paths to symbol lists

        Returns:
            Combined list of all symbols
        """
        all_symbols = []
        for symbols in file_results.values():
            all_symbols.extend(symbols)
        return all_symbols
