"""Provider abstraction for multi-source repository indexing."""
from .base import GitProvider, ProviderProject, ProviderFile
from .exceptions import (
    ProviderError,
    ProviderNotFoundError,
    ProviderAuthError,
    ProviderFileNotFoundError,
    ProviderRateLimitError,
    ProviderConfigError
)
from .factory import ProviderFactory
from .detector import ProviderDetector
from .gitlab import GitLabProvider
from .github import GitHubProvider
from .local import LocalGitProvider

__all__ = [
    "GitProvider",
    "ProviderProject",
    "ProviderFile",
    "ProviderError",
    "ProviderNotFoundError",
    "ProviderAuthError",
    "ProviderFileNotFoundError",
    "ProviderRateLimitError",
    "ProviderConfigError",
    "ProviderFactory",
    "ProviderDetector",
    "GitLabProvider",
    "GitHubProvider",
    "LocalGitProvider",
]

# Register providers
ProviderFactory.register("gitlab", GitLabProvider)
ProviderFactory.register("github", GitHubProvider)
ProviderFactory.register("local", LocalGitProvider)
