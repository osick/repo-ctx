"""LLM-enhanced file documentation with source code context."""
import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable, TYPE_CHECKING

from .prompts import (
    format_file_enhancement_prompt,
    parse_file_enhancement_response,
)

if TYPE_CHECKING:
    from repo_ctx.services.llm import LLMService

logger = logging.getLogger("repo_ctx.analysis.file_enhancer")

# Progress callback type: (current_file, current_index, total_files)
ProgressCallback = Callable[[str, int, int], None]


class FileEnhancer:
    """Enhances symbol documentation using LLM with full source code context.

    This class:
    1. Reads the actual source file for context
    2. Sends one LLM request per file (not per symbol)
    3. Gets structured JSON response with all symbol docs
    4. Updates symbols with enhanced documentation
    """

    MAX_CODE_CHARS = 12000  # ~3000 tokens of code
    MAX_RETRIES = 3  # Maximum attempts for empty LLM responses
    RETRY_DELAY = 1.0  # Seconds to wait between retries

    def __init__(
        self,
        llm_service: Optional["LLMService"] = None,
        source_root: Optional[Path] = None,
    ):
        """Initialize the enhancer.

        Args:
            llm_service: LLM service for documentation enhancement.
            source_root: Root path to source files (for reading source code).
        """
        self.llm_service = llm_service
        self.source_root = source_root

    async def enhance_file(
        self,
        file_path: str,
        symbols: list[dict],
        language: str = "unknown",
        include_private: bool = False,
    ) -> dict:
        """Enhance a file's symbols using LLM with source code context.

        Args:
            file_path: Path to the source file (relative to source_root).
            symbols: List of symbol dictionaries from analysis.
            language: Programming language.
            include_private: Whether to document private symbols.

        Returns:
            Dictionary with file path, documentation, and enhanced symbols.
        """
        if not self.llm_service:
            # No LLM service - return original data
            return {
                "file": file_path,
                "documentation": None,
                "symbols": symbols,
            }

        # Filter symbols if needed
        symbols_to_enhance = symbols
        if not include_private:
            symbols_to_enhance = [
                s for s in symbols
                if not s.get("name", "").startswith("_")
                or s.get("name", "").startswith("__") and s.get("name", "").endswith("__")
            ]

        # Read source file
        source_code = self._read_source_file(file_path)
        if not source_code:
            logger.warning(f"Could not read source file: {file_path}")
            return {
                "file": file_path,
                "documentation": None,
                "symbols": symbols,
            }

        # Build and send prompt
        prompt = format_file_enhancement_prompt(
            file_path=file_path,
            language=language,
            source_code=source_code,
            symbols=symbols_to_enhance,
            max_code_chars=self.MAX_CODE_CHARS,
        )

        # Retry loop for empty LLM responses
        last_error_msg = ""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await self.llm_service._complete(prompt)
                if response.content:
                    # Success - parse and return
                    result = parse_file_enhancement_response(response.content)
                    enhanced_symbols = self._apply_enhancements(symbols, result["symbols"])
                    return {
                        "file": file_path,
                        "documentation": result["file_documentation"],
                        "symbols": enhanced_symbols,
                    }

                # Empty response - check for error details
                if hasattr(response, "metadata") and response.metadata:
                    last_error_msg = response.metadata.get("error", "")

                if attempt < self.MAX_RETRIES:
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for {file_path}: {last_error_msg} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    else:
                        logger.warning(f"Empty LLM response for {file_path} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    # Final attempt failed
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for {file_path}: {last_error_msg} (all {self.MAX_RETRIES} attempts failed)")
                    else:
                        logger.warning(f"Empty LLM response for {file_path} (all {self.MAX_RETRIES} attempts failed - possible rate limit)")

            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Failed to enhance file {file_path}: {e} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    logger.warning(f"Failed to enhance file {file_path}: {e} (all {self.MAX_RETRIES} attempts failed)")

        # All retries exhausted
        return {
            "file": file_path,
            "documentation": None,
            "symbols": symbols,
        }

    def _read_source_file(self, file_path: str) -> Optional[str]:
        """Read source file content.

        Args:
            file_path: Path to the source file.

        Returns:
            Source code content or None if not readable.
        """
        # Try different path resolutions
        paths_to_try = []

        if self.source_root:
            paths_to_try.append(self.source_root / file_path)

        # Also try absolute path
        paths_to_try.append(Path(file_path))

        for path in paths_to_try:
            if path.exists() and path.is_file():
                try:
                    return path.read_text(encoding="utf-8")
                except Exception as e:
                    logger.debug(f"Could not read {path}: {e}")
                    continue

        return None

    def _apply_enhancements(
        self,
        symbols: list[dict],
        enhancements: dict[str, str],
    ) -> list[dict]:
        """Apply LLM-generated documentation to symbols.

        Args:
            symbols: Original symbol list.
            enhancements: Dict mapping symbol name to new documentation.

        Returns:
            List of symbols with updated documentation.
        """
        enhanced = []
        for symbol in symbols:
            name = symbol.get("name", "")
            if name in enhancements:
                new_doc = enhancements[name]
                if new_doc:
                    symbol = symbol.copy()
                    symbol["documentation"] = new_doc
            enhanced.append(symbol)
        return enhanced

    async def enhance_files(
        self,
        files_data: list[dict],
        progress_callback: Optional[ProgressCallback] = None,
    ) -> list[dict]:
        """Enhance multiple files with progress reporting (sequential).

        Args:
            files_data: List of file data dicts with 'file', 'symbols', 'language'.
            progress_callback: Optional callback(file_path, current, total).

        Returns:
            List of enhanced file data dicts.
        """
        total = len(files_data)
        results = []

        for i, file_data in enumerate(files_data):
            file_path = file_data.get("file", "")

            if progress_callback:
                progress_callback(file_path, i + 1, total)

            enhanced = await self.enhance_file(
                file_path=file_path,
                symbols=file_data.get("symbols", []),
                language=file_data.get("language", "unknown"),
            )
            results.append(enhanced)

        return results

    async def enhance_files_parallel(
        self,
        files_data: list[dict],
        max_concurrency: int = 5,
        progress_callback: Optional[ProgressCallback] = None,
        include_private: bool = False,
    ) -> list[dict]:
        """Enhance multiple files in parallel with controlled concurrency.

        Args:
            files_data: List of file data dicts with 'file', 'symbols', 'language'.
            max_concurrency: Maximum number of concurrent LLM requests.
            progress_callback: Optional callback(file_path, completed_count, total).
            include_private: Whether to document private symbols.

        Returns:
            List of enhanced file data dicts (in same order as input).
        """
        if not files_data:
            return []

        total = len(files_data)
        semaphore = asyncio.Semaphore(max_concurrency)
        completed_count = 0
        results_lock = asyncio.Lock()

        async def enhance_with_semaphore(index: int, file_data: dict) -> tuple[int, dict]:
            """Enhance a single file with semaphore control."""
            nonlocal completed_count

            async with semaphore:
                file_path = file_data.get("file", "")
                enhanced = await self.enhance_file(
                    file_path=file_path,
                    symbols=file_data.get("symbols", []),
                    language=file_data.get("language", "unknown"),
                    include_private=include_private,
                )

                # Update progress atomically
                async with results_lock:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(file_path, completed_count, total)

                return index, enhanced

        # Create all tasks
        tasks = [
            enhance_with_semaphore(i, file_data)
            for i, file_data in enumerate(files_data)
        ]

        # Run all tasks concurrently (semaphore limits actual parallelism)
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        # Sort results by original index and handle any exceptions
        results = [None] * total
        for item in completed:
            if isinstance(item, Exception):
                logger.error(f"Task failed with exception: {item}")
                continue
            index, enhanced = item
            results[index] = enhanced

        # Replace any None values (from exceptions) with empty enhancement
        for i, result in enumerate(results):
            if result is None:
                file_path = files_data[i].get("file", "")
                results[i] = {
                    "file": file_path,
                    "documentation": None,
                    "symbols": files_data[i].get("symbols", []),
                }

        return results
