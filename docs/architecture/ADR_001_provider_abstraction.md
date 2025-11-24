# ADR 001: Provider Abstraction Layer

**Status:** Proposed
**Date:** 2025-11-24
**Decision Makers:** Development Team
**Related Requirements:** [requirements.md](../.vibe/docs/requirements.md) Section 4

---

## Context

repo-ctx currently supports only GitLab as a source for repository documentation. We need to extend support to multiple providers:
- GitHub (highest priority - large user base)
- Local Git repositories (offline/private use cases)
- Package registries (PyPI, NPM)
- Other Git platforms (Bitbucket, Azure DevOps, Gitea)

The current codebase has direct dependencies on `python-gitlab` throughout the core logic, making it difficult to add new providers without significant refactoring.

## Decision

We will implement an **abstract provider interface** that defines the contract for all repository sources, allowing multiple providers to coexist with minimal code changes to the core business logic.

### Provider Interface Design

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class ProviderProject:
    """Normalized project representation across providers."""
    id: str
    name: str
    path: str
    description: Optional[str]
    default_branch: str
    web_url: Optional[str]

@dataclass
class ProviderFile:
    """Normalized file representation."""
    path: str
    content: str
    size: int

class GitProvider(ABC):
    """Abstract base class for all repository providers."""

    @abstractmethod
    async def get_project(self, path: str) -> ProviderProject:
        """
        Get project metadata.

        Args:
            path: Provider-specific project identifier
                  GitLab: "group/project"
                  GitHub: "owner/repo"
                  Local: "/absolute/path"

        Returns:
            ProviderProject with normalized metadata

        Raises:
            ProviderNotFoundError: Project doesn't exist
            ProviderAuthError: Authentication failed
        """
        pass

    @abstractmethod
    async def get_default_branch(self, project: ProviderProject) -> str:
        """Get default branch name (main, master, etc.)."""
        pass

    @abstractmethod
    async def get_file_tree(
        self,
        project: ProviderProject,
        ref: str,
        recursive: bool = True
    ) -> List[str]:
        """
        Get list of all file paths in repository.

        Args:
            project: Project to query
            ref: Branch, tag, or commit SHA
            recursive: Include subdirectories

        Returns:
            List of file paths relative to repo root
        """
        pass

    @abstractmethod
    async def read_file(
        self,
        project: ProviderProject,
        path: str,
        ref: str
    ) -> ProviderFile:
        """
        Read file contents.

        Args:
            project: Project to query
            path: File path relative to repo root
            ref: Branch, tag, or commit SHA

        Returns:
            ProviderFile with content and metadata

        Raises:
            ProviderFileNotFoundError: File doesn't exist at ref
        """
        pass

    @abstractmethod
    async def read_config(
        self,
        project: ProviderProject,
        ref: str
    ) -> Optional[dict]:
        """
        Read repo-ctx configuration file if it exists.

        Searches for:
        - git_context.json (current name)
        - .git_context.json
        - repo_context.json
        - .repo-ctx.json

        Returns:
            Parsed JSON config or None if not found
        """
        pass

    @abstractmethod
    async def get_tags(
        self,
        project: ProviderProject,
        limit: int = 5
    ) -> List[str]:
        """
        Get repository tags (most recent first).

        Args:
            project: Project to query
            limit: Maximum number of tags to return

        Returns:
            List of tag names
        """
        pass

    @abstractmethod
    async def list_projects_in_group(
        self,
        group_path: str,
        include_subgroups: bool = True
    ) -> List[ProviderProject]:
        """
        List all projects in a group/organization.

        Args:
            group_path: Group identifier (GitLab: "group", GitHub: "org")
            include_subgroups: Include nested groups (GitLab only)

        Returns:
            List of projects in the group

        Note:
            Not all providers support groups (e.g., local repos)
        """
        pass
```

### Provider Implementations

```python
class GitLabProvider(GitProvider):
    """GitLab implementation using python-gitlab."""

    def __init__(self, url: str, token: str):
        self.client = gitlab.Gitlab(url, private_token=token)
        self.client.auth()

    async def get_project(self, path: str) -> ProviderProject:
        project = self.client.projects.get(path)
        return ProviderProject(
            id=str(project.id),
            name=project.name,
            path=project.path_with_namespace,
            description=project.description,
            default_branch=project.default_branch,
            web_url=project.web_url
        )
    # ... implement other methods

class GitHubProvider(GitProvider):
    """GitHub implementation using PyGithub."""

    def __init__(self, url: str, token: Optional[str] = None):
        if url == "https://api.github.com":
            self.client = Github(token)
        else:
            # GitHub Enterprise
            self.client = Github(base_url=url, login_or_token=token)

    async def get_project(self, path: str) -> ProviderProject:
        repo = self.client.get_repo(path)
        return ProviderProject(
            id=str(repo.id),
            name=repo.name,
            path=repo.full_name,
            description=repo.description,
            default_branch=repo.default_branch,
            web_url=repo.html_url
        )
    # ... implement other methods

class LocalGitProvider(GitProvider):
    """Local filesystem Git implementation using GitPython."""

    def __init__(self):
        pass

    async def get_project(self, path: str) -> ProviderProject:
        repo = git.Repo(path)
        # Try to get remote URL, fall back to local path
        try:
            remote_url = repo.remote().url
            name = Path(remote_url).stem
        except:
            name = Path(path).name

        return ProviderProject(
            id=f"local://{path}",
            name=name,
            path=path,
            description=None,
            default_branch=repo.active_branch.name,
            web_url=None
        )
    # ... implement other methods
```

### Provider Factory

```python
class ProviderFactory:
    """Factory for creating provider instances."""

    @staticmethod
    def create_gitlab(url: str, token: str) -> GitLabProvider:
        return GitLabProvider(url, token)

    @staticmethod
    def create_github(url: str, token: Optional[str] = None) -> GitHubProvider:
        return GitHubProvider(url, token)

    @staticmethod
    def create_local() -> LocalGitProvider:
        return LocalGitProvider()

    @staticmethod
    def from_config(config: Config, provider_type: str) -> GitProvider:
        """Create provider from configuration."""
        if provider_type == "gitlab":
            return ProviderFactory.create_gitlab(
                config.gitlab_url,
                config.gitlab_token
            )
        elif provider_type == "github":
            return ProviderFactory.create_github(
                config.github_url,
                config.github_token
            )
        elif provider_type == "local":
            return ProviderFactory.create_local()
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
```

### Provider Detection

```python
class ProviderDetector:
    """Detect provider type from repository path."""

    @staticmethod
    def detect(path: str) -> str:
        """
        Detect provider from path format.

        Examples:
            "owner/repo" -> "github" (2 parts)
            "group/subgroup/project" -> "gitlab" (3+ parts)
            "/absolute/path" -> "local"
            "./relative/path" -> "local"

        Returns:
            Provider type: "gitlab", "github", or "local"
        """
        if path.startswith("/") or path.startswith("."):
            return "local"

        parts = path.split("/")
        if len(parts) == 2:
            return "github"  # owner/repo format
        elif len(parts) >= 3:
            return "gitlab"  # group/subgroup/project
        else:
            raise ValueError(f"Cannot detect provider from path: {path}")
```

### Configuration Updates

```yaml
# config.yaml
providers:
  gitlab:
    url: "https://gitlab.internal.com"
    token: "${GITLAB_TOKEN}"
    enabled: true

  github:
    url: "https://api.github.com"
    token: "${GITHUB_TOKEN}"
    enabled: true

  local:
    enabled: true

storage:
  path: "~/.repo-ctx/context.db"

# Default provider for ambiguous cases
default_provider: "gitlab"
```

### Storage Schema Changes

**Option 1: URI Format in library_id (RECOMMENDED)**

No database schema changes needed. Store provider in library_id:

```python
library_id: "gitlab://group/subgroup/project"
library_id: "github://owner/repo"
library_id: "local:///absolute/path/to/repo"
library_id: "pypi://package-name"
```

**Option 2: Add Provider Column**

```sql
ALTER TABLE libraries ADD COLUMN provider TEXT DEFAULT 'gitlab';
CREATE INDEX idx_libraries_provider ON libraries(provider);
```

We choose **Option 1** for the following reasons:
- No database migration required
- More flexible for future providers
- Self-documenting (library_id contains all context)
- Standard URI format
- Easier to parse and validate

### Core Logic Refactoring

```python
class GitLabContext:
    """Rename to RepositoryContext or keep for backwards compatibility."""

    def __init__(self, config: Config):
        self.config = config
        self.storage = Storage(config.storage_path)
        self.parser = MarkdownParser()

        # Initialize providers based on config
        self.providers = {}
        if config.providers.gitlab.enabled:
            self.providers["gitlab"] = ProviderFactory.create_gitlab(
                config.providers.gitlab.url,
                config.providers.gitlab.token
            )
        if config.providers.github.enabled:
            self.providers["github"] = ProviderFactory.create_github(
                config.providers.github.url,
                config.providers.github.token
            )
        if config.providers.local.enabled:
            self.providers["local"] = ProviderFactory.create_local()

    async def index_repository(
        self,
        path: str,
        provider_type: Optional[str] = None
    ):
        """
        Index repository from any provider.

        Args:
            path: Repository path (format depends on provider)
            provider_type: Explicit provider, or auto-detect
        """
        # Detect or use explicit provider
        if provider_type is None:
            provider_type = ProviderDetector.detect(path)

        provider = self.providers.get(provider_type)
        if not provider:
            raise ValueError(f"Provider {provider_type} not configured")

        # Rest of indexing logic is provider-agnostic
        project = await provider.get_project(path)
        default_branch = await provider.get_default_branch(project)
        config = await provider.read_config(project, default_branch)

        # ... continue with indexing using provider interface
```

## Consequences

### Positive

1. **Extensibility**: Adding new providers is straightforward - implement the interface
2. **Testability**: Easy to mock providers in tests
3. **Flexibility**: Supports multiple providers simultaneously
4. **Type Safety**: Abstract methods enforce consistent contract
5. **Separation of Concerns**: Business logic independent of provider details
6. **No Migration**: Using URI format avoids database schema changes

### Negative

1. **Initial Effort**: Refactoring existing GitLab code to use abstraction
2. **Complexity**: Additional abstraction layer adds cognitive overhead
3. **Performance**: Small overhead from abstraction (negligible in practice)
4. **Maintenance**: More code to maintain across multiple providers

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provider API differences | High | Normalize data in ProviderProject/ProviderFile |
| Breaking existing GitLab code | High | Comprehensive test coverage before refactoring |
| Rate limiting varies by provider | Medium | Provider-specific rate limit handling in implementations |
| Authentication complexity | Medium | Provider-specific auth in factory methods |

## Alternatives Considered

### Alternative 1: No Abstraction (Provider-Specific Code)

**Pros:**
- Simpler implementation
- Direct access to provider features
- No abstraction overhead

**Cons:**
- Code duplication across providers
- Difficult to maintain consistency
- Core logic tightly coupled to providers
- Hard to test

**Rejected because:** Not scalable for multiple providers

### Alternative 2: Adapter Pattern (Wrapper Around Existing Client)

**Pros:**
- Minimal changes to existing code
- Quick to implement

**Cons:**
- Still tightly coupled to GitLab client
- Doesn't enforce consistent interface
- Harder to test

**Rejected because:** Doesn't solve the core coupling problem

### Alternative 3: Plugin System with Dynamic Loading

**Pros:**
- Extremely flexible
- Third-party providers possible
- Providers as separate packages

**Cons:**
- Complex implementation
- Security concerns with dynamic loading
- Overkill for current needs

**Rejected because:** Too complex for current requirements

## Implementation Plan

### Phase 1: Abstraction Foundation
1. Create `repo_ctx/providers/` package
2. Implement `base.py` with `GitProvider` ABC
3. Create exceptions: `ProviderError`, `ProviderNotFoundError`, etc.
4. Write unit tests for provider detection logic

### Phase 2: Refactor GitLab
1. Create `GitLabProvider` class in `providers/gitlab.py`
2. Refactor existing `gitlab_client.py` code into provider
3. Update `GitLabContext` to use provider interface
4. Run full test suite to ensure no regressions

### Phase 3: GitHub Provider
1. Implement `GitHubProvider` in `providers/github.py`
2. Add PyGithub dependency
3. Write comprehensive tests
4. Update CLI to support `--provider github`

### Phase 4: Local Provider
1. Implement `LocalGitProvider` in `providers/local.py`
2. Add GitPython dependency
3. Write tests for local repository handling
4. Add watch mode support

## Testing Strategy

### Unit Tests
- Test each provider implementation independently
- Mock external APIs (GitLab, GitHub)
- Test provider detection logic
- Test factory methods

### Integration Tests
- Test indexing with real repositories (test fixtures)
- Test cross-provider search
- Test provider switching

### Test Coverage Target
- Provider base: 100% (abstract interface)
- Provider implementations: >90%
- Provider detection: 100%
- Factory: 100%

## Documentation Updates

- [ ] Update README.md with multi-provider examples
- [ ] Document provider configuration in config.yaml
- [ ] Add provider-specific troubleshooting section
- [ ] Create migration guide for GitLab-only users
- [ ] Document how to add a new provider

## Success Metrics

- ✅ All existing GitLab functionality works unchanged
- ✅ Can index GitHub repository
- ✅ Can index local repository
- ✅ Test coverage maintained at >80%
- ✅ No performance degradation (<5% overhead)
- ✅ Configuration migration is smooth

## Related

- **Requirements:** [Multi-Provider Support Requirements](../.vibe/docs/requirements.md)
- **Implementation:** Phase 1 (v0.3.0)
- **Future ADRs:**
  - ADR_002: Package Registry Provider Design
  - ADR_003: Rate Limiting Strategy
  - ADR_004: Authentication Management

---

**Review and Approval:**

- [ ] Technical review completed
- [ ] User approval received
- [ ] Implementation plan approved
- [ ] Test strategy approved

**Status Change Log:**
- 2025-11-24: Initial draft (Proposed)
