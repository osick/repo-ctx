"""Dump service for exporting repository analysis.

This module provides functionality to dump analyzed repository context
to a .repo-ctx directory with configurable completeness levels.
Optionally uses LLM to generate business-level summaries.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING

from repo_ctx import __version__
from repo_ctx.services.base import BaseService, ServiceContext
from repo_ctx.progress import (
    ProgressCallback,
    ProgressReporter,
    NoOpProgressCallback,
    ProgressPhase,
)

if TYPE_CHECKING:
    from repo_ctx.services.llm import LLMService

logger = logging.getLogger("repo_ctx.services.dump")


class DumpLevel(Enum):
    """Completeness level for dump output."""

    COMPACT = "compact"   # metadata, llms.txt, symbol index only
    MEDIUM = "medium"     # + docs, architecture, metrics
    FULL = "full"         # + per-file symbols, full API docs


@dataclass
class GitInfo:
    """Git repository information."""

    commit: str = ""
    short_commit: str = ""
    tag: Optional[str] = None
    branch: str = ""
    dirty: bool = False
    remote_url: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "commit": self.commit,
            "short_commit": self.short_commit,
            "tag": self.tag,
            "branch": self.branch,
            "dirty": self.dirty,
            "remote_url": self.remote_url,
        }


@dataclass
class DumpMetadata:
    """Metadata for dump output."""

    version: str = "1.0"
    repo_ctx_version: str = __version__
    generated_at: str = ""
    level: str = "medium"
    git: GitInfo = field(default_factory=GitInfo)
    repository: dict[str, Any] = field(default_factory=dict)
    stats: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "repo_ctx_version": self.repo_ctx_version,
            "generated_at": self.generated_at,
            "level": self.level,
            "git": self.git.to_dict(),
            "repository": self.repository,
            "stats": self.stats,
        }


@dataclass
class DumpResult:
    """Result of a dump operation."""

    success: bool
    output_path: Path
    level: DumpLevel
    files_created: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    metadata: Optional[DumpMetadata] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "output_path": str(self.output_path),
            "level": self.level.value,
            "files_created": self.files_created,
            "errors": self.errors,
            "metadata": self.metadata.to_dict() if self.metadata else None,
        }


class DumpService(BaseService):
    """Service for dumping repository analysis to filesystem.

    Exports analyzed repository context to a .repo-ctx directory
    with configurable completeness levels. Optionally uses LLM to
    generate business-level summaries.
    """

    DUMP_DIR_NAME = ".repo-ctx"

    # Prompt for generating business summary
    BUSINESS_SUMMARY_PROMPT = """Analyze this codebase and provide a concise business-level summary.

Repository: {repo_name}
Languages: {languages}
Total Files: {file_count}
Total Symbols: {symbol_count}

Key Classes:
{classes}

Key Functions:
{functions}

Sample Code Structure:
{structure}

Provide a summary covering:
1. **Purpose**: What does this project do? (1-2 sentences)
2. **Target Users**: Who would use this? (developers, end-users, etc.)
3. **Key Features**: Main capabilities (3-5 bullet points)
4. **Architecture**: High-level design (e.g., CLI tool, web service, library)
5. **Tech Stack**: Key technologies and frameworks detected

Respond in Markdown format, keep it under 500 words. Focus on WHAT the project does, not implementation details."""

    def __init__(
        self,
        context: ServiceContext,
        llm_service: Optional["LLMService"] = None,
    ):
        """Initialize dump service.

        Args:
            context: Service context with storage and config.
            llm_service: Optional LLM service for generating business summaries.
        """
        super().__init__(context)
        self._analyzer = None
        self._architecture_analyzer = None
        self._llm_service = llm_service

    def _get_git_info(self, repo_path: Path) -> GitInfo:
        """Get git information for a repository.

        Args:
            repo_path: Path to git repository.

        Returns:
            GitInfo with commit, tag, branch info.
        """
        try:
            from git import Repo, InvalidGitRepositoryError
        except ImportError:
            logger.warning("GitPython not available, skipping git info")
            return GitInfo()

        try:
            repo = Repo(str(repo_path))
        except InvalidGitRepositoryError:
            logger.warning(f"Not a git repository: {repo_path}")
            return GitInfo()

        info = GitInfo()

        try:
            # Get commit info
            if not repo.head.is_detached:
                info.branch = repo.active_branch.name
            info.commit = repo.head.commit.hexsha
            info.short_commit = repo.head.commit.hexsha[:7]
            info.dirty = repo.is_dirty()

            # Get tag if on tagged commit
            for tag in repo.tags:
                if tag.commit == repo.head.commit:
                    info.tag = tag.name
                    break

            # Get remote URL
            if repo.remotes:
                try:
                    info.remote_url = repo.remotes.origin.url
                except Exception:
                    pass

        except Exception as e:
            logger.warning(f"Error getting git info: {e}")

        return info

    def _ensure_output_dir(
        self,
        output_path: Path,
        force: bool = False
    ) -> Path:
        """Ensure output directory exists and is writable.

        Args:
            output_path: Path to output directory.
            force: If True, overwrite existing directory.

        Returns:
            Path to output directory.

        Raises:
            FileExistsError: If directory exists and force=False.
        """
        if output_path.exists():
            if not force:
                raise FileExistsError(
                    f"Output directory already exists: {output_path}. "
                    "Use --force to overwrite."
                )
            # Clear existing directory
            import shutil
            shutil.rmtree(output_path)

        output_path.mkdir(parents=True, exist_ok=True)
        return output_path

    def _write_json(
        self,
        path: Path,
        data: Any,
        indent: int = 2
    ) -> None:
        """Write JSON data to file.

        Args:
            path: Output file path.
            data: Data to serialize.
            indent: JSON indentation level.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, default=str)

    def _write_text(self, path: Path, content: str) -> None:
        """Write text content to file.

        Args:
            path: Output file path.
            content: Text content to write.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    async def dump(
        self,
        source_path: Path,
        output_path: Optional[Path] = None,
        level: DumpLevel = DumpLevel.MEDIUM,
        force: bool = False,
        include_private: bool = False,
        progress: Optional[ProgressCallback] = None,
        exclude_patterns: Optional[list[str]] = None,
        persist_to_graph: bool = False,
        skip_joern: bool = False,
    ) -> DumpResult:
        """Dump repository analysis to filesystem.

        Args:
            source_path: Path to repository to analyze/dump.
            output_path: Output directory (default: source_path/.repo-ctx).
            level: Completeness level for output.
            force: Overwrite existing output directory.
            include_private: Include private symbols.
            progress: Optional progress callback for status updates.
            exclude_patterns: Glob patterns for files/dirs to exclude.
            persist_to_graph: Persist analysis to Neo4j graph database.
            skip_joern: Skip Joern analysis (use tree-sitter only). Use when
                Joern runs out of memory on large C/C++ codebases.

        Returns:
            DumpResult with status and file list.
        """
        source_path = Path(source_path).resolve()

        if output_path is None:
            output_path = source_path / self.DUMP_DIR_NAME
        else:
            output_path = Path(output_path).resolve()

        result = DumpResult(
            success=False,
            output_path=output_path,
            level=level,
        )

        try:
            # Ensure output directory
            self._ensure_output_dir(output_path, force=force)

            # Get git info
            git_info = self._get_git_info(source_path)

            if git_info.dirty:
                logger.warning(
                    "Working directory has uncommitted changes. "
                    "Dump may not match any specific commit."
                )

            # Analyze repository if needed
            symbols, dependencies = await self._analyze_repository(
                source_path,
                include_private=include_private,
                progress=progress,
                exclude_patterns=exclude_patterns,
                skip_joern=skip_joern,
            )

            # Create metadata
            metadata = DumpMetadata(
                generated_at=datetime.now(timezone.utc).isoformat(),
                level=level.value,
                git=git_info,
                repository={
                    "name": source_path.name,
                    "path": str(source_path),
                },
                stats={
                    "symbols_extracted": len(symbols),
                    "dependencies": len(dependencies),
                },
            )

            # Generate outputs based on level
            files_created = []

            # Collect documentation from README and docs/*.md
            if progress:
                await progress.report(
                    operation="dump",
                    phase=ProgressPhase.PROCESSING,
                    current=0,
                    total=1,
                    message="Collecting documentation",
                    detail="Reading README and docs/...",
                )
            documentation = self._collect_documentation(source_path, exclude_patterns)
            logger.info(f"Collected {len(documentation)} documentation files")

            # Generate business summary if LLM available
            business_summary = None
            if self._llm_service is not None:
                logger.info("Generating LLM-powered business summary...")
                if progress:
                    await progress.report(
                        operation="dump",
                        phase=ProgressPhase.PROCESSING,
                        current=0,
                        total=1,
                        message="Generating business summary",
                        detail="Calling LLM...",
                    )
                business_summary = await self._generate_business_summary(
                    source_path, symbols
                )

            # Always: metadata.json
            metadata.stats["documentation_files"] = len(documentation)
            self._write_json(output_path / "metadata.json", metadata.to_dict())
            files_created.append("metadata.json")

            # Always: symbols/index.json
            symbol_index = self._generate_symbol_index(symbols)
            self._write_json(output_path / "symbols" / "index.json", symbol_index)
            files_created.append("symbols/index.json")

            # Architecture data (generated for MEDIUM/FULL, empty for COMPACT)
            arch_data = None

            if level in (DumpLevel.MEDIUM, DumpLevel.FULL):
                # architecture/
                arch_files, arch_data = await self._generate_architecture(
                    output_path / "architecture",
                    symbols,
                    dependencies,
                )
                files_created.extend(arch_files)

                # metrics/complexity.json
                metrics = self._generate_metrics(symbols)
                self._write_json(output_path / "metrics" / "complexity.json", metrics)
                files_created.append("metrics/complexity.json")

            # Always: llms.txt (with business summary, documentation, and architecture)
            llms_txt = self._generate_llms_txt(
                source_path, symbols, git_info,
                business_summary=business_summary,
                documentation=documentation,
                architecture=arch_data,
            )
            self._write_text(output_path / "llms.txt", llms_txt)
            files_created.append("llms.txt")

            if level == DumpLevel.FULL:
                # symbols/by-file/
                by_file_files = self._generate_symbols_by_file(
                    output_path / "symbols" / "by-file",
                    symbols,
                )
                files_created.extend(by_file_files)

            # Persist to graph database if requested
            graph_stats = {"nodes": 0, "relationships": 0}
            if persist_to_graph:
                if progress:
                    await progress.report(
                        operation="dump",
                        phase=ProgressPhase.PROCESSING,
                        current=0,
                        total=1,
                        message="Persisting to graph database",
                        detail="Creating nodes and relationships...",
                    )

                # Create library_id from repo info
                library_id = self._create_library_id(source_path, git_info)

                # Convert dependencies to dicts for graph storage
                dep_dicts = self._convert_dependencies_to_dicts(dependencies)

                # Persist to graph
                graph_stats = await self._persist_to_graph(
                    library_id=library_id,
                    symbols=symbols,
                    dependencies=dep_dicts,
                )
                logger.info(
                    f"Persisted to graph: {graph_stats['nodes']} nodes, "
                    f"{graph_stats['relationships']} relationships"
                )

            # Add graph stats to metadata
            metadata.stats["graph_nodes"] = graph_stats["nodes"]
            metadata.stats["graph_relationships"] = graph_stats["relationships"]

            result.success = True
            result.files_created = files_created
            result.metadata = metadata

        except Exception as e:
            logger.error(f"Dump failed: {e}")
            result.errors.append(str(e))

        return result

    # Default directories to exclude from analysis
    DEFAULT_EXCLUDES = {
        'node_modules', 'venv', '.venv', '__pycache__', 'dist', 'build',
        '.git', '.hg', '.svn', 'vendor', 'target', 'bin', 'obj',
        '.tox', '.nox', '.mypy_cache', '.pytest_cache', '.ruff_cache',
        'coverage', '.coverage', 'htmlcov', '.eggs', '*.egg-info',
    }

    async def _analyze_repository(
        self,
        source_path: Path,
        include_private: bool = False,
        progress: Optional[ProgressCallback] = None,
        exclude_patterns: Optional[list[str]] = None,
        skip_joern: bool = False,
    ) -> tuple[list[dict], list[str]]:
        """Analyze repository and extract symbols.

        Args:
            source_path: Path to repository.
            include_private: Include private symbols.
            progress: Optional progress callback.
            exclude_patterns: Additional patterns to exclude (glob patterns).
            skip_joern: Skip Joern analysis, use tree-sitter only.

        Returns:
            Tuple of (symbols, dependencies).
        """
        from repo_ctx.analysis import CodeAnalyzer
        import fnmatch

        # Build exclude set first (needed for scanning)
        excludes = self.DEFAULT_EXCLUDES.copy()
        if exclude_patterns:
            excludes.update(exclude_patterns)

        def should_exclude(path: Path) -> bool:
            """Check if path should be excluded."""
            rel_path = str(path.relative_to(source_path))
            parts = path.parts

            # Check directory parts
            for part in parts:
                if part.startswith('.'):
                    return True
                if part in excludes:
                    return True

            # Check glob patterns
            for pattern in excludes:
                if '*' in pattern or '?' in pattern:
                    if fnmatch.fnmatch(rel_path, pattern):
                        return True
            return False

        if self._analyzer is None:
            # If skip_joern is set, force tree-sitter mode regardless of file types
            if skip_joern:
                logger.info("Joern analysis skipped (--skip-joern flag). Using tree-sitter only.")
                self._analyzer = CodeAnalyzer(use_treesitter=True)
            else:
                # Detect if we need Joern for any files in this repository
                # Swift is the only language that's truly Joern-only (tree-sitter-swift is very old)
                joern_only_exts = {'.swift'}

                # Quick scan to detect Joern-only files
                needs_joern = False
                for ext in joern_only_exts:
                    for path in source_path.rglob(f"*{ext}"):
                        if not should_exclude(path):
                            needs_joern = True
                            logger.info(f"Found {ext} files, will use Joern for analysis")
                            break
                    if needs_joern:
                        break

                if needs_joern:
                    # Use Joern for Swift (or other Joern-only languages)
                    self._analyzer = CodeAnalyzer(use_treesitter=False)
                    if not self._analyzer.is_joern_available():
                        logger.warning(
                            "Swift files detected but Joern is not available. "
                            "Install Joern for Swift support. Falling back to tree-sitter."
                        )
                        self._analyzer = CodeAnalyzer(use_treesitter=True)
                else:
                    # Use tree-sitter (fast, supports Python/JS/Java/C/C++/Go/Rust/Ruby/PHP/C#/etc.)
                    self._analyzer = CodeAnalyzer(use_treesitter=True)

        # Find code files - use supported_extensions from the chosen analyzer
        # Use ABSOLUTE paths for proper Joern support
        code_files = {}
        for ext in self._analyzer.supported_extensions:
            for path in source_path.rglob(f"*{ext}"):
                if should_exclude(path):
                    continue
                try:
                    # Use absolute paths for Joern compatibility
                    abs_path = str(path.resolve())
                    code_files[abs_path] = path.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

        # Report start of analysis
        total_files = len(code_files)
        if progress:
            await progress.report(
                operation="analyze",
                phase=ProgressPhase.INIT,
                current=0,
                total=total_files,
                message=f"Analyzing {total_files} files",
            )

        # Analyze files using bulk analysis (better Joern support)
        all_symbols = []
        all_dependencies = []
        seen_deps = set()  # Track unique dependencies by (source, target, type)

        # Use analyze_files for bulk processing (handles Joern properly)
        if progress:
            await progress.report(
                operation="analyze",
                phase=ProgressPhase.PROCESSING,
                current=0,
                total=total_files,
                message="Analyzing files (bulk mode)",
                detail=f"Processing {total_files} files...",
            )

        try:
            results = self._analyzer.analyze_files(code_files)

            for idx, (file_path, (symbols, deps)) in enumerate(results.items()):
                # Report progress
                if progress and idx % 10 == 0:  # Report every 10 files
                    await progress.report(
                        operation="analyze",
                        phase=ProgressPhase.PROCESSING,
                        current=idx + 1,
                        total=total_files,
                        message="Processing analysis results",
                        detail=Path(file_path).name,
                    )

                # Convert file path back to relative for storage
                try:
                    rel_path = str(Path(file_path).relative_to(source_path.resolve()))
                except ValueError:
                    rel_path = file_path  # Keep as-is if not under source_path

                for sym in symbols:
                    # Filter private if needed
                    if not include_private and sym.visibility == "private":
                        continue

                    # Update file_path to relative
                    sym_file_path = rel_path
                    if sym.file_path:
                        try:
                            sym_file_path = str(Path(sym.file_path).relative_to(source_path.resolve()))
                        except ValueError:
                            sym_file_path = sym.file_path

                    all_symbols.append({
                        "name": sym.name,
                        "qualified_name": sym.qualified_name,
                        "type": sym.symbol_type.value,
                        "file_path": sym_file_path,
                        "line_start": sym.line_start,
                        "line_end": sym.line_end,
                        "signature": sym.signature,
                        "visibility": sym.visibility,
                        "documentation": sym.documentation,
                    })

                # Add dependencies (deduplicate by key fields)
                for dep in deps:
                    # Convert absolute paths to relative paths
                    dep_source = getattr(dep, 'source', '')
                    dep_target = getattr(dep, 'target', '')
                    try:
                        dep_source = str(Path(dep_source).relative_to(source_path.resolve()))
                    except ValueError:
                        pass  # Keep as-is if not under source_path
                    try:
                        dep_target = str(Path(dep_target).relative_to(source_path.resolve()))
                    except ValueError:
                        pass  # Keep as-is if not under source_path

                    # Create hashable key from dependency
                    dep_key = (dep_source, dep_target, getattr(dep, 'dependency_type', ''))
                    if dep_key not in seen_deps:
                        seen_deps.add(dep_key)
                        # Create a new dependency with relative paths
                        from repo_ctx.analysis.models import Dependency
                        all_dependencies.append(Dependency(
                            source=dep_source,
                            target=dep_target,
                            dependency_type=getattr(dep, 'dependency_type', 'import'),
                            file_path=dep_source,
                        ))

        except Exception as e:
            logger.warning(f"Bulk analysis failed: {e}, falling back to individual file analysis")
            # Fallback to individual file analysis
            for idx, (file_path, code) in enumerate(code_files.items()):
                if progress:
                    await progress.report(
                        operation="analyze",
                        phase=ProgressPhase.PROCESSING,
                        current=idx + 1,
                        total=total_files,
                        message="Analyzing files (fallback mode)",
                        detail=Path(file_path).name,
                    )
                try:
                    symbols, deps = self._analyzer.analyze_file(code, file_path)
                    rel_path = str(Path(file_path).relative_to(source_path.resolve()))
                    for sym in symbols:
                        if not include_private and sym.visibility == "private":
                            continue
                        all_symbols.append({
                            "name": sym.name,
                            "qualified_name": sym.qualified_name,
                            "type": sym.symbol_type.value,
                            "file_path": rel_path,
                            "line_start": sym.line_start,
                            "line_end": sym.line_end,
                            "signature": sym.signature,
                            "visibility": sym.visibility,
                            "documentation": sym.documentation,
                        })
                    for dep in deps:
                        # Convert absolute paths to relative paths
                        dep_source = getattr(dep, 'source', '')
                        dep_target = getattr(dep, 'target', '')
                        try:
                            dep_source = str(Path(dep_source).relative_to(source_path.resolve()))
                        except ValueError:
                            pass  # Keep as-is if not under source_path
                        try:
                            dep_target = str(Path(dep_target).relative_to(source_path.resolve()))
                        except ValueError:
                            pass  # Keep as-is if not under source_path

                        dep_key = (dep_source, dep_target, getattr(dep, 'dependency_type', ''))
                        if dep_key not in seen_deps:
                            seen_deps.add(dep_key)
                            # Create a new dependency with relative paths
                            from repo_ctx.analysis.models import Dependency
                            all_dependencies.append(Dependency(
                                source=dep_source,
                                target=dep_target,
                                dependency_type=getattr(dep, 'dependency_type', 'import'),
                                file_path=rel_path,
                            ))
                except Exception as e:
                    logger.warning(f"Error analyzing {file_path}: {e}")

        # Report completion
        if progress:
            await progress.report(
                operation="analyze",
                phase=ProgressPhase.COMPLETE,
                current=total_files,
                total=total_files,
                message=f"Analyzed {total_files} files, found {len(all_symbols)} symbols",
            )

        return all_symbols, all_dependencies

    async def _generate_business_summary(
        self,
        source_path: Path,
        symbols: list[dict],
    ) -> Optional[str]:
        """Generate business-level summary using LLM.

        Args:
            source_path: Repository path.
            symbols: Extracted symbols.

        Returns:
            Business summary markdown or None if LLM unavailable.
        """
        if self._llm_service is None:
            logger.debug("No LLM service configured, skipping business summary")
            return None

        try:
            # Prepare context for the prompt
            classes = [s for s in symbols if s.get("type") == "class"]
            functions = [s for s in symbols if s.get("type") == "function"]
            files = set(s.get("file_path", "") for s in symbols if s.get("file_path"))

            # Detect languages from file extensions
            languages = set()
            for f in files:
                ext = Path(f).suffix.lower()
                lang_map = {
                    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                    ".java": "Java", ".kt": "Kotlin", ".go": "Go",
                    ".rs": "Rust", ".rb": "Ruby", ".php": "PHP",
                    ".cs": "C#", ".cpp": "C++", ".c": "C",
                    ".swift": "Swift", ".st": "Smalltalk",
                }
                if ext in lang_map:
                    languages.add(lang_map[ext])

            # Build class/function summaries
            class_summary = "\n".join([
                f"- {c['qualified_name']}: {(c.get('documentation') or 'No docs')[:100]}"
                for c in classes[:15]
            ]) or "No classes found"

            func_summary = "\n".join([
                f"- {f['qualified_name']}: {(f.get('documentation') or 'No docs')[:100]}"
                for f in functions[:15]
            ]) or "No functions found"

            # Build file structure (simplified)
            dirs = set()
            for f in files:
                parts = Path(f).parts
                if len(parts) > 1:
                    dirs.add(parts[0])
            structure = "\n".join([f"- {d}/" for d in sorted(dirs)[:10]]) or "Flat structure"

            # Create prompt
            prompt = self.BUSINESS_SUMMARY_PROMPT.format(
                repo_name=source_path.name,
                languages=", ".join(sorted(languages)) or "Unknown",
                file_count=len(files),
                symbol_count=len(symbols),
                classes=class_summary,
                functions=func_summary,
                structure=structure,
            )

            # Call LLM
            response = await self._llm_service._complete(
                prompt=prompt,
                system_prompt="You are a technical writer analyzing codebases. Provide clear, concise summaries that help developers quickly understand what a project does.",
            )

            if response.content:
                logger.info(f"Generated business summary ({response.total_tokens} tokens)")
                return response.content.strip()
            else:
                logger.warning("LLM returned empty response for business summary")
                return None

        except Exception as e:
            logger.warning(f"Failed to generate business summary: {e}")
            return None

    def _collect_documentation(
        self,
        source_path: Path,
        exclude_patterns: Optional[list[str]] = None,
    ) -> dict[str, str]:
        """Collect documentation from README and docs/*.md.

        Args:
            source_path: Repository path.
            exclude_patterns: Glob patterns for files/dirs to exclude.

        Returns:
            Dictionary mapping file names to content.
        """
        import fnmatch

        # Build exclude set for documentation
        excludes = self.DEFAULT_EXCLUDES.copy()
        if exclude_patterns:
            excludes.update(exclude_patterns)

        def should_exclude(path: Path) -> bool:
            """Check if path should be excluded."""
            rel_path = str(path.relative_to(source_path))
            parts = path.parts

            # Check directory parts
            for part in parts:
                if part.startswith('.'):
                    return True
                if part in excludes:
                    return True

            # Check glob patterns
            for pattern in excludes:
                if '*' in pattern or '?' in pattern:
                    if fnmatch.fnmatch(rel_path, pattern):
                        return True
            return False

        docs = {}

        # Read README files (various naming conventions)
        readme_names = ["README.md", "readme.md", "README.MD", "README", "readme"]
        for name in readme_names:
            readme_path = source_path / name
            if readme_path.exists() and readme_path.is_file():
                try:
                    content = readme_path.read_text(encoding='utf-8', errors='ignore')
                    docs["README.md"] = content
                    break
                except Exception as e:
                    logger.warning(f"Could not read {readme_path}: {e}")

        # Read docs/*.md files
        docs_dirs = ["docs", "doc", "documentation"]
        for docs_dir in docs_dirs:
            docs_path = source_path / docs_dir
            if docs_path.exists() and docs_path.is_dir():
                for md_file in docs_path.rglob("*.md"):
                    # Skip hidden files and large files
                    if md_file.name.startswith("."):
                        continue
                    # Check exclude patterns
                    if should_exclude(md_file):
                        logger.debug(f"Excluding doc file by pattern: {md_file}")
                        continue
                    try:
                        # Skip files larger than 100KB to avoid bloat
                        if md_file.stat().st_size > 100 * 1024:
                            logger.debug(f"Skipping large doc file: {md_file}")
                            continue
                        content = md_file.read_text(encoding='utf-8', errors='ignore')
                        rel_path = str(md_file.relative_to(source_path))
                        docs[rel_path] = content
                    except Exception as e:
                        logger.warning(f"Could not read {md_file}: {e}")

        # Also check for CLAUDE.md (common for AI-assisted repos)
        claude_md = source_path / "CLAUDE.md"
        if claude_md.exists():
            try:
                docs["CLAUDE.md"] = claude_md.read_text(encoding='utf-8', errors='ignore')
            except Exception:
                pass

        return docs

    def _extract_readme_summary(self, readme_content: str) -> str:
        """Extract key information from README.

        Args:
            readme_content: Full README content.

        Returns:
            Summarized README content (first 1500 chars or first sections).
        """
        lines = readme_content.split('\n')
        summary_lines = []
        in_code_block = False
        char_count = 0
        max_chars = 2000

        for line in lines:
            # Track code blocks to skip them
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            # Skip empty lines at start
            if not summary_lines and not line.strip():
                continue

            # Stop at installation/setup sections (keep overview only)
            if line.strip().lower().startswith(("## install", "## setup", "## getting started",
                                                 "## requirements", "## prerequisites")):
                break

            summary_lines.append(line)
            char_count += len(line)

            if char_count >= max_chars:
                break

        return '\n'.join(summary_lines).strip()

    def _generate_llms_txt(
        self,
        source_path: Path,
        symbols: list[dict],
        git_info: GitInfo,
        business_summary: Optional[str] = None,
        documentation: Optional[dict[str, str]] = None,
        architecture: Optional[dict] = None,
    ) -> str:
        """Generate llms.txt summary.

        Args:
            source_path: Repository path.
            symbols: Extracted symbols.
            git_info: Git information.
            business_summary: Optional LLM-generated business summary.
            documentation: Optional documentation files content.
            architecture: Optional architecture data with mermaid diagrams.

        Returns:
            llms.txt content.
        """
        lines = [
            f"# {source_path.name}",
            "",
        ]

        if git_info.tag:
            lines.append(f"> Version: {git_info.tag}")
        elif git_info.short_commit:
            lines.append(f"> Commit: {git_info.short_commit}")

        if git_info.branch:
            lines.append(f"> Branch: {git_info.branch}")

        lines.append("")

        # Include business summary if available (LLM-generated)
        if business_summary:
            lines.append(business_summary)
            lines.append("")
            lines.append("---")
            lines.append("")

        # Include README summary (project overview from documentation)
        documentation = documentation or {}
        if "README.md" in documentation:
            readme_summary = self._extract_readme_summary(documentation["README.md"])
            if readme_summary:
                lines.append("## Project Overview")
                lines.append("")
                lines.append(readme_summary)
                lines.append("")
                lines.append("---")
                lines.append("")

        # Include CLAUDE.md if present (AI-specific instructions)
        if "CLAUDE.md" in documentation:
            claude_content = documentation["CLAUDE.md"]
            # Extract first 1500 chars
            if len(claude_content) > 1500:
                claude_content = claude_content[:1500] + "\n\n*[Content truncated - see docs/CLAUDE.md for full content]*"
            lines.append("## Developer Notes (CLAUDE.md)")
            lines.append("")
            lines.append(claude_content)
            lines.append("")
            lines.append("---")
            lines.append("")

        # List available documentation
        doc_files = [k for k in documentation.keys() if k not in ("README.md", "CLAUDE.md")]
        if doc_files:
            lines.append("## Available Documentation")
            lines.append("")
            lines.append("*See `.repo-ctx/docs/` for detailed documentation:*")
            lines.append("")
            for doc_file in sorted(doc_files)[:20]:
                # Extract first heading from doc as description
                content = documentation[doc_file]
                first_line = ""
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('#'):
                        first_line = line.lstrip('#').strip()
                        break
                    elif line and not first_line:
                        first_line = line[:60]
                        break
                lines.append(f"- `{doc_file}`: {first_line}")
            if len(doc_files) > 20:
                lines.append(f"- ... and {len(doc_files) - 20} more documentation files")
            lines.append("")
            lines.append("---")
            lines.append("")

        # Count by type
        type_counts = {}
        for sym in symbols:
            sym_type = sym.get("type", "unknown")
            type_counts[sym_type] = type_counts.get(sym_type, 0) + 1

        if type_counts:
            lines.append("## Code Statistics")
            lines.append("")
            for sym_type, count in sorted(type_counts.items()):
                lines.append(f"- {count} {sym_type}(s)")
            lines.append("")

        # Key classes/functions
        classes = [s for s in symbols if s.get("type") == "class"]
        functions = [s for s in symbols if s.get("type") == "function"]

        if classes:
            lines.append("## Key Classes")
            lines.append("")
            for cls in classes[:10]:  # Top 10
                doc = cls.get("documentation", "")
                if doc:
                    doc = doc.split('\n')[0][:80]  # First line, truncated
                    lines.append(f"- `{cls['qualified_name']}`: {doc}")
                else:
                    lines.append(f"- `{cls['qualified_name']}`")
            if len(classes) > 10:
                lines.append(f"- ... and {len(classes) - 10} more")
            lines.append("")

        if functions:
            lines.append("## Key Functions")
            lines.append("")
            for func in functions[:10]:  # Top 10
                sig = func.get("signature", func["name"])
                lines.append(f"- `{sig}`")
            if len(functions) > 10:
                lines.append(f"- ... and {len(functions) - 10} more")
            lines.append("")

        # Architecture section (if available)
        if architecture:
            lines.append("## Architecture")
            lines.append("")

            # Dependency summary
            edges = architecture.get("edges", [])
            nodes = architecture.get("nodes", [])
            cycles_count = architecture.get("cycles_count", 0)

            lines.append(f"- **Files**: {len(nodes)}")
            lines.append(f"- **Dependencies**: {len(edges)}")
            lines.append(f"- **Cycles**: {cycles_count}")
            lines.append("")

            # Layer info
            layers = architecture.get("layers", {})
            if layers.get("is_acyclic"):
                layer_count = layers.get("count", 0)
                lines.append(f"- **Layers**: {layer_count} (acyclic)")
            else:
                lines.append("- **Layers**: Not available (graph has cycles)")
            lines.append("")

            # Include mermaid dependency diagram
            mermaid_deps = architecture.get("mermaid_deps", "")
            if mermaid_deps and len(edges) > 0 and len(edges) <= 50:  # Only for small-medium graphs
                lines.append("### Dependency Graph")
                lines.append("")
                lines.append("```mermaid")
                lines.append(mermaid_deps)
                lines.append("```")
                lines.append("")

            # Include mermaid layers diagram
            mermaid_layers = architecture.get("mermaid_layers", "")
            if mermaid_layers and layers.get("is_acyclic") and layers.get("count", 0) > 0:
                lines.append("### Architecture Layers")
                lines.append("")
                lines.append("```mermaid")
                lines.append(mermaid_layers)
                lines.append("```")
                lines.append("")

            lines.append("---")
            lines.append("")

        # File structure
        files = set(s.get("file_path", "") for s in symbols if s.get("file_path"))
        if files:
            lines.append("## Files")
            lines.append("")
            for f in sorted(files)[:20]:  # Top 20
                lines.append(f"- {f}")
            if len(files) > 20:
                lines.append(f"- ... and {len(files) - 20} more")
            lines.append("")

        # Add .repo-ctx directory guide
        lines.append("---")
        lines.append("")
        lines.append("## About This Directory (.repo-ctx)")
        lines.append("")
        lines.append("This `.repo-ctx/` directory contains machine-readable context about the repository,")
        lines.append("generated by [repo-ctx](https://github.com/repo-ctx/repo-ctx) for LLM assistance.")
        lines.append("")
        lines.append("### Directory Structure")
        lines.append("")
        lines.append("```")
        lines.append(".repo-ctx/")
        lines.append("├── llms.txt              # This file - LLM-optimized summary")
        lines.append("├── metadata.json         # Generation metadata and stats")
        lines.append("├── ARCHITECTURE_SUMMARY.md # Combined architecture overview")
        lines.append("├── symbols/")
        lines.append("│   ├── index.json        # All extracted symbols")
        lines.append("│   └── by-file/          # Per-file symbol details (FULL level)")
        lines.append("├── architecture/")
        lines.append("│   ├── dependencies.html # Interactive dependency graph")
        lines.append("│   ├── dependencies.dot  # GraphViz format")
        lines.append("│   ├── dependencies.mmd  # Mermaid format")
        lines.append("│   ├── layers.json       # Topological layers")
        lines.append("│   ├── dsm.json          # Design Structure Matrix")
        lines.append("│   └── cycles.json       # Detected cycles")
        lines.append("└── metrics/")
        lines.append("    └── complexity.json   # Code complexity metrics")
        lines.append("```")
        lines.append("")
        lines.append("### Quick Reference")
        lines.append("")
        lines.append("- **Find a symbol**: Check `symbols/index.json`")
        lines.append("- **Understand architecture**: Read `ARCHITECTURE_SUMMARY.md`")
        lines.append("- **Explore dependencies**: Open `architecture/dependencies.html` in browser")
        lines.append("- **Check for cycles**: See `architecture/cycles.json`")
        lines.append("")

        return "\n".join(lines)

    def _generate_symbol_index(self, symbols: list[dict]) -> dict:
        """Generate symbol index.

        Args:
            symbols: Extracted symbols.

        Returns:
            Symbol index dictionary.
        """
        return {
            "total": len(symbols),
            "by_type": self._group_by(symbols, "type"),
            "by_file": self._group_by(symbols, "file_path"),
            "symbols": [
                {
                    "name": s["name"],
                    "qualified_name": s["qualified_name"],
                    "type": s["type"],
                    "file": s["file_path"],
                    "line": s["line_start"],
                }
                for s in symbols
            ],
        }

    def _group_by(self, items: list[dict], key: str) -> dict[str, int]:
        """Group items by key and count.

        Args:
            items: List of dictionaries.
            key: Key to group by.

        Returns:
            Dictionary of key -> count.
        """
        counts = {}
        for item in items:
            value = item.get(key, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts

    def _resolve_target_to_file(
        self,
        target: str,
        symbols: list[dict],
    ) -> Optional[str]:
        """Resolve an import target to a file path.

        Args:
            target: Import target (e.g., "repo_ctx.services.dump").
            symbols: List of symbols with file paths.

        Returns:
            File path if found, None otherwise.
        """
        # Build a map of qualified names to file paths
        name_to_file = {}
        for sym in symbols:
            qname = sym.get("qualified_name", "")
            file_path = sym.get("file_path", "")
            if qname and file_path:
                name_to_file[qname] = file_path
                # Also map the module path (without class/function name)
                parts = qname.rsplit(".", 1)
                if len(parts) > 1:
                    name_to_file[parts[0]] = file_path

        # Direct match
        if target in name_to_file:
            return name_to_file[target]

        # Try to match by converting module path to file path
        # e.g., "repo_ctx.services.dump" -> "repo_ctx/services/dump.py"
        for qname, file_path in name_to_file.items():
            # Check if target is a prefix of qualified name
            if qname.startswith(target + "."):
                return file_path
            # Check if file path matches target pattern
            target_as_path = target.replace(".", "/")
            if target_as_path in file_path:
                return file_path

        return None

    def _generate_summary_md(
        self,
        source_path: Path,
        symbols: list[dict],
        git_info: GitInfo,
    ) -> str:
        """Generate summary markdown.

        Args:
            source_path: Repository path.
            symbols: Extracted symbols.
            git_info: Git information.

        Returns:
            Summary markdown content.
        """
        lines = [
            f"# {source_path.name} - Repository Summary",
            "",
            f"Generated by repo-ctx v{__version__}",
            "",
            "## Overview",
            "",
        ]

        # Git info
        if git_info.commit:
            lines.append("### Git Information")
            lines.append("")
            lines.append(f"- **Commit**: `{git_info.short_commit}`")
            if git_info.tag:
                lines.append(f"- **Tag**: `{git_info.tag}`")
            if git_info.branch:
                lines.append(f"- **Branch**: `{git_info.branch}`")
            if git_info.dirty:
                lines.append("- **Warning**: Working directory has uncommitted changes")
            lines.append("")

        # Statistics
        lines.append("### Statistics")
        lines.append("")
        lines.append(f"- **Total Symbols**: {len(symbols)}")

        type_counts = self._group_by(symbols, "type")
        for sym_type, count in sorted(type_counts.items()):
            lines.append(f"- **{sym_type.title()}s**: {count}")

        file_count = len(set(s.get("file_path", "") for s in symbols))
        lines.append(f"- **Files Analyzed**: {file_count}")
        lines.append("")

        # Classes
        classes = [s for s in symbols if s.get("type") == "class"]
        if classes:
            lines.append("## Classes")
            lines.append("")
            for cls in sorted(classes, key=lambda x: x["qualified_name"]):
                lines.append(f"### {cls['qualified_name']}")
                lines.append("")
                lines.append(f"**File**: `{cls['file_path']}:{cls['line_start']}`")
                if cls.get("documentation"):
                    lines.append("")
                    lines.append(cls["documentation"])
                lines.append("")

        return "\n".join(lines)

    def _sanitize_mermaid_label(self, label: str, max_length: int = 40) -> str:
        """Sanitize a label for use in mermaid diagrams.

        Args:
            label: The raw label text.
            max_length: Maximum length before truncation.

        Returns:
            Sanitized label safe for mermaid.
        """
        if not label:
            return "unnamed"

        # Take only the first line
        label = label.split('\n')[0].strip()

        # Remove or escape problematic characters
        # Mermaid has issues with: [ ] ( ) { } | " ' ` < > # & ; \
        for char in ['[', ']', '(', ')', '{', '}', '|', '"', "'", '`', '<', '>', '#', '&', ';', '\\']:
            label = label.replace(char, '')

        # Remove any remaining control characters
        label = ''.join(c for c in label if c.isprintable() and c != '\n' and c != '\r')

        # Truncate if too long
        if len(label) > max_length:
            label = label[:max_length-3] + "..."

        # Handle empty result
        if not label.strip():
            return "unnamed"

        return label.strip()

    def _get_top_nodes_by_degree(
        self,
        nodes: list[str],
        edges: list[tuple[str, str, str]],
        top_n: int = 20,
    ) -> tuple[list[str], list[tuple[str, str, str]]]:
        """Get top N nodes by degree (most connected) and their edges.

        Args:
            nodes: All node names.
            edges: All (source, target, label) tuples.
            top_n: Maximum number of nodes to return.

        Returns:
            Tuple of (filtered_nodes, filtered_edges).
        """
        if len(nodes) <= top_n:
            return nodes, edges

        # Calculate degree (in + out) for each node
        degree = {n: 0 for n in nodes}
        for src, tgt, _ in edges:
            if src in degree:
                degree[src] += 1
            if tgt in degree:
                degree[tgt] += 1

        # Sort by degree and take top N
        sorted_nodes = sorted(degree.keys(), key=lambda n: degree[n], reverse=True)
        top_nodes = set(sorted_nodes[:top_n])

        # Filter edges to only include those between top nodes
        filtered_edges = [
            (src, tgt, label)
            for src, tgt, label in edges
            if src in top_nodes and tgt in top_nodes
        ]

        return list(top_nodes), filtered_edges

    def _generate_mermaid_flowchart(
        self,
        nodes: list[str],
        edges: list[tuple[str, str, str]],
        title: str = "Dependency Graph",
    ) -> str:
        """Generate mermaid flowchart from graph data.

        Args:
            nodes: List of node names.
            edges: List of (source, target, label) tuples.
            title: Optional title comment.

        Returns:
            Mermaid flowchart string.
        """
        # Note: We skip mermaid frontmatter title as it's not universally supported
        # The title is provided in the markdown heading above the diagram
        lines = ["flowchart LR"]

        # Create safe node IDs (mermaid requires alphanumeric)
        node_ids = {}
        for i, node in enumerate(sorted(nodes)):
            safe_id = f"N{i}"
            node_ids[node] = safe_id

            # Extract a clean short label
            if ":" in node:
                # For class-level nodes like "file.py:ClassName"
                parts = node.split(":")
                short_name = parts[-1] if parts[-1] else parts[0]
            else:
                # For file/package nodes
                short_name = Path(node).name if node else "root"

            # Sanitize the label
            short_name = self._sanitize_mermaid_label(short_name)

            lines.append(f"    {safe_id}[{short_name}]")

        # Add edges with labels
        for source, target, label in edges:
            if source in node_ids and target in node_ids:
                src_id = node_ids[source]
                tgt_id = node_ids[target]
                safe_label = self._sanitize_mermaid_label(label, max_length=20) if label else ""
                if safe_label:
                    lines.append(f"    {src_id} -->|{safe_label}| {tgt_id}")
                else:
                    lines.append(f"    {src_id} --> {tgt_id}")

        return "\n".join(lines)

    def _generate_mermaid_from_layers(
        self,
        layers_data: dict,
    ) -> str:
        """Generate mermaid diagram from layer data.

        Args:
            layers_data: Layer information dict.

        Returns:
            Mermaid flowchart showing layers.
        """
        # Note: We skip mermaid frontmatter title as it's not universally supported
        lines = ["flowchart TB"]

        if not layers_data.get("is_acyclic", False):
            lines.append("    note[Graph contains cycles - layers not available]")
            return "\n".join(lines)

        layers = layers_data.get("layers", [])
        if not layers:
            lines.append("    note[No layers detected]")
            return "\n".join(lines)

        # Create subgraphs for each layer
        for layer in layers:
            level = layer.get("level", 0)
            nodes = layer.get("nodes", [])
            if nodes:
                lines.append(f"    subgraph Layer{level}[Level {level}]")
                for i, node in enumerate(nodes):
                    short_name = Path(node).name if node else "root"
                    short_name = self._sanitize_mermaid_label(short_name)
                    safe_id = f"L{level}N{i}"
                    lines.append(f"        {safe_id}[{short_name}]")
                lines.append("    end")
                lines.append("")

        return "\n".join(lines)

    async def _generate_architecture(
        self,
        output_dir: Path,
        symbols: list[dict],
        dependencies: list[str],
    ) -> tuple[list[str], dict]:
        """Generate architecture analysis files.

        Args:
            output_dir: Output directory for architecture files.
            symbols: Extracted symbols.
            dependencies: Extracted dependencies.

        Returns:
            Tuple of (list of created file paths, architecture data dict).
        """
        files_created = []
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build dependency graph from symbols using networkx
        import networkx as nx
        graph = nx.DiGraph()

        # Add nodes from symbols
        for sym in symbols:
            file_path = sym.get("file_path", "")
            if file_path:
                graph.add_node(file_path)

        # Build set of known files for quick lookup
        known_files = set()
        for sym in symbols:
            fp = sym.get("file_path", "")
            if fp:
                known_files.add(fp)

        # Add edges from dependencies (file-level)
        for dep in dependencies:
            # Get source and target info from dependency
            source_file = getattr(dep, 'source', '') or getattr(dep, 'file_path', '') or ''
            target = getattr(dep, 'target', '') or ''
            dep_type = getattr(dep, 'dependency_type', 'import')

            if source_file and target:
                target_file = None

                # First, check if target is already a known file path (C/C++ includes)
                if target in known_files:
                    target_file = target
                elif target in graph.nodes():
                    target_file = target
                else:
                    # Try to resolve target to a file in the repository
                    # For Python imports, target is module name like "repo_ctx.services"
                    target_file = self._resolve_target_to_file(target, symbols)

                if target_file and source_file != target_file:
                    # Add both nodes if not present
                    if source_file not in graph:
                        graph.add_node(source_file)
                    if target_file not in graph:
                        graph.add_node(target_file)
                    graph.add_edge(
                        source_file,
                        target_file,
                        dependency_type=dep_type,
                    )

        # DSM - Generate directly from networkx graph
        try:
            nodes = sorted(graph.nodes())
            node_to_idx = {node: i for i, node in enumerate(nodes)}
            size = len(nodes)

            # Build adjacency matrix
            matrix = [[0] * size for _ in range(size)]
            for u, v in graph.edges():
                if u in node_to_idx and v in node_to_idx:
                    matrix[node_to_idx[u]][node_to_idx[v]] = 1

            dsm_data = {
                "nodes": nodes,
                "labels": [Path(n).name for n in nodes],  # Short names
                "matrix": matrix,
                "size": size,
            }
            self._write_json(output_dir / "dsm.json", dsm_data)
            files_created.append("architecture/dsm.json")
        except Exception as e:
            logger.warning(f"DSM generation failed: {e}")

        # Cycles - Use networkx cycle detection
        try:
            import networkx as nx
            cycles = list(nx.simple_cycles(graph))
            cycles_data = {
                "count": len(cycles),
                "cycles": [
                    {
                        "nodes": cycle,
                        "length": len(cycle),
                    }
                    for cycle in cycles[:50]  # Limit to first 50 cycles
                ]
            }
            self._write_json(output_dir / "cycles.json", cycles_data)
            files_created.append("architecture/cycles.json")
        except Exception as e:
            logger.warning(f"Cycle detection failed: {e}")

        # Layers - Simple topological layering from networkx
        try:
            import networkx as nx
            # Try topological generations (layers)
            if nx.is_directed_acyclic_graph(graph):
                generations = list(nx.topological_generations(graph))
                layers_data = {
                    "count": len(generations),
                    "is_acyclic": True,
                    "layers": [
                        {
                            "level": i,
                            "nodes": sorted(gen),
                        }
                        for i, gen in enumerate(generations)
                    ]
                }
            else:
                # Graph has cycles, can't do topological sort
                # Just report connected components
                layers_data = {
                    "count": 0,
                    "is_acyclic": False,
                    "layers": [],
                    "note": "Graph contains cycles, topological layering not possible"
                }
            self._write_json(output_dir / "layers.json", layers_data)
            files_created.append("architecture/layers.json")
        except Exception as e:
            logger.warning(f"Layer detection failed: {e}")

        # Dependency graph as DOT
        try:
            dot_lines = ["digraph dependencies {"]
            dot_lines.append("  rankdir=LR;")
            dot_lines.append("  node [shape=box, style=filled, fillcolor=lightblue];")
            dot_lines.append("  edge [color=gray50];")
            dot_lines.append("")

            # Group nodes by directory for better visualization
            for node in graph.nodes():
                safe_name = node.replace('"', '\\"').replace('/', '_')
                # Use short label (just filename)
                short_label = Path(node).name
                dot_lines.append(f'  "{safe_name}" [label="{short_label}"];')

            dot_lines.append("")

            # Add edges with dependency type labels
            for u, v, data in graph.edges(data=True):
                safe_u = u.replace('"', '\\"').replace('/', '_')
                safe_v = v.replace('"', '\\"').replace('/', '_')
                dep_type = data.get('dependency_type', 'import')
                # Color code by type
                color = {
                    'import': 'blue',
                    'call': 'green',
                    'inherit': 'red',
                    'compose': 'purple',
                }.get(dep_type, 'gray')
                dot_lines.append(f'  "{safe_u}" -> "{safe_v}" [color={color}, label="{dep_type}"];')

            dot_lines.append("}")
            self._write_text(output_dir / "dependencies.dot", "\n".join(dot_lines))
            files_created.append("architecture/dependencies.dot")
        except Exception as e:
            logger.warning(f"DOT generation failed: {e}")

        # Collect edges for mermaid
        edges_for_mermaid = []
        for u, v, data in graph.edges(data=True):
            dep_type = data.get('dependency_type', 'import')
            edges_for_mermaid.append((u, v, dep_type))

        # Generate mermaid dependency diagram
        try:
            mermaid_deps = self._generate_mermaid_flowchart(
                list(graph.nodes()),
                edges_for_mermaid,
                title="File Dependencies",
            )
            self._write_text(output_dir / "dependencies.mmd", mermaid_deps)
            files_created.append("architecture/dependencies.mmd")
        except Exception as e:
            logger.warning(f"Mermaid dependency diagram generation failed: {e}")

        # Generate mermaid layers diagram
        try:
            mermaid_layers = self._generate_mermaid_from_layers(layers_data)
            self._write_text(output_dir / "layers.mmd", mermaid_layers)
            files_created.append("architecture/layers.mmd")
        except Exception as e:
            logger.warning(f"Mermaid layers diagram generation failed: {e}")

        # === Class-Level Analysis ===
        class_graph_result = None
        class_cycles_data = {"count": 0, "cycles": []}
        class_coupling_data = {}

        try:
            from ..analysis import DependencyGraph, GraphType, CouplingAnalyzer, CycleDetector
            from ..analysis.models import Symbol, SymbolType

            # Convert symbol dicts to Symbol objects for the graph builder
            symbol_objects = []
            for sym in symbols:
                # Validate symbol has required fields and valid name
                name = sym.get("name", "")
                file_path = sym.get("file_path", "")

                # Skip invalid symbols (no name, no file, or corrupted name)
                if not name or not file_path:
                    continue

                # Skip symbols with names that look like docstring fragments
                # Valid names should be identifier-like (alphanumeric + underscore)
                clean_name = name.replace('_', '').replace('.', '')
                if not clean_name or not clean_name[0].isalpha():
                    # Allow names starting with underscore (private/dunder)
                    if not name.startswith('_'):
                        continue

                # Skip names with whitespace or special characters (docstring fragments)
                if any(c in name for c in ['\n', '\r', '\t', '=', '"', "'", '(', ')', '{', '}', '[', ']', ' ']):
                    continue

                # Skip very short or very long names (likely corrupted)
                if len(name) < 2 or len(name) > 100:
                    continue

                sym_type = sym.get("type", "function")
                type_map = {
                    "class": SymbolType.CLASS,
                    "function": SymbolType.FUNCTION,
                    "method": SymbolType.METHOD,
                    "interface": SymbolType.INTERFACE,
                    "enum": SymbolType.ENUM,
                    "variable": SymbolType.VARIABLE,
                    "constant": SymbolType.CONSTANT,
                    "module": SymbolType.MODULE,
                }
                symbol_objects.append(Symbol(
                    name=name,
                    symbol_type=type_map.get(sym_type, SymbolType.FUNCTION),
                    file_path=file_path,
                    line_start=sym.get("line_start", 0),
                    line_end=sym.get("line_end"),
                    signature=sym.get("signature"),
                    visibility=sym.get("visibility", "public"),
                    language=sym.get("language", "unknown"),
                    documentation=sym.get("documentation"),
                    qualified_name=sym.get("qualified_name"),
                    metadata=sym.get("metadata", {}),
                ))

            # Convert dependencies to dicts - preserve caller/callee info for class-level analysis
            dep_dicts = []
            for dep in dependencies:
                dep_dict = {
                    "file_path": getattr(dep, 'file_path', ''),
                    "target": getattr(dep, 'target', ''),
                    "type": getattr(dep, 'dependency_type', 'import'),
                }
                # For call dependencies, preserve the caller (source) info
                # source contains qualified name like "ClassName.method_name"
                if hasattr(dep, 'source') and dep.source:
                    dep_dict["caller"] = dep.source
                    dep_dict["source"] = dep.source  # Also set source for compatibility
                if hasattr(dep, 'target') and dep.target:
                    dep_dict["callee"] = dep.target
                dep_dicts.append(dep_dict)

            # Build class-level graph
            graph_builder = DependencyGraph()
            class_graph_result = graph_builder.build(
                symbol_objects, dep_dicts,
                graph_type=GraphType.CLASS,
                graph_id="class-dependencies",
                graph_label="Class Dependencies"
            )

            # Cycle detection at class level
            if class_graph_result and class_graph_result.nodes:
                cycle_detector = CycleDetector()
                class_cycles = cycle_detector.detect(class_graph_result)
                class_cycles_data = {
                    "level": "class",
                    "count": len(class_cycles),
                    "cycles": [c.to_dict() for c in class_cycles[:20]]
                }

                # Coupling analysis at class level
                coupling_analyzer = CouplingAnalyzer()
                coupling_result = coupling_analyzer.analyze(class_graph_result)
                class_coupling_data = coupling_result.to_dict()

                # Save class-level analysis
                self._write_json(output_dir / "class_cycles.json", class_cycles_data)
                files_created.append("architecture/class_cycles.json")

                self._write_json(output_dir / "class_coupling.json", class_coupling_data)
                files_created.append("architecture/class_coupling.json")

                # Generate class dependency mermaid diagram
                class_edges = [(e.source, e.target, e.relation) for e in class_graph_result.edges]
                class_nodes = list(class_graph_result.nodes.keys())
                class_mermaid = ""
                if class_nodes:
                    class_mermaid = self._generate_mermaid_flowchart(
                        class_nodes, class_edges, "Class Dependencies"
                    )
                    self._write_text(output_dir / "class_dependencies.mmd", class_mermaid)
                    files_created.append("architecture/class_dependencies.mmd")

                # Store mermaid for embedding in architecture.md
                class_cycles_data["mermaid"] = class_mermaid

        except Exception as e:
            logger.warning(f"Class-level analysis failed: {e}")

        # === Package-Level Analysis ===
        package_graph_result = None
        package_cycles_data = {"count": 0, "cycles": []}
        package_coupling_data = {}

        try:
            from ..analysis import DependencyGraph, GraphType, CouplingAnalyzer, CycleDetector

            # Build package-level graph
            package_graph_result = graph_builder.build(
                symbol_objects, dep_dicts,
                graph_type=GraphType.PACKAGE,
                graph_id="package-dependencies",
                graph_label="Package Dependencies"
            )

            # Cycle detection at package level (CRITICAL - these are architectural issues)
            if package_graph_result and package_graph_result.nodes:
                cycle_detector = CycleDetector()
                package_cycles = cycle_detector.detect(package_graph_result)
                package_cycles_data = {
                    "level": "package",
                    "count": len(package_cycles),
                    "severity": "CRITICAL" if package_cycles else "OK",
                    "cycles": [c.to_dict() for c in package_cycles[:20]]
                }

                # Coupling analysis at package level
                coupling_analyzer = CouplingAnalyzer()
                pkg_coupling_result = coupling_analyzer.analyze_packages(
                    package_graph_result, class_graph_result
                )
                package_coupling_data = pkg_coupling_result.to_dict()

                # Save package-level analysis
                self._write_json(output_dir / "package_cycles.json", package_cycles_data)
                files_created.append("architecture/package_cycles.json")

                self._write_json(output_dir / "package_coupling.json", package_coupling_data)
                files_created.append("architecture/package_coupling.json")

                # Generate package dependency mermaid diagram
                pkg_edges = [(e.source, e.target, e.relation) for e in package_graph_result.edges]
                pkg_nodes = list(package_graph_result.nodes.keys())
                pkg_mermaid = ""
                if pkg_nodes:
                    pkg_mermaid = self._generate_mermaid_flowchart(
                        pkg_nodes, pkg_edges, "Package Dependencies"
                    )
                    self._write_text(output_dir / "package_dependencies.mmd", pkg_mermaid)
                    files_created.append("architecture/package_dependencies.mmd")

                # Store mermaid for embedding in architecture.md
                package_cycles_data["mermaid"] = pkg_mermaid

        except Exception as e:
            logger.warning(f"Package-level analysis failed: {e}")

        # Return architecture data for inclusion in llms.txt
        arch_data = {
            "nodes": list(graph.nodes()),
            "edges": edges_for_mermaid,
            "cycles_count": cycles_data.get("count", 0) if 'cycles_data' in dir() else 0,
            "layers": layers_data if 'layers_data' in dir() else {},
            "mermaid_deps": mermaid_deps if 'mermaid_deps' in dir() else "",
            "mermaid_layers": mermaid_layers if 'mermaid_layers' in dir() else "",
            "dsm": dsm_data if 'dsm_data' in dir() else {},
            "cycles": cycles_data if 'cycles_data' in dir() else {},
            # New multi-level analysis
            "class_cycles": class_cycles_data,
            "package_cycles": package_cycles_data,
            "class_coupling": class_coupling_data,
            "package_coupling": package_coupling_data,
        }

        # Generate interactive HTML dependency graph
        try:
            from ..analysis.interactive_graph import InteractiveGraphGenerator
            html_generator = InteractiveGraphGenerator()
            html_path = html_generator.generate_from_arch_data(
                arch_data,
                output_dir / "dependencies.html",
                title=f"{output_dir.parent.name} - Dependency Graph",
            )
            files_created.append("architecture/dependencies.html")
        except Exception as e:
            logger.warning(f"Interactive HTML graph generation failed: {e}")

        # Generate ARCHITECTURE_SUMMARY.md at root level
        try:
            arch_md = self._generate_architecture_md(arch_data)
            self._write_text(output_dir.parent / "ARCHITECTURE_SUMMARY.md", arch_md)
            files_created.append("ARCHITECTURE_SUMMARY.md")
        except Exception as e:
            logger.warning(f"ARCHITECTURE_SUMMARY.md generation failed: {e}")

        return files_created, arch_data

    def _generate_architecture_md(self, arch_data: dict) -> str:
        """Generate combined architecture markdown file.

        Args:
            arch_data: Architecture data dictionary.

        Returns:
            Combined architecture markdown content.
        """
        lines = [
            "# Architecture Overview",
            "",
            "This document provides a comprehensive view of the codebase architecture,",
            "including dependency graphs, layers, and structural analysis.",
            "",
            "---",
            "",
        ]

        # Summary statistics
        nodes = arch_data.get("nodes", [])
        edges = arch_data.get("edges", [])
        cycles_count = arch_data.get("cycles_count", 0)
        layers = arch_data.get("layers", {})

        lines.append("## Summary")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Files | {len(nodes)} |")
        lines.append(f"| Dependencies | {len(edges)} |")
        lines.append(f"| Cycles | {cycles_count} |")
        if layers.get("is_acyclic"):
            lines.append(f"| Layers | {layers.get('count', 0)} |")
        else:
            lines.append(f"| Layers | N/A (has cycles) |")
        lines.append("")

        # Dependency graph (mermaid) - limited to top nodes for readability
        nodes = arch_data.get("nodes", [])
        edges = arch_data.get("edges", [])
        mermaid_deps = arch_data.get("mermaid_deps", "")

        if mermaid_deps and nodes:
            lines.append("## Dependency Graph")
            lines.append("")

            # For large graphs, show only top N most connected nodes
            MAX_NODES_IN_DIAGRAM = 25
            if len(nodes) > MAX_NODES_IN_DIAGRAM:
                lines.append(f"Shows top {MAX_NODES_IN_DIAGRAM} most connected files (out of {len(nodes)} total).")
                lines.append("")
                lines.append("📊 **[Open Interactive Graph](architecture/dependencies.html)** for full visualization with search, filtering, and zoom.")
                lines.append("")

                # Generate limited diagram
                top_nodes, top_edges = self._get_top_nodes_by_degree(
                    nodes, edges, top_n=MAX_NODES_IN_DIAGRAM
                )
                limited_mermaid = self._generate_mermaid_flowchart(
                    top_nodes, top_edges, title="File Dependencies (Top Nodes)"
                )
                lines.append("```mermaid")
                lines.append(limited_mermaid)
                lines.append("```")
            else:
                lines.append("Shows file-level dependencies between modules.")
                lines.append("")
                lines.append("📊 **[Open Interactive Graph](architecture/dependencies.html)** for enhanced visualization.")
                lines.append("")
                lines.append("```mermaid")
                lines.append(mermaid_deps)
                lines.append("```")

            lines.append("")
            lines.append("*Also available as: `dependencies.dot` (GraphViz), `dependencies.mmd` (Mermaid), `dependencies.html` (Interactive)*")
            lines.append("")

        # Architecture layers (mermaid)
        mermaid_layers = arch_data.get("mermaid_layers", "")
        if layers.get("is_acyclic") and mermaid_layers:
            lines.append("## Architecture Layers")
            lines.append("")
            lines.append("Topological layering of modules. Higher layers depend on lower layers.")
            lines.append("")
            lines.append("```mermaid")
            lines.append(mermaid_layers)
            lines.append("```")
            lines.append("")
            lines.append("*Also available as: `layers.json`, `layers.mmd` (Mermaid)*")
            lines.append("")

            # Layer details
            layer_list = layers.get("layers", [])
            if layer_list:
                lines.append("### Layer Details")
                lines.append("")
                for layer in layer_list:
                    level = layer.get("level", 0)
                    layer_nodes = layer.get("nodes", [])
                    lines.append(f"**Level {level}**: {len(layer_nodes)} file(s)")
                    for node in layer_nodes:
                        lines.append(f"  - `{node}`")
                    lines.append("")

        # Cycles section
        cycles_data = arch_data.get("cycles", {})
        if cycles_count > 0:
            lines.append("## Detected Cycles")
            lines.append("")
            lines.append(f"⚠️ **{cycles_count} cycle(s) detected** - consider refactoring to reduce coupling.")
            lines.append("")

            cycles_list = cycles_data.get("cycles", [])
            for i, cycle in enumerate(cycles_list[:10]):  # Show max 10
                cycle_nodes = cycle.get("nodes", [])
                lines.append(f"### Cycle {i + 1}")
                lines.append("")
                lines.append("```")
                lines.append(" → ".join(cycle_nodes) + " → " + cycle_nodes[0] if cycle_nodes else "")
                lines.append("```")
                lines.append("")

            if len(cycles_list) > 10:
                lines.append(f"*... and {len(cycles_list) - 10} more cycles (see cycles.json)*")
                lines.append("")

        # DSM section
        dsm_data = arch_data.get("dsm", {})
        if dsm_data and dsm_data.get("size", 0) > 0:
            lines.append("## Design Structure Matrix (DSM)")
            lines.append("")
            lines.append("The DSM shows dependencies between files as a matrix.")
            lines.append("A mark at row R, column C means R depends on C.")
            lines.append("")
            lines.append("*Full DSM data available in: `dsm.json`*")
            lines.append("")

            # Show compact text DSM for small graphs
            size = dsm_data.get("size", 0)
            if size <= 10:
                labels = dsm_data.get("labels", [])
                matrix = dsm_data.get("matrix", [])
                if labels and matrix:
                    # Create ASCII DSM
                    max_label_len = max(len(l) for l in labels) if labels else 0
                    lines.append("```")
                    # Header row
                    header = " " * (max_label_len + 2)
                    for i, label in enumerate(labels):
                        header += f" {i} "
                    lines.append(header)

                    # Data rows
                    for i, row in enumerate(matrix):
                        row_str = f"{labels[i]:<{max_label_len}} │"
                        for val in row:
                            row_str += " × " if val else " · "
                        lines.append(row_str)
                    lines.append("```")
                    lines.append("")

        # === Class-Level Analysis ===
        class_coupling = arch_data.get("class_coupling", {})
        class_cycles = arch_data.get("class_cycles", {})

        if class_coupling or class_cycles:
            lines.append("## Class-Level Analysis")
            lines.append("")
            lines.append("Analysis at the class granularity for detailed refactoring insights.")
            lines.append("")

            # Embed class dependency diagram if available (limited for readability)
            class_mermaid = class_cycles.get("mermaid", "")
            if class_mermaid:
                lines.append("### Class Dependency Graph")
                lines.append("")
                # Check if diagram is too large (simple line count heuristic)
                mermaid_lines = class_mermaid.split('\n')
                if len(mermaid_lines) > 50:
                    lines.append(f"*Diagram limited for readability. See `class_dependencies.mmd` for full view.*")
                    lines.append("")
                    # Show truncated version
                    lines.append("```mermaid")
                    lines.append('\n'.join(mermaid_lines[:50]))
                    lines.append("    ...")
                    lines.append("```")
                else:
                    lines.append("```mermaid")
                    lines.append(class_mermaid)
                    lines.append("```")
                lines.append("")

            # Class cycles
            if class_cycles.get("count", 0) > 0:
                lines.append(f"### Class Cycles: {class_cycles.get('count', 0)} detected")
                lines.append("")
                for i, cycle in enumerate(class_cycles.get("cycles", [])[:5]):
                    cycle_nodes = cycle.get("nodes", [])
                    if cycle_nodes:
                        short_names = [n.split(":")[-1] if ":" in n else n for n in cycle_nodes]
                        lines.append(f"- Cycle {i+1}: `{' → '.join(short_names)}`")
                lines.append("")

            # Class coupling metrics
            if class_coupling:
                problems = class_coupling.get("problems", {})
                aggregates = class_coupling.get("aggregates", {})

                if problems.get("god_classes", 0) > 0 or problems.get("unstable_cores", 0) > 0:
                    lines.append("### Coupling Problems")
                    lines.append("")
                    lines.append("| Issue | Count |")
                    lines.append("|-------|-------|")
                    if problems.get("god_classes", 0) > 0:
                        lines.append(f"| God Classes | {problems['god_classes']} |")
                    if problems.get("unstable_cores", 0) > 0:
                        lines.append(f"| Unstable Cores | {problems['unstable_cores']} |")
                    if problems.get("high_coupling", 0) > 0:
                        lines.append(f"| High Coupling | {problems['high_coupling']} |")
                    lines.append("")

                # Refactoring targets
                targets = class_coupling.get("refactoring_targets", [])
                if targets:
                    lines.append("### Refactoring Targets")
                    lines.append("")
                    for target in targets[:5]:
                        risk = target.get("risk_level", "")
                        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(risk, "⚪")
                        lines.append(f"- {icon} **{target.get('node_label', '')}** (Ca={target.get('ca', 0)}, Ce={target.get('ce', 0)})")
                        lines.append(f"  - {target.get('suggestion', '')}")
                    lines.append("")

            lines.append("*Details: `class_cycles.json`, `class_coupling.json`, `class_dependencies.mmd`*")
            lines.append("")

        # === Package-Level Analysis ===
        package_coupling = arch_data.get("package_coupling", {})
        package_cycles = arch_data.get("package_cycles", {})

        if package_coupling or package_cycles:
            lines.append("## Package-Level Analysis")
            lines.append("")
            lines.append("High-level architecture view at the package/directory level.")
            lines.append("")

            # Embed package dependency diagram if available (limited for readability)
            pkg_mermaid = package_cycles.get("mermaid", "")
            if pkg_mermaid:
                lines.append("### Package Dependency Graph")
                lines.append("")
                # Check if diagram is too large
                mermaid_lines = pkg_mermaid.split('\n')
                if len(mermaid_lines) > 50:
                    lines.append(f"*Diagram limited for readability. See `package_dependencies.mmd` for full view.*")
                    lines.append("")
                    lines.append("```mermaid")
                    lines.append('\n'.join(mermaid_lines[:50]))
                    lines.append("    ...")
                    lines.append("```")
                else:
                    lines.append("```mermaid")
                    lines.append(pkg_mermaid)
                    lines.append("```")
                lines.append("")

            # Package cycles (CRITICAL)
            if package_cycles.get("count", 0) > 0:
                lines.append(f"### 🔴 CRITICAL: Package Cycles Detected ({package_cycles.get('count', 0)})")
                lines.append("")
                lines.append("Package cycles prevent independent deployment and indicate architectural issues.")
                lines.append("")
                for i, cycle in enumerate(package_cycles.get("cycles", [])[:5]):
                    cycle_nodes = cycle.get("nodes", [])
                    if cycle_nodes:
                        lines.append(f"- `{' ↔ '.join(cycle_nodes)}`")
                lines.append("")

            # Package coupling
            if package_coupling:
                metrics = package_coupling.get("metrics", [])
                zones = {"zone_of_pain": 0, "zone_of_uselessness": 0}
                for m in metrics:
                    zone = m.get("zone", "normal")
                    if zone in zones:
                        zones[zone] += 1

                if zones["zone_of_pain"] > 0 or zones["zone_of_uselessness"] > 0:
                    lines.append("### Package Zones")
                    lines.append("")
                    if zones["zone_of_pain"] > 0:
                        lines.append(f"- **Zone of Pain**: {zones['zone_of_pain']} packages (low abstractness, low instability)")
                    if zones["zone_of_uselessness"] > 0:
                        lines.append(f"- **Zone of Uselessness**: {zones['zone_of_uselessness']} packages (high abstractness, high instability)")
                    lines.append("")

            lines.append("*Details: `package_cycles.json`, `package_coupling.json`, `package_dependencies.mmd`*")
            lines.append("")

        # Files list
        if nodes:
            lines.append("## Analyzed Files")
            lines.append("")
            for node in sorted(nodes):
                lines.append(f"- `{node}`")
            lines.append("")

        # Related files
        lines.append("---")
        lines.append("")
        lines.append("## Related Files")
        lines.append("")
        lines.append("| File | Description |")
        lines.append("|------|-------------|")
        lines.append("| **File Level** | |")
        lines.append("| `dependencies.html` | **Interactive graph** - Open in browser for search, filter, zoom |")
        lines.append("| `dependencies.dot` | GraphViz format dependency graph |")
        lines.append("| `dependencies.mmd` | Mermaid format dependency graph |")
        lines.append("| `layers.json` | Layer assignments as JSON |")
        lines.append("| `layers.mmd` | Mermaid format layer diagram |")
        lines.append("| `dsm.json` | Design Structure Matrix data |")
        lines.append("| `cycles.json` | File-level cycles data |")
        lines.append("| **Class Level** | |")
        lines.append("| `class_dependencies.mmd` | Class dependency diagram |")
        lines.append("| `class_cycles.json` | Class-level cycles |")
        lines.append("| `class_coupling.json` | Class coupling metrics (Ca/Ce/Instability) |")
        lines.append("| **Package Level** | |")
        lines.append("| `package_dependencies.mmd` | Package dependency diagram |")
        lines.append("| `package_cycles.json` | Package-level cycles (CRITICAL) |")
        lines.append("| `package_coupling.json` | Package coupling with abstractness |")
        lines.append("")

        return "\n".join(lines)

    def _generate_metrics(self, symbols: list[dict]) -> dict:
        """Generate complexity metrics.

        Args:
            symbols: Extracted symbols.

        Returns:
            Metrics dictionary.
        """
        # Calculate basic metrics
        file_counts = {}
        for sym in symbols:
            file_path = sym.get("file_path", "")
            if file_path:
                if file_path not in file_counts:
                    file_counts[file_path] = {
                        "class": 0,
                        "function": 0,
                        "method": 0,
                        "total": 0,
                    }
                file_counts[file_path]["total"] += 1
                sym_type = sym.get("type", "")
                if sym_type in file_counts[file_path]:
                    file_counts[file_path][sym_type] += 1

        return {
            "summary": {
                "total_files": len(file_counts),
                "total_symbols": len(symbols),
                "avg_symbols_per_file": len(symbols) / max(len(file_counts), 1),
            },
            "by_file": file_counts,
        }

    def _generate_symbols_by_file(
        self,
        output_dir: Path,
        symbols: list[dict],
    ) -> list[str]:
        """Generate per-file symbol files.

        Args:
            output_dir: Output directory.
            symbols: Extracted symbols.

        Returns:
            List of created file paths.
        """
        files_created = []
        output_dir.mkdir(parents=True, exist_ok=True)

        # Group by file
        by_file = {}
        for sym in symbols:
            file_path = sym.get("file_path", "unknown")
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(sym)

        # Write each file
        for file_path, file_symbols in by_file.items():
            # Create safe filename
            safe_name = file_path.replace("/", "_").replace("\\", "_")
            if not safe_name.endswith(".json"):
                safe_name += ".json"

            self._write_json(output_dir / safe_name, {
                "file": file_path,
                "symbols": file_symbols,
            })
            files_created.append(f"symbols/by-file/{safe_name}")

        return files_created

    def _create_library_id(self, source_path: Path, git_info: GitInfo) -> str:
        """Create a unique library ID from repository info.

        Args:
            source_path: Path to repository.
            git_info: Git information.

        Returns:
            Library ID in format "repo_name:branch:commit_short".
        """
        repo_name = source_path.name
        branch = git_info.branch or "unknown"
        commit = git_info.short_commit or "unknown"
        return f"{repo_name}:{branch}:{commit}"

    def _convert_dependencies_to_dicts(
        self,
        dependencies: list,
    ) -> list[dict[str, Any]]:
        """Convert dependency objects to dictionaries for graph storage.

        Args:
            dependencies: List of Dependency objects.

        Returns:
            List of dependency dictionaries.
        """
        dep_dicts = []
        for dep in dependencies:
            if isinstance(dep, dict):
                dep_dicts.append(dep)
            else:
                # Convert Dependency object to dict
                dep_dict = {
                    "source": getattr(dep, 'source', ''),
                    "target": getattr(dep, 'target', ''),
                    "dependency_type": getattr(dep, 'dependency_type', 'import'),
                    "file_path": getattr(dep, 'file_path', ''),
                }
                dep_dicts.append(dep_dict)
        return dep_dicts

    async def _persist_to_graph(
        self,
        library_id: str,
        symbols: list[dict],
        dependencies: list[dict[str, Any]],
    ) -> dict[str, int]:
        """Persist analysis results to graph storage.

        Creates nodes for symbols and relationships for dependencies.

        Args:
            library_id: Unique library identifier.
            symbols: List of symbol dictionaries.
            dependencies: List of dependency dictionaries.

        Returns:
            Dictionary with counts: {"nodes": N, "relationships": M}.
        """
        from repo_ctx.storage.protocols import GraphNode, GraphRelationship

        graph_storage = getattr(self._context, 'graph_storage', None)

        if graph_storage is None:
            logger.warning("No graph storage configured, skipping graph persistence")
            return {"nodes": 0, "relationships": 0}

        # Create nodes for symbols
        nodes = []
        for sym in symbols:
            symbol_type = sym.get("type", "function")
            labels = ["Symbol", symbol_type.capitalize()]

            # Add visibility label
            visibility = sym.get("visibility", "public")
            if visibility == "public":
                labels.append("PublicAPI")

            node = GraphNode(
                id=f"{library_id}:{sym.get('qualified_name', sym.get('name'))}",
                labels=labels,
                properties={
                    "name": sym.get("name"),
                    "qualified_name": sym.get("qualified_name"),
                    "file_path": sym.get("file_path"),
                    "line_start": sym.get("line_start"),
                    "line_end": sym.get("line_end"),
                    "signature": sym.get("signature"),
                    "docstring": sym.get("documentation"),
                    "visibility": visibility,
                    "library_id": library_id,
                    "symbol_type": symbol_type,
                },
            )
            nodes.append(node)

        await graph_storage.create_nodes(nodes)

        # Create relationships for dependencies
        relationships = []
        for dep in dependencies:
            source = dep.get("source")
            target = dep.get("target")
            dep_type = dep.get("dependency_type", "DEPENDS_ON")

            if source and target:
                rel = GraphRelationship(
                    from_id=f"{library_id}:{source}",
                    to_id=f"{library_id}:{target}",
                    type=dep_type.upper().replace(" ", "_"),
                    properties={
                        "file_path": dep.get("file_path"),
                        "library_id": library_id,
                    },
                )
                relationships.append(rel)

        await graph_storage.create_relationships(relationships)

        return {
            "nodes": len(nodes),
            "relationships": len(relationships),
        }


def create_dump_service(
    context: ServiceContext,
    llm_service: Optional["LLMService"] = None,
) -> DumpService:
    """Create a DumpService instance.

    Args:
        context: Service context with storage and config.
        llm_service: Optional LLM service for generating business summaries.
            If provided, dumps will include LLM-generated business context
            in llms.txt.

    Returns:
        Configured DumpService instance.
    """
    return DumpService(context, llm_service=llm_service)
