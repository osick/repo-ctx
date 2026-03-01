"""Tests for CLI target detection module."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch

from repo_ctx.cli.target import (
    detect_target,
    Target,
    TargetType,
    _looks_like_repo_name,
    _has_file_extension,
)


class TestTargetType:
    """Tests for TargetType enum."""

    def test_target_types_exist(self):
        """All expected target types should exist."""
        assert TargetType.LOCAL_PATH.value == "local"
        assert TargetType.INDEXED_REPO.value == "indexed"
        assert TargetType.REMOTE_REPO.value == "remote"


class TestTarget:
    """Tests for Target dataclass."""

    def test_local_target_properties(self):
        """Local target should have correct properties."""
        target = Target(type=TargetType.LOCAL_PATH, value="./src")
        assert target.is_local is True
        assert target.is_repo is False
        assert target.repo_id == ""

    def test_indexed_repo_properties(self):
        """Indexed repo target should have correct properties."""
        target = Target(
            type=TargetType.INDEXED_REPO,
            value="/owner/repo",
            owner="owner",
            repo="repo"
        )
        assert target.is_local is False
        assert target.is_repo is True
        assert target.repo_id == "/owner/repo"

    def test_remote_repo_properties(self):
        """Remote repo target should have correct properties."""
        target = Target(
            type=TargetType.REMOTE_REPO,
            value="owner/repo",
            owner="owner",
            repo="repo"
        )
        assert target.is_local is False
        assert target.is_repo is True
        assert target.repo_id == "/owner/repo"


class TestDetectTargetLocalPaths:
    """Tests for detecting local filesystem paths."""

    def test_relative_path_dot_slash(self):
        """./path should be detected as local."""
        target = detect_target("./src")
        assert target.type == TargetType.LOCAL_PATH
        assert target.value.endswith("src")

    def test_relative_path_dot_dot_slash(self):
        """../path should be detected as local."""
        target = detect_target("../other")
        assert target.type == TargetType.LOCAL_PATH

    def test_home_path_tilde(self):
        """~/path should be detected as local."""
        target = detect_target("~/projects")
        assert target.type == TargetType.LOCAL_PATH
        assert target.value.startswith(os.path.expanduser("~"))

    def test_absolute_path_existing(self, tmp_path):
        """Existing absolute path should be detected as local."""
        test_dir = tmp_path / "test_project"
        test_dir.mkdir()

        target = detect_target(str(test_dir))
        assert target.type == TargetType.LOCAL_PATH
        assert target.value == str(test_dir)

    def test_single_word_as_local(self):
        """Single word without slashes should be local."""
        target = detect_target("myfile")
        assert target.type == TargetType.LOCAL_PATH

    def test_file_with_extension_as_local(self):
        """File with extension should be detected as local."""
        target = detect_target("main.py")
        assert target.type == TargetType.LOCAL_PATH

    def test_path_with_dots_as_local(self):
        """Path containing dots should be detected as local."""
        target = detect_target("src/main.py")
        assert target.type == TargetType.LOCAL_PATH


class TestDetectTargetIndexedRepos:
    """Tests for detecting indexed repository IDs."""

    def test_indexed_repo_format(self):
        """/owner/repo format should be indexed repo."""
        # Mock Path.exists to return False (not a local path)
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("/owner/repo")
            assert target.type == TargetType.INDEXED_REPO
            assert target.owner == "owner"
            assert target.repo == "repo"
            assert target.repo_id == "/owner/repo"

    def test_indexed_repo_with_org(self):
        """/organization/project should be indexed repo."""
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("/myorg/myproject")
            assert target.type == TargetType.INDEXED_REPO
            assert target.owner == "myorg"
            assert target.repo == "myproject"

    def test_absolute_path_not_existing_looks_like_repo(self):
        """/owner/repo that doesn't exist should be indexed repo."""
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("/fastapi/fastapi")
            assert target.type == TargetType.INDEXED_REPO
            assert target.owner == "fastapi"
            assert target.repo == "fastapi"


class TestDetectTargetRemoteRepos:
    """Tests for detecting remote repository references."""

    def test_remote_repo_github_style(self):
        """owner/repo format should be remote repo."""
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("owner/repo")
            assert target.type == TargetType.REMOTE_REPO
            assert target.owner == "owner"
            assert target.repo == "repo"

    def test_remote_repo_gitlab_style(self):
        """group/project format should be remote repo."""
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("mygroup/myproject")
            assert target.type == TargetType.REMOTE_REPO
            assert target.owner == "mygroup"
            assert target.repo == "myproject"

    def test_remote_repo_nested_group(self):
        """group/subgroup/project should be remote repo."""
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("group/subgroup/project")
            assert target.type == TargetType.REMOTE_REPO
            assert target.owner == "group/subgroup"
            assert target.repo == "project"


class TestDetectTargetEdgeCases:
    """Tests for edge cases in target detection."""

    def test_empty_components_handled(self):
        """Should handle edge cases gracefully."""
        # Single slash
        target = detect_target("/")
        # Should not crash, type depends on implementation
        assert target is not None

    def test_existing_local_path_takes_precedence(self, tmp_path):
        """If path exists locally, should be LOCAL_PATH even if looks like repo."""
        # Create a directory that looks like owner/repo
        owner_dir = tmp_path / "owner"
        repo_dir = owner_dir / "repo"
        repo_dir.mkdir(parents=True)

        target = detect_target(str(repo_dir))
        assert target.type == TargetType.LOCAL_PATH

    def test_path_with_spaces(self):
        """Paths with spaces should work."""
        target = detect_target("./my project/src")
        assert target.type == TargetType.LOCAL_PATH


class TestLooksLikeRepoName:
    """Tests for _looks_like_repo_name helper."""

    def test_valid_repo_names(self):
        """Valid repo names should return True."""
        assert _looks_like_repo_name("fastapi") is True
        assert _looks_like_repo_name("my-project") is True
        assert _looks_like_repo_name("my_project") is True
        assert _looks_like_repo_name("project123") is True

    def test_invalid_repo_names(self):
        """Invalid repo names should return False."""
        assert _looks_like_repo_name("") is False
        assert _looks_like_repo_name("file.py") is False  # Has extension
        assert _looks_like_repo_name("-invalid") is False  # Starts with hyphen
        assert _looks_like_repo_name("has.dot") is False  # Has dot


class TestHasFileExtension:
    """Tests for _has_file_extension helper."""

    def test_common_extensions(self):
        """Common file extensions should be detected."""
        assert _has_file_extension("main.py") is True
        assert _has_file_extension("app.js") is True
        assert _has_file_extension("config.yaml") is True
        assert _has_file_extension("README.md") is True
        assert _has_file_extension("Sample.st") is True

    def test_no_extension(self):
        """Files without extensions should return False."""
        assert _has_file_extension("Makefile") is False
        assert _has_file_extension("owner/repo") is False
        assert _has_file_extension("myproject") is False


class TestDetectTargetIntegration:
    """Integration tests for target detection."""

    def test_typical_cli_usage_patterns(self):
        """Test common CLI usage patterns."""
        # Local analysis
        target = detect_target("./src")
        assert target.is_local

        # Indexed repo analysis
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("/fastapi/fastapi")
            assert target.is_repo
            assert target.type == TargetType.INDEXED_REPO

        # Remote repo (to be indexed)
        with patch.object(Path, 'exists', return_value=False):
            target = detect_target("pallets/flask")
            assert target.is_repo
            assert target.type == TargetType.REMOTE_REPO

    def test_ambiguous_cases(self, tmp_path):
        """Test cases that could be ambiguous."""
        # Create a local file that looks like it could be a repo
        test_file = tmp_path / "owner"
        test_file.mkdir()

        # When the path exists, should be local
        target = detect_target(str(test_file))
        assert target.type == TargetType.LOCAL_PATH
