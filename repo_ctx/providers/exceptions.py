"""Provider-specific exceptions."""


class ProviderError(Exception):
    """Base exception for all provider errors."""
    pass


class ProviderNotFoundError(ProviderError):
    """Raised when a project/repository is not found."""
    pass


class ProviderAuthError(ProviderError):
    """Raised when authentication fails."""
    pass


class ProviderFileNotFoundError(ProviderError):
    """Raised when a file is not found in the repository."""
    pass


class ProviderRateLimitError(ProviderError):
    """Raised when API rate limit is exceeded."""
    pass


class ProviderConfigError(ProviderError):
    """Raised when provider configuration is invalid."""
    pass
