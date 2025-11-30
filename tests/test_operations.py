"""Tests for repo_ctx.operations module."""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from repo_ctx.operations import (
    parse_repo_id,
    is_local_path,
    clone_repo_to_temp,
    analyze_local_directory,
    get_clone_url,
    parse_include_options,
    cleanup_temp_directory,
    VALID_INCLUDE_OPTIONS,
)


class TestParseRepoId:
    """Tests for parse_repo_id function."""

    def test_simple_owner_repo(self):
        """Test parsing simple owner/repo format."""
        group, project = parse_repo_id("owner/repo")
        assert group == "owner"
        assert project == "repo"

    def test_with_leading_slash(self):
        """Test parsing with leading slash."""
        group, project = parse_repo_id("/owner/repo")
        assert group == "owner"
        assert project == "repo"

    def test_with_trailing_slash(self):
        """Test parsing with trailing slash."""
        group, project = parse_repo_id("owner/repo/")
        assert group == "owner"
        assert project == "repo"

    def test_nested_group(self):
        """Test parsing nested group path."""
        group, project = parse_repo_id("group/subgroup/repo")
        assert group == "group/subgroup"
        assert project == "repo"

    def test_deeply_nested_group(self):
        """Test parsing deeply nested group path."""
        group, project = parse_repo_id("/a/b/c/d/repo")
        assert group == "a/b/c/d"
        assert project == "repo"

    def test_single_part(self):
        """Test parsing single part (no slash)."""
        group, project = parse_repo_id("single")
        assert group == "single"
        assert project == ""

    def test_empty_string(self):
        """Test parsing empty string."""
        group, project = parse_repo_id("")
        assert group == ""
        assert project == ""


class TestIsLocalPath:
    """Tests for is_local_path function."""

    def test_absolute_path(self):
        """Test absolute path detection."""
        assert is_local_path("/home/user/project") is True
        assert is_local_path("/tmp/repo") is True
        assert is_local_path("/usr/local/src") is True

    def test_relative_path_current_dir(self):
        """Test relative path with ./."""
        assert is_local_path("./project") is True
        assert is_local_path("../project") is True

    def test_home_tilde_path(self):
        """Test home directory ~ path."""
        assert is_local_path("~/project") is True
        assert is_local_path("~/.config/repo") is True

    def test_github_style_path(self):
        """Test GitHub-style owner/repo is not local."""
        assert is_local_path("owner/repo") is False
        assert is_local_path("facebook/react") is False

    def test_empty_path(self):
        """Test empty path."""
        assert is_local_path("") is False
        assert is_local_path(None) is False

    def test_existing_local_path(self):
        """Test path that exists on filesystem."""
        # The current directory should exist
        assert is_local_path(".") is True


class TestCloneRepoToTemp:
    """Tests for clone_repo_to_temp function."""

    @patch('repo_ctx.operations.subprocess.run')
    def test_successful_clone(self, mock_run):
        """Test successful git clone."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        temp_dir = clone_repo_to_temp("https://github.com/test/repo.git")

        assert temp_dir is not None
        assert temp_dir.startswith(tempfile.gettempdir())
        mock_run.assert_called_once()

        # Verify clone command structure
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "clone" in call_args
        assert "--depth" in call_args
        assert "1" in call_args

        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @patch('repo_ctx.operations.subprocess.run')
    def test_clone_with_ref(self, mock_run):
        """Test clone with specific branch/tag."""
        mock_run.return_value = Mock(returncode=0, stderr="")

        temp_dir = clone_repo_to_temp("https://github.com/test/repo.git", ref="v1.0.0")

        call_args = mock_run.call_args[0][0]
        assert "--branch" in call_args
        assert "v1.0.0" in call_args

        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @patch('repo_ctx.operations.subprocess.run')
    def test_clone_failure(self, mock_run):
        """Test clone failure handling."""
        mock_run.return_value = Mock(returncode=1, stderr="Clone failed")

        with pytest.raises(RuntimeError, match="Git clone failed"):
            clone_repo_to_temp("https://github.com/test/repo.git")

    @patch('repo_ctx.operations.subprocess.run')
    def test_clone_timeout(self, mock_run):
        """Test clone timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("git", 120)

        with pytest.raises(RuntimeError, match="Git clone timed out"):
            clone_repo_to_temp("https://github.com/test/repo.git")


class TestAnalyzeLocalDirectory:
    """Tests for analyze_local_directory function."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        temp_dir = tempfile.mkdtemp()

        # Create some Python files
        (Path(temp_dir) / "main.py").write_text("def main(): pass")
        (Path(temp_dir) / "utils.py").write_text("def helper(): pass")

        # Create a subdirectory
        (Path(temp_dir) / "src").mkdir()
        (Path(temp_dir) / "src" / "module.py").write_text("class Module: pass")

        # Create test files
        (Path(temp_dir) / "tests").mkdir()
        (Path(temp_dir) / "tests" / "test_main.py").write_text("def test_main(): pass")
        (Path(temp_dir) / "test_utils.py").write_text("def test_utils(): pass")

        # Create hidden and skip directories
        (Path(temp_dir) / ".git").mkdir()
        (Path(temp_dir) / ".git" / "config").write_text("[core]")
        (Path(temp_dir) / "__pycache__").mkdir()
        (Path(temp_dir) / "__pycache__" / "main.cpython-311.pyc").write_text("bytecode")

        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_analyzer(self):
        """Create a mock analyzer."""
        analyzer = Mock()
        analyzer.detect_language = Mock(side_effect=lambda f: "python" if f.endswith(".py") else None)
        return analyzer

    def test_finds_python_files(self, temp_repo, mock_analyzer):
        """Test that Python files are found."""
        files = analyze_local_directory(temp_repo, mock_analyzer)

        assert "main.py" in files
        assert "utils.py" in files
        assert "src/module.py" in files

    def test_excludes_test_files_by_default(self, temp_repo, mock_analyzer):
        """Test that test files are excluded by default."""
        files = analyze_local_directory(temp_repo, mock_analyzer, exclude_tests=True)

        assert "test_utils.py" not in files
        assert "tests/test_main.py" not in files

    def test_includes_test_files_when_requested(self, temp_repo, mock_analyzer):
        """Test that test files can be included."""
        files = analyze_local_directory(temp_repo, mock_analyzer, exclude_tests=False)

        assert "test_utils.py" in files
        assert "tests/test_main.py" in files

    def test_excludes_hidden_directories(self, temp_repo, mock_analyzer):
        """Test that hidden directories are excluded."""
        files = analyze_local_directory(temp_repo, mock_analyzer)

        # No files from .git directory
        assert all(".git" not in f for f in files)

    def test_excludes_cache_directories(self, temp_repo, mock_analyzer):
        """Test that cache directories are excluded."""
        files = analyze_local_directory(temp_repo, mock_analyzer)

        # No files from __pycache__ directory
        assert all("__pycache__" not in f for f in files)


class TestGetCloneUrl:
    """Tests for get_clone_url function."""

    def test_github_without_token(self):
        """Test GitHub URL without token."""
        url = get_clone_url("github", "owner", "repo")
        assert url == "https://github.com/owner/repo.git"

    def test_github_with_token(self):
        """Test GitHub URL with token."""
        config = Mock()
        config.github_token = "ghp_test123"

        url = get_clone_url("github", "owner", "repo", config)
        assert url == "https://ghp_test123@github.com/owner/repo.git"

    def test_gitlab_without_token(self):
        """Test GitLab URL without token."""
        url = get_clone_url("gitlab", "group", "project")
        assert url == "https://gitlab.com/group/project.git"

    def test_gitlab_with_token(self):
        """Test GitLab URL with token."""
        config = Mock()
        config.gitlab_url = "https://gitlab.com"
        config.gitlab_token = "glpat-test123"

        url = get_clone_url("gitlab", "group", "project", config)
        assert url == "https://oauth2:glpat-test123@gitlab.com/group/project.git"

    def test_gitlab_self_hosted(self):
        """Test GitLab self-hosted URL."""
        config = Mock()
        config.gitlab_url = "https://git.company.com"
        config.gitlab_token = None

        url = get_clone_url("gitlab", "group", "project", config)
        assert url == "https://git.company.com/group/project.git"

    def test_unsupported_provider(self):
        """Test unsupported provider raises error."""
        with pytest.raises(ValueError, match="Unsupported provider"):
            get_clone_url("bitbucket", "owner", "repo")


class TestParseIncludeOptions:
    """Tests for parse_include_options function."""

    def test_empty_input(self):
        """Test empty input returns all False."""
        result = parse_include_options()
        assert result['include_code'] is False
        assert result['include_symbols'] is False
        assert result['include_diagrams'] is False
        assert result['include_tests'] is False
        assert result['include_examples'] is False

    def test_single_option_string(self):
        """Test single option from string."""
        result = parse_include_options(include_str="code")
        assert result['include_code'] is True
        assert result['include_symbols'] is False

    def test_multiple_options_string(self):
        """Test multiple options from string."""
        result = parse_include_options(include_str="code,diagrams,tests")
        assert result['include_code'] is True
        assert result['include_diagrams'] is True
        assert result['include_tests'] is True
        assert result['include_symbols'] is False

    def test_options_list(self):
        """Test options from list."""
        result = parse_include_options(include_list=["code", "symbols"])
        assert result['include_code'] is True
        assert result['include_symbols'] is True
        assert result['include_diagrams'] is False

    def test_all_option(self):
        """Test 'all' enables everything."""
        result = parse_include_options(include_str="all")
        assert all(v is True for v in result.values())

    def test_case_insensitive(self):
        """Test options are case insensitive."""
        result = parse_include_options(include_str="CODE,DIAGRAMS")
        assert result['include_code'] is True
        assert result['include_diagrams'] is True

    def test_whitespace_handling(self):
        """Test whitespace in options is handled."""
        result = parse_include_options(include_str=" code , diagrams ")
        assert result['include_code'] is True
        assert result['include_diagrams'] is True

    def test_invalid_options_ignored(self):
        """Test invalid options are ignored with warning."""
        result = parse_include_options(include_str="code,invalid,diagrams")
        assert result['include_code'] is True
        assert result['include_diagrams'] is True

    def test_valid_include_options_constant(self):
        """Test VALID_INCLUDE_OPTIONS constant."""
        assert 'code' in VALID_INCLUDE_OPTIONS
        assert 'symbols' in VALID_INCLUDE_OPTIONS
        assert 'diagrams' in VALID_INCLUDE_OPTIONS
        assert 'tests' in VALID_INCLUDE_OPTIONS
        assert 'examples' in VALID_INCLUDE_OPTIONS
        assert 'all' in VALID_INCLUDE_OPTIONS


class TestCleanupTempDirectory:
    """Tests for cleanup_temp_directory function."""

    def test_cleanup_existing_directory(self):
        """Test cleanup of existing directory."""
        temp_dir = tempfile.mkdtemp()
        (Path(temp_dir) / "file.txt").write_text("content")

        cleanup_temp_directory(temp_dir)

        assert not os.path.exists(temp_dir)

    def test_cleanup_nonexistent_directory(self):
        """Test cleanup of non-existent directory doesn't error."""
        cleanup_temp_directory("/nonexistent/path")
        # Should not raise

    def test_cleanup_none(self):
        """Test cleanup with None doesn't error."""
        cleanup_temp_directory(None)
        # Should not raise


class TestGetOrAnalyzeRepo:
    """Tests for get_or_analyze_repo function."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock GitLabContext."""
        context = Mock()
        context.config = Mock()
        context.storage = AsyncMock()
        return context

    @pytest.mark.asyncio
    async def test_repo_not_found(self, mock_context):
        """Test error when repository not found."""
        from repo_ctx.operations import get_or_analyze_repo

        mock_context.storage.get_library.return_value = None

        symbols, lib, error = await get_or_analyze_repo(mock_context, "owner/repo")

        assert symbols is None
        assert lib is None
        assert "not found" in error.lower()

    @pytest.mark.asyncio
    async def test_returns_cached_symbols(self, mock_context):
        """Test returns cached symbols when available."""
        from repo_ctx.operations import get_or_analyze_repo

        mock_lib = Mock()
        mock_lib.id = 1
        mock_lib.provider = "github"
        mock_context.storage.get_library.return_value = mock_lib
        mock_context.storage.search_symbols.return_value = [
            {
                'name': 'TestClass',
                'symbol_type': 'class',
                'file_path': 'test.py',
                'line_start': 1,
                'line_end': 10,
                'metadata': '{}'
            }
        ]

        symbols, lib, error = await get_or_analyze_repo(mock_context, "owner/repo")

        assert error is None
        assert lib == mock_lib
        assert len(symbols) == 1
        assert symbols[0].name == 'TestClass'
