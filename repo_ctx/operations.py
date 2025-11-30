"""Shared operations for repository analysis and management.

This module consolidates common functions used across MCP, CLI, and TUI interfaces.
It provides a single source of truth for repository operations.
"""

import json
import os
import shutil
import subprocess
import tempfile
from typing import Tuple, Optional, Dict, List, Any
from pathlib import Path


# Valid include options for documentation retrieval
VALID_INCLUDE_OPTIONS = {'code', 'symbols', 'diagrams', 'tests', 'examples', 'all'}


def parse_repo_id(repo_id: str) -> Tuple[str, str]:
    """Parse repo_id into (group, project) tuple.

    Handles various formats:
    - /owner/repo -> (owner, repo)
    - owner/repo -> (owner, repo)
    - /group/subgroup/repo -> (group/subgroup, repo)
    - single-part -> (single-part, "")

    Args:
        repo_id: Repository identifier string

    Returns:
        Tuple of (group, project) where group may contain nested paths
    """
    clean_id = repo_id.strip("/")
    parts = clean_id.split("/")
    if len(parts) >= 2:
        project = parts[-1]
        group = "/".join(parts[:-1])
        return (group, project)
    return (clean_id, "")


def is_local_path(path: str) -> bool:
    """Check if a path is a local filesystem path.

    Args:
        path: Path string to check

    Returns:
        True if path appears to be a local filesystem path
    """
    if not path:
        return False

    # Explicit local path indicators
    if path.startswith(("/", "./", "../", "~/")):
        return True

    # Check common Unix path prefixes
    prefixes = ("/home/", "/usr/", "/opt/", "/tmp/", "/var/", "/mnt/", "/media/", "/root/")
    if path.startswith(prefixes):
        return True

    # Check if it's an absolute path with more than 3 parts
    parts = path.strip("/").split("/")
    if len(parts) > 3 and parts[0] in ('home', 'usr', 'opt', 'tmp', 'var', 'mnt', 'media', 'root'):
        return True

    # Check if path exists on filesystem
    expanded = os.path.expanduser(path)
    if os.path.exists(expanded):
        return True

    return False


def clone_repo_to_temp(clone_url: str, ref: Optional[str] = None, timeout: int = 120) -> str:
    """Clone a repository to a temporary directory using shallow clone.

    Args:
        clone_url: Git clone URL (https or ssh)
        ref: Optional branch/tag to checkout
        timeout: Clone timeout in seconds (default: 120)

    Returns:
        Path to the cloned repository

    Raises:
        RuntimeError: If clone fails or times out
    """
    temp_dir = tempfile.mkdtemp(prefix="repo_ctx_")

    try:
        # Build clone command - shallow clone for speed
        cmd = ["git", "clone", "--depth", "1"]
        if ref:
            cmd.extend(["--branch", ref])
        cmd.extend([clone_url, temp_dir])

        # Run clone
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Git clone failed: {result.stderr}")

        return temp_dir

    except subprocess.TimeoutExpired:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError("Git clone timed out")


def analyze_local_directory(
    repo_path: str,
    analyzer,
    exclude_tests: bool = True
) -> Dict[str, str]:
    """Analyze all code files in a local directory.

    Args:
        repo_path: Path to the repository
        analyzer: CodeAnalyzer instance with detect_language method
        exclude_tests: If True, exclude test files and directories

    Returns:
        Dictionary mapping relative file paths to their content
    """
    # Directories to always skip (virtual envs, caches, build artifacts)
    skip_dirs = {
        '.git', '.venv', 'venv', 'env', '.env',
        'node_modules', '__pycache__', '.pytest_cache',
        '.mypy_cache', '.ruff_cache', '.tox',
        'dist', 'build', 'egg-info', '.eggs',
        'htmlcov', '.coverage', 'coverage',
        '.idea', '.vscode', '.vs',
        'vendor', 'third_party', 'external',
        'target',  # Java/Rust build output
    }

    # Test directories to skip if exclude_tests is True
    test_dirs = {'tests', 'test', 'spec', 'specs', '__tests__'}

    files = {}
    for root, dirs, filenames in os.walk(repo_path):
        # Remove directories we want to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.endswith('.egg-info')]

        # Also skip test directories if requested
        if exclude_tests:
            dirs[:] = [d for d in dirs if d not in test_dirs]

        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in filenames:
            # Skip hidden files
            if filename.startswith('.'):
                continue

            # Skip test files if exclude_tests is True
            if exclude_tests:
                if filename.startswith('test_') or filename.endswith('_test.py'):
                    continue
                if filename.startswith('spec_') or filename.endswith('.spec.js'):
                    continue

            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_path)

            # Check if it's a code file we can analyze
            if analyzer.detect_language(rel_path):
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        files[rel_path] = f.read()
                except (IOError, OSError):
                    continue

    return files


def get_clone_url(provider_type: str, group: str, project: str, config=None) -> str:
    """Get the clone URL for a repository.

    Args:
        provider_type: Provider type ('github', 'gitlab')
        group: Repository group/owner
        project: Repository name
        config: Optional config object with token attributes

    Returns:
        Clone URL string

    Raises:
        ValueError: If provider_type is not supported
    """
    if provider_type == "github":
        # Use HTTPS with token if available
        token = None
        if config:
            token = getattr(config, 'github_token', None)
        if token:
            return f"https://{token}@github.com/{group}/{project}.git"
        return f"https://github.com/{group}/{project}.git"

    elif provider_type == "gitlab":
        # Get GitLab host from config or default
        base_url = "https://gitlab.com"
        if config:
            base_url = getattr(config, 'gitlab_url', base_url) or base_url
        base_url = base_url.rstrip('/')

        # Extract host from URL
        from urllib.parse import urlparse
        parsed = urlparse(base_url)
        host = parsed.netloc or parsed.path

        token = None
        if config:
            token = getattr(config, 'gitlab_token', None)
        if token:
            return f"https://oauth2:{token}@{host}/{group}/{project}.git"
        return f"https://{host}/{group}/{project}.git"

    else:
        raise ValueError(f"Unsupported provider for clone: {provider_type}")


def parse_include_options(include_str: Optional[str] = None, include_list: Optional[List[str]] = None) -> dict:
    """Parse include options into a dictionary of boolean flags.

    Accepts either a comma-separated string or a list of options.

    Args:
        include_str: Comma-separated string like "code,diagrams,tests"
        include_list: List of option strings like ["code", "diagrams"]

    Returns:
        Dictionary with boolean flags:
        - include_code: Include code structure (symbol lists)
        - include_symbols: Include detailed symbol info
        - include_diagrams: Include mermaid diagrams
        - include_tests: Include test files/symbols
        - include_examples: Include all doc code examples
    """
    result = {
        'include_code': False,
        'include_symbols': False,
        'include_diagrams': False,
        'include_tests': False,
        'include_examples': False,
    }

    # Build options set from either input
    options = set()
    if include_str:
        options = {opt.strip().lower() for opt in include_str.split(',')}
    elif include_list:
        options = {opt.lower() for opt in include_list}

    if not options:
        return result

    # Validate options
    invalid = options - VALID_INCLUDE_OPTIONS
    if invalid:
        # Log warning but don't fail
        import logging
        logging.warning(f"Unknown include options ignored: {', '.join(invalid)}")

    # Handle 'all' - enables everything
    if 'all' in options:
        return {
            'include_code': True,
            'include_symbols': True,
            'include_diagrams': True,
            'include_tests': True,
            'include_examples': True,
        }

    # Set individual flags
    result['include_code'] = 'code' in options
    result['include_symbols'] = 'symbols' in options
    result['include_diagrams'] = 'diagrams' in options
    result['include_tests'] = 'tests' in options
    result['include_examples'] = 'examples' in options

    return result


async def get_or_analyze_repo(
    context,
    repo_id: str,
    force_refresh: bool = False
) -> Tuple[Optional[List], Optional[Any], Optional[str]]:
    """Get stored analysis for a repo, or analyze and store it.

    Uses git clone for efficient bulk file loading instead of per-file API calls.

    Args:
        context: GitLabContext instance
        repo_id: Repository identifier (e.g., /owner/repo or /path/to/local)
        force_refresh: If True, re-analyze even if cached symbols exist

    Returns:
        Tuple of (symbols, library, error_message)
        - symbols: List of Symbol objects, or None on error
        - library: Library object from storage
        - error_message: Error string if failed, None on success
    """
    from .analysis import CodeAnalyzer, Symbol, SymbolType

    # Handle local paths differently
    if is_local_path(repo_id):
        group = repo_id.rstrip("/")
        project = ""
    else:
        group, project = parse_repo_id(repo_id)

    lib = await context.storage.get_library(group, project)

    if not lib:
        return None, None, f"Repository {repo_id} not found in index. Use repo-ctx-index first."

    # Check if we have stored symbols
    stored_symbols = await context.storage.search_symbols(lib.id, "")

    if stored_symbols and not force_refresh:
        # Return stored symbols
        symbols = []
        for s in stored_symbols:
            # Parse metadata from JSON string
            metadata = {}
            if s.get('metadata'):
                try:
                    metadata = json.loads(s['metadata']) if isinstance(s['metadata'], str) else s['metadata']
                except (json.JSONDecodeError, TypeError):
                    metadata = {}

            symbols.append(Symbol(
                name=s['name'],
                symbol_type=SymbolType(s['symbol_type']),
                file_path=s['file_path'],
                line_start=s['line_start'],
                line_end=s['line_end'],
                signature=s.get('signature'),
                visibility=s.get('visibility', 'public'),
                language=s.get('language', 'unknown'),
                qualified_name=s.get('qualified_name'),
                documentation=s.get('documentation'),
                is_exported=s.get('is_exported', True),
                metadata=metadata
            ))
        return symbols, lib, None

    # Need to fetch and analyze - use git clone for efficiency
    temp_dir = None
    try:
        config = context.config
        analyzer = CodeAnalyzer()

        # For local provider, analyze directly
        if lib.provider == "local":
            repo_path = f"{group}/{project}" if project else group
            files = analyze_local_directory(repo_path, analyzer)
        else:
            # Clone repo to temp directory (single operation, no API rate limits)
            clone_url = get_clone_url(lib.provider, group, project, config)
            temp_dir = clone_repo_to_temp(clone_url)
            files = analyze_local_directory(temp_dir, analyzer)

        if not files:
            return [], lib, None

        # Analyze all files
        analysis_results = analyzer.analyze_files(files)
        symbols = analyzer.aggregate_symbols(analysis_results)

        # Store symbols in database
        await context.storage.save_symbols(symbols, lib.id)

        return symbols, lib, None

    except Exception as e:
        return None, lib, str(e)

    finally:
        # Clean up temp directory
        if temp_dir:
            shutil.rmtree(temp_dir, ignore_errors=True)


async def get_or_analyze_repo_standalone(
    repo_id: str,
    force_refresh: bool = False,
    config_path: Optional[str] = None
) -> Tuple[Optional[List], Optional[Any], Optional[str]]:
    """Standalone version of get_or_analyze_repo that creates its own context.

    Useful for CLI and TUI that don't have a pre-existing context.

    Args:
        repo_id: Repository identifier
        force_refresh: If True, re-analyze even if cached
        config_path: Optional path to config file

    Returns:
        Tuple of (symbols, library, error_message)
    """
    from .config import Config
    from .core import GitLabContext

    config = Config.load(config_path=config_path)
    context = GitLabContext(config)
    await context.init()

    return await get_or_analyze_repo(context, repo_id, force_refresh)


def cleanup_temp_directory(temp_dir: Optional[str]) -> None:
    """Safely clean up a temporary directory.

    Args:
        temp_dir: Path to temporary directory, or None
    """
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
