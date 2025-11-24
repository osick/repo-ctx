"""Tests for provider base classes and utilities."""
import pytest
from repo_ctx.providers import (
    ProviderProject,
    ProviderFile,
    GitProvider,
    ProviderError,
    ProviderNotFoundError,
    ProviderAuthError,
    ProviderFileNotFoundError,
    ProviderRateLimitError,
    ProviderConfigError,
    ProviderDetector,
    ProviderFactory
)


class TestProviderExceptions:
    """Test provider exception hierarchy."""

    def test_provider_error_base(self):
        """Test base ProviderError exception."""
        error = ProviderError("test message")
        assert str(error) == "test message"
        assert isinstance(error, Exception)

    def test_provider_not_found_error(self):
        """Test ProviderNotFoundError inherits from ProviderError."""
        error = ProviderNotFoundError("not found")
        assert isinstance(error, ProviderError)
        assert str(error) == "not found"

    def test_provider_auth_error(self):
        """Test ProviderAuthError inherits from ProviderError."""
        error = ProviderAuthError("auth failed")
        assert isinstance(error, ProviderError)
        assert str(error) == "auth failed"

    def test_provider_file_not_found_error(self):
        """Test ProviderFileNotFoundError inherits from ProviderError."""
        error = ProviderFileNotFoundError("file not found")
        assert isinstance(error, ProviderError)
        assert str(error) == "file not found"

    def test_provider_rate_limit_error(self):
        """Test ProviderRateLimitError inherits from ProviderError."""
        error = ProviderRateLimitError("rate limit exceeded")
        assert isinstance(error, ProviderError)
        assert str(error) == "rate limit exceeded"

    def test_provider_config_error(self):
        """Test ProviderConfigError inherits from ProviderError."""
        error = ProviderConfigError("invalid config")
        assert isinstance(error, ProviderError)
        assert str(error) == "invalid config"


class TestProviderProject:
    """Test ProviderProject dataclass."""

    def test_create_provider_project_minimal(self):
        """Test creating ProviderProject with minimal fields."""
        project = ProviderProject(
            id="123",
            name="test-repo",
            path="owner/test-repo",
            description=None,
            default_branch="main",
            web_url=None
        )
        assert project.id == "123"
        assert project.name == "test-repo"
        assert project.path == "owner/test-repo"
        assert project.description is None
        assert project.default_branch == "main"
        assert project.web_url is None

    def test_create_provider_project_full(self):
        """Test creating ProviderProject with all fields."""
        project = ProviderProject(
            id="456",
            name="my-project",
            path="group/subgroup/my-project",
            description="A test project",
            default_branch="develop",
            web_url="https://gitlab.com/group/my-project"
        )
        assert project.id == "456"
        assert project.name == "my-project"
        assert project.path == "group/subgroup/my-project"
        assert project.description == "A test project"
        assert project.default_branch == "develop"
        assert project.web_url == "https://gitlab.com/group/my-project"


class TestProviderFile:
    """Test ProviderFile dataclass."""

    def test_create_provider_file(self):
        """Test creating ProviderFile."""
        file = ProviderFile(
            path="README.md",
            content="# Test\n\nContent here",
            size=100
        )
        assert file.path == "README.md"
        assert file.content == "# Test\n\nContent here"
        assert file.size == 100

    def test_provider_file_empty_content(self):
        """Test ProviderFile with empty content."""
        file = ProviderFile(
            path="empty.txt",
            content="",
            size=0
        )
        assert file.path == "empty.txt"
        assert file.content == ""
        assert file.size == 0


class TestProviderDetector:
    """Test provider detection logic."""

    def test_detect_local_absolute_path(self):
        """Test detecting local provider from absolute path."""
        assert ProviderDetector.detect("/home/user/repo") == "local"
        assert ProviderDetector.detect("/var/repos/project") == "local"

    def test_detect_local_relative_path(self):
        """Test detecting local provider from relative path."""
        assert ProviderDetector.detect("./repo") == "local"
        assert ProviderDetector.detect("../project") == "local"
        assert ProviderDetector.detect("./path/to/repo") == "local"

    def test_detect_local_home_path(self):
        """Test detecting local provider from home path."""
        assert ProviderDetector.detect("~/repos/project") == "local"

    def test_detect_github_two_parts(self):
        """Test detecting GitHub from owner/repo format."""
        assert ProviderDetector.detect("owner/repo") == "github"
        assert ProviderDetector.detect("fastapi/fastapi") == "github"

    def test_detect_gitlab_three_parts(self):
        """Test detecting GitLab from group/subgroup/project format."""
        assert ProviderDetector.detect("group/subgroup/project") == "gitlab"
        assert ProviderDetector.detect("a/b/c") == "gitlab"

    def test_detect_gitlab_four_parts(self):
        """Test detecting GitLab from deeply nested groups."""
        assert ProviderDetector.detect("group/sub1/sub2/project") == "gitlab"

    def test_detect_explicit_protocol(self):
        """Test detecting provider from explicit protocol."""
        assert ProviderDetector.detect("gitlab://group/project") == "gitlab"
        assert ProviderDetector.detect("github://owner/repo") == "github"
        assert ProviderDetector.detect("local:///path/to/repo") == "local"

    def test_detect_with_default_provider(self):
        """Test using default provider for ambiguous cases."""
        # owner/repo could be GitLab or GitHub
        assert ProviderDetector.detect("owner/repo", default="gitlab") == "gitlab"
        assert ProviderDetector.detect("owner/repo", default="github") == "github"

    def test_detect_invalid_single_part(self):
        """Test error on single-part path."""
        with pytest.raises(ValueError, match="Cannot detect provider"):
            ProviderDetector.detect("invalidpath")

    def test_detect_invalid_empty(self):
        """Test error on empty path."""
        with pytest.raises(ValueError):
            ProviderDetector.detect("")

    def test_normalize_path_removes_protocol(self):
        """Test normalizing path removes protocol."""
        assert ProviderDetector.normalize_path(
            "gitlab://group/project",
            "gitlab"
        ) == "group/project"
        assert ProviderDetector.normalize_path(
            "github://owner/repo",
            "github"
        ) == "owner/repo"
        assert ProviderDetector.normalize_path(
            "local:///path/to/repo",
            "local"
        ) == "/path/to/repo"

    def test_normalize_path_without_protocol(self):
        """Test normalizing path without protocol returns as-is."""
        assert ProviderDetector.normalize_path(
            "group/project",
            "gitlab"
        ) == "group/project"
        assert ProviderDetector.normalize_path(
            "/path/to/repo",
            "local"
        ) == "/path/to/repo"

    def test_to_library_id_gitlab(self):
        """Test converting GitLab path to library_id."""
        assert ProviderDetector.to_library_id(
            "group/project",
            "gitlab"
        ) == "gitlab://group/project"

    def test_to_library_id_github(self):
        """Test converting GitHub path to library_id."""
        assert ProviderDetector.to_library_id(
            "owner/repo",
            "github"
        ) == "github://owner/repo"

    def test_to_library_id_local(self):
        """Test converting local path to library_id."""
        assert ProviderDetector.to_library_id(
            "/path/to/repo",
            "local"
        ) == "local:///path/to/repo"

    def test_to_library_id_local_relative_fails(self):
        """Test error when converting relative local path."""
        with pytest.raises(ValueError, match="Local paths must be absolute"):
            ProviderDetector.to_library_id("./repo", "local")

    def test_from_library_id_gitlab(self):
        """Test parsing GitLab library_id."""
        provider, path = ProviderDetector.from_library_id("gitlab://group/project")
        assert provider == "gitlab"
        assert path == "group/project"

    def test_from_library_id_github(self):
        """Test parsing GitHub library_id."""
        provider, path = ProviderDetector.from_library_id("github://owner/repo")
        assert provider == "github"
        assert path == "owner/repo"

    def test_from_library_id_local(self):
        """Test parsing local library_id."""
        provider, path = ProviderDetector.from_library_id("local:///path/to/repo")
        assert provider == "local"
        assert path == "/path/to/repo"

    def test_from_library_id_invalid_format(self):
        """Test error on invalid library_id format."""
        with pytest.raises(ValueError, match="Invalid library_id format"):
            ProviderDetector.from_library_id("invalidformat")


class TestProviderFactory:
    """Test provider factory."""

    def test_list_providers_initially_empty(self):
        """Test factory has no providers registered initially."""
        # Factory is a class with class variables, may have providers from other tests
        # Just verify it returns a list
        providers = ProviderFactory.list_providers()
        assert isinstance(providers, list)

    def test_register_provider(self):
        """Test registering a provider class."""
        class MockProvider(GitProvider):
            async def get_project(self, path: str):
                pass
            async def get_default_branch(self, project):
                pass
            async def get_file_tree(self, project, ref, recursive=True):
                pass
            async def read_file(self, project, path, ref):
                pass
            async def read_config(self, project, ref):
                pass
            async def get_tags(self, project, limit=5):
                pass
            async def list_projects_in_group(self, group_path, include_subgroups=True):
                pass

        ProviderFactory.register("mock", MockProvider)
        assert ProviderFactory.is_registered("mock")
        assert "mock" in ProviderFactory.list_providers()

    def test_is_registered_false(self):
        """Test is_registered returns False for unknown provider."""
        assert not ProviderFactory.is_registered("nonexistent-provider-xyz")

    def test_create_unknown_provider_raises(self):
        """Test creating unknown provider raises error."""
        with pytest.raises(ProviderConfigError, match="Unknown provider type"):
            ProviderFactory.create("unknown-provider")

    def test_create_with_invalid_config_raises(self):
        """Test creating provider with invalid config raises error."""
        class StrictProvider(GitProvider):
            def __init__(self, required_param: str):
                self.required_param = required_param

            async def get_project(self, path: str):
                pass
            async def get_default_branch(self, project):
                pass
            async def get_file_tree(self, project, ref, recursive=True):
                pass
            async def read_file(self, project, path, ref):
                pass
            async def read_config(self, project, ref):
                pass
            async def get_tags(self, project, limit=5):
                pass
            async def list_projects_in_group(self, group_path, include_subgroups=True):
                pass

        ProviderFactory.register("strict", StrictProvider)

        with pytest.raises(ProviderConfigError, match="Invalid configuration"):
            ProviderFactory.create("strict")  # Missing required_param


class TestGitProviderInterface:
    """Test GitProvider abstract interface."""

    def test_cannot_instantiate_abstract_class(self):
        """Test GitProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            GitProvider()

    def test_must_implement_all_methods(self):
        """Test provider must implement all abstract methods."""
        class IncompleteProvider(GitProvider):
            pass

        with pytest.raises(TypeError):
            IncompleteProvider()

    def test_complete_implementation_works(self):
        """Test a complete provider implementation can be instantiated."""
        class CompleteProvider(GitProvider):
            async def get_project(self, path: str):
                return ProviderProject("1", "test", path, None, "main", None)

            async def get_default_branch(self, project):
                return "main"

            async def get_file_tree(self, project, ref, recursive=True):
                return ["README.md"]

            async def read_file(self, project, path, ref):
                return ProviderFile(path, "content", 100)

            async def read_config(self, project, ref):
                return None

            async def get_tags(self, project, limit=5):
                return ["v1.0.0"]

            async def list_projects_in_group(self, group_path, include_subgroups=True):
                return []

        # Should not raise
        provider = CompleteProvider()
        assert isinstance(provider, GitProvider)
