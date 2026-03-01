"""Core code analyzer orchestrating multiple language extractors."""
import os
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path
from .models import Symbol, SymbolType, Dependency
from .python_extractor import PythonExtractor
from .javascript_extractor import JavaScriptExtractor
from .java_extractor import JavaExtractor
from .kotlin_extractor import KotlinExtractor
from .smalltalk_extractor import SmalltalkExtractor
from .generic_extractor import GenericExtractor, create_generic_extractor

logger = logging.getLogger(__name__)

# Joern adapter (lazy import to avoid hard dependency)
_joern_adapter = None


def get_joern_adapter():
    """Get or create JoernAdapter instance (lazy loading)."""
    global _joern_adapter
    if _joern_adapter is None:
        try:
            from repo_ctx.joern.adapter import JoernAdapter
            _joern_adapter = JoernAdapter()
            if not _joern_adapter.is_available():
                logger.debug("Joern is not available on this system")
                _joern_adapter = False  # Mark as unavailable
        except ImportError:
            logger.debug("Joern module not available")
            _joern_adapter = False
    return _joern_adapter if _joern_adapter is not False else None


class CodeAnalyzer:
    """Main code analyzer that coordinates language-specific extractors.

    By default, uses Joern CPG for comprehensive analysis when available.
    Falls back to tree-sitter for speed or when Joern is not installed.
    """

    # Languages supported via tree-sitter (fast, fallback backend)
    # Also includes Smalltalk with custom parser
    TREESITTER_LANGUAGES = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".kt": "kotlin",
        ".st": "smalltalk",
        # Additional languages (previously Joern-only)
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php",
        ".cs": "c_sharp",
        ".sh": "bash",
        ".bash": "bash",
    }

    # Languages supported via Joern CPG (comprehensive, primary backend)
    # Joern provides deeper analysis (call graphs, data flow) but requires external tool
    JOERN_LANGUAGES = {
        # Languages with both Joern and tree-sitter support
        ".c": "c",
        ".h": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".hpp": "cpp",
        ".hxx": "cpp",
        ".go": "go",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",  # Swift only via Joern (no tree-sitter-swift)
        ".cs": "csharp",
        ".rs": "rust",
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".java": "java",
        ".kt": "kotlin",
        ".kts": "kotlin",
    }

    def __init__(
        self,
        use_treesitter: bool = False,
        joern_path: str | None = None,
        smalltalk_dialect: str | None = None,
    ):
        """
        Initialize code analyzer with language extractors.

        Args:
            use_treesitter: If True, force tree-sitter instead of Joern for
                           supported languages (faster but less comprehensive).
            joern_path: Custom path to Joern installation.
            smalltalk_dialect: Smalltalk dialect to use ("standard", "squeak",
                             "pharo", "visualworks", "cincom"). If None,
                             auto-detects from source code.
        """
        self.use_treesitter = use_treesitter
        self._joern_path = joern_path
        self._joern_adapter = None  # Lazy initialization
        self._smalltalk_dialect = smalltalk_dialect

        # Tree-sitter extractors (used as fallback or when use_treesitter=True)
        self.python_extractor = PythonExtractor()
        self.javascript_extractor = JavaScriptExtractor("javascript")
        self.typescript_extractor = JavaScriptExtractor("typescript")
        self.java_extractor = JavaExtractor()
        self.kotlin_extractor = KotlinExtractor()
        self.smalltalk_extractor = SmalltalkExtractor(dialect=smalltalk_dialect)

        # Generic extractors for additional languages (lazy initialization)
        self._generic_extractors: Dict[str, GenericExtractor] = {}

        # Combined language detection mapping (Joern takes precedence)
        self.language_map = {**self.TREESITTER_LANGUAGES, **self.JOERN_LANGUAGES}

    def _get_generic_extractor(self, language: str) -> Optional[GenericExtractor]:
        """Get or create a generic extractor for the given language."""
        if language not in self._generic_extractors:
            try:
                self._generic_extractors[language] = create_generic_extractor(language)
            except (ImportError, ValueError) as e:
                logger.warning(f"Could not create extractor for {language}: {e}")
                return None
        return self._generic_extractors.get(language)

    @property
    def supported_extensions(self) -> dict[str, str]:
        """Get extensions that can actually be analyzed in current mode.

        When use_treesitter=True, only returns tree-sitter supported extensions.
        Otherwise returns all supported extensions.
        """
        if self.use_treesitter:
            return self.TREESITTER_LANGUAGES.copy()
        return self.language_map.copy()

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

    @property
    def joern_adapter(self):
        """Get or create JoernAdapter (lazy initialization)."""
        if self._joern_adapter is None:
            if self._joern_path:
                from repo_ctx.joern.adapter import JoernAdapter
                self._joern_adapter = JoernAdapter(joern_path=self._joern_path)
            else:
                self._joern_adapter = get_joern_adapter()
        return self._joern_adapter

    def is_joern_available(self) -> bool:
        """Check if Joern is available for analysis."""
        adapter = self.joern_adapter
        return adapter is not None and adapter.is_available()

    # Extensions where tree-sitter is preferred over Joern
    # Joern's jssrc2cpg creates temp files during transpilation, losing original file paths
    PREFER_TREESITTER = {".js", ".jsx", ".ts", ".tsx", ".mjs"}

    def _use_joern_for_language(self, language: str, ext: str) -> bool:
        """Determine if Joern should be used for a given language.

        Default behavior: Use Joern when available (comprehensive analysis).
        Exceptions:
        - JS/TS: Prefer tree-sitter because Joern's jssrc2cpg loses file paths
        - user set use_treesitter=True: Force tree-sitter for all supported langs
        """
        # User explicitly requested tree-sitter
        if self.use_treesitter and ext in self.TREESITTER_LANGUAGES:
            return False

        # Prefer tree-sitter for JS/TS - Joern's transpilation loses file paths
        if ext in self.PREFER_TREESITTER:
            return False

        # Use Joern for all other supported languages
        if ext in self.JOERN_LANGUAGES:
            return True

        return False

    def analyze_file(self, code: str, file_path: str) -> tuple[List[Symbol], List[Dependency]]:
        """
        Analyze a single file and extract symbols and dependencies.

        Args:
            code: Source code content
            file_path: Path to the file

        Returns:
            A tuple containing:
            - List of Symbol objects
            - List of Dependency objects
        """
        language = self.detect_language(file_path)

        if not language:
            return [], []

        ext = Path(file_path).suffix.lower()

        # Check if we should use Joern for this file
        if self._use_joern_for_language(language, ext):
            adapter = self.joern_adapter
            if adapter and adapter.is_available():
                try:
                    analysis_result = adapter.analyze_directory(file_path)
                    return analysis_result.symbols, analysis_result.dependencies
                except Exception as e:
                    logger.warning(f"Joern analysis failed for {file_path}: {e}")
                    # Fall through to tree-sitter if Joern fails and it's supported

        # Use tree-sitter extractors (or custom parsers)
        if language == "python":
            return self.python_extractor.extract(code, file_path)
        elif language == "javascript":
            symbols = self.javascript_extractor.extract_symbols(code, file_path)
            dependencies = self.javascript_extractor.extract_dependencies(code, file_path, symbols)
            return symbols, dependencies
        elif language == "typescript":
            symbols = self.typescript_extractor.extract_symbols(code, file_path)
            dependencies = self.typescript_extractor.extract_dependencies(code, file_path, symbols)
            return symbols, dependencies
        elif language == "java":
            symbols = self.java_extractor.extract_symbols(code, file_path)
            dependencies = self.java_extractor.extract_dependencies(code, file_path, symbols)
            return symbols, dependencies
        elif language == "kotlin":
            symbols = self.kotlin_extractor.extract_symbols(code, file_path)
            dependencies = self.kotlin_extractor.extract_dependencies(code, file_path, symbols)
            return symbols, dependencies
        elif language == "smalltalk":
            symbols = self.smalltalk_extractor.extract_symbols(code, file_path)
            dependencies = self.smalltalk_extractor.extract_dependencies(code, file_path, symbols)
            return symbols, dependencies
        elif language in ("c", "cpp", "go", "rust", "ruby", "php", "c_sharp", "bash"):
            # Use generic extractor for additional languages
            extractor = self._get_generic_extractor(language)
            if extractor:
                symbols = extractor.extract_symbols(code, file_path)
                dependencies = extractor.extract_dependencies(code, file_path, symbols)
                return symbols, dependencies

        return [], []

    def analyze_files(self, files: Dict[str, str]) -> Dict[str, tuple[List[Symbol], List[Dependency]]]:
        """
        Analyze multiple files.

        Args:
            files: Dictionary mapping file paths to code content

        Returns:
            Dictionary mapping file paths to a tuple of (symbols, dependencies)
        """
        results = {}
        
        # 1. Identify Joern candidates
        joern_candidates = []
        other_files = []
        
        for file_path in files:
            lang = self.detect_language(file_path)
            if not lang:
                continue
                
            ext = Path(file_path).suffix.lower()
            if self._use_joern_for_language(lang, ext):
                joern_candidates.append(file_path)
            else:
                other_files.append(file_path)
                
        # 2. Bulk analyze Joern candidates
        if joern_candidates and self.is_joern_available():
            try:
                # Find common root
                abs_paths = [os.path.abspath(p) for p in joern_candidates]
                common_root = os.path.commonpath(abs_paths)
                if os.path.isfile(common_root):
                    common_root = os.path.dirname(common_root)
                
                # Analyze root
                analysis_result = self.joern_adapter.analyze_directory(
                    common_root,
                    use_cache=True
                )
                
                # Group results by file path
                # Create a map of abs_path -> original_key
                path_map = {os.path.abspath(p): p for p in joern_candidates}
                
                # Initialize results for candidates (so empty files get empty lists)
                for p in joern_candidates:
                    results[p] = ([], [])
                
                # Distribute symbols
                for sym in analysis_result.symbols:
                    if not sym.file_path:
                        continue
                    # Joern may return relative paths - resolve against common_root
                    if os.path.isabs(sym.file_path):
                        abs_sym_path = sym.file_path
                    else:
                        abs_sym_path = os.path.normpath(os.path.join(common_root, sym.file_path))
                    if abs_sym_path in path_map:
                        original_key = path_map[abs_sym_path]
                        results[original_key][0].append(sym)

                # Distribute dependencies
                for dep in analysis_result.dependencies:
                    if dep.file_path:
                        # Joern may return relative paths - resolve against common_root
                        if os.path.isabs(dep.file_path):
                            abs_dep_path = dep.file_path
                        else:
                            abs_dep_path = os.path.normpath(os.path.join(common_root, dep.file_path))
                        if abs_dep_path in path_map:
                            original_key = path_map[abs_dep_path]
                            results[original_key][1].append(dep)
                            
            except Exception as e:
                logger.error(f"Bulk Joern analysis failed: {e}")
                # Fallback to individual analysis for these files
                other_files.extend(joern_candidates)
        else:
            # If Joern not available, treat all as others
            other_files.extend(joern_candidates)
            
        # 3. Analyze remaining files individually
        for file_path in other_files:
            code = files.get(file_path, "")
            results[file_path] = self.analyze_file(code, file_path)
            
        return results

    def extract_dependencies(self, code: str, file_path: str, symbols: Optional[List[Symbol]] = None) -> List[Dependency]:
        """
        Extract dependencies from a file. (Deprecated)
        """
        language = self.detect_language(file_path)

        if not language:
            return []

        if language == "python":
            _, dependencies = self.python_extractor.extract(code, file_path)
            return dependencies
        elif language in ["javascript", "typescript"]:
            extractor = self.javascript_extractor if language == "javascript" else self.typescript_extractor
            return extractor.extract_dependencies(code, file_path)
        elif language == "java":
            return self.java_extractor.extract_dependencies(code, file_path)
        elif language == "kotlin":
            return self.kotlin_extractor.extract_dependencies(code, file_path)
        elif language == "smalltalk":
            return self.smalltalk_extractor.extract_dependencies(code, file_path)
        elif language in ("c", "cpp", "go", "rust", "ruby", "php", "c_sharp", "bash"):
            extractor = self._get_generic_extractor(language)
            if extractor:
                return extractor.extract_dependencies(code, file_path, symbols)

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

    def aggregate_symbols(self, file_results: Dict[str, tuple[List[Symbol], List[Dependency]]]) -> List[Symbol]:
        """
        Aggregate symbols from multiple files into a single list.

        Args:
            file_results: Dictionary mapping file paths to (symbols, dependencies)

        Returns:
            Combined list of all symbols
        """
        all_symbols = []
        for symbols, _ in file_results.values():
            all_symbols.extend(symbols)
        return all_symbols

    def get_dependencies(self, dependencies: List[Dependency], source_qualified_name: str) -> List[Dependency]:
        """
        Get all dependencies originating from a specific symbol.

        Args:
            dependencies: List of all dependencies
            source_qualified_name: The qualified name of the source symbol

        Returns:
            A list of dependencies originating from the given symbol.
        """
        return [dep for dep in dependencies if dep.source == source_qualified_name]

    def aggregate_dependencies(self, file_results: Dict[str, tuple[List[Symbol], List[Dependency]]]) -> List[Dependency]:
        """
        Aggregate dependencies from multiple files into a single list.

        Args:
            file_results: Dictionary mapping file paths to (symbols, dependencies)

        Returns:
            Combined list of all dependencies
        """
        all_dependencies = []
        for _, dependencies in file_results.values():
            all_dependencies.extend(dependencies)
        return all_dependencies

    # =========================================================================
    # Joern CPG-specific methods
    # =========================================================================

    def analyze_directory_cpg(
        self,
        directory: str,
        language: str | None = None,
        include_external: bool = False,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze a directory using Joern CPG analysis.

        This provides more comprehensive analysis than tree-sitter for
        supported languages, including call graphs and data flow.

        Args:
            directory: Path to directory to analyze
            language: Language hint (auto-detected if None)
            include_external: Include external/library symbols
            force_refresh: Force regeneration of CPG

        Returns:
            Dictionary with symbols, dependencies, and metadata
        """
        adapter = self.joern_adapter
        if not adapter or not adapter.is_available():
            return {
                "success": False,
                "error": "Joern is not available",
                "symbols": [],
                "dependencies": [],
            }

        try:
            result = adapter.analyze_directory(
                path=directory,
                language=language,
                include_external=include_external,
                force_refresh=force_refresh,
            )

            return {
                "success": len(result.errors) == 0,
                "symbols": result.symbols,
                "dependencies": result.dependencies,
                "files_analyzed": result.files_analyzed,
                "languages_detected": result.languages_detected,
                "cpg_path": result.cpg_path,
                "errors": result.errors,
            }

        except Exception as e:
            logger.error(f"CPG analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "symbols": [],
                "dependencies": [],
            }

    def run_cpg_query(
        self,
        path: str,
        query: str,
        output_format: str = "text",
    ) -> Dict[str, Any]:
        """
        Run a CPGQL query on source code or CPG file.

        Args:
            path: Path to source directory or CPG file
            query: CPGQL query string
            output_format: Output format (text, json)

        Returns:
            Dictionary with query results
        """
        adapter = self.joern_adapter
        if not adapter or not adapter.is_available():
            return {
                "success": False,
                "error": "Joern is not available",
                "output": "",
            }

        try:
            result = adapter.run_query(
                path=path,
                query=query,
                output_format=output_format,
            )

            return {
                "success": result.success,
                "output": result.output,
                "query": result.query,
                "execution_time_ms": result.execution_time_ms,
                "parsed_result": result.parsed_result,
            }

        except Exception as e:
            logger.error(f"CPG query failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
            }

    def export_cpg_graph(
        self,
        path: str,
        output_dir: str,
        representation: str = "all",
        format: str = "dot",
    ) -> Dict[str, Any]:
        """
        Export CPG to a visualization format.

        Args:
            path: Path to source directory or CPG file
            output_dir: Directory for exported files
            representation: Graph type (all, ast, cfg, cdg, ddg, pdg, cpg14)
            format: Output format (dot, graphml, graphson, neo4jcsv)

        Returns:
            Dictionary with export information
        """
        adapter = self.joern_adapter
        if not adapter or not adapter.is_available():
            return {
                "success": False,
                "error": "Joern is not available",
            }

        try:
            return adapter.export_graph(
                path=path,
                output_dir=output_dir,
                representation=representation,
                format=format,
            )

        except Exception as e:
            logger.error(f"CPG export failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }

    def get_joern_version(self) -> str | None:
        """Get the Joern version if available."""
        adapter = self.joern_adapter
        if adapter and adapter.is_available():
            return adapter.get_version()
        return None

    def get_joern_supported_languages(self) -> List[str]:
        """Get list of languages supported by Joern."""
        return list(self.JOERN_LANGUAGES.values())

    def get_treesitter_supported_languages(self) -> List[str]:
        """Get list of languages supported by tree-sitter."""
        return list(set(self.TREESITTER_LANGUAGES.values()))
