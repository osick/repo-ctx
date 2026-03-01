"""Tests for local Git repository provider."""

import pytest
import os
import tempfile
from pathlib import Path
from git import Repo
from repo_ctx.providers.local import LocalGitProvider
from repo_ctx.providers.base import ProviderProject, ProviderFile


class TestLocalGitProviderPathResolution:
    """Test path resolution and repository discovery."""

    def test_absolute_path_resolution(self, tmp_git_repo):
        """Test indexing with absolute path."""
        provider = LocalGitProvider(tmp_git_repo)
        assert provider.repo_path == Path(tmp_git_repo).resolve()
        assert provider.repo_path.is_absolute()

    def test_relative_path_resolution(self, tmp_git_repo):
        """Test indexing with relative path."""
        # Change to parent directory and use relative path
        original_cwd = os.getcwd()
        try:
            parent = Path(tmp_git_repo).parent
            os.chdir(parent)
            rel_path = f"./{Path(tmp_git_repo).name}"

            provider = LocalGitProvider(rel_path)
            assert provider.repo_path.is_absolute()
            assert provider.repo_path == Path(tmp_git_repo).resolve()
        finally:
            os.chdir(original_cwd)

    def test_home_path_resolution(self):
        """Test indexing with home-relative path."""
        # Create a test repo in a known location
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Repo.init(tmpdir)
            self._setup_git_user(repo)

            # Use expanduser to get actual path
            expanded = Path(tmpdir).expanduser().resolve()
            provider = LocalGitProvider(tmpdir)

            assert provider.repo_path.is_absolute()
            assert provider.repo_path == expanded

    def test_invalid_path_raises_error(self):
        """Test error handling for non-existent path."""
        with pytest.raises(FileNotFoundError):
            LocalGitProvider("/nonexistent/path/to/repo")

    def test_non_git_directory_raises_error(self):
        """Test error handling for non-Git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="not a Git repository"):
                LocalGitProvider(tmpdir)

    @staticmethod
    def _setup_git_user(repo):
        """Configure git user for commits."""
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()


class TestLocalGitProviderGitOperations:
    """Test Git operations (branches, tags, files)."""

    @pytest.mark.asyncio
    async def test_get_project_extracts_name(self, tmp_git_repo):
        """Test extracting project name from directory."""
        provider = LocalGitProvider(tmp_git_repo)
        project = await provider.get_project(tmp_git_repo)

        assert isinstance(project, ProviderProject)
        assert project.name == Path(tmp_git_repo).name
        assert project.path == tmp_git_repo
        assert project.id is not None

    @pytest.mark.asyncio
    async def test_get_project_with_description(self, tmp_git_repo_with_readme):
        """Test extracting description from README."""
        provider = LocalGitProvider(tmp_git_repo_with_readme)
        project = await provider.get_project(tmp_git_repo_with_readme)

        assert project.description == "Test Project"

    @pytest.mark.asyncio
    async def test_get_default_branch(self, tmp_git_repo):
        """Test getting default branch."""
        provider = LocalGitProvider(tmp_git_repo)
        project = await provider.get_project(tmp_git_repo)
        branch = await provider.get_default_branch(project)

        assert branch in ['main', 'master']  # Depends on Git version

    @pytest.mark.asyncio
    async def test_get_file_tree_recursive(self, tmp_git_repo_with_files):
        """Test recursive file tree listing."""
        provider = LocalGitProvider(tmp_git_repo_with_files)
        project = await provider.get_project(tmp_git_repo_with_files)
        branch = await provider.get_default_branch(project)

        files = await provider.get_file_tree(project, branch, recursive=True)

        assert "README.md" in files
        assert "docs/guide.md" in files
        assert "docs/api/reference.md" in files
        assert len(files) >= 3

    @pytest.mark.asyncio
    async def test_get_file_tree_non_recursive(self, tmp_git_repo_with_files):
        """Test non-recursive file tree listing."""
        provider = LocalGitProvider(tmp_git_repo_with_files)
        project = await provider.get_project(tmp_git_repo_with_files)
        branch = await provider.get_default_branch(project)

        files = await provider.get_file_tree(project, branch, recursive=False)

        assert "README.md" in files
        assert "docs/guide.md" not in files  # In subdirectory

    @pytest.mark.asyncio
    async def test_read_file_content(self, tmp_git_repo_with_files):
        """Test reading file content at specific ref."""
        provider = LocalGitProvider(tmp_git_repo_with_files)
        project = await provider.get_project(tmp_git_repo_with_files)
        branch = await provider.get_default_branch(project)

        file = await provider.read_file(project, "README.md", branch)

        assert isinstance(file, ProviderFile)
        assert file.path == "README.md"
        assert "# Test Project" in file.content
        assert file.size > 0

    @pytest.mark.asyncio
    async def test_read_file_from_subdirectory(self, tmp_git_repo_with_files):
        """Test reading file from subdirectory."""
        provider = LocalGitProvider(tmp_git_repo_with_files)
        project = await provider.get_project(tmp_git_repo_with_files)
        branch = await provider.get_default_branch(project)

        file = await provider.read_file(project, "docs/guide.md", branch)

        assert file.path == "docs/guide.md"
        assert "# User Guide" in file.content

    @pytest.mark.asyncio
    async def test_read_file_from_tag(self, tmp_git_repo_with_tag):
        """Test reading file from specific tag."""
        provider = LocalGitProvider(tmp_git_repo_with_tag)
        project = await provider.get_project(tmp_git_repo_with_tag)

        file = await provider.read_file(project, "README.md", "v1.0.0")

        assert file.content is not None
        assert "# Test Project" in file.content

    @pytest.mark.asyncio
    async def test_read_nonexistent_file_raises_error(self, tmp_git_repo):
        """Test error when reading non-existent file."""
        provider = LocalGitProvider(tmp_git_repo)
        project = await provider.get_project(tmp_git_repo)
        branch = await provider.get_default_branch(project)

        with pytest.raises(FileNotFoundError):
            await provider.read_file(project, "nonexistent.md", branch)

    @pytest.mark.asyncio
    async def test_get_tags_sorted_by_date(self, tmp_git_repo_with_tags):
        """Test getting tags sorted by creation date."""
        provider = LocalGitProvider(tmp_git_repo_with_tags)
        project = await provider.get_project(tmp_git_repo_with_tags)

        tags = await provider.get_tags(project, limit=5)

        assert len(tags) >= 2
        assert "v1.0.0" in tags
        assert "v0.9.0" in tags
        # v1.0.0 should come before v0.9.0 (newest first)
        assert tags.index("v1.0.0") < tags.index("v0.9.0")

    @pytest.mark.asyncio
    async def test_get_tags_respects_limit(self, tmp_git_repo_with_tags):
        """Test that get_tags respects the limit parameter."""
        provider = LocalGitProvider(tmp_git_repo_with_tags)
        project = await provider.get_project(tmp_git_repo_with_tags)

        tags = await provider.get_tags(project, limit=1)

        assert len(tags) == 1
        assert tags[0] == "v1.0.0"  # Most recent

    @pytest.mark.asyncio
    async def test_read_config_file(self, tmp_git_repo_with_config):
        """Test reading .repo-ctx.json configuration."""
        provider = LocalGitProvider(tmp_git_repo_with_config)
        project = await provider.get_project(tmp_git_repo_with_config)
        branch = await provider.get_default_branch(project)

        config = await provider.read_config(project, branch)

        assert config is not None
        assert config["folders"] == ["docs/"]
        assert "internal.md" in config["exclude_files"]

    @pytest.mark.asyncio
    async def test_read_config_returns_none_if_not_found(self, tmp_git_repo):
        """Test that read_config returns None when no config file exists."""
        provider = LocalGitProvider(tmp_git_repo)
        project = await provider.get_project(tmp_git_repo)
        branch = await provider.get_default_branch(project)

        config = await provider.read_config(project, branch)

        assert config is None


class TestLocalGitProviderEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_repository_without_commits(self):
        """Test handling empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Repo.init(tmpdir)

            provider = LocalGitProvider(tmpdir)
            project = await provider.get_project(tmpdir)

            # Should handle empty repo gracefully
            assert project.name == Path(tmpdir).name

    @pytest.mark.asyncio
    async def test_repository_without_remote(self, tmp_git_repo):
        """Test repository without git remote configured."""
        provider = LocalGitProvider(tmp_git_repo)
        project = await provider.get_project(tmp_git_repo)

        # Should still work, use directory name as project name
        assert project.name is not None
        assert project.name == Path(tmp_git_repo).name
        # web_url should be None
        assert project.web_url is None

    @pytest.mark.asyncio
    async def test_repository_with_remote(self, tmp_git_repo_with_remote):
        """Test repository with git remote configured."""
        provider = LocalGitProvider(tmp_git_repo_with_remote)
        project = await provider.get_project(tmp_git_repo_with_remote)

        # Should extract web_url from remote
        assert project.web_url is not None
        assert "github.com" in project.web_url

    @pytest.mark.asyncio
    async def test_binary_file_exclusion(self, tmp_git_repo_with_binary):
        """Test that binary files are excluded from file tree."""
        provider = LocalGitProvider(tmp_git_repo_with_binary)
        project = await provider.get_project(tmp_git_repo_with_binary)
        branch = await provider.get_default_branch(project)

        files = await provider.get_file_tree(project, branch, recursive=True)

        # Should include text files
        assert "README.md" in files
        # Should exclude binary files
        assert "image.png" not in files

    @pytest.mark.asyncio
    async def test_list_projects_in_group_not_implemented(self, tmp_git_repo):
        """Test that list_projects_in_group raises NotImplementedError."""
        provider = LocalGitProvider(tmp_git_repo)

        with pytest.raises(NotImplementedError):
            await provider.list_projects_in_group("/some/path")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def tmp_git_repo():
    """Create a minimal temporary Git repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        # Create initial commit
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Repo\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_readme():
    """Create a git repo with README containing description."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n\nA test repository for unit tests")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_files():
    """Create a git repo with multiple files in directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        # Create README
        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        # Create docs directory with files
        docs_dir = Path(tmpdir) / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("# User Guide\n")

        api_dir = docs_dir / "api"
        api_dir.mkdir()
        (api_dir / "reference.md").write_text("# API Reference\n")

        repo.index.add(["docs/guide.md", "docs/api/reference.md"])
        repo.index.commit("Add documentation")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_tag():
    """Create a git repo with a tag."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        # Create tag
        repo.create_tag("v1.0.0")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_tags():
    """Create a git repo with multiple tags."""
    import time
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project v0.9\n")
        repo.index.add(["README.md"])
        commit1 = repo.index.commit("Version 0.9")

        # Longer delay to ensure different commit timestamps
        time.sleep(1)

        # Create v0.9.0 tag (older)
        repo.create_tag("v0.9.0", ref=commit1)

        # Make another commit with delay
        time.sleep(1)
        readme.write_text("# Test Project v1.0\n\nUpdated for release")
        repo.index.add(["README.md"])
        commit2 = repo.index.commit("Version 1.0")

        # Small delay before creating tag
        time.sleep(1)

        # Create v1.0.0 tag (newer commit)
        repo.create_tag("v1.0.0", ref=commit2)

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_config():
    """Create a git repo with .repo-ctx.json config file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        # Create config file
        config_path = Path(tmpdir) / ".repo-ctx.json"
        config_path.write_text('{"folders": ["docs/"], "exclude_files": ["internal.md"]}')

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n")

        repo.index.add([".repo-ctx.json", "README.md"])
        repo.index.commit("Add config")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_remote():
    """Create a git repo with remote configured."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n")
        repo.index.add(["README.md"])
        repo.index.commit("Initial commit")

        # Add remote
        repo.create_remote("origin", "https://github.com/test/repo.git")

        yield tmpdir


@pytest.fixture
def tmp_git_repo_with_binary():
    """Create a git repo with binary file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        _setup_git_user(repo)

        readme = Path(tmpdir) / "README.md"
        readme.write_text("# Test Project\n")

        # Create a binary file (PNG header)
        binary = Path(tmpdir) / "image.png"
        binary.write_bytes(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)

        repo.index.add(["README.md", "image.png"])
        repo.index.commit("Add files")

        yield tmpdir


def _setup_git_user(repo):
    """Configure git user for commits."""
    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()
