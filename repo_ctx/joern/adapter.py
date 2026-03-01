"""
Main Joern adapter for repo-ctx integration.

This module provides the high-level interface for using Joern
code analysis within repo-ctx.
"""

import hashlib
import logging
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any

from repo_ctx.analysis.models import Symbol, Dependency
from repo_ctx.joern.cli import JoernCLI, JoernError
from repo_ctx.joern.parser import CPGParser
from repo_ctx.joern.mapper import CPGMapper
from repo_ctx.joern import queries
from repo_ctx.joern.languages import JOERN_LANGUAGES, get_language_for_file, requires_directory

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result from Joern analysis."""

    symbols: list[Symbol] = field(default_factory=list)
    dependencies: list[Dependency] = field(default_factory=list)
    files_analyzed: int = 0
    languages_detected: list[str] = field(default_factory=list)
    cpg_path: str | None = None
    errors: list[str] = field(default_factory=list)


@dataclass
class QueryResult:
    """Result from a CPGQL query."""

    output: str
    success: bool
    query: str
    execution_time_ms: int = 0
    parsed_result: Any = None


class JoernAdapter:
    """
    High-level adapter for Joern CPG analysis.

    Provides methods for:
    - Analyzing source code directories
    - Running CPGQL queries
    - Exporting CPG graphs
    - Caching CPG files for performance
    """

    # Cache directory for CPG files
    DEFAULT_CACHE_DIR = os.path.expanduser("~/.cache/repo-ctx/cpg")

    def __init__(
        self,
        joern_path: str | None = None,
        cache_dir: str | None = None,
        timeout: int = 300,
    ):
        """
        Initialize the Joern adapter.

        Args:
            joern_path: Custom path to Joern installation.
            cache_dir: Directory for caching CPG files.
            timeout: Default timeout for Joern commands.
        """
        self._cli = JoernCLI(joern_path=joern_path, timeout=timeout)
        self._parser = CPGParser()
        self._mapper = CPGMapper()
        self._cache_dir = cache_dir or self.DEFAULT_CACHE_DIR
        self._timeout = timeout

        # Ensure cache directory exists
        os.makedirs(self._cache_dir, exist_ok=True)

    def is_available(self) -> bool:
        """
        Check if Joern is installed and accessible.

        Returns:
            True if Joern is available.
        """
        return self._cli.is_available()

    def get_version(self) -> str | None:
        """
        Get the Joern version.

        Returns:
            Version string or None.
        """
        return self._cli.get_version()

    def get_supported_languages(self) -> list[str]:
        """
        Get list of supported programming languages.

        Returns:
            List of language identifiers.
        """
        return list(JOERN_LANGUAGES.keys())

    def analyze_directory(
        self,
        path: str,
        language: str | None = None,
        include_external: bool = False,
        use_cache: bool = True,
        force_refresh: bool = False,
    ) -> AnalysisResult:
        """
        Analyze a directory of source code.

        Args:
            path: Path to source directory.
            language: Language hint (auto-detected if None).
            include_external: Include external/library symbols.
            use_cache: Use cached CPG if available.
            force_refresh: Force regeneration of CPG.

        Returns:
            AnalysisResult with extracted symbols and dependencies.
        """
        result = AnalysisResult()

        if not os.path.exists(path):
            result.errors.append(f"Path does not exist: {path}")
            return result

        # Check if Joern is available
        if not self.is_available():
            result.errors.append("Joern is not installed or not accessible")
            return result

        try:
            # Get or create CPG
            cpg_path = self._get_or_create_cpg(
                path, language, use_cache, force_refresh
            )
            result.cpg_path = cpg_path

            # Run extraction query
            query_result = self._cli.run_query(
                cpg_path=cpg_path,
                query=queries.QUERY_EXTRACT_ALL,
                timeout=self._timeout,
            )

            # Run comments query
            comments_result = self._cli.run_query(
                cpg_path=cpg_path,
                query=queries.QUERY_COMMENTS,
                timeout=self._timeout,
            )

            # Run data flow query
            data_flow_result = self._cli.run_query(
                cpg_path=cpg_path,
                query=queries.QUERY_DATA_FLOW,
                timeout=self._timeout,
            )

            # Parse the output
            parsed = self._parser.parse_output(
                query_result.output,
                comments_output=comments_result.output,
                data_flow_output=data_flow_result.output,
            )

            # Map to symbols and dependencies
            symbols, dependencies = self._mapper.map_parse_result(parsed)

            # Filter external symbols if requested
            if not include_external:
                symbols = [s for s in symbols if not s.metadata.get("is_external")]

            result.symbols = symbols
            result.dependencies = dependencies
            result.files_analyzed = len(set(s.file_path for s in symbols if s.file_path))
            result.languages_detected = list(set(
                s.language for s in symbols if s.language
            ))

        except JoernError as e:
            logger.error(f"Joern analysis failed: {e}")
            result.errors.append(str(e))

        return result

    def analyze_file(
        self,
        file_path: str,
        code: str | None = None,
    ) -> list[Symbol]:
        """
        Analyze a single source file.

        Args:
            file_path: Path to source file.
            code: Optional source code (reads file if not provided).

        Returns:
            List of extracted symbols.
        """
        if code is not None:
            # Detect language to check if it requires a directory
            language = get_language_for_file(file_path)
            ext = os.path.splitext(file_path)[1]
            filename = os.path.basename(file_path)

            if language and requires_directory(language):
                # Some frontends (like kotlin2cpg) require a directory
                tmp_dir = tempfile.mkdtemp(prefix="joern_")
                tmp_path = os.path.join(tmp_dir, filename)
                try:
                    with open(tmp_path, "w") as f:
                        f.write(code)
                    result = self.analyze_directory(tmp_dir, language=language, use_cache=False)
                    # Update file paths in symbols
                    for symbol in result.symbols:
                        if symbol.file_path == tmp_path or symbol.file_path == filename:
                            symbol.file_path = file_path
                    return result.symbols
                finally:
                    import shutil
                    shutil.rmtree(tmp_dir, ignore_errors=True)
            else:
                # Single file works for most frontends
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=ext,
                    delete=False
                ) as tmp:
                    tmp.write(code)
                    tmp_path = tmp.name

                try:
                    result = self.analyze_directory(tmp_path, use_cache=False)
                    # Update file paths in symbols
                    for symbol in result.symbols:
                        if symbol.file_path == tmp_path:
                            symbol.file_path = file_path
                    return result.symbols
                finally:
                    os.unlink(tmp_path)
        else:
            if not os.path.exists(file_path):
                return []

            # Analyze the parent directory with language detection
            language = get_language_for_file(file_path)
            result = self.analyze_directory(
                os.path.dirname(file_path) or ".",
                language=language,
                use_cache=True,
            )
            # Filter to just the requested file
            return [s for s in result.symbols if s.file_path == file_path]

    def run_query(
        self,
        path: str,
        query: str,
        output_format: str = "text",
    ) -> QueryResult:
        """
        Run a CPGQL query on source code.

        Args:
            path: Path to source code directory or CPG file.
            query: CPGQL query string.
            output_format: Output format (text, json).

        Returns:
            QueryResult with query output.
        """
        # Determine if path is a CPG file or source directory
        if path.endswith(".bin") and os.path.isfile(path):
            cpg_path = path
        else:
            # Generate or retrieve CPG
            cpg_path = self._get_or_create_cpg(path, None, True, False)

        try:
            cli_result = self._cli.run_query(
                cpg_path=cpg_path,
                query=query,
                timeout=self._timeout,
            )

            # Try to parse the result
            parsed = None
            if output_format == "text":
                parsed = self._parser.parse_simple_list(cli_result.output)

            return QueryResult(
                output=cli_result.output,
                success=cli_result.success,
                query=query,
                execution_time_ms=cli_result.execution_time_ms,
                parsed_result=parsed,
            )

        except JoernError as e:
            return QueryResult(
                output=str(e),
                success=False,
                query=query,
            )

    def export_graph(
        self,
        path: str,
        output_dir: str,
        representation: str = "all",
        format: str = "dot",
    ) -> dict[str, Any]:
        """
        Export CPG to a visualization format.

        Args:
            path: Path to source code or CPG file.
            output_dir: Directory for exported files.
            representation: Graph type (all, ast, cfg, cdg, ddg, pdg, cpg14).
            format: Output format (dot, graphml, graphson, neo4jcsv).

        Returns:
            Dictionary with export information.
        """
        # Get CPG path
        if path.endswith(".bin") and os.path.isfile(path):
            cpg_path = path
        else:
            cpg_path = self._get_or_create_cpg(path, None, True, False)

        try:
            result = self._cli.export(
                cpg_path=cpg_path,
                output_dir=output_dir,
                representation=representation,
                format=format,
                timeout=self._timeout,
            )

            return {
                "success": True,
                "output_dir": result.output_dir,
                "format": result.format,
                "representation": result.representation,
                "files": result.files_created,
                "file_count": len(result.files_created),
            }

        except JoernError as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_cpg_path(
        self,
        source_path: str,
        language: str | None = None,
        force_refresh: bool = False,
    ) -> str:
        """
        Get path to CPG file for source code.

        Creates CPG if it doesn't exist or if refresh is requested.

        Args:
            source_path: Path to source code.
            language: Language hint.
            force_refresh: Force regeneration.

        Returns:
            Path to CPG file.
        """
        return self._get_or_create_cpg(source_path, language, True, force_refresh)

    def _get_or_create_cpg(
        self,
        source_path: str,
        language: str | None,
        use_cache: bool,
        force_refresh: bool,
    ) -> str:
        """
        Get existing CPG or create new one.

        Args:
            source_path: Path to source code.
            language: Language hint.
            use_cache: Whether to use cached CPG.
            force_refresh: Force regeneration.

        Returns:
            Path to CPG file.
        """
        # Generate cache key from source path
        abs_path = os.path.abspath(source_path)
        cache_key = hashlib.md5(abs_path.encode()).hexdigest()
        cpg_path = os.path.join(self._cache_dir, f"{cache_key}.bin")

        # Check cache
        if use_cache and not force_refresh and os.path.exists(cpg_path):
            # Check if CPG is newer than source
            cpg_mtime = os.path.getmtime(cpg_path)
            source_mtime = self._get_latest_mtime(source_path)

            if cpg_mtime > source_mtime:
                logger.debug(f"Using cached CPG: {cpg_path}")
                return cpg_path

        # Create new CPG
        logger.info(f"Creating CPG for: {source_path}")
        result = self._cli.parse(
            input_path=source_path,
            output_path=cpg_path,
            language=language,
            timeout=self._timeout,
        )

        return result.cpg_path

    def _get_latest_mtime(self, path: str) -> float:
        """Get the latest modification time in a directory."""
        if os.path.isfile(path):
            return os.path.getmtime(path)

        latest = 0.0
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                mtime = os.path.getmtime(file_path)
                if mtime > latest:
                    latest = mtime

        return latest

    def clear_cache(self, source_path: str | None = None) -> int:
        """
        Clear cached CPG files.

        Args:
            source_path: Clear cache for specific path (all if None).

        Returns:
            Number of files removed.
        """
        if source_path:
            abs_path = os.path.abspath(source_path)
            cache_key = hashlib.md5(abs_path.encode()).hexdigest()
            cpg_path = os.path.join(self._cache_dir, f"{cache_key}.bin")

            if os.path.exists(cpg_path):
                os.unlink(cpg_path)
                return 1
            return 0
        else:
            count = 0
            for file in os.listdir(self._cache_dir):
                if file.endswith(".bin"):
                    os.unlink(os.path.join(self._cache_dir, file))
                    count += 1
            return count
